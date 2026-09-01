# Goal

Compose **"Cut Loose"** — a Dixieland piece in the form of a New Orleans
jazz funeral: the slow procession to the cemetery, the whistle, and the
second line home. Commissioned by Joel ("compose another Dixieland piece");
everything else is the composer's choice. Third piece on the shared `lib/`
toolkit, and the first for a band that *walks*.

The seed image is found (see `docs/01-inspiration.md`): the band is burying
its own cornet player. On the way out the front line plays the hymn with
his chair empty — clarinet, alto, trombone, sousaphone, two drummers, no
lead. At the grave the body is "cut loose", the grand marshal blows the
whistle, and the same hymn comes back as a strut at three times the tempo,
with the cornet on top as if he had only gone on ahead. One tune, two
lives. Deepen that before writing a note; don't trade it for something
easier or safer.

Explore the real idioms first. A jazz funeral has a strict two-part
grammar — the dirge (muffled snare, dead-march cadence, hymn tune with
heavy vibrato, the plagal "Amen"), the whistle and the snares coming on,
then the second line (street beat, two-beat sousaphone, riffing horns,
collective improvisation, breaks, the tag). The marching brass band is its
own instrumentation: no banjo, no piano — the horns are the harmony. Study
enough to honor all of it; the piece should sound like a band that has
walked people out for a hundred years, not a concert band doing a
tribute.

Then plan the scaffolding: the procession is the form. Decide what the
hymn does slow and what it does fast, exactly how the turn is staged (the
Amen, the silence, the whistle, the cadence, the sousaphone, the horns),
where the new strain enters, who leads each chorus, and how the cornet's
return is earned. Key moments and effects on paper first.

Then build it — the hymn, the strut, the ramble strain, the full brass-band
texture — and self-assess against the real thing: does the dirge grieve or
merely drag? Is the hymn recognizable when it comes back hot? Does the turn
land as an event? Does the second line dance?

## Tooling

- Build on `lib/` (see `lib/README.md`): define the brass band as a custom
  `Ensemble` in `src/band.py` (rosters are data; two percussion players
  are two instruments). Use the DSL, chord charts, figures, groove, and the
  assessment suite.
- Second-line idioms want piece-local helpers first (`src/street.py`):
  dirge cadence, street beat, sousaphone dirge halves and two-beat, riff
  backgrounds, obbligato and tailgate generators, the whistle. Promote to
  `lib/` only what proves general, with a test.
- Keep the working record in `docs/`, generate MIDI into `output/`,
  package via `tools/midi_to_piece.py`, render per `web/README.md`, and
  export the engraved score with `export_score.py`.

## Constraints

1. Four to five and a half minutes; one continuous piece with one tempo
   change that matters.
2. Marching brass-band instrumentation only: cornet, clarinet, alto sax,
   trombone, sousaphone, snare drum, bass drum with cymbal. No banjo, no
   piano — the horns must carry the harmony the way brass bands do.
3. The cornet is silent until the second line. Its first note must be an
   event.
4. The deliverable must be playable and *verified* — render it, measure
   the arc, check the package and the score in the web player.
