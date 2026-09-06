"""Still Turning — a passacaglia on a dead star, for solo piano.

Twenty-seven statements of eight bars, one tempo, one bass line, one change
of mode. The bar map is docs/03; the reasons are docs/01 and docs/02.

    ../../.venv/bin/python src/compose.py     (from pieces-src/still-turning/)
"""
import pathlib
import sys
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from lib import Piece, assess, keyboard, midi_report                # noqa: E402
from lib.ensemble import solo_piano                                 # noqa: E402
from lib.pitch import midi, pitch_name                              # noqa: E402

import ground as G                                                  # noqa: E402
import themes as T                                                  # noqa: E402
from ground import BAR, PNO, above, arc, bass, chord_on, pool, \
    pulse, roll_to, st                                              # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / 'output'

MINOR, MAJOR = False, True
TRIPLET = Fraction(1, 3)


# ====================================================================== #
#  shared textures                                                       #
# ====================================================================== #
def lh_run(p, bar: int, i: int, major: bool, unit, vel: int, top: int = 21,
           gate: float = 0.92, accent: int = 7, beats: int = 3):
    """The left hand sweeps up (and back down) the chord for one bar, always
    *starting on the ground note*. The ladder's first rung and its last."""
    g = G.GROUND[i % 8]
    n = int(round(beats / float(unit)))
    seq = arc(pool(i, major, g, g + top), n)
    for k, pitch in enumerate(seq):
        v = vel + (accent if k == 0 else 0) - (2 if k % 2 else 0)
        p.add(PNO, p.bar(bar) + k * float(unit), [(pitch, unit)],
              vel=max(1, min(127, v)), gate=gate, swing=False)


