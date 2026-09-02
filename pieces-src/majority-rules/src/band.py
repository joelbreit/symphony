"""The seven people who turned a town meeting into a parade."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib import Ensemble, Instrument
from lib.ensemble import I


def brass_band() -> Ensemble:
    """The Cut Loose marching roster, preserved as seven named players."""
    return Ensemble([
        I('cornet',   'Cornet',     56, 'F#3', 'D6',  'brass', 58, 106),
        I('clarinet', 'Clarinet',   71, 'E3',  'G6',  'winds', 84, 94),
        I('alto',     'Alto Sax',   65, 'Db3', 'Ab5', 'winds', 40, 98),
        I('tbn',      'Trombone',   57, 'E2',  'Bb4', 'brass', 46, 102),
        I('sousa',    'Sousaphone', 58, 'Eb1', 'Eb3', 'brass', 64, 112),
        Instrument('snare', 'Snare Drum', family='perc', percussion=True),
        Instrument('bassdrum', 'Bass Drum', family='perc', percussion=True),
    ], name='the public nuisance', reverb=34)
