import { useEffect, useRef } from 'react'
import { NoteTuple } from './types'
import { INSTRUMENT_COLORS, PITCH_MIN, PITCH_MAX } from './theme'

interface Props {
  notes: NoteTuple[]
  duration: number
  getTime: () => number
  playing: boolean
  started: boolean
  spotlight: number
}

interface RGB { r: number; g: number; b: number }

const rgbCache: RGB[] = INSTRUMENT_COLORS.map(hex => ({
  r: parseInt(hex.slice(1, 3), 16),
  g: parseInt(hex.slice(3, 5), 16),
  b: parseInt(hex.slice(5, 7), 16),
}))

function rgba(c: RGB, a: number) {
  return `rgba(${c.r},${c.g},${c.b},${a})`
}

/** binary search: first index with note start >= t */
function lowerBound(notes: NoteTuple[], t: number): number {
  let lo = 0, hi = notes.length
  while (lo < hi) {
    const mid = (lo + hi) >> 1
    if (notes[mid][0] < t) lo = mid + 1
    else hi = mid
  }
  return lo
}

export default function PianoRoll({ notes, duration, getTime, playing, started, spotlight }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wrapRef = useRef<HTMLDivElement>(null)
  const stateRef = useRef({ notes, duration, playing, started, spotlight, getTime })
  stateRef.current = { notes, duration, playing, started, spotlight, getTime }
  const maxDurRef = useRef(8)

  useEffect(() => {
    maxDurRef.current = notes.reduce((m, n) => Math.max(m, n[1]), 1)
  }, [notes])

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
      const span = PITCH_MAX - PITCH_MIN
      return h - ((pitch - PITCH_MIN) / span) * h
    }

    const drawLanes = () => {
      ctx.strokeStyle = 'rgba(30,38,56,0.55)'
      ctx.lineWidth = 1
      ctx.fillStyle = 'rgba(138,143,163,0.4)'
      ctx.font = '9px Inter, sans-serif'
      for (let p = 24; p <= 96; p += 12) {
        const y = laneY(p)
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(w, y)
        ctx.stroke()
        if (w > 640) ctx.fillText('C' + (p / 12 - 1), 6, y - 3)
      }
    }

    const draw = () => {
      const s = stateRef.current
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.clearRect(0, 0, w, h)
      drawLanes()
      const laneH = h / (PITCH_MAX - PITCH_MIN)
      const noteH = Math.max(2, laneH * 1.7)

      if (!s.started) {
        // overview: the whole movement as a constellation, gently breathing
        const breathe = 0.86 + 0.14 * Math.sin(performance.now() / 2600)
        const scale = w / Math.max(s.duration, 1)
        for (let i = 0; i < s.notes.length; i++) {
          const [t, d, p, inst, v] = s.notes[i]
          const a = (0.16 + (v / 127) * 0.45) * breathe
          ctx.fillStyle = rgba(rgbCache[inst], a)
          ctx.fillRect(t * scale, laneY(p) - noteH / 2, Math.max(d * scale, 1.5), noteH)
        }
        raf = requestAnimationFrame(draw)
        return
      }

      const t = s.getTime()
      const windowSec = Math.min(16, Math.max(7, w / 80))
      const pxPerSec = w / windowSec
      const playheadX = w * 0.38
      const timeLeft = t - playheadX / pxPerSec
      const timeRight = t + (w - playheadX) / pxPerSec

      // the column of light — the window of the present
      const colW = Math.min(110, w * 0.16)
      const grad = ctx.createLinearGradient(playheadX - colW / 2, 0, playheadX + colW / 2, 0)
      grad.addColorStop(0, 'rgba(233,228,210,0)')
      grad.addColorStop(0.5, 'rgba(233,228,210,0.065)')
      grad.addColorStop(1, 'rgba(233,228,210,0)')
      ctx.fillStyle = grad
      ctx.fillRect(playheadX - colW / 2, 0, colW, h)

      const start = lowerBound(s.notes, timeLeft - maxDurRef.current)
      for (let i = start; i < s.notes.length; i++) {
        const n = s.notes[i]
        if (n[0] > timeRight) break
        const [nt, nd, p, inst, v] = n
        const end = nt + nd
        if (end < timeLeft) continue
        const x = (nt - timeLeft) * pxPerSec
        const wd = Math.max(nd * pxPerSec - 1, 2)
        const y = laneY(p) - noteH / 2
        const active = nt <= t && end >= t
        let alpha: number
        if (active) {
          alpha = 0.95
        } else if (nt > t) {
          alpha = 0.22 + (v / 127) * 0.13          // the unkindled future
        } else {
          const fade = (t - end) / 2.6              // memory, cooling
          alpha = Math.max(0.1, 0.8 - fade * 0.65)
        }
        if (s.spotlight >= 0 && inst !== s.spotlight) alpha *= 0.18
        const c = rgbCache[inst]
        if (active && (s.spotlight < 0 || inst === s.spotlight)) {
          ctx.shadowColor = rgba(c, 0.9)
          ctx.shadowBlur = 9
        }
        ctx.fillStyle = rgba(c, alpha)
        ctx.fillRect(x, y, wd, noteH)
        ctx.shadowBlur = 0
      }

      // playhead core
      ctx.fillStyle = 'rgba(217,168,78,0.9)'
      ctx.fillRect(playheadX - 0.75, 0, 1.5, h)

      raf = requestAnimationFrame(draw)
    }
    raf = requestAnimationFrame(draw)
    return () => { cancelAnimationFrame(raf); ro.disconnect() }
  }, [])

  return (
    <div ref={wrapRef} className="roll-wrap">
      <canvas ref={canvasRef} />
    </div>
  )
}
