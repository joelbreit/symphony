# The canvas — geometry blueprint

The roll (`lib.assess.pianoroll`) draws the top panel at ~2000×560 px:
x = seconds, y = MIDI pitch, one horizontal dash per note (lw 1.6),
color = family, alpha = 0.3 + 0.55·vel/127. Percussion never prints.

**Fixed frame for this piece:** one tempo, 120 bpm (1 beat = 0.5 s), 4/4,
~190 s = 380 beats = 95 bars. Pitch used: 26 (D1, bass low) to ~103 (harp
ray tip) → y-limits ≈ 23–110, so **~6.5 px per semitone, ~10.5 px per
second**. Rule of thumb: 1 semitone ≈ 0.6 s visually; a "circle" needs
width(s) ≈ 0.62 × height(semitones).

Storm in D minor, rainbow/sun in F major. Seed **1666** — the year Newton
split white light with a prism.

## Scene layout (x in seconds, y in MIDI pitch)

| element | x | y | material |
|---|---|---|---|
| ground (full width) | 0–190 | 26–40 | bass: pale pedal → walking strut → outro trades (amber) |
| cloud #1 (rain cloud) | 2–50 | 74–85 | tremolo-strings cluster blobs, vel 22–36 (pale gray) |
| rain | 8–58 | 44–74 | pizzicato strings, 16th-grid Dm-pentatonic dots + falling 3-dot streaks (blue) |
| lightning bolt #1 | 28.5 | 76→48 | gtr+harp unison 32nd zigzag, ~2 s, ff (bold amber) |
| lightning bolt #2 | 44.5 | 80→44 | same, bigger; **thunder = kit roll 0.7 s later, invisible** |
| cloud #2 (left foot) | 57–77 | 53–68 | tremolo blob hiding the staggered stripe entries |
| THE RAINBOW | 61–157 | 44–86 | seven parallel elliptical arcs, one family each (see below) |
| cloud #3 (right foot) | 141–163 | 53–68 | tremolo blob hiding the staggered exits |
| outro strut | 158–176 | 26–40 | bass + invisible drum-solo trades — the kit's last laugh |
| sun disc | 175.5–186.5 | 87–102 | harp: cycling pentatonic glissandi filling the disc (amber) |
| sun rays | 172–190 | 85–103 | 8 short harp/guitar dashes around the disc |

## The arch

Top stripe (pink/choir): ellipse **center x = 109 s, rx = 48 s; foot pitch
62 (D4), ry = 24 → crown 86 (D6)**, sampled per rhythm slot and snapped to
F major. Stripe k (k = 0..6: choir, trumpets, guitar, clarinet, square
synth, strings, organ — R O Y G B I V top to bottom) plays the same curve
**2k diatonic steps lower**: constant band spacing ≈ 3.4 st ≈ 22 px, with
white gaps between bands. Any vertical slice of the arch = stacked diatonic
thirds; at the crown the full stack is **F–A–C–E–G–B♭–D = F13** — every
scale tone at once. White light, split.

- Entries staggered 1 bar apart (b122 + 4k), pitches 57–66 at x 61–73 — all
  inside cloud #2. The ellipse is steep at the edges, so each entry is a
  fast upward rip; each exit (reverse order, org first at 145 s) a fall
  into cloud #3.
- Rhythm chosen by local slope: steep → eighth-note runs; moderate → the
  strut riff (syncopated, gaps ≤ 0.3 beat ≈ 1.5 px, reads as a solid band);
  crown plateau (~97–121 s) → shout riff, claps and kit peaking underneath.
- Stripe velocity tracks height: ~86 at the feet → ~104 at the crown
  (saturation = altitude = loudness).

## Beat map (beats at 120 bpm = 0.5 s)

| beat | s | event |
|---|---|---|
| 0 | 0 | mark 'a gray morning' — cloud #1 fades in, pale bass pedal, brushes |
| 16 | 8 | first drips |
| 32 | 16 | mark 'the storm' — rain patterns thicken, bass pulses |
| 57 | 28.5 | bolt #1 → thunder | 
| 89 | 44.5 | bolt #2 → big thunder → downpour |
| 112–121 | 56–60.5 | the turn: rain recedes, press-roll pickup, strut starts |
| 122 | 61 | mark 'Roy G. Biv' — choir enters; entries every 4 beats to org at b146 |
| 194–242 | 97–121 | crown plateau, F13, full shout |
| 290–314 | 145–157 | staggered landings into cloud #3 |
| 316 | 158 | mark 'strut into the sun' — bass/drums trade fours, invisible solo |
| 351–373 | 175.5–186.5 | sun: harp gliss disc + rays; final resolve ~b368; ring to b380 |

## Legend & labels

The family legend would sit lower-right — exactly over the outro ground
line. Extend `lib.assess.pianoroll` with a backwards-compatible
`legend_loc` parameter and put it **upper left**, in the empty sky above
cloud #1. Marks are few (4) and their vertical lines land at scene seams
(two inside cloud cover). Mark labels float along the top of the sky like
a kid's caption.
