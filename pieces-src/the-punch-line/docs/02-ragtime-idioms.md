# Ragtime idioms — the written language

The study doc: what classic ragtime actually is on paper, and the concrete
decisions this piece inherits from it. Sources of truth: the classic-rag
trinity (Joplin, James Scott, Joseph Lamb), the roll catalogs (QRS), and the
stride school the commission names (Johnson, Waller) for the left hand's
swagger.

## 1. The form

Classic rags are **multi-strain marches**: three or four 16-bar strains,
each repeated, with a key change at the **trio**. The canonical floor plans:

- Maple Leaf Rag: `A A B B A C C D D` — A/B/D in A♭, trio C in D♭ (IV).
- The Entertainer: `Intro A A B B A C C Intro' D D` — C, trio in F.

Structural laws worth keeping:

- **16-bar strains** in four 4-bar phrases, usually `a a' b a''` or
  `a b a c` — a tune, its echo, a contrast, a cadence.
- **A is the best tune.** The first strain is the hit single; B is busier
  and brighter; the A return is a literal callback; the trio is the change
  of scene — warmer, more lyrical, subdominant; D is the rideout, the
  strongest rhythmic energy.
- **Intros are 4 bars**, both hands in octaves, ending on V7 with a breath
  before the downbeat of A.
- **Repeats are varied on rolls.** A human reading sheet music repeats
  verbatim; a roll arranger re-punches the repeat an octave up, adds fills,
  thickens the texture. This piece treats every repeat as a variation —
  that is both roll practice and basic listening mercy.

## 2. Meter and tempo

- **2/4**, the march's meter. The melodic grid is the **sixteenth note**;
  the left hand moves in eighths.
- Joplin's law, printed on his scores: *"It is never right to play Ragtime
  fast."* Period tempo for classic rags: quarter ≈ 88–104. This piece:
  **96** — with a hair of machine-crank push (≤ +4) allowed in the doctored
  finale only.
- Ragtime is **straight**, not swung. Swing came later; rolls especially
  play dead-even sixteenths. (In `lib` terms: `write(swing=None)` — and the
  keys-family humanize profile is already pianola-tight.)

## 3. The left hand — the law

The oom-pah is a **register machine** with three zones:

| Zone | Range | Job |
|---|---|---|
| Bass notes | A♭1–E♭3 | beats 1 and 2 ("oom"): roots and fifths, often octaves |
| After-beat chords | ~G3–G4 | the "&" of each beat ("pah"): 3–4 note close voicings |
| (Melody stays above) | C4 upward | never colliding with the chord zone |

Grammar rules:

- **Bass on the beat, chord off the beat**: `oom-pah oom-pah` per bar.
  Root on beat 1; fifth (or root again, or a passing tone) on beat 2.
  Octave basses on strong arrivals, single notes when light.
- **The chord is dry**: short (staccato-ish, gate ≈ 0.55), quieter than
  the bass (≈ −12 velocity). The bass rings slightly longer.
