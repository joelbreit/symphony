# Self-assessment — "The Punch Line"

What was designed (docs/03) against what was measured, plus the honest
ledger of what a further revision pass should touch.

## Measured against designed

- **Duration**: designed ~3:17 + ring; measured 3:17.5 of music, 197.6 s
  file, 2,782 notes, 158 bars. Inside the goal's 3–5 minute window.
- **Ranges**: `assess.report` clean — A0..G♯7 inside the piano's A0..C8,
  nothing clamped.
- **The arc**: the pianoroll plot's measured-RMS row (rendered WAV)
  reproduces the designed two-hump comedy arc: B′ is the loudest music of
  the first half, the trio sits ~8 dB under it, the pause reads as a real
  hole at 2:31, and the doctored roll is the loudest music in the piece
  before the drop to the final ping. Design and render agree.
- **The pause works on paper and in air**: one full bar of silence (bar
  122) shows as a white column in the roll and a notch in the RMS.

## Playability audit (the "honest for six strains" claim)

A dedicated audit script grouped every simultaneous onset before the
doctored roll (beat 276) and split each group into two hands at the
optimal cut: **879 onset groups, zero groups needing a hand span beyond
a tenth.** The audit caught one real violation on the first build — bar
124's stop-time stab (full bass-plus-chord stack) landing at the same
instant as the melody's B♭5, a quiet three-hand moment — fixed by making
that stab bass-octave-only, which is what a real stop-time left hand does
when the right hand is already talking. After beat 276 the audit is
deliberately not run: the impossibility is the punch line.

## Idiom checklist (docs/02 held to)

- Straight sixteenths, no swing; the keys-family humanize profile is
  pianola-tight (±6 ms). ✓
- The left hand never syncopates; stop-time appears exactly three times
  (D's opening two bars, the tag) so it keeps its power. ✓
- Joplin's law: 96 flat, one +4 crank at the doctored roll only. ✓
- Flat keys, trio in the subdominant, 16-bar strains, varied repeats
  (A′ +8va with octave basses, B′ crushes, C′ music-box octave). ✓
- Crushes, rolls, and tremolos all written as sounded notes. ✓
- Pedal only as trio dabs and under the final chord. ✓

## Web package

Converted with `tools/midi_to_piece.py`, audio re-rendered from the same
MIDI after every source change (sync by construction). Verified in the
dev player: gallery entry, overview constellation, playback with the
playhead igniting notes on time, section labels, emblem (shave-and-a-
haircut completes itself at "two bits"), console clean.

## The honest ledger — for a revision pass

1. **B strain melodic strength.** The secondary-rag cells carry rhythm
   more than tune; A and the trio are the singable strains. If anything
   gets recomposed after human listening, start with B's bars 5–8.
2. **The trio could breathe more** — a turn or two between phrases, and
   its second half leans on sequence. It is warm but not yet the piece's
   heart the way the best trios (Maple Leaf's, Gladiolus') are.
3. **A′ has no new fills** — the octave lift and heavier bass do the
   varying. A roll arranger would have chattered in the phrase gaps
   (bars 4, 8); candidates for a later punch-in.
4. **The doctored escalation** reads clearly in the roll and the RMS;
   whether rung 2 (tremolo filler) *sounds* as distinct from rung 1 as
   it looks needs ears. If it doesn't, thin rung 1 to make room.
5. Nothing promoted to `lib/` yet, deliberately: the stride engine stays
   piece-local until a second rag needs it (lib's own rule: generalize
   from the second use, not the first).
