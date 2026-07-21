# The Punch Line — a rag for the player piano

A classic piano rag: stride left hand, syncopated right hand, A♭ major
with the trio in D♭, 2/4 at Joplin's printed tempo law. Six strains of
honest two-hand ragtime; then the roll gets doctored the way QRS doctored
theirs, and the final strain needs more hands than anyone has. It ends
with shave-and-a-haircut and one last hole punched in the roll.

~3:20 · 158 bars · 2,782 notes. Commissioned by Joel (fun, catchy,
skillful; details composer's choice). Second piece built on the shared
`lib/` toolkit.

## Build

```sh
cd pieces-src/the-punch-line
../../.venv/bin/python src/compose.py    # MIDI + marks.json + roll.png into output/
```

Render + package (per `web/README.md` / `PIECES.md`):

```sh
fluidsynth -ni -g 0.5 -r 44100 -F output/the_punch_line.wav \
    ../../../soundfonts/GeneralUser-GS.sf2 output/the_punch_line.mid
afconvert -f m4af -d aac -b 160000 output/the_punch_line.wav \
    ../../web/public/pieces/the-punch-line/audio/mvt1.m4a
cd ../.. && .venv/bin/python tools/midi_to_piece.py --id the-punch-line \
    --title "The Punch Line" --composer "Claude" \
    pieces-src/the-punch-line/output/the_punch_line.mid
```

## Layout

- `goal.md` — the commission.
- `docs/01-inspiration.md` — the image: a rag is a joke told in eighth
  notes; the punched roll; the doctored-roll license.
- `docs/02-ragtime-idioms.md` — the study: form, the left hand's law, the
  syncopation vocabulary, harmony, roll practice.
- `docs/03-blueprint.md` — bar map, charts, registers, dynamics targets.
- `docs/04-self-assessment.md` — measured vs designed, the playability
  audit, the honest ledger.
- `src/rag.py` — stride engine, stop-time, walking octaves, crushes,
  the octave-doubler, the impossible scale run.
- `src/themes.py` — the strains, every one bar-guarded (`B(…, n, (2,4))`).
- `src/compose.py` — assembly; build entry point.
- `output/` — MIDI, marks.json, roll.png, WAV (not committed if large).

The web package lives at `web/public/pieces/the-punch-line/`.
