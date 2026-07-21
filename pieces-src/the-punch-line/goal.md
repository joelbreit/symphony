# Goal

Compose **"The Punch Line"** — a classic piano rag for solo piano: stride
left hand, syncopated right hand. Commissioned by Joel; the brief is *fun,
catchy, and skillful*, with every other decision left to the composer.

The seed image is already found (see `docs/01-inspiration.md`): a rag and a
joke are the same machine — a strict grid that builds expectation, and an
accent that lands where you don't expect it. Comic timing *is* syncopation.
The physical setting is the player-piano roll: punched paper, the first
music you could store as holes — both meanings of "punch" in one title.
Deepen that image before writing a note; don't trade it for something easier.

Explore the real idioms first. Ragtime has a strict written language — the
oom-pah left hand striding bass-to-chord, untied and tied syncopations, the
secondary rag (3+3+2 against the march), stop-time, the multi-strain march
form with the trio in the subdominant — and one law, printed on Joplin's own
scores: never play it fast. Study enough to honor all of it; the piece
should read like a rag written by someone who has played rags all their
life, not a modern piece wearing arm garters as a costume.

Then plan the scaffolding: the form is a joke's anatomy. Decide what each
strain does (setup, topper, callback, aside, punch line), where the
stop-time pause goes — the silence before the landing — and exactly how the
doctored-roll finale earns its extra hands. Key moments and effects on
paper before any notes.

Then build it — strains, progressions, the full two-hand texture — and
self-assess against the real repertoire: does the left hand walk or plod?
Would the tunes survive being whistled? Does the punch line actually land?

## Tooling

- Build on `lib/` (see `lib/README.md`): `solo_piano()` is already a preset
  — one instrument is still an `Ensemble`. Use the DSL, chord charts,
  `groove.Humanize`, pedal (CC64), and the assessment suite.
- Ragtime wants piece-local helpers first — a stride-bass generator over
  chord charts is the obvious one. Promote to `lib/` only what proves
  general, with a test in `lib/tests.py` for anything promoted.
- Keep the working record in `docs/`, generate MIDI into `output/`, package
  via `tools/midi_to_piece.py`, render per `web/README.md`.

## Constraints

1. Three to five minutes; classic multi-strain rag form with repeats.
2. Solo piano only. Two human hands throughout — with one licensed
   exception: the final strain may be *doctored* the way QRS doctored
   their rolls, sprouting notes no ten fingers could reach. That moment is
   the punch line; it must be earned, not leaned on.
3. Playability discipline everywhere else: spans within a tenth, real
   alternation between hands, and Joplin's tempo law obeyed.
4. The deliverable must be playable and *verified* — listen to the render,
   measure the arc, check the package in the web player (where the
   audience literally watches the roll go by).
