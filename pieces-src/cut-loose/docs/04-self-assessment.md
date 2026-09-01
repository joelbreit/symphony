# Self-assessment — "Cut Loose"

What was designed (docs/03) against what was measured, plus the honest
ledger of what a further pass should touch.

## Measured against designed

- **Duration**: designed ~5:00; measured 5:07.6 of music, 310 s rendered,
  5,107 notes, 176 bars. Inside the goal's 4–5½ minute window.
- **Ranges**: `assess.report` clean — cornet D4..C♯6, clarinet B♭4..G6
  (G6 touched at the top of the clarinet chorus and the cry, where a
  New Orleans clarinetist actually goes), alto D4..A♭5, trombone G2..G4,
  sousaphone E♭1..E♭3 (E♭1 only under the last chord).
- **The cornet's silence**: first sounding event at beat 175.8 — the
  grace notes of the smear into his first note in bar 45. Checked in the
  build (`check_cornet_silence`); the build fails if anything earlier
  ever creeps in.
- **The arc** (RMS of the render, per section):

  | section | dBFS |
  |---|---|
  | the cadence | −39.4 |
  | the hymn | −32.0 |
  | the cry | −26.3 |
  | amen | −32.6 |
  | the whistle (2.1 s of true silence, then −34.8) | −39.7 |
  | snares on → riffing in | −27.5 → −26.9 |
  | the strut ×2 | −26.2, −25.9 |
  | the ramble, trombone, clarinet | −26.1, −27.2, −26.3 |
  | the umbrellas go up | −24.3 |
  | home | −24.2 |
  | the tag | −21.8 |
  | benediction | −39.6 |

  That is the designed shape: a low plateau rising to the cry, the Amen
  dying into real silence, the second line climbing in steps to the tag
  as the loudest bar, and a single quiet tail. Peak −7.4 dBFS, no
  clipping. The first hymn statement was lowered ~6 velocity units after
  the first render to widen the lift into the second line.
- **Vibrato is real**: pitch-tracked on this soundfont, CC1 = 127 gives
  ±37 cents on every horn; the dirge leads run 80–110, the second line 0.

## Idiom checklist (docs/02 held to)

- Two drummers as two instruments; no banjo, no piano. ✓
- Dirge cadence (bass drum 1 and 3, muffled buzz rolls), sousaphone
  halves with walks, hymn in quarters and halves, the tear once per pass,
  plagal Amen with rit. ✓
- The turn staged in order: silence → whistle (GM 72 then 71×2) → snare
  alone → bass drum → sousaphone riff (the call in the bass) → horns
  riffing → one hit → the cornet alone. ✓
- Street beat with the and-of-2 bass drum, cymbal chick, rotating snare
  cells, fills every fourth bar; two-beat sousaphone with chromatic
  walk-ups; four-to-the-bar only in the second half of Home. ✓
- Collective improvisation audit (bars 46–165, shout chorus excluded):
  per half-bar, front-line voices moving in eighths (≥ 3 short onsets):
  none 69 %, one 30 %, two 1 % (two half-bars, both phrase-turn pickups).
  Clarinet below the cornet in 3 of 385 sounding overlaps; trombone above
  the alto never. ✓
- Long-note chord-tone check on every hand-written lead: every flagged
  note is an intended appoggiatura (the hymn's D over E♭), an anticipation
  of the next chord on the and-of-4, or a dominant extension (13ths on
  E♭7). No wrong notes found. ✓
- Light swing (0.58), one tempo push (196 from the shout), the tag with
  the head in octaves and the clarinet trill. ✓

## Web package and score

Converted with `tools/midi_to_piece.py`, audio re-rendered from the same
MIDI after the last source change; manifest hand-written (concept, four
program-note paragraphs, 19 narrated sections, the call as a
two-state emblem that accents the E♭ when the tune is cut loose, five
moments). Score exported by `export_score.py` with **0 ms** worst sync
drift against the piece's own clock. Verified in the dev player: gallery
card, overview constellation, playback with the playhead igniting notes
on time, section labels, the score toggle, console clean.

## The honest ledger — for a revision pass

1. **The dirge is long for a listener who came for Dixieland** (1:58
   before the whistle). It earns the turn, and the cry gives it a peak,
   but a human ear might want the first hymn statement trimmed to twelve
   bars. I kept sixteen because the tune needs to be *known* before it
   comes back fast.
2. **The muffled snare is velocity, not timbre.** GM has no snares-off
   sample; the dirge rolls are soft 32nd-note buzzes. A real dead-march
   snare is duller and wetter than anything this soundfont can do.
3. **The riff backgrounds are generated** (chord-tone stabs) and could
   be more melodic — real brass bands riff in little tunes, not just
   thirds and fifths on the offbeats. The hand-written shout chorus shows
   what the backgrounds could sound like everywhere.
4. **The obbligato is better than Rattler's** (four run types, scale
   passages, triplet turns) but still chooses by dice; a clarinetist
   would answer the lead's actual phrase shapes.
5. **The trombone chorus mirrors the head's stop-time bars** deliberately
   ("his way"); if it reads as a copy rather than a callback, bars 7–8
   are the ones to recompose.
6. Nothing promoted to `lib/` yet: the street beat, the two-beat bass and
   the block-harmony helper are candidates once a second walking-band
   piece needs them (lib's rule: generalize from the second use).

## The meta-level check

The trap for a second Dixieland piece is writing the first one again
with different chords. The defenses here were structural: a form the
catalog did not have (the two-part funeral), a band that could not be
the first band (it walks, so no banjo), a rule the first piece could
not have followed (the lead is silent for two minutes), and one idea
that the whole piece is a demonstration of — that a melody can grieve
and dance without changing a note. The piece can be described in one
sentence, and the sentence is not about a streetcar. That is the test.
