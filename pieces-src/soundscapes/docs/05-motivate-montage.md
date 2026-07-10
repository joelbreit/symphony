# 05 — Motivate v2: from weather to montage

*Written 2026-07-09, after Joel's redirect on the first Motivate draft.*

## The feedback

The first Motivate (and Focus/Deeper Focus before it) underestimated how
musical a soundscape can be. Not attention-grabbing does not mean empty:
concert music and film scores establish a *vibe* and people study to them
constantly. The brief, in Joel's image: **the soundtrack of a motivational,
tenacious building montage — without any harsh cuts or abrupt transitions.**
Perigee and parts of The Window are closer to the bar than Focus is.

## Why the first draft was empty (the honest diagnosis)

The emptiness was not restraint; it was *structurally forced*. The Eno trick
— loop lengths pairwise non-multiple, layers phase-drifting for hours — only
stays consonant if every layer works against every other layer in **any**
alignment. That forbids progressions (a melody would land on the wrong
chord), forbids themes (they'd collide), and forces pan-diatonic pitch sets.
Weather, by construction, can't have an argument.

## The pivot: one shared form, variation in the conductor

Motivate v2 coordinates all stems on a single **16-bar harmonic form**;
every loop length is a multiple of 16 bars, so any combination of playing
stems is always on the same bar of the same progression — which is what
makes real harmony, a real theme, and real counterpoint possible. What the
Eno trick used to provide (never repeating), the conductor now provides:

- **variants** are alternate composed realizations of the same form
  (a horn statement vs. a cello countermelody; pulsing vs. arpeggiated
  piano), swapped at loop boundaries — always in the right place;
- **rests/returns** re-enter quantized to the 16-bar cycle (new engine
  field `quantizeBars`), so sections enter on the form's downbeat the way
  a montage brings in a scene;
- **gain drift** breathes as before.

The passacaglia is the precedent: concert music holds attention for ten
minutes over an unchanging ground by varying the layers above it. That is
exactly this design.

## The form (E aeolian, 104 bpm, 16 bars)

    | Em | C | G | D |   statement
    | Em | C | G | D |   restatement
    | Am7 | Bm7 | C | D | the riser — roots climb stepwise, the build
    | Em | C | G | D |   peak and return

All four-chord rows are the "axis" anthem loop (i–♭VI–♭III–♭VII), circular
by construction: bar 16's D resolves stepwise up into bar 1's Em, so the
loop seam *is* a resolution. The theme is written so its last note (F#)
steps onto the next iteration's first note (E) **across the seam** — the
join is a cadence, not a cut. Same trick in the bass: bar 16 walks
A–B–C–D up the scale and lands on E at the loop point.

## Stems

Five layers, nine stems, all multiples of the 16-bar cycle (36.9 s):

- **ground** (always, 16) — bass line with real contour: dotted-quarter
  drive on the changes, stepwise walk-ups into each phrase.
- **engine** (always, 16×2) — piano ostinato following the chart: (a)
  pulsing eighths on root/fifth/tenth, (b) rising arpeggio waves. The
  montage motor; never rests.
- **strings** (16×2) — (a) legato voicings swelling through the riser,
  (b) pulsing marcato quarters. The energy selector.
- **theme** (32×2) — (a) horns: a 16-bar melody stated then developed
  over two cycles; (b) celli: a countermelody-character second theme.
  The vibe carrier.
- **descant** (32 flute / 16 celesta) — high color at risers and peaks.

Dynamics stay mp–mf; the montage is determined, not triumphant — it has to
survive an hour of someone else's work.

## What this trades away, on purpose

Full-state recurrence drops from "hours" to ~74 s of *harmonic* state — but
the audible state includes which variants and which layers are up, and that
space (2 always + 3 restable layers × 2 variants × gain drift) does not
restate for a long time. The bet: **memorable material varied beats
unmemorable material permuted.** If the theme nags after an hour, the
fallbacks are longer theme stems (48 bars), more variants, or wider rests —
the architecture absorbs all three.
