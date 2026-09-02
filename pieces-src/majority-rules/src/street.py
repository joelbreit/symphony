"""Street-band language shared with Cut Loose, plus this piece's gavel.

The roster is intentionally identical, so the mature second-line primitives
are loaded from Cut Loose rather than forked. The civic-rondo material and
form remain local to this piece.
"""
import importlib.util
import pathlib

_SOURCE = pathlib.Path(__file__).resolve().parents[2] / 'cut-loose' / 'src' / 'street.py'
_SPEC = importlib.util.spec_from_file_location('_cut_loose_street', _SOURCE)
_BASE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_BASE)

for _name in dir(_BASE):
    if not _name.startswith('_'):
        globals()[_name] = getattr(_BASE, _name)


def gavel(p, t, sym='Bb6', vel=104, final=False):
    """Long, short, short band hits: the chair's increasingly abused gavel."""
    for off, dur, dv in ((0.0, 0.7, 0), (1.5, 0.35, -3), (2.25, 0.35, 3)):
        stab(p, t + off, sym, vel=vel + dv, dur=dur,
             who=('cornet', 'clarinet', 'alto', 'tbn'))
    p.perc(t, [('crash', 1.2)], vel=vel, inst=BD)
    if final:
        p.perc(t + 3.0, [('kick', 0.4)], vel=min(127, vel + 6), inst=BD)
        p.perc(t + 3.0, [('sn', 0.3)], vel=min(127, vel + 2), inst=SN)
