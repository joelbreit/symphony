"""Tango idiom helpers — the vocabulary from docs/02, executable.

The accompaniment feels (marcato, síncopa, 3-3-2, la yumba), the arrastre,
the bellows, the ornaments, the yeites. Piece-local by design: promote to
lib/ only what proves general (goal.md). Everything writes swing=False —
tango never swings; its elasticity is written into the notes.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib import figures, parse_chord, fit, voicing
from lib.dsl import R as R_
from lib.dsl import events as _events
from lib.pitch import midi

BASS_LO, BASS_HI = 'E1', 'D3'


def _root_fifth(sym, near):
    root_pc, bass_pc, pcs = parse_chord(sym)
    r = fit(bass_pc, BASS_LO, BASS_HI, near=near)
    f = fit(pcs[2 % len(pcs)], BASS_LO, BASS_HI, near=r)
    return r, f


def fit_root(sym, lo, hi, near=None):
    """The chord's bass note placed in a range (thin wrapper over fit)."""
    return fit(parse_chord(sym)[1], lo, hi, near=near)


# ------------------------------------------------------------- the feels

def bass_marcato(p, t, sym, vel=88, near='A2', gate=0.6):
    """Marcato en cuatro: root/fifth quarters, 1 and 3 heavy (docs/02)."""
    r, f = _root_fifth(sym, near)
    for i, pitch in enumerate([r, f, r, f]):
        p.note('cb', t + i, pitch, 1, vel=vel - (0 if i % 2 == 0 else 18),
               gate=gate, swing=False)
    return r


def bass_endos(p, t, sym, vel=46, near='A2'):
    """Marcato en dos: half-note weight, the lyrical sections' floor."""
    r, f = _root_fifth(sym, near)
    p.note('cb', t, r, 2, vel=vel, gate=0.9, swing=False)
    p.note('cb', t + 2, f, 2, vel=max(1, vel - 10), gate=0.9, swing=False)
    return r


def piano_marcato(p, t, sym, vel=82, stabs=True):
    """Piano LH octaves double the bass; RH chord stabs on 2 and 4."""
    r, f = _root_fifth(sym, 'A1')
    for i, pitch in enumerate([r, f, r, f]):
        p.add('pno', t + i, [([pitch, pitch + 12], 1)],
              vel=vel - (0 if i % 2 == 0 else 16), gate=0.55, swing=False)
    if stabs:
        v = voicing(sym, 'G3', 'G4')
        for b in (1, 3):
            p.add('pno', t + b, [(v, 0.5)], vel=max(1, vel - 24), gate=0.5,
                  swing=False)


def guitar_comp(p, t, sym, vel=64, rhythm=(1.5, 3.5), lo='A3', hi='B4'):
    """Dry offbeat chords — Piazzolla's guitar in rhythmic sections."""
    v = voicing(sym, lo, hi)
    for b in rhythm:
        p.add('gtr', t + b, [(v, 0.5)], vel=vel, gate=0.5, swing=False)


def sincopa332(p, t, sym, vel=88, near='C2', sym2=None, golpe_hit=False):
    """The 3-3-2 engine: attacks at 1, the and-of-2, and 4 (docs/02).
    Bass + piano LH octaves + RH chord; sym2, if given, colors the last hit."""
    r, _ = _root_fifth(sym, near)
    r2 = r if sym2 is None else _root_fifth(sym2, r)[0]
    hits = [(0.0, 1.5, sym, r, 6), (1.5, 1.5, sym, r, 0),
            (3.0, 1.0, sym2 or sym, r2, -8)]
    for off, d, s, root, acc in hits:
        p.note('cb', t + off, root, d, vel=vel + acc, gate=0.7, swing=False)
        p.add('pno', t + off, [([root, root + 12], d)], vel=vel + acc - 6,
              gate=0.65, swing=False)
        v = voicing(s, 'G3', 'G4', near='C4')
        p.add('pno', t + off, [(v, d)], vel=max(1, vel + acc - 22), gate=0.6,
              swing=False)
    if golpe_hit:
        p.perc(t + 3.0, [('wbh', 0.5)], vel=max(1, vel - 30), inst='golpe',
               swing=False)
    return r


