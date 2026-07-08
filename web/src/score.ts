// Sheet-music data model: turns the quantized score JSON emitted by
// tools/midi_to_score.py into drawable measures (voices, chords, rests,
// ties, accidentals) plus the units<->seconds tempo map that drives the
// live cursor. Pure logic — all VexFlow calls live in SheetMusic.tsx.

export type ScoreNote = [number, number, number, number] // startU, durU, midi, vel

export interface ScorePartData {
  i: number                              // instrument index into the manifest
  clef: 'treble' | 'bass' | 'alto' | 'tenor' | 'grand' | 'perc'
  notes: ScoreNote[]
}

export interface ScoreData {
  v: 1
  upq: number                            // units per quarter (24)
  num: number
  den: number
  fifths: number
  mode: 'major' | 'minor'
  tonic: number
  bars: number
  tempos: [number, number][]             // [units, seconds] anchors
  parts: ScorePartData[]
}

// ---------------------------------------------------------------- tempo map

export class TempoMap {
  private a: [number, number][]
  constructor(anchors: [number, number][]) {
    this.a = anchors.length >= 2 ? anchors : [[0, 0], [48, 1]] // fallback 120bpm
  }
  private slope(i: number) {
    const [u1, s1] = this.a[i], [u2, s2] = this.a[i + 1]
    return s2 > s1 ? (u2 - u1) / (s2 - s1) : 48
  }
  unitsAt(sec: number): number {
    const a = this.a
    let i = 0
    while (i < a.length - 2 && sec >= a[i + 1][1]) i++
    return a[i][0] + (sec - a[i][1]) * this.slope(i)
  }
  secAt(units: number): number {
    const a = this.a
    let i = 0
    while (i < a.length - 2 && units >= a[i + 1][0]) i++
    return a[i][1] + (units - a[i][0]) / this.slope(i)
  }
}

// ------------------------------------------------------------ pitch spelling

