# vibe-compositions

A collection of original musical compositions — each generated as playable MIDI
by Claude — gathered into one repository and surfaced together in a single
piano-roll web player. Claude is the composer.

## The compositions

Each piece is a self-contained project under `pieces-src/<slug>/`, with its own
generator source, `goal.md`, creative `docs/`, and rendered `output/`.

| Piece | Slug | About |
|-------|------|-------|
| **The Window** | [`pieces-src/the-window`](pieces-src/the-window) | Symphony No. 1 in C minor — four movements, full orchestra (music21) |
| **The Unfinished Spire** | [`pieces-src/the-unfinished-spire`](pieces-src/the-unfinished-spire) | An anthem for the builders of things they will not see finished (midiutil) |
| **Royal Street Rattler** | [`pieces-src/royal-street-rattler`](pieces-src/royal-street-rattler) | A Dixieland strut for six players (midiutil) |
| **High Street Riot** | [`pieces-src/high-street-riot`](pieces-src/high-street-riot) | A grotesquely funky vamp-jam for an oversized Dixieland band (music21) |
| **The Box Is Full** | [`pieces-src/the-box-is-full`](pieces-src/the-box-is-full) | Korobeiniki (the Tetris tune) as folk tragedy, for orchestra and square wave (music21) |
| **Perigee** | [`pieces-src/perigee`](pieces-src/perigee) | A nuevo tango for a falling satellite — Piazzolla quintet (lib) |

The first five pieces were built on two generator lineages — **music21** and
**midiutil** — kept as independent forks per piece; they stay frozen as-is.
See each piece's README for how to rebuild it. The best tools from both
lineages now live in [`lib/`](lib/), the shared composition toolkit that new
pieces start from (note DSL, chord charts, ensemble presets, groove and
humanize, CC expression, direct MIDI writer, assessment plots — see
[lib/README.md](lib/README.md)). **Perigee** is the first piece built on it.

## The web player

[`web/`](web/) is a React app that plays every composition with a live
piano-roll visualization — notes color-coded by orchestral family, a fixed
"window of attention" playhead, poetic section labels, a full-piece
constellation seek bar, and per-instrument spotlighting. Mobile-first; audio
pre-rendered to AAC.

```sh
cd web && npm install && npm run build   # → web/dist/, fully static
```

Each composition is a self-contained package under `web/public/pieces/<id>/`
(manifest + notes JSON + audio), registered in `web/public/pieces/index.json`.
**[PIECES.md](PIECES.md)** documents how to package a new one — a MIDI file per
movement is nearly all it takes, and `tools/midi_to_piece.py` does the
conversion. (The Window is the exception: its package is generated directly from
its music21 sources by `pieces-src/the-window/export_web.py`.)

See [web/README.md](web/README.md) for publishing notes and
[web/DESIGN.md](web/DESIGN.md) for the design language.

## Environment

One shared Python environment at the repo root serves every piece:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt   # music21, mido, midiutil, matplotlib, numpy
```

Python 3.14 works. Each piece builds from its own directory (see its README);
generators write to that piece's local `output/`.

## Adding a new composition

1. Create `pieces-src/<your-slug>/` with your generator source, a `goal.md`, and
   `docs/` for the creative record. Start the generator from the
   [`lib/`](lib/) toolkit (`python -m lib.demo` shows two worked examples).
2. Generate MIDI (one file per movement) into your piece's `output/`.
3. Package it for the player following [PIECES.md](PIECES.md).
