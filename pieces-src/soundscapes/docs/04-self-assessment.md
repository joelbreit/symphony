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
