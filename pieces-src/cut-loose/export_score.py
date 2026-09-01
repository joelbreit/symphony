"""Export Cut Loose's engraved score into its web piece package.

    ../../.venv/bin/python export_score.py    (from pieces-src/cut-loose/)

Staff order, key regions (E-flat, A-flat for the ramble, E-flat home) and
the tempo map all come from the piece itself. The percussion tracks are
skipped by the exporter (no drum notation yet), so the score is the five
horns. min_nom stays at the default: rolls, smears, scoops and curls are
performance, not notation.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'src'))

from lib import notation
from compose import build

if __name__ == '__main__':
    notation.export(build(), 'cut-loose')
