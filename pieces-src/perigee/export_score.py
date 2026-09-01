"""Export Perigee's engraved score into its web piece package.

    ../../.venv/bin/python export_score.py    (from pieces-src/perigee/)

Staff order, key regions, and the piano's grand staff all come from the piece
itself (src/compose.py declares the keys, src/band.py marks the piano
`grand=True`), so there is nothing to say here twice.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'src'))

from lib import notation
from compose import build

if __name__ == '__main__':
    notation.export(build(), 'perigee')
