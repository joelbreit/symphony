"""The Piazzolla quintet as data (docs/01, docs/02).

Five soloists in fixed jobs plus the golpe channel (knocks on wood — tango's
percussion is the players hitting their instruments). No drums: the marcato
is the percussion. The double bass is family 'plucked' deliberately — it IS
plucked here, and it puts the timekeeper on the tight humanize profile.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib import Ensemble, Instrument
from lib.ensemble import I


def quintet() -> Ensemble:
    return Ensemble([
        I('vln', 'Violin',      40, 'G3', 'E7', 'strings', 42),
        I('bnd', 'Bandoneon',   23, 'A2', 'B6', 'winds',   64, 105),
        I('pno', 'Piano',        0, 'A0', 'C8', 'keys',    56, grand=True),
        I('gtr', 'Guitar',      26, 'E2', 'B5', 'plucked', 84, 88),
        I('cb',  'Double Bass', 32, 'E1', 'A3', 'plucked', 70, 110),
        Instrument('golpe', 'Golpe', family='perc', percussion=True),
    ], name='tango quintet', reverb=35)
