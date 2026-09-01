import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Moment, NoteTuple, PieceManifest } from './types'
import { DEFAULT_ACCENT, pitchRange, resolveColors } from './theme'
import PianoRoll from './PianoRoll'
import ScoreView from './ScoreView'
import Minimap from './Minimap'
import Emblem from './Emblem'

interface Entry { movementId?: string; t?: number }

interface Props {
  manifest: PieceManifest
  baseDir: string                 // absolute-ish prefix for piece assets
  entry?: Entry | null
  onBack?: (() => void) | null
}

function fmt(sec: number) {
  if (!isFinite(sec) || sec < 0) sec = 0
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export default function Player({ manifest, baseDir, entry, onBack }: Props) {
  const [notesByMvt, setNotesByMvt] = useState<NoteTuple[][] | null>(null)
  const [mvt, setMvt] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [started, setStarted] = useState(false)
  const [userSpotlight, setUserSpotlight] = useState(-1)
  const [section, setSection] = useState('')
  const [moment, setMoment] = useState<Moment | null>(null)
  const [emblemState, setEmblemState] = useState(0)
  const [showAbout, setShowAbout] = useState(false)
  const [showScore, setShowScore] = useState(false)
  const [clock, setClock] = useState(0)
  const audioRef = useRef<HTMLAudioElement>(null)
  const pendingSeek = useRef<number | null>(null)
  const mvtRef = useRef(0)
  mvtRef.current = mvt

  const accent = manifest.theme?.accent ?? DEFAULT_ACCENT
  const colors = useMemo(() => resolveColors(manifest.instruments, manifest.theme), [manifest])
  const instIndex = useMemo(() => {
    const m: Record<string, number> = {}
    manifest.instruments.forEach((inst, i) => { m[inst.id] = i })
    return m
  }, [manifest])

  useEffect(() => {
    Promise.all(manifest.movements.map(mv => fetch(`${baseDir}${mv.notes}`).then(r => r.json())))
      .then(all => setNotesByMvt(all as NoteTuple[][]))
      .catch(err => console.error('failed to load piece data', err))
  }, [manifest, baseDir])

  const [pitchMin, pitchMax] = useMemo(
    () => (notesByMvt ? pitchRange(notesByMvt) : [24, 105] as [number, number]),
    [notesByMvt],
  )

  const durations = manifest.movements.map(m => m.duration)
  const starts = durations.reduce<number[]>((acc, d, i) => {
    acc.push(i === 0 ? 0 : acc[i - 1] + durations[i - 1])
    return acc
  }, [])
  const total = durations.reduce((a, b) => a + b, 0)

  const getLocalTime = useCallback(() => audioRef.current?.currentTime ?? 0, [])
  const getGlobalTime = useCallback(
    () => (starts[mvtRef.current] ?? 0) + (audioRef.current?.currentTime ?? 0),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [manifest],
  )

  // clock, section label, moments, emblem state
  useEffect(() => {
    const id = setInterval(() => {
      const t = audioRef.current?.currentTime ?? 0
      setClock(t)
      const mv = manifest.movements[mvtRef.current]
      const secs = mv.sections ?? []
      let label = secs[0]?.[1] ?? ''
      for (const [st, name] of secs) {
        if (t >= st - 0.25) label = name
        else break
      }
      setSection(label)
      // active moment
      const active = (manifest.moments ?? []).find(
        mo => mo.movement === mv.id && t >= mo.time && t < mo.time + (mo.hold ?? 8),
      )
      setMoment(active ?? null)
      // emblem state: highest-index state whose trigger has been satisfied
      let st = 0
      manifest.emblem?.states.forEach((es, i) => {
        if (es.trigger && es.trigger.movement === mv.id && t >= es.trigger.time) st = i
      })
      setEmblemState(st)
    }, 250)
    return () => clearInterval(id)
  }, [manifest])

  const loadMovement = useCallback((i: number, seekTo: number | null, andPlay: boolean) => {
    const audio = audioRef.current!
    setMvt(i)
    pendingSeek.current = seekTo
    audio.src = `${baseDir}${manifest.movements[i].audio}`
    audio.load()
    // play() must be called inside the user gesture's call stack (iOS Safari)
    if (andPlay) audio.play().catch(() => setPlaying(false))
  }, [manifest, baseDir])

  // deep-link entry: land seeked and paused, roll visible
  const entryApplied = useRef(false)
  useEffect(() => {
    if (!notesByMvt || entryApplied.current || !entry) return
    entryApplied.current = true
    const idx = Math.max(0, manifest.movements.findIndex(m => m.id === entry.movementId))
    if (entry.movementId || entry.t != null) {
      setStarted(true)
      loadMovement(idx === -1 ? 0 : idx, entry.t ?? 0, false)
    }
  }, [notesByMvt, entry, manifest, loadMovement])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return
    const onMeta = () => {
      if (pendingSeek.current != null) {
        audio.currentTime = pendingSeek.current
        pendingSeek.current = null
      }
    }
    const onEnded = () => {
      if (mvtRef.current < manifest.movements.length - 1) {
        loadMovement(mvtRef.current + 1, 0, true)
      } else {
        setPlaying(false)
      }
    }
    const onPlay = () => setPlaying(true)
    const onPause = () => setPlaying(false)
    audio.addEventListener('loadedmetadata', onMeta)
    audio.addEventListener('ended', onEnded)
    audio.addEventListener('play', onPlay)
    audio.addEventListener('pause', onPause)
    return () => {
      audio.removeEventListener('loadedmetadata', onMeta)
      audio.removeEventListener('ended', onEnded)
      audio.removeEventListener('play', onPlay)
      audio.removeEventListener('pause', onPause)
    }
  }, [loadMovement, notesByMvt, manifest])

  const togglePlay = () => {
    const audio = audioRef.current!
    if (!started) {
      setStarted(true)
      loadMovement(mvt, null, true)
      return
    }
    if (!audio.src) {
      loadMovement(mvt, null, true)
      return
    }
    if (audio.paused) audio.play().catch(() => {})
    else audio.pause()
  }

  const selectMovement = (i: number) => {
    setStarted(true)
    loadMovement(i, 0, started ? playing : true)
  }

  const seekGlobal = (g: number) => {
    let i = 0
    while (i < manifest.movements.length - 1 && g >= starts[i + 1]) i++
    const local = Math.min(Math.max(g - starts[i], 0), durations[i] - 0.5)
    setStarted(true)
    if (i === mvt && audioRef.current?.src) {
      audioRef.current.currentTime = local
    } else {
      loadMovement(i, local, playing || !started)
    }
  }

  if (!notesByMvt) {
    return (
      <div className="app loading" style={{ ['--accent' as string]: accent }}>
        <div className="load-title">{manifest.title}</div>
        <div className="load-sub">gathering the notes…</div>
      </div>
    )
  }

  const m = manifest.movements[mvt]
  const spotlight = moment?.spotlight != null ? (instIndex[moment.spotlight] ?? -1) : userSpotlight
  const overline = [manifest.composer, manifest.subtitle, manifest.year]
    .filter(Boolean).join(' · ')

  return (
    <div className={'app' + (started ? ' started' : '')} style={{ ['--accent' as string]: accent }}>
      <header>
        <div className="title-block">
          <div className="overline">
            {onBack && <button className="back-btn" onClick={onBack} aria-label="All pieces">←</button>}
            {overline}
          </div>
          <h1>{manifest.title}</h1>
          {manifest.concept && <div className="byline">{manifest.concept}</div>}
        </div>
        {manifest.emblem && (
          <Emblem state={manifest.emblem.states[emblemState]} accent={accent} />
        )}
      </header>

      <main>
        {showScore && m.score ? (
          <ScoreView url={`${baseDir}${m.score}`} getTime={getLocalTime} />
        ) : (
          <PianoRoll
            notes={notesByMvt[mvt]}
            duration={m.duration}
            getTime={getLocalTime}
            playing={playing}
            started={started}
            spotlight={spotlight}
            colors={colors}
            accent={accent}
            pitchMin={pitchMin}
            pitchMax={pitchMax}
          />
        )}
        <div className="overlay-top">
          <span className="mvt-name">{m.num} · {m.title}</span>
          {m.key && <span className="mvt-key">{m.key}</span>}
          {m.score && (
            <button className="about-btn" onClick={() => setShowScore(s => !s)}>
              {showScore && m.score ? 'roll' : 'score'}
            </button>
          )}
          {(manifest.about?.length || manifest.credits?.length) && (
            <button className="about-btn" onClick={() => setShowAbout(true)}>about</button>
          )}
        </div>
        <div className="overlay-section" key={section}>{section}</div>
        {moment && <div className="overlay-moment" key={moment.text}>{moment.text}</div>}
        {!started && (
          <button className="hero-hint" onClick={togglePlay} aria-label="Play">
            <span className="hint-play">▶</span>
            <span className="hint-text">the whole movement, asleep — wake it</span>
          </button>
        )}
      </main>

      <Minimap
        notesByMvt={notesByMvt}
        durations={durations}
        numerals={manifest.movements.map(x => x.num)}
        colors={colors}
        accent={accent}
        pitchMin={pitchMin}
        pitchMax={pitchMax}
        getGlobalTime={getGlobalTime}
        onSeek={seekGlobal}
      />

      <div className="controls">
        <button className="play-btn" onClick={togglePlay} aria-label={playing ? 'Pause' : 'Play'}>
          {playing ? (
            <svg viewBox="0 0 24 24"><rect x="6" y="5" width="4" height="14" rx="1" /><rect x="14" y="5" width="4" height="14" rx="1" /></svg>
          ) : (
            <svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z" /></svg>
          )}
        </button>
        {manifest.movements.length > 1 && (
          <div className="pills">
            {manifest.movements.map((mm, i) => (
              <button
                key={mm.id}
                className={'pill' + (i === mvt ? ' active' : '')}
                onClick={() => selectMovement(i)}
                title={mm.title}
              >
                {mm.num}
              </button>
            ))}
          </div>
        )}
        <div className="time">{fmt(starts[mvt] + clock)} <span className="time-total">/ {fmt(total)}</span></div>
      </div>

      <div className="legend">
        {manifest.instruments.map((inst, i) => (
          <button
            key={inst.id}
            className={'chip' + (userSpotlight === i ? ' lit' : '') + (userSpotlight >= 0 && userSpotlight !== i ? ' dim' : '')}
            style={{ ['--c' as string]: colors[i] }}
            onClick={() => setUserSpotlight(userSpotlight === i ? -1 : i)}
          >
            <span className="dot" />{inst.name}
          </button>
        ))}
      </div>

      <footer>
        <span>{m.tempoLabel ?? ''}</span>
      </footer>

      {showAbout && (
        <div className="about-modal" onClick={() => setShowAbout(false)}>
          <div className="about-card" onClick={e => e.stopPropagation()}>
            <button className="about-close" onClick={() => setShowAbout(false)} aria-label="Close">×</button>
            <h2>{manifest.title}</h2>
            <div className="about-meta">{overline}</div>
            {(manifest.about ?? []).map((p, i) => <p key={i}>{p}</p>)}
            {manifest.movements.some(mm => mm.note) && (
              <ul className="about-movements">
                {manifest.movements.map(mm => (
                  <li key={mm.id}>
                    <strong>{mm.num} · {mm.title}</strong>
                    {mm.key ? ` (${mm.key})` : ''}{mm.note ? ` — ${mm.note}` : ''}
                  </li>
                ))}
              </ul>
            )}
            {(manifest.credits ?? []).length > 0 && (
              <div className="about-credits">
                {manifest.credits!.map((c, i) => (
                  <div key={i}><span>{c.label}</span>{c.value}</div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      <audio ref={audioRef} preload="auto" />
    </div>
  )
}