def yumba(p, t, sym, vel=96, near='C2'):
    """La yumba: 1 and 3 slammed with a scoop into each, 2 and 4 ghosted."""
    r, f = _root_fifth(sym, near)
    v = voicing(sym, 'E3', 'E4', near='A3')
    for b, heavy in ((0, True), (1, False), (2, True), (3, False)):
        if heavy:
            figures.scoop(p, 'cb', t + b, semitones=1.5)
            p.note('cb', t + b, r, 1, vel=vel, gate=0.8, swing=False)
            p.add('pno', t + b, [([r, r + 12], 1)], vel=vel - 4, gate=0.7,
                  swing=False)
            p.add('pno', t + b, [(v, 1)], vel=vel - 14, gate=0.65, swing=False)
        else:
            p.note('cb', t + b, f, 1, vel=max(1, vel - 40), gate=0.4,
                   swing=False)
    return r


def arrastre(p, t, sym, vel=92):
    """The drag into the downbeat at `t`: bass scoop + piano chromatic ramp
    (docs/02). Write the downbeat itself with a feel helper."""
    _, bass_pc, _ = parse_chord(sym)
    figures.scoop(p, 'cb', t, semitones=2.0)
    figures.smear_into(p, 'pno', fit(bass_pc, 'C3', 'C4'), t, vel - 8, n=4)


# ------------------------------------------------------------- ornaments

def mordent(p, inst, pitch, at, vel, lower=True):
    """Crushed mordent graces before the beat; write the main note at `at`
    yourself (lib figure convention). More mordents = more heat (docs/02)."""
    m = midi(pitch)
    n = m - 1 if lower else m + 2
    p.note(inst, at - 0.16, m, 0.08, vel=max(20, vel - 10), swing=False)
    p.note(inst, at - 0.08, n, 0.08, vel=max(20, vel - 14), swing=False)


def latigo(p, inst, target, at, vel, n=8):
    """Látigo, the whip: fast chromatic rise cracking into `at` (write the
    target yourself). Steeper and faster than a tailgate smear."""
    m = midi(target)
    for i in range(n, 0, -1):
        p.note(inst, at - 0.055 * i, m - i, 0.05, vel=max(24, vel - 4 * i),
               swing=False)


# ------------------------------------------------------------- the lungs

def bellows(p, inst, t0, t1, intensity=1.0):
    """One breath on [t0, t1]: attack, settle, swell, release (CC11)."""
    span = t1 - t0
    lo = round(96 - 20 * intensity)
    hi = min(127, round(96 + 16 * intensity))
    p.cc(inst, t0, 11, 92)
    p.hairpin(inst, t0 + 0.10 * span, t0 + 0.45 * span, 92, lo)
    p.hairpin(inst, t0 + 0.45 * span, t1 - 0.12 * span, lo, hi)
    p.cc(inst, max(t0, t1 - 0.05), 11, 88)


def sing(p, inst, t, notes, vel='mf', vel_end=None, breathe=1.0, **kw):
    """p.add plus lungs: every sounding note >= 1 beat gets a bellows shape.
    A bandoneón (or bowed) line with flat CC11 is dead — docs/02."""
    end = p.add(inst, t, notes, vel=vel, vel_end=vel_end, **kw)
    tt = t
    for pitch, d in _events(notes):
        d = float(d)
        if pitch is not None and d >= 1.0:
            bellows(p, inst, tt, tt + d, intensity=breathe)
        tt += d
    return end


def full_voice(p, t, insts=('bnd', 'vln')):
    """Reset CC11 before a rítmico section (hairpin values persist)."""
    for inst in insts:
        p.cc(inst, t, 11, 114)


# ------------------------------------------------------------- punctuation

def golpe(p, t, pattern, vel=30):
    """Knocks on wood — rim/woodblocks/claves/cabasa on the golpe channel."""
    return p.perc(t, pattern, vel=vel, inst='golpe', swing=False)


def stab(p, t, sym, vel=96, dur=0.5, insts=('bnd', 'gtr', 'pno'), near='C4'):
    """One unison chord hit across the band (for breaks and freezes)."""
    for inst, lo, hi in (('bnd', 'G3', 'A4'), ('gtr', 'A3', 'B4'),
                         ('pno', 'C4', 'C5')):
        if inst in insts:
            p.add(inst, t, [(voicing(sym, lo, hi, near=near), dur)], vel=vel,
                  gate=0.5, swing=False)
