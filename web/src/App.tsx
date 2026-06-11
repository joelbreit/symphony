import { useCallback, useEffect, useState } from 'react'
import { PieceManifest, PiecesIndex } from './types'
import Player from './Player'
import Gallery from './Gallery'

const BASE = import.meta.env.BASE_URL

interface Route {
  pieceId: string | null
  movementId?: string
  t?: number
}

function parseHash(): Route {
  const h = window.location.hash.replace(/^#\/?/, '')
  if (!h) return { pieceId: null }
  const [path, query] = h.split('?')
  const params = new URLSearchParams(query ?? '')
  const t = params.get('t')
  return {
    pieceId: path || null,
    movementId: params.get('m') ?? undefined,
    t: t != null ? parseFloat(t) : undefined,
  }
}

export default function App() {
  const [index, setIndex] = useState<PiecesIndex | null>(null)
  const [route, setRoute] = useState<Route>(parseHash())
  const [manifest, setManifest] = useState<PieceManifest | null>(null)

  useEffect(() => {
    fetch(`${BASE}pieces/index.json`)
      .then(r => r.json())
      .then((idx: PiecesIndex) => {
        setIndex(idx)
        // single-piece installs go straight to the piece
        if (!parseHash().pieceId && idx.pieces.length === 1) {
          window.location.replace(`#/${idx.pieces[0].id}`)
        }
      })
      .catch(err => console.error('failed to load pieces index', err))
  }, [])

  useEffect(() => {
    const onHash = () => setRoute(parseHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  useEffect(() => {
    if (!index || !route.pieceId) { setManifest(null); return }
    const entry = index.pieces.find(p => p.id === route.pieceId)
    if (!entry) { setManifest(null); return }
    fetch(`${BASE}${entry.dir}/piece.json`)
      .then(r => r.json())
      .then(setManifest)
      .catch(err => console.error('failed to load piece manifest', err))
  }, [index, route.pieceId])

  const openPiece = useCallback((id: string) => { window.location.hash = `#/${id}` }, [])
  const goBack = useCallback(() => { window.location.hash = '#/' }, [])

  if (!index) {
    return (
      <div className="app loading">
        <div className="load-title">…</div>
      </div>
    )
  }

  if (route.pieceId && manifest) {
    const entry = index.pieces.find(p => p.id === route.pieceId)!
    return (
      <Player
        key={manifest.id}
        manifest={manifest}
        baseDir={`${BASE}${entry.dir}/`}
        entry={{ movementId: route.movementId, t: route.t }}
        onBack={index.pieces.length > 1 ? goBack : null}
      />
    )
  }

  if (route.pieceId && !manifest) {
    return (
      <div className="app loading">
        <div className="load-title">…</div>
        <div className="load-sub">opening the piece</div>
      </div>
    )
  }

  return <Gallery index={index} onOpen={openPiece} />
}
