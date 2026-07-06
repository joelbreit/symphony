"""'The beacon call' — the one melody, and its diminution schedule (docs/03).

One tango tune carries the whole piece; each return is more compressed and
more ornamented, until at re-entry only its rhythm is left. All material is
B()-guarded. Concert pitch, A minor; other keys via transpose.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib import B

# The gravity well: one chord per bar, the tetrachord descending twice per
# phrase. Phrase B answers from the iv side through the B-flat Phrygian lean.
CHORDS_A = ['Am', 'G', 'F', 'E7', 'Am', 'G', 'F', 'E7']
CHORDS_B = ['Dm', 'C', 'Bb', 'E7', 'Am', 'F', 'E7b9', 'Am']

# -- cantando: the full theme (Apogee I) ---------------------------------
# Phrase A (pregunta): the three-note rise that leaps to a held call, then
# sighing descents; bar 4 tumbles down E7 with the b9 (F natural) burning.
PHRASE_A1 = B(
    'A4:e B4:e C5:q E5:h '
    'F5:e E5:e D5:q. C5:e B4:q '
    'A4:e B4:e C5:q A5:h '
    'G#5:e F5:e E5:q. D5:e C5:e B4:e', 4)
PHRASE_A2 = B(
    'C5:q. B4:e A4:e G#4:e A4:e B4:e '
    'C5:e D5:e E5:q. F5:e E5:e D5:e '
    'E5:e D5:e C5:q. B4:e C5:e D5:e '
    'B4:h. G#4:q', 4)
PHRASE_A = B(PHRASE_A1 + ' ' + PHRASE_A2, 8)

# Phrase B (respuesta): reaches the peak through Bb, settles home late —
# the last note lands after the harmony has already resolved.
PHRASE_B1 = B(
    'F5:q. E5:e F5:e G5:e A5:q '
    'G5:e E5:e C5:q E5:q G5:q '
    'F5:e G5:e A5:q Bb5:q. A5:e '
    'G#5:e A5:e F5:q E5:q. r:e', 4)
PHRASE_B2 = B(
    'C5:e E5:e A5:q. G5:e F5:e E5:e '
    'D5:e E5:e F5:q A5:q G5:e F5:e '
    'E5:q C5:e B4:e F5:q. E5:e '
    'E5:e C5:e B4:q A4:h', 4)
PHRASE_B = B(PHRASE_B1 + ' ' + PHRASE_B2, 8)

# Violin countermelody under phrase B: a guide-tone line in long bows.
COUNTER_B = B(
    'A4:h F4:h '
    'G4:w '
    'F4:h D5:h '
    'B4:h. G#4:q '
    'C5:h A4:h '
    'A4:h C5:h '
    'B4:h F4:h '
    'A4:w', 8)

# -- ritmico: the theme on the marcato grid (Perigee I) -------------------
# Same skeleton, snapped to 3-3-2 accents, staccato; the leap inverted —
# the ritmico version starts at the top and falls.
RITMICO = B(
    'E5:q. C5:e A4:e r:e A4:q '
    'B4:q. G4:e B4:e r:e D5:e B4:e '
    'F5:q. C5:e A4:e r:e A5:q '
    'G#5:e F5:e E5:e D5:e C5:e B4:e G#4:e E4:e '
    'E5:q. C5:e A4:e r:e C5:e E5:e '
    'D5:q. B4:e G4:e r:e G4:e B4:e '
    'C5:e C5:e C5:q A4:e F4:e A4:q '
    'B4:e E5:e G#4:q E4:e r:e B4:q', 8)

# -- halved: note values cut in two, phrase A in four bars (Perigee II) ----
CELL4 = B(
    'A4:s B4:s C5:e E5:q F5:s E5:s D5:e. C5:s B4:e '
    'A4:s B4:s C5:e A5:q G#5:s F5:s E5:e. D5:s C5:s B4:s '
    'C5:e. B4:s A4:s G#4:s A4:s B4:s C5:s D5:s E5:e. F5:s E5:s D5:s '
    'E5:s D5:s C5:e. B4:s C5:s D5:s B4:q. G#4:e', 4)
# where the mordents land when the heat rises: (offset beats, pitch)
CELL4_HEADS = [(0.0, 'A4'), (4.0, 'A4'), (8.0, 'C5'), (13.0, 'E5')]

# -- the essence: rise, leap, b9 tumble, in two bars (Perigee III) ---------
CELL2 = B(
    'A4:s B4:s C5:s E5:s A5:e. G#5:s F5:e E5:e D5:e C5:e '
    'B4:e C5:s D5:s B4:q G#4:e E4:e r:q', 2)
CELL2_HEADS = [(0.0, 'A4'), (1.5, 'A5'), (4.0, 'B4')]

# -- the first gesture alone (Apogee III) ----------------------------------
GESTURE = B(
    'A4:e B4:e C5:q E5:h '
    'F5:e E5:e D5:q. C5:e B4:q', 2)

# -- rhythm only (re-entry): the ritmico bar's attacks, one pitch ----------
# hits at 1, the and-of-2, 4 — written in compose.py on hammered octaves.
RHYTHM_332 = [(0.0, 1.5), (1.5, 1.5), (3.0, 1.0)]
