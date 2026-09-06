# The composer's notebook

Craft that transfers between pieces. Not the API (that's `lib/README.md`) and
not the map (that's `CLAUDE.md`) — this is the part that is hard to work out
twice. Add to it when a piece teaches you something a future composer would
otherwise have to learn again. Keep entries short and say which piece taught
you.

---

## Before any notes

**Find a real thing, not a mood.** "Inspiring" is not a subject; "a graduate
student found a quarter inch of scruff on a roll of chart paper" is. Every
piece in this collection that works is *about* something specific enough to
argue with. The moods are what the specifics produce, not the other way round.

**Make the form and the subject the same object, if you can.** A metaphor laid
over a form is decoration and the listener can feel the seam. When the form
*is* the thing — the orbit as the shape of *Perigee*, a joke's anatomy as the
strain order of *The Punch Line*, a passacaglia's fixed ground as a pulsar in
*Still Turning* — every structural decision after that makes itself, and they
all agree with each other. This is the single highest-leverage decision
available and it is made before a note exists.

**Set one rule you refuse to break, and say why in `docs/01`.** Not for
discipline's sake: a real constraint decides hundreds of small questions for
you and makes the piece coherent in a way taste alone will not. *Still
Turning* never changes tempo after bar 9. *The Punch Line* obeys two-hand
ragtime rules for six strains precisely so it can break them in the seventh.
The rule has to cost you something or it isn't one.

**Write the bar map before the code.** `docs/03` is a contract with yourself:
sections, bar numbers, subdivision, dynamic, and one sentence of what happens.
Writing it takes an hour and saves a day, because every later question ("how
long is this?", "is this too loud?") has an answer to check against instead of
being re-litigated.

## Making a variation set, a jam, or any long form that repeats

**Put your parameters on different schedules.** The failure mode of every
repeating form is that all its parameters move together, so the piece has one
gesture and plays it twenty times. Decide separately how subdivision, dynamic,
register, texture and harmony each move, and make sure at least two of them
disagree at any moment. In *Still Turning* the loudest minor music arrives
*before* the fastest music finishes, and the quietest statement in the second
half comes immediately after the loudest.

**Two summits beat one ramp.** A single five-minute crescendo is not a shape.
A false summit that collapses, then a real one, is — and the collapse is what
makes the second one audible. Measure it: the collapse in *Still Turning* is
16 dB in one bar and it is doing more work than the 2 dB by which the real
summit exceeds the false one.

**Group your repetitions and give each group a door.** Five statements in a
row with a new texture each is a list. Five statements that share an idea, with
an opening gesture on the first bar of each group, is a paragraph.

## Mechanics that pay for themselves

**Guard every melody with `B(dsl, n_bars, meter)`.** It catches almost every
note-entry error, immediately, with the offending string in the message. Four
lineages of this repo independently converged on this; do not skip it.

**Gate your own compositional rules in the build.** This is the biggest
quality lever in the repo and it is underused. If your piece claims the ground
never changes, write the assertion that extracts the bass from the finished
note list and compares it to the ground, 27 times, and make the build exit
nonzero. If it claims one instrument is silent until bar 45, assert it (*Cut
Loose* does). If it claims no F sharp before bar 137, assert that. A claim in a
README is a hope; a claim in the build is a fact. `pieces-src/still-turning/
src/compose.py` has four of them at the bottom and they all caught something.

**Render early and measure the arc, not the velocities.** The designed arc and
the measured arc are different animals. Velocity → loudness is badly
compressed at the top (nine velocity units bought one decibel in the storm)
and *density* moves RMS more than velocity does. `assess.pianoroll(p, path,
wav=...)` puts both under each other; the first render of *Still Turning*
moved more music than any amount of thinking before it.

**Write a probe instead of guessing.** When something is off — a hand
assignment, a voicing, a drift — spend the thirty seconds to print exactly the
thing at exactly the beat. Every time I guessed instead, I was wrong and paid
for it twice.

**After touching `lib/`, run `tools/check_all.py`.** It rebuilds every
lib-built piece and fails if one byte of anybody's finished MIDI moved. The
generators are seeded and deterministic precisely so this check works; the
failure it catches (published audio and regenerated MIDI drifting apart) is
silent and horrible.

**Velocity is a keystroke; a dynamic is a loudness.** They are the same number
only in the middle of an instrument's range. A thin top octave needs real force
to speak at all, so a composer writing for a sampler pushes it — and then the
engraved score, reading velocity back, prints `mf` over the quietest bars in
the piece. Two consequences worth carrying: when you catch yourself pushing
velocity to fix *audibility*, write down that you did, because it is no longer
expressing loudness; and when you read velocity back for anything (a dynamic
mark, an arc plot, a mix decision), correct for register or know that you
haven't. *(Still Turning, via `lib/notation._effective_vel`)*

**A list of textures is not a paragraph.** The most useful test I know for a
long repeating form: describe each statement in three words. If two of them
get the same three words, one of them is not earning its place. *Still
Turning*'s subdivision ladder was "sweep, faster sweep, faster sweep" and had
to be rewritten as wave / hammer / swirl / shimmer / torrent. The ratchet that
justified it (the subdivision) was real; the sameness underneath it was not.

## Traps, with the piece that found them

- **A piano cannot crescendo a held note.** `Piece.hairpin` (CC11) is right
  for a bandoneón and a lie on a keyboard — a GM synth will render it happily
  and it will sound like an organ. Velocity is the dynamic. Pedal (CC64) is
  the other half. *(Still Turning)*
- **Three registers at once is three hands.** A bass note, a tune and
  something at the top of the keyboard cannot be struck together. Either fold
  one into another voice, or roll the chord so the hand sweeps into it — and
  when the top note is the one that matters, roll so it *lands on* the beat
  rather than starting there. *(Still Turning; `src/ground.py:roll_to`)*
- **Check the seams.** Unplayable leaps hide at section boundaries, where a
  hand that ended a run in one register has to start the next one somewhere
  else. Leaving the last beat before a big entrance empty fixes it and is
  better music anyway — it is a breath. *(Still Turning)*
- **Nothing tighter than a fifth below C3, or a third below C4.** Almost every
  "the MIDI piano sounds like sludge" complaint is that rule being broken.
- **`Piece.add` quantizes starts to 1/96.** If you record note positions to
  find them again later (for a score-only retime, say), quantize your record
  the same way or it will not match. *(Still Turning)*
- **`s * 4` on a DSL string concatenates without spaces.** Use `R(s, 4)`.
- **MIDI meta text is latin-1.** `lib/` sanitizes; older writers may not.
- **music21 rounds tempo to whole BPM on MusicXML export.** Fixed in
  `lib/notation.py`, but the shape of the bug is worth remembering: it was
  invisible on the page and cost a second of score/audio sync over five
  minutes. *(Still Turning)*
- **Ornaments below `min_nom` vanish from the engraved score.** Audible,
  invisible. Backlog item 7.

## How to tell whether it is any good

Ask what a listener would be able to say about it afterwards. If the answer is
only "it was pretty" or "it got loud", the piece has a texture and not a shape.
Then check three things you can actually measure:

1. **The arc**, from the render, per section. Can you describe it in one
   sentence? Does the sentence match `docs/03`?
2. **The claim.** Does the piece have a thesis, and does the build check it?
3. **The ledger.** Write `docs/04` honestly, including what you are least
   sure about. Every piece here has real weaknesses; the ones that name them
   are the ones a future pass can improve.
