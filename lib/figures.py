"""Textures and idioms: the figure library from all four lineages.

Two shapes of helper:
  - *event makers* (trem, arp, ost) return (pitch, dur) lists for piece.add,
    so you choose instrument/velocity/gate at the call site;
  - *writers* (roll, cym_swell, smear_into, scoop, ...) take the piece and
    write directly, because they need velocity ramps or micro-timing.

Micro-timed figures write with swing=False — they carry their own feel and
must not be re-warped by a swung write.
"""
from .chords import fit  # noqa: F401  (re-export: figures and harmony travel together)
from .ensemble import DRUMS
from .pitch import midi


# ---------------------------------------------------------------- textures

def trem(pitches, total: float, unit: float = 0.5):
    """Measured tremolo: repeat pitch/chord every `unit` for `total` beats."""
    n = int(round(total / unit))
    return [(pitches, unit)] * n


def ost(pattern, repeats: int):
    """Ostinato: repeat a (pitch, dur) list or DSL string."""
    from . import dsl
    return dsl.events(pattern) * repeats


def arp(pitches, unit: float, total: float, direction: str = 'up'):
    """Cycle through pitches every `unit` beats for `total` beats."""
    seq = [midi(p) for p in pitches]
    if direction == 'down':
        seq = seq[::-1]
    elif direction == 'updown':
        seq = seq + seq[-2:0:-1]
    n = int(round(total / unit))
    return [(seq[i % len(seq)], unit) for i in range(n)]


# ---------------------------------------------------------------- rolls & swells

def _ramp(v0, v1, i, n):
    return int(round(v0 + (v1 - v0) * i / max(1, n - 1)))


def roll(piece, inst, pitch, start, dur, v0, v1, unit: float = 0.125):
    """Timpani/snare-style roll with a velocity hairpin."""
    n = max(2, int(dur / unit))
    for i in range(n):
        piece.note(inst, start + i * unit, pitch, unit * 0.95,
                   vel=_ramp(v0, v1, i, n), swing=False)


def perc_roll(piece, key, start, dur, v0, v1, unit: float = 0.125, inst=None):
    """Drum roll on a GM drum key name ('sn', 'susp', ...)."""
    n = max(2, int(dur / unit))
    for i in range(n):
        piece.perc(start + i * unit, [(key, unit * 0.95)],
                   vel=_ramp(v0, v1, i, n), inst=inst, swing=False)


def cym_swell(piece, start, dur, v0, v1, key: str = 'susp', inst=None):
    """Suspended-cymbal crescendo: soft fast retriggers."""
    perc_roll(piece, key, start, dur, v0, v1, unit=0.25, inst=inst)


def strum(piece, inst, pitches, start, dur, vel, spread: float = 0.02, **kw):
    """Chord with a slight upward stagger for warmth."""
    for i, p in enumerate(pitches):
        piece.note(inst, start + i * spread, p, max(0.05, dur - i * spread),
                   vel=vel, swing=False, **kw)


def harp_arp(piece, inst, pitches, start, step: float = 0.125, vel='mf',
             ring: float = 1.9):
    """Rising broken chord, notes left ringing (duplicates dropped)."""
    seen = set()
    for i, p in enumerate(pitches):
        p = midi(p)
        if p in seen:
            continue
        seen.add(p)
        piece.note(inst, start + i * step, p, step * ring, vel=vel, swing=False)


# ---------------------------------------------------------------- jazz idioms

def smear_into(piece, inst, target, at, vel, n: int = 3):
    """Tailgate smear: fast chromatics rising into a downbeat at `at`.
    Write the target note yourself at `at`."""
    t = midi(target)
    for i in range(n, 0, -1):
        piece.note(inst, at - 0.17 * i, t - i, 0.15,
                   vel=max(20, vel - 6 * i), swing=False)


def falloff(piece, inst, from_pitch, at, vel, n: int = 4):
    """Brass fall: loose descending chromatics after a held note ends at `at`."""
    f = midi(from_pitch)
    for i in range(1, n + 1):
        piece.note(inst, at + 0.11 * (i - 1), f - i, 0.1,
                   vel=max(20, vel - 16 - 9 * i), swing=False)


def curl(piece, inst, target, at, vel):
    """Clarinet curl: quick upper-lower turn ending on the beat at `at`.
    Write the target note yourself at `at`."""
    t = midi(target)
    for i, (p, dv) in enumerate([(t + 2, -18), (t, -12), (t - 1, -15)]):
        piece.note(inst, at - 0.375 + i * 0.125, p, 0.115,
                   vel=max(20, vel + dv), swing=False)


def trill(piece, inst, pitch, start, dur, vel, step: int = 2, unit: float = 0.25):
    """Alternation ending on the main pitch held to the end of `dur`."""
    p = midi(pitch)
    n = max(0, int(dur / unit) - 1)
    for i in range(n):
        piece.note(inst, start + i * unit, p + (step if i % 2 else 0),
                   unit * 0.9, vel=max(20, vel - 8 - (i % 2) * 6), swing=False)
    piece.note(inst, start + n * unit, p, dur - n * unit, vel=vel, swing=False)


def scoop(piece, inst, at, semitones: float = 1.0):
    """Pitch-bend scoop into a note starting at `at` (bend range +-2 assumed)."""
    piece.bend(inst, at - 0.03, -semitones)
    piece.bend(inst, at + 0.10, -semitones * 0.45)
    piece.bend(inst, at + 0.22, 0.0)


def press_roll(piece, at, vel_end, n: int = 5, key: str = 'sn', inst=None):
    """Snare press-roll crescendo landing at `at`."""
    for i in range(n):
        piece.perc(at - (n - i) * 0.09, [(key, 0.07)],
                   vel=int(vel_end * (0.35 + 0.1 * i)), inst=inst, swing=False)


_ = DRUMS  # imported for callers' convenience via `from lib.figures import DRUMS`
