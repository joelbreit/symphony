"""One tune, two lives (docs/03). Concert pitch; E-flat home, A-flat for
the ramble. Every strain is B()-guarded — that catches almost every entry
error. Bars are 4/4 = 4 beats.

The cell is the hymn's call: G B-flat E-flat D C B-flat. Slow it is a
hymn line; syncopated, with the E-flat landing on the and-of-2, it is a
strut. The sousaphone riff, the shout chorus, and the benediction are all
the call.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib import B

# ---------------------------------------------------------------- the hymn
CH_HYMN = ['Eb', 'Eb', 'Ab', 'Bb7', 'Eb', 'Eb', 'Bb7', 'Eb',
           'Eb7', 'Ab', 'Abm', ('Eb/Bb', 'Bb7'), 'Eb', 'C7', ('F7', 'Bb7'), 'Eb']

HYMN_BARS = [
    'G4:q Bb4:q Eb5:h',            # 1  Eb    the call
    'D5:q. C5:e Bb4:h',            # 2  Eb    the fall
    'C5:q Ab4:q Bb4:q G4:q',       # 3  Ab
    'F4:h. r:q',                   # 4  Bb7   half cadence, breath
    'G4:q Bb4:q Eb5:h',            # 5  Eb
    'D5:q. C5:e Bb4:q G4:q',       # 6  Eb
    'F4:q G4:q Ab4:q F4:q',        # 7  Bb7
    'Eb4:h. r:q',                  # 8  Eb    settles low
    'Bb4:q Eb5:q G5:h',            # 9  Eb7   the climb
    'F5:q Eb5:q C5:h',             # 10 Ab
    'Cb5:h. Bb4:q',                # 11 Abm   the tear (C -> C-flat)
    'Ab4:q G4:q F4:h',             # 12 Eb/Bb, Bb7
    'G4:q Bb4:q Eb5:h',            # 13 Eb    the call
    'E5:q. D5:e C5:h',             # 14 C7    the light (E natural)
    'A4:q C5:q Bb4:q D5:q',        # 15 F7, Bb7
    'Eb5:w',                       # 16 Eb    amen
]
HYMN = B(' '.join(HYMN_BARS), 16)
HYMN_HALF2 = B(' '.join(HYMN_BARS[8:]), 8)

# trombone tenor line under the hymn (statement 1); smears added in compose
TBN_HYMN = B(' '.join([
    'Bb3:h G3:h', 'Bb3:h Eb3:h', 'C4:h Eb3:h', 'D3:h Ab3:h',
    'G3:h Bb3:h', 'G3:h Eb3:h', 'D3:h F3:h', 'G3:h. r:q',
    'G3:h Db4:h', 'C4:h Ab3:h', 'Cb4:h. Bb3:q', 'Bb3:h Ab3:h',
    'G3:h Bb3:h', 'Bb3:h. G3:q', 'A3:h Ab3:h', 'G3:w']), 16)

# clarinet descant above the hymn's second half (statement 1)
DESCANT = B(' '.join([
    'Bb5:w', 'C6:h Ab5:h', 'Cb6:h. Bb5:q', 'Ab5:h F5:h',
    'Bb5:w', 'Bb5:h. G5:q', 'A5:h Ab5:h', 'G5:w']), 8)

# alto harmony under the cry (hymn bars 9-16, clarinet an octave up)
CRY_HARMONY = B(' '.join([
    'G4:q Bb4:q Eb5:h', 'Ab4:q C5:q Ab4:h', 'Ab4:h. Eb4:q', 'Eb4:h D4:h',
    'Eb4:q G4:q G4:h', 'C5:q. Bb4:e G4:h', 'F4:q A4:q F4:q F4:q', 'G4:w']), 8)

# trombone in the cry: doubles the climb and the tear an octave down,
# then its own tenor line home
TBN_CRY = B(' '.join([
    'Bb3:q Eb4:q G4:h', 'F4:q Eb4:q C4:h', 'Cb4:h. Bb3:q', 'Ab3:q G3:q F3:h',
    'G3:h Bb3:h', 'Bb3:h. G3:q', 'A3:h Ab3:h', 'G3:w']), 8)

# the benediction: the call, the fall, and the amen — cornet alone
BENEDICTION = B('G4:q Bb4:q Eb5:h D5:q. C5:e Bb4:h Eb5:w', 3)

# ---------------------------------------------------------------- the strut
# The hymn cut loose: same pitches, the long notes moved onto the and-of-2,
# pickups and chromatic walk-ups in the seams, beat 4 of bars 4/8/12 open.
CH_STRUT = ['Eb', 'Eb', 'Ab', 'Bb7', 'Eb', 'Eb', 'Bb7', ('Eb', 'Bb7'),
            'Eb7', 'Ab', 'Abm', ('Eb/Bb', 'Bb7'), 'Eb', 'C7', ('F7', 'Bb7'), 'Eb']
CH_STRUT_TURN = CH_STRUT[:15] + [('Eb', 'Bb7')]

STRUT_P1 = B('G4:e Bb4:e r:e Eb5:q. r:e D5:q '
             'C5:e Bb4:q r:e r:q C5:e '
             'r:e Ab4:e Bb4:e G4:h r:e '
             'F4:h r:q Eb4:e F4:e', 4)
STRUT_P2 = B('G4:e Bb4:e r:e Eb5:q. r:e D5:q '
             'C5:e Bb4:e G4:q r:e G4:e Ab4:e A4:e '
             'Bb4:e r:e Ab4:q F4:q. '
             'Eb4:q r:e Eb4:e r:e G4:e Ab4:e A4:e', 4)
STRUT_P3 = B('Bb4:e Eb5:e r:e G5:q. r:e F5:q '
             'Eb5:e C5:q r:e r:q C5:e '
             'r:e Cb5:q. Bb4:q r:e Ab4:e '
             'G4:q. F4:e r:h', 4)
STRUT_P4 = B('G4:e Bb4:e r:e Eb5:q. r:e E5:q '
             'D5:e C5:q r:e r:q A4:e '
             'r:e C5:q. Bb4:e D5:q r:e '
             'Eb5:q. r:e Bb4:e G4:e Eb4:q', 4)
STRUT = B(' '.join([STRUT_P1, STRUT_P2, STRUT_P3, STRUT_P4]), 16)

# out-chorus variant: the climb goes to B-flat 5, the last bar rips up
STRUT_P3_OUT = B('Bb4:e Eb5:e r:e Bb5:q. r:e Ab5:q '
                 'G5:e F5:e Eb5:e C5:e r:q C5:e '
                 'r:e Cb5:q. Bb4:q r:e Ab4:e '
                 'G4:q. F4:e r:h', 4)
STRUT_P4_OUT = B('G4:e Bb4:e r:e Eb5:q. r:e E5:q '
                 'D5:e C5:q r:e r:q A4:e '
                 'r:e C5:q. Bb4:e D5:q r:e '
                 'Eb5:q. r:e G5:e Bb5:e Bb5:q', 4)
STRUT_OUT = B(' '.join([STRUT_P1, STRUT_P2, STRUT_P3_OUT, STRUT_P4_OUT]), 16)

# clarinet fills for the open beats (bar 4, 8, 12 of the strut): (bar, beat, dsl)
STRUT_FILLS = [
    (3, 2.0, 'Bb5:e C6:e D6:e F6:e'),
    (7, 2.5, 'Bb5:e G5:e Bb5:e'),
    (11, 2.0, 'F5:e Ab5:e Bb5:e D6:e'),
]

# ---------------------------------------------------------------- the turn
# the sousaphone riff: the call in the bass, two bars
SOUSA_RIFF = B('G1:e Bb1:e r:e Eb2:q. r:e D2:e C2:e Bb1:q r:e Eb1:e r:e Bb1:e r:e', 2)
# the cornet's first notes: the fall, alone, after one hit
CORNET_BREAK = B('r:e Eb5:e D5:e C5:e Bb4:e G4:e Eb4:e F4:e', 1)
# the turn for home: a rip and a two-bar run into the call
CORNET_TURN = B('Bb5:q. Ab5:e G5:e F5:e Eb5:e D5:e '
                'C5:e Bb4:e G4:e Bb4:e Eb5:e D5:e Eb4:e F4:e', 2)
# the tag: everyone plays the head in octaves
UNISON_TAG = B('G4:e Bb4:e r:e Eb5:q. r:e D5:q C5:e Bb4:q r:h', 2)

# ---------------------------------------------------------------- the ramble
CH_RAMBLE = ['Ab', 'Ab', 'Eb7', 'Eb7', 'Eb7', 'Eb7', 'Ab', ('Ab', 'Ab7'),
             'Db', 'Db', 'Dbm', 'Ab/Eb', 'F7', 'Bb7', 'Eb7', 'Ab']
CH_RAMBLE_TURN = CH_RAMBLE[:15] + [('Ab', 'Eb7')]

RAMBLE_BARS = [
    'r:e Eb5:e C5:e Ab4:e r:e C5:e Eb5:q',          # 1  Ab    the bounce
    'r:e Eb5:e C5:e Ab4:e r:e Ab4:e Bb4:e B4:e',    # 2  Ab    chromatic lean
    'C5:q. Bb4:e r:e G4:e Bb4:e Db5:e',             # 3  Eb7
    'C5:e Bb4:e G4:q. r:e Bb4:e Db5:e',             # 4  Eb7
    'Eb5:e Db5:e Bb4:e G4:e r:e Bb4:e Db5:q',       # 5  Eb7   the answer
    'r:e Db5:e Bb4:e G4:e r:e F4:e G4:e Ab4:e',     # 6  Eb7
    'C5:q r:e Eb5:e r:e C5:e Ab4:q',                # 7  Ab    stop-time
    'r:e C5:e Eb5:e C5:e Gb5:q. r:e',               # 8  Ab,Ab7
    'F5:e Db5:e r:e Ab4:e r:e Db5:e F5:q',          # 9  Db    the bounce on IV
    'r:e F5:e Db5:e Ab4:e r:e Ab4:e Db5:e F5:e',    # 10 Db
    'Fb5:q. Eb5:e Db5:q r:e Ab4:e',                 # 11 Dbm   the tear (F -> F-flat)
    'C5:e Ab4:e Eb4:q r:e Ab4:e A4:e Bb4:e',        # 12 Ab/Eb walk-up
    'C5:q. A4:e r:e F4:e A4:e C5:e',                # 13 F7
    'D5:q. Bb4:e Ab4:q F4:e D4:e',             # 14 Bb7
    'Eb4:e G4:e Bb4:e Db5:e C5:e Bb4:e G4:e Bb4:e', # 15 Eb7
    'Ab4:q. r:e Eb5:e C5:e Ab4:q',                  # 16 Ab
]
RAMBLE = B(' '.join(RAMBLE_BARS), 16)

# trombone's chorus on the ramble
TBN_RAMBLE = B(' '.join([
    'r:q Eb3:e Ab3:e C4:q. Bb3:e',                  # 1
    'Ab3:q. r:e Ab3:e Bb3:e B3:e C4:e',             # 2
    'Db4:h r:e Bb3:e G3:e Eb3:e',                   # 3
    'F3:q G3:q Bb3:q. Db4:e',                       # 4
    'C4:q. Bb3:e G3:q r:e Eb3:e',                   # 5
    'F3:e G3:e Bb3:e Db4:e Eb4:q. r:e',             # 6
    'C4:q r:e Eb4:e r:e C4:e Ab3:q',                # 7  stop-time, his way
    'r:e C4:e Eb4:e C4:e Gb4:q. r:e',               # 8
    'F3:h. Ab3:e Db4:e',                            # 9
    'F4:q. Eb4:e Db4:q Ab3:q',                      # 10 the high F
    'Fb4:h. Eb4:q',                                 # 11 the tear
    'Db4:q C4:q Eb3:h',                             # 12
    'A3:h. F3:e A3:e',                              # 13
    'D4:q Bb3:e Ab3:q. r:e F3:e',                   # 14
    'G3:e Bb3:e Db4:e Eb4:e Db4:e Bb3:e G3:e Eb3:e',# 15
    'Ab3:q. r:e C4:e Eb4:e Ab3:q']), 16)            # 16

# clarinet's chorus on the ramble (bar 5 has a written trill, see compose)
CLAR_RAMBLE = B(' '.join([
    'r:e Eb6:e C6:e Ab5:e r:e C6:e Eb6:e F6:e',     # 1
    'Eb6:e C6:e Ab5:e Eb5:e Ab5:e C6:e Eb6:q',      # 2
    'Db6:e. Bb5:s G5:e Bb5:e Db6:e Eb6:e Db6:e Bb5:e',  # 3
    'G5:q. Bb5:e Db6:t C6:t Bb5:t G5:e Eb5:e',      # 4  triplet turn
    'r:e Bb5:e Db6:e Eb6:e r:q. Eb6:e',             # 5  (trill fills the hole)
    'Db6:e Bb5:e G5:e Bb5:e Db6:e Bb5:e A5:e B5:e', # 6
    'C6:q r:e Eb6:e r:e C6:e Ab5:q',                # 7  stop-time
    'r:e Ab5:e C6:e Eb6:e Gb6:q. r:e',              # 8
    'F6:e Db6:e Ab5:e F5:e Ab5:e Db6:e F6:q',       # 9
    'F6:e Eb6:e Db6:e C6:e Db6:e Ab5:e F5:e Ab5:e', # 10
    'Fb6:q. Eb6:e Db6:q Ab5:q',                     # 11 the tear
    'C6:e Ab5:e Eb5:e Ab5:e C6:e Eb6:e F6:e Eb6:e', # 12
    'C6:q. A5:e F5:e A5:e C6:e Eb6:e',              # 13
    'D6:e F6:e D6:e Bb5:e Ab5:e F5:e D5:e F5:e',    # 14
    'G5:e Bb5:e Db6:e Eb6:e G6:q Eb6:e Db6:e',      # 15 the G6, once
    'C6:q. r:e Eb6:e C6:e Ab5:q']), 16)             # 16

# ---------------------------------------------------------------- the shout
CH_SHOUT = ['Ab', 'Ab', 'Eb7', 'Eb7', 'Eb7', 'Eb7', 'Ab', ('Ab', 'Ab7'),
            'Db', 'Db', 'Dbm', ('Ab/Eb', 'Eb7'), 'Ab', 'F7', ('Bb7', 'Eb7'), 'Ab']
# the call in A-flat, shouted; drummers answer beats 3-4 of bars 2/4/6/8
SHOUT = B(' '.join([
    'C5:e Eb5:e r:e Ab5:q. r:e G5:q',               # 1  Ab
    'F5:e Eb5:q r:h',                               # 2     (drums)
    'G4:e Bb4:e r:e Eb5:q. r:e Db5:q',              # 3  Eb7
    'C5:e Bb4:q r:h',                               # 4     (drums)
    'C5:e Eb5:e r:e Ab5:q. r:e G5:q',               # 5  Eb7 (sus into the third)
    'F5:e Eb5:q r:h',                               # 6     (drums)
    'C5:e Eb5:e r:e Ab5:q. r:e G5:q',               # 7  Ab
    'Gb5:e Eb5:q r:h',                              # 8     (drums) Gb -> Db
    'F5:e Ab5:e r:e Db6:q. r:e C6:q',               # 9  Db  the call, high
    'Bb5:e Ab5:q r:e r:q Ab5:e',                    # 10
    'r:e Fb5:q. Eb5:q r:e Db5:e',                   # 11 Dbm the tear
    'C5:q. Bb4:e r:h',                              # 12     (drum fill)
    'C5:e Eb5:e r:e Ab5:q. r:e A5:q',               # 13 Ab -> F7
    'G5:e F5:q r:e r:q D5:e',                       # 14 F7
    'r:e F5:q. Eb5:e G5:q r:e',                     # 15 Bb7, Eb7
    'Ab5:q. r:e Eb5:e C5:e Ab4:q']), 16)            # 16 Ab
SHOUT_ANSWERS = [(1, 2.0), (3, 2.0), (5, 2.0), (7, 2.0)]   # (bar, beat)
