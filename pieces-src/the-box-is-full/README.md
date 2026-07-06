# The Box Is Full

Korobeiniki as folk tragedy — one full game of Tetris, boot to top-out, for
orchestra and square wave. One continuous movement, nine sections, ~6:11,
G minor, 4/4 throughout.

*In 1861 the song was about a peddler whose box fills with wares and who is
murdered on the road home; everyone remembers the happy verse. In 1989 the
same tune shipped on a grey cartridge with a game nobody beats. The peddler's
box and the player's well fill the same way — piece by piece — and the song
knows how both stories end.*

The source is [tune.mxl](tune.mxl), the Korobeiniki transcription in G minor
(`tune_extracted/` is its unzipped MusicXML). Two themes come from it: the
famous A-theme patter, whose four-note head cell **D5–A4–B♭4–C5** (four notes
= four squares of a tetromino) is the piece's DNA, and the half-note B theme —
the chorale hiding inside the chiptune — which ends on F♯ over D7, the half
cadence that loops forever. The piece ends there too: unresolved, a woodblock
ticking, the next piece already falling.

## Listen

```sh
open output/the-box-is-full.mid          # the playable score (GM MIDI)
```

Rendered audio lives in the listening-room gallery (`symphony/web`,
`#/the-box-is-full`) with piano-roll playback, section narration, and the
four-note cell as a transforming emblem.

## The band

Full orchestra with one substitution: the celesta slot becomes a
**square-wave lead (GM 80, "the Console")** — the Game Boy's actual voice.
It is rationed to three appearances (the boot, the turquoise ring, the kill
screen + score screen) so it stays a ghost, not a band member. Winds, brass,
timpani, harp, strings, and a drum kit + orchestral percussion on channel 10.

## The shape

One game, played start to finish. Intensity comes from tempo, key ratchets,
texture stacking, and hemiola — never from changing the grid.

| Time | Section |
|---|---|
| 0:00 | **Insert cartridge** — woodblock timer; four-note cells fall and lock; the square wave boots |
| 0:42 | **Level 1 — the peddler struts** — oom-pah bass, theme low and cocky |
| 1:23 | **Level 3 — first sweat** — theme up top, brass counters, stretto pile-up → line clear |
| 2:01 | **The rye field (music B)** — the chorale as romance; at 2:48 the square wave dreams along: the turquoise ring |
| 3:08 | **The climb — levels 5 · 6 · 7** — each level-up: timpani hit, key up a whole step, tempo +8 |
| 3:59 | **TETRIS! — four lines** — B theme blazing in brass, in D major. Triumph is short |
| 4:15 | **The bottom drops** — D major curdles to D7♭9; the triumph was structurally a trapdoor |
| 4:21 | **Level 9 — kill screen** — theme double-time, bass rising a semitone every 2 bars, the stack cluster filling voice by voice |
| 4:53 | **Top out** — one tutti cluster-chord, cut to silence |
| 5:00 | **Score screen** — square wave alone, then strings; at 5:30 solo cello takes the peddler's verse — the song outlives the player |
| 6:07 | **Press start** — F♯ over D7, unresolved; tick, tick |

The key insight is literal: the TETRIS blaze is in D major, the dominant of
G minor — victory and doom are the same chord.

## Files

- [output/the-box-is-full.mid](output/the-box-is-full.mid) — GM MIDI, full orchestra + square wave
- [output/marks.json](output/marks.json) — section/cue offsets in seconds, for the web manifest
- [compose/box.py](compose/box.py) — the score generator: nine sections §0–§8 as functions `(orchestra, t0) -> t1`
- [compose/common.py](compose/common.py) — adapted music21 framework (note DSL, `Orchestra` with the custom roster, range guards, deterministic humanization, MIDI writer)
- [compose/themes.py](compose/themes.py) — the source tune encoded exactly, the four-note cells and their rotations, the B-theme transpositions
- [tune.mxl](tune.mxl) / [tune_extracted/](tune_extracted/) — the Korobeiniki source transcription
- [docs/](docs/) — inspiration, architecture, self-assessment

## Rebuild from source

Uses the shared venv at the repo root (see the top-level README).

```sh
cd pieces-src/the-box-is-full
../../.venv/bin/python compose/box.py    # → output/the-box-is-full.mid + marks.json
                                         #   (range checks + MIDI report built in)
```

To repackage for the web player, run `tools/midi_to_piece.py` from the repo
root per [PIECES.md](../../PIECES.md); audio renders via fluidsynth +
GeneralUser GS (see [web/README.md](../../web/README.md)).
