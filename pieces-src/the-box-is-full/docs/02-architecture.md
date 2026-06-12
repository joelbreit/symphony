# Architecture — "The Box Is Full"

One continuous movement, ~6 minutes, shaped as a single game played start to
finish. 4/4 throughout (the grid is relentless); intensity comes from tempo,
key ratchets, texture stacking, and hemiola — never from changing the grid.

## Source material (from tune.mxl, G minor)

- **A theme** (16 bars): the famous patter. Head cell **T = D5 A4 B♭4 C5**
  (5̂–2̂–3̂–4̂, four notes = four squares of a tetromino). Phrases: A1 (4),
  A1' (4, closes on G), A2 (C minor/E♭ excursion, 4), A2' (4).
- **B theme** (8 bars of half notes): descending-thirds chorale
  D–B♭ | C–A | B♭–G | F♯–A | D–B♭ | C–A | B♭–D–G | F♯. Ends on a HALF
  CADENCE (F♯ over D7) — the loop point. In Tetris menus this slot is
  literally "Music B": here it is the night in the rye field.
- Harmony A: D7 Gm | D7 Gm | Cm B♭ | D7 Gm. Harmony B: Gm⇄D7 …B♭ D7.

## The sections ("levels")

| § | what happens | bars | tempo ♩ | key | target |
|---|---|---|---|---|---|
| 0 | **insert cartridge** — woodblock timer ticks; four-note cells fall and lock around the orchestra (pizz/winds); the square wave boots with phrase 1 alone | 16 | 92 | Gm | ~0:40 |
| 1 | **levels 1–2, the strut** — oom-pah bass (the tuba's ghost), theme low in vc+bsn then vln1+ob, cocky; light kit | 24 | 138 | Gm | ~0:42 |
| 2 | **levels 3–4, first sweat** — theme up top, driving 8ths, brass counters, backbeat; ends in a 4-voice stretto pile-up → **line clear**: harp gliss + crash + texture trapdoor | 24 | 152 | Gm | ~0:38 |
| 3 | **the rye field (music B)** — B theme as romance: solo horn → cello counter → violins; harp arpeggios; the square wave dreams along for one phrase (the ring). Darkens to D7 at the close | 20 | 72 | E♭→D7 | ~1:06 |
| 4 | **the climb: levels 5·6·7** — A theme variations, each level-up = timp hit + key ratchet up a whole step + tempo +8; background "stack" cluster grows a voice every 4 bars; stretto + hemiola at L7 | 32 | 144/152/160 | Gm→Am→Bm | ~0:50 |
| 5 | **TETRIS!** — four-line clear: quadruple gliss, then B theme blazing in brass over 16ths; A-head as bass riff. Triumph is short | 12 | 160 | D major | ~0:18 |
| 6 | **the bottom drops** — D major curdles to D7♭9; chromatic bass starts rising; D7 is V of Gm: the triumph was structurally a trapdoor | 4 | 160→ | D7 | ~0:06 |
| 7 | **level 9 — kill screen** — theme double-time in square+vln+fl; pounding bass rising a semitone every 2 bars; the stack cluster fills voice by voice; accel 176→188; ends **TOP OUT**: one tutti cluster-chord, cut to silence | 26 | 176→188 | Gm | ~0:40 |
| 8 | **score screen** — square wave alone: B theme slow (game-over jingle as elegy); strings join; solo cello takes the verse (the song outlives the player); final cadence is the source's own bar 16: F♯ over D7, unresolved. Woodblock: tick, tick — **press start** | ~16 | 64 | Gm→D7 | ~1:10 |

Total ≈ 6:10.

## The key insight (literally)

The triumphant TETRIS blaze is in **D major — the dominant of G minor**.
Victory and doom are the same chord. The piece's biggest moment is, by
construction, the trapdoor into its catastrophe — exactly the poem's shape
(the best market day ends on the road home), exactly the game's shape
(the higher the level, the nearer the end).

## Orchestration

Adapted roster from the symphony framework (celesta slot → square wave):
winds (fl, ob, cl, bsn), brass (4 hn, 3 tpt, tbn+tuba), timpani, harp,
**square-wave lead (GM 80, "the Console")**, strings (vln1, vln2, vla, vc, cb),
drum kit + orchestral percussion on ch 10 (kick, snare, hats, toms, wood-
blocks, tambourine, crashes, china, triangle).

Square wave usage is rationed to three appearances: boot, the ring, the
kill screen + score screen. It must feel like a ghost, not a band member.

## Recurring devices

- **Falling cells**: 4-note T-fragments (transposed/rotated = tetromino
  rotations) that enter high and "lock" with a low pizz + woodblock thunk.
- **The stack**: a sustained background cluster that adds one voice at a
  time as panic grows; at top-out it IS the final chord.
- **Line clear**: harp/wind gliss up + crash + sudden texture drop. Used
  twice small (§2, §4), once huge (§5, four at once).
- **Level-up ratchet**: timp+kick hit, key +2 semitones, tempo +8.
- **The tick**: solo woodblock quarter pulse — opens the piece, closes it.

## Emblem

"the tetromino" — state 1: the four-note cell D5 A4 B♭4 C5. State 2
(trigger at the score screen): the cell with F♯5 appended, accented — the
unresolved note the whole piece ends on.

## Build plan

- `compose/common.py` — adapted framework (custom roster, extended perc map)
- `compose/themes.py` — source tune encoded exactly + cells + B-theme E♭ set
- `compose/sections.py` — §0–§8 as functions `(orch, t0) -> t1`, each also
  logging `(label, offset)` section marks
- `compose/build.py` — assemble, tempo map, write MIDI, range-check, report,
  and emit `output/marks.json` (section/moment offsets → seconds) for the
  manifest
- Package via symphony `tools/midi_to_piece.py`, render via fluidsynth +
  GeneralUser GS (`/Users/joel/code/workbench/soundfonts/GeneralUser-GS.sf2`)
