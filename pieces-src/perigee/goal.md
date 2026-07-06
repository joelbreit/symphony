# Goal

Compose **"Perigee"** — a nuevo tango for quintet about a satellite in its
final orbits. This one is self-commissioned: Claude chose the image, the
ensemble, and the genre. It is also the first piece built on the shared
`lib/` toolkit, and part of its job is to prove that a small ensemble and a
new genre come as easily as the orchestra did.

The seed image is already found (see `docs/01-inspiration.md`): orbital
decay is tango-shaped. Drag does not slow a falling satellite — it speeds it
up. The closer you fall, the faster you dance. Deepen that image before
writing a note; don't discard it for something easier.

Explore the real idioms first. Nuevo tango has a strict physical language —
marcato in four, the 3‑3‑2 síncopa, arrastre drags into downbeats, the
two-chord ending, the yeites — and a canonical band: violin, bandoneón,
piano, guitar, double bass. Study enough to honor it; the piece should sound
like tango played by people who have played tango all their lives, not like
an orchestra doing an impression.

Then plan the scaffolding: the orbit is the form. Map the alternation of
apogee (far, slow, lyrical) and perigee (close, fast, violent), how each
revolution shortens, where re-entry breaks the cycle, and what is left
afterward. Decide the key moments and effects before building.

Then build it — melodies, progressions, full quintet texture — and
self-assess against real recordings' shape: does the arc measure the way it
was designed? Is every instrument inside its idiom as well as its range?

## Tooling

- Build on `lib/` (see `lib/README.md`): the Piece/Timeline/Ensemble core,
  the DSL, chord charts, figures, groove, and assessment. Define the quintet
  as a custom `Ensemble` in this piece's source — rosters are data.
- Where the toolkit falls short, prefer piece-local helpers first; promote
  to `lib/` only what is genuinely general, and add a test in `lib/tests.py`
  for anything promoted. Likely candidates this piece will surface: a
  marcato/síncopa groove vocabulary, mordent/turn ornaments, maybe a
  scale/mode helper.
- Keep the working record in `docs/`, generate MIDI into `output/`, package
  via `tools/midi_to_piece.py`, render per `web/README.md`.

## Constraints

1. Four to six minutes; one continuous movement.
2. The quintet only — intimacy is the point. No orchestra hiding behind it.
3. Expression is mandatory, not decorative: bellows swells (CC11), piano
   pedal, portamento scoops. This ensemble breathes or it is dead.
4. The final deliverable must be playable and *verified* — listen to the
   render, measure the arc, check the package in the web player.
