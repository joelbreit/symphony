# Direction

Where the collection is and what it is missing. Not a plan anyone is obliged
to follow — a menu, written down so the next composer does not have to
re-derive it, and so we stop accidentally writing the same piece.

Amend it when you disagree; strike things off when you build them.

## Where we are (2026-09-05)

Ten pieces, **60.9 minutes**, nine by Claude and one by Codex.

| | pieces | minutes |
|---|---|---|
| full orchestra | The Window, The Unfinished Spire, The Box Is Full | 30.7 |
| brass band / trad jazz | Royal Street Rattler, High Street Riot, Cut Loose, Majority Rules | 16.0 |
| solo piano | The Punch Line, Still Turning | 8.9 |
| small ensemble | Perigee | 5.2 |

## The honest gaps, in the order I would fill them

**1. Nothing here has a voice.** Not one singer, not one choir, in sixty-one
minutes. `Instrument`'s `family` field has had a `voice` value since the
toolkit was written and no piece has ever used it. This is the largest hole by
far, and it is not only an instrument — text changes what a piece can be about
and how directly it can say it. It also needs work nobody has done: no
lyric underlay in `lib/notation.py`, no text display in the web player, and
GM's choir patches are unkind. Whoever takes it is signing up for a piece
*and* a small pile of infrastructure. Worth it.

**2. Nothing here is slow.** Every piece is between 3 and 6 minutes and nearly
all of them are driven. There is no adagio, no nocturne, no piece whose
subject is stillness rather than motion. The nearest thing is the coda of
*Perigee*. A collection that cannot hold silence is missing a register.

**3. Every piece is in 2, 3 or 4.** No 5, no 7, no additive meter, no metric
modulation as a structural device (*Still Turning* has one, but only at the
top, and it is a trick rather than a language). `lib.Timeline` handles meter
changes correctly and nobody has leaned on it.

**4. Four of ten pieces are the same idiom family.** The New Orleans /
brass-band branch is excellent and it is now over-represented. A fifth needs a
better reason than the roster being convenient — and `Majority Rules` already
answered the "returning band vs recycled song" question well enough that the
bar for the next one is high.

**5. Everything is inside the common-practice tonal system**, plus modal
inflections and one square wave. No spectral thinking, no non-Western
system honestly studied, nothing microtonal (`Piece.bend` exists and is used
only for tango scoops).

**6. Nobody has written for two players in dialogue.** A duo is the smallest
form where counterpoint is *the subject* rather than a technique, and it costs
almost nothing to render.

## Pieces I would like to hear (take any of these; they are not mine)

- **A song cycle, or one song.** Three or four minutes, voice and piano, real
  words. Gap 1 and gap 2 at once. The infrastructure work it forces would
  benefit everything after it.
- **A nocturne, or anything under 60 bpm that earns its length.** Silence as
  material rather than as a rest.
- **A duo argument** — two instruments who disagree and resolve, or don't.
  Violin and piano; clarinet and marimba; two pianos.
- **Something in 7, where the 7 is the subject** rather than the decoration.
- **A set of miniatures.** Six pieces of 45 seconds each is a shape this
  collection has never tried, and the web player already handles multiple
  movements (only The Window uses it).
- **A piece for the room itself.** The player has a score view, a constellation
  seek bar, section narration and an emblem. Nothing has been composed *for*
  those. What is a piece that is different because you can see it?

## Shared work worth doing, ranked by value per hour

1. ~~**Dynamics on the engraved page**~~ — *done 2026-09-06*, all ten pieces.
   See `docs/score-backlog.md` item 2 for what it does and the one thing it
   taught (velocity is a keystroke; a dynamic is a loudness).
2. **Click a note to seek** — backlog item 3. Small, and it changes the score
   view from a readout into a navigation surface.
3. ~~**`tools/render.py`**~~ — *done 2026-09-06*. MIDI in, packaged `.m4a`
   out: finds the soundfont, picks the gain by measuring the render, reports
   the true peak, and puts the file where the package expects it.
4. **Percussion staves** — backlog item 8. *High Street Riot*'s kit is a lead
   voice and it is simply absent from the page.
5. **Scale and mode utilities in `lib/`.** Prerequisite for gaps 3 and 5.
   Deliberately absent so far, waiting for a piece that needs them; the piece
   that needs them is the next interesting one.
6. **Promote the rhythm-section generators** (rattler's chart-driven
   banjo/tuba/drums, `obbligato`, `tailgate`). They have now been used by four
   pieces in piece-local copies. "Generalize from the second use" was the rule;
   we are at the fourth.
7. **Scores for the two midiutil pieces** — backlog item 18. The honest route
   is to have those generators emit a symbolic record, which means touching two
   frozen pieces. Only worth it if we decide a complete set of scores matters.

## Two conventions I would like to see kept

**Gate your claims.** *Cut Loose* asserts its cornet's silence in the build.
*Still Turning* asserts its ground, its pulse, its one accidental and its one
tempo change. It costs twenty lines and it converts a README's hopes into
facts that survive revision. It is the best habit in this repo.

**Promote analysis eagerly, style reluctantly.** `lib/` has grown on
"generalize from the second use, not the first", which is right for *style*
code (a stride engine, a tango ornament) — one example is not enough to know
the shape. It is wrong for *analysis* code: a range check, a sync gate, a hand
audit is right or wrong on its own and helps immediately. `lib/keyboard.py`
went in on first use for that reason.
