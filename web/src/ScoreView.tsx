import { useEffect, useRef, useState } from 'react'

/**
 * Engraved-score view, synced to the audio clock.
 *
 * Renders the piece package's MusicXML (exported from the pre-humanized
 * symbolic layer — see lib/notation.py) with Verovio in-browser, then uses
 * Verovio's timemap to light up the sounding notes and keep the current
 * system in view. The toolkit (~7 MB wasm) is loaded lazily on first open
 * and shared across pieces.
 */

interface Props {
  url: string
  getTime: () => number
}

// Verovio lays a system out to `pageWidth`, and a system's *height* is fixed
// by its staff count — so how much of the score fits on screen is decided
// almost entirely by how wide we tell Verovio the page is. A wide page puts
// more music on each line and shrinks it to fit; a narrow one does the
// opposite. Rather than guess, we render one page, measure the system, and
// pick the page width that makes a whole system (every instrument, top to
// bottom) land inside the visible pane.
const PROBE_WIDTH = 3000
const MIN_PAGE_WIDTH = 1500          // below this, few enough bars that the
const MAX_PAGE_WIDTH = 20000         // page looks empty; above, unreadably fine
const PAGE_MAX_PX = 1400             // keep in step with .score-page max-width
const ZOOMS = [0.5, 0.7, 1, 1.4, 2, 2.8]     // 1 = a whole system fits the pane
const FIT_ZOOM = 2

interface TimemapEntry {
  qstamp: number
  tstamp: number                       // milliseconds, from the score's tempi
  on?: string[]
  off?: string[]
}

const SCALE = 38

// setTimeout, not requestAnimationFrame: rAF (and native smooth scrollTo,
// which rides on it) is suspended entirely in hidden/embedded pages
const glides = new WeakMap<Element, { target: number }>()
function glideTo(el: Element, top: number) {
  const max = el.scrollHeight - el.clientHeight
  const target = Math.max(0, Math.min(max, top))
  const g = glides.get(el)
  if (g) { g.target = target; return }        // live glide: just retarget
  const state = { target }
  glides.set(el, state)
  const step = () => {
    const d = state.target - el.scrollTop
    if (Math.abs(d) < 1) {
      el.scrollTop = state.target
      glides.delete(el)
      return
    }
    el.scrollTop += Math.sign(d) * Math.max(1, Math.abs(d) * 0.14)
    setTimeout(step, 16)
  }
  setTimeout(step, 16)
}

let toolkitPromise: Promise<InstanceType<typeof import('verovio/esm').VerovioToolkit>> | null = null
function getToolkit() {
  if (!toolkitPromise) {
    toolkitPromise = Promise.all([import('verovio/wasm'), import('verovio/esm')])
      .then(async ([wasm, esm]) => new esm.VerovioToolkit(await wasm.default()))
  }
  return toolkitPromise
}

