// Two ways of seeing the weather.
//
// 'scroll' — the familiar roll: each layer's loop unwinds past a playhead,
// exactly in step with the engine (phase comes from the scheduler's own
// loop grid via getPlayhead, so what you see is what is sounding).
//
// 'breathe' — no timeline at all: every sounding note is a soft orb that
// blooms on its attack, breathes while it holds, and cools after release.
// Vertical position is pitch, size is velocity and length, brightness
// follows the conductor's live layer gains — the mix drifting IS the light
// drifting.
import { useEffect, useMemo, useRef } from 'react'
import { hexToRgb, RGB } from '../theme'
import { LayerPlayhead, NoteEvt, SoundscapeManifest } from './types'

export type VizMode = 'scroll' | 'breathe'

// ---- color: fan the layer hues around the scene accent so the layers read
// as one weather system, not confetti (the legend chips use these too)
function rgbToHsl({ r, g, b }: RGB): [number, number, number] {
  const rn = r / 255, gn = g / 255, bn = b / 255
  const max = Math.max(rn, gn, bn), min = Math.min(rn, gn, bn)
  const l = (max + min) / 2
  if (max === min) return [0, 0, l]
  const d = max - min
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
  let h: number
  if (max === rn) h = (gn - bn) / d + (gn < bn ? 6 : 0)
  else if (max === gn) h = (bn - rn) / d + 2
  else h = (rn - gn) / d + 4
  return [h * 60, s, l]
}

function hslToRgb(h: number, s: number, l: number): RGB {
  const c = (1 - Math.abs(2 * l - 1)) * s
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1))
  const m = l - c / 2
  const [r, g, b] =
    h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] :
    h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x]
  return {
    r: Math.round((r + m) * 255),
    g: Math.round((g + m) * 255),
    b: Math.round((b + m) * 255),
  }
}

function toHex({ r, g, b }: RGB): string {
  const two = (v: number) => v.toString(16).padStart(2, '0')
  return `#${two(r)}${two(g)}${two(b)}`
}

export function layerColors(accent: string, n: number): string[] {
  const [h, s, l] = rgbToHsl(hexToRgb(accent))
  return Array.from({ length: n }, (_, i) => {
    const spread = n > 1 ? i / (n - 1) - 0.5 : 0
    return toHex(hslToRgb(
      (h + spread * 80 + 360) % 360,
      Math.min(1, s + 0.06),
      Math.min(0.8, Math.max(0.45, l + spread * 0.18 + 0.03)),
    ))
  })
}

function rgba(c: RGB, a: number) {
  return `rgba(${c.r},${c.g},${c.b},${a})`
}

// deterministic per-note jitter so orbs keep their places across frames
function hash01(i: number): number {
  let x = Math.imul(i + 1, 2654435761) >>> 0
  x ^= x >>> 13
  x = Math.imul(x, 0x5bd1e995) >>> 0
  x ^= x >>> 15
  return x / 4294967296
}

const smooth = (t: number) => t * t * (3 - 2 * t)
const WHITE: RGB = { r: 240, g: 238, b: 228 }

function mix(a: RGB, b: RGB, t: number): RGB {
  return {
    r: Math.round(a.r + (b.r - a.r) * t),
    g: Math.round(a.g + (b.g - a.g) * t),
    b: Math.round(a.b + (b.b - a.b) * t),
  }
}

interface Props {
  manifest: SoundscapeManifest
  accent: string
  mode: VizMode
  started: boolean
  playing: boolean
  getPlayhead: () => LayerPlayhead[]
}

