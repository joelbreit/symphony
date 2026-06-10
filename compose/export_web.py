"""Export note/tempo/section data for the web piano roll.

Writes web/public/data/meta.json (movements, sections, instruments) and
web/public/data/mvt{1..4}.json (compact note arrays [t, dur, pitch, inst, vel]
in seconds, sorted by onset).
"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from music21 import tempo as m21tempo

from compose.common import Orchestra, ROSTER
from compose import mvt1, mvt2, mvt3, mvt4

PART_ORDER = list(ROSTER.keys()) + ['perc']

INSTRUMENTS = [
    {'id': 'fl',   'name': 'Flutes',      'family': 'winds'},
    {'id': 'ob',   'name': 'Oboes',       'family': 'winds'},
    {'id': 'cl',   'name': 'Clarinets',   'family': 'winds'},
    {'id': 'bsn',  'name': 'Bassoons',    'family': 'winds'},
    {'id': 'hn',   'name': 'Horns',       'family': 'brass'},
    {'id': 'tpt',  'name': 'Trumpets',    'family': 'brass'},
    {'id': 'tbn',  'name': 'Trombones',   'family': 'brass'},
    {'id': 'timp', 'name': 'Timpani',     'family': 'color'},
    {'id': 'hp',   'name': 'Harp',        'family': 'color'},
    {'id': 'cel',  'name': 'Celesta',     'family': 'color'},
    {'id': 'vln1', 'name': 'Violin I',    'family': 'strings'},
    {'id': 'vln2', 'name': 'Violin II',   'family': 'strings'},
    {'id': 'vla',  'name': 'Violas',      'family': 'strings'},
    {'id': 'vc',   'name': 'Cellos',      'family': 'strings'},
    {'id': 'cb',   'name': 'Basses',      'family': 'strings'},
    {'id': 'perc', 'name': 'Percussion',  'family': 'color'},
]

MOVEMENTS = [
    dict(mod=mvt1, id='mvt1', num='I', title='Kindling', key='C minor',
         tempoLabel='Adagio misterioso — Allegro con fuoco',
         sections=[
             (0, 'fragments in the dark'),
             (56, 'the Question, assembled'),
             (64, 'Allegro con fuoco'),
             (160, 'a gentler thought'),
             (256, 'the bass remembers the Question'),
             (288, 'development — lost'),
             (384, 'brass stretto'),
             (432, 'the dam about to break'),
             (464, 'recapitulation'),
             (544, 'the light, foreshadowed'),
             (608, 'darkening'),
             (656, 'coda — the Question, unresolved'),
         ]),
    dict(mod=mvt2, id='mvt2', num='II', title='The Garden of Forking Paths', key='G minor',
         tempoLabel='Presto leggiero',
         sections=[
             (0, 'the cell, branching'),
             (45, 'the first fork'),
             (72, 'the Question, mocked'),
             (120, 'canon chase'),
             (168, 'full romp'),
             (216, 'pause at the fork'),
             (240, 'Trio — the warm branch'),
             (288, 'a fork even here'),
             (312, 'the musette returns'),
             (408, 'Scherzo again, impatient'),
             (504, 'the big fork — wrong key!'),
             (552, 'evaporation'),
         ]),
    dict(mod=mvt3, id='mvt3', num='III', title='What the Light Holds', key='A♭ major',
         tempoLabel='Adagio cantabile',
         sections=[
             (0, 'the hymn — the almost-answer'),
             (32, 'soaring'),
             (64, 'wandering warmth'),
             (88, 'the F-minor shadow'),
             (112, 'with full heart'),
             (160, 'the interruption'),
             (168, 'serenity — the door ajar'),
         ]),
    dict(mod=mvt4, id='mvt4', num='IV', title='Through', key='C minor → C major',
         tempoLabel='Allegro agitato — Maestoso — Lento lucente',
         sections=[
             (0, 'the storm returns'),
             (80, 'the striving march'),
             (176, 'collapse'),
             (208, 'rebuilding'),
             (272, 'the greater collapse'),
             (336, 'the gathering — a major third, from far away'),
             (368, 'THE ANSWER'),
             (456, 'apotheosis'),
             (552, 'the Question resolves'),
             (584, 'largamente'),
             (616, 'the window closes'),
         ]),
]

def tempo_map(orch):
    """[(offset_ql, bpm), ...] from the conductor part, sorted."""
    marks = []
    for mm in orch.parts['vln1'].recurse().getElementsByClass(m21tempo.MetronomeMark):
        marks.append((float(mm.getOffsetInHierarchy(orch.parts['vln1'])), float(mm.number)))
    marks.sort()
    if not marks or marks[0][0] > 0:
        marks.insert(0, (0.0, 120.0))
    return marks

def make_seconds(marks):
    """Piecewise ql->seconds converter."""
    anchors = []   # (ql, sec, bpm)
    sec = 0.0
    for i, (ql, bpm) in enumerate(marks):
        if i > 0:
            pql, pbpm = marks[i - 1]
            sec += (ql - pql) * 60.0 / pbpm
        anchors.append((ql, sec, bpm))

    def to_sec(q):
        lo = 0
        for (aql, asec, abpm) in reversed(anchors):
            if q >= aql - 1e-9:
                return asec + (q - aql) * 60.0 / abpm
        return q * 60.0 / anchors[0][2]
    return to_sec

def export():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'web', 'public', 'data')
    os.makedirs(out_dir, exist_ok=True)
    meta = {'title': 'Symphony No. 1 in C minor — “The Window”',
            'composer': 'Claude', 'year': 2026,
            'instruments': INSTRUMENTS, 'movements': []}
    inst_index = {d['id']: i for i, d in enumerate(INSTRUMENTS)}

    for mv in MOVEMENTS:
        o = Orchestra()
        end_ql = mv['mod'].compose(o, 0.0)
        to_sec = make_seconds(tempo_map(o))
        notes = []
        for pname in PART_ORDER:
            idx = inst_index[pname]
            for n in o.parts[pname].recurse().notes:
                t = to_sec(float(n.getOffsetInHierarchy(o.parts[pname])))
                # duration in seconds: convert end ql - start ql through the map
                start_ql = float(n.getOffsetInHierarchy(o.parts[pname]))
                d = to_sec(start_ql + float(n.duration.quarterLength)) - t
                vel = n.volume.velocity or 64
                pitches = n.pitches if hasattr(n, 'pitches') else [n.pitch]
                for p in pitches:
                    notes.append([round(t, 3), round(max(d, 0.05), 3), p.midi, idx, vel])
        notes.sort(key=lambda x: (x[0], x[2]))
        dur = to_sec(end_ql)
        meta['movements'].append({
            'id': mv['id'], 'num': mv['num'], 'title': mv['title'], 'key': mv['key'],
            'tempoLabel': mv['tempoLabel'],
            'duration': round(max(dur, max((n[0] + n[1]) for n in notes)), 2),
            'noteCount': len(notes),
            'audio': f'audio/{mv["id"]}.m4a',
            'data': f'data/{mv["id"]}.json',
            'sections': [[round(to_sec(q), 2), label] for q, label in mv['sections']],
        })
        with open(os.path.join(out_dir, f'{mv["id"]}.json'), 'w') as f:
            json.dump(notes, f, separators=(',', ':'))
        print(f'{mv["id"]}: {len(notes)} notes, {dur/60:.2f} min')

    with open(os.path.join(out_dir, 'meta.json'), 'w') as f:
        json.dump(meta, f, separators=(',', ':'), ensure_ascii=False)
    print('wrote meta.json')

if __name__ == '__main__':
    export()
