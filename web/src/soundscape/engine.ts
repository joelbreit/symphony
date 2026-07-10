// The soundscape engine: loops stems on their own cycles, drifts the mix.
//
// Plain TypeScript, zero React — this module is the deliberately small,
// swappable surface behind the flagged engine decision. Contract:
// AudioBuffers scheduled overlapping (iteration k+1 starts at k·loopSeconds
// while k's tail rings — the tail is the crossfade, see
// pieces-src/soundscapes/docs/02-loop-craft.md), a per-layer gain graph,
// and a seeded "conductor" that drifts gains, rests layers, and swaps
// variants so the weather never repeats.
//
// iOS discipline (same as Player.tsx): the context is created suspended and
// decode happens while suspended; start()/resume() must be called inside a
// user gesture's call stack.

import { LayerDef, LayerLevel, LayerPlayhead, SoundscapeManifest, VariantDef } from './types'

const LOOKAHEAD = 3          // seconds of scheduling horizon
const HIDDEN_LOOKAHEAD = 30  // horizon when the tab is hidden (timers throttle)
const TICK_MS = 500
const FADE_S = 6             // layer entrance/exit fade
const KEEP_AUDIBLE = 2       // conductor never drops below this many layers

// deterministic RNG so ?seed= reproduces a session exactly
function mulberry32(seed: number) {
  let a = seed >>> 0
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

// half-cosine curve for setValueCurveAtTime — equal-power-ish, click-free
function fadeCurve(from: number, to: number, n = 32): Float32Array {
  const c = new Float32Array(n)
  for (let i = 0; i < n; i++) {
    const f = (1 - Math.cos((i / (n - 1)) * Math.PI)) / 2
    c[i] = from + (to - from) * f
  }
  return c
}

interface LayerState {
  def: LayerDef
  buffers: AudioBuffer[]       // one per variant
  node: GainNode
  active: boolean
  targetGain: number           // current drift target (base `gain` at start)
  variant: number
  pendingVariant: number       // applied at the next scheduled loop boundary
  nextStart: number            // ctx time of the next iteration's downbeat
  lastToggle: number           // ctx time of the last rest/return
}

export interface SoundscapeEngine {
  load(onProgress?: (done: number, total: number) => void): Promise<void>
  start(): void                // call inside the user gesture
  pause(): void
  resume(): void               // call inside the user gesture
  playing(): boolean
  setVolume(v: number): void
  getLevels(): LayerLevel[]
  getPlayhead(): LayerPlayhead[]
  elapsed(): number
  dispose(): void
}

export function createEngine(
  manifest: SoundscapeManifest,
  baseDir: string,
  opts: { seed?: number; debug?: boolean } = {},
): SoundscapeEngine {
  const ctx = new AudioContext()
  if (ctx.state === 'running') void ctx.suspend()   // stay silent until start()
  const rng = mulberry32(opts.seed ?? (Date.now() & 0xfffff))
  const log = opts.debug
    ? (...a: unknown[]) => console.log('[scape]', ...a)
    : () => {}

  const master = new GainNode(ctx, { gain: 0.7 })
  master.connect(ctx.destination)

  const barSec = (60 / manifest.bpm) * 4
  const layers: LayerState[] = manifest.layers.map(def => ({
    def,
    buffers: [],
    node: new GainNode(ctx, { gain: 0 }),
    active: true,
    targetGain: def.gain,
    variant: 0,
    pendingVariant: 0,
    nextStart: 0,
    lastToggle: 0,
  }))
  layers.forEach(l => l.node.connect(master))

  let t0 = 0                   // ctx time of the session downbeat
  let started = false
  let schedTimer: ReturnType<typeof setInterval> | undefined
  let moveTimer: ReturnType<typeof setTimeout> | undefined
  let disposed = false

  async function load(onProgress?: (done: number, total: number) => void) {
    const jobs: { layer: LayerState; v: VariantDef; i: number }[] = []
    layers.forEach(layer => layer.def.variants.forEach((v, i) => jobs.push({ layer, v, i })))
    let done = 0
    await Promise.all(jobs.map(async ({ layer, v, i }) => {
      const res = await fetch(baseDir + v.file)
      if (!res.ok) throw new Error(`failed to load ${v.file}`)
      layer.buffers[i] = await ctx.decodeAudioData(await res.arrayBuffer())
      onProgress?.(++done, jobs.length)
    }))
  }

  function schedule(horizon: number) {
    const now = ctx.currentTime
    for (const l of layers) {
      if (!l.active || !l.buffers.length) continue
      while (l.nextStart < now + horizon) {
        if (l.pendingVariant !== l.variant) {
          l.variant = l.pendingVariant
          log(l.def.id, 'variant ->', l.variant, '@', l.nextStart.toFixed(2))
        }
        const v = l.def.variants[l.variant]
        const src = new AudioBufferSourceNode(ctx, { buffer: l.buffers[l.variant] })
        src.connect(l.node)
        src.start(l.nextStart, v.headOffset ?? 0)
        if (opts.debug && l.nextStart < now) log('MISSED DEADLINE', l.def.id)
        l.nextStart += v.loopSeconds
      }
    }
  }

  function fade(l: LayerState, to: number, dur = FADE_S) {
    const now = ctx.currentTime
    const from = l.node.gain.value
    l.node.gain.cancelScheduledValues(now)
    try {
      l.node.gain.setValueCurveAtTime(fadeCurve(from, to), now, dur)
    } catch {
      l.node.gain.setTargetAtTime(to, now, dur / 4)   // overlapping curve fallback
    }
  }

  // ---- the conductor ------------------------------------------------------
  function nextMove() {
    if (disposed) return
    moveTimer = setTimeout(() => { move(); nextMove() }, (20 + rng() * 25) * 1000)
  }

  function move() {
    if (ctx.state !== 'running') return               // paused: the weather waits
    const now = ctx.currentTime
    const roll = rng()
    if (roll < 0.45) {
      // gain drift within gainRange
      const cands = layers.filter(l => l.active && l.def.gainRange)
      if (!cands.length) return
      const l = cands[Math.floor(rng() * cands.length)]
      const [lo, hi] = l.def.gainRange!
      l.targetGain = lo + rng() * (hi - lo)
      fade(l, l.targetGain, 10 + rng() * 10)
      log('drift', l.def.id, '->', l.targetGain.toFixed(2))
    } else if (roll < 0.75) {
      // rest a layer, or bring one back
      const restable = layers.filter(l =>
        l.active && !l.def.always && now - l.lastToggle > (l.def.minOn ?? 30))
      const returnable = layers.filter(l =>
        !l.active && now - l.lastToggle > (l.def.minOff ?? 20))
      const audible = layers.filter(l => l.active).length
      const pool = audible > KEEP_AUDIBLE ? [...restable, ...returnable] : returnable
      if (!pool.length) return
      const l = pool[Math.floor(rng() * pool.length)]
      l.active = !l.active
      l.lastToggle = now
      if (l.active) {
        // re-enter on the shared bar grid so grid layers stay in step;
        // layers with quantizeBars (shared-form scenes) snap to the cycle
        const qSec = (l.def.quantizeBars ?? 1) * barSec
        l.nextStart = t0 + Math.ceil((now + FADE_S / 2 - t0) / qSec) * qSec
        fade(l, l.targetGain)
        schedule(LOOKAHEAD)
      } else {
        fade(l, 0)
        // sources already scheduled keep playing into the fade; that's fine
      }
      log(l.active ? 'enter' : 'rest', l.def.id)
    } else {
      // swap a variant at its next loop boundary
      const cands = layers.filter(l => l.active && l.def.variants.length > 1)
      if (!cands.length) return
      const l = cands[Math.floor(rng() * cands.length)]
      l.pendingVariant = (l.variant + 1) % l.def.variants.length
      log('swap queued', l.def.id, '->', l.pendingVariant)
    }
  }

  // ---- lifecycle ----------------------------------------------------------
  function onVisibility() {
    if (document.hidden && started && ctx.state === 'running') {
      schedule(HIDDEN_LOOKAHEAD)  // timers throttle in background tabs
    }
  }
  document.addEventListener('visibilitychange', onVisibility)

  return {
    load,
    start() {
      if (started) return
      started = true
      void ctx.resume()                                // inside the gesture
      t0 = ctx.currentTime + 0.15
      for (const l of layers) {
        l.nextStart = t0                               // only after all decodes
        l.lastToggle = t0
        fade(l, l.targetGain, 2)
      }
      schedule(LOOKAHEAD)
      schedTimer = setInterval(() => schedule(LOOKAHEAD), TICK_MS)
      nextMove()
    },
    pause() { void ctx.suspend() },                    // clock freezes; all
    resume() { void ctx.resume() },                    // schedules stay valid
    playing() { return started && ctx.state === 'running' },
    setVolume(v: number) {
      master.gain.setTargetAtTime(Math.max(0, Math.min(1, v)), ctx.currentTime, 0.05)
    },
    getLevels(): LayerLevel[] {
      return layers.map(l => ({
        id: l.def.id,
        name: l.def.name,
        active: l.active,
        gain: l.active ? l.targetGain : 0,
      }))
    },
    getPlayhead(): LayerPlayhead[] {
      // nextStart sits on the layer's loop grid, so phase falls out of it —
      // exact against the scheduler even when it has run several loops ahead
      const now = ctx.currentTime
      return layers.map(l => {
        const loop = l.def.variants[l.variant].loopSeconds
        return {
          id: l.def.id,
          active: l.active,
          gain: l.node.gain.value,
          variant: l.variant,
          pendingVariant: l.pendingVariant,
          phase: started ? (((now - l.nextStart) % loop) + loop) % loop : 0,
          loopSeconds: loop,
        }
      })
    },
    elapsed() { return started ? Math.max(0, ctx.currentTime - t0) : 0 },
    dispose() {
      disposed = true
      clearInterval(schedTimer)
      clearTimeout(moveTimer)
      document.removeEventListener('visibilitychange', onVisibility)
      void ctx.close()
    },
  }
}