export default function ScapeVisual(props: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wrapRef = useRef<HTMLDivElement>(null)

  const data = useMemo(() => {
    const layers = props.manifest.layers.map(l => ({
      base: l.gain || 0.5,
      variants: l.variants.map(v => ({
        loop: v.loopSeconds,
        notes: (v.notes ?? []) as NoteEvt[],
      })),
    }))
    let lo = 127, hi = 0, maxEnd = 0
    for (const l of layers)
      for (const v of l.variants)
        for (const n of v.notes) {
          if (n[2] < lo) lo = n[2]
          if (n[2] > hi) hi = n[2]
          if (n[0] + n[1] > maxEnd) maxEnd = n[0] + n[1]
        }
    if (lo > hi) { lo = 40; hi = 90 }
    return { layers, pmin: Math.max(0, lo - 3), pmax: Math.min(127, hi + 4), maxEnd }
  }, [props.manifest])

  const rgbColors = useMemo(
    () => layerColors(props.accent, props.manifest.layers.length).map(hexToRgb),
    [props.accent, props.manifest])
  const accentRgb = useMemo(() => hexToRgb(props.accent), [props.accent])

  const stateRef = useRef({ ...props, data, rgbColors, accentRgb })
  stateRef.current = { ...props, data, rgbColors, accentRgb }

  useEffect(() => {
    const canvas = canvasRef.current!
    const wrap = wrapRef.current!
    const ctx = canvas.getContext('2d')!
    let raf = 0
    let w = 0, h = 0, dpr = 1

    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2)
      w = wrap.clientWidth
      h = wrap.clientHeight
      canvas.width = Math.round(w * dpr)
      canvas.height = Math.round(h * dpr)
      canvas.style.width = w + 'px'
      canvas.style.height = h + 'px'
    }
    resize()
    const ro = new ResizeObserver(resize)
    ro.observe(wrap)

    const laneY = (pitch: number) => {
      const s = stateRef.current
      const span = s.data.pmax - s.data.pmin
      return h - ((pitch - s.data.pmin) / span) * h
    }

    // pre-start: the whole weather at rest — every layer's first variant laid
    // across its own loop, faintly breathing (the piece player's overview idiom)
    const drawOverview = () => {
      const s = stateRef.current
      const breathe = 0.8 + 0.2 * Math.sin(performance.now() / 2600)
      const span = s.data.pmax - s.data.pmin
      const noteH = Math.max(2, (h / span) * 1.7)
      s.data.layers.forEach((l, li) => {
        const v = l.variants[0]
        if (!v || !v.notes.length) return
        const c = s.rgbColors[li]
        for (const n of v.notes) {
          const x = (n[0] / v.loop) * w
          const wd = Math.max((n[1] / v.loop) * w, 2)
          ctx.fillStyle = rgba(c, (0.08 + (n[3] / 127) * 0.22) * breathe)
          ctx.fillRect(x, laneY(n[2]) - noteH / 2, Math.min(wd, w - x), noteH)
        }
      })
    }

    const drawScroll = (heads: LayerPlayhead[]) => {
      const s = stateRef.current
      const span = s.data.pmax - s.data.pmin
      const noteH = Math.max(2.5, (h / span) * 1.8)
      const windowSec = Math.min(26, Math.max(14, w / 60))
      const pxPerSec = w / windowSec
      const playheadX = w * 0.38
      const tLeft = -playheadX / pxPerSec          // times relative to now
      const tRight = (w - playheadX) / pxPerSec

      // faint octave lanes
      ctx.strokeStyle = 'rgba(30,38,56,0.5)'
      ctx.lineWidth = 1
      for (let p = Math.ceil(s.data.pmin / 12) * 12; p <= s.data.pmax; p += 12) {
        const y = laneY(p)
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke()
      }

      // the column of light — the window of the present
      const colW = Math.min(110, w * 0.16)
      const grad = ctx.createLinearGradient(playheadX - colW / 2, 0, playheadX + colW / 2, 0)
      grad.addColorStop(0, 'rgba(233,228,210,0)')
      grad.addColorStop(0.5, 'rgba(233,228,210,0.06)')
      grad.addColorStop(1, 'rgba(233,228,210,0)')
      ctx.fillStyle = grad
      ctx.fillRect(playheadX - colW / 2, 0, colW, h)

      s.data.layers.forEach((l, li) => {
        const head = heads[li]
        if (!head) return
        const presence = Math.min(1, head.gain / l.base)
        if (presence < 0.02) return
        const c = s.rgbColors[li]
        const loop = head.loopSeconds
        const jLo = Math.floor((tLeft + head.phase - s.data.maxEnd) / loop)
        const jHi = Math.ceil((tRight + head.phase) / loop)
        for (let j = jLo; j <= jHi; j++) {
          // future iterations sound the queued variant; past/current the live one
          const vi = j >= 1 ? head.pendingVariant : head.variant
          const v = l.variants[vi]
          if (!v) continue
          const off = j * loop - head.phase
          for (const n of v.notes) {
            const rel = off + n[0]
            if (rel > tRight) break
            const end = rel + n[1]
            if (end < tLeft) continue
            const x = (rel - tLeft) * pxPerSec
            const wd = Math.max(n[1] * pxPerSec - 1, 2)
            const y = laneY(n[2]) - noteH / 2
            const active = rel <= 0 && end >= 0
            let alpha: number
            if (active) alpha = 0.95
            else if (rel > 0) alpha = 0.2 + (n[3] / 127) * 0.15   // yet to sound
            else alpha = Math.max(0.08, 0.75 - ((-end) / 2.6) * 0.6) // cooling
            alpha *= 0.25 + 0.75 * presence
            if (active) {
              ctx.shadowColor = rgba(c, 0.85)
              ctx.shadowBlur = 9
            }
            ctx.fillStyle = rgba(c, alpha)
            ctx.fillRect(x, y, wd, noteH)
            ctx.shadowBlur = 0
          }
        }
      })

      // playhead core
      ctx.fillStyle = rgba(s.accentRgb, 0.9)
      ctx.fillRect(playheadX - 0.75, 0, 1.5, h)
    }

    const drawBreathe = (heads: LayerPlayhead[]) => {
      const s = stateRef.current
      const nowS = performance.now() / 1000
      const sizeK = Math.max(0.65, Math.min(1.6, Math.min(w, h) / 560))
      const maxR = Math.min(w, h) * 0.17
      ctx.globalCompositeOperation = 'lighter'
      s.data.layers.forEach((l, li) => {
        const head = heads[li]
        if (!head) return
        const presence = Math.min(1, head.gain / l.base)
        if (presence < 0.02) return
        const loop = head.loopSeconds
        const v = l.variants[head.variant]
        if (!v) return
        // j=-1 catches voices still ringing (or releasing) across the seam
        for (let j = -1; j <= 0; j++) {
          const off = j * loop - head.phase
          for (let ni = 0; ni < v.notes.length; ni++) {
            const n = v.notes[ni]
            const since = -(off + n[0])   // seconds since this note began
            if (since < 0) break          // notes are sorted: rest are unborn
            const dur = Math.max(n[1], 0.15)
            const attack = Math.min(0.8, Math.max(0.05, dur * 0.18))
            const release = Math.min(5, Math.max(1.2, dur * 0.4))
            let env: number
            if (since < attack) env = smooth(since / attack)
            else if (since <= dur) env = 1
            else {
              const e = (since - dur) / release
              if (e >= 1) continue        // long gone; earlier notes may not be
              env = smooth(1 - e)
            }
            const seed = li * 131 + ni * 17
            const phi = hash01(seed) * Math.PI * 2
            const breath = 1 + 0.13 * Math.sin(nowS * (2 * Math.PI / (4 + hash01(seed + 5) * 4)) + phi)
            const velN = Math.min(1, n[3] / 90)
            // golden-ratio strides spread each layer's voices across the
            // width — seeded hash alone bunches the few sounding notes
            const gx = (ni * 0.61803398875 + hash01(li * 29)) % 1
            const x = (0.07 + 0.86 * gx) * w
              + Math.sin(nowS * 0.25 + phi) * w * 0.015
            const y = laneY(n[2]) + Math.sin(nowS * 0.4 + phi * 1.7) * 3
            const R = Math.min(maxR,
              (7 + velN * 17) * (0.75 + Math.min(dur, 12) * 0.09)
              * sizeK * env * breath * (0.6 + 0.55 * presence))
            if (R < 0.5) continue
            const alpha = env * (0.26 + 0.58 * velN) * (0.3 + 0.7 * presence)
            // the attack flashes toward white, then settles into the layer color
            const flash = Math.max(0, 1 - since / (attack + 0.25))
            const col = mix(s.rgbColors[li], WHITE, flash * 0.45)
            const g = ctx.createRadialGradient(x, y, 0, x, y, R)
            g.addColorStop(0, rgba(col, alpha))
            g.addColorStop(0.45, rgba(col, alpha * 0.45))
            g.addColorStop(1, rgba(col, 0))
            ctx.fillStyle = g
            ctx.beginPath()
            ctx.arc(x, y, R, 0, Math.PI * 2)
            ctx.fill()
          }
        }
      })
      ctx.globalCompositeOperation = 'source-over'
    }

    const draw = () => {
      const s = stateRef.current
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.clearRect(0, 0, w, h)
      if (!s.started) {
        drawOverview()
      } else {
        const heads = s.getPlayhead()
        if (heads.length) {
          if (s.mode === 'scroll') drawScroll(heads)
          else drawBreathe(heads)
        }
      }
      raf = requestAnimationFrame(draw)
    }
    raf = requestAnimationFrame(draw)
    return () => { cancelAnimationFrame(raf); ro.disconnect() }
  }, [])

  return (
    <div ref={wrapRef} className="viz-wrap">
      <canvas ref={canvasRef} />
    </div>
  )
}
