# Blueprint — "High Street Riot"

## Ground rules

- **Key:** G minor (dorian-leaning blues: G A B♭ C C♯/D♭ D F F♯ as neighbors). The vamp
  never leaves G — episodes color it instead (iv = Cm7, V = D7♯9, ♭9 = A♭9 the "riot chord").
- **Tempo:** 160 bpm, 4/4, swung 8ths (~0.62 swing — lighter than 2:1 at this speed).
- **Length target:** ~128 bars ≈ 3:15.
- **Build:** Python + music21. Themes hand-written note-by-note; banjo/drums/tailgate
  realized by small constrained generators; swing + velocity humanization applied in a
  post-pass before MIDI export. Render: fluidsynth + GeneralUser-GS.sf2 → wav → m4a.

## The materials

1. **THE RIFF** (sousa, 2 bars) — see inspiration doc. Strut up / snarl down.
2. **SHOUT-BACKS** (horns) — stabs landing in the riff's breaths (beat 2 area), so
   tuba and horns interlock like gears. "HEY!" … "HEY-HEY!"
3. **THE ANTHEM** (the wail) — 8-bar screamed descent built from long tones with
   fall-offs: D5 world, bends through C–B♭, lands on the ♭5 D♭ before resolving.
   Harmonized Gm — Gm — Cm7 — D7♯9 cycle when full band carries it.
4. **THE LADDER** — the transcription's m9–12 trick: same riff, horns stacking
   3rds/6ths above, voices added every 2 bars, dissonance rising (F♯, A♭, B♮ creep in).
5. **THE RIOT CHORD** — A♭9 slammed against the G pedal (Neapolitan), resolving down
   a half-step. The "angry" sound, used sparingly until the stomp, then abused.
6. **THE CLUSTER** — hammered [E♭–A–D] quartal/tritone stab (straight from the
   transcription's m14) as the climax punctuation.

## The form (bar numbers, 160bpm → 1.5s/bar)

| Bars | Len | Section | What happens |
|---|---|---|---|
| 1–4 | 4 | The shrug | Sousa alone ×2 riffs, raw and confident |
| 5–8 | 4 | The pile-on I | + drums (press roll → backbeat), banjo chunk |
| 9–12 | 4 | The pile-on II | + trombones in 3rds/6ths (the ladder begins), clarinet curl at 12 |
| 13–20 | 8 | The shout | Full band; horn shout-backs interlock with riff; cornet calls |
| 21–28 | 8 | The wail | Anthem screamed over Gm–Gm–Cm7–D7♯9; tailgate trombone |
| 29–32 | 4 | Floor drop | Sousa + banjo + hats only |
| 33–44 | 12 | Trombone lead | Rude gliss-heavy solo; bone 2 + sax pads creep in at 41 |
| 45–56 | 12 | Cornet lead | Declamatory; bones stab riff fragments behind; clarinet shriek at 55 |
| 57–68 | 12 | Clarinet lead | High acrobatics over iv (Cm) half, back to G; ladder rebuilds beneath |
| 69–80 | 12 | The argument | Bone vs cornet trade 2s; sax + clarinet butt in; ends all-at-once |
| 81–92 | 12 | The stomp | Stop-time: Gm and A♭9 slams on the riff's downbeats; sousa never stops; toms four-on-floor |
| 93–96 | 4 | The collapse | Drums alone 2, sousa mutters back in under drum chatter 2 |
| 97–120 | 24 | The riot | Riff 8va in bones+sax, anthem on top (themes combined), four-on-floor; 113–120 climb + cluster hammers + A♭9→Gm slams |
| 121–124 | 4 | The wink | Dead stop · sousa alone snarl lick · A♭9 stab → Gm6/9 stab · unison G "HUH" |

Total: 124 bars + final hit ≈ 3:10–3:20.

## Craft checklist (self-assessment targets)

- [ ] Riff singable, loops with no seam, survives 60+ repetitions via re-orchestration
- [ ] Horns and tuba interlock (notes in each other's rests) — never mud
- [ ] Every section change earns itself (add/subtract ≥2 elements or shift harmony)
- [ ] Dynamics travel: solo tuba pp→f … full riot fff, with two real valleys
- [ ] Anger = dissonance ON the beat (D♭, A♭9, clusters), resolved late — not random wrong notes
- [ ] Idiomatic ranges: sousa E1–G3, bones E2–B♭4, cornet F♯3–C6 (scream D6 once), clarinet E3–G6, tenor sax A♭2–E♭5 written-sounding
- [ ] Swing + velocity shaping + slight time scatter so MIDI doesn't sound like a typewriter
- [ ] Ends with a wink, not a fade
