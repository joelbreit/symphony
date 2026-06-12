# Architecture — Symphony No. 1 in C minor, "The Window"

Target: 16–19 minutes, full symphonic orchestration, delivered as playable MIDI
(per-movement + full assembly), built programmatically with music21.

## The cyclic spine

- **The Question (motto)**: G–C–E♭–D — rising 4th, rising minor 3rd, falling semitone.
  Never resolves to C until the final movement. Appears in every movement.
- **The Answer**: G–C–E–D–C — major-mode transformation, resolution granted. Finale only.
- Mvt III opens with the motto in major (E♭–A♭–C–B♭ in A♭) — the "almost-answer,"
  still denied its final note.

## Movement form maps

### I. Kindling — C minor, ~5.5 min
| Section | Tempo | Meter | Bars | Content |
|---|---|---|---|---|
| Intro | Adagio misterioso ♩=54 | 4/4 | 16 | Low C pedal; motto fragments scattered (vc: G–C; ob: E♭–D; hn: rising 4th) coalescing; crescendo into first full motto **ff** in brass |
| Exposition | Allegro con fuoco ♩=144 | 4/4 | 56 | T1 (Cm, driving 8ths from motto diminution, strings); transition; T2 (E♭, lyric inversion, ww + pizz); codetta |
| Development | ♩=144 | 4/4 | 44 | T1/motto fragments cycled (Fm→Gm→A♭→D♭); brass stretto on motto; dominant pedal |
| Recap | ♩=144 | 4/4 | 48 | T1 in Cm; T2 in C **major** (foreshadow of Answer) then darkened back to minor |
| Coda | ♩=152 | 4/4 | 14 | Drive to cadence; final motto **ff**, D left hanging over open G–C — unresolved |

### II. The Garden of Forking Paths — G minor, ~2:50
| Section | Tempo | Meter | Bars | Content |
|---|---|---|---|---|
| Scherzo A | Presto leggiero ♩.=80 (one-in-a-bar) | 3/4 | 80 | Staccato arpeggio theme, offbeat accents, deceptive cadences as "forks"; motto in diminution, mocked |
| Trio | Poco meno ♩.=66 | 3/4 | 56 | G major; horn/bassoon drone, flute musette tune; warm branch |
| Scherzo A′ | ♩.=80 | 3/4 | 48 | Compressed reprise, more feints |
| Coda | ♩.=80 | 3/4 | 20 | Evaporates — pizzicato, piccolo wisp, gone |

### III. What the Light Holds — A♭ major, ~4 min
| Section | Tempo | Meter | Bars | Content |
|---|---|---|---|---|
| A | Adagio cantabile ♩=56 | 4/4 | 16 | Long-breathed string melody opening with major-mode motto (E♭–A♭–C–B♭); harp underlay |
| B | ♩=56 | 4/4 | 12 | Woodwind dialogue, modulating warmth (D♭, F minor shadow) |
| A′ climax | ♩=60 | 4/4 | 14 | Tutti soaring restatement → **interrupted at the peak by the minor motto** (brass, the memory of mortality) |
| Coda | ♩=52 | 4/4 | 12 | Serenity regained but resolution *evaded* (deceptive cadence → settles on A♭ with C on top, leading to finale) |

### IV. Through — C minor → C major, ~6 min
| Section | Tempo | Meter | Bars | Content |
|---|---|---|---|---|
| Storm | Allegro agitato ♩=138 | 4/4 | 20 | Mvt I intro fragments return, agitated; motto in canon over tremolo |
| Striving | ♩=138 | 4/4 | 72 | March-like theme; rising sequences; collapses twice before breaking through |
| Chorale | Maestoso ♩=84 | 4/4 | 22 | **The Answer** — G–C–E–D–C in brass chorale, sunrise scoring |
| Apotheosis | Allegro glorioso ♩=144 | 4/4 | 40 | Mvt I T1 in C major in counterpoint with the Answer; full tutti |
| Coda | Lento lucente ♩=48 | 4/4 | 14 | Sudden hush; texture dissolves to opening fragments — harp, celesta, solo strings; final **pp** Answer in flute/celesta; high C alone. The window closes. |

## Orchestra roster (16 MIDI channels)

| Part | GM program | Range guard (MIDI) |
|---|---|---|
| Flutes 1&2 (+picc) | 73 | C4–C7 (picc to C8) |
| Oboes 1&2 | 68 | B♭3–F6 |
| Clarinets 1&2 | 71 | D3–G6 |
| Bassoons 1&2 | 70 | B♭1–E♭5 |
| Horns 1–4 | 60 | B1–F5 |
| Trumpets 1&2 | 56 | E3–C6 |
| Trombones + Tuba | 57 | D1–C5 |
| Timpani | 47 | D2–A3 |
| Harp | 46 | C1–G7 |
| Celesta/Glock | 8 | C4–C8 |
| Violin I | 48 (ensemble) | G3–E7 |
| Violin II | 48 | G3–C6 |
| Viola | 48 | C3–E6 |
| Cello | 48 | C2–A5 |
| Contrabass | 48 | E1–G3 (sounding) |
| Percussion (cym/bd) | ch 10, keys 49/35/57 | — |

Strings use GM 48 (String Ensemble) rather than solo programs for section weight;
pizzicato passages switch to GM 45 mid-part.

## Tooling

```
compose/
  common.py    # note DSL ("G4:q Eb5:e r:h"), Orchestra class, texture helpers,
               # velocity/dynamics map + humanization, range validation, MIDI writer
  mvt1.py ... mvt4.py   # each: compose(orch, t0) -> end_offset
  build.py     # per-movement MIDIs + full assembly with inter-movement gaps
  validate.py  # mido-based: duration, per-track note counts, range checks, channels
output/        # mvt1.mid ... mvt4.mid, symphony_full.mid
```

- Offsets are quarterLengths; MetronomeMarks inserted at section boundaries drive real time.
- Dynamics as explicit velocities (ppp 28 … fff 112), ±4 humanization, downbeat accent.
- Tremolos/trills written out as sounded notes (MIDI realism > notation shorthand).
- Percussion channel-10 handling verified in smoke test; mido post-process as fallback.

## Validation gates (per movement, then full)

1. MIDI loads in mido; duration within ±15% of budget.
2. Every part within its range guard.
3. No silent movement-long part gaps unless scored as tacet.
4. Dynamic arc sanity: climaxes where planned (velocity profile over time).
5. Final: total ≥ 15 min, 16 channels max, program numbers correct.
