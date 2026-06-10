import { useEffect, useRef } from 'react'
import { NoteTuple } from './types'
import { INSTRUMENT_COLORS, PITCH_MIN, PITCH_MAX } from './theme'

interface Props {
  notesByMvt: NoteTuple[][]
  durations: number[]
  numerals: string[]
  getGlobalTime: () => number
  onSeek: (globalSec: number) => void
}

export default function Minimap({ notesByMvt, durations, numerals, getGlobalTime, onSeek }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wrapRef = useRef<HTMLDivElement>(null)
  const baseRef = useRef<HTMLCanvasElement | null>(null)
  const propsRef = useRef({ notesByMvt, durations, getGlobalTime })
  propsRef.current = { notesByMvt, durations, getGlobalTime }

  const total = durations.reduce((a, b) => a + b, 0)
  const starts = durations.reduce<number[]>((acc, d, i) => {
    acc.push(i === 0 ? 0 : acc[i - 1] + durations[i - 1])
    return acc
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current!
    const wrap = wrapRef.current!
    const ctx = canvas.getContext('2d')!
    let raf = 0
    let w = 0, h = 0, dpr = 1

    const renderBase = () => {
      const base = document.createElement('canvas')
      base.width = canvas.width
      base.height = canvas.height
      const bctx = base.getContext('2d')!
      bctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      const scale = w / Math.max(total, 1)
      const span = PITCH_MAX - PITCH_MIN
      const pad = 4
      for (let m = 0; m < notesByMvt.length; m++) {
        const x0 = starts[m] * scale
        for (const [t, d, p, inst, v] of notesByMvt[m]) {
          const a = 0.18 + (v / 127) * 0.5
          bctx.fillStyle = INSTRUMENT_COLORS[inst] + Math.round(a * 255).toString(16).padStart(2, '0')
          const y = pad + (1 - (p - PITCH_MIN) / span) * (h - pad * 2)
          bctx.fillRect(x0 + t * scale, y, Math.max(d * scale, 0.8), 1.4)
        }
      }
      // movement boundaries + numerals
      bctx.fillStyle = 'rgba(217,168,78,0.55)'
      bctx.font = '600 10px "Cormorant Garamond", serif'
      for (let m = 1; m < starts.length; m++) {
        bctx.fillRect(starts[m] * scale, 0, 1, h)
      }
      bctx.fillStyle = 'rgba(232,230,223,0.5)'
      for (let m = 0; m < starts.length; m++) {
        bctx.fillText(numerals[m], starts[m] * scale + 4, 11)
      }
      baseRef.current = base
    }

    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2)
      w = wrap.clientWidth
      h = wrap.clientHeight
      canvas.width = Math.round(w * dpr)
      canvas.height = Math.round(h * dpr)
      canvas.style.width = w + 'px'
      canvas.style.height = h + 'px'
      renderBase()
    }
    resize()
    const ro = new ResizeObserver(resize)
    ro.observe(wrap)

    const draw = () => {
      const t = propsRef.current.getGlobalTime()
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      if (baseRef.current) ctx.drawImage(baseRef.current, 0, 0)
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      const x = (t / Math.max(total, 1)) * w
      // dim the future
      ctx.fillStyle = 'rgba(11,14,20,0.5)'
      ctx.fillRect(x, 0, w - x, h)
      // playhead
      ctx.fillStyle = '#d9a84e'
      ctx.fillRect(x - 0.75, 0, 1.5, h)
      raf = requestAnimationFrame(draw)
    }
    raf = requestAnimationFrame(draw)
    return () => { cancelAnimationFrame(raf); ro.disconnect() }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [notesByMvt, total])

  const seekFromEvent = (e: React.PointerEvent) => {
    const rect = wrapRef.current!.getBoundingClientRect()
    const frac = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width))
    onSeek(frac * total)
  }

  return (
    <div
      ref={wrapRef}
      className="minimap"
      onPointerDown={e => { (e.target as Element).setPointerCapture(e.pointerId); seekFromEvent(e) }}
      onPointerMove={e => { if (e.buttons & 1) seekFromEvent(e) }}
    >
      <canvas ref={canvasRef} />
    </div>
  )
}
