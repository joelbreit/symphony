# Tango idioms — the study

What the quintet actually does, gathered before writing a note. Each idiom
ends with *(MIDI)*: how it maps onto `lib/`. The bar is goal.md's: "tango
played by people who have played tango all their lives."

## The accompaniment vocabulary

Tango has no drummer. Time lives in the bass and the piano's left hand, and
it comes in a small number of named feels — arrangers call them out like
chord symbols:

- **Marcato in 4** (*marcato en cuatro*): even quarter notes, all four
  beats, detached and weighted — 1 and 3 heavier than 2 and 4. Not a walking
  bass: no passing tones, chord roots and fifths, the tread of something
  heavy and certain. *(MIDI: bass + piano LH octaves, gate ≈ 0.6, velocity
  pattern f‑mf‑f‑mf, straight — never swung.)*
- **Marcato in 2** (*en dos*): only 1 and 3, half-note weight. The lyrical
  sections breathe over this. *(MIDI: same, half notes, gate ≈ 0.8.)*
- **Síncopa**: the anticipation figure — the offbeat before the strong beat
  is accented and the strong beat itself is ghosted or tied over. The
  classic cell hits on 1, the *and* of 1, then lands on 3 (D–s–D): weight,
  stumble, catch. *(MIDI: hits at +0.0, +0.5, +2.0 beats, accent the +0.5.)*
- **3‑3‑2** (*el tres tres dos*): eight eighth-notes split 3+3+2 — attacks
  on 1, the *and* of 2, and 4. Piazzolla's engine (Libertango's bass is
  exactly this). It is a rhythm that never stops falling forward — which is
  this piece's whole thesis. *(MIDI: hits at +0.0, +1.5, +3.0; chain bars
  so the pattern grinds.)*
- **La yumba**: Pugliese's grind — beats 1 and 3 slammed with an arrastre
  scrape into each, 2 and 4 almost silent. Named for the sound. Use for the
  heaviest passes. *(MIDI: accented low cluster + scoop into 1 and 3,
  velocities ~f/pp alternating.)*
- **Arrastre** ("the drag"): a smear that starts before the downbeat and
  crashes into it — bass slides up from below, piano runs a fast chromatic
  ramp. It is the sound of weight arriving. Tango places it at phrase
  starts, especially returning to marcato. *(MIDI: `figures.scoop` on the
  bass note at the barline; piano gets 3–4 rising chromatic sixteenths into
  beat 1 — `figures.smear_into` is exactly this.)*

## The band and its roles

The Piazzolla quintet is five soloists in fixed jobs:

- **Bandoneón** — the voice and the lungs. Carries the main melody;
  phrases swell and collapse mid-note because the bellows never stop
  moving. Also stabs chords with both hands in rhythmic sections. *(MIDI:
  GM 23 "Tango Accordion". Every held note ≥ 1 beat gets a CC11 shape —
  attack mf, dip, swell, release. A bandoneón line with flat CC11 is dead;
  goal.md makes this a constraint, not a nicety.)*
- **Violin** — the second voice: countermelodies, sighing portamento
  descents, duets in thirds/sixths with the bandoneón — and the *yeites*
  (noise effects, below). *(MIDI: GM 40; `figures.scoop` for portamento
  entries, CC11 swells on long notes.)*
- **Piano** — both hands in the rhythm (LH doubles bass in octaves, RH
  comps middle-register chords on offbeats or síncopa), arrastre runs,
  and takes the melody for one lyrical stretch if the piece has one.
  *(MIDI: GM 0; pedal (CC64) only in lyrical sections — marcato is dry.)*
- **Electric guitar** — Piazzolla's quintet color: dry, close, plucked.
  Arpeggiated ostinati in slow music, crisp offbeat comping in fast,
  the occasional solo break. *(MIDI: GM 26 jazz guitar — already dry;
  `figures.strum` for rolled chords, tight gate for comping.)*
- **Double bass** — the floor. Marcato, arrastre slides, occasional
  two-feel. In this piece the bass *is* gravity; its silence in the coda
  is the point. *(MIDI: GM 32; pizzicato is the patch's nature — fine,
  tango bass is played both ways; scoops for arrastre.)*

