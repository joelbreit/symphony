// note tuple: [startSec, durSec, midiPitch, instrumentIndex, velocity]
export type NoteTuple = [number, number, number, number, number]

export interface InstrumentInfo {
  id: string
  name: string
  family: 'strings' | 'winds' | 'brass' | 'color' | 'voices' | 'keys' | 'other'
}

export interface MovementInfo {
  id: string
  num: string
  title: string
  key?: string
  tempoLabel?: string
  duration: number
  noteCount?: number
  audio: string                       // path relative to the piece directory
  notes: string                       // path relative to the piece directory
  sections?: [number, string][]       // [seconds, label]
  note?: string                       // short program note for this movement
}

export interface EmblemNote {
  p: string                           // pitch name, e.g. "Eb5"
  accent?: boolean                    // draw in the accent color
}

export interface EmblemState {
  notes: EmblemNote[]
  mark?: string                       // small glyph after the last note, e.g. "?"
  label?: string
  trigger?: { movement: string; time: number }   // state becomes active from here on
}

export interface Moment {
  movement: string
  time: number
  text: string
  spotlight?: string                  // instrument id to spotlight while held
  hold?: number                       // seconds to keep on screen (default 8)
}

export interface PieceTheme {
  accent?: string                                  // hex; default gold
  instrumentColors?: Record<string, string>        // by instrument id; else family ramp
}

export interface PieceManifest {
  schema: 1
  id: string
  title: string
  subtitle?: string
  composer: string
  year?: number
  concept?: string                    // the one-line hook under the title
  about?: string[]                    // paragraphs for the About panel
  credits?: { label: string; value: string }[]
  theme?: PieceTheme
  instruments: InstrumentInfo[]
  movements: MovementInfo[]
  emblem?: { label?: string; states: EmblemState[] }
  moments?: Moment[]
}

export interface IndexEntry {
  id: string
  dir: string                         // e.g. "pieces/the-window"
  title: string
  subtitle?: string
  composer: string
  concept?: string
  accent?: string
  movements: number
  duration: number
}

export interface PiecesIndex {
  pieces: IndexEntry[]
}
