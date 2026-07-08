import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  Accidental, Barline, Beam, Dot, Formatter, GhostNote, Renderer, Stave,
  StaveConnector, StaveNote, StaveTie, Voice, VoiceMode,
} from 'vexflow'
import { InstrumentInfo } from './types'
import { Ev, PreparedScore, ScoreData, prepareScore } from './score'

interface Props {
  score: ScoreData
  instruments: InstrumentInfo[]
  colors: string[]
  accent: string
  getTime: () => number
  playing: boolean
  spotlight: number
  onSeek: (sec: number) => void
}

const BAR_U = 96
const CHUNK_BARS = 4
const TOP_PAD = 34
const BOT_PAD = 26
const STAFF_H = 40
const PART_STEP = 92
const GRAND_EXTRA = 64
const STAFF_LINE = 'rgba(138,143,163,0.38)'
const REST_COLOR = 'rgba(138,143,163,0.5)'

interface Layout {
  barX: number[]          // per bar, x origin within content
  barW: number[]
  totalW: number
  partY: number[]         // per prepared part, y of (first) staff
  totalH: number
  gutterW: number
  chunks: number
}

interface NoteReg { u0: number; u1: number; el: SVGElement }

export default function SheetMusic({
  score, instruments, colors, accent, getTime, playing, spotlight, onSeek,
}: Props) {
  const prepared = useMemo(() => prepareScore(score), [score])
  const layout = useMemo<Layout>(() => {
    const barX: number[] = []
    const barW: number[] = []
    let x = 0
    for (let b = 0; b < prepared.bars; b++) {
      const w = Math.max(76, Math.min(460, 40 + prepared.cols[b] * 17))
      barX.push(x)
      barW.push(w)
      x += w
    }
    const partY: number[] = []
    let y = TOP_PAD
    for (const p of prepared.parts) {
      partY.push(y)
      y += PART_STEP + (p.grand ? GRAND_EXTRA : 0)
    }
    return {
      barX, barW, totalW: x,
      partY, totalH: y - PART_STEP + STAFF_H + BOT_PAD,
      gutterW: 66 + Math.abs(prepared.fifths) * 10 + 30,
      chunks: Math.ceil(prepared.bars / CHUNK_BARS),
    }
  }, [prepared])

  const scrollRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)
  const gutterRef = useRef<HTMLDivElement>(null)
  const cursorRef = useRef<HTMLDivElement>(null)
  const [range, setRange] = useState<[number, number]>([0, 2])
  const anchorsRef = useRef<Map<number, [number, number][]>>(new Map())
  const regRef = useRef<Map<number, NoteReg[]>>(new Map())
  const litRef = useRef<Set<SVGElement>>(new Set())
  const lastInteract = useRef(0)
  const lastT = useRef(-1)

  const stateRef = useRef({ playing, spotlight })
  stateRef.current = { playing, spotlight }

  // reset caches when the movement (score) changes
  useEffect(() => {
    anchorsRef.current = new Map()
    regRef.current = new Map()
    litRef.current = new Set()
    lastT.current = -1
    setRange([0, 2])
    if (scrollRef.current) scrollRef.current.scrollLeft = 0
  }, [prepared])

  const uToX = useCallback((u: number) => {
    const bars = prepared.bars
    const bar = Math.max(0, Math.min(bars - 1, Math.floor(u / BAR_U)))
    const x0 = layout.barX[bar] + 12
    const x1 = layout.barX[bar] + layout.barW[bar] - 6
    const pts: [number, number][] = [[bar * BAR_U, x0], ...(anchorsRef.current.get(bar) ?? []), [(bar + 1) * BAR_U, x1]]
    let px = pts[0]
    for (const p of pts) {
      if (p[0] > u) {
        const span = p[0] - px[0]
        return span > 0 ? px[1] + ((u - px[0]) / span) * (p[1] - px[1]) : px[1]
      }
      if (p[1] >= px[1]) px = p
    }
    return px[1]
  }, [prepared, layout])

  const xToSec = useCallback((x: number) => {
    let bar = 0
    while (bar < prepared.bars - 1 && x >= layout.barX[bar + 1]) bar++
    const frac = Math.max(0, Math.min(1, (x - layout.barX[bar] - 12) / (layout.barW[bar] - 18)))
    return prepared.tempo.secAt((bar + frac) * BAR_U)
  }, [prepared, layout])

  // visible chunk range from scroll position
  const updateRange = useCallback(() => {
    const sc = scrollRef.current
    if (!sc) return
    const lo = sc.scrollLeft - 900
    const hi = sc.scrollLeft + sc.clientWidth + 1400
    let a = 0
    while (a < layout.chunks - 1 && layout.barX[Math.min(prepared.bars - 1, (a + 1) * CHUNK_BARS)] < lo) a++
    let b = a
    while (b < layout.chunks - 1 && layout.barX[Math.min(prepared.bars - 1, b * CHUNK_BARS)] < hi) b++
    setRange(r => (r[0] === a && r[1] === b ? r : [a, b]))
  }, [layout, prepared])

  useEffect(() => { updateRange() }, [updateRange])

  // cursor + follow + note lighting
  useEffect(() => {
    let raf = 0
    const tick = () => {
      raf = requestAnimationFrame(tick)
      const sc = scrollRef.current, cur = cursorRef.current
      if (!sc || !cur) return
      const t = getTime()
      const u = prepared.tempo.unitsAt(t)
      const x = uToX(u)
      cur.style.transform = `translateX(${x}px)`
      const jumped = lastT.current >= 0 && Math.abs(t - lastT.current) > 1.5
      lastT.current = t
      const userBusy = performance.now() - lastInteract.current < 2600
      if ((stateRef.current.playing || jumped) && !userBusy) {
        const target = x - sc.clientWidth * 0.35
        if (stateRef.current.playing) sc.scrollLeft = target
        else sc.scrollTo({ left: target })
        updateRange()
      }
      // light the sounding notes
      const bar = Math.floor(u / BAR_U)
      const chunk = Math.floor(bar / CHUNK_BARS)
      const lit = new Set<SVGElement>()
      for (const c of [chunk - 1, chunk]) {
        for (const n of regRef.current.get(c) ?? []) {
          if (n.u0 <= u && u < n.u1 + 2) lit.add(n.el)
        }
      }
      for (const el of litRef.current) if (!lit.has(el)) el.classList.remove('lit')
      for (const el of lit) if (!litRef.current.has(el)) el.classList.add('lit')
      litRef.current = lit
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [prepared, uToX, getTime, updateRange])

  // spotlight dims the other parts
  useEffect(() => {
    const apply = (root: HTMLElement | null) => {
      if (!root) return
      root.querySelectorAll<SVGElement>('.sheet-part').forEach(g => {
        const idx = Number(g.dataset.part)
        g.style.opacity = spotlight < 0 || idx === spotlight ? '1' : '0.18'
      })
    }
    apply(contentRef.current)
    apply(gutterRef.current)
  }, [spotlight, range, prepared])

  const markInteract = () => { lastInteract.current = performance.now() }

  const onClick = (e: React.MouseEvent) => {
    const rect = contentRef.current!.getBoundingClientRect()
    onSeek(Math.max(0, xToSec(e.clientX - rect.left)))
    lastInteract.current = 0
  }

  const chunkIds = []
  for (let c = range[0]; c <= range[1] && c < layout.chunks; c++) chunkIds.push(c)

  return (
    <div
      ref={scrollRef}
      className="sheet-scroll"
      onScroll={updateRange}
      onWheel={markInteract}
      onPointerDown={markInteract}
      onTouchMove={markInteract}
    >
      <div className="sheet-inner" style={{ width: layout.gutterW + layout.totalW, height: layout.totalH }}>
        <div ref={gutterRef} className="sheet-gutter" style={{ width: layout.gutterW, height: layout.totalH }}>
          <Gutter prepared={prepared} layout={layout} instruments={instruments} colors={colors} />
        </div>
        <div
          ref={contentRef}
          className="sheet-content"
          style={{ left: layout.gutterW, width: layout.totalW, height: layout.totalH }}
          onClick={onClick}
        >
          {chunkIds.map(c => (
            <Chunk
              key={c}
              chunk={c}
              prepared={prepared}
              layout={layout}
              colors={colors}
              spotlight={spotlight}
              onRendered={(bars, regs) => {
                for (const [bar, pts] of bars) anchorsRef.current.set(bar, pts)
                regRef.current.set(c, regs)
              }}
              onUnmount={() => regRef.current.delete(c)}
            />
          ))}
          <div ref={cursorRef} className="sheet-cursor" style={{ height: layout.totalH, ['--accent' as string]: accent }} />
        </div>
      </div>
    </div>
  )
}

// ------------------------------------------------------------------- gutter

function Gutter({ prepared, layout, instruments, colors }: {
  prepared: PreparedScore
  layout: Layout
  instruments: InstrumentInfo[]
  colors: string[]
}) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const div = ref.current!
    div.innerHTML = ''
    const renderer = new Renderer(div, Renderer.Backends.SVG)
    renderer.resize(layout.gutterW, layout.totalH)
    const ctx = renderer.getContext()
    prepared.parts.forEach((part, pi) => {
      const g = ctx.openGroup('sheet-part') as SVGElement
      g.dataset.part = String(part.i)
      const staves: Stave[] = []
      part.staves.forEach((staff, si) => {
        const y = layout.partY[pi] + si * GRAND_EXTRA
        const stave = new Stave(2, y, layout.gutterW - 4, { spaceAboveStaffLn: 0, spaceBelowStaffLn: 0 })
        stave.setBegBarType(Barline.type.NONE).setEndBarType(Barline.type.NONE)
        stave.addClef(staff.clef)
        if (staff.clef !== 'percussion') stave.addKeySignature(prepared.keySpec)
        stave.addTimeSignature('4/4')
        stave.setStyle({ strokeStyle: STAFF_LINE, fillStyle: STAFF_LINE })
        stave.setContext(ctx).draw()
        staves.push(stave)
      })
      if (staves.length === 2) {
        for (const type of [StaveConnector.type.BRACE, StaveConnector.type.SINGLE_LEFT]) {
          const conn = new StaveConnector(staves[0], staves[1])
          conn.setType(type)
          conn.setContext(ctx)
          conn.setStyle?.({ strokeStyle: STAFF_LINE, fillStyle: STAFF_LINE })
          conn.draw()
        }
      }
      ctx.closeGroup()
    })
    const svg = div.querySelector('svg')
    if (svg) svg.style.overflow = 'visible'
  }, [prepared, layout])

  return (
    <>
      <div ref={ref} className="sheet-gutter-svg" />
      {prepared.parts.map((part, pi) => (
        <span
          key={part.i}
          className="sheet-label"
          style={{ top: layout.partY[pi] - 16, ['--c' as string]: colors[part.i] }}
        >
          {instruments[part.i]?.name ?? `Part ${part.i + 1}`}
        </span>
      ))}
    </>
  )
}

