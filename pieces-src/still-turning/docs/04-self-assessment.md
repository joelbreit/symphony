# Self-assessment — "Still Turning"

What was designed (`docs/03`) against what was measured, and the honest
ledger of what a further pass should touch.

## Measured against designed

- **Duration**: designed 5:31.7; measured 5:31.7 of music, 2,216 notes, 232
  bars, 27 statements. (The bar map is arithmetic here, not estimation — one
  tempo means the design *is* the duration.)
- **Range**: A0..A7 — the full keyboard except its top three notes. Only the
  final chord and statements 22–23 go below C2; the piece lives in the middle
  four octaves and earns the outer ones.
- **Playability**: 1,196 onsets, **0 errors, 0 stretches, widest hand 12
  semitones**. 833 onsets are a single note or one note per hand; the widest
  interval any hand is asked to hold is an octave, 174 times. The audit
  (`lib/keyboard.py`) is a floor rather than a proof — it checks the notes
  being *struck*, on the assumption that anything still sounding is held by
  the pedal — but the assumption is true here: pedal changes on the bar
  throughout, in half-bars under the sixteenths.
- **The gates**, all clean:
  - the ground, checked bar by bar: the eight notes present on all 216
    downbeats of all 27 statements, nothing ever more than two octaves below
    them;
  - the pulse: 108 strikes, every one an A in the top two octaves, every one
    marked `rigid` and therefore exactly on a beat before the lock and
    exactly on a bar after it;
  - the hinge: the first F♯ in the piece is at beat 410.0, bar 137 beat 3,
    3:24.2 — and the build fails if any earlier one ever appears;
  - the tempo: exactly two marks, the second at the lock, and no others.
- **Peak −8.7 dBFS, no clipping.**
- **The arc**, RMS per statement of the render:

  | span | statements | dBFS |
  |---|---|---|
  | a bit of scruff | — | −52 |
  | the ground | 1–5 | −44 → −31 |
  | sidereal | 6–8 | −44, −41, −42 |
  | the ladder | 9–13 | −35 → −28 |
  | the storm | 14–15 | −27, −26 |
  | the collapse | 16–17 | −42, −37 |
  | a star | 18–23 | −31 → −23 |
  | still turning | 24–27 | −31 → −37 |
  | the coda | — | −55 |

  That is the designed shape: a long quiet opening, a subito drop into
  sidereal, a staircase up the ladder, a false summit, a sixteen-decibel
  collapse in one bar (16.4 dB, statement 15 to statement 16), and a second
  summit three decibels above the first. The last tick is A7 at velocity 50 —
  the same note struck the same way as the first one, 5½ minutes earlier.

- **Density** tracks the subdivision ladder, the one thing in the piece that
  only moves one way: 16 notes in statement 1, 67 · 86 · 144 · 134 · **191**
  across the ladder, then the storm's chordal 97 · 124, down to 21 in the
  collapse, and 136 · **160** · 154 at the anthem.

## What the render changed

Three things the design got wrong and the measurement caught:

1. **The opening was inaudible.** −57 dBFS: 48 dB under the climax, which is
   not "quiet", it is "off". A7 is a thin sample on any soundfont and needs
   real velocity to speak at all. The intro ticks went from 32–54 to 50–71.
2. **The coda was worse** — −76 dBFS, and it is the last thing anyone hears.
   Two causes: the final chord's notes stopped before the coda began (so
   there was nothing under the ticks), and a lone A7 at velocity 30 is
   nothing. Fixed by holding the second sweep's chord for twelve bars and
   doubling the ticks at A6.
3. **The two summits were 1 dB apart**, which makes the false one not false.
   The storm came down about nine velocity units and the ladder's top came
   down with it; the anthem went up five. Two decibels is still a narrow gap
   on paper — see the note in `docs/03` on why it works anyway.

## The honest ledger

**What I think is genuinely good.**

The form and the subject are the same object, which is rare and is the whole
reason to write this piece rather than a nice D minor thing. The ground being
its own retrograde around the dominant does real work in all 27 statements
for free. The mode change costing exactly one note is true, checkable, and
the piece's thesis. And statement 23 — where the tune stops and the bass line
becomes the melody — is an arrival that the form earns rather than a climax
that the volume asserts.

**What I am least sure about.**

- **One key for five and a half minutes.** The ground can't move, so the
  piece never leaves D. Mode, register and density carry everything that key
  normally carries. I believe the constraint is right and I am not certain it
  is enough — a listener who does not notice the mode change at 3:34 will
  hear a long time on one chord centre.
- **Statements 6–8 (sidereal) may be too long a hole.** Thirty-two seconds at
  −42 dBFS at the one-third mark is a lot of quiet to spend before the piece
  has fully earned it. The phasing idea is my favourite thing in the piece and
  I might be protecting it.
- **The storm is not as violent as its name.** It is chordal where the ladder
  before it was in constant sixteenths, so it is *heavier* but not busier, and
  on a synthesised piano heavier reads as slower. On a real instrument the
  attack would sell it; on this soundfont I am relying on the collapse after
  it to do the work.

## The second pass

Three of the five things this ledger asked for have been done.

**The ladder was rewritten** (2026-09-06). It was five statements of one
left-hand figure at increasing speed, which is the failure mode `docs/02`
warns about in someone else's piece. It is now five figures: a sweep, broken
octaves, a sweep under thumb-melody chords, a murky bass, and both hands
sweeping. The subdivision still only ratchets up; the hand changes every
time. The murky bass in statement 12 also does something the piece wanted
anyway — at the busiest point before the storm, the ground note sounds six
times a bar instead of once.

**The anthem's octaves are filled.** Statements 21–22 doubled the melody at
the octave and nothing in between, which is bright and thin. A chord tone
now sits inside the fist — chosen to avoid striking a tritone against the
tune, which matters over the ♭VII where the theme is already sitting on the
tonic's third. The anthem gained a decibel and stopped sounding hollow: the
gap between the false summit and the real one went from 2.1 dB to **3.0**.

**Dynamics are on the page** — `lib/notation.py` now reads them back out of
the velocities for every piece in the collection, hairpins included. Doing it
turned up something worth knowing generally: velocity is a keystroke and a
dynamic is a loudness, and at the top of a keyboard those are very different
things. This piece's coda ticks were written loud so a thin A7 sample would
speak at all, and read literally that printed `mf` over the quietest bars in
the piece. The reader now corrects for register, and the coda's velocities
came down to match what they mean.

**What a further pass should still touch.**

1. **The engraved score has eight unclosed ties** (bars in the long held
   chord), the same Verovio import quirk logged as item 10 in
   `docs/score-backlog.md`. Harmless to the audio, visible on the page.
2. **Try it on a real piano sample library.** Every judgement here about
   weight and attack is a judgement about GeneralUser GS.
3. **The sidereal hole and the one-key question** above are still open, and
   both of them need ears rather than another plot.

## One thing I would not change

The tempo never moves. Not into the summit, not into the last chord, not
anywhere. Every draft instinct wanted to broaden bar 184 and the ending, and
refusing that is the only reason the piece is about what it says it is about.
If a future pass adds a ritardando, it should also change the title.
