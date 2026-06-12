# Self-assessment — "High Street Riot"

## What I was aiming at

A vamp that drips catchiness, played by a band that's too big, getting angrier the way the
High Street Jazz Band got angry: joyfully. The structural bet was that one two-bar riff
could carry 124 bars if the *orchestration* keeps moving — accumulate, shout, strip, rebuild,
argue, stomp, collapse, riot, wink.

## Measured results (src/assess.py)

The loudness arc came out exactly as drawn on the blueprint:

| | dB (mean RMS) | |
|---|---|---|
| shrug → wail | -30.1 → -20.3 | one long ten-bar-block crescendo, no dips |
| floor drop | -29.8 | a real valley, back to the opening's level |
| solos → argument | -25.7 → -21.7 | second slow build across three soloists |
| collapse | -27.0 | second valley |
| **riot** | **-18.7** | the loudest music in the piece, where it belongs |
| wink | -31.6 | ends quieter than it began, then one fat G |

All instrument ranges check out (cornet D4–D6, clarinet G4–E6, sax F3–D5, bones to A4,
sousa G1–A3, peak 0.83 — no clipping). 3:08 long. The sousa's brief A3s are the riff
transposed to D at the climaxes — the tuba player wails too; that's the whole point of
the band.

## What works (honest version)

- **The riff survives 60+ repetitions.** It transposes (G→C→D as the anthem's changes),
  it thins (two-beat under solos, returning as the "wrap it up" signal), it climbs
  (8va in the bones for the riot), and it gets the last word alone in bar 122.
- **The interlock.** Horn stabs land in the riff's breaths (beat 2 of each bar), so the
  shout choruses gear-mesh instead of mudding. Visible in the pianoroll; audible.
- **The anger is placed, not sprayed.** The ♭5 (D♭ over G) is in the riff's DNA from
  bar 1; the melody syncs onto it in the wail; the A♭9 riot chord is withheld until
  bar 86, then abused; the E♭–A–D cluster hammers (quoted straight from the original
  transcription's m14) only fire at the climax. Dissonance lands ON beats, resolved late.
- **The pincer.** The anthem's last gesture — melody leaning A♭ from above while the
  bass pushes F♯ from below, both collapsing onto G — is the single best bar of theory
  in the piece and it's also just *singable*.
- **Band-as-characters.** The trombone interrupts the sax two beats early in the
  argument. The clarinet photobombs the cornet solo. The pads creep in behind the
  trombone because nobody in this band can lay out for twelve whole bars. These are
  transcription-of-behavior, not just notes.

## What's approximated (MIDI is MIDI)

- Tailgate smears are fast chromatic runs, not true glissandi — no pitch-bend events.
  Real bones would smear continuously; GeneralUser GS renders the runs convincingly
  at tempo, but it's an idiom impression.
- No plunger/growl timbres available in GM — anger is carried by register, dissonance,
  velocity, and rhythm instead. (It carries.)
- Swing is a fixed-ratio offset (+0.12q) with small jitter, not phrase-aware rubato.
  At 160bpm the lighter ratio is correct, but a live band would lean harder into
  the snarl bar.
- The drum break (bars 93–96) is written, not played — it's the most "composed"
  improvisation in the piece.

## If there were another pass

1. Real pitch-bend glisses for the bones and a falloff curve for the cornet screams.
2. A second strain — the original band would eventually have stumbled into a bridge.
3. More banjo variation (passing-chord chromatics on bar 4s of phrases).
4. A room-mic impulse response; the GM render is dry-ish even with CC91.

## Verdict

It does the thing the goal asked: it's catchy enough to whistle after one listen
(the riff *and* the anthem), it's grotesquely fun, it builds like the original jam
built, and it ends with a wink instead of an apology. I'd play this one at the end
of the setlist.
