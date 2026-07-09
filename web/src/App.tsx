import { useCallback, useEffect, useState } from 'react'
import { PieceManifest, PiecesIndex } from './types'
import { SoundscapeManifest, SoundscapesIndex } from './soundscape/types'
import Player from './Player'
import Gallery from './Gallery'
import SoundscapePlayer from './soundscape/SoundscapePlayer'

const BASE = import.meta.env.BASE_URL

interface Route {
  view: 'gallery' | 'scapes' | 'scape' | 'piece'
  pieceId?: string
  sceneId?: string
  movementId?: string
  t?: number
  seed?: number
}

function parseHash(): Route {
  const h = window.location.hash.replace(/^#\/?/, '')
  if (!h) return { view: 'gallery' }
  const [path, query] = h.split('?')
  const params = new URLSearchParams(query ?? '')
  const [head, sub] = path.split('/')
  if (head === 'focus') {
    if (!sub) return { view: 'scapes' }
    const seed = params.get('seed')
    return { view: 'scape', sceneId: sub, seed: seed != null ? parseInt(seed, 10) : undefined }
  }
  const t = params.get('t')
  return {
    view: 'piece',
    pieceId: path,
    movementId: params.get('m') ?? undefined,
    t: t != null ? parseFloat(t) : undefined,
  }
}

export default function App() {
  const [index, setIndex] = useState<PiecesIndex | null>(null)
  const [scapes, setScapes] = useState<SoundscapesIndex | null>(null)
  const [route, setRoute] = useState<Route>(parseHash())
  const [manifest, setManifest] = useState<PieceManifest | null>(null)
  const [scapeManifest, setScapeManifest] = useState<SoundscapeManifest | null>(null)

  useEffect(() => {
    fetch(`${BASE}pieces/index.json`)
      .then(r => r.json())
      .then((idx: PiecesIndex) => {
        setIndex(idx)
        // single-piece installs go straight to the piece
        if (parseHash().view === 'gallery' && idx.pieces.length === 1) {
          window.location.replace(`#/${idx.pieces[0].id}`)
        }
      })
      .catch(err => console.error('failed to load pieces index', err))
    // absent index = tab hidden; the compositions gallery works without it
    fetch(`${BASE}soundscapes/index.json`)
      .then(r => (r.ok ? r.json() : null))
      .then((idx: SoundscapesIndex | null) => setScapes(idx))
      .catch(() => setScapes(null))
  }, [])

  useEffect(() => {
    const onHash = () => setRoute(parseHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  useEffect(() => {
    if (!index || route.view !== 'piece') { setManifest(null); return }
    const entry = index.pieces.find(p => p.id === route.pieceId)
    if (!entry) { setManifest(null); return }
    fetch(`${BASE}${entry.dir}/piece.json`)
      .then(r => r.json())
      .then(setManifest)
      .catch(err => console.error('failed to load piece manifest', err))
  }, [index, route.view, route.pieceId])

  useEffect(() => {
    if (!scapes || route.view !== 'scape') { setScapeManifest(null); return }
    const entry = scapes.scenes.find(s => s.id === route.sceneId)
    if (!entry) { setScapeManifest(null); return }
    fetch(`${BASE}${entry.dir}/soundscape.json`)
      .then(r => r.json())
      .then(setScapeManifest)
      .catch(err => console.error('failed to load soundscape manifest', err))
  }, [scapes, route.view, route.sceneId])

  const openPiece = useCallback((id: string) => { window.location.hash = `#/${id}` }, [])
  const openScene = useCallback((id: string) => { window.location.hash = `#/focus/${id}` }, [])
  const setTab = useCallback((tab: 'pieces' | 'scapes') => {
    window.location.hash = tab === 'scapes' ? '#/focus' : '#/'
  }, [])
  const goBack = useCallback(() => { window.location.hash = '#/' }, [])
  const backToScapes = useCallback(() => { window.location.hash = '#/focus' }, [])

  if (!index) {
    return (
      <div className="app loading">
        <div className="load-title">…</div>
      </div>
    )
  }

  if (route.view === 'piece' && manifest) {
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

  if (route.view === 'scape' && scapeManifest) {
    const entry = scapes!.scenes.find(s => s.id === route.sceneId)!
    return (
      <SoundscapePlayer
        key={`${scapeManifest.id}:${route.seed ?? ''}`}
        manifest={scapeManifest}
        baseDir={`${BASE}${entry.dir}/`}
        seed={route.seed}
        onBack={backToScapes}
      />
    )
  }

  if (route.view === 'piece' || route.view === 'scape') {
    return (
      <div className="app loading">
        <div className="load-title">…</div>
        <div className="load-sub">opening {route.view === 'scape' ? 'the soundscape' : 'the piece'}</div>
      </div>
    )
  }

  return (
    <Gallery
      index={index}
      scapes={scapes}
      tab={route.view === 'scapes' && scapes ? 'scapes' : 'pieces'}
      onOpen={openPiece}
      onOpenScene={openScene}
      onTab={setTab}
    />
  )
}
