"""The strains (docs/03). One 2/4 bar = 2 beats; every strain is guarded.

Naming the devices (docs/02 §4): the *snap* is s-e-s with the long note off
the grid; the *knocks* are short-short-long repeated notes (knock, knock);
the *tie* holds an off-beat sixteenth across the next beat; the *secondary
rag* accents every 3 sixteenths against the 4-grid.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib import B

M = (2, 4)

# ---------------------------------------------------------------- intro
# The walk-on: a chromatic strut down, the tonic arpeggio back up, a bow
# on Eb7 and a breath. Played in octaves by both hands (octified in
# compose.py).
INTRO_LINE = B(
    'Ab5:e. G5:s Gb5:e. F5:s '
    'E5:e. Eb5:s D5:e. Db5:s '
    'C5:s Eb5:s Ab5:s C6:s Bb5:s Ab5:s G5:s Eb5:s '
    'Db5:s Bb4:s G4:s Eb4:s Bb4:e r:e', 4, M)

# ---------------------------------------------------------------- A strain
# The setup. b1 the rising-arpeggio hook with the snap seesaw; b2 the
# knocks; b9-10 the tie over the beat; b15 lands the tonic a sixteenth
# early (the joke arrives before you're ready), b16's downbeat is empty —
# the deadpan.
A_BARS = [
    'C5:s Eb5:s Ab5:s C6:s Ab5:s C6:e Ab5:s',            # 1  Ab    hook
    'Bb5:s Bb5:s Bb5:e Eb5:s G5:s Bb5:s G5:s',           # 2  Ab    knocks
    'Ab5:s G5:s F5:s G5:s Eb5:e G5:s Bb5:s',             # 3  Eb7
    'Db6:s C6:s Bb5:s G5:s Bb5:e r:e',                   # 4  Eb7   breath
    'Bb4:s Db5:s G5:s Bb5:s G5:s Bb5:e G5:s',            # 5  Eb7   hook echo
    'Bb5:s Bb5:s Bb5:e G5:s Eb5:s Db5:s Bb4:s',          # 6  Eb7   knocks
    'C5:s Eb5:s Ab5:s Eb5:s C5:s Eb5:s Ab4:e',           # 7  Ab
    'Ab4:q r:e G4:s Bb4:s',                              # 8  Ab    pickup
    'Eb5:s G5:s Ab5:s C6:e Ab5:s Eb5:s G5:s',            # 9  Ab    the tie
    'Eb5:s Gb5:s Ab5:s C6:e Ab5:s Gb5:s Eb5:s',          # 10 Ab7   tilted
    'F5:s Ab5:s Db6:e Ab5:s F5:s Db5:e',                 # 11 Db
    'D5:s F5:s Ab5:e F5:s D5:s B4:e',                    # 12 Ddim7
    'C5:s Eb5:s Ab5:s C6:s Bb5:s Ab5:s G5:s Ab5:s',      # 13 Ab/Eb hook recall
    'A4:s C5:s Eb5:s F5:s A5:s F5:s Eb5:s C5:s',         # 14 F7
    'Bb4:s D5:s F5:s Ab5:s G5:s Eb5:s Db5:s Ab4:s',      # 15 Bb7,Eb7 — early!
    'r:e Eb5:s C5:s Ab4:q',                              # 16 Ab    deadpan
]
STRAIN_A = B(' '.join(A_BARS), 16, M)

# ---------------------------------------------------------------- B strain
# The topper: the secondary rag (3-note cells across the 4-grid) over the
# rag cycle III7 -> VI7 -> II7 -> V7, twice.
_B_CELLS_C = 'Bb5:s G5:s E5:s Bb5:s G5:s E5:s Bb5:s G5:s'    # C7 cells
_B_CELLS_F = 'A5:s F5:s C5:s A5:s F5:s C5:s A5:s F5:s'       # F7 cells
B_BARS = [
    _B_CELLS_C,                                          # 1  C7   3+3+2
    'E5:s Bb5:s G5:s E5:s G5:e C6:e',                    # 2  C7   snap out
    _B_CELLS_F,                                          # 3  F7
    'C5:s F5:s A5:s C6:s A5:e F5:e',                     # 4  F7
    'D5:s F5:s Ab5:s D6:s C6:s Ab5:s F5:s D5:s',         # 5  Bb7  the arch
    'Db6:s Bb5:s G5:e Bb5:s G5:s Eb5:e',                 # 6  Eb7
    'C6:s Eb6:s C6:s Ab5:s Eb5:s Ab5:s C6:s Eb5:s',      # 7  Ab
    'G5:s Bb5:s Db6:s Bb5:s G5:e r:e',                   # 8  Eb7  breath
    _B_CELLS_C,                                          # 9  C7
    'E5:s Bb5:s G5:s E5:s G5:e C6:e',                    # 10 C7
    _B_CELLS_F,                                          # 11 F7
    'C5:s F5:s A5:s C6:s A5:e F5:e',                     # 12 F7
    'F5:s D5:s Bb4:s D5:s F5:s Ab5:s Bb5:s D6:s',        # 13 Bb7  climb
    'Eb6:s Db6:s Bb5:s G5:s Eb5:s G5:s Bb5:s Db6:s',     # 14 Eb7
    'C6:s Ab5:s Eb5:s C5:s Db5:s Eb5:s G5:s Db6:s',      # 15 Ab,Eb7
    'C6:e Ab5:s C6:s Eb6:q',                             # 16 Ab   bright out
]
STRAIN_B = B(' '.join(B_BARS), 16, M)

# ---------------------------------------------------------------- C trio
# The aside, in Db: parallel sixths, long notes, the dynamic floor.
C_BARS = [
    '(Ab4 F5):q. (Bb4 G5):s (Ab4 F5):s',                 # 1  Db
    '(F4 Db5):e (Gb4 Eb5):e (Ab4 F5):q',                 # 2  Db
    '(Gb4 Eb5):q. (F4 Db5):s (Eb4 C5):s',                # 3  Ab7
    '(Eb4 C5):q (Gb4 Eb5):q',                            # 4  Ab7
    '(Ab4 F5):q. (Bb4 G5):s (C5 Ab5):s',                 # 5  Ab7  reaching
    '(Bb4 G5):e (Ab4 F5):e (Gb4 Eb5):q',                 # 6  Ab7
    '(F4 Db5):q. (Ab4 F5):s (Db5 Bb5):s',                # 7  Db
    '(Db5 Bb5):e (B4 Ab5):e (Ab4 F5):q',                 # 8  Db7
    '(Gb4 Eb5):q. (Ab4 F5):s (Bb4 Gb5):s',               # 9  Gb
    '(Bb4 Gb5):e (Ab4 F5):e (Gb4 Eb5):q',                # 10 Gb
    '(G4 E5):q. (Bb4 G5):s (Db5 Bb5):s',                 # 11 Gdim7
    '(Db5 Bb5):e (Bb4 G5):e (G4 E5):q',                  # 12 Gdim7
    '(Ab4 F5):q (Db5 Ab5):e (Eb5 C6):e',                 # 13 Db/Ab climbing
    '(D5 Bb5):q. (C5 Ab5):s (Bb4 F5):s',                 # 14 Bb7
    '(G4 Eb5):e (Bb4 G5):e (Ab4 Gb5):q',                 # 15 Eb7,Ab7
    '(F4 Db5):h',                                        # 16 Db   settle
]
STRAIN_C = B(' '.join(C_BARS), 16, M)

# ---------------------------------------------------------------- the pause
# Bar 121: right hand alone, rising up Eb7 — and it stops before the top.
# Bar 122 is written silence (no events at all).
PAUSE_BAR = B('Eb4:s G4:s Bb4:s Db5:s Eb5:s G5:s r:e', 1, M)

# ---------------------------------------------------------------- D strain
# The punch line: two stop-time bars (the right hand answers the stabs),
# then the rideout; the second half is A's second half verbatim — the
# punch line recycles the setup's own words.
D_BARS = [
    'r:e C5:s Eb5:s Ab5:e C6:e',                         # 1  Ab   stop-time
    'Bb5:s C6:s Bb5:s Ab5:s G5:s Eb5:s C5:s Bb4:s',      # 2  Ab   stop-time
    'C5:s E5:s G5:s Bb5:s G5:s Bb5:e G5:s',              # 3  C7   snap
    'C6:s Bb5:s G5:s E5:s G5:e C5:e',                    # 4  C7
    'C5:s F5:s A5:s C6:s A5:s C6:e A5:s',                # 5  F7   snap
    'F5:s A5:s C6:s Eb6:s C6:s A5:s F5:s C5:s',          # 6  F7
    'D5:s F5:s Ab5:s Bb5:s Ab5:s Bb5:e Ab5:s',           # 7  Bb7  snap
    'G5:s Bb5:s Db6:s Bb5:s G5:e Eb5:e',                 # 8  Eb7
] + A_BARS[8:]                                           # 9-16: the callback
STRAIN_D = B(' '.join(D_BARS), 16, M)

# ---------------------------------------------------------------- interlude
# Leaning in (bars 85-88): the hook shrinks to a sigh, Ab turns into Ab7,
# and a rising arpeggio hands the top voice to the trio's F5.
INT_BARS = [
    'Eb5:e C5:e Ab4:q',                                  # 85 Ab
    'E5:e C5:e Ab4:q',                                   # 86 Ab,Abaug
    'Gb4:s Ab4:s C5:s Eb5:s Gb5:s Eb5:s C5:s Ab4:s',     # 87 Ab7
    'Ab4:s C5:s Eb5:s Gb5:s Ab5:e Gb5:e',                # 88 Ab7
]
INTERLUDE = B(' '.join(INT_BARS), 4, M)

# ---------------------------------------------------------------- tag
# Shave and a haircut (bar 2 of it is written silence), two bits landing
# off the beat — the last wink. The final chord lives in compose.py.
TAG_1 = B('Ab4:e Eb4:s Eb4:s F4:e Eb4:e', 1, M)          # shave and a haircut
TAG_3 = B('r:e G4:e Ab4:q', 1, M)                        # ... two bits
