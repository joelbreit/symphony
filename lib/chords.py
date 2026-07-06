"""Chord symbols, chord charts, and voice-leading placement.

Ported from Royal Street Rattler's harmony machinery: charts are plain
lists of chord symbols (one per bar; a (sym1, sym2) tuple splits the bar),
and `fit` places a pitch class into an instrument's range near the previous
note — the primitive that makes comping and bass lines voice-lead.
"""
from .pitch import _PC, midi  # noqa: F401  (midi re-exported for convenience)

# quality -> intervals in semitones from the root (mod 12 applied later)
QUAL = {
    '': (0, 4, 7), 'm': (0, 3, 7), 'dim': (0, 3, 6), 'aug': (0, 4, 8),
    '5': (0, 7), '6': (0, 4, 7, 9), 'm6': (0, 3, 7, 9),
    '7': (0, 4, 7, 10), 'maj7': (0, 4, 7, 11), 'm7': (0, 3, 7, 10),
    'mmaj7': (0, 3, 7, 11), 'dim7': (0, 3, 6, 9), 'm7b5': (0, 3, 6, 10),
    '7b5': (0, 4, 6, 10), '7#5': (0, 4, 8, 10),
    'sus2': (0, 2, 7), 'sus4': (0, 5, 7), '7sus4': (0, 5, 7, 10),
    '9': (0, 4, 7, 10, 14), 'maj9': (0, 4, 7, 11, 14), 'm9': (0, 3, 7, 10, 14),
    '7b9': (0, 4, 7, 10, 13), '7#9': (0, 4, 7, 10, 15),
    '13': (0, 4, 7, 10, 14, 21), 'add9': (0, 4, 7, 14),
}


def parse_chord(sym: str):
    """'F/C' -> (root_pc, bass_pc, [pcs]). Bass defaults to root.

    pcs are pitch classes (0-11) in chord-tone order: root, third, fifth…
    """
    if '/' in sym:
        sym, bass = sym.split('/')
        bass_pc = _PC[bass[0]]
        for ch in bass[1:]:
            bass_pc += 1 if ch == '#' else -1
        bass_pc %= 12
    else:
        bass_pc = None
    root_pc = _PC[sym[0]]
    i = 1
    while i < len(sym) and sym[i] in '#b':
        root_pc += 1 if sym[i] == '#' else -1
        i += 1
    root_pc %= 12
    if sym[i:] not in QUAL:
        raise ValueError(f'unknown chord quality {sym[i:]!r} in {sym!r}')
    pcs = [(root_pc + iv) % 12 for iv in QUAL[sym[i:]]]
    return root_pc, (root_pc if bass_pc is None else bass_pc), pcs


def chord_at(chart, bar: int, half: int = 0) -> str:
    """Chart lookup, wrapping. A (sym1, sym2) entry splits the bar in two."""
    entry = chart[bar % len(chart)]
    if isinstance(entry, tuple):
        return entry[half]
    return entry


def fit(pc: int, lo, hi, near=None) -> int:
    """Place pitch-class `pc` in [lo, hi], optionally nearest to `near`."""
    lo, hi = midi(lo), midi(hi)
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc % 12]
    if not cands:
        return lo + ((pc - lo) % 12)
    if near is None:
        return cands[len(cands) // 2]
    return min(cands, key=lambda p: abs(p - midi(near)))


def voicing(sym: str, lo, hi, near=None):
    """Fit every chord tone into [lo, hi]: a ready-to-strum comping voicing."""
    _, _, pcs = parse_chord(sym)
    return sorted({fit(pc, lo, hi, near=near) for pc in pcs})
