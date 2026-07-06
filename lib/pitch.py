"""Pitch names <-> MIDI numbers. Middle C is C4 = 60."""

_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
_SHARP_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def midi(p) -> int:
    """'Bb3' -> 58, 'F#4' -> 66, 'C4' -> 60. Ints pass through."""
    if isinstance(p, int):
        return p
    pc = _PC[p[0].upper()]
    i = 1
    while i < len(p) and p[i] in '#b':
        pc += 1 if p[i] == '#' else -1
        i += 1
    return 12 * (int(p[i:]) + 1) + pc


def pitch_name(m: int) -> str:
    """58 -> 'A#3' (sharp spelling; for messages and reports only)."""
    return f'{_SHARP_NAMES[m % 12]}{m // 12 - 1}'


def transpose_pitch(p, semitones: int) -> int:
    return midi(p) + semitones
