"""Cyclic thematic material shared across movements.

The Question (motto): G–C–Eb–D — rising 4th, rising minor 3rd, falling
semitone, never resolving to C until the finale's Answer: G–C–E–D–C.
"""

# canonical slow form (5 ql + held note shaped per context)
MOTTO = 'G4:q C5:h Eb5:q D5:w'
MOTTO_HEAD = 'G4:q C5:h'          # the rising 4th alone
MOTTO_TAIL = 'Eb5:q D5:h'         # the fall that never lands

# The Answer — finale only. Major third, and the resolution granted.
ANSWER = 'G4:h C5:h E5:h D5:h C5:w'

# Movement I, Theme 1 — Allegro con fuoco, C minor. Motto in diminution,
# driving eighths. 8 bars of 4/4.
T1 = (
    'G4:e C5:e C5:e C5:e Eb5:e D5:e C5:e D5:e '
    'Eb5:e F5:e G5:h. '
    'F5:e Eb5:e D5:e C5:e B4:e C5:e D5:e B4:e '
    'C5:q G4:q Eb4:q G4:q '
    'Bb4:e Eb5:e Eb5:e Eb5:e G5:e F5:e Eb5:e F5:e '
    'G5:e Ab5:e Bb5:h. '
    'Ab5:e G5:e F5:e Eb5:e D5:e C5:e B4:e D5:e '
    'C5:q Eb5:q G5:q C6:q'
)
T1_HEAD = 'G4:e C5:e C5:e C5:e Eb5:e D5:e C5:e D5:e'  # bar 1 only

# Movement I, Theme 2 — lyric, opens with the motto's rising 4th made
# gentle (Bb up to Eb), then long-breathed steps. 8 bars, written in Eb.
T2 = (
    'Bb4:q. C5:e Eb5:q F5:q '
    'G5:h F5:q Eb5:q '
    'Ab5:q. G5:e F5:e Eb5:e C5:q '
    'Bb4:h. Eb5:q '
    'G5:q. Ab5:e Bb5:q G5:q '
    'C6:h Bb5:q Ab5:q '
    'G5:q Eb5:q F5:q D5:q '
    'Eb5:h. r:q'
)

# Movement II scherzo cell — falling G-minor arpeggio, one bar of 3/4.
SCHERZO_CELL = 'D5:e Bb4:e G4:e Bb4:e D5:e G5:e'

# Movement III theme opens with the motto in MAJOR (Eb-Ab-C-Bb in Ab):
# the almost-answer — still denied its final note.
HYMN_OPEN = 'Eb4:q Ab4:h C5:q Bb4:h.'
