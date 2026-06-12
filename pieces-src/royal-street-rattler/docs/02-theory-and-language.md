# Theory & Language — what makes it sound like Dixieland

Working notes: the stylistic rules I'm composing inside of, and how each one maps to
something concrete in the MIDI.

## Rhythm section

- **Two-beat feel.** Sousaphone plays beats 1 and 3 (root–fifth alternation), banjo
  chunks all four beats with accents on 2 and 4. The "flat four" banjo against the
  two-beat tuba is *the* New Orleans street-band engine.
- **Tuba walkups.** At the end of 4-bar phrases the sousaphone walks quarter notes
  (diatonic/chromatic) into the next chord's root. This is what makes the bass feel
  alive instead of mechanical.
- **Early-jazz drums.** No ride cymbal pattern (that's 1935+). Instead: bass drum on
  1 and 3, snare back-beats and press-roll figures, **woodblock** syncopation (very
  1920s), cymbal crashes to mark section downbeats, and stop-time/break choruses.

## The front line — collective improvisation roles

Three voices at once, kept out of each other's way by **register and rhythm**:

- **Trumpet/cornet**: the lead. Plays the melody (or a paraphrase), middle register
  (~F4–F5), declamatory, syncopated, leaves holes at phrase ends.
- **Clarinet**: the obbligato. Lives *above* the trumpet (~C5–G6), moves when the
  trumpet holds, arpeggio runs, chromatic enclosures, trills. Fills every hole.
- **Trombone**: the tailgate. Lives *below* (~F2–F4), connects chord roots with
  glissandi and smears, plays half-note counterlines, punches pickups into downbeats.
  MIDI realization: pitch-bend scoops into notes + fast chromatic run-ups for smears.

Rule of thumb I'm enforcing: at any moment, at most one front-line voice is moving in
eighth notes; the others hold or punch.

## Harmonic language

- **Secondary-dominant chains** — the "ragtime progression": III7→VI7→II7→V7→I.
  My A strain runs I … V/ii (D7) … V/V (G7) … V (C7), the "Ja-Da"/"Bill Bailey" family.
- **Diminished passing chords**: ♯I°7 and ♯IV°7 between diatonic chords
  (B♭→B°7→F/C in the A strain; E♭→E°7→B♭/F in the trio).
- **Blue notes** in melody: ♭3 (A♭ in F) used as grace/crush into the major 3rd, ♭7 freely.
- **Added 6th** on tonic chords in melodies — the 1920s "sweet" sound.
- **The Dixieland tag**: I–VI7 / II7–V7 repeated three times with solo breaks
  (trombone, clarinet, trumpet), then the final cadence. Mandatory. Non-negotiable.

## Swing & humanization (MIDI craft)

- At ≈198 bpm swing is **light**, not hard triplet: offbeat eighths placed at ~57–58%
  of the beat, not 67%.
- Timing jitter ±8 ms equivalent, velocity jitter ±6, so nothing is machine-perfect.
- Accent map: melodic offbeat syncopations get +12 velocity; banjo beats 2/4 get +8.
- Strums: banjo chord notes staggered ~10 ms low→high.
- Trombone scoops: pitch wheel starts −2 semitones, releases to center over ~80 ms.

## Form vocabulary

Multi-strain march/rag architecture (like "That's a Plenty", "Muskrat Ramble"):
16-bar strains, a minor strain for contrast, then a **trio** in the subdominant
(F → B♭) where the solos and the shout choruses live. Breaks (2-beat to 2-bar holes
where one voice fills), stop-time for the trumpet solo, an out-chorus where the lead
jumps the octave, and the three-break tag to close.

## Ranges I'm holding myself to (concert pitch)

| Instrument | Floor | Ceiling | Sweet spot |
|---|---|---|---|
| Trumpet | E3 | B♭5 | F4–F5 |
| Clarinet | E3 | G6 | C5–E6 |
| Trombone | E2 | B♭4 | A2–F4 |
| Tenor sax | A♭2 | E5 | C3–C5 |
| Sousaphone | E1 | B♭2 | F1–F2 cores |
| Banjo | C3 | C5 voicings | around C4 |
