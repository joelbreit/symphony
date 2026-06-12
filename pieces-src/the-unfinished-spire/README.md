# The Unfinished Spire

*An Anthem for Builders* — for full orchestra. E♭ major, 4/4, ≈ 6 minutes.

An anthem for the builders of things they will not see finished: a cathedral
site at first light, c. 1300. The masons who laid the foundation are forty
years dead; the children who will set the capstone are not yet born. The
answer the piece argues for: **the building is the cathedral.**

## Listen

- **[out/anthem.m4a](out/anthem.m4a)** — rendered audio (GeneralUser GS soundfont)
- **[out/anthem.mid](out/anthem.mid)** — the playable score (16-channel GM MIDI;
  open in any DAW, notation app, or synth — sounds best with a good orchestral
  soundfont or sample library)
- `out/anthem.wav` — uncompressed render

## The shape

| time | section | |
|------|---------|---|
| 0:00 | I. Dawn | mist over the site; the Summons (solo horn) |
| 0:54 | II. The Anthem | the 16-bar hymn — horns and celli, then tutti |
| 1:57 | III. The Work | C-minor motor; the Summons in stretto — many hands |
| 2:36 | IV. The Single Voice | solo oboe: the Doubt theme. *Will any of this matter?* |
| 3:26 | V. The Long Night | lament ground bass; the call, inverted, failing |
| 3:53 | — | one full bar of silence |
| 3:56 | VI. The Sunrise | B♭7 resolves deceptively to C♭ major; the first bell |
| 4:19 | VII. Apotheosis | the Anthem fff — **with the Doubt theme inside it as counterpoint** |
| 5:10 | VIII. Coda | pealing hemiola; the far-off horn; the blaze; one bell rings last |

The structural promise: the oboe's private song in IV was composed against the
anthem's harmony all along, so at VII the two combine — the private voice was
part of the hymn the whole time.

## Rebuild from source

```sh
python3 -m venv .venv && .venv/bin/pip install midiutil matplotlib numpy
.venv/bin/python src/compose.py        # -> out/anthem.mid
.venv/bin/python src/analyze.py        # -> piano roll + dynamics plots
fluidsynth -ni -g 0.45 -r 44100 -F out/anthem.wav \
    assets/GeneralUserGS.sf2 out/anthem.mid
```

- [src/score.py](src/score.py) — composition framework (absolute-beat placement,
  tempo map, hairpins, humanization, hard range validation per instrument)
- [src/compose.py](src/compose.py) — the piece, one function per section
- [src/analyze.py](src/analyze.py) — piano roll, dynamic-arc and density plots
- [docs/](docs/) — inspiration → materials → structure → self-assessment trail
