# The study — passacaglia practice, and writing for one piano

Two bodies of craft this piece has to get right: the variation form, and the
instrument. Notes from working through both before writing bars.

## Part 1 — how a passacaglia avoids being a list

The form's failure mode is obvious and fatal: twenty-seven statements of the
same eight bars, each with a different texture, in a row. That is a list, not
a piece. What separates Bach's C minor Passacaglia or the Brahms Fourth
finale from a list is that the variations are **grouped into spans with their
own arcs**, and that several independent parameters move on *different*
schedules so the seams never all land in the same place.

### The parameters, and the rule for each

| parameter | schedule | why |
|---|---|---|
| **the ground** | never changes | the whole subject of the piece |
| **subdivision** | ratchets up, never down, until the collapse | the one irreversible clock; it is how the listener knows time is passing |
| **register** | expands outward from the middle | the cheapest and most reliable sense of growth on a piano |
| **dynamic** | two arcs, not one | a single 5-minute crescendo is a ramp, not a shape |
| **mode** | one change, three-quarters through | spend it once; it is the only card of its size |
| **texture density** | free — the local variable | this is what makes each statement itself |

The important one is that **subdivision and dynamic must not be locked to
each other**. If every increase in speed is also an increase in volume, the
piece has exactly one gesture and plays it repeatedly. So: the loudest minor
music arrives *before* the fastest music finishes ratcheting, and the quietest
statement in the second half (the hinge) comes immediately after the loudest.

### Grouping

Statements are grouped 5–3–5–3–1–6–4. Nothing is left running for more than
about a minute without the frame changing underneath it. Each group gets its
own opening gesture on its first bar so the listener hears a door open, not
another lap.

### The three structural decisions

1. **The ground is its own retrograde.** D–C–B♭–A ‖ B♭–C–D–A: bars 1–3 fall,
   bars 5–7 rise through the same notes, and both halves land on A. It turns
   and comes back — which is what the object does. It also means the second
   half of every statement feels like a *lift* rather than a repeat, and that
   lift is doing free work in all twenty-seven.
2. **The mode change costs one note.** The ground's roots harmonize
   i–♭VII–♭VI–V ‖ ♭VI–♭VII–i–V in D minor and I–♭VII–♭VI–V ‖ ♭VI–♭VII–I–V in
   D major. Same roots, same bass, same voice-leading. The only obligatory
   change in the whole texture is F♮ → F♯. In major that progression is the
   modern anthem cadence (♭VI and ♭VII borrowed into a major key); in minor
   it is the Andalusian lament. One accidental is the distance between them,
   which is a fact about music theory that happens to be exactly the point of
   this piece.
3. **The ground becomes the melody at the climax.** Statement 23 abandons the
   tune and hammers the eight ground notes themselves in octaves in both
   hands, in the open. Everything the listener stopped hearing forty
   variations ago turns out to be the thing worth hearing. Structurally this
   is also the only honest way to make a passacaglia's climax feel like an
   arrival instead of just the loudest lap.

### What I deliberately did not use

- **No fugue.** Bach ends his passacaglia with one. It is the correct
  historical answer and the wrong one here: a fugue is an argument, and this
  piece's climax is a recognition.
- **No modulation.** The ground can't move, so the piece stays on D for five
  and a half minutes. Everything usually done with key is done with mode,
  register, and density instead. (This is a real cost. See `04`.)
- **No tempo change.** Argued in `docs/01`. It is the constraint the piece is
  most likely to be criticised for and the one I am least willing to trade.

## Part 2 — writing for the piano, when a synthesiser will play it

### The register map (what actually sounds good, not what fits)

| span | use |
|---|---|
| A0–B1 | single notes and bare octaves only; any third down here is mud |
| C2–B2 | octaves, fifths, open tenths; the ground's home |
| C3–B3 | the danger zone — full triads here sound thick and cheap |
| C4–C6 | melody, thirds, sixths, close harmony; the singing register |
| C6–C8 | brilliance and bells; single notes and octaves |