## Yeites — the noise effects

Percussion without a percussionist; the players attack their instruments.
Used sparingly, they are tango's punctuation:

- **Chicharra** ("cicada"): violin bowed behind the bridge — a pitchless
  scratch in eighth notes. *(MIDI: no true equivalent — approximate with
  cabasa/maracas ticks pp on the golpe channel, or skip.)*
- **Tambor** ("drum"): violin left-hand-muted snap, a dry pop. *(MIDI:
  rim shot (37) doubled with a short low violin pizz-like note pp.)*
- **Látigo** ("whip"): a fast rising glissando cracking into a downbeat.
  *(MIDI: quick chromatic run up in the violin, or a bend released at
  the target.)*
- **Golpe** ("knock"): rapping the instrument body — bandoneón lid,
  guitar top. *(MIDI: woodblocks 76/77 + rim 37 on a percussion channel,
  soft, sparse. This piece's "telemetry" ticks live here.)*

## Melody: cantando vs. rítmico

Every tango melody is one of two species, and Piazzolla's forms alternate
them:

- **Cantando** (singing): long lines, appoggiaturas leaning on strong
  beats and resolving down, portamento entries, rubato against a steady
  accompaniment. Phrases arch in 4-bar units, question then answer.
- **Rítmico** (rhythmic): angular, staccato, repeated notes, the melody
  snapped onto the marcato or síncopa grid. The same tune can be recast —
  arrangers do exactly this between choruses.

Ornaments are constant and small: **mordents** (note–lower neighbor–note,
fast, on the beat), **turns/gruppetti** (four-note curl into the next
note), **acciaccaturas** (crushed grace a semitone below). More ornament =
more intensity; a tune returning "ornamented harder" is idiomatic
escalation, which is exactly the decay scheme this piece needs. *(MIDI:
piece-local `mordent()` / `turn()` helpers writing ~1/8-beat grace notes,
swing=False.)*

## Harmony

- **Minor with a Phrygian lean.** The workhorse cadence is iv–V7(♭9)–i;
  the ♭9 over the dominant (F over E7 in A minor) is *the* tango pain
  interval. Melodies sit on it, resolve late.
- **The descending tetrachord** — A–G–F–E bass, i–♭VII–♭VI–V — is tango's
  gravity well (and the Andalusian cadence's cousin). "Verano Porteño"
  leans on it; so will Perigee, literally: it is the orbit losing altitude.
- **♭II (Neapolitan) as color**: B♭ major over or beside A minor — the
  "Phrygian lean" — approached directly, often B♭→E7, tritone bass drop.
- **Piazzolla extensions**: m9, 7♭9, 13, maj7 with #11 color, planing
  chords chromatically under a pedal, sequences rising by minor thirds
  (his favorite ratchet — Perigee's perigee-to-perigee key plan).
- **The ending**: the **chan‑chan** — two final chords, dominant → tonic,
  short, dry, both accented, after the last phrase has already finished.
  Every tango in the tradition ends with this stamp. Perigee ends with the
  quietest one ever played.

## Rhythmic feel

Straight eighths, always — tango never swings. The elasticity lives
elsewhere: melodies drag behind and rush ahead of a metronomic
accompaniment (write the rubato into note placement, not the tempo map),
and whole sections push/pull tempo (the tempo map's job). Fast nuevo
tango sits around ♩=120–152; lyrical sections ♩=56–80.

## Form (Piazzolla's shapes)

Sectional, hard-cut contrasts: a driving rítmico block, a suspended
cantando middle, the drive again, coda. "Adiós Nonino" alternates elegy
and dance; Libertango is a single ostinato arc. Fugato openings
("Fuga y Misterio") stack entries then slam into homophony. Freezes —
the whole band cutting to silence mid-phrase — are idiomatic and land
hardest right before an ending. Perigee's orbital form (shrinking apogees,
growing perigees) is a Piazzolla alternation with a physics engine
deciding the proportions.
