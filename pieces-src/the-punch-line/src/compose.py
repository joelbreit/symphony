"""The Punch Line — a rag for the player piano.

Solo piano, 2/4, A-flat major, ~3:20. The form is a joke's anatomy
(docs/03): setup, topper, callback, aside, the pause, punch line, and the
doctored-roll finale where the ghost stops pretending.

    ../../../.venv/bin/python src/compose.py     (from pieces-src/the-punch-line/)
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib import Piece, assess, figures, midi_report
from lib.chords import voicing
from lib.ensemble import solo_piano
from lib.pitch import midi

import rag
from rag import PNO, crush, octify, roll_chord, scale_run, stoptime, stride, walk_oct
from themes import (A_BARS, D_BARS, INTERLUDE, INTRO_LINE, PAUSE_BAR,
                    STRAIN_A, STRAIN_B, STRAIN_C, STRAIN_D, TAG_1, TAG_3)

OUT = pathlib.Path(__file__).resolve().parents[1] / 'output'

# Section starts in absolute beats (2/4: one bar = 2 beats; docs/03 map).
INTRO, A1, A2, B1, B2, A3 = 0, 8, 40, 72, 104, 136
INT, C1, C2, PAUSE, D1, D2, TAG = 168, 176, 208, 240, 244, 276, 308

# Charts (docs/03): one symbol per bar, tuples split the bar.
CH_A = ['Ab', 'Ab', 'Eb7', 'Eb7', 'Eb7', 'Eb7', 'Ab', 'Ab',
        'Ab', 'Ab7', 'Db', 'Ddim7', 'Ab/Eb', 'F7', ('Bb7', 'Eb7'), 'Ab']
CH_B = ['C7', 'C7', 'F7', 'F7', 'Bb7', 'Eb7', 'Ab', 'Eb7',
        'C7', 'C7', 'F7', 'F7', 'Bb7', 'Eb7', ('Ab', 'Eb7'), 'Ab']
CH_C = ['Db', 'Db', 'Ab7', 'Ab7', 'Ab7', 'Ab7', 'Db', 'Db7',
        'Gb', 'Gb', 'Gdim7', 'Gdim7', 'Db/Ab', 'Bb7', ('Eb7', 'Ab7'), 'Db']
CH_D = ['Ab', 'Ab', 'C7', 'C7', 'F7', 'F7', 'Bb7', 'Eb7'] + CH_A[8:]

# The doctored-roll finale rides an Ab pedal under the run, then hangs on V7.
CH_D2 = CH_D[:12] + ['Ab', 'Ab', 'Bb7', 'Eb7']

# QRS filler thirds for the "improbable" rung, keyed by the bar's harmony.
FILLER = {'F7': ['A4', 'C5'], 'Bb7': ['Ab4', 'D5'], 'Eb7': ['G4', 'Db5']}

STACK_BB7 = ['Bb1', 'Bb2', 'Ab3', 'D4', 'F4', 'Ab4', 'D5', 'F5', 'Bb5', 'D6']
STACK_EB7 = ['Eb2', 'Eb3', 'Db4', 'G4', 'Bb4', 'Db5', 'G5', 'Bb5', 'Eb6', 'G6']


# ------------------------------------------------------------ the walk-on
def walk_on(p):
    p.mark('the walk-on', INTRO)
    p.add(PNO, INTRO, octify(INTRO_LINE, -12), vel=90, gate=0.9)
    p.add(PNO, INTRO, octify(INTRO_LINE, -12), vel=84, gate=0.9,
          transpose=-24)


# ------------------------------------------------------- A: the setup (x3)
def the_setup(p):
    p.mark('A - the setup', A1)
    stride(p, A1, CH_A, 16, vel=68, near='Ab2')
    p.add(PNO, A1, STRAIN_A, vel=76, gate=0.85)

    # the roll arranger's varied repeat: an octave up, octave basses
    p.mark('A - re-punched', A2)
    stride(p, A2, CH_A, 16, vel=72, near='Ab2', oct_bass=True)
    p.add(PNO, A2, STRAIN_A, vel=80, gate=0.85, transpose=12)


def the_callback(p):
    p.mark('A - the callback', A3)
    stride(p, A3, CH_A, 16, vel=64, near='Ab2')
    p.add(PNO, A3, ' '.join(A_BARS[:8]), vel=74, gate=0.85)
    p.add(PNO, A3 + 16, ' '.join(A_BARS[8:]), vel=68, vel_end=58, gate=0.85)


# ------------------------------------------------------- B: the topper (x2)
def the_topper(p):
    p.mark('B - the topper', B1)
    stride(p, B1, CH_B, 16, vel=76, near='Ab2')
    p.add(PNO, B1, STRAIN_B, vel=86, gate=0.82)

    p.mark('B - with teeth', B2)
    stride(p, B2, CH_B, 16, vel=80, near='Ab2', oct_bass=True)
    p.add(PNO, B2, STRAIN_B, vel=90, vel_end=94, gate=0.82)
    # crushes on the secondary-rag cell heads
    for bar, top in ((0, 'Bb5'), (2, 'A5'), (8, 'Bb5'), (10, 'A5')):
        for off in (0.0, 0.75, 1.5):
            crush(p, B2 + 2 * bar + off, top, 92)


# ---------------------------------------------------- interlude: leaning in
def leaning_in(p):
    p.mark('leaning in', INT)
    stride(p, INT, ['Ab', ('Ab', 'Abaug')], 2, vel=56, near='Ab2',
           oct_bass=False)
    walk_oct(p, INT + 4, ['Ab2', 'Gb2', 'F2', 'Eb2'], vel=56, vel_step=0)
    walk_oct(p, INT + 6, ['Db2', 'Eb2', 'F2', 'Gb2'], vel=56, vel_step=2)
    p.add(PNO, INT, INTERLUDE, vel=62, vel_end=54, gate=0.9)


# --------------------------------------------------------- C: the trio (x2)
def the_aside(p):
    p.mark('trio - the aside', C1)
    stride(p, C1, CH_C, 16, vel=48, near='Db2', oct_bass=False,
           chord_lo='Eb3', chord_hi='Db4')
    p.add(PNO, C1, STRAIN_C, vel=52, vel_end=62, gate=0.98)
    for i in range(0, 16, 2):
        p.pedal(PNO, C1 + 2 * i, C1 + 2 * i + 1.85)

    p.mark('trio - up an octave', C2)
    stride(p, C2, CH_C, 16, vel=54, near='Db2', oct_bass='arrivals',
           chord_lo='Eb3', chord_hi='Db4')
    p.add(PNO, C2, STRAIN_C, vel=60, vel_end=68, gate=0.98, transpose=12)
    for i in range(0, 16, 2):
        p.pedal(PNO, C2 + 2 * i, C2 + 2 * i + 1.85)


# ------------------------------------------------------------- the pause
def the_pause(p):
    p.mark('the pause', PAUSE)
    p.cue('wait for it', PAUSE)
    p.add(PNO, PAUSE, PAUSE_BAR, vel=78, gate=0.7)
    # bar 122: a full bar of nothing — the longest silence in the piece.


# ------------------------------------------------------ D: the punch line
def punch_line(p):
    p.mark('D - the punch line', D1)
    stoptime(p, D1, CH_D[:1], 1, vel=94)
    # bar 124's stab is bass-only: the right hand is already talking
    p.add(PNO, D1 + 2, [([midi('Ab2'), midi('Ab3')], 0.5)], vel=94,
          gate=0.5, swing=False)
    stride(p, D1 + 4, CH_D[2:], 14, vel=78, near='Ab2', oct_bass=True)
    p.add(PNO, D1, STRAIN_D, vel=88, vel_end=94, gate=0.85)


# -------------------------------------------------- D': the doctored roll
def doctored_roll(p):
    t = D2
    p.mark('D - the doctored roll', t)
    p.cue('the ghost stops pretending', t)
    p.tempo(t, 100, 'the crank slips')
    stoptime(p, t, CH_D2[:2], 2, vel=102)
    stride(p, t + 4, CH_D2[2:8], 6, vel=88, near='Ab2', oct_bass=True)
    stride(p, t + 16, CH_D2[8:12], 4, vel=94, near='Ab2', oct_bass=True,
           double=True)
    stride(p, t + 24, CH_D2[12:14], 2, vel=98, near='Ab2', oct_bass=True,
           double=True)

    twelve = ' '.join(D_BARS[:12])
    p.add(PNO, t, twelve, vel=98, vel_end=104, gate=0.85)          # the hands
    p.add(PNO, t, twelve, vel=94, vel_end=102, gate=0.85,          # rung 1:
          transpose=12)                                            # +8va ghost
    for i, bar in enumerate(range(4, 8)):                          # rung 2:
        sym = CH_D2[bar]                                           # filler
        p.add(PNO, t + 2 * bar, figures.trem(FILLER[sym], 2.0, 0.25),
              vel=82 + 2 * i, gate=0.9, swing=False)
    p.add(PNO, t + 16, ' '.join(D_BARS[8:12]), vel=92, vel_end=98, # rung 3:
          gate=0.85, transpose=-12)                                # third reg.

    # rung 4: the five-octave run (32nds — no hand alive) into the stacks
    scale_run(p, t + 24, 'Ab1', 'Db6', vel=100, vel_end=114, unit=0.125)
    for at, stack, dur, v in ((t + 28, STACK_BB7, 0.5, 106),
                              (t + 28.75, STACK_BB7, 0.5, 108),
                              (t + 29.5, STACK_EB7, 0.5, 110),
                              (t + 30, STACK_EB7, 1.5, 112)):
        p.add(PNO, at, [(stack, dur)], vel=v, gate=0.9, swing=False)


# ------------------------------------------------- tag: shave and a haircut
def two_bits(p):
    t = TAG
    p.mark('shave and a haircut', t)
    stoptime(p, t, ['Ab'], 1, vel=102)
    p.add(PNO, t, octify(TAG_1, -12), vel=106, gate=0.8)
    # bar 156: the wait.
    p.cue('two bits', t + 4.5)
    stab = sorted({midi('Eb2'), midi('Eb3'), *voicing('Eb7', 'G3', 'G4')})
    p.add(PNO, t + 4.5, [(stab, 0.5)], vel=100, gate=0.6, swing=False)
    crush(p, t + 5, 'Ab4', 104)
    p.add(PNO, t + 4, octify(TAG_3, -12), vel=104, gate=0.85)
    # bar 158: the ghost repeats the landing, five octaves wide
    roll_chord(p, t + 6, ['Ab1', 'Eb2', 'Ab2', 'Eb3', 'Ab3', 'C4', 'Eb4',
                          'Ab4', 'C5', 'Eb5', 'Ab5', 'C6', 'Eb6', 'Ab6'],
               3.4, 102)
    p.pedal(PNO, t + 6, t + 9.8)
    # the last hole punched in the roll
    p.cue('the last hole', t + 9.4)
    p.note(PNO, t + 9.4, 'Ab7', 0.35, vel=32, swing=False)


def build() -> Piece:
    p = Piece(solo_piano(), seed=1902,
              title='The Punch Line — a rag for the player piano')
    p.meter(0, 2, 4)
    p.tempo(0, 96, "not fast (Joplin's law)")
    walk_on(p)
    the_setup(p)
    the_topper(p)
    the_callback(p)
    leaning_in(p)
    the_aside(p)
    the_pause(p)
    punch_line(p)
    doctored_roll(p)
    two_bits(p)
    return p


def main():
    p = build()
    OUT.mkdir(exist_ok=True)
    ok = assess.report(p)
    p.write(str(OUT / 'the_punch_line.mid'))
    p.write_marks(str(OUT / 'marks.json'))
    wav = OUT / 'the_punch_line.wav'
    assess.pianoroll(p, str(OUT / 'roll.png'),
                     wav=str(wav) if wav.exists() else None)
    print()
    print(midi_report(str(OUT / 'the_punch_line.mid')))
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
