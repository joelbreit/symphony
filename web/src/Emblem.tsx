// A piece's musical emblem: a few notes on a hand-drawn treble staff.
// States can switch at trigger points (e.g. the Question becoming the Answer).
import { EmblemState } from './types'

const LETTER_STEP: Record<string, number> = { C: 0, D: 1, E: 2, F: 3, G: 4, A: 5, B: 6 }

/** diatonic index: E4 (bottom staff line) = 30 */
function diatonic(p: string): { dia: number; acc: string } {
  const letter = p[0].toUpperCase()
  let i = 1
  let acc = ''
  while (i < p.length && (p[i] === 'b' || p[i] === '#')) {
    acc = p[i] === 'b' ? '♭' : '♯'
    i++
  }
  const octave = parseInt(p.slice(i))
  return { dia: octave * 7 + LETTER_STEP[letter], acc }
}

export default function Emblem({ state, accent }: { state: EmblemState; accent: string }) {
  const lineY = (i: number) => 38 - i * 7          // staff lines, bottom (E4) to top (F5)
  const E4 = 30
  const yOf = (dia: number) => lineY(0) - (dia - E4) * 3.5

  const n = state.notes.length
  const x0 = 28
  const spacing = n > 1 ? Math.min(32, (118 - x0) / (n - 1) + 14) : 0
  const placed = state.notes.map((note, i) => {
    const { dia, acc } = diatonic(note.p)
    return { x: x0 + i * Math.min(30, spacing), y: yOf(dia), dia, acc, accent: note.accent }
  })

  return (
    <svg className="motto" viewBox="0 0 156 48" aria-label={state.label ?? 'musical emblem'}>
      {[0, 1, 2, 3, 4].map(i => (
        <line key={i} x1="4" x2="152" y1={lineY(i)} y2={lineY(i)}
          stroke="currentColor" strokeOpacity="0.35" strokeWidth="0.8" />
      ))}
      {placed.map((p, i) => (
        <g key={i}>
          {/* ledger lines outside the staff */}
          {p.dia <= 28 && Array.from({ length: Math.floor((28 - p.dia) / 2) + 1 }, (_, k) => 28 - k * 2)
            .filter(d => d >= p.dia)
            .map(d => (
              <line key={d} x1={p.x - 7} x2={p.x + 7} y1={yOf(d)} y2={yOf(d)}
                stroke="currentColor" strokeOpacity="0.4" strokeWidth="0.8" />
            ))}
          {p.dia >= 40 && Array.from({ length: Math.floor((p.dia - 40) / 2) + 1 }, (_, k) => 40 + k * 2)
            .filter(d => d <= p.dia)
            .map(d => (
              <line key={d} x1={p.x - 7} x2={p.x + 7} y1={yOf(d)} y2={yOf(d)}
                stroke="currentColor" strokeOpacity="0.4" strokeWidth="0.8" />
            ))}
          {p.acc && (
            <text x={p.x - 11} y={p.y + 3.5} fontSize="11" fill="currentColor"
              fillOpacity="0.85" fontFamily="serif">{p.acc}</text>
          )}
          <ellipse cx={p.x} cy={p.y} rx="4.6" ry="3.4"
            transform={`rotate(-14 ${p.x} ${p.y})`}
            fill={p.accent ? accent : 'currentColor'} />
          <line x1={p.x + 4.2} x2={p.x + 4.2} y1={p.y - 1} y2={p.y - 22}
            stroke={p.accent ? accent : 'currentColor'} strokeWidth="1" />
        </g>
      ))}
      {state.mark && (
        <text x={placed.length ? placed[placed.length - 1].x + 12 : 140} y={14}
          fontSize="13" fill="currentColor" fillOpacity="0.7"
          fontFamily="serif" fontStyle="italic">{state.mark}</text>
      )}
    </svg>
  )
}
