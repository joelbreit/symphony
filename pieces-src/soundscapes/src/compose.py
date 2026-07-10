"""Soundscapes — build every stem MIDI into output/midi/<scene>/.

    ../../.venv/bin/python src/compose.py               (from pieces-src/soundscapes/)
    ../../.venv/bin/python src/compose.py focus/bed-a   (one stem)

Each stem is its own short loopable MIDI (see docs/02 for the seam rules);
audio rendering + web manifests are export_web.py's job.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib import midi_report  # noqa: E402

import loopcraft  # noqa: E402
import palette  # noqa: E402
import scene_focus  # noqa: E402
import scene_motivate  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / 'output'

SCENES = [
    dict(module=scene_focus, ensemble=palette.focus),
    dict(module=scene_motivate, ensemble=palette.motivate),
    # scene_relax, scene_sleep land in M4
]


def build(only: str | None = None) -> list[dict]:
    """Build stem MIDIs; returns one record per stem for export_web.py."""
    records = []
    for scene in SCENES:
        mod, ens_factory = scene['module'], scene['ensemble']
        for stem in mod.STEMS:
            name = f"{stem['slot']}-{stem['variant']}"
            if only and only not in (f'{mod.ID}/{name}', mod.ID):
                continue
            p = loopcraft.new_stem(ens_factory(), mod.ID, stem['slot'],
                                   stem['variant'], stem['bars'], mod.BPM,
                                   stem['seed'])
            stem['build'](p)
            loopcraft.finish(p, stem['bars'])
            mid = OUT / 'midi' / mod.ID / f'{name}.mid'
            mid.parent.mkdir(parents=True, exist_ok=True)
            p.write(str(mid))
            records.append(dict(scene=mod.ID, bpm=mod.BPM, stem=stem,
                                mid=mid, piece=p,
                                loop_seconds=loopcraft.loop_seconds(
                                    stem['bars'], mod.BPM)))
            print(f"{mod.ID}/{name}: {stem['bars']} bars, "
                  f"loop {records[-1]['loop_seconds']:.3f}s -> {mid.relative_to(OUT.parent)}")
    return records


if __name__ == '__main__':
    only = sys.argv[1] if len(sys.argv) > 1 else None
    recs = build(only)
    if not recs:
        sys.exit(f'no stems matched {only!r}')
    print()
    for r in recs:
        print(midi_report(str(r['mid'])))
