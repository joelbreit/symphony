# Self-assessment — Royal Street Rattler

## What I verified (measured, not vibes)

- **Length**: 185 bars at 198 bpm = 3:44 of music (3:55 with reverb tail). Meets the
  "few minutes" brief.
- **Dynamic arc** (RMS per section, normalized): heads sit at ~0.72–0.82, the three solos
  step *upward* (clarinet 0.54 → sax 0.62 → trumpet 0.70) — an intensity ladder, exactly
  the shape I wanted — drum break drops to 0.25 as the breath before the finale, shout
  0.81, **out chorus is the loudest moment of the piece (1.00)**, tag 0.75. No clipping
  (peak 0.73).
- **Swing**: trumpet offbeat eighths cluster at 55–60% of the beat (target 57.5%);
  downbeats clean on the grid. Light fast-tempo swing, not stiff straight eighths.
- **Ranges**: every instrument inside its real-world playable range (trumpet caps at B♭5
  and touches it exactly twice, at the solo peak and the final chord — where a lead
  player would actually go).
- **MIDI hygiene**: zero same-pitch overlapping notes on melodic channels (fixed three
  classes of collisions: a doubled final-chord clarinet note, generator-vs-pickup
  collisions, stab tails).

## What works musically

- **Motivic unity.** The rattle cell (three repeated eighths → offbeat leap, held) opens
  the piece *as percussion*, builds the A strain, reappears in the trombone's minor
  strain, gets quoted by every soloist once, caps the trio melody, and is the full-band
  unison figure that launches the out chorus and ends the tune. The piece is *about*
  something.
- **Real Dixieland texture rules.** At most one front-line voice moves in eighths at a
  time; clarinet lives above the trumpet and fills its holes; trombone connects roots
  with smears and scoops (actual pitch-bend events, not just notes).
- **Form does the storytelling.** Strain keys (F → Dm → B♭) and the texture changes
  (stop-time, breaks, walking-tuba lift in the last 8 of the out chorus) carry the
  streetcar narrative without needing program notes.
- **The ending is earned**: three-break tag (trombone → clarinet → trumpet, each two
  beats of fame), full-band rattle, two short hits, held chord with clarinet trill and
  cymbal — then the sousaphone plop. It lands like a grin.

## What I'd do with another session (honest list)

- **The obbligato generator is good, not great.** Its runs are always chord-tone
  arpeggios in even eighths; a human clarinetist would mix in scale passages, triplet
  turns, and more chromatic enclosures. The hand-written solo choruses show what the
  generated filigree should sound like.
- **GM "banjo" reads more bluegrass than plectrum-banjo.** A 1920s four-string chunk is
  drier and woodier. Mitigated with short durations and modest velocity, but the timbre
  is the soundfont's, not mine.
- **No piano.** Defensible (street-band instrumentation — banjo *is* the comper), but a
  second harmonic voice would thicken bars where the front line breathes.
- **Drum language is approximated.** Real press rolls are buzz strokes, not five fast
  hits; GM has no brushes-on-calfskin. The woodblock-forward writing is the right
  period flavor and covers some of this.
- **Tempo is constant 198.** A real band would push the shout chorus a hair (+2-3 bpm)
  and lean back into the tag. MIDI tempo events could fake this; I chose stability.

## The meta-level check the brief asked for

The trap for an LLM in this task is writing "music-shaped data" — correct chords,
plausible rhythms, no point of view. My defenses were: (1) commit to one concrete image
before writing a note, and let it pick the hook, the form, and the cast; (2) hand-compose
every melody, solo, and the tag note-by-note, using generators only where real bands use
formula (comping, two-beat bass, guide-tone counterlines); (3) verify the things I can't
hear — energy arc, swing placement, register collisions — with measurement instead of
hoping. The result has an identity I can describe in one sentence: *a streetcar's rattle
taught to strut.* That's the test of whether it's a composition rather than output.
