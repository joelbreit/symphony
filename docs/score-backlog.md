# Score view — backlog

Written 2026-07-29, after all six non-midiutil pieces got engraved scores wired
into the web player. This is the work I'd still like to do, ordered by what
buys the most per hour. Nothing here is required — the scores are correct and
in sync today; these are fidelity, cost, and usability improvements.

Effort labels are rough: **S** = an afternoon, **M** = a day, **L** = more.

## Done since

**Scores are now automatic for new pieces** (2026-07-29). Key regions are
first-class on the Piece (`piece.key(beat, 'a')`, next to tempo and meter),
grand staves are roster data (`grand=True`), and `notation.export(piece,
slug)` infers staff order, keys, and grand staves from the piece itself,
writes the MusicXML into the web package, registers it in `piece.json`, and
gates on sync drift. Perigee's export script went from 48 lines to one call.

Also landed: `notation.check_sync()` — a headless Verovio drift check that
all five exports now run (worst across the repo: 1 ms) — the voice-0
renumbering guard moved into `lib/notation.py` so no future piece rediscovers
it, pinned part ids so re-exports diff cleanly, notation coverage in
`lib/tests.py` (items 4 below), and `tools/export_scores.py` (item 5).
`midi_to_piece.py` now carries the `score` field across a `--force` rewrite;
the non-force path always preserved it, so the earlier note that it "drops"
the field was only true with `--force`.

**Beat groups are beamed solid** (2026-09-06). music21 broke the *secondary*
beams of a group at the eighth-note subdivision: four sixteenths in one beat
came out with the primary beam running the whole beat and the 16th beam
stopping and restarting halfway, which engraves — and reads — as two pairs of
two. `lib/notation._join_secondary_beams` now makes every deeper beam
continuous inside a primary group, wherever both neighbours actually carry
that level; a genuine eighth in the middle of sixteenths still breaks it,
because there the break is real. Groups longer than one beat are left alone:
a beam spanning two beats *should* break its secondary at the beat, and
music21 gets that one right. `finish()` in `notation_m21` calls the same
function, so the frozen three are fixed too. Verified structurally across all
eleven score files: 0 remaining cases of a secondary beam stopping between
two adjacent short notes.

**The three music21 exporters are consolidated** into `lib/notation_m21.py`
(the recording Orchestra subclass, chord folding, staff frame, rest/voice
finishing, orchestral assembly, manifest patch, sync gate). Piece-local
export code dropped from 909 lines to 589, and the triplicated logic —
including the voice-0 guard — now lives in one place. Verified by content
diff: the riot's and the box's scores came out byte-identical, and The
Window's kept every one of its notes while shedding redundant rest-only
voices (mvt4: 3741 rests → 2089, file 1.81 → 1.40 MB). The frozen
generators were not touched.

