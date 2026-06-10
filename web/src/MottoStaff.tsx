// The Question, hand-drawn: G–C–Eb–D on a tiny staff. Pure SVG, no engraving lib.
export default function MottoStaff({ answered = false }: { answered?: boolean }) {
  // staff lines E4(bottom) G4 B4 D5 F5(top); y spacing 7px
  const lineY = (i: number) => 38 - i * 7 // i=0 bottom line E4
  const pitchY: Record<string, number> = {
    G4: lineY(1),               // on the G line
    C5: lineY(2) - 3.5,         // third space
    Eb5: lineY(3),              // D line +... Eb sits just above D line
    E5: lineY(3) - 3.5,
    D5: lineY(3),               // on the D line
    C5end: lineY(2) - 3.5,
  }
  interface StaffNote { x: number; y: number; gold?: boolean; flat?: boolean }
  const notes: StaffNote[] = answered
    ? [
        { x: 26, y: pitchY.G4 }, { x: 52, y: pitchY.C5 },
        { x: 78, y: pitchY.E5 }, { x: 104, y: pitchY.D5 }, { x: 130, y: pitchY.C5end, gold: true },
      ]
    : [
        { x: 30, y: pitchY.G4 }, { x: 62, y: pitchY.C5 },
        { x: 94, y: pitchY.Eb5, flat: true }, { x: 126, y: pitchY.D5 },
      ]
  return (
    <svg className="motto" viewBox="0 0 156 48" aria-label={answered ? 'the Answer: G C E D C' : 'the Question: G C E-flat D'}>
      {[0, 1, 2, 3, 4].map(i => (
        <line key={i} x1="4" x2="152" y1={lineY(i)} y2={lineY(i)} stroke="currentColor" strokeOpacity="0.35" strokeWidth="0.8" />
      ))}
      {notes.map((n, i) => (
        <g key={i}>
          {n.flat && (
            <text x={n.x - 11} y={n.y + 3.5} fontSize="11" fill="currentColor" fillOpacity="0.85" fontFamily="serif">♭</text>
          )}
          <ellipse
            cx={n.x} cy={n.y} rx="4.6" ry="3.4"
            transform={`rotate(-14 ${n.x} ${n.y})`}
            fill={n.gold ? '#d9a84e' : 'currentColor'}
          />
          <line x1={n.x + 4.2} x2={n.x + 4.2} y1={n.y - 1} y2={n.y - 22} stroke={n.gold ? '#d9a84e' : 'currentColor'} strokeWidth="1" />
        </g>
      ))}
      {!answered && (
        <text x={140} y={pitchY.D5 - 14} fontSize="13" fill="currentColor" fillOpacity="0.7" fontFamily="serif" fontStyle="italic">?</text>
      )}
    </svg>
  )
}
