# Goal

Compose **"Roy G. Biv"** — a rain-to-rainbow jubilee for seven-color band —
under a double mandate:

1. **The song must be fun.** Not pretty-fun, not clever-fun: actually fun.
   The kind of piece that makes someone tap the desk. Groove is mandatory.
2. **The piano roll must be a picture.** `output/roll.png` — the image
   `lib.assess.pianoroll` draws — has to read, instantly, as a drawing of
   something. The target: the drawing every kid makes after a storm. Rain,
   clouds, a lightning bolt, the ground, the sun, and a rainbow arched over
   everything. Someone who has never heard of this project should glance at
   the roll and say "that's a rainbow" without being prompted.

The two mandates are one mandate. Every visual element must be a real
musical event that earns its place by ear, and every musical event lands
somewhere on the canvas — so the picture is composed, not drawn. The seed
insight is in `docs/01-inspiration.md`: the toolkit's seven instrument-family
colors, stacked in the right order, *are* ROYGBIV. The rainbow is not
painted onto the music; the orchestration is the rainbow.

## The canvas (know it before writing a note)

`lib/assess.py` draws each pitched note as a horizontal dash: x = real
seconds (via tempo map), y = MIDI pitch, color = instrument *family*,
opacity = velocity (0.3–0.85), line width 1.6. The roll panel is roughly
2000×560 px, so at ~3 minutes each second is ~10 px wide and each semitone
~7–10 px tall. Consequences to design around:

- **Percussion never prints.** Drums and thunder are invisible — the free
  groove engine under the picture, and the joke that makes the lightning
  work (you can draw lightning; you can't draw thunder).
- **Velocity is paint density.** Loud = saturated, soft = pale. Dynamics and
  shading are the same decision.
- **Melodic contour is line.** Stepwise motion at ~1 semitone per second
  reads as a smooth curve; a leap is a gap. Fills are texture (tremolo,
  gliss), outlines are tunes.
- **Marks draw vertical lines + labels.** Use few, at scene boundaries only,
  or none.
- **Title prints at top, family legend at lower right.** Keep the picture's
  lower-right corner expendable.

## Tooling

- Build on `lib/` (see `lib/README.md`): Piece/Timeline/Ensemble, the DSL,
  chords, figures, groove, assessment. Roster as data in `src/band.py`,
  piece-local idioms in their own module, build via `src/compose.py` —
  follow the Perigee pattern.
- Add a piece-local "scene geometry" helper that maps (seconds, pitch)
  targets to beats/notes, so image landmarks and musical landmarks are
  declared in one place. Promote to `lib/` only if it turns out general.
- Iterate with eyes *and* ears: regenerate `output/roll.png` constantly
  while composing, and listen to every render. Keep the working record in
  `docs/`.

## Constraints

1. Two and a half to four minutes; one continuous scene.
2. The music must stand alone with eyes closed — if a passage exists only
   to place pixels, recompose it until it doesn't.
3. The image must stand alone without the music — the squint test: rain,
   rainbow, sun, ground, recognizable at a glance from across the room.
4. Deterministic build (seeded RNG), ranges guarded, playable and
   *verified*: listen to the render, look at the roll, check the package in
   the web player.