**The score now fits itself to the pane** (2026-07-29). Verovio lays a system
out to `pageWidth`, and a system's *height* is fixed by its staff count — so
what fits on screen is decided almost entirely by the page width we ask for.
ScoreView renders one page as a probe, measures the system, and solves for
the page width at which a whole system (every instrument, top to bottom)
lands inside the visible height. It only widens past a comfortable reading
size when a system actually needs it, so a two-stave rag still stacks three
systems at full size while a sixteen-stave orchestral system compresses to
fit. Plus `spacingStaff: 7` (a fifth off every system's height on 16 staves),
tighter page margins, a fit/zoom control (50 %–280 %), re-fit on window
resize, and an autoscroll anchor that parks a pane-filling system at the top.
The Window's mvt1 went from 41 pages to 11, and all 16 staves are legible at
once even in a 620 px-tall window.

Still open below: items 2, 6–11, 13–18 (12 is easier now — far fewer pages).

## Do these first

**1. Consolidate the three music21 export scripts** — M — *done*
(`lib/notation_m21.py`)

**2. Dynamics on the page** — M — *done* (2026-09-06)

Every score in the collection now prints dynamics and hairpins, read back out
of the velocities: `lib/notation._dynamic_plan` bands the per-bar median
velocity, smooths it over three bars, prints a mark where a band change holds,
and draws a hairpin where the median ramped monotonically far enough to be a
ramp rather than a step (capped at eight bars so it does not become an
underline). `lib/notation_m21` feeds the same reader — the recording
`Orchestra` now captures the platonic velocity alongside the platonic rhythm
(without touching the frozen RNG stream), and High Street Riot reads its
velocities straight off the chart dicts it was written from. Counts, and they
look like the pieces: The Window mvt1 198 marks / 155 hairpins, Perigee 79/34,
Cut Loose 60/29, Still Turning 28/11, The Punch Line 19/9. All eight exports
still gate at 0–1 ms drift.

One finding worth keeping, because it will bite the next person: **velocity is
a keystroke and a dynamic is a loudness**, and at the top of a keyboard those
are very different numbers. A composer pushing a thin A7 sample so it speaks
at all is not writing `mf`. `_effective_vel` takes one band off the top
octave; below that it does nothing, because low notes carry on their own.

**3. Click a note to seek** — S/M

`renderToTimemap()` already gives qstamp→ms; reversing it gives id→ms. The
player has `seekGlobal`; `ScoreView` currently only receives `getTime`. Pass a
seek callback and make the engraved score a navigation surface, not just a
readout. Cheap, and it changes how the view feels.

**4. Notation self-tests in `lib/tests.py`** — S — *done*

**5. One command to regenerate every score, with a drift gate** — S — *done*
(`tools/export_scores.py`)

## Notation fidelity

**6. Tremolo slashes instead of written-out repetitions** — M

`trem()` writes literal 32nds because that's what MIDI needs, and the score
faithfully engraves the literal 32nds — dense black clouds where a player
expects a stemmed note with three slashes. Needs a marker on the note that
survives into the symbolic layer, then music21's `TremoloSpanner`. Most
visible in The Window and The Box Is Full.

**7. Grace notes for the dropped ornaments** — M/L

`min_nom` silently deletes mordents, latigos, and smears — they're audible but
invisible. Re-rendering them as grace-note glyphs attached to the following
note would close the last real "the page doesn't match the audio" gap. Perigee
has the most of these, so it's the piece to prototype on.

**8. Percussion staves** — M

`to_score()` skips percussion outright (`if spec.percussion: continue`), so
High Street Riot's drum kit and The Box Is Full's percussion are simply absent.
Needs a percussion clef plus a GM-note→staff-position/notehead map. Worth it
for Riot especially, where the kit is a lead voice.

**9. Articulations from gate and accent** — S/M

Staccato from a short gate ratio, accents from velocity spikes against the
local plateau. Low risk, and it makes the rhythmic pieces read correctly.
Slurs from sustained/overlapping gates are the same idea but noisier — try it
behind a flag and look before shipping.

**10. Chase the unclosed ties** — S

About five notes in The Window and five in The Box Is Full (m.156, m.175)
render with an open tie. It's a Verovio import quirk on tied chord members
carrying accidentals; find the minimal repro and either fix the export or file
it upstream.

**11. Transposed-score option** — S/M

Everything is concert pitch, which is right for a study score. A
`transposed=True` mode would make the output usable as actual parts.

## Web player

**12. Lazy page rendering** — M

The big scores still render every page up front when the score opens. The
auto-fit cut the page counts a long way (The Window's mvt1: 41 → 11), so this
hurts less than it did, but rendering the current page plus its neighbours
and filling the rest in idle time is still the fix. Note the fit probe adds
one extra layout pass, which lazy rendering would also help pay for.

**13. Remember the score/roll choice, and deep-link it** — S

The toggle resets on every movement change. Persist it, and support
`?view=score` so a score link can be shared directly.

**14. Measure numbers and section marks in the margin** — S/M

Section labels currently sit as text expressions that occasionally collide with
the staves at bottom-left. Put them in a proper margin gutter with measure
numbers, and let the roll's section markers jump the score view too.

**15. Download the MusicXML / print the score** — S

The scores are real artifacts now. A download link and a print stylesheet cost
almost nothing and make them useful outside the player.

**16. Mobile layout** — S/M

Untested on a narrow viewport. Needs a smaller `pageWidth` with a larger
`scale` so a phone shows a readable system or two rather than a shrunken page.

**17. Help the eye on 16-stave scores** — M

The Window's full-orchestra pages are hard to follow even with the note
highlighting. Options worth trying: dim staves that are resting, or a soft band
behind the sounding system. Design work as much as code — prototype before
committing.

## Coverage

**18. The two midiutil pieces** — L

`the-unfinished-spire` and `royal-street-rattler` have no symbolic layer, and
transcribing from humanized MIDI is the low-quality path. The honest route is
to have their generators emit a parallel symbolic record the way `lib.Piece`
does — real work, and it means touching two frozen generators, so only if we
decide a complete set of scores matters.

## If I only got to three

With 1 done, the top of the list is **2 (dynamics)**, **3 (click-to-seek)**,
and **6 (tremolo slashes)** — the three a musician would notice within
seconds of opening any of these scores. Dynamics and tremolos now only have
to be written twice (once in `notation`, once in `notation_m21`) instead of
four times.