def lh_broken_octaves(p, bar: int, i: int, major: bool, vel: int,
                      unit: float = 0.5, gate: float = 0.72):
    """Broken octaves climbing the chord: low, its octave, next tone, its
    octave. Hammering where `lh_run` sweeps — the same subdivision, a
    completely different hand and a completely different sound. The ground
    note is still the first thing the bar plays."""
    g = G.GROUND[i % 8]
    tones = pool(i, major, g, g + 9)[:3]
    while len(tones) < 3:
        tones.append(tones[-1])
    n = int(round(BAR / unit))
    for k in range(n):
        pitch = tones[k // 2] + (12 if k % 2 else 0)
        p.add(PNO, p.bar(bar) + k * unit, [(pitch, unit)],
              vel=max(1, vel + (7 if k == 0 else 0) - (k % 2) * 3),
              gate=gate, swing=False)


def lh_rocking(p, bar: int, i: int, major: bool, vel: int,
               unit: float = 0.25, gate: float = 0.8):
    """The ground note on every other sixteenth, with a line walking above it.

    A murky bass — the oldest way a keyboard fakes sustain, and here it does
    something the piece wants anyway: at the tightest point of the ladder the
    ground is sounding six times a bar instead of once. It is impossible to
    lose. The upper note stays inside a 12th so the hand can oscillate at
    speed rather than leap.
    """
    g = G.GROUND[i % 8]
    ups = pool(i, major, g + 7, g + 17) or [g + 7]
    n = int(round(BAR / unit))
    for k in range(n):
        low = k % 2 == 0
        pitch = g if low else ups[min((k // 2) % (2 * len(ups)),
                                      2 * len(ups) - 1 - (k // 2) % (2 * len(ups)))
                                  if len(ups) > 1 else 0]
        p.add(PNO, p.bar(bar) + k * unit, [(pitch, unit)],
              vel=max(1, vel + (7 if k == 0 else 0) - (0 if low else 4)),
              gate=gate, swing=False)


def rh_cascade(p, bar: int, i: int, major: bool, mel: list, vel: int,
               unit=Fraction(1, 4), beats=(0, 1, 2)):
    """Sixteenths in the right hand with the tune on top of every beat: the
    melody note, then chord tones falling away from it. The theme survives
    inside the torrent because the ear hears the top of each group."""
    per = int(round(1.0 / float(unit)))
    for beat in beats:
        top = mel[beat]
        under = [x for x in pool(i, major, top - 16, top - 1)][::-1][:per - 1]
        while len(under) < per - 1:
            under.append(under[-1] - 12 if under else top - 12)
        for k, pitch in enumerate([top] + under):
            p.add(PNO, p.bar(bar) + beat + k * float(unit), [(pitch, unit)],
                  vel=max(1, min(127, vel + (9 if k == 0 else -4))),
                  gate=0.9, swing=False)


def lay_cell(p, bar0: int, n_bars: int, cell: str, vel: int, period: float,
             gate: float = 0.9, fade: int = 0, offset: float = 0.0,
             yield_to_ground: bool = False):
    """Repeat a cell across a span on its own period, truncated at the end —
    the middle section's whole idea. A five-eighth cell in a six-eighth bar
    never lands twice in the same place.

    `yield_to_ground` drops any note that would land on a downbeat: the hand
    playing this cell is the hand playing the ground, and the ground wins.
    The cell develops holes as it drifts, which is what it should sound like.
    """
    from lib.dsl import events
    t0, end = p.bar(bar0), p.bar(bar0 + n_bars) + offset
    t0 += offset
    k, ev = 0, events(cell)
    downbeats = {round(p.bar(b), 4) for b in range(bar0, bar0 + n_bars + 1)}
    while t0 + k * period < end:
        base = t0 + k * period
        frac = (base - t0) / max(1e-9, end - t0)
        t = base
        for pitch, dur in ev:
            if (pitch is not None and t < end
                    and not (yield_to_ground and round(t, 4) in downbeats)):
                p.add(PNO, t, [(pitch, dur)], vel=max(1, vel + int(fade * frac)),
                      gate=gate, swing=False)
            t += float(dur)
        k += 1


def filled_octave(i: int, major: bool, m: int) -> list:
    """[m, a chord tone inside the octave, m+12] — a filled octave.

    Melody in bare octaves is bright and thin; a real pianist puts a chord
    tone in the middle of the right hand and the tune stops sounding hollow.
    Still an octave across, so still one hand.

    Near the middle of the octave is the goal, but not at the price of
    striking a tritone against the tune in the same hand — over the ♭VII the
    theme is already sitting on the tonic's third, which is a bright ♯11 with
    the chord underneath it and a much harder sound doubled inside the fist.
    """
    inner = pool(i, major, m + 2, m + 11)
    if not inner:
        return [m, m + 12]
    best = min(inner, key=lambda x: abs(x - (m + 7)) + (12 if (x - m) % 12 == 6
                                                        else 0))
    return [m, best, m + 12]


def waltz_lh(p, bar: int, i: int, major: bool, vel: int, floor_add: int = 17,
             n: int = 2, low_octave=False, unit: float = 1.0):
    """Bass on one, open chord tones on two and three. The accompaniment
    that carries most of the quiet half of the piece."""
    g = G.GROUND[i % 8]
    bass(p, bar, i, vel, dur=1.0, low_octave=low_octave, gate=0.95)
    tones = above(i, major, g + floor_add, n)
    steps = int(round(2.0 / unit))
    for s in range(steps):
        chord_on(p, p.bar(bar) + 1.0 + s * unit, tones, unit * 0.95,
                 vel - 6 - (s % 2) * 2)


# ====================================================================== #
#  I. a bit of scruff  (bars 1-8, one pulse per beat)                    #
# ====================================================================== #
def scruff(p):
    p.mark('a bit of scruff', p.bar(1))
    # The pulses nobody had noticed yet are the ones missing here: this is
    # the chart trace, not the star. From bar 5 on, none are missed again.
    ticks = {1: [(0, 50), (2, 47)],
             2: [(1, 48)],
             3: [(0, 50), (1, 53), (2, 51)],
             4: [(0, 54), (2, 56)],
             5: [(0, 55), (1, 54), (2, 58)],
             6: [(0, 58), (1, 60), (2, 59)],
             7: [(0, 61), (1, 63), (2, 62)],
             8: [(0, 64), (1, 67), (2, 71)]}
    for b, beats in ticks.items():
        for beat, vel in beats:
            p.add(PNO, p.bar(b) + beat, [(G.PULSE, 0.9)], vel=vel, gate=0.85,
                  swing=False, rigid=True)

    p.note(PNO, p.bar(3), 'D1', BAR, vel=40, swing=False)          # something low
    p.add(PNO, p.bar(5), [([midi('D1'), midi('A1')], BAR)], vel=44, swing=False)
    # two bars of the ground, guessed at, and dropped again
    p.cue('the first guess', p.bar(6))
    p.note(PNO, p.bar(6), 'D2', BAR, vel=50, swing=False)
    p.note(PNO, p.bar(7), 'C2', BAR, vel=52, swing=False)
    for b in (3, 5, 6, 7):
        p.pedal(PNO, p.bar(b) - 0.02, p.bar(b) + BAR - 0.2)


# ====================================================================== #
#  II. the ground  (S1-S5)                                               #
# ====================================================================== #
def the_ground(p):
    b = st(1)
    p.mark('the ground', p.bar(b))
    p.cue('the lock', p.bar(b))
    p.tempo(p.bar(b), G.BPM, 'the rate has not changed')
    for i in range(8):                      # S1 — the bass, alone
        bass(p, b + i, i, 52 + (i % 2))
        pulse(p, b + i, 54)
    G.pedal_bars(p, b, 8)

    b = st(2)                               # S2 — bare fifths
    for i in range(8):
        g = G.GROUND[i]
        p.add(PNO, p.bar(b + i), [([g, g + 7], BAR)], vel=56, gate=0.98,
              swing=False)
        pulse(p, b + i, 56)
    G.pedal_bars(p, b, 8)


def first_reading(p):
    b = st(3)
    p.mark('the first reading', p.bar(b))
    for i in range(8):                      # S3 — half a theme, then nothing
        waltz_lh(p, b + i, i, MINOR, 52)
        if i >= 4:                          # the theme stops; it is still there
            pulse(p, b + i, 54)
    p.add(PNO, p.bar(b), T.HALF_MIN, vel=64, gate=0.97)
    G.pedal_bars(p, b, 8)

    b = st(4)                               # S4 — the theme, complete
    for i in range(8):
        waltz_lh(p, b + i, i, MINOR, 56)
    p.add(PNO, p.bar(b), T.THEME_MIN, vel=70, gate=0.97)
    G.pedal_bars(p, b, 8)

    b = st(5)                               # S5 — in sixths, the hand rocking
    for i in range(8):
        waltz_lh(p, b + i, i, MINOR, 58, unit=0.5)
    p.add(PNO, p.bar(b), T.THEME_MIN, vel=76, gate=0.97)
    p.add(PNO, p.bar(b), T.SIXTH_MIN, vel=66, gate=0.97)
    G.pedal_bars(p, b, 8)


# ====================================================================== #
#  III. sidereal  (S6-S8) — the signal keeps a clock that is not ours     #
# ====================================================================== #
def sidereal(p):
    b = st(6)
    p.mark('sidereal', p.bar(b))
    for i in range(8):                      # S6 — five against six
        bass(p, b + i, i, 46)
    lay_cell(p, b, 8, T.CELL_HI, 52, period=2.5)

    b = st(7)                               # S7 — and seven against both
    p.mark('little green men', p.bar(b))
    for i in range(8):
        bass(p, b + i, i, 48, dur=1.0)
    lay_cell(p, b, 8, T.CELL_HI, 56, period=2.5)
    lay_cell(p, b, 8, T.CELL_LO, 50, period=3.5, offset=0.5,
             yield_to_ground=True)

    b = st(8)                               # S8 — it breaks; a question
    for i in range(8):
        bass(p, b + i, i, 46 - i)
    lay_cell(p, b, 4, T.CELL_HI, 54, period=2.5, fade=-14)
    lay_cell(p, b, 4, T.CELL_LO, 46, period=3.5, fade=-12, offset=0.5,
             yield_to_ground=True)
    p.cue('the question', p.bar(b + 5))
    p.add(PNO, p.bar(b + 5), T.QUESTION, vel=56, vel_end=46, gate=0.99)
    G.pedal_bars(p, b + 5, 3)


# ====================================================================== #
#  IV. not a message  (S9-S13) — the subdivision ladder                  #
# ====================================================================== #
def the_ladder(p):
    b = st(9)                               # S9 — eighths
    p.mark('not a message', p.bar(b))
    for i in range(8):
        lh_run(p, b + i, i, MINOR, 0.5, 46, top=19)
    p.add(PNO, p.bar(b), T.THEME_MIN, vel=68, gate=0.97)
    G.pedal_bars(p, b, 8)

    b = st(10)                              # S10 — broken octaves: the hammer
    for i in range(8):
        lh_broken_octaves(p, b + i, i, MINOR, 54)
    mel = T.per_beat(T.THEME_MIN)
    p.add(PNO, p.bar(b), T.THEME_MIN, vel=76, gate=0.97)
    p.add(PNO, p.bar(b), T.THEME_MIN, vel=72, gate=0.97, transpose=12)
    G.pedal_bars(p, b, 8)

    b = st(11)                              # S11 — triplets; tune in the thumb
    for i in range(8):
        lh_run(p, b + i, i, MINOR, TRIPLET, 56, top=26)
        for beat in range(3):
            top = mel[i * 3 + beat]
            chord_on(p, p.bar(b + i) + beat, [top] + above(i, MINOR, top + 1, 2),
                     0.95, 66, top_vel=-6)
    G.pedal_bars(p, b, 8)

    b = st(12)                              # S12 — the murky bass: the shimmer
    for i in range(8):
        lh_rocking(p, b + i, i, MINOR, 61)
    p.add(PNO, p.bar(b), T.THEME_MIN, vel=82, gate=0.97)
    p.add(PNO, p.bar(b), T.THEME_MIN, vel=78, gate=0.97, transpose=12)
    G.pedal_halves(p, b, 8)

    b = st(13)                              # S13 — sixteenths in both hands
    for i in range(8):
        lh_run(p, b + i, i, MINOR, 0.25, 58, top=26, gate=0.85)
        rh_cascade(p, b + i, i, MINOR, mel[i * 3:i * 3 + 3], 70 + i,
                   beats=(0, 1, 2) if i < 7 else (0, 1))   # a breath first
    G.pedal_halves(p, b, 8)


# ====================================================================== #
#  V. the storm  (S14-S16) — the false summit, and its collapse          #
# ====================================================================== #
def the_storm(p):
    b = st(14)
    p.mark('the storm', p.bar(b))
    mel = T.per_beat(T.THEME_MIN)
    for i in range(8):
        g = G.GROUND[i]
        # the pulse comes back as the top of a rolled chord, landing on the
        # beat — one roll per hand, because that is how it would be played
        chord_on(p, p.bar(b + i), [g, g + 12], 1.0, 83)
        roll_to(p, pool(i, MINOR, 69, G.PULSE_LOW - 1)[-3:] + [G.PULSE_LOW],
                p.bar(b + i), 81, spread=0.05, dur=1.0, voice_top=10,
                rigid_top=True)
        for beat in (1, 2):
            top = mel[i * 3 + beat]
            chord_on(p, p.bar(b + i) + beat,
                     [x for x in pool(i, MINOR, top - 15, top - 3)][-2:] + [top],
                     0.95, 81, top_vel=10)
    G.pedal_bars(p, b, 8, release=0.10)

    b = st(15)                              # S15 — the minor summit
    for i in range(8):
        g = G.GROUND[i]
        roll_to(p, [g - 12, g, g + 7], p.bar(b + i), 88, spread=0.04, dur=1.2)
        for k in range(6):                  # the left hand keeps churning
            seq = arc(pool(i, MINOR, g + 12, g + 26)[:5], 6)
            p.add(PNO, p.bar(b + i) + 1.0 + k * 0.25, [(seq[k], 0.25)],
                  vel=77 - (k % 2) * 4, gate=0.88, swing=False)
        top = mel[i * 3]
        tops = ([top, top + 12, G.PULSE_LOW] if top + 12 < G.PULSE_LOW
                else [top, top + 12])
        roll_to(p, tops, p.bar(b + i), 95, spread=0.035, dur=BAR - 0.1,
                voice_top=6, rigid_top=tops[-1] == G.PULSE_LOW)
        for beat in (1, 2):
            m = mel[i * 3 + beat]
            chord_on(p, p.bar(b + i) + beat, [m, m + 12], 0.95, 92, top_vel=4)
    G.pedal_bars(p, b, 8, release=0.10)

    b = st(16)                              # S16 — it collapses
    p.cue('it is not a message', p.bar(b))
    for i in range(8):
        bass(p, b + i, i, 40)
        if i >= 4:
            pulse(p, b + i, 42, double=(i == 4))
    p.add(PNO, p.bar(b), T.HALF_MIN, vel=52, vel_end=44, gate=0.98)
    # bars 5-8: nothing but the bass and the tick. The quietest place in the
    # second half of the piece, and the one the whole turn depends on.
    G.pedal_bars(p, b, 8)


# ====================================================================== #
#  VI. one note different  (S17) — the hinge                             #
# ====================================================================== #
def the_hinge(p):
    b = st(17)
    p.mark('one note different', p.bar(b))
    for i in range(8):
        waltz_lh(p, b + i, i, MINOR if i < 6 else MAJOR, 46)
    # the first F sharp in the piece: one note, on the third beat, alone
    p.cue('the first F sharp', p.bar(b) + 2)
    p.add(PNO, p.bar(b) + 2, T.HINGE_1, vel=54, gate=1.0)
    p.add(PNO, p.bar(b + 1), 'E4:h. D4:h. C#4:h. D4:h.', vel=48, gate=0.99)
    # and the second, ten seconds later, with the chord under it
    p.add(PNO, p.bar(b + 6), T.HINGE_2, vel=64, gate=1.0)
    chord_on(p, p.bar(b + 6), [midi('A4')], BAR, 58)
    chord_on(p, p.bar(b + 7), [midi('C#4'), midi('E4'), midi('A4')], BAR, 66)
    G.pedal_bars(p, b, 8)


# ====================================================================== #
#  VII. a star  (S18-S23) — the same bass, in the major                  #
# ====================================================================== #
def a_star(p):
    mel = T.per_beat(T.THEME_MAJ)

    b = st(18)                              # S18 — D major arrives
    p.mark('a star', p.bar(b))
    for i in range(8):
        waltz_lh(p, b + i, i, MAJOR, 58)
    p.add(PNO, p.bar(b), T.THEME_MAJ, vel=76, gate=0.97)
    p.add(PNO, p.bar(b), T.SIXTH_MAJ, vel=64, gate=0.97)
    G.pedal_bars(p, b, 8)

    b = st(19)                              # S19 — eighths, three octaves
    for i in range(8):
        lh_run(p, b + i, i, MAJOR, 0.5, 62, top=31)
    p.add(PNO, p.bar(b), T.THEME_MAJ, vel=86, gate=0.97)
    p.add(PNO, p.bar(b), T.THEME_MAJ, vel=80, gate=0.97, transpose=12)
    G.pedal_bars(p, b, 8)

    b = st(20)                              # S20 — sixteenths
    for i in range(8):
        lh_run(p, b + i, i, MAJOR, 0.25, 70, top=28, gate=0.85,
               beats=3 if i < 7 else 2)                    # a breath first
    p.add(PNO, p.bar(b), T.THEME_MAJ, vel=94, gate=0.97)
    p.add(PNO, p.bar(b), T.THEME_MAJ, vel=88, gate=0.97, transpose=12)
    G.pedal_halves(p, b, 8)

    b = st(21)                              # S21 — the anthem
    p.mark('the anthem', p.bar(b))
    for i in range(8):
        g = G.GROUND[i]
        roll_to(p, [g - 12, g, g + 7, g + 12], p.bar(b + i), 98, spread=0.04,
                dur=1.4)
        for k in range(6):
            seq = arc(pool(i, MAJOR, g + 12, g + 28)[:5], 6)
            p.add(PNO, p.bar(b + i) + 1.0 + k * 0.25, [(seq[k], 0.25)],
                  vel=88 - (k % 2) * 4, gate=0.88, swing=False)
        for beat in range(3):
            m = mel[i * 3 + beat]
            tops = filled_octave(i, MAJOR, m) + ([G.PULSE_LOW] if beat == 0
                                                 else [])
            if beat == 0:
                roll_to(p, tops, p.bar(b + i), 104, spread=0.03, dur=1.0,
                        voice_top=8, rigid_top=True)
            else:
                chord_on(p, p.bar(b + i) + beat, tops, 0.95, 100, top_vel=4)
    G.pedal_bars(p, b, 8, release=0.10)

    b = st(22)                              # S22 — the summit
    p.cue('the summit', p.bar(b))
    for i in range(8):
        g = G.GROUND[i]
        roll_to(p, [g - 12, g, g + 7, g + 12], p.bar(b + i), 102,
                spread=0.035, dur=1.6)
        for k in range(6):
            seq = arc(pool(i, MAJOR, g + 12, g + 31)[:5], 6)
            p.add(PNO, p.bar(b + i) + 1.0 + k * 0.25, [(seq[k], 0.25)],
                  vel=92 - (k % 2) * 4, gate=0.88, swing=False)
        for beat in range(3):
            m = mel[i * 3 + beat]
            if beat == 0:
                roll_to(p, filled_octave(i, MAJOR, m) + [G.PULSE_LOW],
                        p.bar(b + i), 113, spread=0.03, dur=1.0, voice_top=10,
                        rigid_top=True)
            else:
                chord_on(p, p.bar(b + i) + beat, filled_octave(i, MAJOR, m),
                         0.95, 109, top_vel=6)
    G.pedal_bars(p, b, 8, release=0.10)


def the_ground_was_the_tune(p):
    """S23 — the theme stops. What is left is the eight notes underneath."""
    b = st(23)
    p.mark('the ground was the tune', p.bar(b))
    for i in range(4):                      # the descent, hammered in octaves
        g = G.GROUND[i]
        for beat in range(3):
            v = 106 if beat == 0 else 100
            chord_on(p, p.bar(b + i) + beat, [g - 12, g], 0.9, v)
            chord_on(p, p.bar(b + i) + beat, [g + 24, g + 36], 0.9, v + 4)
    for i in range(4, 8):                   # the rise, held open
        g = G.GROUND[i]
        roll_to(p, [g - 12, g, g + 7, g + 12], p.bar(b + i), 104, spread=0.06,
                dur=BAR - 0.1)
        if i < 6:
            roll_to(p, [g + 24, g + 31, g + 36], p.bar(b + i), 106,
                    spread=0.05, dur=BAR - 0.1, voice_top=6)
    # the theme's last phrase, once, on top of the rise
    p.add(PNO, p.bar(b + 6), 'F#5:q E5:q D5:q  E5:q C#5:q A4:q', vel=110,
          gate=0.98)
    p.add(PNO, p.bar(b + 6), 'F#6:q E6:q D6:q  E6:q C#6:q A5:q', vel=106,
          gate=0.98)
    G.pedal_bars(p, b, 8, release=0.10)


# ====================================================================== #
#  VIII. still turning  (S24-S27, coda)                                  #
# ====================================================================== #
def still_turning(p):
    b = st(24)
    p.mark('still turning', p.bar(b))
    for i in range(8):                      # S24 — opening out, ringing
        g = G.GROUND[i]
        vel = 88 - i * 5
        roll_to(p, [g, g + 7, g + 12] + above(i, MAJOR, g + 19, 2),
                p.bar(b + i), vel, spread=0.045, dur=BAR - 0.1)
        pulse(p, b + i, 76 - i * 3, double=True)
    G.pedal_bars(p, b, 8)

    b = st(25)                              # S25 — the theme, once, alone
    for i in range(8):
        waltz_lh(p, b + i, i, MAJOR, 48)
    p.add(PNO, p.bar(b), T.THEME_MAJ, vel=70, vel_end=60, gate=0.98)
    G.pedal_bars(p, b, 8)

    b = st(26)                              # S26 — the bass and the tick
    for i in range(8):
        g = G.GROUND[i]
        p.add(PNO, p.bar(b + i), [([g, g + 7], BAR)], vel=52 - i * 2,
              gate=0.98, swing=False)
        pulse(p, b + i, 52 - i * 2)
    G.pedal_bars(p, b, 8)

    b = st(27)                              # S27 — the last turn, under one chord
    p.mark('the last chord', p.bar(b))
    # Two waves rather than one eight-bar pedal: a piano cannot hold a chord
    # for eleven seconds *and* keep the bass clear, and a pianist would
    # re-take both. The ground keeps going underneath either way — it does
    # not stop for the nice chord.
    for wave, vel, hold in ((0, 62, 4), (4, 56, G.LAST_BAR + 1 - (st(27) + 4))):
        roll_to(p, [midi(n) for n in ('D1', 'D2', 'A2', 'D3', 'F#3')],
                p.bar(b + wave) - 0.42, vel - 4, spread=0.07, dur=hold * BAR,
                gate=1.0)
        # the right hand sweeps three octaves of D major and arrives on the
        # pulse: the last chord's top note *is* the tick
        roll_to(p, [midi(n) for n in ('A3', 'D4', 'F#4', 'A4', 'D5', 'F#5',
                                      'A5', 'D6', 'F#6', 'A6')],
                p.bar(b + wave), vel, spread=0.07, dur=hold * BAR, gate=1.0,
                voice_top=8, rigid_top=True)
        p.pedal(PNO, p.bar(b + wave) - 0.6,
                p.bar(b + wave + hold) - (0.1 if wave == 0 else 0.0))
    for i in range(8):
        bass(p, b + i, i, 44 - i * 2, dur=1.5, gate=0.9)
        if i not in (0, 4):                 # 0 and 4 arrive on the sweep's top
            pulse(p, b + i, 48 - i * 2, double=(i == 1))

    for i in range(8):                      # coda — the recording stops
        # ...and the last one is the first one: A7 alone at velocity 50, the
        # same note struck the same way as the piece's opening tick. Nothing
        # about it changed while we listened.
        p.add(PNO, p.bar(G.CODA + i),
              [([G.PULSE_LOW, G.PULSE] if i < 7 else [G.PULSE], 1.0)],
              vel=62 - i * 2 if i < 7 else 50, gate=0.9, swing=False,
              rigid=True)


# ====================================================================== #
#  the build                                                             #
# ====================================================================== #
def build() -> Piece:
    p = Piece(solo_piano(), seed=1919,
              title='Still Turning - a passacaglia on a dead star')
    p.meter(0, 3, 4)
    p.tempo(0, G.BPM_SCRUFF, 'one pulse per beat')
    p.key(0, 'd')
    p.key(p.bar(st(18)), 'D')
    scruff(p)
    the_ground(p)
    first_reading(p)
    sidereal(p)
    the_ladder(p)
    the_storm(p)
    the_hinge(p)
    a_star(p)
    the_ground_was_the_tune(p)
    still_turning(p)
    return p


# ---------------------------------------------------------------- gates
def check_ground(p) -> list:
    """The ground is never altered. Twenty-seven statements, eight notes."""
    bad = []
    for n in range(1, G.N_STATEMENTS + 1):
        for i in range(8):
            bar = st(n) + i
            at = p.bar(bar)
            here = {x.pitch for x in p.notes
                    if abs(x.start - at) < 0.2 and x.pitch < 60}
            want = G.GROUND[i]
            if want not in here:
                bad.append(f'S{n} bar {bar}: no {pitch_name(want)} '
                           f'(found {sorted(here)})')
            elif any(x < want - 24 for x in here):
                bad.append(f'S{n} bar {bar}: something below {pitch_name(want)}-2oct')
    return bad


def check_pulse(p) -> list:
    """The pulse voice: machine-exact, always an A, never anywhere but a beat.

    The pulse is not struck in every bar — three hands would be needed under
    the theme statements, and burying it is half the story (docs/01). What is
    guaranteed is that every note of the pulse voice is an A in the top two
    octaves, marked rigid so the humaniser cannot touch it, and lands exactly
    on a pulse: a beat before the lock, a bar after it.
    """
    bad, bars = [], set()
    lock = p.bar(st(1))
    for n in (x for x in p.notes if x.rigid):
        if n.pitch % 12 != 9 or n.pitch < 93:
            bad.append(f'beat {n.start}: pulse voice has {pitch_name(n.pitch)}')
            continue
        off = n.start if n.start < lock else n.start - lock
        grid = 1.0 if n.start < lock else BAR
        if abs(off / grid - round(off / grid)) > 1e-6:
            bad.append(f'beat {n.start}: pulse off the grid')
        bars.add(round(n.start, 3))
    if len(bars) < 100:
        bad.append(f'only {len(bars)} pulses struck')
    return bad


def check_hinge(p) -> list:
    """No F sharp anywhere before the hinge, or it is not a hinge."""
    first = min((n for n in p.notes if n.pitch % 12 == 6),
                key=lambda n: n.start, default=None)
    if first is None:
        return ['no F sharp in the piece at all']
    want = p.bar(st(17)) + 2
    if abs(first.start - want) > 0.05:
        return [f'first F sharp at beat {first.start:.2f} '
                f'({pitch_name(first.pitch)}), wanted {want:.2f}']
    return []


def check_tempo(p) -> list:
    """One tempo change, at the lock, and no other. No ritardando. Ever."""
    tempi = p.timeline.tempi()
    if len(tempi) != 2:
        return [f'{len(tempi)} tempo marks, wanted 2: {tempi}']
    if abs(tempi[1][0] - p.bar(st(1))) > 1e-6:
        return [f'the lock is at beat {tempi[1][0]}, not {p.bar(st(1))}']
    return []


def main():
    p = build()
    OUT.mkdir(exist_ok=True)
    ok = assess.report(p)
    print()
    problems = (check_tempo(p) + check_ground(p) + check_pulse(p)
                + check_hinge(p))
    for line in problems:
        print(f'  GATE  {line}')
    struck = len({round(n.start, 3) for n in p.notes if n.rigid})
    print(f'gates: {"clean" if not problems else str(len(problems)) + " failures"}'
          f'  (ground x{G.N_STATEMENTS}, {struck} pulses struck, hinge, one tempo)')
    print()
    playable = keyboard.report(p)

    mid = OUT / 'still_turning.mid'
    p.write(str(mid))
    p.write_marks(str(OUT / 'marks.json'))
    wav = OUT / 'still_turning.wav'
    assess.pianoroll(p, str(OUT / 'roll.png'), wav=str(wav) if wav.exists() else None)
    print()
    print(midi_report(str(mid)))
    if not (ok and playable and not problems):
        sys.exit(1)


if __name__ == '__main__':
    main()
