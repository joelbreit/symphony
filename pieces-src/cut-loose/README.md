# Cut Loose — a second line for a cornet player

A Dixieland piece in the shape of a New Orleans jazz funeral, for a
marching brass band: cornet, clarinet, alto sax, trombone, sousaphone,
snare drum, bass drum. One continuous piece, ~5:08, 176 bars. E♭ major
for the hymn and the strut, A♭ for the ramble, home to E♭. Third piece
on the shared [`lib/`](../../lib/) toolkit.

*The band is burying its own cornet player. On the way out the front line
plays the hymn with his chair empty. At the grave the body is cut loose,
the grand marshal blows the whistle, the snares come on — and the same
hymn comes home as a strut at three times the tempo, with the cornet on
top of it as if he had only gone on ahead.*

**One tune, two lives.** The hymn's notes never change between the dirge
and the strut; only where the long notes land. The cornet is silent
until bar 45.

## Listen

```sh
open output/cut_loose.mid                # the playable score (GM MIDI, 7 tracks)
```

Rendered audio lives in the listening-room gallery (`symphony/web`,
`#/cut-loose`) with piano-roll playback, section narration, the engraved
score, and the hymn's call as a transforming emblem.

## The band

Cornet (the one being buried — silent until the second line) ·
Clarinet (the one who cries) · Alto sax (the steady friend) ·
Trombone (the old-timer, tailgate) · Sousaphone (the ground) ·
Snare drum (the grand marshal's clock) · Bass drum & cymbal (the heartbeat)

No banjo, no piano: this band walks. The drums are two people, not a kit.

## The shape

| Time | Section |
|---|---|
| 0:00 | **The cadence** — bass drum on 1 and 3, muffled snare rolls; the sousaphone joins |
| 0:15 | **The hymn** (E♭) — alto sax plainly, trombone tenor line with smears; clarinet descant on the second half; the tear (A♭ → A♭m) at 0:51 |
| 1:13 | **The cry** — the last half again, clarinet an octave up, widest vibrato in the piece |
| 1:42 | **Amen** — IV → I held, dying, rit. Silence. |
| 2:00 | **The whistle** — one long, two short |
| 2:03 | **Snares on** → 2:08 the sousaphone riff (the call in the bass) → 2:13 riffing in |
| 2:16 | **His first note** — one hit, silence, the cornet alone plays the hymn's fall |
| 2:18 | **The strut** — the hymn cut loose; collective improvisation |
| 2:38 | **Clarinet up top** — the strut an octave up while the cornet plays the hymn slow underneath |
| 2:58 | Around the corner to A♭ — E♭7 Charleston hits, two bars of snare drum |
| 3:03 | **The ramble** — new strain, stop-time, its own tear (D♭ → D♭m) |
| 3:24 | Trombone takes it → 3:44 Clarinet takes it |
| 4:04 | **The umbrellas go up** — shout chorus: the call in block harmony, drummers answering; tempo pushes to 196 |
| 4:24 | Turn for home — B♭7 hits, the cornet's rip and run |
| 4:29 | **Home** — the strut at full boil, sousaphone walking four |
| 4:48 | **The tag** — the head in octaves, I–VI7–II7–V7 with snare fills, one bar of drums, the last chord |
| 4:57 | **Benediction** — the cornet alone at the walking tempo: the call, the fall, the amen; the band answers once |

## Files

- [output/cut_loose.mid](output/cut_loose.mid) — GM MIDI, the band on 7 tracks
- [output/marks.json](output/marks.json) — section/cue offsets in seconds, for the web manifest
- [output/roll.png](output/roll.png) — pianoroll, designed arc, measured RMS from the render
- [src/compose.py](src/compose.py) — the score: nineteen sections as functions over one `lib.Piece`
- [src/band.py](src/band.py) — the brass band as a `lib` `Ensemble` (two drummers as two instruments)
- [src/street.py](src/street.py) — the idioms: dirge cadence, street beat, two-beat sousaphone, riffs, obbligato (four run types), tailgate, block harmony, the whistle, the vibrato
- [src/themes.py](src/themes.py) — the hymn, the strut, the ramble, the shout, the choruses; all bar-guarded
- [export_score.py](export_score.py) — engraved score into the web package, sync-verified
- [docs/](docs/) — inspiration, idiom study, blueprint, self-assessment

## Rebuild from source

```sh
cd pieces-src/cut-loose
../../.venv/bin/python src/compose.py        # MIDI + marks.json + roll.png into output/
fluidsynth -ni -g 0.5 -r 44100 -F output/cut_loose.wav \
    ../../../soundfonts/GeneralUser-GS.sf2 output/cut_loose.mid
afconvert -f m4af -d aac -b 160000 output/cut_loose.wav \
    ../../web/public/pieces/cut-loose/audio/mvt1.m4a
cd ../.. && .venv/bin/python tools/midi_to_piece.py --id cut-loose \
    --title "Cut Loose" --composer "Claude" pieces-src/cut-loose/output/cut_loose.mid
cd pieces-src/cut-loose && ../../.venv/bin/python export_score.py
```

Composed by Claude (Fable 5.1), September 2026.
