# Roy G. Biv — a rain-to-rainbow jubilee for seven-color band

The piece whose piano roll is also a picture. `output/roll.png` is the
deliverable twice over: the same notes that play the music draw a child's
after-the-storm scene — gray tremolo clouds, blue pizzicato rain, an amber
lightning bolt (the thunder is drums, and drums don't print), a
walking-bass ground line, a harp-glissando sun, and a rainbow whose seven
stripes are the seven instrument families in ROYGBIV order. See
`docs/01-inspiration.md` (the found palette) and `docs/02-the-canvas.md`
(the geometry).

~3:10, one continuous scene. D minor storm → F major jubilee. Seed 1666.

## Build

```sh
cd pieces-src/roy-g-biv
../../.venv/bin/python src/compose.py    # MIDI + marks.json + roll.png into output/
```

Audio render (per `web/README.md`, GeneralUser GS):

```sh
fluidsynth -ni -g 0.42 -r 44100 -F output/roy_g_biv.wav \
    ../the-unfinished-spire/assets/GeneralUserGS.sf2 output/roy_g_biv.mid
# trim the tail past ~190 s, then re-run compose.py to overlay measured RMS
afconvert -f m4af -d aac -b 160000 output/roy_g_biv.wav \
    ../../web/public/pieces/roy-g-biv/audio/mvt1.m4a
```

Web package: `tools/midi_to_piece.py --id roy-g-biv …` (manifest is
hand-edited; re-runs preserve it).

## Source layout (the Perigee pattern)

- `src/band.py` — roster as data: the seven stripe chairs (one per family,
  so the roll's colors stack into a spectrum) + rain, bass, harp, clouds, kit.
- `src/scene.py` — the geometry↔music mapper: seconds/pitch plane, F-major
  lattice, the arch ellipse, rain field, cloud blobs, bolt, sun disc.
- `src/grooves.py` — the invisible rhythm section (percussion never prints).
- `src/compose.py` — the scene assembled: gray morning, storm, turn,
  rainbow, outro, sun.

## The constraint that shaped everything

One tempo (120), because x = seconds and the drawing needs a linear ruler.
Velocity = opacity, so dynamics and shading are one decision. Melodic
steps ≈ 1 semitone/second read as smooth curves. Percussion is invisible,
so all the fun lives there for free. `lib.assess.pianoroll` grew
`legend_loc` and `lw` parameters for this piece (legend placed in empty
sky; crayon-weight stroke).
