"""The motion, amendment, speeches, and votes — all in concert pitch."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib import B


# ------------------------------------------------------------ the motion
CH_MOTION = [
    'Bb6', 'Bb6', 'G7', 'Cm7', 'F7', 'F7', 'Bb6', ('Bb6', 'F7'),
    'Bb7', 'Eb6', 'Edim7', ('Bb/F', 'F7'), 'G7', 'C7', 'F7', 'Bb6',
]

MOTION_BARS = [
    'r:e D5:e F5:e Bb5:q. r:e A5:e',
    'G5:e F5:q D5:e r:q C5:e Db5:e',
    'D5:e F5:e G5:e A5:e Bb5:q D5:q',
    'C5:q. A4:e F4:h',
    'r:e D5:e F5:e Bb5:q. r:e C6:e',
    'Bb5:e A5:q F5:e r:q D5:e Eb5:e',
    'F5:e G5:e Ab5:e A5:e Bb5:q F5:q',
    'D5:q. C5:e Bb4:h',
    'F5:q Bb5:q D6:q C6:q',
    'Bb5:q G5:e Eb5:e F5:q r:q',
    'E5:q. G5:e Bb5:q G5:q',
    'F5:h r:q D5:e Eb5:e',
    'D5:e F5:e G5:q B5:q A5:q',
    'G5:e E5:e C5:q Bb4:e C5:e Db5:e D5:e',
    'Eb5:e C5:e A4:e C5:e F5:q A5:q',
    'Bb5:q. r:e F5:e D5:e Bb4:q',
]
MOTION = B(' '.join(MOTION_BARS), 16)
MOTION_HALF = B(' '.join(MOTION_BARS[:8]), 8)
MOTION_HOOK = B(' '.join(MOTION_BARS[:2]), 2)


# ---------------------------------------------------------- the amendment
CH_AMENDMENT = [
    'Eb6', 'Eb6', 'Bb7', 'Eb6', 'Cm7', 'F7', 'Bb6', 'Bb7',
    'Eb6', 'Eb6', 'Ebm6', ('Bb/F', 'F7'), 'G7', 'Cm7', 'F7', 'Bb6',
]

AMENDMENT_BARS = [
    'r:q G4:e Bb4:e Eb5:q G5:q',
    'F5:q. Eb5:e C5:q Bb4:q',
    'D5:e F5:e Ab5:q F5:e D5:e Bb4:q',
    'Eb5:h r:q Bb4:e C5:e',
    'Eb5:q G5:e Bb5:e C6:q Bb5:q',
    'A5:q. G5:e F5:q C5:q',
    'D5:e F5:e Bb5:q A5:e G5:e F5:q',
    'D5:h r:q F5:e Ab5:e',
    'G5:e Bb5:e Eb6:q D6:q Bb5:q',
    'G5:q F5:e Eb5:e G5:q Bb5:q',
    'Gb5:q. F5:e Eb5:q C5:q',
    'D5:h r:q Bb4:e C5:e',
    'D5:e F5:e G5:q B5:q A5:q',
    'G5:q Eb5:e C5:e Bb4:q C5:q',
    'A4:e C5:e Eb5:e F5:e A5:q C6:q',
    'Bb5:q. r:e F5:e D5:e Bb4:q',
]
AMENDMENT = B(' '.join(AMENDMENT_BARS), 16)

# A trombone version: same rhetoric, revoiced into a real tailgate register.
TBN_OPPOSITION = B(' '.join([
    'r:q G3:e Bb3:e Eb4:q G4:q',
    'F4:q. Eb4:e C4:q Bb3:q',
    'D4:e F4:e Ab4:q F4:e D4:e Bb3:q',
    'Eb4:h r:q Bb3:e C4:e',
    'Eb4:q G4:e Bb4:e G4:q Eb4:q',
    'A4:q. G4:e F4:q C4:q',
    'D4:e F4:e Bb4:q A4:e G4:e F4:q',
    'D4:h r:q F4:e Ab4:e',
    'G4:e Bb4:e Eb4:q F4:q G4:q',
    'Bb4:q G4:e Eb4:e G4:q Bb4:q',
    'Gb4:q. F4:e Eb4:q C4:q',
    'D4:h r:q Bb3:e C4:e',
    'D4:e F4:e G4:q B3:q A4:q',
    'G4:q Eb4:e C4:e Bb3:q C4:q',
    'A3:e C4:e Eb4:e F4:e A4:q F4:q',
    'Bb4:q. r:e F4:e D4:e Bb3:q',
]), 16)

# Sparse version of the amendment that fits into the motion's breaths.
AMENDMENT_VOTES = B(' '.join([
    'G4:h r:h', 'r:h Eb4:q F4:q', 'r:h Bb4:h', 'G4:w',
    'G4:h r:h', 'r:h F4:q Eb4:q', 'D4:h r:h', 'Bb3:w',
    'Bb4:h r:h', 'r:h G4:q F4:q', 'Gb4:h Eb4:h', 'D4:w',
    'r:h D4:q F4:q', 'G4:h Eb4:h', 'C4:q Eb4:q F4:h', 'Bb3:w',
]), 16)


# ------------------------------------------------------------- filibuster
CH_FILIBUSTER = [
    'Gm7', 'Gm7', 'Cm7', 'D7', 'Gm7', 'Eb7', 'D7', 'D7',
    'Gm7', 'C7', 'Cm7', 'F7', 'Bb6', 'G7', 'C7', 'F7',
]
FILIBUSTER = B(' '.join([
    'r:e D6:e G6:q F6:e D6:e Bb5:q',
    'G5:e A5:e Bb5:e D6:e F6:q D6:q',
    'Eb6:e D6:e C6:e Bb5:e G5:q Bb5:q',
    'A5:q C6:e Eb6:e D6:e C6:e A5:q',
    'Bb5:e D6:e F6:e G6:e F6:q D6:q',
    'Db6:e Bb5:e G5:e F5:e Eb5:q G5:q',
    'F#5:e A5:e C6:e D6:e F6:q Eb6:q',
    'D6:q. C6:e A5:q F#5:q',
    'G5:e Bb5:e D6:e F6:e G6:e F6:e D6:e Bb5:e',
    'E6:e D6:e C6:e Bb5:e A5:e G5:e F#5:e G5:e',
    'C6:e Eb6:e G6:q F6:e Eb6:e C6:q',
    'A5:e C6:e Eb6:e F6:e G6:q F6:q',
    'D6:e F6:e G6:q F6:e Eb6:e D6:q',
    'B5:e D6:e F6:e G6:e G6:q F#6:q',
    'G6:e E6:e C6:e Bb5:e G5:e E5:e Db5:e C5:e',
    'A5:q. C6:e F6:q r:q',
]), 16)


# ------------------------------------------------------------- roll call
CORNET_BALLOT = B(' '.join([
    MOTION_BARS[0], MOTION_BARS[1],
    'D5:q F5:q Bb5:q C6:q', 'Bb5:q. A5:e F5:q D5:q',
]), 4)

CLARINET_BALLOT = B(' '.join([
    'r:e D6:e F6:e G6:q. r:e F6:e',
    'G6:e F6:e D6:e Bb5:e D6:e F6:e G6:e F6:e',
    'G6:e F6:e Eb6:e D6:e C6:e Bb5:e Db6:e D6:e',
    'F6:q D6:e Bb5:e F5:q r:q',
]), 4)

ALTO_BALLOT = B(' '.join([
    'r:e D4:e F4:e Bb4:q. r:e A4:e',
    'G4:e F4:q D4:e r:q C4:e Db4:e',
    'D4:q F4:e G4:e Bb4:q G4:q',
    'F4:q. D4:e Bb3:h',
]), 4)

TBN_BALLOT = B(' '.join([
    'r:q D3:e F3:e Bb3:q D4:q',
    'C4:q. A3:e F3:q D3:q',
    'F3:e Ab3:e A3:e Bb3:e D4:q F4:q',
    'Bb3:q. r:e F3:e D3:e Bb2:q',
]), 4)


# --------------------------------------------------------------- endings
REBUTTAL_CORNET = B(' '.join([
    'r:e C5:e E5:e G5:q. r:e Bb5:e', 'A5:q G5:e E5:e C5:q r:q',
    'r:e D5:e F5:e Bb5:q. r:e A5:e', 'G5:q F5:e D5:e C5:q r:q',
    'D5:e F5:e G5:e A5:e Bb5:q D5:q', 'C5:q. A4:e F4:h',
    'Eb5:e C5:e A4:e C5:e F5:q A5:q', 'Bb5:q. r:e F5:e D5:e Bb4:q',
]), 8)

FINAL_HOOK = B('D5:e F5:e Bb5:q A5:e G5:e F5:q D5:q Bb4:h r:q', 2)
