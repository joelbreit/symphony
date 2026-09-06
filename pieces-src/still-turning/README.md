# Still Turning — a passacaglia on a dead star

Solo piano, D minor to D major, 3/4, ♩=134.6 and never anything else.
Twenty-seven statements of eight bass notes that are never altered, over one
tempo set by the rotation of PSR B1919+21 — the first pulsar, found in 1967 in
a quarter inch of scruff on a roll of chart paper. One 3/4 bar is one
rotation: 1.3373 seconds.

The opening ticks one pulse per *beat*; when the ground locks in, the tempo
triples so one pulse becomes one *bar*. The pulse rate does not change across
that — nothing sped up, we just started seeing what was between the pulses.
After it, the tempo never changes again, including at the end, because the
subject of the piece is something that does not slow down for us.

5:32 · 232 bars · 2,216 notes · playable by two hands (verified: widest hand
an octave). Self-commissioned from Joel's brief — "a powerful, inspiring piano
piece", everything else composer's choice. Fifth piece built on the shared
`lib/` toolkit; the second for solo piano, and the opposite of the first in
every way that matters (*The Punch Line* is a machine that cheats; this is a
person at a keyboard).

## Build

```sh
cd pieces-src/still-turning
../../.venv/bin/python src/compose.py     # MIDI + marks.json + roll.png, and
                                          # runs every gate and the hand audit
```

The build **fails** if the ground was altered, if the pulse voice drifts off
the grid, if an F sharp appears before the hinge, if a second tempo change
sneaks in, or if any chord needs a third hand.

Render, package, engrave (from the repo root):

```sh
.venv/bin/python tools/render.py pieces-src/still-turning/output/still_turning.mid \
    --id still-turning
.venv/bin/python tools/midi_to_piece.py --id still-turning \
    --title "Still Turning" --composer "Claude" \
    pieces-src/still-turning/output/still_turning.mid
(cd pieces-src/still-turning && ../../.venv/bin/python export_score.py)
```

## Layout

- `goal.md` — the brief, and the four rules I set myself.
- `docs/01-inspiration.md` — Jocelyn Bell, the scruff, LGM-1, and why a
  passacaglia is not a metaphor for a pulsar but the same object.
- `docs/02-passacaglia-and-piano.md` — how a variation set avoids being a
  list; the register map, the pedal scheme, and the three things that keep
  MIDI piano from sounding like porridge.
- `docs/03-blueprint.md` — the constants, the ground, the theme, and the
  bar-by-bar map of all 27 statements.
- `docs/04-self-assessment.md` — measured against designed, what the render
  forced, and the honest ledger.
- `src/ground.py` — the ground, the pulse, the chord pools, `roll_to` (a
  rolled chord whose *top* lands on the beat, because the top note is the
  pulse).
- `src/themes.py` — the theme in both modes, the sixths, the phasing cells;
  every one bar-guarded.
- `src/compose.py` — the twenty-seven statements, and the gates.
- `export_score.py` — folds the performance's rolls back into notated chords
  and engraves.

## What this piece put into `lib/`

- **`lib/keyboard.py`** (new) — hand assignment and a playability audit for
  any keyboard piece: span, finger count, and reach at the tempo actually
  available. It found 272 real problems in the first draft.
- **`Note.rigid`** (`lib/piece.py`, `lib/groove.py`) — material that opts out
  of swing, lean and timing jitter but keeps velocity jitter: a machine part
  inside a human performance. It draws from the RNG like any other note, so
  marking something rigid does not reshuffle anything else.
- **Exact tempi in the engraved score** (`lib/notation.py`) — music21 rounds
  `<per-minute>` and `<sound tempo>` to whole BPM on export, which silently
  desynced this score by a second over five minutes. Now restored from the
  piece's own timeline. Every piece with an integer tempo is unaffected;
  every future piece with a tempo taken from the world is not.
- **Dynamics and hairpins on the engraved page** (`lib/notation.py`,
  `lib/notation_m21.py`) — velocity is the dynamic in this system, so the
  page can read it back: band it, smooth it, print the plateaus and the
  ramps. All ten pieces in the collection have them now. It included one
  finding worth keeping: velocity is a keystroke and a dynamic is a
  loudness, and at the top of a keyboard those are not the same number.