/** Height of one system, and the page width, in Verovio's own units. */
function systemMetrics(svg: string) {
  const box = svg.match(/viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"/)
  if (!box) return null
  const systems = (svg.match(/class="system"/g) ?? []).length || 1
  return { w: Number(box[1]), h: Number(box[2]) / systems }
}

export default function ScoreView({ url, getTime }: Props) {
  const wrapRef = useRef<HTMLDivElement>(null)
  const [pages, setPages] = useState<string[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [zoomIdx, setZoomIdx] = useState(FIT_ZOOM)
  const zoom = ZOOMS[zoomIdx]
  const [fitKey, setFitKey] = useState(0)
  const timemapRef = useRef<TimemapEntry[] | null>(null)
  const playheadRef = useRef({ idx: 0, lastMs: -1, lit: new Set<string>() })

  // a resized window changes what fits, so lay the score out again — but only
  // for real changes, not the pixel jitter of a scrollbar appearing
  useEffect(() => {
    const wrap = wrapRef.current
    if (!wrap || typeof ResizeObserver === 'undefined') return
    let last = { w: wrap.clientWidth, h: wrap.clientHeight }
    let timer: ReturnType<typeof setTimeout>
    const ro = new ResizeObserver(() => {
      const w = wrap.clientWidth, h = wrap.clientHeight
      if (Math.abs(w - last.w) < last.w * 0.1 &&
          Math.abs(h - last.h) < last.h * 0.1) return
      last = { w, h }
      clearTimeout(timer)
      timer = setTimeout(() => setFitKey(k => k + 1), 250)
    })
    ro.observe(wrap)
    return () => { ro.disconnect(); clearTimeout(timer) }
  }, [])

  useEffect(() => {
    let dead = false
    setPages(null)
    setError(null)
    timemapRef.current = null
    playheadRef.current = { idx: 0, lastMs: -1, lit: new Set() }
    Promise.all([
      getToolkit(),
      fetch(url).then(r => {
        if (!r.ok) throw new Error(`score fetch failed (${r.status})`)
        return r.text()
      }),
    ])
      .then(([tk, xml]) => {
        if (dead) return
        const wrap = wrapRef.current
        // the pane minus its padding, and no wider than the page cap in CSS
        const cw = Math.min((wrap?.clientWidth ?? 900) - 36, PAGE_MAX_PX)
        // aim a little under the full height: a system wedged edge to edge
        // leaves the autoscroll no room to place it
        const ch = (wrap?.clientHeight ?? 600) * 0.85
        const base = {
          scale: SCALE,
          adjustPageHeight: true,
          breaks: 'auto',
          svgViewBox: true,
          footer: 'none',
          header: 'none',
          // a staff sits closer to its neighbour than Verovio's default: on
          // 16 staves that alone is a fifth off the height of every system
          spacingStaff: 7,
          pageMarginTop: 20,
          pageMarginBottom: 20,
          pageMarginLeft: 25,
          pageMarginRight: 25,
        }
        tk.setOptions({ ...base, pageWidth: PROBE_WIDTH })
        if (!tk.loadData(xml)) throw new Error('Verovio could not parse the score')

        // probe: how tall is one system when the page is PROBE_WIDTH wide?
        const m = systemMetrics(tk.renderToSVG(1))
        let pageWidth = PROBE_WIDTH
        if (m) {
          // On screen the page is scaled to the pane's width, so one system
          // takes cw * (h / w) pixels of height. Solve that for the page
          // width at which it just fits the height we have.
          const fit = PROBE_WIDTH * (m.h / m.w) * (cw / ch)
          // …but only widen past a comfortable reading size when a system
          // actually needs it. A two-stave rag has height to spare and wants
          // several systems stacked, not one stretched across the pane; a
          // sixteen-stave orchestral system has no such luxury.
          const comfortable = cw * 100 / SCALE
          pageWidth = Math.round(Math.max(MIN_PAGE_WIDTH,
            Math.min(MAX_PAGE_WIDTH, Math.max(comfortable, fit) / zoom)))
          tk.setOptions({ ...base, pageWidth })
          tk.redoLayout()
        }
        const n = tk.getPageCount()
        const svgs: string[] = []
        for (let i = 1; i <= n; i++) svgs.push(tk.renderToSVG(i))
        timemapRef.current = tk.renderToTimemap({}) as TimemapEntry[]
        setPages(svgs)
      })
      .catch(e => { if (!dead) setError(String(e?.message ?? e)) })
    return () => { dead = true }
  }, [url, zoom, fitKey])

  // playhead: advance through the timemap, toggling .sc-on by element id
  useEffect(() => {
    if (!pages) return
    const id = setInterval(() => {
      const tm = timemapRef.current
      const wrap = wrapRef.current
      if (!tm || !wrap) return
      const ms = getTime() * 1000
      const ph = playheadRef.current
      if (ms < ph.lastMs - 60) {                   // seeked backwards: reset
        ph.lit.forEach(x => document.getElementById(x)?.classList.remove('sc-on'))
        ph.lit.clear()
        ph.idx = 0
      }
      ph.lastMs = ms
      let landed: string | null = null
      while (ph.idx < tm.length && tm[ph.idx].tstamp <= ms) {
        const e = tm[ph.idx]
        e.off?.forEach(x => {
          document.getElementById(x)?.classList.remove('sc-on')
          ph.lit.delete(x)
        })
        e.on?.forEach(x => {
          document.getElementById(x)?.classList.add('sc-on')
          ph.lit.add(x)
          landed = x
        })
        ph.idx++
      }
      // glide via our own rAF loop: native scrollTo({smooth}) is a no-op in
      // some embedded browsers, and re-issuing it every tick never catches up
      // anchor on the system, not the note: the landed note is often in the
      // bottom staff, and centering it would push the system's top off-screen
      if (landed) {
        const el = document.getElementById(landed)
        const sys = el?.closest('.system') ?? el
        if (sys) {
          const wr = wrap.getBoundingClientRect()
          const box = sys.getBoundingClientRect()
          const y = box.top - wr.top
          // a system that nearly fills the pane gets parked at the top;
          // a short one can sit lower, where it reads more comfortably
          const anchor = box.height > wr.height * 0.55 ? 0.04 : 0.15
          if (y < wr.height * 0.02 || y > wr.height * 0.45) {
            glideTo(wrap, wrap.scrollTop + y - wr.height * anchor)
          }
        }
      }
    }, 120)
    return () => clearInterval(id)
  }, [pages, getTime])

  if (error) {
    return <div className="score-wrap score-msg" ref={wrapRef}>the score could not be loaded — {error}</div>
  }
  return (
    <>
      <div className="score-wrap" ref={wrapRef}>
        {pages
          ? pages.map((svg, i) => (
            <div key={i} className="score-page" dangerouslySetInnerHTML={{ __html: svg }} />
          ))
          : <div className="score-msg score-msg-inline">engraving…</div>}
      </div>
      <div className="score-zoom">
        <button onClick={() => setZoomIdx(i => Math.max(0, i - 1))}
                disabled={!pages || zoomIdx === 0} title="show more of the score">−</button>
        <span>{zoomIdx === FIT_ZOOM ? 'fit' : `${Math.round(zoom * 100)}%`}</span>
        <button onClick={() => setZoomIdx(i => Math.min(ZOOMS.length - 1, i + 1))}
                disabled={!pages || zoomIdx === ZOOMS.length - 1} title="larger notes">+</button>
      </div>
    </>
  )
}
