# Blueprint — the orbit as form

The decay engine, made concrete. Three revolutions (apogee → perigee), each
apogee shorter and each perigee longer and hotter, then re-entry, the cut,
and the weightless coda. All in 4/4; the 3‑3‑2 lives inside the bar.

## Section map

| # | Section | Key | Tempo ♩ | Bars | ≈ secs | What happens |
|---|---------|-----|--------|------|--------|--------------|
| 0 | Telemetry | A pedal | 66 | 4 | 15 | High piano ping on E6, bass harmonic A, golpe ticks — a beacon, still healthy |
| 1 | Apogee I | A minor | 66 | 16 | 58 | The theme, complete (8+8), bandoneón cantando over guitar arpeggios; violin joins phrase B in sixths |
| 2 | Perigee I | A minor | 120 | 16 | 32 | First low pass: marcato in 4, arrastre into the downbeat, theme recast rítmico (8 bars × 2, violin answers) |
| 3 | Apogee II | C minor | 72 | 10 | 33 | Violin takes phrase A only, octave up; final 2 bars the marcato invades early — the orbit won't wait |
| 4 | Perigee II | C minor | 132 | 20 | 36 | The 3‑3‑2 engine; theme halved to a 4-bar cell, mordents on; 4-bar trades bandoneón/violin/piano; síncopa break |
| 5 | Apogee III | E♭ minor | 80 | 6 | 18 | Bandoneón alone, 2 bars of theme over a violin harmonic — stalls; bass enters at the *next* tempo under it |
| 6 | Perigee III | E♭ minor | 144 | 24 | 40 | Full heat, la yumba weight, theme cell sequenced up the diminished ratchet (E♭–G♭–A); látigo; last 2 bars slide up a semitone |
| 7 | Re-entry | E pedal, 7♭9 | 152 | 16 | 25 | Toccata: the theme is only rhythm now — 3‑3‑2 hammered on E octaves, violin tremolo F↔E (the ♭9), stabbed clusters, register climbing |
| 8 | The cut | — | — | 1 | 3 | Mid-gesture silence. Loss of signal. |
| 9 | After | A minor | 56 | ~11 | 47 | No bass — no floor. Violin harmonics, the E6 ping returns and slows, bandoneón breathes phrase A intact and original. Ends on the quietest chan‑chan ever played |

Total ≈ **5:07**. Apogee durations 58 → 33 → 18 s — a decay constant of
~0.57 per revolution, an actual exponential. Perigee durations 32 → 36 →
40(+25) s, tempos 120 → 132 → 144 → 152: each pass longer, faster, lower.

## The tonal story

Three revolutions at **A minor → C minor → E♭ minor**: the orbits
themselves spell a diminished arpeggio (Piazzolla's minor-third ratchet as
structure, not just sequence). The fourth minor third never arrives —
from E♭ everything is dragged up a *semitone* to **E**, and E is the
dominant of home: re-entry burns on E7♭9, sixteen bars of dominant that
the cut refuses to resolve. The coda's A minor is the resolution — the
ground was the tonic all along. Inside every section, the descending
tetrachord (A–G–F–E and its transpositions) is the bass's gravity well.

## The theme — "the beacon call"

One melody carries the whole piece. Cantando form, A minor, two 8-bar
phrases over the tetrachord bass (one chord change per bar, the well
descending twice per phrase):

- **Phrase A (pregunta)**: a three-note rise (A–B–C) that leaps to a held
  E — the call, sent upward — then sighing stepwise descents; the fourth
  bar tumbles down E7 with F♮ (the ♭9) burning in it; half cadence.
- **Phrase B (respuesta)**: answers from iv (the D minor side), reaches
  the melody's peak through the B♭ Phrygian lean, and settles home late,
  the last note arriving after the harmony has already resolved.

Its life across the piece is the diminution schedule:

| Return | Form |
|--------|------|
| Apogee I | complete, cantando, 16 bars |
| Perigee I | rítmico recast on the marcato grid, staccato, 8 bars |
| Apogee II | phrase A only, violin, octave up |
| Perigee II | halved note values → 4-bar cell, mordents added |
| Apogee III | first gesture only (2 bars), alone |
| Perigee III | 2-bar cell, sequenced, ornamented harder |
| Re-entry | rhythm only, on one pitch |
| After | phrase A bars 1–4, intact, original register — restored |

## Texture rules (per idiom study)

- Straight eighths everywhere; `write(swing=None)`. Rubato is written into
  the melody's note placement, not the tempo map.
- Every bandoneón note ≥ 1 beat gets a CC11 bellows shape; violin long
  notes swell too; CC11 resets to full before each rítmico section.
- Marcato gate 0.6, velocities alternating heavy–light; arrastre
  (bass scoop + piano chromatic smear) into phrase downbeats.
- Piano pedal only in apogees and the coda; perigees are dry.
- Golpe channel (rim/woodblocks/cabasa): telemetry ticks in §0, tambor
  pops in P1, chicharra-ish cabasa in P2, nothing in the coda until the
  final two blinks.
- Coda: **no double bass**. The floor is gone; that's the point.

## Verification targets

- Designed arc: pp / mp / **f** / p / **f+** / pp / **ff** / **fff** / — /
  ppp — a sawtooth with rising peaks and sinking valleys. The measured RMS
  overlay in `assess.pianoroll` must show this shape.
- Range report clean; every melody entered through `B()` bar guards.
- Total duration 4–6 min (design says 5:07).
- Byte-identical rebuild (seeded).
