import { InstrumentInfo, PieceTheme } from './types'

export const BG = '#0b0e14'
export const DEFAULT_ACCENT = '#d9a84e'

// Family color ramps — members of a family get successive shades (light -> dark)
// so the orchestra reads as choirs, not confetti. Pieces may override any
// instrument via theme.instrumentColors.
const FAMILY_RAMPS: Record<string, string[]> = {
  strings: ['#ffd27a', '#f0b75a', '#d99a43', '#b87c33', '#8f5d28', '#6f4a22'],
  winds: ['#9fe8e0', '#6cd3c8', '#45b5ad', '#2e8f8a', '#23706c', '#1a5450'],
  brass: ['#e8a08a', '#f07d6a', '#c05a50', '#a04840', '#7e3a34'],
  color: ['#cfd9ff', '#a98fd6', '#7d6aa8', '#5d5878', '#474360'],
  voices: ['#f2d8c4', '#e0b89a', '#c79a78', '#a87e5e'],
  keys: ['#d8e6c3', '#b3cd96', '#8fb070', '#6e9152'],
  other: ['#aab3c5', '#8a93a8', '#6b7488', '#525a6e'],
}

export function resolveColors(instruments: InstrumentInfo[], theme?: PieceTheme): string[] {
  const counters: Record<string, number> = {}
  return instruments.map(inst => {
    const override = theme?.instrumentColors?.[inst.id]
    if (override) return override
    const ramp = FAMILY_RAMPS[inst.family] ?? FAMILY_RAMPS.other
    const n = counters[inst.family] ?? 0
    counters[inst.family] = n + 1
    return ramp[n % ramp.length]
  })
}

export interface RGB { r: number; g: number; b: number }

export function hexToRgb(hex: string): RGB {
  return {
    r: parseInt(hex.slice(1, 3), 16),
    g: parseInt(hex.slice(3, 5), 16),
    b: parseInt(hex.slice(5, 7), 16),
  }
}

export function pitchRange(notesByMvt: { length: number }[][] | number[][][]): [number, number] {
  let lo = 127, hi = 0
  for (const notes of notesByMvt as number[][][]) {
    for (const n of notes) {
      const p = n[2] as number
      if (p < lo) lo = p
      if (p > hi) hi = p
    }
  }
  if (lo > hi) return [24, 105]
  return [Math.max(0, lo - 3), Math.min(127, hi + 3)]
}
