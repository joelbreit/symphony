# 02 — Loop craft: what makes a stem seamless

The engine's contract: a stem file is an **exact musical loop body** (N bars
at the scene's bpm; `loopSeconds` is computed from the score, never measured
from the file) followed by the natural release/reverb **tail** (~2–3 s). The
web engine starts iteration k+1 at `k·loopSeconds` while iteration k's tail
still rings — *the tail is the crossfade*. No trimming, no sample-accurate
looping (AAC can't do that anyway: encoder priming pads the file head by
~45 ms).

That contract only holds if every stem obeys these rules — enforced
fail-fast by `loopcraft.finish()` where a guard can express them:

1. **Nothing starts at or after the loop end** (guarded). The last beats of
   the body may *sound* busy, but every onset belongs to this iteration.
2. **Voices may cross the seam — through the tail window** (guarded: notes
   may ring up to 2 bars past the loop end, never further). This is the
   seam's real continuity mechanism: if every voice broke at the boundary,
   the join would be a simultaneous re-attack of everything, and slow pad
   attacks leave a measurable ~4 dB hole (we measured it). Instead, stagger
   sustained voices so at least one group *starts mid-loop and rings into
   the tail* — under the next head, it simply keeps sounding. Don't
   double-write: a voice ringing into the tail must not also be restated
   at the same position in the head.
3. **CC11 ends where it starts — or a notch above** (guarded: drift 0–14).
   Each iteration is the same rendered file, so this is about *audio*
   continuity at the seam, not MIDI state. An exact round trip actually
   dips: the synth release decays faster than the attack swells, leaving a
   ~4 dB hole for a few hundred ms (measured on the focus bed). Composing
   the loop end slightly hot fills the hole — the tail is the crossfade,
   so mix the crossfade.
4. **No sustain pedal across the seam** (guarded): last CC64 must be a
   release.
5. **Soft attacks near beat 0** (guarded, velocity cap): the AAC priming
   gap means a hard downbeat transient at the file head would click at
   every join. Pads swell in; ostinati start at low velocity; nothing
   percussive on beat 0. This is the one rule that makes the priming gap
   inaudible *by construction*.
6. **Harmonic circularity** (musical, unguarded): the last bar's harmony
   resolves into bar 1 — write progressions as cycles. Modal harmony
   (no leading tones) makes this natural.
7. **Tail must fit the window** (checked at render): scene reverb stays
   modest (~30) and pad releases moderate, so the tail decays inside ~3 s.
   `finish()` pads the MIDI with a harmless CC event past the loop end,
   otherwise fluidsynth cuts the render at the last note-off and the tail
   clicks to silence.

Layering rules (between stems of one scene):

- One mode, one bpm, all stems bar-aligned — any subset must layer cleanly.
- Loop lengths pairwise non-multiple in bars (16/10/12/14/8: the full-state
  recurrence is LCM = 1680 bars ≈ 93 minutes for Focus).
- Stems are voiced in separate registers (bed low, halo high) so any
  combination stays transparent; the engine's job is weather, not counterpoint.
- Humanize stays on (deterministic, ±12 ms): each iteration of a loop is
  identical, but layers drift against each other, which reads as alive.
