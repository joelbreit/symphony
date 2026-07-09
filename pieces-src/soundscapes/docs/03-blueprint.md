# 03 — Blueprint: scenes, stems, budget

Shared rules: 4/4 throughout; one mode and one bpm per scene; loop lengths in
bars pairwise non-multiple (docs/02); every stem obeys the seam rules; audio
budget ≤ ~8 MB per scene at 160 kbps AAC (≈ 1.2 MB/min).

Slot grammar (what the engine understands, per layer): `always` layers never
rest; others enter/exit on the conductor's cadence within `minOn`/`minOff`;
`gainRange` bounds slow gain drift; variants swap only at loop boundaries.

## Focus — A dorian, 72 bpm · steady, present

Harmonic cycle: Am – C – G – D (i, ♭III, ♭VII, IV — all diatonic, no leading
tone; D major is the dorian color). The bed holds an A–E fifth that reads as
home under all four.

| slot | bars | loop | variants | content | register |
|---|---|---|---|---|---|
| bed (always) | 16 | 53.3s | a | A–E fifth in two overlapped breath groups + organ anchor (docs/02 rule 2) | A1–A4 |
| pad-mid | 10 | 33.3s | a, b | the cycle as slow pad chords, `voicing()`, one chord per 2–3 bars | G2–E5 |
| halo | 12 | 40.0s | a, b | bowed glass, high sparse dyads drifting across the cycle | E4–C7 |
| motif | 14 | 46.7s | a, b | e-piano fragments, 3–5 notes, long rests between phrases | C3–E6 |
| pulse | 8 | 26.7s | a, b | kalimba ostinato, quiet eighths, small melodic cells | C4–C7 |

9 files ≈ 6.2 min audio ≈ 7.5 MB. Full-state recurrence LCM(16,10,12,14,8)
= 1680 bars ≈ 93 min.

## Deeper Focus — D dorian, 60 bpm · further down, tidal

The same room as Focus later at night: the center sinks a fifth, the clock
slows, the pulse becomes a bass tide. Cycle in threes: Dm – F – C (variant b:
Dm – G – Am, leaning on the dorian IV). Same proven patches as Focus sunk a
register; the one new voice is a fingered bass, chosen because a pluck's
natural decay is seam-proof (nothing sustains across the boundary).

| slot | bars | loop | variants | content | register |
|---|---|---|---|---|---|
| bed (always) | 16 | 64.0s | a | D–A fifth, two overlapped breath groups + organ anchor | A1–D4 |
| pad-low | 12 | 48.0s | a, b | three overlapping chords per cycle, `voicing()` | E3–E4 |
| haze | 14 | 56.0s | a, b | halo-pad dyads, higher and quieter than focus halo | A4–E6 |
| murmur | 10 | 40.0s | a, b | low e-piano fragments, 2–3 phrases, long rests | D3–D4 |
| tide | 8 | 32.0s | a, b | half-note bass rocking root–fifth on the bar grid | A1–D2 |

9 files. Full-state recurrence LCM(16,12,14,10,8) = 1680 bars ≈ 112 min.

## Relax — D mixolydian, 58 bpm · warm, unhurried

Cycle: D – C – G/B – D (I, ♭VII, IV6 — plagal drift, never a cadence).

| slot | bars | loop | variants | content |
|---|---|---|---|---|
| bed (always) | 16 | 66.2s | a | D–A fifth, warmer/lower than focus, same two-group construction |
| pad-mid | 10 | 41.4s | a, b | cycle chords, low-mid voicings |
| halo | 12 | 49.7s | a, b | soft high pad, fewer notes than focus halo |
| motif | 14 | 57.9s | a, b | breathy flute, even sparser than focus motif |
| arp | 8 | 33.1s | a, b | slow harp broken chords (`harp_arp`), replaces the pulse |

9 files ≈ 8.2 min ≈ 8 MB (longest scene — watch the budget at render).

## Sleep — C aeolian, 48 bpm · dark, nearly still

Cycle: Cm – Ab – Fm – Cm (i, ♭VI, iv — all soft thirds, no motion upward).
No pulse of any kind; everything below mf; high register only as haze.

| slot | bars | loop | variants | content |
|---|---|---|---|---|
| bed (always) | 12 | 60.0s | a | C–G sub fifth, slowest breathing, organ anchor very low |
| pad | 10 | 50.0s | a, b | dark low-mid chords, one per 3–4 bars |
| bell | 16 | 80.0s | a, b | celesta, one or two pp notes per 4 bars |
| breath | 8 | 40.0s | a, b | very quiet pad swells, more silence than sound |

7 files ≈ 7.7 min ≈ 7 MB. (Bell at 16 vs bed 12: recurrence LCM(12,10,16,8)
= 240 bars = 20 min for the full state — acceptable; the conductor's layer
resting stretches perceived recurrence far past that.)

## Accents (refined at manifest time)

Focus `#8fb7c9` cool steel · Deeper Focus `#6d94ad` deep steel · Relax
`#d9915e` warm amber · Sleep `#8a7fc9` deep violet — all muted against the
room's `#0b0e14`.
