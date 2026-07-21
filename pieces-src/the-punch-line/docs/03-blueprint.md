# Blueprint — "The Punch Line"

The scaffolding, decided before notes. 2/4 throughout; one bar = 2 beats;
tempo 96 (flat). 158 bars ≈ 3:17 plus the final ring.

## The map

| Bars | Section | Key | Dyn | What happens |
|---|---|---|---|---|
| 1–4 | **Intro — the walk-on** | A♭ | f | Both hands in octaves: a descending chromatic strut, a rising snap back up, landing on E♭7 with a breath. Attention, please. |
| 5–20 | **A — the setup** | A♭ | mf | The hit single. Rising tonic-arpeggio hook with the snap; "knock-knock" repeated-note motif; tied syncope in the third phrase; cadence that lands a sixteenth early (the joke arriving before you're ready). Light stride: single basses, octaves at arrivals. |
| 21–36 | **A′ — re-punched** | A♭ | mf+ | The roll arranger's varied repeat: melody an octave up, chattering fills in the phrase gaps, walking-octave seams in the left hand. |
| 37–52 | **B — the topper** | A♭ | f | Same premise, escalated: starts on III7 (the rag cycle III7→VI7→II7→V7 twice), register a third higher, **secondary rag** (3+3+2 sixteenth accents) as the engine. |
| 53–68 | **B′ — with teeth** | A♭ | f+ | Repeat with crushes on the secondary-rag accents, octave basses throughout, one broken-tenth roll per phrase. |
| 69–84 | **A″ — the callback** | A♭ | mf | First half verbatim (recognition is the joke). Second half re-cadenced softer, tilting toward IV — the aside is coming. |
| 85–88 | **Interlude — leaning in** | A♭→A♭7 | mp | Four bars: the stride thins, walking octaves descend, A♭ becomes A♭7 (V7 of D♭). The storyteller drops his voice. |
| 89–104 | **C — the aside (trio)** | D♭ | p→mp | The warm strain: melody in parallel sixths, longer notes, legato, pedal dabs on the lyrical bars. Dynamic floor of the piece. |
| 105–120 | **C′ — in octaves** | D♭ | mp+ | Trio repeat: melody in octaves, a tenor countermelody answering in the gaps, still gentle. |
| 121–122 | **The pause** | (E♭7) | — | Bar 121: right hand alone — an E♭7 "wait-for-it" figure. Bar 122: **silence.** A full bar of nothing, the longest the piece ever goes without the grid. |
| 123–138 | **D — the punch line** | A♭ | f | Opens in **stop-time**: two bars of downbeat stabs under solo right hand. Stride slams back in bar 3. The rideout strain: snap + secondary rag at full grin; second half reuses A's cadence half (the punch line recycles the setup's own words). |
| 139–154 | **D′ — the doctored roll** | A♭ | ff | The ghost stops pretending. Escalation every 4 bars: ① melody doubled an octave up (plausible); ② + sustained tremolo thirds punched into the middle register (improbable); ③ + three registers of melody, doubled octave basses in contrary motion (impossible); ④ a five-octave unison run and stacked chords into the tag. Tempo may crank to 100. |
| 155–158 | **Tag — shave and a haircut** | A♭ | ff | Stop-time: the oldest punch line in music, fully orchestrated. "Two bits" lands; a five-octave rolled A♭ chord with pedal; then — after the ring — **one tiny high A♭, pp**: the last hole punched in the roll. |

Section marks at every boundary above (they label the web player); cues:
`wait for it` (b.121), `the ghost stops pretending` (b.139), `two bits`
(b.157), `the last hole` (final note).

## Harmony per strain

One chord per bar unless slashed; `(x,y)` = split bar.

- **A / A′ / A″** (and D's second half):
  `Ab Ab Eb7 Eb7 | Eb7 Eb7 Ab Ab | Ab Ab7 Db Ddim7 | Ab/Eb F7 (Bb7,Eb7) Ab`
  — I, the long dominant lean, then the classic second half: V7/IV → IV →
  ♯ivdim7 → I/5 → VI7 → II7 → V7 → I. A″ bars 81–84 soften: `Ab/Eb F7
  (Bb7,Eb7) (Ab,Ab7)` never quite closing, spilling into the interlude.
- **B / B′**: the rag cycle, twice:
  `C7 C7 F7 F7 | Bb7 Eb7 Ab Eb7 | C7 C7 F7 F7 | Bb7 Eb7 (Ab,Eb7) Ab`
- **Interlude**: `Ab (Ab,Abaug) Ab7 Ab7` with a rising run into D♭.
- **C / C′** (in D♭): same skeleton as A transposed —
  `Db Db Ab7 Ab7 | Ab7 Ab7 Db Db7 | Gb Gb Gdim7 Gdim7 | Db/Ab Bb7 (Eb7,Ab7) Db`
  (C′ bar 120 splits `(Db,Eb7)` — E♭7 is V of A♭: the pause and D strain
  hang off it.)
- **D**: `Ab Ab C7 C7 | F7 F7 Bb7 Eb7 |` + A's second half.
- **Tag**: `Ab Ddim7 | (Ab/Eb,Eb7) | Eb7 | Ab` under shave-and-a-haircut.

## Registers

| Layer | Range |
|---|---|
| Bass notes (oom) | A♭1–E♭3, octaves at arrivals |
| After-beat chords (pah) | G3–G4, 3–4 notes, dry |
| Melody A/B/D | C5–C6 (A′ up an octave; B a third higher) |
| Trio melody | A♭4–F5 in sixths; C′ octaves |
| Doctored layers | +12 and +24 doublings up to C8's neighborhood; runs down to A♭1 |

## Dynamics arc (design targets for the assess plot)

Intro f (86) → A mf (72) → A′ 76 → B f (86) → B′ 90 → A″ 72 →
interlude mp (60) → C p→mp (48→60) → C′ 64 → pause (thin) →
D f (88) → D′ ff (100→108) → tag 108, final ping pp (36).
Bass ≈ melody −6; after-beat chords ≈ melody −16. The shape is a
two-hump comedy arc: big laugh at B′, reset for the trio, biggest laugh
at the end.

## Verification plan

1. `assess.report` — clean ranges, section map, ~3:20 duration.
2. `assess.pianoroll` — the arc above must be visible in the plot; the
   pause must read as a white column.
3. Render (fluidsynth → wav), listen start to finish; re-punch anything
   that plods; overlay measured RMS on the arc plot.
4. Playability audit of everything before bar 139 (spans ≤ octave RH /
   tenth LH, no three-hand moments); confirm the doctoring *reads* as an
   event at bar 139 — if it doesn't shock a little, escalate ④.
5. Package via `tools/midi_to_piece.py`, check in the web player.
