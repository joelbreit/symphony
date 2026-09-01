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

**The three music21 exporters are consolidated** into `lib/notation_m21.py`
(the recording Orchestra subclass, chord folding, staff frame, rest/voice
finishing, orchestral assembly, manifest patch, sync gate). Piece-local
export code dropped from 909 lines to 589, and the triplicated logic —
including the voice-0 guard — now lives in one place. Verified by content
diff: the riot's and the box's scores came out byte-identical, and The
Window's kept every one of its notes while shedding redundant rest-only
voices (mvt4: 3741 rests → 2089, file 1.81 → 1.40 MB). The frozen
generators were not touched.

Still open below: items 2, 6–18.

## Do these first

**1. Consolidate the three music21 export scripts** — M — *done*
(`lib/notation_m21.py`)

**2. Dynamics on the page** — M

The scores currently have no `p`, `f`, or hairpins at all. Velocity is the
dynamic in this system, so the information exists: quantize each staff's
velocity into plateaus, emit the plateau as a dynamic mark, and emit a hairpin
where a plateau ramps. This is the single biggest visual gap between what we
render and what a real study score looks like — right now the page looks
uninflected while the audio is doing a lot.

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

The Box Is Full renders all 53 pages up front when the score opens (2.5 MB of
MusicXML). Render the current page plus its neighbours, fill the rest in idle
time. This is the main reason opening the score on the big pieces feels heavy.

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
