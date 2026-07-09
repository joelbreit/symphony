import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { DEFAULT_ACCENT } from '../theme'
import { createEngine, SoundscapeEngine } from './engine'
import ScapeVisual, { layerColors, VizMode } from './ScapeVisual'
import { LayerLevel, SoundscapeManifest } from './types'

function fmt(sec: number) {
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

const VIZ_KEY = 'scape-viz-mode'

export default function SoundscapePlayer({ manifest, baseDir, seed, onBack }: {
  manifest: SoundscapeManifest
  baseDir: string
  seed?: number
  onBack: (() => void) | null
}) {
  const engineRef = useRef<SoundscapeEngine | null>(null)
  const [loaded, setLoaded] = useState(false)
  const [progress, setProgress] = useState(0)
  const [started, setStarted] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [levels, setLevels] = useState<LayerLevel[]>([])
  const [elapsed, setElapsed] = useState(0)
  const [volume, setVolume] = useState(0.7)
  const [showAbout, setShowAbout] = useState(false)
  const [viz, setViz] = useState<VizMode>(
    () => (localStorage.getItem(VIZ_KEY) === 'breathe' ? 'breathe' : 'scroll'))
  const accent = manifest.accent ?? DEFAULT_ACCENT
  const chipColors = useMemo(
    () => layerColors(accent, manifest.layers.length), [accent, manifest])
  const getPlayhead = useCallback(
    () => engineRef.current?.getPlayhead() ?? [], [])

  const setVizMode = (m: VizMode) => {
    setViz(m)
    localStorage.setItem(VIZ_KEY, m)
  }

  useEffect(() => {
    const engine = createEngine(manifest, baseDir, {
      seed,
      debug: new URLSearchParams(window.location.hash.split('?')[1] ?? '').has('debug'),
    })
    engineRef.current = engine
    engine.load((done, total) => setProgress(done / total))
      .then(() => setLoaded(true))
      .catch(err => console.error('failed to load soundscape', err))
    return () => { engine.dispose() }
  }, [manifest, baseDir, seed])

  useEffect(() => {
    const id = setInterval(() => {
      const engine = engineRef.current
      if (!engine) return
      setPlaying(engine.playing())
      setLevels(engine.getLevels())
      setElapsed(engine.elapsed())
    }, 250)
    return () => clearInterval(id)
  }, [])

  // start/resume must stay inside the click's call stack (iOS)
  const togglePlay = () => {
    const engine = engineRef.current
    if (!engine || !loaded) return
    if (!started) {
      setStarted(true)
      engine.start()
    } else if (playing) {
      engine.pause()
    } else {
      engine.resume()
    }
  }

  const onVolume = (v: number) => {
    setVolume(v)
    engineRef.current?.setVolume(v)
  }

  if (!loaded) {
    return (
      <div className="app loading" style={{ ['--accent' as string]: accent }}>
        <div className="load-title">{manifest.title}</div>
        <div className="load-sub">gathering the weather… {Math.round(progress * 100)}%</div>
      </div>
    )
  }

  return (
    <div className={'app scape' + (started ? ' started' : '')}
         style={{ ['--accent' as string]: accent }}>
      <header>
        <div className="title-block">
          <div className="overline">
            {onBack && <button className="back-btn" onClick={onBack} aria-label="All pieces">←</button>}
            {manifest.composer} · endless soundscape
          </div>
          <h1>{manifest.title}</h1>
          {manifest.concept && <div className="byline">{manifest.concept}</div>}
        </div>
      </header>

      <main>
        <div className="scape-visual">
          <div className="scape-glow" data-live={playing ? 'yes' : 'no'} />
          <ScapeVisual
            manifest={manifest}
            accent={accent}
            mode={viz}
            started={started}
            playing={playing}
            getPlayhead={getPlayhead}
          />
        </div>
        <div className="overlay-top">
          <span className="mvt-name">{manifest.key}</span>
          <span className="mvt-key">{manifest.bpm} bpm</span>
          {manifest.about?.length ? (
            <button className="about-btn" onClick={() => setShowAbout(true)}>about</button>
          ) : null}
        </div>
        {!started && (
          <button className="hero-hint" onClick={togglePlay} aria-label="Begin">
            <span className="hint-play">▶</span>
            <span className="hint-text">endless — begin, leave it on</span>
          </button>
        )}
      </main>

      <div className="controls">
        <button className="play-btn" onClick={togglePlay} aria-label={playing ? 'Pause' : 'Play'}>
          {playing ? (
            <svg viewBox="0 0 24 24"><rect x="6" y="5" width="4" height="14" rx="1" /><rect x="14" y="5" width="4" height="14" rx="1" /></svg>
          ) : (
            <svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z" /></svg>
          )}
        </button>
        <input
          className="volume"
          type="range" min="0" max="1" step="0.01" value={volume}
          onChange={e => onVolume(parseFloat(e.target.value))}
          aria-label="Volume"
        />
        <div className="viz-toggle" role="group" aria-label="Visualization mode">
          <button className={viz === 'scroll' ? 'active' : ''}
                  onClick={() => setVizMode('scroll')}>scroll</button>
          <button className={viz === 'breathe' ? 'active' : ''}
                  onClick={() => setVizMode('breathe')}>breathe</button>
        </div>
        <div className="time">{fmt(elapsed)} <span className="time-total">/ ∞</span></div>
      </div>

      <div className="legend">
        {levels.map((l, i) => (
          <span key={l.id} className={'chip' + (l.active ? ' lit' : ' dim')}
                style={{ ['--c' as string]: chipColors[i] ?? accent }}>
            <span className="dot" />{l.name}
          </span>
        ))}
      </div>

      <footer>
        <span>{manifest.layers.length} layers · alignment never repeats</span>
      </footer>

      {showAbout && (
        <div className="about-modal" onClick={() => setShowAbout(false)}>
          <div className="about-card" onClick={e => e.stopPropagation()}>
            <button className="about-close" onClick={() => setShowAbout(false)} aria-label="Close">×</button>
            <h2>{manifest.title}</h2>
            <div className="about-meta">{manifest.composer} · {manifest.key} · {manifest.bpm} bpm</div>
            {(manifest.about ?? []).map((p, i) => <p key={i}>{p}</p>)}
          </div>
        </div>
      )}
    </div>
  )
}
