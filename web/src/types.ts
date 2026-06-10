// note tuple: [startSec, durSec, midiPitch, instrumentIndex, velocity]
export type NoteTuple = [number, number, number, number, number]

export interface InstrumentInfo {
  id: string
  name: string
  family: 'strings' | 'winds' | 'brass' | 'color'
}

export interface MovementMeta {
  id: string
  num: string
  title: string
  key: string
  tempoLabel: string
  duration: number
  noteCount: number
  audio: string
  data: string
  sections: [number, string][]
}

export interface SymphonyMeta {
  title: string
  composer: string
  year: number
  instruments: InstrumentInfo[]
  movements: MovementMeta[]
}
