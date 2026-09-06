"""The theme, its modes, and the material of the middle section.

Every melody is bar-guarded: `B(dsl, n_bars, (3, 4))` fails the build if it
does not span exactly n bars of 3/4. Almost every note-entry error this piece
made was caught here rather than in the render.

The theme is bounded by the pulse note at both ends — it begins on A4 and
ends on A4 — and its only difference between the two modes is F natural
becoming F sharp in bars 2 and 7. Bar 5's F stays natural in both: it is the
fifth of the B-flat chord, and F sharp over B-flat is an augmented triad, not
a brighter one.
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib.dsl import B, events                                       # noqa: E402

THREE = (3, 4)

#                bar 1            bar 2         bar 3        bar 4
THEME_MIN = B('A4:q D5:q E5:q  F5:h E5:q   D5:h C5:q   A4:h. '
              #  bar 5            bar 6         bar 7            bar 8
              'Bb4:q D5:q F5:q  G5:h E5:q   F5:q E5:q D5:q  E5:q C#5:q A4:q',
              8, THREE)

THEME_MAJ = B('A4:q D5:q E5:q  F#5:h E5:q  D5:h C5:q   A4:h. '
              'Bb4:q D5:q F5:q  G5:h E5:q   F#5:q E5:q D5:q  E5:q C#5:q A4:q',
              8, THREE)

# the voice a sixth below — S5's warmth, and the inner line of the anthem
SIXTH_MIN = B('C4:q F4:q G4:q   A4:h G4:q   F4:h E4:q   C4:h. '
              'D4:q F4:q A4:q   Bb4:h G4:q  A4:q G4:q F4:q  G4:q E4:q C4:q',
              8, THREE)

SIXTH_MAJ = B('C4:q F#4:q G4:q  A4:h G4:q   F#4:h E4:q  C#4:h. '
              'D4:q F#4:q A4:q  Bb4:h G4:q  A4:q G4:q F#4:q  G4:q E4:q C#4:q',
              8, THREE)

# first half alone — the first reading, and the collapse after the storm
HALF_MIN = B('A4:q D5:q E5:q  F5:h E5:q  D5:h C5:q  A4:h.', 4, THREE)
HALF_MAJ = B('A4:q D5:q E5:q  F#5:h E5:q  D5:h C5:q  A4:h.', 4, THREE)

# --- the middle section -------------------------------------------------
# Five eighths against a six-eighth bar: the cell never lands in the same
# place twice until the sixth bar. Only A and E — the dominant's bare frame,
# indifferent to whatever chord the ground is under it.
#
# It opens on A7 — the pulse's own pitch, and for these three statements the
# pulse is *inside* the cell rather than on the downbeat. That is the whole
# section: the signal we had nailed to bar lines turns out to keep its own
# clock, and walks off ours one eighth per bar.
CELL_HI = 'A7:e A6:e E6:e r:e r:e'
# The same two notes four octaves down on a seven-eighth period: one signal,
# two speeds, neither of them ours. Low enough to be unambiguously the left
# hand's, which the ground also owns — so it yields wherever they collide.
CELL_LO = 'A3:e r:e E3:e r:e r:e r:e r:e'          # seven, against six and five

# what is left when the cell breaks: a question that stops on the leading tone
QUESTION = B('F4:h. A4:h. C#5:h.', 3, THREE)

# --- the hinge ----------------------------------------------------------
# The first F sharp in the piece, and the second. Nothing else changes.
HINGE_1 = 'F#4:q'
HINGE_2 = B('F#5:h. ', 1, THREE)


def per_beat(notes, n_beats: int = 24) -> list:
    """The melody pitch sounding on each beat — held notes repeat.

    Chordal statements need a note per beat (the tune is the top of the
    chord); the theme has half notes in it, so it has to be resampled.
    """
    out, t, cur = [], 0.0, None
    grid = {}
    for pitch, dur in events(notes):
        if pitch is not None:
            grid[round(t, 6)] = pitch if isinstance(pitch, int) else pitch[-1]
        t += float(dur)
    for k in range(n_beats):
        cur = grid.get(float(k), cur)
        out.append(cur)
    return out


def onset_beats(notes) -> set:
    """Beats where the theme actually re-articulates (for accenting)."""
    out, t = set(), 0.0
    for pitch, dur in events(notes):
        if pitch is not None:
            out.add(round(t, 6))
        t += float(dur)
    return out
