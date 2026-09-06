"""Export Still Turning's engraved score into its web piece package.

    ../../.venv/bin/python export_score.py    (from pieces-src/still-turning/)

Staff order, the grand staff, and the two key regions all come from the piece
itself (`src/compose.py` declares `p.key(0, 'd')` and `p.key(…, 'D')`), so the
only thing this file has to say is score-only: a rolled chord is *notated* as
a chord on its beat with an arpeggio sign, not as the sweep of separate notes
the performance actually plays. `ground.roll_to` records every sweep it
writes; this folds them back before engraving. The MIDI is untouched.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'src'))

from lib import notation
from compose import build


def fold_rolls(p) -> int:
    """Put every rolled chord back on its beat, as one chord, for the page."""
    index = {}
    for land, dur, written in getattr(p, 'rolls', []):
        for start, pitch in written:
            index[(round(start, 6), pitch)] = (land, dur)
    folded = 0
    for n in p.notes:
        hit = index.get((round(n.start, 6), n.pitch))
        if hit is None:
            continue
        land, dur = hit
        n.start, n.nom = land, dur
        folded += 1
    return folded


if __name__ == '__main__':
    p = build()
    print(f'folded {fold_rolls(p)} rolled notes onto their beats')
    notation.export(p, 'still-turning')
