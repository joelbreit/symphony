import { PiecesIndex } from './types'
import { SoundscapesIndex } from './soundscape/types'
import { DEFAULT_ACCENT } from './theme'

function fmtDur(sec: number) {
  const m = Math.round(sec / 60)
  return `${m} min`
}

export default function Gallery({ index, scapes, tab, onOpen, onOpenScene, onTab }: {
  index: PiecesIndex
  scapes: SoundscapesIndex | null
  tab: 'pieces' | 'scapes'
  onOpen: (id: string) => void
  onOpenScene: (id: string) => void
  onTab: (tab: 'pieces' | 'scapes') => void
}) {
  return (
    <div className="app gallery">
      <header className="gallery-header">
        <div className="overline">a listening room</div>
        <h1>{tab === 'scapes' ? 'Focus' : 'Compositions'}</h1>
        <div className="byline">
          {tab === 'scapes'
            ? 'endless generative soundscapes — rooms with weather, music to do something else to.'
            : 'original music, visualized as it plays — each piece a window of attention.'}
        </div>
        {scapes && scapes.scenes.length > 0 && (
          <div className="tabs">
            <button className={'tab' + (tab === 'pieces' ? ' active' : '')}
                    onClick={() => onTab('pieces')}>compositions</button>
            <button className={'tab' + (tab === 'scapes' ? ' active' : '')}
                    onClick={() => onTab('scapes')}>focus</button>
          </div>
        )}
      </header>
      <div className="cards">
        {tab === 'scapes' && scapes ? (
          scapes.scenes.map(s => (
            <button
              key={s.id}
              className="card"
              style={{ ['--accent' as string]: s.accent ?? DEFAULT_ACCENT }}
              onClick={() => onOpenScene(s.id)}
            >
              <div className="card-title">{s.title}</div>
              {s.concept && <div className="card-concept">{s.concept}</div>}
              <div className="card-meta">endless · generative · {s.layers} layers</div>
            </button>
          ))
        ) : (
          index.pieces.map(p => (
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
          ))
        )}
      </div>
    </div>
  )
}
