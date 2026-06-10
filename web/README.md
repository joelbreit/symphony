# The Window — web experience

A React + Vite single-page app that plays the symphony with a live piano-roll
visualization. See [DESIGN.md](DESIGN.md) for the design language.

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

## Regenerating the data and audio

Both are derived from the composition in `../compose`:

```sh
# note/section/tempo JSON  ->  web/public/data/
../.venv/bin/python ../compose/export_web.py

# audio  ->  web/public/audio/   (requires fluidsynth + a GM soundfont)
fluidsynth -ni -g 0.5 -r 44100 -F /tmp/mvt1.wav <soundfont>.sf2 ../output/mvt1.mid
afconvert -f m4af -d aac -b 160000 /tmp/mvt1.wav public/audio/mvt1.m4a
# (repeat for mvt2..mvt4; soundfont used for the published render:
#  GeneralUser GS, github.com/mrbumpy409/GeneralUser-GS)
```

## Architecture

- `src/PianoRoll.tsx` — canvas renderer. Two modes: *overview* (whole movement
  as a constellation, shown before first play) and *roll* (scrolling window;
  playhead column fixed at 38% width). Notes ahead of the playhead are dim,
  notes crossing it ignite with a glow, notes behind cool over ~2.6s. Only the
  visible time-slice is drawn each frame (binary search into time-sorted notes).
- `src/Minimap.tsx` — full-symphony constellation strip, rendered once to an
  offscreen canvas; doubles as the seek bar (global time across all movements).
- `src/App.tsx` — audio element + state. One `<audio>` per page, src swapped
  per movement, auto-advance on `ended`. `play()` is always called inside the
  user-gesture call stack (iOS requirement).
- `src/MottoStaff.tsx` — hand-drawn SVG of the four-note Question; switches to
  the five-note Answer (gold final C) during the finale's chorale.
- Time sync: the canvas reads `audio.currentTime` every frame; the note JSON
  was exported through the same tempo map that generated the MIDI the audio
  was rendered from, so they agree by construction.
