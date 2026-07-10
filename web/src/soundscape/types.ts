// Soundscape packages live under public/soundscapes/<scene>/ — a separate
// world from piece packages (see PIECES.md for those). The manifest is the
// contract between the Python export (pieces-src/soundscapes/src/export_web.py)
// and the engine; keep it small — the engine is deliberately swappable.

// [startSec, durSec, midi pitch, velocity] — sorted by start; times relative
// to the loop downbeat (seam-crossing tails run past loopSeconds by design)
export type NoteEvt = [number, number, number, number]

export interface VariantDef {
  file: string                 // path relative to the scene directory
  loopSeconds: number          // loop body length, from the score
  tailSeconds?: number         // measured release/reverb tail past the body
  headOffset?: number          // escape hatch if a seam ever needs trimming
  notes?: NoteEvt[]            // score events, for the visualization only
}

export interface LayerDef {
  id: string
  name: string                 // legend chip label
  role?: string                // bed | pad | melody | texture
  always?: boolean             // never rested by the conductor
  gain: number                 // base level in the mix
  gainRange?: [number, number] // bounds for slow gain drift
  minOn?: number               // seconds before the conductor may rest it
  minOff?: number              // seconds before it may return
  quantizeBars?: number        // re-entry snaps to this many bars (default 1);
                               // scenes with a shared harmonic form set it to
                               // the form length so returns land on the cycle
  variants: VariantDef[]       // conductor swaps these at loop boundaries
}

export interface SoundscapeManifest {
  schema: 1
  id: string
  title: string
  composer: string
  concept?: string
  about?: string[]
  accent?: string
  key?: string
  bpm: number
  layers: LayerDef[]
}

export interface SceneIndexEntry {
  id: string
  dir: string                  // e.g. "soundscapes/focus"
  title: string
  concept?: string
  accent?: string
  layers: number
}

export interface SoundscapesIndex {
  schema: 1
  scenes: SceneIndexEntry[]
}

export interface LayerLevel {
  id: string
  name: string
  active: boolean
  gain: number                 // current target gain (0 when resting)
}

// per-frame geometry for the visualization (see engine.getPlayhead)
export interface LayerPlayhead {
  id: string
  active: boolean
  gain: number                 // live node gain — follows fades in real time
  variant: number
  pendingVariant: number       // takes over at the next loop boundary
  phase: number                // seconds into the current loop iteration
  loopSeconds: number
}
