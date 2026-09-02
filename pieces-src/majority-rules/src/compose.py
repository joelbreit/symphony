"""Majority Rules — a town meeting for seven walking musicians.

    ../../.venv/bin/python src/compose.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib import Piece, assess, figures, midi_report

import street
from band import brass_band
from street import BD, SN
from themes import (ALTO_BALLOT, AMENDMENT, AMENDMENT_VOTES, CH_AMENDMENT,
                    CH_FILIBUSTER, CH_MOTION, CLARINET_BALLOT, CORNET_BALLOT,
                    FILIBUSTER, FINAL_HOOK, MOTION, MOTION_HALF,
                    MOTION_HOOK, REBUTTAL_CORNET, TBN_BALLOT,
                    TBN_OPPOSITION)

OUT = pathlib.Path(__file__).resolve().parents[1] / 'output'
SWING = 0.58


def bar(n):
    return 4 * (n - 1)


CALL, MOTION1, AMENDMENT1, MOTION2 = 1, 5, 21, 37
ORDER, OPPOSITION, REBUTTAL, MOTION3 = 53, 61, 77, 85
FILIBUSTER1, TABLE, ROLL_CALL = 101, 117, 125
UNANIMOUS, RECOUNT, FINAL, END = 141, 157, 161, 165


def call_to_order(p):
    t = bar(CALL)
    p.tempo(t, 176, 'with entirely too much confidence')
    p.mark('call to order', t)
    street.dry(p, t)
    # The snare calls a room to order; the sousaphone starts counting anyway.
    figures.perc_roll(p, 'sn', t, 3.5, 38, 90, unit=1 / 16, inst=SN)
    p.perc(t, [('kick', 0.5)], vel=76, inst=BD)
    p.perc(t + 3.5, [('crash', 0.8)], vel=88, inst=BD)
    for i, q in enumerate(('Bb1', 'F2', 'Bb2', 'A2', 'G2', 'F2', 'D2', 'F2')):
        p.note('sousa', t + 4 + i, q, 0.8, vel=72 + i * 2, gate=0.82)
    p.cue('the gavel', t + 12)
    street.gavel(p, t + 12, 'Bb6', vel=100)


def the_motion(p):
    t = bar(MOTION1)
    p.mark('the motion', t)
    p.add('cornet', t, MOTION, vel=94, vel_end=100, gate=0.84)
    figures.scoop(p, 'cornet', t + 0.5, semitones=1.0)
    figures.falloff(p, 'cornet', 'Bb5', t + 62.0, 96, n=3)
    street.obbligato(p, t, CH_MOTION, 16, MOTION, energy=0.48, vel=72,
                     anchor='F6', hi='G6')
    street.riff(p, 'alto', t, CH_MOTION, 16, 'F4', 'F5',
                rhythm='offbeats', vel=68, tones=(1, 2))
    street.tailgate(p, t, CH_MOTION, 16, vel=76, density=0.78, near='F3')
    street.two_beat(p, t, CH_MOTION, 16, vel=94, near='Bb1', next_sym='Eb6')
    street.street_beat(p, t, 16, vel=82, crash_first=True, fill_every=4)


def the_amendment(p):
    t = bar(AMENDMENT1)
    p.mark('the amendment', t)
    p.key(t, 'E-')
    # Alto speaks warmly, one octave below the written prototype.
    p.add('alto', t, AMENDMENT, transpose=-12, vel=88, vel_end=94, gate=0.88)
    figures.scoop(p, 'alto', t + 1.0, semitones=0.8)
    # Cornet cannot resist objecting in the phrase-end breaths.
    for k, (off, dsl) in enumerate((
            (14, 'r:q Bb4:e D5:e F5:q'),
            (30, 'r:q F5:e Ab5:e Bb5:q'),
            (46, 'r:q D5:e F5:e G5:q'),
            (62, 'r:q C5:e D5:e Bb4:q'))):
        p.add('cornet', t + off, dsl, vel=76 + 2 * k, gate=0.78)
    street.riff(p, 'clarinet', t, CH_AMENDMENT, 16, 'G5', 'G6',
                rhythm='and-of-4', vel=70, tones=(2, 1))
    street.pads(p, 'tbn', t, CH_AMENDMENT, 16, 'Bb2', 'Bb3', vel=58)
    street.two_beat(p, t, CH_AMENDMENT, 16, vel=92, near='Eb2', next_sym='Bb6')
    street.street_beat(p, t, 16, vel=80, crash_first=True, fill_every=4, cell0=1)


def motion_amended(p):
    t = bar(MOTION2)
    p.mark('the motion, amended', t)
    p.key(t, 'B-')
    p.add('clarinet', t, MOTION, vel=91, vel_end=96, gate=0.84)
    p.add('alto', t, AMENDMENT_VOTES, vel=70, vel_end=76, gate=0.92)
    street.riff(p, 'cornet', t, CH_MOTION, 16, 'Bb4', 'Bb5',
                rhythm='charleston', vel=72, tones=(2, 1))
    street.tailgate(p, t, CH_MOTION, 16, vel=78, density=0.86, near='F3')
    street.two_beat(p, t, CH_MOTION, 16, vel=98, near='Bb1', next_sym='Bb7')
    street.street_beat(p, t, 16, vel=85, crash_first=True, fill_every=4, cell0=2)


def point_of_order(p):
    t = bar(ORDER)
    p.mark('point of order', t)
    p.cue('four objections', t)
    speeches = (
        ('cornet', 'r:e D5:e F5:e Bb5:q. A5:e F5:e D5:q r:q', 100),
        ('clarinet', 'r:q Bb5:e D6:e F6:e G6:e F6:q D6:q r:h', 96),
        ('alto', 'r:e D4:e F4:q Bb4:e A4:e G4:q F4:q D4:q r:h', 94),
        ('tbn', 'r:q F3:e Ab3:e Bb3:q D4:q C4:e A3:e F3:q r:h', 100),
    )
    chords = ('Bb6', 'G7', 'C7', 'F7')
    for i, ((inst, dsl, vel), sym) in enumerate(zip(speeches, chords)):
        bt = t + 8 * i
        street.stab(p, bt, sym, vel=98, dur=0.45,
                    who=tuple(x for x in ('cornet', 'clarinet', 'alto', 'tbn')
                              if x != inst))
        p.add(inst, bt, dsl, vel=vel, gate=0.8)
        street.snare_answer(p, bt + 6, vel=90, variant=i)
        p.note('sousa', bt, ('Bb1', 'G1', 'C2', 'F1')[i], 0.8,
               vel=94, gate=0.82)
    p.perc(t + 31.5, [('crash', 0.8)], vel=96, inst=BD)


def honorable_opposition(p):
    t = bar(OPPOSITION)
    p.mark('the honorable opposition', t)
    p.key(t, 'E-')
    p.add('tbn', t, TBN_OPPOSITION, vel=94, vel_end=101, gate=0.83)
    for off in (1.0, 16.0, 32.0, 44.0):
        figures.scoop(p, 'tbn', t + off, semitones=1.5)
    figures.falloff(p, 'tbn', 'Bb4', t + 61.0, 102, n=4)
    street.riff(p, 'clarinet', t, CH_AMENDMENT, 16, 'G5', 'G6',
                rhythm='offbeats', vel=68, tones=(2, 1))
    street.riff(p, 'alto', t, CH_AMENDMENT, 16, 'Eb4', 'F5',
                rhythm='push', vel=68, tones=(1, 2), every=2)
    street.pads(p, 'cornet', t + 32, CH_AMENDMENT[8:], 8, 'Bb4', 'G5', vel=54)
    street.two_beat(p, t, CH_AMENDMENT, 16, vel=96, near='Eb2', next_sym='C7')
    street.street_beat(p, t, 16, vel=84, crash_first=True, fill_every=4, cell0=3)


def rebuttal(p):
    t = bar(REBUTTAL)
    p.mark('rebuttal', t)
    p.key(t, 'B-')
    chart = ['C7', 'C7', 'F7', 'F7', 'G7', 'Cm7', 'F7', 'Bb6']
    p.add('cornet', t, REBUTTAL_CORNET, vel=98, vel_end=102, gate=0.82)
    # Trombone butts in after each two-bar claim.
    for off, dsl in ((6, 'r:q E3:e G3:e Bb3:q C4:q'),
                     (14, 'r:q F3:e A3:e C4:q Eb4:q'),
                     (22, 'r:q B3:e D4:e F4:q G4:q'),
                     (30, 'r:q C4:e Eb4:e F4:q Bb3:q')):
        p.add('tbn', t + off, dsl, vel=90, gate=0.76)
    street.riff(p, 'clarinet', t, chart, 8, 'G5', 'G6', rhythm='offbeats',
                vel=72, tones=(1, 2))
    street.riff(p, 'alto', t, chart, 8, 'F4', 'F5', rhythm='charleston',
                vel=70, tones=(1, 2))
    street.two_beat(p, t, chart, 8, vel=100, near='C2', next_sym='Bb6')
    street.street_beat(p, t, 8, vel=88, crash_first=True, fill_every=4)


def motion_returns(p):
    t = bar(MOTION3)
    p.mark('the motion carries', t)
    p.add('cornet', t, MOTION, vel=102, vel_end=106, gate=0.82)
    street.obbligato(p, t, CH_MOTION, 16, MOTION, energy=0.82, vel=80,
                     anchor='F6', hi='G6', hold_prob=0.72)
    street.tailgate(p, t, CH_MOTION, 16, vel=84, density=0.92, near='F3')
    street.riff(p, 'alto', t, CH_MOTION, 16, 'F4', 'F5',
                rhythm='offbeats', vel=76, tones=(1, 2))
    street.two_beat(p, t, CH_MOTION, 16, vel=104, near='Bb1', next_sym='Gm7')
    street.street_beat(p, t, 16, vel=91, crash_first=True, fill_every=4)


def the_filibuster(p):
    t = bar(FILIBUSTER1)
    p.mark('the filibuster', t)
    p.key(t, 'g')
    p.add('clarinet', t, FILIBUSTER, vel=86, vel_end=104, gate=0.82)
    figures.curl(p, 'clarinet', 'F6', t + 32, 96)
    figures.trill(p, 'clarinet', 'F6', t + 58, 2, 104, unit=0.125)
    street.pads(p, 'alto', t, CH_FILIBUSTER, 16, 'Eb4', 'F5', vel=56)
    street.riff(p, 'tbn', t, CH_FILIBUSTER, 16, 'Bb2', 'Bb3',
                rhythm='charleston', vel=66, tones=(0, 2), every=2)
    # The chair tries three times to recover the floor.
    for off, sym in ((44, 'Bb6'), (52, 'C7'), (60, 'F7')):
        street.stab(p, t + off, sym, vel=86, dur=0.35,
                    who=('cornet', 'alto', 'tbn'), sousa=False, drums=False)
    street.two_beat(p, t, CH_FILIBUSTER, 16, vel=96, near='G1', next_sym='Bb6')
    street.street_beat(p, t, 16, vel=84, crash_first=False, fill_every=4, cell0=1)


def table_the_motion(p):
    t = bar(TABLE)
    p.mark('table the motion', t)
    p.cue('the clerk keeps counting', t)
    p.key(t, 'B-')
    # Horns vanish: the clerk and the public gallery continue the meeting.
    bass = ('Bb1', 'F2', 'Bb2', 'A2', 'G2', 'Gb2', 'F2', 'E2',
            'Eb2', 'D2', 'Db2', 'C2', 'F1', 'A1', 'C2', 'F2',
            'Bb1', 'D2', 'F2', 'Ab2', 'G2', 'C2', 'F1', 'A1',
            'Bb1', 'F2', 'D2', 'C2', 'Bb1', 'D2', 'F2', 'A2')
    for i, q in enumerate(bass):
        p.note('sousa', t + i, q, 0.78, vel=74 + min(i, 16), gate=0.8)
    street.drum_break(p, t, 8, vel=82)
    p.perc(t, [('crash', 0.7)], vel=72, inst=BD)


def roll_call(p):
    t = bar(ROLL_CALL)
    p.mark('roll call', t)
    ballots = (('cornet', CORNET_BALLOT, 98), ('clarinet', CLARINET_BALLOT, 94),
               ('alto', ALTO_BALLOT, 94), ('tbn', TBN_BALLOT, 100))
    for i, (inst, line, vel) in enumerate(ballots):
        bt = t + 16 * i
        p.cue(f'{inst} votes aye', bt)
        p.add(inst, bt, line, vel=vel, vel_end=vel + 3, gate=0.82)
        p.perc(bt, [('crash', 0.8)], vel=88 + i * 2, inst=BD)
    street.two_beat(p, t, CH_MOTION, 16, vel=100, near='Bb1', next_sym='Bb6',
                    walk_every=4)
    street.street_beat(p, t, 16, vel=87, crash_first=False, fill_every=4, cell0=2)


def unanimous(p):
    t = bar(UNANIMOUS)
    p.tempo(t, 184, 'the vote spills into the street')
    p.mark('unanimous', t)
    p.cue('motion and amendment agree', t)
    street.block_harmony(p, t, CH_MOTION, MOTION, vel=108)
    # The amendment is now the trombone's answer beneath the block-harmony motion.
    p.add('tbn', t, AMENDMENT_VOTES, transpose=-12, vel=88, vel_end=96, gate=0.84)
    street.two_beat(p, t, CH_MOTION, 16, vel=108, near='Bb1', next_sym='Bb6',
                    four=True)
    street.street_beat(p, t, 16, vel=96, crash_first=True, fill_every=4, cell0=0)
    for off in (16, 32, 48):
        p.perc(t + off, [('crash', 1)], vel=104, inst=BD)


def recount(p):
    t = bar(RECOUNT)
    p.mark('recount', t)
    # Three endings, each immediately contradicted by a different loudmouth.
    street.stab(p, t, 'Bb6', vel=108, dur=1.8,
                who=('cornet', 'clarinet', 'alto', 'tbn'))
    p.add('clarinet', t + 2.5, 'F6:e G6:e F6:e D6:e', vel=102, gate=0.75)
    street.stab(p, t + 4, 'Bb6', vel=110, dur=2.2,
                who=('cornet', 'clarinet', 'alto', 'tbn'))
    figures.falloff(p, 'tbn', 'Bb4', t + 6.5, 106, n=5)
    street.stab(p, t + 8, 'Bb6', vel=112, dur=2.8,
                who=('cornet', 'clarinet', 'alto', 'tbn'))
    street.snare_answer(p, t + 11, vel=108, variant=3)
    # One bar of suspicious silence, except for the sousaphone clearing its throat.
    p.note('sousa', t + 14.5, 'F1', 0.35, vel=48, gate=0.7)
    p.note('sousa', t + 15.2, 'A1', 0.35, vel=56, gate=0.7)


def majority_rules(p):
    t = bar(FINAL)
    p.mark('majority rules', t)
    street.unison(p, t, FINAL_HOOK, 108,
                  [('cornet', 0, 4), ('clarinet', 0, -5), ('alto', -12, -2),
                   ('tbn', -12, 0), ('sousa', -36, 3)])
    street.street_beat(p, t, 2, vel=98, crash_first=True, fill_every=2)
    street.gavel(p, t + 8, 'Bb6', vel=112, final=True)
    tf = t + 12
    p.cue('the vote', tf)
    p.note('cornet', tf, 'Bb5', 7.5, vel=116, gate=1.0)
    p.note('clarinet', tf, 'F6', 7.5, vel=108, gate=1.0)
    p.note('alto', tf, 'D5', 7.5, vel=110, gate=1.0)
    p.note('tbn', tf, 'Bb3', 7.5, vel=112, gate=1.0)
    p.note('sousa', tf, 'Bb1', 7.5, vel=118, gate=1.0)
    p.perc(tf, [('kick', 0.8)], vel=120, inst=BD)
    p.perc(tf, [('crash', 4)], vel=116, inst=BD)
    figures.perc_roll(p, 'sn', tf, 7.0, 72, 108, unit=1 / 16, inst=SN)
    for inst in ('cornet', 'clarinet', 'alto', 'tbn', 'sousa'):
        p.hairpin(inst, tf + 3, tf + 7.4, 118, 76)
    p.perc(tf + 7.5, [('kick', 0.5)], vel=120, inst=BD)
    p.perc(tf + 7.5, [('crash', 1)], vel=118, inst=BD)
    p.perc(tf + 7.5, [('sn', 0.3)], vel=116, inst=SN)


def build() -> Piece:
    p = Piece(brass_band(), seed=1920, title='Majority Rules — a town meeting in B-flat')
    p.meter(0, 4, 4)
    p.key(0, 'B-')
    call_to_order(p)
    the_motion(p)
    the_amendment(p)
    motion_amended(p)
    point_of_order(p)
    honorable_opposition(p)
    rebuttal(p)
    motion_returns(p)
    the_filibuster(p)
    table_the_motion(p)
    roll_call(p)
    unanimous(p)
    recount(p)
    majority_rules(p)
    return p


def verify_design(p) -> bool:
    expected = {'cornet', 'clarinet', 'alto', 'tbn', 'sousa', 'snare', 'bassdrum'}
    roster_ok = {i.key for i in p.ensemble} == expected
    length_ok = 3.4 * 60 <= p.seconds(p.end()) <= 4.5 * 60
    final_bass = [n for n in p.notes if n.inst == 'sousa' and n.start >= bar(FINAL) + 12]
    tonic_ok = bool(final_bass) and final_bass[-1].pitch % 12 == 10
    print(f'roster exactly seven: {"OK" if roster_ok else "FAIL"}')
    print(f'duration 3:24..4:30: {"OK" if length_ok else "FAIL"}')
    print(f'final sousaphone vote is B-flat: {"OK" if tonic_ok else "FAIL"}')
    return roster_ok and length_ok and tonic_ok


def main():
    p = build()
    OUT.mkdir(exist_ok=True)
    ok = assess.report(p)
    ok = verify_design(p) and ok
    p.write(str(OUT / 'majority_rules.mid'), swing=SWING)
    p.write_marks(str(OUT / 'marks.json'))
    wav = OUT / 'majority_rules.wav'
    assess.pianoroll(p, str(OUT / 'roll.png'),
                     wav=str(wav) if wav.exists() else None)
    print()
    print(midi_report(str(OUT / 'majority_rules.mid')))
    if not ok:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
