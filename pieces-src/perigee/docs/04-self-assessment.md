# Self-assessment

Against the blueprint's verification targets (docs/03) and goal.md's
constraints, on the built MIDI (`output/perigee.mid`, seed 1957) and the
FluidSynth/GeneralUser GS render.

## The arc, designed vs. measured

The whole thesis was measurable: a sawtooth with rising peaks (each perigee
hotter) and sinking valleys (each apogee thinner), then silence, then a
whisper. Per-section RMS of the render:

| Section | Designed | Measured |
|---|---|---|
| telemetry | pp, sparse | −46.4 dBFS |
| apogee I | p, lyric | −37.7 |
| **perigee I** | **f** | **−27.7** |
| apogee II | p, shorter | −35.2 |
| **perigee II** | **f+** | **−25.6** |
| the last apogee | pp | −35.0 |
| **perigee III** | **ff** | **−24.2** |
| **re-entry** | **fff** | **−22.1** |
| loss of signal | silence | −51.8 (median −93: true silence) |
| after | ppp | −47.1 (peaks −38.8) |

Peaks rise monotonically 27.7 → 25.6 → 24.2 → 22.1; the decay engine is
audible in numbers. Durations landed as designed: apogees 58 → 33 → 18 s
(the ~0.57 decay constant), perigees 32 → 36 → 40 s at ♩=120/132/144,
total 5:05 — inside the 4–6 minute constraint.

## What the checks caught (the iteration record)

- **Bandoneón over its ceiling**: the re-entry hammering originally
  stacked octaves to E7, above the roster's B6 — caught while writing,
  fixed by re-voicing the third tier as triple octaves E4/E5/E6. The
  fail-fast range guard is why the first build ran clean.
- **Coda too faint**: first render's coda peaked at −41.5 dBFS, 6 dB
  *below* the telemetry intro — a listener leveled for the piece would
  have lost it. Lifted all coda velocities ~8 points; now peaks −38.8
  with the median still ~13 dB under the piece average. Quietest music
  in the piece, but present. This is exactly the check a designed-arc
  plot alone would not catch — it needed the measured render.
- **Determinism**: rebuild is byte-identical (MD5 stable across runs).
- **Ranges**: final report all OK — violin F4..D#7, bandoneón G3..B6,
  guitar G#2..B5, bass E1..A2, every melody entered through `B()` guards.

## Idiom honesty (docs/02 as the bar)

Kept faithfully: marcato in four with heavy/light alternation; the 3‑3‑2
engine with the anticipation accented; arrastre as bass scoop + piano
chromatic ramp into phrase downbeats; la yumba's slammed 1-and-3 with
ghosted 2-and-4; mordents arriving as the heat rises; bellows shapes on
every held bandoneón note; the chan‑chan ending, played ppp. The elastic
melody/strict accompaniment split is honored (straight write, rubato in
the note placement).

GM compromises, owned: the "bandoneón" is GM 23 Tango Accordion (close in
spirit, brighter in tone); violin "harmonics" in the coda are ordinary
timbre played very quietly and high; the chicharra is approximated by
pp cabasa ticks on the golpe channel; the látigo is a written-out
chromatic whip rather than a true gliss. Nothing pretends to be what the
synth cannot do — tremolos, turns, and smears are all sounded notes.

## Honest weaknesses

- The re-entry toccata is deliberately static (a hammered dominant pedal);
  on a synth without timbral escalation it leans on register and density
  alone. The four-bar rocket rescues it, but a real band would burn more.
- Apogee II's early-marcato "invasion" approximates a tempo collision
  (eighth-note double-time under the old tempo) — the real effect wants
  two simultaneous tempi, which single-track MIDI cannot do.
- The guitar comps correctly but never solos; in a real quintet it would
  earn one break. The piece chose compression over democracy.

## Toolkit verdict (the piece's second job)

Perigee is the first piece built on `lib/`, and the toolkit held: no
channel hacks, CC bellows/pedal/scoops first-class, the quintet defined
as data in `band.py`, marks exported straight to the web schema. All
tango vocabulary fit in one piece-local module (`src/tango.py`) on top of
`fit`/`voicing`/`figures` — nothing needed lib changes. Promotion
candidates that emerged: `mordent` (general ornament, used constantly)
and possibly `bellows` (any breathing instrument); left local for now per
goal.md's promote-with-tests policy, to be promoted when a second piece
wants them.
