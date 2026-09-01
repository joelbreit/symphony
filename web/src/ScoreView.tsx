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

export default function ScoreView({ url, getTime }: Props) {
  const wrapRef = useRef<HTMLDivElement>(null)
  const [pages, setPages] = useState<string[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const timemapRef = useRef<TimemapEntry[] | null>(null)
  const playheadRef = useRef({ idx: 0, lastMs: -1, lit: new Set<string>() })

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
        const width = wrapRef.current?.clientWidth ?? 900
        tk.setOptions({
          pageWidth: Math.max(1200, Math.min(2600, Math.round(width * 100 / SCALE))),
          scale: SCALE,
          adjustPageHeight: true,
          breaks: 'auto',
          svgViewBox: true,
          footer: 'none',
          header: 'none',
        })
        if (!tk.loadData(xml)) throw new Error('Verovio could not parse the score')
        const n = tk.getPageCount()
        const svgs: string[] = []
        for (let i = 1; i <= n; i++) svgs.push(tk.renderToSVG(i))
        timemapRef.current = tk.renderToTimemap({}) as TimemapEntry[]
        setPages(svgs)
      })
      .catch(e => { if (!dead) setError(String(e?.message ?? e)) })
    return () => { dead = true }
  }, [url])

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
          const y = sys.getBoundingClientRect().top - wr.top
          if (y < wr.height * 0.02 || y > wr.height * 0.45) {
            glideTo(wrap, wrap.scrollTop + y - wr.height * 0.15)
          }
        }
      }
    }, 120)
    return () => clearInterval(id)
  }, [pages, getTime])

  if (error) {
    return <div className="score-wrap score-msg" ref={wrapRef}>the score could not be loaded — {error}</div>
  }
  if (!pages) {
    return <div className="score-wrap score-msg" ref={wrapRef}>engraving…</div>
  }
  return (
    <div className="score-wrap" ref={wrapRef}>
      {pages.map((svg, i) => (
        <div key={i} className="score-page" dangerouslySetInnerHTML={{ __html: svg }} />
      ))}
    </div>
  )
}