const LETTER_PC: Record<string, number> = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 }
const SHARP_ORDER = ['F', 'C', 'G', 'D', 'A', 'E', 'B']
const SHARPS: [string, number][] = [
  ['C', 0], ['C', 1], ['D', 0], ['D', 1], ['E', 0], ['F', 0],
  ['F', 1], ['G', 0], ['G', 1], ['A', 0], ['A', 1], ['B', 0],
]
const FLATS: [string, number][] = [
  ['C', 0], ['D', -1], ['D', 0], ['E', -1], ['E', 0], ['F', 0],
  ['G', -1], ['G', 0], ['A', -1], ['A', 0], ['B', -1], ['B', 0],
]
const MINOR_TONIC_LETTERS = ['A', 'E', 'B', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F', 'C', 'G', 'D', 'A'] // fifths -7..7
const MAJOR_KEYS = ['Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#']
const MINOR_KEYS = ['Abm', 'Ebm', 'Bbm', 'Fm', 'Cm', 'Gm', 'Dm', 'Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'A#m']

export function keySpec(fifths: number, mode: string): string {
  const i = Math.max(0, Math.min(14, fifths + 7))
  return mode === 'minor' ? MINOR_KEYS[i] : MAJOR_KEYS[i]
}

/** per-letter alteration implied by the key signature */
export function keySigAlters(fifths: number): Record<string, number> {
  const out: Record<string, number> = {}
  if (fifths > 0) for (let i = 0; i < fifths; i++) out[SHARP_ORDER[i]] = 1
  if (fifths < 0) for (let i = 0; i < -fifths; i++) out[SHARP_ORDER[6 - i]] = -1
  return out
}

/** spelling table: pitch class -> [letter, alter] for this key */
function spellTable(fifths: number, mode: string): [string, number][] {
  const table = (fifths >= 1 ? SHARPS : FLATS).map(x => [...x] as [string, number])
  for (const [letter, alter] of Object.entries(keySigAlters(fifths))) {
    table[((LETTER_PC[letter] + alter) % 12 + 12) % 12] = [letter, alter]
  }
  if (mode === 'minor') {
    // raised leading tone (e.g. F# in G minor), the one chromatic note flat
    // spelling reliably gets wrong
    const tonicLetter = MINOR_TONIC_LETTERS[Math.max(0, Math.min(14, fifths + 7))]
    const seventhLetter = 'ABCDEFG'[('ABCDEFG'.indexOf(tonicLetter) + 6) % 7]
    const tonicPc = ((LETTER_PC[tonicLetter] + (keySigAlters(fifths)[tonicLetter] ?? 0)) % 12 + 12) % 12
    const leadPc = (tonicPc + 11) % 12
    let alter = leadPc - LETTER_PC[seventhLetter]
    if (alter > 6) alter -= 12
    if (alter < -6) alter += 12
    if (Math.abs(alter) <= 1) table[leadPc] = [seventhLetter, alter]
  }
  return table
}

const ACC_GLYPH: Record<number, string> = { [-2]: 'bb', [-1]: 'b', 0: 'n', 1: '#', 2: '##' }

// ------------------------------------------------- percussion note placement

const PERC_MAP: [number[], string][] = [
  [[35, 36], 'f/4'],
  [[41, 43, 45], 'a/4'],
  [[38, 40], 'c/5'],
  [[37, 39], 'c/5/x2'],
  [[47, 48, 50], 'e/5'],
  [[42, 44, 46, 70, 82], 'g/5/x2'],
  [[51, 53, 59], 'f/5/x2'],
  [[49, 52, 55, 57], 'a/5/x2'],
  [[54, 56, 75, 76, 77], 'e/5/x2'],
]

function percKey(midi: number): string {
  for (const [pitches, key] of PERC_MAP) if (pitches.includes(midi)) return key
  return midi < 45 ? 'f/4' : 'c/5'
}

// -------------------------------------------------------- duration handling

// [units, vexflow duration, dots] — notes may use dotted values
const NOTE_VALUES: [number, string, number][] = [
  [96, 'w', 0], [72, 'h', 1], [48, 'h', 0], [36, 'q', 1],
  [24, 'q', 0], [18, '8', 1], [12, '8', 0], [9, '16', 1], [6, '16', 0], [3, '32', 0],
]
// rests and spacers stay un-dotted (reads more conventionally)
const REST_VALUES: [number, string, number][] = [
  [96, 'w', 0], [48, 'h', 0], [24, 'q', 0], [12, '8', 0], [6, '16', 0], [3, '32', 0],
]

const BAR_U = 96                          // 4/4 at 24 units per quarter
const BEAT_U = 24

function pickValue(relS: number, rem: number, rest: boolean): [number, string, number] {
  const values = rest ? REST_VALUES : NOTE_VALUES
  const toBeat = BEAT_U - (relS % BEAT_U)
  let cap = rem
  if (relS % BEAT_U !== 0) cap = Math.min(cap, toBeat)               // fill to the next beat first
  else if (rest) cap = Math.min(cap, relS < 48 ? 48 - relS : 96 - relS) // rests don't cross mid-bar
  for (const v of values) {
    if (v[0] > cap) continue
    if (v[0] === 96 && relS !== 0) continue
    return v
  }
  return values[values.length - 1]
}

// ------------------------------------------------------------ prepared model

export interface Ev {
  startU: number
  units: number
  bar: number
  dur: string
  dots: number
  kind: 'note' | 'rest' | 'ghost'
  keys: string[]
  accs: (string | null)[]
  tieToNext: boolean
  tiedFromPrev: boolean
  vel: number
}

export interface PreparedStaff {
  clef: 'treble' | 'bass' | 'alto' | 'tenor' | 'percussion'
  voices: Ev[][][]                        // [voice][bar] -> events
}

export interface PreparedPart {
  i: number                               // instrument index
  grand: boolean
  staves: PreparedStaff[]
}

export interface PreparedScore {
  parts: PreparedPart[]
  bars: number
  cols: number[]                          // distinct onset count per bar (for widths)
  keySpec: string
  fifths: number
  tempo: TempoMap
  endU: number
}

interface Chord { startU: number; durU: number; pitches: number[]; vel: number }

const restKeyFor = (clef: string, whole: boolean) =>
  clef === 'bass' ? (whole ? 'f/3' : 'd/3')
    : clef === 'alto' ? (whole ? 'e/4' : 'c/4')
      : clef === 'tenor' ? (whole ? 'c/4' : 'a/3')
        : whole ? 'd/5' : 'b/4'

/** greedy two-voice packing; overlaps clip the earlier chord */
function packVoices(chords: Chord[]): Chord[][] {
  const voices: Chord[][] = [[], []]
  const ends = [0, 0]
  for (const c of chords) {
    let placed = false
    for (let v = 0; v < 2; v++) {
      if (ends[v] <= c.startU) {
        voices[v].push(c)
        ends[v] = c.startU + c.durU
        placed = true
        break
      }
    }
    if (!placed) {
      // both voices busy: clip whichever last chord started earlier, or merge
      const v = voices[0].length && voices[0][voices[0].length - 1].startU < c.startU ? 0
        : voices[1].length && voices[1][voices[1].length - 1].startU < c.startU ? 1 : -1
      if (v >= 0) {
        const last = voices[v][voices[v].length - 1]
        last.durU = Math.max(6, c.startU - last.startU)
        voices[v].push(c)
        ends[v] = c.startU + c.durU
      } else {
        const last = voices[0][voices[0].length - 1]
        for (const p of c.pitches) if (!last.pitches.includes(p)) last.pitches.push(p)
      }
    }
  }
  return voices[1].length ? voices : [voices[0]]
}

/** split a chord at barlines, then into notatable tied chunks */
function emit(c: Chord, keys: string[], perc: boolean, out: Ev[]) {
  let s = c.startU
  let remTotal = c.durU
  let first = true
  while (remTotal > 0) {
    const bar = Math.floor(s / BAR_U)
    const inBar = Math.min(remTotal, (bar + 1) * BAR_U - s)
    let rel = s - bar * BAR_U
    let rem = inBar
    while (rem > 0) {
      const [units, dur, dots] = pickValue(rel, rem, false)
      out.push({
        startU: bar * BAR_U + rel, units, bar, dur, dots,
        kind: 'note', keys, accs: keys.map(() => null),
        tieToNext: rem - units > 0 || remTotal - inBar > 0,
        tiedFromPrev: !first,
        vel: c.vel,
      })
      first = false
      rel += units
      rem -= units
      if (perc) { // percussion hits don't tie — the tail becomes space
        out[out.length - 1].tieToNext = false
        remTotal = inBar
        rem = 0
        break
      }
    }
    s = (bar + 1) * BAR_U
    remTotal -= inBar
  }
}

function fillGaps(events: Ev[], bars: number, kind: 'rest' | 'ghost', clef: string): Ev[][] {
  // events assumed sorted, non-overlapping; returns per-bar lists incl. fills
  const byBar: Ev[][] = Array.from({ length: bars }, () => [])
  for (const e of events) byBar[e.bar]?.push(e)
  for (let bar = 0; bar < bars; bar++) {
    const list = byBar[bar]
    if (!list.length) {
      if (kind === 'rest') byBar[bar] = [{
        startU: bar * BAR_U, units: BAR_U, bar, dur: 'w', dots: 0, kind: 'rest',
        keys: [restKeyFor(clef, true)], accs: [null], tieToNext: false, tiedFromPrev: false, vel: 0,
      }]
      continue
    }
    const filled: Ev[] = []
    let cur = bar * BAR_U
    const pushFill = (from: number, to: number) => {
      let rel = from - bar * BAR_U
      let rem = to - from
      while (rem > 0) {
        const [units, dur] = pickValue(rel, rem, true)
        filled.push({
          startU: bar * BAR_U + rel, units, bar, dur, dots: 0, kind,
          keys: [restKeyFor(clef, false)], accs: [null], tieToNext: false, tiedFromPrev: false, vel: 0,
        })
        rel += units
        rem -= units
      }
    }
    for (const e of list) {
      if (e.startU > cur) pushFill(cur, e.startU)
      filled.push(e)
      cur = Math.max(cur, e.startU + e.units)
    }
    if (cur < (bar + 1) * BAR_U && kind === 'rest') pushFill(cur, (bar + 1) * BAR_U)
    byBar[bar] = filled
  }
  return byBar
}

export function prepareScore(score: ScoreData): PreparedScore {
  const table = spellTable(score.fifths, score.mode)
  const sigAlters = keySigAlters(score.fifths)
  const onsets: Set<number>[] = Array.from({ length: score.bars }, () => new Set())
  let endU = 0

  const spellKey = (midi: number): string => {
    const [letter, alter] = table[((midi % 12) + 12) % 12]
    const octave = (midi - alter - LETTER_PC[letter]) / 12 - 1
    return `${letter.toLowerCase()}${alter === 1 ? '#' : alter === -1 ? 'b' : alter === 2 ? '##' : alter === -2 ? 'bb' : ''}/${octave}`
  }

  const parts: PreparedPart[] = score.parts.map(part => {
    const perc = part.clef === 'perc'
    const staffDefs: { clef: PreparedStaff['clef']; notes: ScoreNote[] }[] =
      part.clef === 'grand'
        ? [{ clef: 'treble', notes: part.notes.filter(n => n[2] >= 60) },
           { clef: 'bass', notes: part.notes.filter(n => n[2] < 60) }]
        : [{ clef: perc ? 'percussion' : part.clef as PreparedStaff['clef'], notes: part.notes }]

    const staves: PreparedStaff[] = staffDefs.map(sd => {
      // chord grouping: same start (+ same duration, except percussion) merge
      const groups = new Map<string, Chord>()
      for (const [startU, durU, midi, vel] of sd.notes) {
        endU = Math.max(endU, startU + durU)
        onsets[Math.min(score.bars - 1, Math.floor(startU / BAR_U))].add(startU)
        const gk = perc ? `${startU}` : `${startU}/${durU}`
        const g = groups.get(gk)
        if (g) {
          if (!g.pitches.includes(midi)) g.pitches.push(midi)
          g.vel = Math.max(g.vel, vel)
        } else {
          groups.set(gk, { startU, durU: perc ? Math.min(durU, BEAT_U) : durU, pitches: [midi], vel })
        }
      }
      const chords = [...groups.values()].sort((a, b) => a.startU - b.startU || b.durU - a.durU)
      // percussion: a hit lasts until the next hit (up to a beat)
      if (perc) {
        for (let i = 0; i < chords.length; i++) {
          const next = i + 1 < chords.length ? chords[i + 1].startU - chords[i].startU : BEAT_U
          chords[i].durU = Math.max(6, Math.min(BEAT_U, next))
        }
      }
      const voices = packVoices(chords)
      const streams = voices.map((vc, vi) => {
        const evs: Ev[] = []
        for (const c of vc) {
          const keys = c.pitches
            .sort((a, b) => a - b)
            .map(p => (perc ? percKey(p) : spellKey(p)))
            .filter((k, i, arr) => arr.indexOf(k) === i)
          emit(c, keys, perc, evs)
        }
        return fillGaps(evs, score.bars, vi === 0 ? 'rest' : 'ghost', sd.clef)
      })
      // accidentals: measure-scoped, across both voices in start order
      if (!perc) {
        for (let bar = 0; bar < score.bars; bar++) {
          const state: Record<string, number> = {}
          const all = streams.flatMap(v => v[bar]).filter(e => e.kind === 'note')
            .sort((a, b) => a.startU - b.startU)
          for (const e of all) {
            e.keys.forEach((k, ki) => {
              const m = k.match(/^([a-g])(#{1,2}|b{1,2})?\/(-?\d+)$/)
              if (!m) return
              const letter = m[1].toUpperCase()
              const alter = m[2] === '#' ? 1 : m[2] === '##' ? 2 : m[2] === 'b' ? -1 : m[2] === 'bb' ? -2 : 0
              const slot = `${letter}/${m[3]}`
              const current = state[slot] ?? sigAlters[letter] ?? 0
              if (current !== alter && !e.tiedFromPrev) e.accs[ki] = ACC_GLYPH[alter]
              state[slot] = alter
            })
          }
        }
      }
      return { clef: sd.clef, voices: streams }
    })
    return { i: part.i, grand: part.clef === 'grand', staves }
  })

  return {
    parts,
    bars: score.bars,
    cols: onsets.map(s => Math.max(1, s.size)),
    keySpec: keySpec(score.fifths, score.mode),
    fifths: score.fifths,
    tempo: new TempoMap(score.tempos),
    endU,
  }
}
