"""Assemble the full symphony: four movements with breaths between them."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compose.common import Orchestra, write_midi, midi_report, check_ranges
from compose import mvt1, mvt2, mvt3, mvt4

def build_full(path='output/symphony_full.mid'):
    o = Orchestra()
    t = mvt1.compose(o, 0.0)            # ends q=152 -> 8 ql ~ 3.2s breath
    t = mvt2.compose(o, t + 8)          # ends q=240 -> 12 ql ~ 3.0s breath
    t = mvt3.compose(o, t + 12)         # ends q=52  -> 4 ql  ~ 4.6s breath
    t = mvt4.compose(o, t + 4)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_midi(o, path)
    return o, path

if __name__ == '__main__':
    o, path = build_full()
    print(midi_report(path))
    probs = check_ranges(o)
    print('range problems:', probs if probs else 'none')

    # per-movement files too
    for name, mod in (('mvt1', mvt1), ('mvt2', mvt2), ('mvt3', mvt3), ('mvt4', mvt4)):
        om = Orchestra()
        mod.compose(om, 0.0)
        write_midi(om, f'output/{name}.mid')
    print('wrote per-movement files')
