import { PiecesIndex } from './types'
import { DEFAULT_ACCENT } from './theme'

function fmtDur(sec: number) {
  const m = Math.round(sec / 60)
  return `${m} min`
}

export default function Gallery({ index, onOpen }: { index: PiecesIndex; onOpen: (id: string) => void }) {
  return (
    <div className="app gallery">
      <header className="gallery-header">
        <div className="overline">a listening room</div>
        <h1>Compositions</h1>
        <div className="byline">
          original music, visualized as it plays — each piece a window of attention.
        </div>
      </header>
      <div className="cards">
        {index.pieces.map(p => (
          <button
            key={p.id}
            className="card"
            style={{ ['--accent' as string]: p.accent ?? DEFAULT_ACCENT }}
            onClick={() => onOpen(p.id)}
          >
            <div className="card-title">{p.title}</div>
            {p.subtitle && <div className="card-sub">{p.subtitle}</div>}
            <div className="card-composer">{p.composer}</div>
            {p.concept && <div className="card-concept">{p.concept}</div>}
            <div className="card-meta">
              {p.movements > 1 ? `${p.movements} movements · ` : ''}{fmtDur(p.duration)}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
