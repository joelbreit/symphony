"""The ground, the pulse, and the machinery that never changes.

Everything in this file exists to serve one invariant: eight bass notes, in
one order, in one register, twenty-seven times. Nothing here transposes,
inverts, augments or ornaments the ground — that is the whole point of the
piece, and the build asserts it afterwards rather than trusting this file.
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib.chords import parse_chord                                  # noqa: E402
from lib.pitch import midi                                          # noqa: E402

PNO = 'piano'

# -- the constants ------------------------------------------------------
PERIOD = 1.3373            # PSR B1919+21's rotation period, seconds
BPM_SCRUFF = 60 / PERIOD   # one pulse per beat    (44.867)
BPM = 180 / PERIOD         # one pulse per 3/4 bar (134.600)
BAR = 3.0                  # beats

# -- the ground ---------------------------------------------------------
GROUND = [midi(n) for n in ('D2', 'C2', 'Bb1', 'A1', 'Bb1', 'C2', 'D2', 'A1')]
ROOTS_MIN = ['Dm', 'C', 'Bb', 'A', 'Bb', 'C', 'Dm', 'A']
ROOTS_MAJ = ['D',  'C', 'Bb', 'A', 'Bb', 'C', 'D',  'A']

INTRO_BARS = 8
S1 = 9                     # the bar the ground locks in
N_STATEMENTS = 27
CODA = S1 + N_STATEMENTS * 8               # bar 227
LAST_BAR = CODA + 7                        # bar 234, the last bar

PULSE = midi('A7')         # 105 — the tick
PULSE_LOW = midi('A6')     # 93  — its octave, for when the top is too thin


def st(n: int) -> int:
    """First bar of statement n (1-indexed): st(1) == 11."""
    return S1 + (n - 1) * 8


def sym(i: int, major: bool) -> str:
    """Chord symbol for position i (0-7) of the ground."""
    return (ROOTS_MAJ if major else ROOTS_MIN)[i % 8]


def pool(i: int, major: bool, lo, hi, add=()) -> list:
    """Every chord tone of position i inside [lo, hi], ascending.

    `add` takes extra pitch classes (a 9th to open a voicing up, the 7th on
    the dominant) as note names — 'E', 'G' — not octaves.
    """
    _, _, pcs = parse_chord(sym(i, major))
    pcs = list(pcs) + [midi(f'{a}4') % 12 for a in add]
    lo, hi = midi(lo), midi(hi)
    return [p for p in range(lo, hi + 1) if p % 12 in pcs]


def above(i: int, major: bool, floor, n: int, add=()) -> list:
    """The n lowest chord tones at or above `floor` — a voicing, bottom-up."""
    return pool(i, major, floor, midi(floor) + 40, add=add)[:n]


def arc(pitches: list, n: int, start: int = 0) -> list:
    """Walk up then down a pitch pool, n notes long — the arpeggio spine."""
    if not pitches:
        return []
    m = len(pitches)
    if m == 1:
        return pitches * n
    cycle = list(range(m)) + list(range(m - 2, 0, -1))     # 0..m-1..1
    return [pitches[cycle[(start + k) % len(cycle)]] for k in range(n)]


# -- writers ------------------------------------------------------------
def bass(p, bar: int, i: int, vel: int, dur: float = BAR, low_octave=False,
         gate: float = 0.98):
    """The ground note for position i, in its one and only register."""
    g = GROUND[i % 8]
    pitches = [g - 12, g] if low_octave else [g]
    p.add(PNO, p.bar(bar), [(pitches, dur)], vel=vel, gate=gate, swing=False)


def pulse(p, bar: int, vel: int, pitch: int = PULSE, double: bool = False,
          dur: float = 1.0):
    """The tick: an A on the downbeat, machine-exact (rigid), never late."""
    pitches = [PULSE_LOW, pitch] if double else [pitch]
    p.add(PNO, p.bar(bar), [(pitches, dur)], vel=vel, gate=0.9, swing=False,
          rigid=True)


def pedal_bars(p, bar0: int, n: int, release: float = 0.14):
    """One pedal per bar — the thing that makes a ground ring instead of tick."""
    for b in range(bar0, bar0 + n):
        p.pedal(PNO, p.bar(b) - 0.02, p.bar(b) + BAR - release)


def pedal_halves(p, bar0: int, n: int, release: float = 0.10):
    """Two pedals per bar, for the sixteenth-note statements."""
    for b in range(bar0, bar0 + n):
        for h in (0.0, 1.5):
            p.pedal(PNO, p.bar(b) + h - 0.02, p.bar(b) + h + 1.5 - release)


def roll_to(p, pitches, land: float, vel: int, spread: float = 0.055,
            dur: float = BAR, gate: float = 0.98, voice_top: int = 0,
            rigid_top: bool = False):
    """A rolled chord whose TOP note lands exactly on `land`.

    Pianists roll a big chord *into* the beat when its top note is the one
    that matters — which here is always, because the top note is the pulse.
    Writing it the other way (bottom on the beat) puts the melody late.
    """
    from fractions import Fraction
    ps = sorted(pitches)
    n = len(ps)
    written = []
    for k, pitch in enumerate(ps):
        # quantize exactly the way Piece.add will, so the record below still
        # identifies the note afterwards
        t = float(Fraction(land - (n - 1 - k) * spread).limit_denominator(96))
        v = vel + (voice_top if k == n - 1 else 0)
        p.add(PNO, t, [(pitch, dur + (n - 1 - k) * spread)],
              vel=max(1, min(127, v)), gate=gate, swing=False,
              rigid=rigid_top and k == n - 1)
        written.append((t, pitch))
    # A roll is a chord in notation and a sweep in performance. Record what
    # was written so export_score.py can fold the sweep back into the chord
    # it stands for; the MIDI keeps the sweep.
    p.__dict__.setdefault('rolls', []).append((land, float(dur), written))


def chord_on(p, at: float, pitches, dur: float, vel: int, gate: float = 0.95,
             top_vel: int = 0):
    """A struck chord, with the top note voiced above the rest if asked."""
    ps = sorted(pitches)
    for k, pitch in enumerate(ps):
        v = vel + (top_vel if k == len(ps) - 1 else 0)
        p.add(PNO, at, [(pitch, dur)], vel=max(1, min(127, v)), gate=gate,
              swing=False)
