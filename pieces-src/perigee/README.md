# Perigee

A nuevo tango for a falling satellite — Piazzolla quintet (violin,
bandoneón, piano, guitar, double bass, plus golpe knocks). One continuous
movement, ~5:05, A minor, 4/4 throughout. The first piece built on the
shared [`lib/`](../../lib/) toolkit.

*A satellite in its last weeks is not falling the way a stone falls. Drag
does not slow it down — losing altitude means gaining speed, every orbit
shorter, every low pass hotter, the most brilliant flying of the machine's
life happening in its final days. The closer you fall, the faster you
dance. That is a tango.*

The orbit is the form: three revolutions of apogee and perigee, run by a
decay engine — apogees shrink 58 → 33 → 18 seconds while perigees grow
32 → 36 → 40 seconds at ♩ = 120 → 132 → 144. The revolutions climb by
minor thirds (A minor → C minor → E♭ minor — the orbits spell a diminished
arpeggio), then everything is dragged up a semitone onto E, the dominant of
home, where re-entry burns without resolving. The cut comes mid-gesture.
The coda has no double bass: no floor.

## Listen

```sh
open output/perigee.mid                  # the playable score (GM MIDI)
```

Rendered audio lives in the listening-room gallery (`symphony/web`,
`#/perigee`) with piano-roll playback, section narration, and the theme's
opening rise ("the beacon call") as a transforming emblem.

## The shape

| Time | Section |
|---|---|
| 0:00 | **Telemetry** — high piano ping on E6, a beacon still healthy; golpe ticks |
| 0:15 | **Apogee — the whole Earth at once** — the theme complete, bandoneón cantando over guitar arpeggios; violin joins phrase B |
| 1:13 | **First perigee — gravity says hello** — marcato in four, the first arrastre, the theme recast rítmico |
| 1:45 | **Apogee, but shorter** — violin takes phrase A an octave up in C minor; the marcato invades two bars early |
| 2:18 | **Second perigee — longer, faster, lower** — the 3‑3‑2 engine; the theme halved to a 4-bar cell, mordents arriving; stop-time síncopa break |
| 2:54 | **The last apogee** — bandoneón alone in E♭ minor, two bars of theme; it stalls; the bass creeps in beneath |
| 3:12 | **Third perigee — the heat** — la yumba, the theme's essence sequenced up the diminished ratchet, látigo, stretto, chromatic climb |
| 3:52 | **Re-entry** — toccata on E7♭9: the theme is only rhythm now, hammered on octave E's; violin tremolo burns the ♭9; a four-bar rocket climb |
| 4:17 | **Loss of signal** — the climb stops mid-bar. Silence |
| 4:21 | **After — a trail of light** — no bass; the ping returns and slows; phrase A intact and weightless; the quietest chan‑chan ever played |

The tonal insight is the cruel one: E — the note re-entry burns on — was
the dominant of A minor all along. The ground was the tonic.

## Files

- [output/perigee.mid](output/perigee.mid) — GM MIDI, the quintet on 6 tracks
- [output/marks.json](output/marks.json) — section/cue offsets in seconds, for the web manifest
- [src/compose.py](src/compose.py) — the score: nine sections as functions over one `lib.Piece`
- [src/band.py](src/band.py) — the quintet as a `lib` `Ensemble` (rosters are data)
- [src/tango.py](src/tango.py) — the idiom vocabulary: marcato/síncopa/3‑3‑2/yumba, arrastre, bellows (`sing`), mordent, látigo, golpe
- [src/themes.py](src/themes.py) — "the beacon call" and its diminutions (cantando → rítmico → halved cell → essence → rhythm only)
- [docs/](docs/) — inspiration, idiom study, blueprint, self-assessment

## Rebuild from source

Uses the shared venv at the repo root (see the top-level README).

```sh
cd pieces-src/perigee
../../.venv/bin/python src/compose.py    # → output/perigee.mid + marks.json + roll.png
                                         #   (range report + MIDI report built in;
                                         #    drop a perigee.wav in output/ to get
                                         #    the measured-RMS overlay on the roll)
```

Builds are deterministic (seed 1957 — Sputnik's year).
To repackage for the web player, run `tools/midi_to_piece.py` from the repo
root per [PIECES.md](../../PIECES.md); audio renders via fluidsynth +
GeneralUser GS (see [web/README.md](../../web/README.md)).
