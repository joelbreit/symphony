# Royal Street Rattler

A Dixieland jazz composition — 185 bars, ~3:45, 198 bpm. F major → D minor → B♭ major.

*New Orleans, 1924. A streetcar rattles down Royal Street, and the band on the corner
plays the rattle back at it until the whole block is strutting.*

## Listen

```sh
open output/royal_street_rattler.m4a        # rendered audio (MuseScore General soundfont)
open output/royal_street_rattler.mid        # the playable score (GM MIDI, 7 tracks)
```

## The band

Trumpet (lead) · Clarinet (obbligato) · Trombone (tailgate) · Tenor sax (guest soloist) ·
Sousaphone · Banjo · Drums (with streetcar cowbell)

## The shape

| Time | Section |
|---|---|
| 0:00 | Intro — streetcar bell, trumpet fanfare, unison break |
| 0:10 | **The Strut** (A strain ×2 — trumpet lead, then clarinet) |
| 0:48 | **Balcony Shadows** (D minor, trombone feature) |
| 1:08 | The Strut returns |
| 1:27 | Modulation — clarinet break into B♭ |
| 1:32 | **Out to the River** (trio theme) |
| 1:52 | Clarinet solo → 2:11 Tenor sax solo → 2:30 Trumpet solo (stop-time) |
| 2:50 | Drum break — the rattle as a drum solo |
| 2:55 | Shout chorus → 3:14 Out chorus (full boil, walking sousaphone) |
| 3:33 | Tag — three breaks (tbn/cl/tpt), final chord, sousaphone plop |

## Files

- [output/royal_street_rattler.mid](output/royal_street_rattler.mid) — the piece (GM MIDI)
- [output/royal_street_rattler.m4a](output/royal_street_rattler.m4a) — rendered audio
- [output/leadsheet.abc](output/leadsheet.abc) — lead sheet of the three strains (ABC notation)
- [output/pianoroll.png](output/pianoroll.png) — full-piece visualization
- [src/compose.py](src/compose.py) — the score generator: melodies/solos hand-composed
  note-by-note; banjo/sousaphone/drums/obbligato/tailgate realized by constrained
  generators; swing + humanization applied at render
- [docs/](docs/) — inspiration, theory notes, blueprint, self-assessment

## Rebuild from source

```sh
python3 -m venv .venv && .venv/bin/pip install midiutil mido matplotlib numpy
.venv/bin/python src/compose.py                                   # → output/*.mid
fluidsynth -ni -g 0.6 -F output/royal_street_rattler.wav -r 44100 \
    assets/MuseScore_General.sf3 output/royal_street_rattler.mid  # → audio
```

Composed by Claude (Fable 5), June 2026.
