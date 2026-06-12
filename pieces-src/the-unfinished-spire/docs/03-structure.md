# Structure Blueprint

All in 4/4. Durations from bars × 4 ÷ tempo. Target total ≈ 5¾ minutes.

| § | Name | Key | Bars | Tempo | ≈Time | What happens |
|---|------|-----|------|-------|-------|--------------|
| I | **Dawn** | E♭ | 16 | q=69 | 0:56 | pp low E♭ pedal (vc+cb), divisi violin mist, harp arpeggios. Solo horn: the Summons; soft trumpet echo. Woodwind flickers (birdsong). Slow crescendo of light. |
| II | **The Anthem** | E♭ | 24 | q=92 | 1:03 | Full 16-bar theme, mf — melody horns+celli, hymn voicing beneath. Then Strain B repeated, f — violins take melody 8va, countermelody stirring, timpani enters. |
| III | **The Work** | Cm→E♭ | 20 | q=126 | 0:38 | Motoric ostinato, walking bass, snare. Summons in stretto (cl→ob→fl→tpt). Accumulates every 4 bars, brightens to E♭, hemiola, G7… |
| IV | **The Single Voice** | A♭ | 16 | q=78 | 0:49 | …deceptive resolve to A♭. Solo oboe sings the Doubt theme over cushioned strings, harp. Flute takes it 8va, clarinet beneath; small climax; sigh-off. |
| V | **The Long Night** | Cm | 14 | q=126→138 | 0:25 | Lament-bass ground, fragments of doubt-theme minor-warped, inverted summons in muted trumpet, diminished climb, chromatic ascent, Ger6 → I6/4 → B♭7 pedal fff. |
| — | **G.P.** | — | 1 | — | 0:03 | One full bar of silence. The longest second in the piece. |
| VI | **The Sunrise** | C♭→B♭7 | 6 | q=66 | 0:22 | C♭ major (♭VI) pp→ff swell, first tubular bell. Change-ring figure. Brightens through B♭sus → B♭7, bells pealing, strings climbing. |
| VII | **Apotheosis** | E♭ | 18 | q=86 | 0:50 | Full anthem, fff: trumpets+Vln I melody, **horns+celli sing the Doubt theme as countermelody**, trombone/tuba pillars, woodwind garlands, bells, timpani. Bar 15: deceptive vi — one last shadow — then IV → I6/4 → V7 broadening. |
| VIII | **Coda** | E♭ | 12 | q=80→52 | 0:45 | Hemiola peal. Subito p: solo horn Summons over pp strings — the next morning, far off. Final 2-bar build to fff E♭ across five octaves; cymbal, timpani roll. Cutoff — **bells alone ring into silence.** |

**Total ≈ 5:51** + ring-out.

## The dynamic arc (what the loudness curve should show)

```
fff                                          ▄▄▄    ▄█
ff                      ▂▄▆            ▆██▆▄▆███▆  ▆██
f          ▂▄▆▆▄▂    ▄▆███            ▆████████████ ██
mf       ▄▆██████▆▄▆██████           ▆██████████████ █
p   ▂▄▆▆█████████████████▆▄▂       ▄▆███████████████ ▆▂
pp ▆██████████████████████ ▆▄▂▁ ▁▆████████████████████ ▁
    I       II      III    IV  V GP VI   VII      VIII
```

Quiet birth → first pride → busy joy → inward hush → gathering dark → silence →
awe-swell → full blaze → far-off echo → final blaze → bells decay.

## Build plan (code)

1. `src/theory.py` — pitch names, chords, scales, dynamics constants.
2. `src/score.py` — `Score` wrapper over MIDIUtil: absolute-beat note placement,
   tempo map, hairpins, staggered entries, humanization (seeded), range validation
   per instrument with hard assertions.
3. `src/compose.py` — the piece, one function per section, each returning its end beat.
4. `src/analyze.py` — duration check, per-instrument range report, piano-roll PNG,
   note-density and velocity-arc plots. **Look at the plots, then revise.**
5. Render: fluidsynth + GeneralUser GS → WAV; RMS loudness curve → compare against
   the target arc above; revise until it matches.
