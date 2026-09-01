# Second-line idioms — what makes it sound like a jazz funeral

Working notes: the two grammars I am composing inside of (the dirge and
the second line), what a marching brass band is as an instrument, and how
each rule maps to something concrete in the MIDI.

## The two-part form

A New Orleans jazz funeral is one ritual with two musics:

1. **The procession** — from church to cemetery, walking pace, ♩ ≈ 60–70.
   Hymns and dirges: "Just a Closer Walk", "Flee as a Bird", "Nearer My
   God to Thee", "West Lawn Dirge". Major-key hymns played *as* dirges —
   heavy vibrato, long tones, the borrowed minor iv as the tear.
2. **Cutting the body loose** — at the grave the mourners let go. The grand
   marshal's whistle; the snare drummer tightens the snares; the drummers
   play the street cadence; the band turns for home.
3. **The second line** — up-tempo, ♩ ≈ 180–200 in the quarter (a fast
   two-beat), "Didn't He Ramble", "Bourbon Street Parade", "Joe Avery".
   Umbrellas, handkerchiefs, the crowd dancing behind the band.

The turn is the whole point and it is *staged*: silence, whistle, cadence,
bass line, horns. Nothing enters before its cue.

## The band that walks

Marching brass band, not a corner band: cornet, clarinet, alto (or tenor)
sax, trombone, sousaphone, **snare drum and bass drum as two players**.
No banjo, no piano — the harmony is the riffing horns and the sousaphone.
The bass drummer carries a cymbal mounted on the drum and plays it with a
coat hanger (the "chick" on 2 and 4). Neither drummer has a ride pattern
or a hi-hat; there is no kit.

In the MIDI: two percussion instruments in the roster, both on channel
10, each its own named track. Bass drum = GM 36, snare = 38, side-stick =
37, the mounted cymbal = a soft closed-hat (42) for the chick and a
crash (49) for section downbeats. The whistle is on the drum map: 72
long, 71 short (a real referee whistle in GeneralUser GS).

## The dirge

- **Cadence.** Bass drum on 1 and 3; muffled snare (snares loosened) in
  soft press-rolls: a buzz through beat 4 that swells into the next
  downbeat, a soft tap on 2. Choked cymbal on phrase downbeats only.
  MIDI: snare at pp–p velocities with 32nd-note buzz rolls
  (`figures.perc_roll`, unit 1/16 beat); the "muffled" quality is
  velocity and density, GM has no snares-off sample.
- **Sousaphone.** Half notes: root on 1, fifth on 3, a quarter-note walk
  into each new phrase. Heavy, slow, on the beat.
- **The hymn.** Quarters, halves, dotted quarters — a tune you could sing
  from a hymnal. Stated plainly first (alto sax lead, trombone tenor line,
  sousaphone, drums), then the last half again as **the cry**: clarinet
  an octave up, wide vibrato, the trombone doubling the climb below.
- **Vibrato is the grief.** CC1 (modulation wheel) drives the soundfont's
  vibrato LFO: measured on this soundfont, CC1 = 127 gives ≈ ±37 cents on
  every horn. The dirge lead runs CC1 ≈ 90–110; the second line runs it
  at 0. Same instruments, different lungs.
- **Smears.** The trombone slides into every phrase downbeat
  (`figures.smear_into` + `scoop`), slow and low.
- **The tear.** IV → iv (A♭ → A♭ minor in E♭): the melody's C falling to
  C♭. The single most jazz-funeral chord there is; used once per pass.
- **Amen.** Plagal cadence, IV → I, held; the snare roll swells and dies;
  the tempo lets go (rit.) into silence.
- **Swing in the dirge.** A real dirge has a dotted lilt; the write's
  light swing warp (0.58) at ♩ = 66 delays the eighth after a dotted
  quarter by ~70 ms. That is the lilt. Nothing is written straight.

## The second line

- **Street beat.** Bass drum: 1, the *and* of 2, 4 (the "boom — ba-boom"
  that is the Caribbean tresillo's cousin); cymbal chick on 2 and 4;
  snare: syncopated rolls and accents around the backbeat with press-roll
  pickups into 1 and a fill every fourth bar. Two-bar cells, rotated.
- **Sousaphone.** Two-beat: root on 1, fifth on 3, a walk into each
  four-bar phrase (chromatic from below for rising roots, from above for
  falling); four-to-the-bar walking when the out chorus lifts.
- **Riffs.** The brass-band engine is horns riffing behind the lead:
  offbeat chord-tone stabs on the *and* of 2 and 4, or the Charleston
  (1, and-of-2). Voice-led, never leaping.
- **Collective improvisation** — the Dixieland rule: cornet leads in the
  middle (F4–G5), clarinet fills its holes above (E♭5–G6), trombone
  connects roots below (B♭2–F4) with smears. At any moment at most one
  front-line voice moves in eighths.
- **The obbligato** mixes four run types (this is where Royal Street
  Rattler's generator was thinnest): chord-tone arpeggios, scale
  passages in the chord's scale (mixolydian on dominants), triplet turns
  on a chord tone, and chromatic enclosures into the target.
- **Stop-time and breaks.** Band hits beat 1 only while a horn talks; a
  full-bar break with the band silent is how a soloist is *introduced*
  — the cornet's entrance is exactly that.
- **Shout chorus.** The tune in block harmony (three horns, chord tones
  above and below the lead) in call-and-response with the snare drum —
  the horns shout two bars, the drummers answer two beats.
- **Tempo.** A second-line band pushes: ♩ = 190 for the strut, 196 from
  the shout chorus on. MIDI tempo events, no fake.
- **Swing.** Light and fast: offbeats at 58 % of the beat, not triplets.
- **The tag.** Everyone plays the head in octaves, hits on I–VI7–II7–V7,
  one bar of drums, the final chord with the clarinet trilling on top.

## Harmony

- Hymn in E♭ with the hymnal's chords: I, IV, V7, the V7/IV → IV → iv
  tear, and the C7 → F7 → B♭7 rag chain in the last phrase, which is
  what lets the same tune strut later without changing a note.
- Ramble strain in A♭ (the subdominant, the trio convention), with its
  own tear (D♭ → D♭ minor) so the second half rhymes with the first.
- Blue notes in the hot choruses: the ♭3 crush, the ♭7 freely, chromatic
  walk-ups into chord roots (G–A♭–A–B♭).

## Ranges held to (concert pitch, GM)

| Instrument | Floor | Ceiling | Where it lives |
|---|---|---|---|
| Cornet (56) | F♯3 | D6 | F4–G5 lead; B♭5 at the peaks |
| Clarinet (71) | E3 | G6 | E♭5–F6 filigree; G6 twice |
| Alto sax (65) | D♭3 | A♭5 | E♭4–F5 hymn; riffs G4–E♭5 |
| Trombone (57) | E2 | B♭4 | B♭2–F4 |
| Sousaphone (58) | E♭1 | E♭3 | B♭1–B♭2 two-beat; E♭1 for the last chord |
