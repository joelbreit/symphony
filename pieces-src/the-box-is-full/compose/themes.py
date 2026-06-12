"""Source material for "The Box Is Full" — Korobeiniki exactly as extracted
from tune.mxl (G minor), plus the derived cells and re-keyed versions.

All strings are in the common.py DSL. A1/A2 are 4 bars each; B is 8 bars.
"""

# --- the tune, verbatim from the source arrangement (G minor) -------------

# m1-4: the famous phrase (with the source's turn ornament on m1 beat 3)
A1 = ('D5:q A4:e Bb4:e C5:e D5:s C5:s Bb4:e A4:e '
      'G4:q G4:e Bb4:e D5:q C5:e Bb4:e '
      'A4:q. Bb4:e C5:q D5:q '
      'Bb4:q G4:q G4:q r:q')

# plain version (no turn) for heavy unison / double-time statements
A1_PLAIN = ('D5:q A4:e Bb4:e C5:q Bb4:e A4:e '
            'G4:q G4:e Bb4:e D5:q C5:e Bb4:e '
            'A4:q. Bb4:e C5:q D5:q '
            'Bb4:q G4:q G4:q r:q')

# m5-8: the off-beat answer (C minor / E-flat excursion)
A2 = ('r:e C5:q Eb5:e G5:q F5:e Eb5:e '
      'r:e D5:q Bb4:e D5:q C5:e Bb4:e '
      'A4:q. Bb4:e C5:q D5:q '
      'Bb4:q G4:q G4:q r:q')

# m9-16: the chorale of descending thirds ("Music B"); ends on the half
# cadence F# over D7 — the loop point
B = ('D5:h Bb4:h C5:h A4:h Bb4:h G4:h F#4:h A4:h '
     'D5:h Bb4:h C5:h A4:h Bb4:q D5:q G5:h F#5:w')

# --- the tetromino cell (first four notes) --------------------------------
# entry rhythm + a held "lock" note
T_CELL  = 'D5:q A4:e Bb4:e C5:h'          # the piece as it falls
T_INV   = 'D5:q G5:e F#5:e E5:h'          # inversion about D ("rotated")
T_RETRO = 'C5:q Bb4:e A4:e D5:h'          # retrograde ("rotated again")

# double-time A1 (each value halved; 2 bars total) for the kill screen
A1_DT = ('D5:e A4:s Bb4:s C5:e Bb4:s A4:s '
         'G4:e G4:s Bb4:s D5:e C5:s Bb4:s '
         'A4:e. Bb4:s C5:e D5:e '
         'Bb4:e G4:e G4:e r:e')

# kill-screen fragment: the cell at double time, 2 ql, loopable
T_DT = 'D5:e A4:s Bb4:s C5:e r:e'

# --- re-keyed B theme ------------------------------------------------------

# E-flat major (the rye field): same scale-degree contour, warm major
B_EB = ('Bb4:h G4:h Ab4:h F4:h G4:h Eb4:h D4:h F4:h '
        'Bb4:h G4:h Ab4:h F4:h G4:q Bb4:q Eb5:h D5:w')

# D major (the TETRIS blaze): recomposed to resolve UP to the tonic —
# the only time in the piece the tune is allowed to resolve
B_D = ('A4:h F#4:h G4:h E4:h F#4:h D4:h C#4:h E4:h '
       'A4:h F#4:h G4:h E4:h F#4:q A4:q D5:h D5:w')

# --- harmony grids (one chord per bar) -------------------------------------

# A section: D7 Gm D7 Gm | Cm Bb D7 Gm   (verbatim from the source)
CH = {
    'D7': ['D', 'F#', 'A', 'C'],
    'Gm': ['G', 'Bb', 'D'],
    'Cm': ['C', 'Eb', 'G'],
    'Bb': ['Bb', 'D', 'F'],
}
A1_BARS = ['D7', 'Gm', 'D7', 'Gm']
A2_BARS = ['Cm', 'Bb', 'D7', 'Gm']
B_BARS  = ['Gm', 'D7', 'Gm', 'D7', 'Gm', 'D7', 'Bb', 'D7']

# oom-pah bass per chord (source tuba: fifth-root on D7, root-fifth on Gm)
OOMPAH = {
    'D7': 'A2:q D2:q A2:q D2:q',
    'Gm': 'G2:q D2:q G2:q D2:q',
    'Cm': 'C3:q G2:q C3:q G2:q',
    'Bb': 'Bb2:q F2:q Bb2:q F2:q',
}
