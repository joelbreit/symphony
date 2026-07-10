# Soundscapes — build

Loopable ambient scenes for the web player's soundscapes tab — focus and
motivate so far; relax and sleep planned (docs/03). See
`goal.md` for the brief, `docs/` for the creative record.

```sh
cd pieces-src/soundscapes
../../.venv/bin/python src/compose.py              # all stem MIDIs -> output/midi/<scene>/
../../.venv/bin/python src/compose.py focus/bed-a  # just one stem
../../.venv/bin/python src/export_web.py           # render audio + manifests -> web/public/soundscapes/
```

`export_web.py` needs fluidsynth + afconvert and a GM soundfont — it defaults
to `pieces-src/the-unfinished-spire/assets/GeneralUserGS.sf2` (override with
`--sf2` or `$SF2`).

Layout: `src/palette.py` scene ensembles (data), `src/loopcraft.py` the
loop-stem harness and its fail-fast seam guards, `src/scene_<id>.py` one
builder per stem variant, `src/compose.py` the conductor.

Each manifest variant also carries `notes` — the stem's score events as
`[startSec, durSec, pitch, vel]` (same bars·60/bpm arithmetic as
`loopSeconds`) — feeding the player's visualizations (`ScapeVisual.tsx`:
a scrolling roll and a "breathe" mode), not the audio engine.
