"""Cut Loose — a second line for a cornet player.

One continuous piece, ~5 minutes: the procession (dirge, E-flat), the
whistle, the second line home. The cornet is silent until bar 45.

    ../../../.venv/bin/python src/compose.py     (from pieces-src/cut-loose/)
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib import B, Piece, assess, figures, midi_report
from lib.chords import voicing
from lib.pitch import midi

import street
from band import brass_band
from street import BD, SN
from themes import (BENEDICTION, CH_HYMN, CH_RAMBLE, CH_RAMBLE_TURN, CH_SHOUT,
                    CH_STRUT, CH_STRUT_TURN, CLAR_RAMBLE, CORNET_BREAK,
                    CORNET_TURN, CRY_HARMONY, DESCANT, HYMN, HYMN_BARS,
                    HYMN_HALF2, RAMBLE, SHOUT, SHOUT_ANSWERS, SOUSA_RIFF, STRUT,
                    STRUT_FILLS, STRUT_OUT, TBN_CRY, TBN_HYMN, TBN_RAMBLE,
                    UNISON_TAG)

OUT = pathlib.Path(__file__).resolve().parents[1] / 'output'

SWING = 0.58


def bar(n):
    """Absolute beat of 1-indexed bar n (4/4 throughout)."""
    return 4 * (n - 1)


# Section starts (docs/03 map), in bars.
CADENCE, HYMN1, CRY, AMEN, WHISTLE = 1, 5, 21, 29, 33
STREET, SOUSA_IN, RIFF_IN = 34, 38, 42
STRUT1, STRUT2, TO_AB = 46, 62, 78
RAMBLE1, TBN_CH, CLAR_CH, SHOUT_CH, TO_EB = 82, 98, 114, 130, 146
HOME, TAG, BENEDICT = 150, 166, 173
END = 177


# ================================================================ I. the procession
def cadence(p):
    t = bar(CADENCE)
    p.tempo(t, 66, 'dirge - the walk begins')
    p.mark('the cadence', t)
    street.dirge_cadence(p, t, 4, vel=46)
    # the sousaphone joins on bar 3: the E-flat pedal under the walk
    p.note('sousa', bar(3), 'Eb2', 2, vel=56, gate=0.94)
    p.note('sousa', bar(3) + 2, 'Bb1', 2, vel=48, gate=0.94)
    p.note('sousa', bar(4), 'Eb2', 2, vel=58, gate=0.94)
    p.note('sousa', bar(4) + 2, 'Bb1', 2, vel=50, gate=0.94)


def the_hymn(p):
    t = bar(HYMN1)
    p.mark('the hymn', t)
    # alto sax states the tune plainly, with a little breath in its tone
    street.cry(p, 'alto', t, bar(CRY), depth=48, rise=8)
    p.add('alto', t, HYMN, vel=58, vel_end=68, gate=0.96)
    # trombone tenor line, smearing into each phrase downbeat
    p.add('tbn', t, TBN_HYMN, vel=52, vel_end=60, gate=0.95)
    for b, target in ((0, 'Bb3'), (4, 'G3'), (8, 'G3'), (12, 'G3')):
        figures.smear_into(p, 'tbn', target, t + 4 * b, 54, n=3)
        figures.scoop(p, 'tbn', t + 4 * b, semitones=1.2)
    street.cry(p, 'tbn', t, bar(CRY), depth=40, rise=8)
    street.dirge_bass(p, t, CH_HYMN, 16, vel=56, near='Eb2', next_sym='Eb7')
    street.dirge_cadence(p, t, 16, vel=48)
    # the clarinet enters on the hymn's second half: a descant, high and still
    tc = t + 32
    p.cue('the tear', t + 40)
    street.cry(p, 'clarinet', tc, bar(CRY), depth=80, rise=2)
    p.add('clarinet', tc, DESCANT, vel=50, vel_end=62, gate=0.98)


def the_cry(p):
    t = bar(CRY)
    p.mark('the cry', t)
    # clarinet takes the tune an octave up, the widest vibrato in the piece
    street.cry(p, 'clarinet', t, bar(AMEN), depth=110, rise=1.0)
    p.add('clarinet', t, HYMN_HALF2, vel=86, vel_end=92, transpose=12, gate=0.98)
    figures.scoop(p, 'clarinet', t + 8, semitones=1.0)     # into the tear
    street.cry(p, 'alto', t, bar(AMEN), depth=70, rise=1.0)
    p.add('alto', t, CRY_HARMONY, vel=74, vel_end=80, gate=0.96)
    street.cry(p, 'tbn', t, bar(AMEN), depth=60, rise=1.0)
    p.add('tbn', t, TBN_CRY, vel=76, vel_end=82, gate=0.95)
    figures.smear_into(p, 'tbn', 'Bb3', t, 70, n=3)
    figures.smear_into(p, 'tbn', 'Cb4', t + 8, 72, n=4)
    figures.scoop(p, 'tbn', t + 8, semitones=1.5)
    figures.smear_into(p, 'tbn', 'G3', t + 16, 72, n=3)
    street.dirge_bass(p, t, CH_HYMN[8:], 8, vel=72, near='Eb2', next_sym='Ab')
    street.dirge_cadence(p, t, 8, vel=62, cymbal_every=4)


def amen(p):
    t = bar(AMEN)
    p.mark('amen', t)
    p.tempo(t + 4, 60)
    p.tempo(t + 8, 54, 'the body is cut loose')
    # IV held two bars, I held two bars; the top voice falls A-flat to G
    for inst, a, b, v in (('clarinet', 'Ab5', 'G5', 86), ('alto', 'C5', 'Bb4', 78),
                          ('tbn', 'Eb4', 'Eb4', 78)):
        p.note(inst, t, a, 8, vel=v, gate=0.99)
        p.note(inst, t + 8, b, 8, vel=v - 6, gate=0.99)
        p.cc(inst, t, 11, 100)
        p.hairpin(inst, t, t + 7, 100, 118)
        p.hairpin(inst, t + 8, t + 15.5, 112, 30)
    street.cry(p, 'clarinet', t, t + 16, depth=110, rise=0.5)
    street.cry(p, 'alto', t, t + 16, depth=80, rise=0.5)
    street.cry(p, 'tbn', t, t + 16, depth=60, rise=0.5)
    p.note('sousa', t, 'Ab1', 8, vel=72, gate=0.99)
    p.note('sousa', t + 8, 'Eb1', 8, vel=66, gate=0.99, check_range=True)
    p.cc('sousa', t, 11, 110)
    p.hairpin('sousa', t + 8, t + 15.5, 110, 40)
    p.perc(t, [('kick', 2)], vel=76, inst=BD)
    p.perc(t, [('crash', 4)], vel=62, inst=BD)
    p.perc(t + 8, [('kick', 2)], vel=64, inst=BD)
    figures.perc_roll(p, 'sn', t, 8, 30, 58, unit=1 / 16, inst=SN)
    figures.perc_roll(p, 'sn', t + 8, 7.5, 54, 8, unit=1 / 16, inst=SN)


def the_whistle(p):
    t = bar(WHISTLE)
    p.mark('the whistle', t)
    p.cue('the whistle', t + 2)
    # two beats of nothing, then the grand marshal
    street.whistle(p, t + 2)


# ================================================================ II. the second line
def snares_on(p):
    t = bar(STREET)
    p.tempo(t, 190, 'second line')
    p.mark('snares on', t)
    street.dry(p, t - 1)
    p.cc('sousa', t - 1, 11, 112)
    street.snare_solo(p, t, 4, vel=86)
    # the bass drummer joins on bar 36
    for i in range(2):
        bt = t + 8 + 4 * i
        for off, dv in ((0.0, 8), (1.5, -8), (3.0, 0)):
            p.perc(bt + off, [('kick', 0.25)], vel=92 + dv, inst=BD)
        for b in (1.0, 3.0):
            p.perc(bt + b, [('hhc', 0.3)], vel=60, inst=BD)
    p.perc(t + 8, [('crash', 1.5)], vel=88, inst=BD)


def sousa_riff(p):
    t = bar(SOUSA_IN)
    p.mark('the sousaphone riff', t)
    p.add('sousa', t, SOUSA_RIFF, vel=100, gate=0.8)
    p.add('sousa', t + 8, SOUSA_RIFF, vel=104, gate=0.8)
    street.street_beat(p, t, 4, vel=86, crash_first=True, fill_every=4)


def riffing_in(p):
    t = bar(RIFF_IN)
    p.mark('riffing in', t)
    p.add('sousa', t, SOUSA_RIFF, vel=106, gate=0.8)
    p.note('sousa', t + 8, 'G1', 0.5, vel=106, gate=0.8)
    p.note('sousa', t + 8.5, 'Bb1', 0.5, vel=104, gate=0.8)
    p.note('sousa', t + 9.5, 'Eb2', 1.5, vel=108, gate=0.8)
    street.street_beat(p, t, 3, vel=90, crash_first=False, fill_every=3,
                       cell0=1)
    eb = ['Eb'] * 4
    street.riff(p, 'alto', t, eb, 3, 'G4', 'Eb5', rhythm='offbeats', vel=82,
                tones=(1, 2))
    street.riff(p, 'tbn', t, eb, 3, 'Bb2', 'Bb3', rhythm='offbeats', vel=84,
                tones=(0, 2))
    street.riff(p, 'clarinet', t + 4, eb, 2, 'Bb5', 'G6', rhythm='charleston',
                vel=78, tones=(2, 1))
    # bar 45: one hit — then the cornet alone. His first notes.
    tb = t + 12
    street.stab(p, tb, 'Eb', vel=104, dur=0.4, who=('clarinet', 'alto', 'tbn'))
    p.perc(tb, [('crash', 1)], vel=100, inst=BD)
    p.cue('his first note', tb + 0.5)
    figures.smear_into(p, 'cornet', 'Eb5', tb + 0.5, 100, n=4)
    p.add('cornet', tb, CORNET_BREAK, vel=104, vel_end=98, gate=0.85)


def strut_one(p):
    t = bar(STRUT1)
    p.mark('the strut - the hymn cut loose', t)
    p.add('cornet', t, STRUT, vel=98, gate=0.85)
    figures.scoop(p, 'cornet', t + 1.5, semitones=1.0)
    figures.scoop(p, 'cornet', t + 33.5, semitones=1.0)
    figures.falloff(p, 'cornet', 'G5', t + 35.0, 96, n=3)
    street.obbligato(p, t, CH_STRUT_TURN, 16, STRUT, energy=0.45, vel=74,
                     anchor='Bb5', hi='F6')
    for b, beat, dsl in STRUT_FILLS:
        p.add('clarinet', t + 4 * b + beat, dsl, vel=84, gate=0.85)
    street.tailgate(p, t, CH_STRUT_TURN, 16, vel=78, density=0.8, near='Eb3')
    street.riff(p, 'alto', t, CH_STRUT_TURN, 16, 'G4', 'Eb5', rhythm='offbeats',
                vel=70, tones=(1, 2))
    street.two_beat(p, t, CH_STRUT_TURN, 16, vel=98, near='Eb2', next_sym='Eb')
    street.street_beat(p, t, 16, vel=86, fill_every=8, cell0=0)


def strut_two(p):
    t = bar(STRUT2)
    p.mark('the strut - clarinet up top, the hymn underneath', t)
    # clarinet takes the strut an octave up
    p.add('clarinet', t, STRUT, vel=90, transpose=12, gate=0.85)
    figures.scoop(p, 'clarinet', t + 33.5, semitones=1.0)
    # ...while the cornet plays the hymn itself, in its slow rhythm, at 190
    p.add('cornet', t, HYMN, vel=78, vel_end=84, gate=0.92)
    street.tailgate(p, t, CH_STRUT_TURN, 16, vel=80, density=0.85, near='Eb3')
    street.riff(p, 'alto', t, CH_STRUT_TURN, 16, 'G4', 'Eb5', rhythm='charleston',
                vel=72, tones=(1, 2))
    street.two_beat(p, t, CH_STRUT_TURN, 16, vel=100, near='Eb2', next_sym='Eb7')
    street.street_beat(p, t, 16, vel=88, fill_every=8, cell0=2)


def around_the_corner(p):
    t = bar(TO_AB)
    p.mark('around the corner to A-flat', t)
    # E-flat 7 Charleston hits, sousaphone walking, then two bars of snare drum
    for i in range(2):
        for off, d in ((0.0, 0.75), (1.5, 0.5)):
            street.stab(p, t + 4 * i + off, 'Eb7', vel=102, dur=d,
                        who=('cornet', 'clarinet', 'alto', 'tbn'), sousa=False,
                        drums=False)
    for k, q in enumerate(['Eb2', 'G2', 'Bb2', 'Db3', 'Eb2', 'Db2', 'C2', 'B1']):
        p.note('sousa', t + k, q, 0.8, vel=98 + 2 * (k % 4), gate=0.85)
    street.street_beat(p, t, 2, vel=90, crash_first=True, fill_every=2, cell0=3)
    street.drum_break(p, t + 8, 2, vel=98)
    p.note('sousa', t + 8, 'Bb1', 0.8, vel=100, gate=0.85)
    p.note('sousa', t + 8 + 2, 'Bb1', 0.8, vel=96, gate=0.85)
    figures.smear_into(p, 'tbn', 'C4', t + 16, 84, n=4)


def the_ramble(p):
    t = bar(RAMBLE1)
    p.mark('the ramble', t)
    p.add('cornet', t, RAMBLE, vel=100, gate=0.85)
    figures.scoop(p, 'cornet', t + 40, semitones=1.0)        # the tear
    figures.falloff(p, 'cornet', 'Gb5', t + 31.0, 98, n=3)
    street.obbligato(p, t, CH_RAMBLE_TURN, 16, RAMBLE, energy=0.55, vel=76,
                     anchor='C6', hi='F6')
    street.tailgate(p, t, CH_RAMBLE_TURN, 16, vel=80, density=0.8, near='Ab3')
    street.riff(p, 'alto', t, CH_RAMBLE_TURN, 16, 'Ab4', 'F5', rhythm='offbeats',
                vel=72, tones=(1, 2))
    # bars 7-8: stop-time — the band hits beat 1 only
    for b in (6, 7):
        street.stab(p, t + 4 * b, CH_RAMBLE[b] if b == 6 else 'Ab', vel=100,
                    dur=0.5, who=('clarinet', 'alto', 'tbn'))
    street.two_beat(p, t, CH_RAMBLE_TURN[:6], 6, vel=100, near='Ab1',
                    next_sym='Ab')
    street.two_beat(p, t + 32, CH_RAMBLE_TURN[8:], 8, vel=100, near='Db2',
                    next_sym='Ab')
    street.street_beat(p, t, 6, vel=88, fill_every=6, cell0=1)
    street.street_beat(p, t + 32, 8, vel=88, crash_first=False, fill_every=4,
                       cell0=3)


def trombone_takes_it(p):
    t = bar(TBN_CH)
    p.mark('trombone takes it', t)
    p.add('tbn', t, TBN_RAMBLE, vel=94, gate=0.85)
    for off, target in ((1.5, 'C4'), (8, 'Db4'), (32, 'F3'), (36, 'F4'),
                        (40, 'Fb4'), (48, 'A3')):
        figures.scoop(p, 'tbn', t + off, semitones=1.5)
    figures.smear_into(p, 'tbn', 'F4', t + 36, 90, n=4)
    figures.falloff(p, 'tbn', 'F4', t + 37.5, 94, n=4)
    street.riff(p, 'clarinet', t, CH_RAMBLE_TURN, 16, 'Ab5', 'F6',
                rhythm='offbeats', vel=66, tones=(2, 1))
    street.riff(p, 'alto', t, CH_RAMBLE_TURN, 16, 'Ab4', 'F5', rhythm='push',
                vel=68, tones=(1, 0), every=2)
    # the cornet lays out, then pads the second half
    street.pads(p, 'cornet', t + 32, CH_RAMBLE_TURN[8:], 8, 'Ab4', 'F5', vel=52)
    street.two_beat(p, t, CH_RAMBLE_TURN, 16, vel=96, near='Ab1', next_sym='Ab')
    street.street_beat(p, t, 16, vel=84, fill_every=4, cell0=0)


def clarinet_takes_it(p):
    t = bar(CLAR_CH)
    p.mark('clarinet takes it', t)
    p.add('clarinet', t, CLAR_RAMBLE, vel=92, gate=0.85)
    figures.trill(p, 'clarinet', 'F6', t + 18.0, 1.5, 90, unit=0.125)
    figures.curl(p, 'clarinet', 'F6', t + 32.0, 92)
    figures.scoop(p, 'clarinet', t + 40, semitones=1.0)
    street.riff(p, 'cornet', t, CH_RAMBLE_TURN, 16, 'Bb4', 'G5',
                rhythm='offbeats', vel=76, tones=(2, 1))
    street.riff(p, 'alto', t, CH_RAMBLE_TURN, 16, 'Ab4', 'F5', rhythm='offbeats',
                vel=70, tones=(1, 2))
    street.tailgate(p, t, CH_RAMBLE_TURN, 16, vel=78, density=0.75, near='Ab3')
    street.two_beat(p, t, CH_RAMBLE_TURN, 16, vel=98, near='Ab1', next_sym='Ab')
    street.street_beat(p, t, 16, vel=86, fill_every=4, cell0=2)


def the_umbrellas(p):
    t = bar(SHOUT_CH)
    p.tempo(t, 196, 'pushing')
    p.mark('the umbrellas go up', t)
    p.cue('the umbrellas', t)
    street.block_harmony(p, t, CH_SHOUT, SHOUT, vel=104)
    figures.scoop(p, 'cornet', t + 1.5, semitones=1.0)
    figures.scoop(p, 'cornet', t + 33.5, semitones=1.0)
    for k, (b, beat) in enumerate(SHOUT_ANSWERS):
        street.snare_answer(p, t + 4 * b + beat, vel=100, variant=k)
    # trombone: the roots, punched, under the shout; two-beat sousaphone
    street.riff(p, 'tbn', t, CH_SHOUT, 16, 'Bb2', 'Bb3', rhythm='charleston',
                vel=90, tones=(0, 0))
    street.two_beat(p, t, CH_SHOUT, 16, vel=104, near='Ab1', next_sym='Ab')
    for b in range(16):
        answer = any(b == ab for ab, _ in SHOUT_ANSWERS)
        if answer:
            # drummers hold the first half, then answer
            for off, dv in ((0.0, 8), (1.5, -8)):
                p.perc(t + 4 * b + off, [('kick', 0.25)], vel=94 + dv, inst=BD)
            p.perc(t + 4 * b + 1.0, [('hhc', 0.3)], vel=62, inst=BD)
            p.perc(t + 4 * b + 0.0, [('sn', 0.25)], vel=86, inst=SN)
            p.perc(t + 4 * b + 1.0, [('sn', 0.25)], vel=100, inst=SN)
        else:
            street.street_beat(p, t + 4 * b, 1, vel=92, crash_first=(b == 0),
                               fill_every=(1 if b in (11, 15) else 0),
                               cell0=b)
    p.perc(t + 32, [('crash', 1)], vel=100, inst=BD)


def turn_for_home(p):
    t = bar(TO_EB)
    p.mark('turn for home', t)
    for i in range(2):
        for off, d in ((0.0, 0.75), (1.5, 0.5), (3.0, 0.5)):
            street.stab(p, t + 4 * i + off, 'Bb7', vel=104, dur=d,
                        who=('clarinet', 'alto', 'tbn'), sousa=False, drums=False)
    for k, q in enumerate(['Bb1', 'D2', 'F2', 'Ab2', 'Bb2', 'Ab2', 'G2', 'Gb2']):
        p.note('sousa', t + k, q, 0.8, vel=100 + 2 * (k % 4), gate=0.85)
    street.street_beat(p, t, 2, vel=92, crash_first=True, fill_every=2, cell0=1)
    # the cornet's two-bar break: a rip up and a run down into the call
    figures.smear_into(p, 'cornet', 'Bb5', t + 8, 104, n=5)
    p.add('cornet', t + 8, CORNET_TURN, vel=108, vel_end=100, gate=0.85)
    street.drum_break(p, t + 8, 2, vel=90)
    p.note('sousa', t + 8, 'F2', 0.8, vel=100, gate=0.85)
    p.note('sousa', t + 10, 'F1', 0.8, vel=100, gate=0.85)
    p.note('sousa', t + 14, 'D2', 0.8, vel=100, gate=0.85)
    p.note('sousa', t + 15, 'D2', 0.8, vel=104, gate=0.85)


def home(p):
    t = bar(HOME)
    p.mark('home - the strut at full boil', t)
    p.add('cornet', t, STRUT_OUT, vel=106, gate=0.85)
    figures.scoop(p, 'cornet', t + 1.5, semitones=1.0)
    figures.scoop(p, 'cornet', t + 33.5, semitones=1.5)
    figures.falloff(p, 'cornet', 'Bb5', t + 35.0, 104, n=4)
    street.obbligato(p, t, CH_STRUT, 16, STRUT_OUT, energy=0.9, vel=82,
                     anchor='C6', hi='G6', hold_prob=0.75)
    for b, beat, dsl in STRUT_FILLS:
        p.add('clarinet', t + 4 * b + beat, dsl, vel=90, transpose=0, gate=0.85)
    street.tailgate(p, t, CH_STRUT, 16, vel=86, density=0.95, near='Eb3')
    street.riff(p, 'alto', t, CH_STRUT, 16, 'G4', 'Eb5', rhythm='charleston',
                vel=78, tones=(1, 2))
    street.two_beat(p, t, CH_STRUT[:8], 8, vel=104, near='Eb2', next_sym='Eb7')
    street.two_beat(p, t + 32, CH_STRUT[8:], 8, vel=108, near='Eb2',
                    next_sym='Eb', four=True)
    p.cue('the sousaphone walks', t + 32)
    street.street_beat(p, t, 16, vel=94, fill_every=4, cell0=0)


def the_tag(p):
    t = bar(TAG)
    p.mark('the tag', t)
    # everyone plays the head in octaves
    street.unison(p, t, UNISON_TAG, 104, [('cornet', 0, 4), ('clarinet', 12, -6),
                                          ('alto', 0, -2), ('tbn', -12, 0),
                                          ('sousa', -24, 2)])
    for off, dv in ((0.0, 6), (0.5, -4), (1.5, 8), (3.5, 0), (4.5, -4), (5.0, 2)):
        p.perc(t + off, [('kick', 0.25)], vel=100 + dv, inst=BD)
        p.perc(t + off, [('sn', 0.25)], vel=96 + dv, inst=SN)
    p.perc(t, [('crash', 1)], vel=104, inst=BD)
    figures.press_roll(p, t + 8, 104, n=5, inst=SN)
    # I - VI7 - II7 - V7 hits with the snare drum in the gaps
    for k, (off, sym) in enumerate(((8, 'Eb'), (10, 'C7'), (12, 'F7'), (14, 'Bb7'))):
        street.stab(p, t + off, sym, vel=106, dur=0.6,
                    who=('cornet', 'clarinet', 'alto', 'tbn'))
        street.snare_answer(p, t + off + 0.75, vel=94, variant=k)
    # one bar of the drummers, then the last chord
    street.drum_break(p, t + 16, 1, vel=104)
    tf = t + 20
    p.cue('the last chord', tf)
    figures.smear_into(p, 'cornet', 'Bb5', tf, 110, n=5)
    p.note('cornet', tf, 'Bb5', 7.5, vel=112, gate=1.0)
    figures.trill(p, 'clarinet', 'Eb6', tf, 7.5, 96, unit=0.125)
    p.note('alto', tf, 'G5', 7.5, vel=100, gate=1.0)
    figures.scoop(p, 'tbn', tf, semitones=2.0)
    p.note('tbn', tf, 'Bb3', 7.5, vel=104, gate=1.0)
    p.note('sousa', tf, 'Eb1', 7.5, vel=110, gate=1.0)
    p.perc(tf, [('crash', 4)], vel=108, inst=BD)
    p.perc(tf, [('kick', 1)], vel=110, inst=BD)
    figures.perc_roll(p, 'sn', tf, 7.0, 70, 96, unit=1 / 16, inst=SN)
    for inst in ('cornet', 'clarinet', 'alto', 'tbn', 'sousa'):
        p.hairpin(inst, tf + 4, tf + 7.4, 118, 70)
    p.perc(tf + 7.5, [('kick', 0.5)], vel=112, inst=BD)
    p.perc(tf + 7.5, [('crash', 1)], vel=110, inst=BD)
    p.perc(tf + 7.5, [('sn', 0.3)], vel=110, inst=SN)


# ================================================================ III. benediction
def benediction(p):
    t = bar(BENEDICT)
    p.tempo(t, 66, 'the walk, once more')
    p.mark('benediction', t)
    p.cue('benediction', t)
    for inst in ('cornet', 'sousa'):
        p.cc(inst, t - 0.5, 11, 104)
    street.cry(p, 'cornet', t, t + 12, depth=104, rise=1.5)
    p.add('cornet', t, BENEDICTION, vel=62, vel_end=56, gate=0.98)
    p.hairpin('cornet', t + 8.5, t + 11.8, 104, 48)
    # the band answers once under the last note
    p.note('sousa', t + 8, 'Eb1', 4, vel=44, gate=0.98)
    p.hairpin('sousa', t + 8.5, t + 11.8, 104, 40)
    p.perc(t + 8, [('kick', 2)], vel=54, inst=BD)
    p.perc(t + 8, [('crash', 3)], vel=30, inst=BD)


def build() -> Piece:
    p = Piece(brass_band(), seed=1917,
              title='Cut Loose — a second line for a cornet player')
    p.meter(0, 4, 4)
    p.key(0, 'E-')
    p.key(bar(RAMBLE1), 'A-')
    p.key(bar(HOME), 'E-')
    cadence(p)
    the_hymn(p)
    the_cry(p)
    amen(p)
    the_whistle(p)
    snares_on(p)
    sousa_riff(p)
    riffing_in(p)
    strut_one(p)
    strut_two(p)
    around_the_corner(p)
    the_ramble(p)
    trombone_takes_it(p)
    clarinet_takes_it(p)
    the_umbrellas(p)
    turn_for_home(p)
    home(p)
    the_tag(p)
    benediction(p)
    return p


def check_cornet_silence(p) -> bool:
    """The cornet's first note must be the break in bar 45 (docs/03)."""
    first = min((n.start for n in p.notes if n.inst == 'cornet'), default=None)
    # the smear into his first note starts a few grace notes early
    ok = first is not None and bar(RIFF_IN) + 12 - 0.75 <= first < bar(STRUT1)
    print(f"cornet's first note at beat {first} (bar {first // 4 + 1:.0f}): "
          f"{'OK' if ok else 'TOO EARLY'}")
    return ok


def main():
    p = build()
    OUT.mkdir(exist_ok=True)
    ok = assess.report(p)
    ok = check_cornet_silence(p) and ok
    p.write(str(OUT / 'cut_loose.mid'), swing=SWING)
    p.write_marks(str(OUT / 'marks.json'))
    wav = OUT / 'cut_loose.wav'
    assess.pianoroll(p, str(OUT / 'roll.png'),
                     wav=str(wav) if wav.exists() else None)
    print()
    print(midi_report(str(OUT / 'cut_loose.mid')))
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