- **Walking octaves** (stride's contribution): broken-octave scalewise
  runs in eighths connecting one harmony to the next, replacing a bar's
  oom-pah at phrase seams. Also the **broken tenth** — bass note then the
  tenth above it as a quick roll — where a plain octave is too plain.
- **The left hand never syncopates.** Its whole job is to be the
  expectation the right hand violates. The one sanctioned deviation:
  **stop-time** — the grid stops entirely, stabs on downbeats only
  (Joplin's *Stoptime Rag* fills the silence with foot stomps). Stop-time
  is the pause before the punch line, and must be rationed to keep its
  power.
- Simultaneous span ≤ a tenth; the hand alternates zones, it does not
  stretch across them.

## 4. The right hand — the wit

The syncopation vocabulary, in order of spice:

1. **The snap** (short-long-short): `s e s` filling one beat — the
   cakewalk cell, ragtime's atomic joke. The long note falls *off* the
   grid and gets the weight.
2. **The tie over the beat**: an off-beat sixteenth held across the next
   beat, so the following downbeat is silent in the melody while the left
   hand marks it — the deadpan held one beat too long.
3. **The secondary rag**: accents every 3 sixteenths against the 4-grid
   (3+3+2, or 3+3+3+3+2+2 across two bars) — the escalation device, the
   joke told faster than the audience can nod. Save it for B and D.
4. **Treble octaves with inner notes** — the fortissimo register of the
   style; and **parallel thirds/sixths** — its warmth (the trio lives in
   sixths).
5. **The crush** (acciaccatura): a semitone grace note crushed into the
   main note — ragtime's wink. Written as a real sounded note per house
   rules (~60 ms before the beat).

Melodic conventions: chord-tone skeletons ornamented with chromatic
neighbors and passing tones; phrases that outline the harmony (the ear must
never need the left hand to know the chord); the melody breathes in 2-bar
units with rests — rags are airy, not moto perpetuo.

## 5. Harmony

Classic-rag diatonicism with period spice, roughly in order of frequency:

- **I, V7, IV** carry 80% of the weight; harmonic rhythm one chord per
  bar, two in cadence bars.
- **Secondary-dominant chains**: `III7 → VI7 → II7 → V7 → I` (the rag/
  barbershop cycle) — the standard second-half-of-strain engine.
- **The chromatic passing diminished**: `IV → ♯IVdim7 → I/5` — the single
  most ragtime-sounding progression that exists.
- **♭VI7 → V7** as the dramatic approach; **V7/IV** to tilt into the
  subdominant; the trio simply *is* IV major.
- Cadence formula: `I/5 – VI7 – II7 – V7 – I` over the last four bars.
- **Keys**: the school lived in flats. Here: **A♭ major**, trio in
  **D♭**, per the Maple Leaf floor plan.

## 6. Texture and playability discipline

- Two voices minimum, four typical: melody (often octave-doubled),
  after-beat chords, bass. The texture *is* the instrument's whole range
  in constant alternation.
- RH simultaneous span ≤ an octave (occasional ninth/tenth rolled);
  LH ≤ a tenth broken.
- Same-pitch re-articulations need real gaps (the lib overlap-trimmer
  guards this, but write honest gates anyway).
- **Pedal almost never.** Ragtime is a dry style — the left hand supplies
  the legato illusion. Sanctioned uses: under the trio's lyrical bars
  (half-bar dabs), and under the final rolled chord.
- Grace notes, rolls (chords arpeggiated bottom-up ~20 ms/note), and
  tremolos are written as sounded notes.

## 7. The player-piano layer

What the roll practice contributes, historically and to this piece:

- **Dead-even time.** Rolls do not rubato. The `lib` keys profile
  (±6 ms) is exactly right; no tempo maps inside strains.
- **Varied repeats** (§1): the arranger's re-punch is the model for every
  second pass here.
- **Doctoring.** QRS arrangers — J. Lawrence Cook above all — punched
  extra notes into "hand-played" rolls: melody doubled an octave up,
  filler thirds tremolo'd in the middle register, bass octaves thickened,
  runs no hand could reach in time. A four-hand arrangement sold as two.
  The public knew, and didn't care, and the fraud became the style.
- This piece's license (from `goal.md`): **doctoring is confined to the
  final strain** (D′), where it escalates from plausible (octave
  doubling) through improbable (doubling + sustained filler thirds) to
  frankly impossible (three registers of melody, five-octave runs), as
  the literal punch line. Everything before D′ must be honestly playable
  by ten fingers.

## 8. Decisions locked for this piece

| Question | Decision |
|---|---|
| Meter / grid | 2/4, sixteenth grid (`s` = 0.25 beats; one bar = 2 beats) |
| Tempo | 96 quarter; flat inside strains; ≤ +4 crank in D′ only |
| Swing | none — `write(swing=None)`; straight sixteenths |
| Keys | A♭ (intro, A, B, D); D♭ (trio C); retransition on E♭7 |
| Form | Intro A A′ B B′ A″ int C C′ pause D D′ tag (~158 bars ≈ 3¼ min) |
| Humanize | lib default (keys are tight = pianola) |
| Pedal | trio dabs + final chord only |
| Ending | shave-and-a-haircut, fully orchestrated — the oldest punch line in music |
| Guards | every strain `B(dsl, n, meter=(2, 4))`; stride helper asserts bar counts |
