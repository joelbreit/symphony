# Goal

Compose **"Still Turning"** — a passacaglia for solo piano, powerful and
inspiring, on a real event: the 1967 discovery of the first pulsar.

Commissioned by Joel ("a powerful, inspiring piano piece"; everything else
composer's choice). Self-directed from there: the image, the form, the key,
and the length are Claude's.

The collection already has one solo-piano piece — *The Punch Line*, a rag
for a machine that cheats. This one has to be its opposite in every respect
that matters: a human at a real keyboard, one tempo, no tricks, and an idea
big enough to hold five minutes of variations without repeating itself.

## The brief to myself

1. **Find a real image, not a mood.** "Inspiring" is not a subject.
   Something happened; find the thing that happened and let the music be
   about that. (`docs/01-inspiration.md`)
2. **Pick a form with a spine.** A passacaglia — a fixed ground repeated
   without alteration while everything above it changes — is the strongest
   architecture in Western music for "the world did not move; we did."
   Use it honestly: the ground is *never* altered, not once.
3. **Make the power structural, not just loud.** The climax has to be
   earned by density, register, and harmony arriving somewhere, not by
   velocity 120 arriving on schedule.
4. **Keep it playable by two human hands.** *The Punch Line* deliberately
   needed more hands than anyone has. This piece must not. Verify it —
   don't assert it.

## Constraints

1. Solo piano. One instrument, 88 keys, ten fingers, one player.
2. Five to seven minutes, one continuous movement.
3. **One tempo.** After the opening locks in, no accelerando, no
   ritardando, no rubato — not even at the end. The reason is in
   `docs/01`; if it stops being a reason, the constraint goes too.
4. The ground bass is fixed forever: same eight notes, same order, same
   register class, every single statement.
5. Piano expression is velocity and pedal. No CC11 hairpins — a piano
   cannot crescendo a note it has already struck, and writing one is a
   lie the render will happily tell.
6. Playable and *verified*: build it, render it, measure the arc, audit
   the hand spans, put it in the player, and listen.

## Tooling

- Build on `lib/` (`lib/README.md`). Roster: the `solo_piano()` preset.
- Piece-local helpers first (`src/ground.py`, `src/themes.py`); promote to
  `lib/` only what is genuinely general, with a test in `lib/tests.py`.
- Working record in `docs/`, MIDI into `output/`, package via
  `tools/midi_to_piece.py`, score via `lib.notation.export`, audio per
  `web/README.md`.
