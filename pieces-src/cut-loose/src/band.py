"""The marching brass band as data (docs/01, docs/02).

Five horns and two drummers. No banjo, no piano: the harmony is the
riffing horns and the sousaphone, the way a band that walks has to do
it. The drummers are two instruments on the percussion channel — snare
and bass drum are two people in a brass band, and each gets its own
named track in the MIDI and the web player.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib import Ensemble, Instrument
from lib.ensemble import I


def brass_band() -> Ensemble:
    return Ensemble([
        I('cornet',   'Cornet',     56, 'F#3', 'D6',  'brass', 58, 106),
        I('clarinet', 'Clarinet',   71, 'E3',  'G6',  'winds', 84, 94),
        I('alto',     'Alto Sax',   65, 'Db3', 'Ab5', 'winds', 40, 98),
        I('tbn',      'Trombone',   57, 'E2',  'Bb4', 'brass', 46, 102),
        I('sousa',    'Sousaphone', 58, 'Eb1', 'Eb3', 'brass', 64, 112),
        Instrument('snare', 'Snare Drum', family='perc', percussion=True),
        Instrument('bassdrum', 'Bass Drum', family='perc', percussion=True),
    ], name='brass band', reverb=34)
