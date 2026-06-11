# The listening room — web experience

A React + Vite single-page app that plays compositions with a live piano-roll
visualization. It is fully data-driven: pieces live as self-contained packages
under `public/pieces/<id>/` (manifest + note JSON + audio), and the gallery,
theming, narration, and player all come from each piece's `piece.json`.
**To add a composition, see [../PIECES.md](../PIECES.md).** With a single
registered piece the app skips the gallery and opens it directly.

See [DESIGN.md](DESIGN.md) for the design language.

## Develop

```sh
cd web
npm install
npm run dev
```

## Build & publish

```sh
cd web
npm run build        # outputs static site to web/dist/
```

`dist/` is fully static (HTML + JS + CSS + JSON note data + m4a audio,
~22MB total, almost all of it audio). Deploy it to any static host or any
path on a domain — the app uses relative URLs (`base: './'`), so it works at
`/`, `/symphony/`, or anywhere else. No server-side anything.

Hosting notes:

- Serve `.m4a` with `audio/mp4` MIME type (any sane host already does).
- Enable gzip/brotli for `.json` (the note data compresses ~4×).
- Far-future cache headers on `audio/` and `data/` are safe; filenames are
  stable per release.

## Regenerating The Window's data and audio

The Window's package is derived from the composition in `../compose`:

```sh
# manifest + note JSON  ->  web/public/pieces/the-window/
../.venv/bin/python ../compose/export_web.py

# audio  ->  web/public/pieces/the-window/audio/  (fluidsynth + a GM soundfont)
fluidsynth -ni -g 0.5 -r 44100 -F /tmp/mvt1.wav <soundfont>.sf2 ../output/mvt1.mid
afconvert -f m4af -d aac -b 160000 /tmp/mvt1.wav public/pieces/the-window/audio/mvt1.m4a
# (repeat for mvt2..mvt4; soundfont used for the published render:
#  GeneralUser GS, github.com/mrbumpy409/GeneralUser-GS)
```

Other pieces use the generic converter instead: `tools/midi_to_piece.py`
(see [../PIECES.md](../PIECES.md)).

## Architecture

- `src/App.tsx` — hash router. `#/` is the gallery, `#/<piece-id>` the player,
  `#/<piece-id>?m=<mvtId>&t=<sec>` a deep link (opens seeked, paused). Loads
  `pieces/index.json`, then the selected piece's manifest.
- `src/Player.tsx` — the player. One `<audio>` element, src swapped per
  movement, auto-advance on `ended`; `play()` is always called inside the
  user-gesture call stack (iOS requirement). Drives section labels, moments
  (timestamped annotations with optional auto-spotlight), emblem state, and
  the About panel from the manifest. Sets `--accent` so all chrome follows
  the piece's color.
- `src/PianoRoll.tsx` — canvas renderer. Two modes: *overview* (whole movement
  as a constellation, shown before first play) and *roll* (scrolling window;
  playhead column fixed at 38% width). Notes ahead of the playhead are dim,
  notes crossing it ignite with a glow, notes behind cool over ~2.6s. Only the
  visible time-slice is drawn each frame (binary search into time-sorted notes).
  Pitch range auto-fits the piece.
- `src/Minimap.tsx` — full-piece constellation strip, rendered once to an
  offscreen canvas; doubles as the seek bar (global time across all movements).
- `src/Emblem.tsx` — small SVG staff for a piece's motif; states switch at
  manifest-defined triggers (The Window's Question → Answer).
- `src/theme.ts` — per-family color ramps used when a piece doesn't specify
  instrument colors.
- Time sync: the canvas reads `audio.currentTime` every frame; note JSON and
  audio must derive from the same MIDI/tempo map, so they agree by
  construction.
