# lib — the shared composition toolkit

The best machinery from the first five compositions, extracted into one
package for every piece that comes after. The shipped pieces stay frozen on
their own code (their builds are deterministic, published artifacts); new
pieces start here and may extend this.

Provenance: the note DSL, dynamics, and roster guards come from The Window /
The Box Is Full; chord charts, `fit()` voice leading, swing, and pitch-bend
scoops from Royal Street Rattler; per-instrument humanize classes, jazz
articulations, and the measured-RMS feedback loop from High Street Riot;
fail-fast range asserts and the figure library from The Unfinished Spire.
The MIDI is written directly with mido — no music21 score container, so no
channel-remap post-hacks, and CC curves / pitch bends are first-class.

## Quickstart

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root

from lib import Piece, orchestra, B, R
from lib import figures, assess

p = Piece(orchestra(), seed=21, title='My Piece')
p.tempo(0, 96, 'con moto')
p.meter(0, 4, 4)

p.mark('first idea', 0)
theme = B('C5:e D5:e Eb5:e F5:e G5:q Eb5:q F5:e G5:e Ab5:e F5:e G5:h', 2)
p.add('vln1', p.bar(1), R(theme, 2), vel='mf', vel_end='f')
p.hairpin('vc', p.bar(1), p.bar(3), 60, 110)      # CC11 swell on held notes
figures.roll(p, 'timp', 'C3', p.bar(4), 4.0, 30, 96)

assess.report(p)                                   # ranges, sections, duration
assess.pianoroll(p, 'output/roll.png')             # + wav= for measured RMS
p.write('output/my_piece.mid')                     # swing=0.62 for jazz feels
p.write_marks('output/marks.json')                 # sections/cues for the web manifest
```

Run `python -m lib.demo` for two complete worked examples (an orchestral
miniature and a swung 12-bar blues), and `python -m lib.tests` after
changing anything in here.

## Module map

| Module | What it holds |
|---|---|
| `pitch` | note names ↔ MIDI (`C4` = 60) |
| `dsl` | the note DSL (`'G4:q (C3 G3):h r:e'`), `R()` repeat, `B()` bar guard, `transpose` |
| `chords` | chord symbols (`'F/C'`, `'Bdim7'`, `'G7#9'`), charts, `fit()` voice-leading, `voicing()` |
| `timeline` | tempo map + meter map: beats ↔ seconds ↔ bars (meter changes work) |
| `ensemble` | `Instrument` specs, channel assignment, `DRUMS` map; presets: `orchestra()`, `dixieland()`, `rhythm_section()`, `solo_piano()` |
| `piece` | the `Piece`: `add`/`perc`/`note`, named dynamics with ramps, fail-fast range guards, `mark`/`cue` → marks.json, `hairpin` (CC11), `pedal` (CC64), `bend`, `program` |
| `groove` | `swing_warp` time-warp, `Humanize` profiles (tight rhythm section, loose horns), overlap trimming |
| `figures` | textures (`trem`, `arp`, `ost`, rolls, swells, `harp_arp`, `strum`) and idioms (`smear_into`, `falloff`, `curl`, `trill`, `scoop`, `press_roll`) |
| `midiwrite` | direct mido writer (format 1, conductor track, one named track per instrument), `midi_report` |
| `assess` | text report + pianoroll/dynamic-arc plots, optional measured-RMS overlay from a rendered WAV |

## Conventions

- All offsets and durations are **beats = quarter notes**, absolute from 0.
  Bars are 1-indexed via `piece.bar(n)` and honor the meter map.
- Everything is deterministic from the `Piece(seed=…)`; never remove seeds.
- Range violations **raise at note entry**. If a player earns an exception
  (the sousa wail), pass `check_range=False` for that one call.
- `hairpin()` values persist: after a decrescendo, reset CC11 before the
  next passage or later notes stay quiet.
- Track names in the MIDI are the instruments' display names — that is what
  `tools/midi_to_piece.py` keys web packages on. Titles and mark labels are
  sanitized to latin-1 (MIDI meta limitation): em-dashes become hyphens.
- New ensembles are data, not code: build an `Ensemble([Instrument(...)])`
  with real sounding ranges, stage pans, and families, or start from a
  preset.

## Deliberately not here (yet)

- **Rhythm-section generators** (rattler's chart-driven banjo/tuba/drums,
  `obbligato`, `tailgate`): opinionated style code — port them when a piece
  needs them, generalizing from the original in that piece's own src first
  if the fit is unclear.
- **Scale/mode utilities** (diatonic transposition, chord-scale mapping) and
  a **groove pattern library** — add when a piece calls for them.
- **Audio render automation** (fluidsynth + afconvert) — still per
  `web/README.md`.
