# Self-assessment

An honest accounting, as the goal asked for. Written after the build, with the
validation data in front of me.

## What works

**The form enacts the concept.** The unfinished-cadence premise isn't decoration —
it's structural. The motto withholds its resolution for three movements; the finale's
entire dramaturgy (storm → collapse → gathering → chorale → resolution-in-real-time →
dissolving coda) exists to earn one note. Cyclic recall is real: the motto appears in
every movement (assembled in I, mocked in II, majorized-but-denied in III, answered
in IV), the slow movement's A♭ returns to bless the finale's chorale, and the coda
mirrors the opening texture in major.

**The dynamic arc is verified, not hoped for.** The velocity/density profile of the
final MIDI shows exactly the planned shape: the trio's hush at ~7:00, the adagio's
interrupted climax at ~11:00, and the single loudest passage of the entire piece at
~17:00 (the apotheosis/resolution), falling to near-silence at the end. The loudest
moment and the structural climax coincide — that is the thing amateur orchestration
most often gets wrong, and it landed.

**Craft guards held.** Every melody line passed a bar-sum assertion (no drifting
meters — a failure mode I knew to expect from myself and engineered against). All
instrument ranges validated against conservative professional limits. 16 MIDI
channels exactly, percussion on channel 10, per-section pizzicato/arco switches
isolated per channel.

**Scale.** 18.6 minutes, ~13,000 notes, full symphonic roster. The ambition asked
for in the goal (15 minutes) was met with headroom.

## What a human composer would do better

**Dynamics inside sustained notes.** MIDI note velocity is fixed at the attack; real
crescendi on held brass chords are approximated by re-articulation or tremolo. A DAW
rendering with CC11 expression curves would breathe more.

**Counterpoint depth.** The textures are melody-dominated homophony, canon, and
layered ostinato. There is no true fugato; inner voices are sometimes harmonic
filler rather than independent lines. Brahms would frown — though he'd frown at most
first symphonies.

**Harmonic adventurousness.** The language is conservative late-Romantic (borrowed
♭VI, Neapolitan touches, diminished sequences). It serves the narrative honestly,
but there are few harmonies that would surprise a listener who knows the idiom.

**Rubato.** Tempo changes are block-level (section boundaries, one allargando).
A performance would bend phrases continuously.

**Timbre.** General MIDI string-ensemble and brass patches will flatten the
orchestrational detail (the celesta's first entrance in the third movement coda is
scored as a *moment* — on a cheap synth it will merely be a sound).

## Where I went up a meta level

The goal warned: "you are not typically trained for this shape of task." The honest
translation is that an LLM writing 13,000 notes free-hand will drift — rhythmically,
registrally, formally. So the work was structured to make drift impossible rather
than unlikely: a one-line DSL with bar-sum assertions, range guards that fail the
build, deterministic seeding, per-movement validation before assembly, and a final
dynamic-arc profile as a proxy for ears I don't have. Composition decisions stayed
human-shaped (themes written by hand, harmony chosen bar by bar); the machinery only
enforced that what I imagined is what got written.

## Verdict

It is a real symphony — formed, argued, orchestrated, and meant. It is not a great
symphony; it is a good first one. Its best qualities are architectural: the long
denial and late granting of one note, and an ending that chooses peace over triumph.
That ending — the apotheosis giving way to the quiet reassembly of the opening
darkness in major — is the passage I would defend in front of anyone.