// ------------------------------------------------------------------- chunks

interface ChunkProps {
  chunk: number
  prepared: PreparedScore
  layout: Layout
  colors: string[]
  spotlight: number
  onRendered: (anchors: Map<number, [number, number][]>, regs: NoteReg[]) => void
  onUnmount: () => void
}

function Chunk({ chunk, prepared, layout, colors, spotlight, onRendered, onUnmount }: ChunkProps) {
  const ref = useRef<HTMLDivElement>(null)
  const b0 = chunk * CHUNK_BARS
  const b1 = Math.min(prepared.bars, b0 + CHUNK_BARS)
  const left = layout.barX[b0]
  const width = layout.barX[b1 - 1] + layout.barW[b1 - 1] - left

  useEffect(() => {
    try {
      renderChunk()
    } catch (err) {
      console.error(`sheet chunk ${chunk} failed to render:`, err)
    }
    return onUnmount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chunk, prepared, layout, colors])

  function renderChunk() {
    const div = ref.current!
    div.innerHTML = ''
    const renderer = new Renderer(div, Renderer.Backends.SVG)
    renderer.resize(width, layout.totalH)
    const ctx = renderer.getContext()

    interface Drawn { ev: Ev; note: StaveNote }
    // pass 1: build notes + voices per bar, join & format across all parts
    const perBar: { voice: Voice; stave: Stave; notes: StaveNote[]; part: number; staff: number; vi: number; dir: number }[][] = []
    const staveByKey = new Map<string, Stave>()

    for (let bar = b0; bar < b1; bar++) {
      const x = layout.barX[bar] - left
      const w = layout.barW[bar]
      const entries: typeof perBar[number] = []
      prepared.parts.forEach((part, pi) => {
        part.staves.forEach((staff, si) => {
          const y = layout.partY[pi] + si * GRAND_EXTRA
          const stave = new Stave(x, y, w, { spaceAboveStaffLn: 0, spaceBelowStaffLn: 0 })
          stave.setBegBarType(Barline.type.NONE)
          stave.setEndBarType(bar === prepared.bars - 1 ? Barline.type.END : Barline.type.SINGLE)
          stave.setStyle({ strokeStyle: STAFF_LINE, fillStyle: STAFF_LINE })
          staveByKey.set(`${pi}/${si}/${bar}`, stave)
          staff.voices.forEach((byBar, vi) => {
            const evs = byBar[bar] ?? []
            if (!evs.length) return
            const dir = staff.voices.length > 1 ? (vi === 0 ? 1 : -1) : 0
            const notes = evs.map(ev => makeNote(ev, staff.clef, dir, colors[part.i]))
            const voice = new Voice({ numBeats: 4, beatValue: 4 }).setMode(VoiceMode.SOFT)
            voice.addTickables(notes)
            entries.push({ voice, stave, notes, part: pi, staff: si, vi, dir })
          })
        })
      })
      perBar.push(entries)
    }

    // beams before formatting, kept per part so they join its draw group
    const beamsByPart = new Map<number, Beam[]>()
    for (const entries of perBar) {
      for (const en of entries) {
        const beamable = en.notes.filter(n => !(n instanceof GhostNote) && !n.isRest() && n.getDuration() !== 'w' && n.getDuration() !== 'h' && n.getDuration() !== 'q')
        try {
          const beams = Beam.generateBeams(beamable as StaveNote[],
            en.dir !== 0 ? { stemDirection: en.dir, beamRests: false } : { maintainStemDirections: true, beamRests: false })
          const c = colors[prepared.parts[en.part].i]
          for (const b of beams) b.setStyle({ fillStyle: c, strokeStyle: c })
          beamsByPart.set(en.part, [...(beamsByPart.get(en.part) ?? []), ...beams])
        } catch { /* unbeamable groupings are fine unbeamed */ }
      }
    }

    perBar.forEach((entries, bi) => {
      if (!entries.length) return
      const fmt = new Formatter()
      const byStaff = new Map<string, Voice[]>()
      for (const en of entries) {
        const k = `${en.part}/${en.staff}`
        byStaff.set(k, [...(byStaff.get(k) ?? []), en.voice])
      }
      for (const voices of byStaff.values()) fmt.joinVoices(voices)
      const w = layout.barW[b0 + bi]
      try {
        fmt.format(entries.map(en => en.voice), Math.max(30, w - 26))
      } catch { /* soft voices occasionally overflow; draw anyway */ }
    })

    // pass 2: draw grouped by part (for spotlighting); ties, note registry
    // and cursor anchors come along for the ride
    const anchors = new Map<number, [number, number][]>()
    const regs: NoteReg[] = []
    prepared.parts.forEach((part, pi) => {
      const g = ctx.openGroup('sheet-part') as SVGElement
      g.dataset.part = String(part.i)
      const color = colors[part.i]
      for (let bar = b0; bar < b1; bar++) {
        part.staves.forEach((_staff, si) => {
          staveByKey.get(`${pi}/${si}/${bar}`)!.setContext(ctx).draw()
        })
      }
      for (const entries of perBar) {
        for (const en of entries) {
          if (en.part !== pi) continue
          en.voice.draw(ctx, en.stave)
        }
      }
      for (const beam of beamsByPart.get(pi) ?? []) {
        try { beam.setContext(ctx).draw() } catch { /* skip broken beam */ }
      }
      part.staves.forEach(staff => {
        staff.voices.forEach(byBar => {
          const drawn: Drawn[] = []
          for (let bar = b0; bar < b1; bar++) {
            for (const ev of byBar[bar] ?? []) {
              const note = evNote.get(ev)
              if (note) drawn.push({ ev, note })
            }
          }
          const firstNote = drawn.findIndex(d => d.ev.kind === 'note')
          for (let i = 0; i < drawn.length; i++) {
            const { ev, note } = drawn[i]
            if (ev.kind !== 'note') continue
            const el = note.getSVGElement?.()
            if (el) {
              el.classList.add('sheet-note')
              regs.push({ u0: ev.startU, u1: ev.startU + ev.units, el })
            }
            const pts = anchors.get(ev.bar) ?? []
            pts.push([ev.startU, left + note.getAbsoluteX()])
            anchors.set(ev.bar, pts)
            // ties: a tie into the chunk renders as a stub; the rest connect pairs
            if (ev.tiedFromPrev && i === firstNote) {
              drawTie(ctx, color, undefined, note, ev.keys.length)
            }
            if (ev.tieToNext) {
              const next = drawn.slice(i + 1).find(d => d.ev.kind === 'note' && d.ev.startU === ev.startU + ev.units)
              drawTie(ctx, color, note, next?.note, ev.keys.length)
            }
          }
        })
      })
      ctx.closeGroup()
    })

    // bar numbers
    ctx.save()
    ctx.setFont('Inter', 9)
    ctx.setFillStyle('rgba(138,143,163,0.55)')
    for (let bar = b0; bar < b1; bar++) {
      ctx.fillText(String(bar + 1), layout.barX[bar] - left + 4, TOP_PAD - 12)
    }
    ctx.restore()

    // dedupe + sort anchors; report to parent
    for (const [bar, pts] of anchors) {
      const uniq = new Map<number, number>()
      for (const [u, x] of pts.sort((a, b) => a[0] - b[0] || a[1] - b[1])) {
        if (!uniq.has(u)) uniq.set(u, x)
      }
      anchors.set(bar, [...uniq.entries()])
    }
    onRendered(anchors, regs)

    const svg = div.querySelector('svg')
    if (svg) svg.style.overflow = 'visible'
    // apply current spotlight immediately
    div.querySelectorAll<SVGElement>('.sheet-part').forEach(el => {
      const idx = Number(el.dataset.part)
      el.style.opacity = spotlight < 0 || idx === spotlight ? '1' : '0.18'
    })
  }

  return <div ref={ref} className="sheet-chunk" style={{ left, width, height: layout.totalH }} />
}

