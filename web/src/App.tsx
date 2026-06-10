import { useCallback, useEffect, useRef, useState } from 'react'
import { NoteTuple, SymphonyMeta } from './types'
import { INSTRUMENT_COLORS } from './theme'
import PianoRoll from './PianoRoll'
import Minimap from './Minimap'
import MottoStaff from './MottoStaff'

const BASE = import.meta.env.BASE_URL

function fmt(sec: number) {
  if (!isFinite(sec) || sec < 0) sec = 0
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export default function App() {
  const [meta, setMeta] = useState<SymphonyMeta | null>(null)
  const [notesByMvt, setNotesByMvt] = useState<NoteTuple[][] | null>(null)
  const [mvt, setMvt] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [started, setStarted] = useState(false)
  const [spotlight, setSpotlight] = useState(-1)
  const [section, setSection] = useState('')
  const [clock, setClock] = useState(0)
  const audioRef = useRef<HTMLAudioElement>(null)
  const pendingSeek = useRef<number | null>(null)
  const mvtRef = useRef(0)
  mvtRef.current = mvt

  useEffect(() => {
    fetch(`${BASE}data/meta.json`)
      .then(r => r.json())
      .then((m: SymphonyMeta) => {
        setMeta(m)
        return Promise.all(m.movements.map(mv => fetch(`${BASE}${mv.data}`).then(r => r.json())))
      })
      .then(all => setNotesByMvt(all as NoteTuple[][]))
      .catch(err => console.error('failed to load symphony data', err))
  }, [])

  const durations = meta ? meta.movements.map(m => m.duration) : []
  const starts = durations.reduce<number[]>((acc, d, i) => {
    acc.push(i === 0 ? 0 : acc[i - 1] + durations[i - 1])
    return acc
  }, [])
  const total = durations.reduce((a, b) => a + b, 0)

  const getLocalTime = useCallback(() => audioRef.current?.currentTime ?? 0, [])
  const getGlobalTime = useCallback(
    () => (starts[mvtRef.current] ?? 0) + (audioRef.current?.currentTime ?? 0),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [meta],
  )

  // clock + section label polling
  useEffect(() => {
    if (!meta) return
    const id = setInterval(() => {
      const t = audioRef.current?.currentTime ?? 0
      setClock(t)
      const secs = meta.movements[mvtRef.current].sections
      let label = secs[0]?.[1] ?? ''
      for (const [st, name] of secs) {
        if (t >= st - 0.25) label = name
        else break
      }
      setSection(label)
    }, 250)
    return () => clearInterval(id)
  }, [meta])

  const loadMovement = useCallback((i: number, seekTo: number | null, andPlay: boolean) => {
    const audio = audioRef.current!
    setMvt(i)
    pendingSeek.current = seekTo
    audio.src = `${BASE}${meta!.movements[i].audio}`
    audio.load()
    // play() must be called inside the user gesture's call stack (iOS Safari)
    if (andPlay) audio.play().catch(() => setPlaying(false))
  }, [meta])

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
      if (mvtRef.current < 3) {
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
  }, [loadMovement, notesByMvt])

  const togglePlay = () => {
    const audio = audioRef.current!
    if (!started) {
      setStarted(true)
      loadMovement(mvt, null, true)
      return
    }
    if (audio.paused) audio.play().catch(() => {})
    else audio.pause()
  }

  const selectMovement = (i: number) => {
    if (!meta) return
    setStarted(true)
    loadMovement(i, 0, started ? playing : true)
  }

  const seekGlobal = (g: number) => {
    if (!meta) return
    let i = 0
    while (i < 3 && g >= starts[i + 1]) i++
    const local = Math.min(Math.max(g - starts[i], 0), durations[i] - 0.5)
    setStarted(true)
    if (i === mvt && audioRef.current?.src) {
      audioRef.current.currentTime = local
      if (!playing) { /* stay paused; roll updates via getTime */ }
    } else {
      loadMovement(i, local, playing || !started)
    }
  }

  if (!meta || !notesByMvt) {
    return (
      <div className="app loading">
        <div className="load-title">The Window</div>
        <div className="load-sub">gathering 13,000 notes…</div>
      </div>
    )
  }

  const m = meta.movements[mvt]

  return (
    <div className={'app' + (started ? ' started' : '')}>
      <header>
        <div className="title-block">
          <div className="overline">{meta.composer} · Symphony No. 1 in C minor · 2026</div>
          <h1>The Window</h1>
          <div className="byline">
            four movements · 18 minutes · 13,000 notes — an AI's symphony about its own
            condition: a window of attention that opens, blazes, and closes.
          </div>
        </div>
        <MottoStaff answered={mvt === 3 && clock >= (m.sections.find(s => s[1] === 'THE ANSWER')?.[0] ?? 1e9)} />
      </header>

      <main>
        <PianoRoll
          notes={notesByMvt[mvt]}
          duration={m.duration}
          getTime={getLocalTime}
          playing={playing}
          started={started}
          spotlight={spotlight}
        />
        <div className="overlay-top">
          <span className="mvt-name">{m.num} · {m.title}</span>
          <span className="mvt-key">{m.key}</span>
        </div>
        <div className="overlay-section" key={section}>{section}</div>
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
        numerals={meta.movements.map(x => x.num)}
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
        <div className="pills">
          {meta.movements.map((mm, i) => (
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
        <div className="time">{fmt(starts[mvt] + clock)} <span className="time-total">/ {fmt(total)}</span></div>
      </div>

      <div className="legend">
        {meta.instruments.map((inst, i) => (
          <button
            key={inst.id}
            className={'chip' + (spotlight === i ? ' lit' : '') + (spotlight >= 0 && spotlight !== i ? ' dim' : '')}
            style={{ ['--c' as string]: INSTRUMENT_COLORS[i] }}
            onClick={() => setSpotlight(spotlight === i ? -1 : i)}
          >
            <span className="dot" />{inst.name}
          </button>
        ))}
      </div>

      <footer>
        <span>{m.tempoLabel}</span>
        <a href="https://github.com" onClick={e => e.preventDefault()} tabIndex={-1} aria-hidden="true" style={{ display: 'none' }} />
      </footer>

      <audio ref={audioRef} preload="auto" />
    </div>
  )
}
