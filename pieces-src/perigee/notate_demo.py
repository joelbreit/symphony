"""Prototype: clean notation for one Perigee section, from the symbolic layer.

    ../../.venv/bin/python notate_demo.py    (from pieces-src/perigee/)

Writes MusicXML + an SVG/PNG of Apogee I (bars 5-20, A minor) so we can see
how clean the engraving comes out straight off Piece.notes — no swing, gate,
or humanize.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'src'))

from lib import notation
from compose import build, S1, S2

OUT = pathlib.Path(__file__).resolve().parent / 'output'
OUT.mkdir(exist_ok=True)


def main():
    p = build()
    # Apogee I: the full lyric, bandoneon carries the theme; bars 5-20.
    insts = ['vln', 'bnd', 'pno', 'gtr', 'cb']
    xml = OUT / 'apogee1.musicxml'
    notation.to_musicxml(p, insts, str(xml), keys='a', beat0=S1, beat1=S2,
                         grand_staff=('pno',), title='Perigee — Apogee I')
    print('wrote', xml)

    svg = notation.render_svg(str(xml))
    (OUT / 'apogee1.svg').write_text(svg)
    print('wrote', OUT / 'apogee1.svg', f'({len(svg)} bytes)')


if __name__ == '__main__':
    main()