// note construction ---------------------------------------------------------

const evNote = new WeakMap<Ev, StaveNote>()

function makeNote(ev: Ev, clef: string, dir: number, color: string): StaveNote {
  if (ev.kind === 'ghost') {
    const g = new GhostNote(ev.dur) as unknown as StaveNote
    evNote.set(ev, g)
    return g
  }
  const rest = ev.kind === 'rest'
  const opts: Record<string, unknown> = {
    keys: ev.keys,
    duration: ev.dur + (rest ? 'r' : ''),
    clef,
  }
  if (rest && ev.dur === 'w') opts.alignCenter = true
  if (!rest && dir !== 0) opts.stemDirection = dir
  else if (!rest) opts.autoStem = true
  const note = new StaveNote(opts as unknown as ConstructorParameters<typeof StaveNote>[0])
  for (let d = 0; d < ev.dots; d++) Dot.buildAndAttach([note], { all: true })
  ev.accs.forEach((a, ki) => { if (a) note.addModifier(new Accidental(a), ki) })
  const style = rest
    ? { fillStyle: REST_COLOR, strokeStyle: REST_COLOR }
    : { fillStyle: color, strokeStyle: color }
  note.setStyle(style)
  note.setLedgerLineStyle(style)
  evNote.set(ev, note)
  return note
}

function drawTie(ctx: ReturnType<Renderer['getContext']>, color: string, from?: StaveNote, to?: StaveNote, nKeys = 1) {
  if (!from && !to) return
  const indices = Array.from({ length: nKeys }, (_x, i) => i)
  try {
    const tie = new StaveTie({
      firstNote: from, lastNote: to,
      firstIndexes: indices, lastIndexes: indices,
    })
    tie.setStyle({ fillStyle: color, strokeStyle: color })
    tie.setContext(ctx).draw()
  } catch { /* mismatched chord splits: skip the tie */ }
}
