# Logbook

The shared record. Composers here work in different sessions, on different
branches, mostly not at the same time — this is how we hand off.

**Add an entry when you finish a piece, or when you change something shared
(`lib/`, `tools/`, `web/`).** Newest first. Keep it to the four headings and
be concrete; this is a handoff, not a diary.

```markdown
## YYYY-MM-DD — <what you did> — <composer>

**Built.** What exists now that didn't before.
**Changed for everyone.** Anything in lib/, tools/, web/ — and why.
**Learned.** One or two things worth another composer's time. Link the
  notebook entry if you added one.
**Left open.** What you would do next, or what you could not finish.
```

The log started on 2026-09-05 and does not reach back — the pieces before it
carry their own record in `pieces-src/<slug>/docs/`, which is the better read
anyway.

---

## 2026-09-06 — dynamics on every score; Still Turning's second pass — Claude (Opus 5)

**Built.** A revision pass on *Still Turning* driven by its own ledger. The
subdivision ladder (statements 9–13) was five statements of one left-hand
figure getting faster, which is the exact failure `docs/composers-notebook.md`
warns about; it is now five figures — sweep, broken octaves, sweep under thumb
chords, murky bass, both hands sweeping. The anthem's bare melody octaves are
filled with a chord tone (chosen to avoid a tritone against the tune), which
took the gap between the false summit and the real one from 2.1 dB to 3.0.
2,216 notes now; hand audit still 0 errors, widest hand still an octave.

**Changed for everyone.**

- **Dynamics and hairpins on every engraved score** — `docs/score-backlog.md`
  item 2, which was the top of `docs/direction.md`'s shared-work list. The
  per-bar median velocity is banded, smoothed over three bars, printed as a
  mark where a band change holds, and drawn as a hairpin where the median
  ramped far enough to be a ramp (capped at eight bars so it does not become
  an underline). `lib/notation` does it for the lib pieces;
  `lib/notation_m21`'s recording `Orchestra` now captures the platonic
  velocity alongside the platonic rhythm — without drawing from the frozen
  RNG, so no frozen MIDI moved — and High Street Riot reads its velocities
  off the chart dicts it was written from. All ten pieces have them; all
  eight exports still gate at 0–1 ms drift.
- One general finding, now in the notebook and `lib/README.md`: **velocity is
  a keystroke and a dynamic is a loudness**, and at the top of a keyboard
  those are not the same number.

**Learned.** Two entries went into `docs/composers-notebook.md`: the velocity
/ loudness distinction above, and a test for repeating forms — *describe each
statement in three words; if two match, one is not earning its place.* That
test is what condemned the ladder, and it is cheap to apply.

**Also fixed, after Joel spotted it on the page.** Four sixteenths in a beat
were engraving as two groups of two: music21 runs the primary beam across the
whole beat but breaks the *secondary* beam at the eighth, and the eye reads
the inner beam. `lib/notation._join_secondary_beams` now joins deeper beams
inside a primary group wherever both neighbours carry that level, and leaves
the break alone where it is real (an eighth among sixteenths) or correct (a
group spanning more than one beat). All eleven score files are clean.
Worth remembering as a class of bug: it was visible only on the page, and no
gate we had could have caught it — the sync gate is about *time*, and this was
about *reading*.

**Left open.**

- **Click a note to seek** (backlog item 3) is now the top of the shared list.
- **`tools/render.py`** — every piece README still repeats the fluidsynth and
  afconvert incantation by hand. I did it eight times today.
- Percussion staves (backlog item 8) — *High Street Riot* now has dynamics on
  a score that still has no drum kit on it, which is a slightly absurd state.
- `lib/keyboard.py` still does not model held notes as occupied fingers.

## 2026-09-05 — "Still Turning", a solo-piano passacaglia — Claude (Opus 5)

**Built.** `pieces-src/still-turning/` and `web/public/pieces/still-turning/`.
Solo piano, 5:32, 232 bars, 2,168 notes, D minor to D major. Twenty-seven
statements of an eight-note ground that is never altered, at one tempo taken
from the rotation period of PSR B1919+21 — one 3/4 bar = 1.3373 s = ♩134.5996.
Engraved score exported and synced to 1 ms. Second solo-piano piece in the
collection and deliberately the opposite of *The Punch Line* in every way: two
hands, one tempo, no tricks.

**Changed for everyone.**

- **`lib/keyboard.py`** (new) — a playability audit for keyboard writing:
  onsets are split into two hands, then checked for span, finger count, and
  reach in the seconds the tempo actually allows. `keyboard.report(piece)`.
  It found 272 real problems in this piece's first draft and every fix
  improved the music. It knows about rolled chords (a sweep, not a grab) and
  has a floor under the reach rule (a hand shifts an octave almost instantly).
  Its assumption is stated in the module docstring and matters: it audits
  notes being *struck*, on the assumption that anything still sounding is held
  by the pedal.
- **`Note.rigid`** (`lib/piece.py`, `lib/groove.py`) — material that opts out
  of swing, lean and timing jitter but keeps velocity jitter: a machine part
  inside a human performance. It still draws from the RNG, so marking
  something rigid does not reshuffle anybody else's humanization — which is
  why every existing piece rebuilds byte-identical.
- **`lib/notation.py`** — music21 writes `<per-minute>` and `<sound tempo>` as
  **whole** BPM. Invisible at ♩=120; at ♩=134.5996 it desynced the score by
  a second over five minutes, which is the score highlighting the wrong bar.
  `to_musicxml` now restores the exact tempi from the piece's own timeline.
  Every existing score re-exports identically (only the encoding date moves).
- **`tools/check_all.py`** (new) — lib self-tests, then rebuild every
  lib-built piece and fail if one byte of anybody's finished MIDI changed.
  Run it after touching `lib/`. I wanted this three times today before I
  wrote it.
- **`docs/`** — this logbook, `composers-notebook.md`, `listening-notes.md`,
  `direction.md`. See `docs/README.md`.

**Learned.** Two things went into the notebook that I would want another
composer to have before starting: *gate your own compositional rules in the
build* (four assertions at the bottom of `src/compose.py`, all of which caught
something real), and *measure the arc from the render rather than from
velocities* (nine velocity units bought one decibel; density moves RMS far
more than velocity does).

**Left open.**

- The subdivision ladder (statements 9–13) is the weakest span in the piece —
  five statements whose job is "denser than the last". It wants genuinely
  different figures, not faster ones. Detail in `docs/04-self-assessment.md`.
- **The score still has no dynamics on it** (`docs/score-backlog.md` item 2).
  It hurts this piece more than most, because the dynamic arc *is* the form.
  If someone wants a high-value shared-infrastructure task, that is the one.
- `lib/keyboard.py` does not model held notes as occupied fingers. Fine for
  pedalled writing, wrong for a sustained inner voice under moving fingers.
  Whoever writes the next contrapuntal keyboard piece should fix it there.
- I did not touch the frozen pieces or the two midiutil ones. Still no scores
  for `the-unfinished-spire` or `royal-street-rattler` (backlog item 18).
