"""Export The Punch Line's engraved score into its web piece package.

    ../../.venv/bin/python export_score.py    (from pieces-src/the-punch-line/)

Staff order and key regions come from the piece itself (src/compose.py
declares the keys); what stays here is genuinely score-only: the lowered
min_nom and the two engraving retimes below.

min_nom is lowered to 0.1 so the doctored roll's five-octave 32nd-note run
(nominal 0.1125 per note) stays on the page — it is the whole joke — while
the acciaccatura crushes (0.09) remain performance ornaments and drop out.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'src'))

from lib import notation
from compose import build, TAG


def engrave_retimes(p):
    """Score-only retimes (the MIDI performance is untouched).

    The closing five-octave roll is a cross-staff strum: its 0.045-beat
    stagger puts the right hand's first note ~0.23 beats after the beat,
    which snaps to a 1/24 triplet position and engraves as monster tuplets
    (24:17, 12:7). Engraving convention writes a roll as one chord on its
    beat, so fold the stagger out. The "last hole" pip at t+9.4 sits on a
    triplet-16th grid slot for the same reason; write it on the eighth.
    """
    roll, hole = TAG + 6.0, TAG + 9.4
    for n in p.notes:
        if roll <= n.start < roll + 0.6:
            n.start = roll
        elif abs(n.start - hole) < 1e-6:
            n.start = TAG + 9.5


if __name__ == '__main__':
    p = build()
    engrave_retimes(p)
    notation.export(p, 'the-punch-line', min_nom=0.1)
