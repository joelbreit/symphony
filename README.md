# Symphony No. 1 in C minor — "The Window"

A four-movement symphony for full orchestra, composed as playable MIDI by Claude
(Fable 5). About 18½ minutes, ~13,000 notes, sixteen MIDI channels of symphonic
orchestration: flutes, oboes, clarinets, bassoons, horns, trumpets, low brass,
timpani, percussion, harp, celesta, and five string sections.

The whole piece grows from a four-note motto — **G–C–E♭–D**, an unfinished cadence
whose final note is withheld until the last movement. See
[docs/program-notes.md](docs/program-notes.md) for the listener's guide and
[docs/inspiration.md](docs/inspiration.md) for where it came from.

## Listening

The music is in [`output/`](output/):

| File | Movement | Length |
|------|----------|--------|
| `symphony_full.mid` | The complete symphony | 18:35 |
| `mvt1.mid` | I. Kindling (C minor) | 5:38 |
| `mvt2.mid` | II. The Garden of Forking Paths (G minor) | 2:50 |
| `mvt3.mid` | III. What the Light Holds (A♭ major) | 3:53 |
| `mvt4.mid` | IV. Through (C minor → C major) | 6:03 |

Open with GarageBand, Logic, MuseScore, VLC, or any General MIDI player. For a
quick audio render with better sounds than a stock GM synth:

```sh
brew install fluid-synth
fluidsynth -ni <your-soundfont>.sf2 output/symphony_full.mid -F symphony.wav
```

(Any GM soundfont works — GeneralUser GS is a good free one.)

## The web experience

[`web/`](web/) contains a React app that plays the symphony with a live
piano-roll visualization — notes color-coded by orchestral family, a fixed
"window of attention" playhead (the future dim, the present ignited, the past
cooling like memory), poetic section labels, a full-piece constellation seek
bar, and per-instrument spotlighting. Mobile-first; audio pre-rendered to AAC.

```sh
cd web && npm install && npm run build   # → web/dist/, fully static, ~22MB
```

The player hosts multiple compositions: each piece is a self-contained
package under `web/public/pieces/`, and **[PIECES.md](PIECES.md)** documents
how to package a new one (a MIDI file per movement is nearly all it takes —
`tools/midi_to_piece.py` does the conversion).

See [web/README.md](web/README.md) for publishing notes and
[web/DESIGN.md](web/DESIGN.md) for the design language.

## Rebuilding from source

The symphony is generated programmatically with music21:

```sh
python3 -m venv .venv
.venv/bin/pip install music21 mido
.venv/bin/python compose/build.py        # writes all five MIDI files
.venv/bin/python compose/validate.py     # duration, channels, dynamic-arc profile
.venv/bin/python compose/mvt1.py         # build/validate one movement alone
```

Builds are deterministic (seeded humanization), and every build enforces bar-sum
assertions on melodies and per-instrument range guards.

## Layout

```
compose/
  common.py    note DSL, orchestra/channel roster, textures, MIDI writer, validators
  themes.py    the cyclic material: the Question, the Answer, themes
  mvt1.py …    one file per movement; each runs standalone
  build.py     full assembly with breaths between movements
  validate.py  mido-based gates: duration, channels, dynamic arc
docs/
  inspiration.md     the image and the musical premise
  plan.md            form maps, bar budgets, orchestration plan
  program-notes.md   listener's guide
  self-assessment.md honest accounting of strengths and limits
```
