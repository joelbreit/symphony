# Majority Rules — a town meeting in B♭

A 164-bar civic rondo for the seven-player *Cut Loose* marching band:
cornet, clarinet, alto sax, trombone, sousaphone, snare drum, and bass drum
with mounted cymbal. One continuous movement, about 3:44 of written music.

*A brass band mistakes a town meeting for a gig. Every horn proposes a tune,
every drummer objects, and the whole block votes for B♭ by playing at once.*

## The joke

The cornet chairs the meeting and proposes **the motion**, a square sixteen-bar
strain in B♭. The alto offers **the amendment**, a smoother E♭ tune. The
clarinet heckles, the trombone delivers the honorable opposition, and the
sousaphone keeps the minutes by hauling every detour home. Motion and
amendment remain separate until the unanimous vote, where the motion becomes
three-part block harmony and the amendment answers from the trombone below.

This is neither *High Street Riot's* endless-vamp lifecycle nor *Cut Loose's*
dirge-to-second-line transformation. Its form is interruption: motion,
amendment, point of order, opposition, rebuttal, filibuster, roll call, vote,
three rejected endings, and one elected final chord.

## The meeting

| Time | Section |
|---|---|
| 0:00 | **Call to order** — snare press roll, sousaphone count, three-hit gavel |
| 0:05 | **The motion** — cornet states the B♭ strain |
| 0:27 | **The amendment** — alto sax in E♭; cornet objects in the breaths |
| 0:49 | **The motion, amended** — clarinet on the motion, alto beneath it |
| 1:11 | **Point of order** — four two-bar objections, one per horn |
| 1:22 | **Honorable opposition** — trombone owns the amendment |
| 1:44 | **Rebuttal** — cornet and trombone trade claims |
| 1:55 | **The motion carries** — collective chorus in B♭ |
| 2:16 | **Filibuster** — clarinet refuses to surrender the floor |
| 2:38 | **Table the motion** — sousaphone and the two drummers alone |
| 2:49 | **Roll call** — four bars each: cornet, clarinet, alto, trombone |
| 3:11 | **Unanimous** — motion and amendment agree; tempo pushes to 184 |
| 3:32 | **Recount** — three false endings, each contradicted |
| 3:37 | **Majority rules** — unison hook, gavel, final vote |

## Files

- `output/majority_rules.mid` — deterministic GM MIDI, seven named tracks
- `output/majority_rules.wav` — rendered source audio
- `output/roll.png` — piano roll, designed arc, and measured RMS
- `output/marks.json` — listening-room section and cue times
- `src/themes.py` — the two strains, speeches, ballots, and final hook
- `src/compose.py` — fourteen formal sections over one `lib.Piece`
- `src/street.py` — shared *Cut Loose* street-band language plus the gavel
- `docs/` — inspiration, blueprint, and self-assessment

The listening-room package at `web/public/pieces/majority-rules/` includes
the synchronized note data, rendered audio, expressive manifest, and an
engraved MusicXML score whose measured drift is 0 ms.

## Rebuild

```sh
cd pieces-src/majority-rules
../../.venv/bin/python src/compose.py
fluidsynth -ni -g 0.5 -r 44100 -F output/majority_rules.wav \
  ../../../soundfonts/GeneralUser-GS.sf2 output/majority_rules.mid
lame --silent -b 160 output/majority_rules.wav \
  ../../web/public/pieces/majority-rules/audio/mvt1.mp3
cd ../..
.venv/bin/python tools/midi_to_piece.py --id majority-rules \
  --title "Majority Rules" --composer "Codex" \
  pieces-src/majority-rules/output/majority_rules.mid
cd pieces-src/majority-rules && ../../.venv/bin/python export_score.py
```

Composed by Codex, September 2026.