The practical rule that survived every draft: **the interval between the two
lowest sounding notes should not be smaller than a fifth below C3, or a
third below C4.** Almost every "MIDI piano sounds like sludge" complaint is
that rule being broken.

### Pedal

Pedal is not decoration; on a passacaglia it is structure, because it is what
makes eight repeated bass notes ring into each other instead of sounding like
eight separate events. The scheme here: **pedal changes on the bar** (one per
harmony) for the entire piece, released a hair before the next downbeat so the
bass re-articulates cleanly. `piece.pedal(inst, t0, t1)` writes CC64; the
gap matters — no gap and the whole variation smears into one chord.

The two exceptions: the sixteenth-note statements pedal in half-bars (full-bar
pedal at that density is a wash), and the final chord holds one pedal for
sixteen bars and lets it decay under the pulse.

### The thing MIDI piano gets wrong, and the fix

A synthesised piano has no sympathetic resonance, no una corda, no
half-pedal, and no key release noise, so it sounds flat in exactly the places
a real piano sounds alive. Three cheap corrections that measurably help:

1. **Voice the melody.** Real pianists play the tune 10–20 velocity units
   above the accompaniment in the same hand. Doing this explicitly is the
   single biggest improvement available; without it, chordal writing turns to
   porridge.
2. **Roll the big chords.** A ten-note fff chord struck perfectly
   simultaneously sounds synthetic, because no human plays one that way.
   `figures.strum(spread=0.012–0.03)` fixes it, and wide chords should be
   rolled bottom-to-top with more spread than narrow ones.
3. **Do not write CC11 hairpins.** A piano note begins decaying the instant
   it is struck; a crescendo on a held note is physically impossible. GM
   synths will render it happily and it will sound like an organ. Velocity is
   the dynamic. (This is why `Piece.hairpin` is unused in this piece — it is
   right for the bandoneón in *Perigee* and wrong here.)

### Playability, treated as a gate rather than a claim

*The Punch Line* broke playability on purpose. This piece claims to be
playable, and a claim like that has to be checked, so the build runs a hand
audit: notes are grouped into onsets, split into two hands, and each hand is
checked for span (≤ a 10th, with 9ths flagged), simultaneous note count
(≤ 5), and the jump it must make from its previous position in the time
available. That check now lives in `lib/keyboard.py` so the next keyboard
piece gets it for free.

It found 272 real problems in the first draft and every one of them changed
the music. The five biggest:

1. **The pulse could not be where I put it** (see `docs/01`) — the largest
   single rewrite in the piece, and an improvement.
2. **The summits were written as one roll across the keyboard**, five or six
   notes from A♯0 to A6. Split into one roll per hand, which is how a pianist
   would have played it anyway.
3. **Statement 14's downbeat was a chord plus a leap** — a mid-register chord
   and then a high A nineteen semitones above it, 22 ms later. Rewritten as a
   ladder of chord tones that arrives *on* the A, which sounds better: a bell
   on every downbeat instead of a chord with a spike.
4. **Two seams were unplayable at speed.** Going from the sixteenth-note
   ladder straight into the storm asks the right hand to jump two octaves in
   45 ms. Fixed by leaving the last beat of each approach empty — which is a
   breath before the big statement, which is what the music wanted.
5. **The churning figures climbed away from the next bar's bass.** A
   six-note run up an open chord ends an octave and a half above where the
   left hand has to be a moment later. Capping the pool at five notes makes
   `arc` turn around, so the figure rocks instead of climbing — better
   writing and a shorter jump.

The audit also found two flaws in *itself*, which is worth recording: it was
treating rolled chords as impossible grabs (a roll is a sweep — the hand
travels through it, so span is the wrong measure), and it had no floor under
the reach rule, so it flagged an octave shift in 22 ms as too fast. Both are
fixed in `lib/keyboard.py`. Final state: 1,196 onsets, **zero errors, zero
stretches, widest hand exactly an octave**.
