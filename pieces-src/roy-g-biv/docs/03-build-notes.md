# Build notes — what it took to draw with an orchestra

## What worked first try

The arch. Parallel elliptical arcs sampled per rhythm slot, snapped to
F major, each stripe 2k diatonic steps below the choir — the very first
render was recognizably a rainbow with the bands in spectral order. The
geometry doc (docs/02) paid for itself: no landmark needed moving.

## What the roll taught me about ink

Three renders of iteration, all on the same lesson: **a note's visual ink
is its duration × stroke width, and the eye needs connected ink.**

1. *Sub-pixel rain.* A 0.13-beat pizzicato is 0.7 px wide — invisible.
   Pizzicato decays the same regardless of written length, so drops
   became 0.26-beat notes purely for the camera. Musically identical.
2. *Dotted lightning.* A run stepping 3 semitones per note leaves 19-px
   vertical gaps between dashes — a ghost, not a bolt. The fix was the
   opposite of intuition: *smaller* pitch steps, *faster* notes.
   Chromatic 64ths (1 st per 31 ms) with overlapping durations render as
   a solid jag — and sound *more* like lightning, not less.
3. *Disconnected streaks.* Rain streaks falling by pentatonic steps
   (3–4 st) scattered into specks; falling by scale steps (1–2 st) they
   became legible diagonal strokes. Steeper is not always more readable.

Same-family unison doubling (guitar + harp on the bolt) multiplies
opacity: alpha compounds to ~0.95 and the bolt reads *bright*.

## lib extensions

`assess.pianoroll` gained two backwards-compatible params: `legend_loc`
(the legend sat exactly on the outro's ground line; it now floats in the
empty sky above the crown) and `lw` (1.6 px lines read as pencil; 2.4 px
reads as crayon, which is the register this drawing wants). `lib.tests`
still 12/12.

## Things the picture forced on the music (all improvements)

- **One tempo.** x = seconds needs a linear ruler; 120 bpm throughout.
  The genre absorbed it — struts don't rubato.
- **Staggered entries/exits hidden in clouds.** The fan-in of seven
  voices would smear the arch's feet, so gray tremolo blobs sit exactly
  there — which is also where a kid draws the clouds. The compromise IS
  the iconography.
- **The ground must never stop.** A picture's horizon can't blink out,
  so the bass plays through the drum break (soft quarter taps) and under
  the sun (pale pulses). Continuity of line = continuity of groove.
- **No stop-time breaks.** A two-beat tutti rest would cut a white slit
  through all seven bands. The shout choruses stay dense; the kit
  carries the punctuation instead, invisibly.

## Verification

- `assess.report`: all 12 instruments in range, 5,072 notes, 3:08.6.
- Rendered WAV (FluidSynth + GeneralUser GS, -g 0.42): peak −1.6 dBFS,
  no clipping; tail trimmed to 189.8 s.
- Measured RMS matches the designed arc: drizzle (−40) → thunder spikes
  (−14, the loudest instants in the piece, exactly at the bolts) →
  rainbow plateau (−21) → outro pocket (−30) → sun glow (−34).
- Web package verified in the player: sync at seek, sections firing,
  ROYGBIV instrument colors, minimap constellation shows the whole
  drawing. Console clean.
