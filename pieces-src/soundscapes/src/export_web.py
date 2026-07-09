"""Render soundscape stems and write the web packages.

    ../../.venv/bin/python src/export_web.py               # everything
    ../../.venv/bin/python src/export_web.py --midi-only   # skip audio render
    ../../.venv/bin/python src/export_web.py --sf2 path.sf2

Writes, per scene: web/public/soundscapes/<scene>/audio/<slot>-<variant>.m4a
and soundscape.json; plus the tab index web/public/soundscapes/index.json.
`loopSeconds` comes from the score (bars · 4 · 60/bpm), never from the file;
`tailSeconds` is measured from the rendered WAV. Audio renders must come
from the exact MIDIs compose.py just built — same rule as every piece here.
"""
import argparse
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib import assess  # noqa: E402

import compose  # noqa: E402
import loopcraft  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / 'output'
WEB = ROOT / 'web' / 'public' / 'soundscapes'


def stem_notes(piece, bpm):
    """Note events for the web visualization: [startSec, durSec, pitch, vel].

    Seconds use the same bars·60/bpm arithmetic as loopSeconds so the roll
    lines up with the scheduler's loop grid (seam-crossing tails included).
    """
    spb = 60.0 / bpm
    return [[round(n.start * spb, 3), round(n.dur * spb, 3), n.pitch, n.vel]
            for n in sorted(piece.notes, key=lambda n: (n.start, n.pitch))]


def export(sf2=None, midi_only=False):
    records = compose.build()
    scenes = []
    for scene_mod in [s['module'] for s in compose.SCENES]:
        recs = [r for r in records if r['scene'] == scene_mod.ID]
        layers: dict[str, dict] = {}
        total_kb = 0
        for r in recs:
            stem, name = r['stem'], f"{r['stem']['slot']}-{r['stem']['variant']}"
            layer = layers.setdefault(stem['slot'],
                                      dict(stem['layer'], variants=[]))
            variant = dict(file=f'audio/{name}.m4a',
                           loopSeconds=round(r['loop_seconds'], 3),
                           notes=stem_notes(r['piece'], r['bpm']))
            if not midi_only:
                wav = OUT / f"{scene_mod.ID}-{name}.wav"
                stderr = loopcraft.render_wav(r['mid'], wav, sf2=sf2)
                clip = [l for l in stderr.splitlines() if 'clip' in l.lower()]
                if clip:
                    print(f'  !! {name}: {clip[0]}', file=sys.stderr)
                m4a = WEB / scene_mod.ID / 'audio' / f'{name}.m4a'
                loopcraft.encode_m4a(wav, m4a)
                variant['tailSeconds'] = round(
                    loopcraft.wav_seconds(wav) - r['loop_seconds'], 3)
                total_kb += m4a.stat().st_size // 1024
                roll = OUT / 'roll' / scene_mod.ID / f'{name}.png'
                roll.parent.mkdir(parents=True, exist_ok=True)
                assess.pianoroll(r['piece'], str(roll), wav=str(wav))
            layer['variants'].append(variant)
        manifest = dict(schema=1, id=scene_mod.ID, title=scene_mod.META['title'],
                        composer='Claude', concept=scene_mod.META['concept'],
                        about=scene_mod.META['about'],
                        accent=scene_mod.META['accent'],
                        key=scene_mod.KEY, bpm=scene_mod.BPM,
                        layers=list(layers.values()))
        mdir = WEB / scene_mod.ID
        mdir.mkdir(parents=True, exist_ok=True)
        with open(mdir / 'soundscape.json', 'w') as f:
            # compact: the inline notes arrays would explode an indented dump
            json.dump(manifest, f, separators=(',', ':'))
        scenes.append(dict(id=scene_mod.ID, dir=f'soundscapes/{scene_mod.ID}',
                           title=scene_mod.META['title'],
                           concept=scene_mod.META['concept'],
                           accent=scene_mod.META['accent'],
                           layers=len(layers)))
        note = '(midi only)' if midi_only else f'{total_kb} KB audio'
        print(f"{scene_mod.ID}: {len(layers)} layers, {len(recs)} stems, {note}")
    with open(WEB / 'index.json', 'w') as f:
        json.dump(dict(schema=1, scenes=scenes), f, indent=1)
    print(f'wrote {WEB / "index.json"}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--sf2', default=os.environ.get('SF2'))
    ap.add_argument('--midi-only', action='store_true')
    args = ap.parse_args()
    export(sf2=args.sf2, midi_only=args.midi_only)
