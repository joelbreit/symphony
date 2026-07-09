# Soundscapes — functional ambient for the listening room

Three endless scenes — **Focus**, **Relax**, **Sleep** — in the spirit of
Endel: music you put on *to do something else to*. Not pieces with arcs and
arguments like the rest of this repo, but rooms with weather: they should
sound composed, breathe slowly, and never obviously repeat.

## The form

Each scene is a small set of **loopable stems** (a drone bed, harmony pads, a
sparse motif, a texture), composed with `lib/` and rendered through the same
fluidsynth pipeline as every other piece. The web player layers them with a
Web Audio engine that loops each stem on its own cycle, drifts gains, swaps
variants, and rests layers — so the combined music only repeats at the least
common multiple of the loop lengths, which is hours. The craft constraints
that make a stem loopable live in `docs/02-loop-craft.md`.

## The bar

The published pieces (The Window, Perigee) are the quality bar — not "good
for generated ambient." The engine choice (layered stems, rather than one
long through-composed loop or browser synthesis) is **explicitly provisional**:
if the stems don't reach that bar at the self-assessment gate
(`docs/04-self-assessment.md`), the decision gets revisited before any more
scenes or interface work. Joel asked for that flag; keep it honest.

## Constraints

- Deterministic builds (seeded, like everything here).
- Each scene ≤ ~8 MB of audio; the whole tab ≤ ~22 MB.
- Every stem must survive its own seam: three loop iterations on headphones
  with no audible join.
- Scenes must work at low volume and at the edge of attention — no events
  that demand listening, no transient that startles.
