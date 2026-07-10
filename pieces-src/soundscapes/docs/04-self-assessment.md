# 04 — Self-assessment: the quality gate (M2)

*Status: measured-clean; awaiting the by-ear verdict (Joel's flagged
revisit point). Written 2026-07-08 after the Focus scene's nine stems.*

## What was measured (all pass)

- **Seams.** Every stem survives simulated overlap-add (the exact schedule
  the engine plays): no clicks (inter-sample deltas at seams *below*
  steady-state levels), level continuity within 2 dB for continuous layers,
  silence-to-silence joins for sparse layers, and the pulse's seam is
  indistinguishable from its own internal bar lines. Verified offline
  (numpy) and live in the browser (AnalyserNode RMS trace rolls straight
  through the join).
- **The composite.** Variant-a mix at manifest gains, 4 minutes: no silence
  holes, 8 dB gentle undulation, 30-second means flat within 0.9 dB —
  weather, not narrative, which is the design. 24 dB of headroom.
- **Craft rules held by construction.** Two findings during the spike are
  now rules: (1) an exact CC round trip *dips* at the seam because release
  outruns attack — continuous layers instead put a voice group across the
  seam through the tail window; (2) instant-attack instruments (the organ
  anchor) are seam-proof by nature and anchor each bed.
- **Determinism, budget.** Byte-identical MIDI across builds; 5.8 MB for
  the scene (budget ≤ 8 MB).

## Honest musical assessment against the bar

The bar is The Window and Perigee — composed music with an argument. A
soundscape's argument is its restraint, so the fair comparison is: *would a
listener who trusts this repo's name on the tin accept an hour in this
room?*

Strengths I'll defend: the modal harmony circulates without cadence and any
layer subset in any phase stays consonant (verified across the full LCM
cycle by construction, and audibly in the rig); the Eno-style unequal loops
genuinely never restate an alignment inside a session; the breathing is
composed, not LFO'd.

The risk, named plainly: **timbre**. These are GeneralUser GS General MIDI
pads. Layered, they can read as "GM demo" rather than as a produced ambient
record — that is exactly the gap analysis cannot judge and the reason this
gate exists. Secondary risks: the kalimba pulse may read music-box rather
than metronome-you-lean-on; the e-piano motif is deliberately plain.

## The listening protocol (the open half of this gate)

`web/public/loop-test.html?scene=focus` (dev server), headphones:

1. Solo each stem ≥ 3 loop iterations — any audible join fails the stem.
2. bed+harmony, then +halo, then +motif, then +pulse — does each addition
   deepen the room or cheapen it?
3. Leave the full mix on for 10+ minutes at low volume while doing
   something else — the real test: does it hold, or does it nag?

## Verdict

Provisional pass — everything measurable is clean, and the construction
rules are sound. **The by-ear verdict is open and gates further composing
(Relax/Sleep) and polish.** If the timbre falls short, the prepared
fallbacks, in order of increasing retreat: (a) re-voice on better patches /
layer two patches per pad; (b) fewer, longer through-composed loops per
scene; (c) one long-form loop per scene with a simple crossfade looper —
the engine's manifest contract survives all three.

## Addendum (2026-07-08): Deeper Focus joins the same gate

A second scene, **Deeper Focus** (D dorian, 60 bpm — docs/03), was composed
on Joel's request before the by-ear verdict landed. Its measurements match
Focus: all 9 stems seam-clean by analysis (bed −42.3/−43.3 dB across the
seam; murmurs silence-to-silence; tide within 1.8 dB of an internal grid
boundary), composite peak −24.0 dBFS, zero holes, 30 s means flat within
1.4 dB. Same timbre risk, same protocol — listen with
`loop-test.html?scene=deeper-focus` or the player at `#/focus/deeper-focus`.
The fingered-bass tide is the one new patch: judge whether it reads as a
tide or as a GM bass demo.

## Addendum (2026-07-09): Motivate — redirected, rebuilt, same gate

A third scene, **Motivate**, was first drafted in the Focus mold (G
mixolydian, 84 bpm, pan-diatonic layers on unequal cycles). It measured
clean, but Joel redirected before the by-ear verdict: the soundscapes
underestimate how musical they can be — the bar is a film score for a
tenacious building montage, closer to Perigee than to Endel. The draft was
replaced, not patched; docs/05 records the diagnosis (the Eno phase-drift
trick *structurally forces* emptiness) and the new architecture: one shared
16-bar form, all loop lengths multiples of it, re-entries quantized to the
cycle, variation moved into the conductor.

The rebuilt scene (E aeolian, 104 bpm) has a real theme (horns, developed
over two cycles; celli answer theme as the swap), a bass line with contour,
a piano engine on the changes, string swells through a composed riser, and
seams written as cadences (F# resolving to E across the join; the bass
walking A–B–C–D into the downbeat).

Measurements, against the same standards: engine and strings within 1.6 dB
across the seam; ground, themes, and celesta seams all *inside* their own
internal phrase-boundary ranges (ground +3.5 vs internal +1.2..+5.7; horn
theme +4.4 vs −2.5..+42; cello theme −6.7 vs −9.5..+24; celesta +50.6 vs
+44..+50 — a glint out of silence is always a step, at the seam no more
than anywhere else); flute silence-to-silence. Composite: peak −21.2 dBFS,
zero holes, 30 s means flat within 0.70 dB. 7.4 MB (budget ≤ 8).

What analysis cannot judge, for the by-ear pass (`loop-test.html?scene=
motivate` or the player at `#/focus/motivate`): (1) **the theme's wear** —
memorable material varied is the whole bet; if the horn melody nags after
an hour, the fallbacks are longer theme stems, more variants, wider rests;
(2) whether the 16-bar harmonic recurrence reads as passacaglia (holds) or
as a stuck loop (nags) when only ground+engine are up; (3) GM brass/string
timbre at mf — the montage register exposes the soundfont more than pads
ever did.
