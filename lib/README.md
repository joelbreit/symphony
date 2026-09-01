# lib — the shared composition toolkit

## Quickstart

```python
import sys, pathlib
# repo root: parents[2] from pieces-src/<slug>/*.py, parents[3] from pieces-src/<slug>/src/*.py
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

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
| `notation` | engraved score (MusicXML) from the pre-humanized layer: key-aware re-spelling, ornament/strum → notation rules, grand staff, key regions; `export()` writes it into a web piece package and verifies the sync, `check_sync()` is the gate on its own |
| `notation_m21` | the same job for the **frozen music21 pieces**, which have no symbolic layer: a recording `Orchestra` subclass, chord folding, staff frame, rest/voice/measure finishing, orchestral assembly, manifest patch. Only those three pieces need it — new pieces use `notation` |

## Scores come for free

A piece that declares its keys gets an engraved, audio-synced score in the
web player for one line of export code:

```python
p.key(0, 'a')                  # in compose(), alongside tempo/meter
p.key(S3, 'c')                 # modulations are just more declarations
...
notation.export(build(), 'perigee')     # in export_score.py
```

`export()` infers the staff order from the roster, the key signatures and
spelling from `piece.key()`, and the grand staves from instruments declared
`grand=True` in the ensemble; then it registers the score on the movement in
`piece.json` (which is what turns on the player's score toggle) and checks
the engraved rhythm back against the piece's own clock before it will call
it done. Pass `beat0`/`beat1` to engrave one movement of several, `min_nom`
to change the ornament threshold, `insts`/`keys`/`grand_staff` to override
any inference.

That last check is the point: a notation bug shows up as the score sliding
*seconds* out of step with the audio, not as anything that looks wrong on
the page. `tools/export_scores.py` re-runs every piece's export and reports
the worst drift for each.

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
