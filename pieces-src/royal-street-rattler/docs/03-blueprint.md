# Blueprint — form, changes, and bar map

**Title:** Royal Street Rattler
**Tempo:** 198 bpm, 4/4 (two-beat feel) · light swing
**Keys:** F major (A strain), D minor (B strain), B♭ major (trio)
**Target length:** ~184 bars ≈ 3:45

## The strains

### A strain — "The Strut" (16 bars, F major)
The catchy one. Rattle motif over the Ja-Da family changes:

| 1–2 | 3–4 | 5–6 | 7–8 |
|---|---|---|---|
| F · F | D7 · D7 | G7 · G7 | C7 · C7 |

| 9–10 | 11–12 | 13–14 | 15–16 |
|---|---|---|---|
| F · F7 | B♭ · B°7 | F/C · D7 | G7–C7 · F |

### B strain — "Balcony Shadows" (16 bars, D minor)
Trombone feature. Minor strut, "That's a Plenty" energy:

| 1–2 | 3–4 | 5–6 | 7–8 |
|---|---|---|---|
| Dm · A7 | Dm · A7 | Dm · Dm/C | B♭7 · A7 |

| 9–10 | 11–12 | 13–14 | 15–16 |
|---|---|---|---|
| Dm · D7 | Gm · Gm | Dm · B♭7–A7 | Dm · C7 (pivot home) |

### Trio — "Out to the River" (16 bars, B♭ major)
Sunny, open, "Saints"-adjacent — the solo/shout vehicle:

| 1–2 | 3–4 | 5–6 | 7–8 |
|---|---|---|---|
| B♭ · B♭ | F7 · F7 | F7 · F7 | B♭ · B♭7 |

| 9–10 | 11–12 | 13–14 | 15–16 |
|---|---|---|---|
| E♭ · E°7 | B♭/F · G7 | C7 · F7 | B♭ · (F7 turn / B♭ final) |

## Roadmap (bar-by-bar)

| # | Section | Bars | Key | What happens |
|---|---|---|---|---|
| 1 | Intro | 8 | F | Streetcar bell + solo trumpet fanfare break (4), band answers with hits (4) |
| 2 | A strain ×2 | 32 | F | Head. 1st: trumpet lead, full collective improv. 2nd: clarinet takes the lead an octave up, trumpet harmonizes below |
| 3 | B strain | 16 | Dm | Trombone feature, growls & smears; clarinet shadows; band tightens |
| 4 | A strain | 16 | F | The Strut returns, everyone leaning in harder |
| 5 | Modulation | 4 | F→B♭ | F7 band hits + sousaphone walkup, 2-beat clarinet break into trio |
| 6 | Trio theme | 16 | B♭ | New sunny tune, ensemble but lighter touch |
| 7 | Clarinet solo | 16 | B♭ | Rhythm section only; pure filigree |
| 8 | Tenor sax solo | 16 | B♭ | Bluesy storytelling; horns pad quiet guide tones in bars 9–16 |
| 9 | Trumpet solo | 16 | B♭ | Bars 1–8 stop-time (band hits beat 1 only), bars 9–16 full backing |
| 10 | Drum break | 4 | — | Woodblock + snare, streetcar rattle as a drum solo |
| 11 | Shout chorus | 16 | B♭ | Band riff in call-and-response, trumpet on top |
| 12 | Out chorus | 16 | B♭ | Trio theme paraphrased up an octave, collective improv at full boil |
| 13 | Tag/coda | 8 | B♭ | Dixieland tag ×3 (breaks: trombone, clarinet, trumpet), final hits + cymbal, sousaphone plop |

**Total: 184 bars ≈ 3:43 at 198 bpm.**

## Production plan

1. `src/compose.py` — everything is data + small builders:
   - chord chart per strain → banjo comping, sousaphone two-beat, drum patterns generated
   - melodies & solos hand-composed as `(beat, duration, pitch, accent)` event lists
   - swing + humanize transform applied at the end, then written with `midiutil`
2. Outputs to `output/`:
   - `royal_street_rattler.mid` — the playable piece (GM, 7 tracks)
   - `royal_street_rattler.wav` / `.m4a` — fluidsynth render with MuseScore General
   - `leadsheet.abc` — human-readable lead sheet of the three strains with chords
   - `pianoroll.png` — visual self-check of registers/density
3. Self-assess: duration, range violations, voice collisions, texture density per
   section; listen-check the render; iterate.
