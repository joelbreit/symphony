"""The melodic note DSL, ported from The Window's framework.

    'G4:q Eb5:e r:h (C3 G3 E4):w'   — pitch:duration tokens; r = rest;
                                       chords in parens.

Durations: w h q e s (+ dotted 'q.' etc.), t = eighth triplet (1/3),
tq = quarter triplet (2/3), ts = sixteenth triplet (1/6), or any number
(':1.5'). All offsets and durations are in beats (quarter notes).

Parsed events are `(pitch, dur)` pairs where pitch is a MIDI int, a list
of MIDI ints (chord), or None (rest), and dur is a Fraction.
"""
from fractions import Fraction

from .pitch import midi

DUR = {
    'w': Fraction(4), 'h': Fraction(2), 'q': Fraction(1),
    'e': Fraction(1, 2), 's': Fraction(1, 4),
    'w.': Fraction(6), 'h.': Fraction(3), 'q.': Fraction(3, 2),
    'e.': Fraction(3, 4), 's.': Fraction(3, 8),
    't': Fraction(1, 3), 'tq': Fraction(2, 3), 'ts': Fraction(1, 6),
}


def _dur(tok: str) -> Fraction:
    if tok in DUR:
        return DUR[tok]
    return Fraction(tok).limit_denominator(96)


def parse(dsl: str):
    """Parse 'G4:q (C3 G3):h r:e' into [(midi|None|[midi], Fraction), ...]."""
    out = []
    s = dsl.split()
    i = 0
    while i < len(s):
        tok = s[i]
        if tok.startswith('('):
            grp = [tok[1:]]
            while ')' not in grp[-1]:
                i += 1
                grp.append(s[i])
            last, dur_part = grp[-1].split(')')
            grp[-1] = last
            grp = [g for g in grp if g]
            out.append(([midi(p) for p in grp], _dur(dur_part.lstrip(':'))))
        else:
            p, d = tok.rsplit(':', 1)
            out.append((None if p == 'r' else midi(p), _dur(d)))
        i += 1
    return out


def events(notes):
    """Normalize DSL string or (pitch, dur) list into parsed-event form."""
    if isinstance(notes, str):
        return parse(notes)
    out = []
    for p, d in notes:
        if isinstance(p, list):
            p = [midi(x) for x in p]
        elif p is not None:
            p = midi(p)
        out.append((p, Fraction(d).limit_denominator(96)))
    return out


def total_beats(notes) -> float:
    return float(sum(d for _, d in events(notes)))


def R(dsl: str, times: int) -> str:
    """Repeat a DSL string with proper spacing (never use `s * n`)."""
    return ' '.join([dsl] * times)


def B(notes, n_bars: int, meter=(4, 4)):
    """Guard: the material must span exactly n_bars of `meter`. Returns it."""
    want = n_bars * meter[0] * 4.0 / meter[1]
    got = total_beats(notes)
    assert got == want, (
        f'wanted {want} beats ({n_bars} bars of {meter[0]}/{meter[1]}), got {got}: '
        f'{str(notes)[:60]}…')
    return notes


def transpose(notes, semitones: int):
    """Transpose parsed events or a DSL string; returns parsed events."""
    out = []
    for p, d in events(notes):
        if p is None:
            out.append((None, d))
        elif isinstance(p, list):
            out.append(([x + semitones for x in p], d))
        else:
            out.append((p + semitones, d))
    return out
