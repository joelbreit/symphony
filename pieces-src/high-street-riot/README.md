# High Street Riot

A vamp-jam for an oversized Dixieland band — 124 bars, ~3:08, G minor, 160bpm swung.

*It's the end of the setlist in Morgantown and the band is out of songs. The sousaphone
drops a riff so greasy the streetlights flicker, and eight people who are way too many
people for improv jazz each decide they are, personally, the lead.*

Written after **"G Minor Jam"** by The High Street Jazz Band — the no-melody, follow-the-tuba,
make-it-angry vamp this project's [g-minor-jam.mxl](g-minor-jam.mxl) transcribes. Nothing is
quoted except the things that mattered: the chromatic walk-ups, the ♭5 snarl over G, the
stacking-thirds build, and the hammered E♭–A–D cluster at the boil.

## Listen

```sh
open output/high_street_riot.m4a        # rendered audio
open output/high_street_riot.mid        # the playable score (GM MIDI, 8 tracks)
```

Also in the listening-room gallery (`symphony/web`, `#/high-street-riot`) with piano-roll
playback, section narration, and the riff as a transforming emblem.

## The band

Sousaphone (the leader) · Trombone ×2 (the muscle) · Cornet (the ego) ·
Clarinet (the shrieker) · Tenor sax (the transfer student) · Banjo (the floor) ·
Drums (the crowd)

## The riff

Two bars, looped basically forever, and it earns it:

```
the strut up:    G . . G  Bb C C# D      (breath after the downbeat, blues-third climb)
the snarl down:  D . . Db C Bb C F#      (the b5 leans in; F# hooks back into the loop)
```

It transposes (G→C→D becomes the anthem's changes), thins to two-beat under solos,
jumps the octave for the riot, and gets the last word alone.

## The shape

| Time | Bars | Section |
|---|---|---|
| 0:00 | 1 | The shrug — sousa alone, riff born fully formed |
| 0:06 | 5 | The pile-on — drums sneak in, banjo, bones laddering 3rds |
| 0:18 | 13 | The shout — horn stabs interlock with the riff's breaths |
| 0:30 | 21 | The wail — the anthem, screamed over Gm–Gm–Cm–D7♯9 |
| 0:42 | 29 | The floor drop — naked vamp |
| 0:48 | 33 | Trombone lead → 1:06 cornet lead → 1:24 clarinet lead (over iv) |
| 1:42 | 69 | The argument — trading twos that stop taking turns |
| 2:00 | 81 | The stomp — stop-time; the A♭9 riot chord starts swinging |
| 2:18 | 93 | The collapse — choke, drum chatter, sousa mutters back in |
| 2:24 | 97 | The riot — riff 8va + anthem on top + cluster hammers + A♭9→Gm slams |
| 3:00 | 121 | The wink — dead stop · sousa snarl lick alone · two stabs · one fat G |

## Files

- [output/high_street_riot.m4a](output/high_street_riot.m4a) — rendered audio
- [output/high_street_riot.mid](output/high_street_riot.mid) — GM MIDI, 8 tracks
- [output/leadsheet.abc](output/leadsheet.abc) — the riff + the anthem (ABC notation)
- [output/pianoroll.png](output/pianoroll.png) — full-piece visualization + measured loudness arc
- [src/compose.py](src/compose.py) — the score generator (music21): riff/anthem/solos
  hand-composed note-by-note; banjo/drums/smears/curls by small constrained generators;
  swing + humanization post-pass; pan/level CCs via mido
- [src/assess.py](src/assess.py) — pianoroll, RMS-vs-design check, range checks
- [docs/](docs/) — inspiration, blueprint, self-assessment

## Rebuild from source

```sh
python3 -m venv .venv && .venv/bin/pip install music21 mido numpy matplotlib
.venv/bin/python src/compose.py          # → output/high_street_riot.mid
fluidsynth -ni -g 0.72 -F output/high_street_riot.wav -r 44100 \
    ../../soundfonts/GeneralUser-GS.sf2 output/high_street_riot.mid
.venv/bin/python src/assess.py           # → pianoroll.png + checks
```
