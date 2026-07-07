"""Roy G. Biv and the Spectrum Seven — the roster as data (docs/01, 02).

Seven stripe chairs, one per instrument family, chosen so the roll's
family colors stack into ROYGBIV top-to-bottom. Plus the scene players:
rain (pizzicato = blue), bass (the amber ground line), harp (lightning and
the sun), cloud (tremolo strings declared family 'other' = gray), and the
kit — the invisible rhythm section that never appears in the photo.

STRIPES is ordered top (outer arc, R) to bottom (inner arc, V); index k
plays the arch 2k diatonic steps below the choir.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib import Ensemble, Instrument
from lib.ensemble import I

STRIPES = ['choir', 'tpt', 'gtr', 'cl', 'sq', 'str', 'org']


def spectrum() -> Ensemble:
    return Ensemble([
        # the stripes, R O Y G B I V (arch spans: k from 62..86 down 2k steps)
        I('choir', 'Choir',        52, 'G3', 'F6',  'voice',   58, 100),
        I('tpt',   'Trumpets',     56, 'F3', 'C6',  'brass',   72, 96),
        I('gtr',   'Guitar',       25, 'E2', 'C6',  'plucked', 50, 96),
        I('cl',    'Clarinet',     71, 'D3', 'G5',  'winds',   44, 100),
        I('sq',    'Square Lead',  80, 'A2', 'G5',  'synth',   78, 78),
        I('str',   'Strings',      48, 'G2', 'E5',  'strings', 36, 100),
        I('org',   'Organ',        16, 'E2', 'D5',  'keys',    86, 96),
        # the scene players
        I('rain',  'Rain (pizzicato)', 45, 'D2', 'C6', 'strings', 62, 100),
        I('bass',  'Bass',         32, 'D1', 'F2',  'plucked', 60, 110),
        I('harp',  'Harp',         46, 'E2', 'A7',  'plucked', 30, 100),
        I('cloud', 'Clouds',       44, 'C3', 'A6',  'other',   52, 82),
        Instrument('kit', 'Drums', family='perc', percussion=True),
    ], name='Roy G. Biv & the Spectrum Seven', reverb=45)
