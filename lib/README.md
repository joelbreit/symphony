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
| `keyboard` | playability audit for keyboard pieces: onsets split into two hands, then checked for span, finger count and reach at the seconds the tempo actually allows. `keyboard.report(piece)` prints and returns True if clean |
| `notation` | engraved score (MusicXML) from the pre-humanized layer: key-aware re-spelling, ornament/strum → notation rules, grand staff, key regions, **dynamics and hairpins read back out of the velocities**; `export()` writes it into a web piece package and verifies the sync, `check_sync()` is the gate on its own |
| `notation_m21` | the same job for the **frozen music21 pieces**, which have no symbolic layer: a recording `Orchestra` subclass (rhythm *and* platonic velocity), chord folding, staff frame, rest/voice/measure finishing, orchestral assembly, manifest patch. Only those three pieces need it — new pieces use `notation` |

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

### Dynamics come with them

Velocity is the dynamic in this system, so the page reads it back: the per-bar
median velocity is banded (the midpoints of `piece.DYN`), smoothed over three
bars, printed as a mark wherever a band change holds, and drawn as a hairpin
wherever the median ramped monotonically far enough to be a ramp instead of a
step. Pass `dyn=False` to `to_score` for a bare score.

Two things it knows that are worth knowing yourself. **Use the median, not the
mean** — forty quiet accompaniment sixteenths under four loud melody notes is
a quiet bar, and the mean disagrees. And **velocity is a keystroke while a
dynamic is a loudness**: the same force at the top of a keyboard makes far
less sound, so a composer pushing a thin top octave to make it speak is not
writing `mf`. `_effective_vel` takes one band off above C6 and leaves
everything else alone.

Beaming is corrected on the way out, too: music21 breaks the secondary beams
of a beat group at the eighth, so four sixteenths engrave as two pairs of two.
`_join_secondary_beams` joins every deeper beam inside a primary group where
both neighbours carry it, and leaves the break where it is real (an eighth in
the middle of sixteenths) or correct (a group longer than one beat).

### One trap, because it is invisible

music21 writes `<per-minute>` and `<sound tempo>` as **whole** BPM. A piece at
♩=120 never notices; a piece whose tempo comes from something in the world
(♩=134.5996, one 3/4 bar per rotation of a pulsar) loses about a second over
five minutes, and a second is the score highlighting the wrong bar.
`to_musicxml` restores the exact tempi from the piece's own timeline after
music21 has written the file.

## Conventions

- All offsets and durations are **beats = quarter notes**, absolute from 0.
  Bars are 1-indexed via `piece.bar(n)` and honor the meter map.
- Everything is deterministic from the `Piece(seed=…)`; never remove seeds.
  After changing anything here, run `tools/check_all.py`: it rebuilds every
  lib-built piece and fails if one byte of anybody's finished MIDI moved.
- `piece.add(..., rigid=True)` exempts material from swing, lean and timing
  jitter while keeping velocity jitter — a machine inside a human
  performance (a click, a sequencer line, a pulse the piece is about). It
  still draws from the RNG, so marking something rigid does not reshuffle
  the humanization of anything else.
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

- **Dynamics and articulations on the engraved page** — see
  `docs/score-backlog.md` items 2 and 9. Velocity is the dynamic in this
  system, so the information exists; the score just doesn't print it.
- **Rhythm-section generators** (rattler's chart-driven banjo/tuba/drums,
  `obbligato`, `tailgate`): opinionated style code — port them when a piece
  needs them, generalizing from the original in that piece's own src first
  if the fit is unclear.
- **Scale/mode utilities** (diatonic transposition, chord-scale mapping) and
  a **groove pattern library** — add when a piece calls for them.
- **Audio render automation** (fluidsynth + afconvert) — still per
  `web/README.md`.
