"""Export the horn score into Majority Rules' listening-room package."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'src'))

from lib import notation
from compose import build


if __name__ == '__main__':
    notation.export(build(), 'majority-rules', composer='Codex')
