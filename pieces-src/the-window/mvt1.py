"""Movement I — Kindling.

Adagio misterioso (fragments coalescing out of darkness) -> Allegro con
fuoco sonata. C minor. The motto is assembled, stated, argued — and the
movement ends with its D defiantly unresolved.

Layout (quarterLength offsets from t0):
    0- 64  intro (16 bars, q=54)
   64-288  exposition (56 bars, q=144)
  288-464  development (44 bars)
  464-656  recapitulation (48 bars)
  656-712  coda (14 bars, q=152)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import (Orchestra, write_midi, midi_report, check_ranges,
                            trem, roll, total_ql, transpose_events, parse)
from themes import T1, T1_HEAD, T2

BAR = 4.0

def B(dsl, n=1):
    """Assert a melody string spans exactly n bars of 4/4."""
    got = total_ql(dsl)
    assert abs(got - 4.0 * n) < 1e-6, f'bad bar sum {got} != {4*n}: {dsl[:60]}'
    return dsl

def R(dsl, times):
    """Repeat a DSL fragment with proper spacing."""
    return ' '.join([dsl] * times)

# ---------------------------------------------------------------- harmony engine

def H(bass, vc4, pad, hn=None, bsn=None):
    return dict(bass=bass, vc=vc4, pad=pad, hn=hn, bsn=bsn)

Cm  = H('C2',  ['C3', 'G3', 'C4', 'G3'],   ['G3', 'C4', 'Eb4'],  hn=['C4', 'Eb4', 'G4'],  bsn=['C3', 'G3'])
G7  = H('G2',  ['G2', 'D3', 'G3', 'D3'],   ['G3', 'B3', 'F4'],   hn=['B3', 'D4', 'G4'],   bsn=['G2', 'D3'])
GM  = H('G2',  ['G2', 'D3', 'G3', 'D3'],   ['G3', 'B3', 'D4'],   hn=['G3', 'B3', 'D4'],   bsn=['G2', 'D3'])
Eb  = H('Eb2', ['Eb3', 'Bb3', 'Eb4', 'Bb3'], ['G3', 'Bb3', 'Eb4'], hn=['Eb4', 'G4', 'Bb4'], bsn=['Eb3', 'Bb3'])
Ab  = H('Ab1', ['Ab2', 'Eb3', 'Ab3', 'Eb3'], ['Ab3', 'C4', 'Eb4'], hn=['C4', 'Eb4', 'Ab4'], bsn=['Ab2', 'Eb3'])
Fm  = H('F2',  ['F2', 'C3', 'F3', 'C3'],   ['Ab3', 'C4', 'F4'],  hn=['F3', 'Ab3', 'C4'],  bsn=['F2', 'C3'])
Dh  = H('F2',  ['F2', 'D3', 'F3', 'Ab3'],  ['F3', 'Ab3', 'D4'],  hn=['F3', 'Ab3', 'D4'],  bsn=['F2', 'D3'])   # ii-half-dim
Bb7 = H('Bb1', ['Bb2', 'F3', 'Bb3', 'F3'], ['F3', 'Ab3', 'D4'],  hn=['F3', 'Bb3', 'D4'],  bsn=['Bb2', 'F3'])
CM  = H('C2',  ['C3', 'G3', 'C4', 'G3'],   ['G3', 'C4', 'E4'],   hn=['C4', 'E4', 'G4'],   bsn=['C3', 'G3'])
FM  = H('F2',  ['F2', 'C3', 'F3', 'C3'],   ['A3', 'C4', 'F4'],   hn=['F3', 'A3', 'C4'],   bsn=['F2', 'C3'])
Am  = H('A1',  ['A2', 'E3', 'A3', 'E3'],   ['A3', 'C4', 'E4'],   hn=['A3', 'C4', 'E4'],   bsn=['A2', 'E3'])
Gm  = H('G2',  ['G2', 'D3', 'G3', 'D3'],   ['G3', 'Bb3', 'D4'],  hn=['G3', 'Bb3', 'D4'],  bsn=['G2', 'D3'])
Db  = H('Db2', ['Db3', 'Ab3', 'Db4', 'Ab3'], ['F3', 'Ab3', 'Db4'], hn=['F3', 'Ab3', 'Db4'], bsn=['Db3', 'Ab3'])
Bbm = H('Bb1', ['Bb2', 'F3', 'Bb3', 'F3'], ['F3', 'Bb3', 'Db4'], hn=['F3', 'Bb3', 'Db4'], bsn=['Bb2', 'F3'])
Bdim= H('B1',  ['B2', 'F3', 'Ab3', 'F3'],  ['F3', 'Ab3', 'B3'],  hn=['F3', 'Ab3', 'B3'],  bsn=['B2', 'F3'])

def pump(o, t, prog, vel='f', pad_vel=None, with_hn=False, with_bsn=True,
         timp_roots=('C2', 'G2', 'G1')):
    """Driving allegro accompaniment: cb quarters, vc eighths, vla offbeats."""
    pad_vel = pad_vel or vel
    for i, h in enumerate(prog):
        bt = t + i * BAR
        o.add('cb', bt, [(h['bass'], 1.0)] * 4, vel=vel, gate=0.85)
        o.add('vc', bt, [(p, 0.5) for p in h['vc'] * 2], vel=vel, gate=0.8)
        o.add('vla', bt, [(None, 0.5), (h['pad'], 0.5)] * 4, vel=pad_vel, gate=0.6)
        if with_bsn and h['bsn']:
            o.add('bsn', bt, [(h['bsn'], 2.0)] * 2, vel=pad_vel, gate=0.95)
        if with_hn and h['hn']:
            o.add('hn', bt, [(h['hn'], 4.0)], vel=pad_vel, gate=1.0)
        timp_pitch = {'C2': 'C3', 'G2': 'G2', 'G1': 'G2'}.get(h['bass'])
        if timp_pitch and h['bass'] in timp_roots:
            o.add('timp', bt, [(timp_pitch, 1.0), (None, 3.0)], vel=vel)

# ================================================================ sections

def intro(o, t):
    o.timesig(t, '4/4')
    o.tempo(t, 54, 'Adagio misterioso')

    # b1-8: darkness, low C pedal; fragments of the motto drift in
    o.add('cb', t, 'C2:w ' * 8, vel='pp', gate=1.0)
    o.add('timp', t, roll('C3', 8, 0.5), vel='ppp', vel_end='pp')
    o.add('vc', t, 'C2:w C2:w C2:w C2:w', vel='pp', gate=1.0)
    o.add('vc', t + 4, 'G2:q C3:3', vel='pp')                    # rising 4th
    o.add('vla', t + 8, 'r:h Eb4:q D4:5', vel='pp', gate=1.0)    # the fall
    o.add('cl', t + 16, 'G3:q C4:7', vel='pp', gate=1.0)
    o.add('hp', t + 16, 'C2:e G2:e C3:e Eb3:e G3:e C4:e r:q', vel='p', gate=1.0)
    o.add('ob', t + 20, 'Eb5:q D5:7', vel='p', gate=1.0)
    o.add('bsn', t + 24, 'G2:q C3:3', vel='p')
    o.add('vln2', t + 24, 'G3:w G3:w', vel='pp', gate=1.0)

    # b9-12: fragments overlap, slight accel, tremolo shimmer
    o.tempo(t + 32, 58)
    o.add('fl', t + 32, 'Eb6:q D6:3', vel='p', gate=1.0)
    o.add('hn', t + 32, 'G3:q C4:3', vel='mp', gate=1.0)
    o.add('vla', t + 32, trem(['C4', 'Eb4'], 16, 0.5), vel='pp', vel_end='mp', gate=1.0)
    o.add('vc', t + 36, 'G2:q C3:q Eb3:q G3:q', vel='mp')
    o.add('cb', t + 32, 'C2:w ' * 4, vel='pp', vel_end='mp', gate=1.0)
    o.add('vln2', t + 40, 'G4:q C5:3', vel='mp', gate=1.0)
    o.add('bsn', t + 40, 'C3:q G2:q C3:h', vel='mp')
    o.add('ob', t + 44, 'Eb5:q D5:q Eb5:q F5:q', vel='mp', vel_end='mf')
    o.add('cl', t + 44, 'C5:q B4:q C5:q D5:q', vel='mp', vel_end='mf')

    # b13-16: the assembly — crescendo into the first full motto
    o.tempo(t + 48, 60)
    o.add('vln1', t + 48, trem('G4', 8, 0.5), vel='mf', vel_end='f', gate=1.0)
    o.add('vln2', t + 48, trem('Eb4', 8, 0.5), vel='mf', vel_end='f', gate=1.0)
    o.add('timp', t + 48, roll('C3', 16, 0.25), vel='p', vel_end='ff')
    o.add('cb', t + 48, 'C2:w C2:w C2:w C2:w', vel='mp', vel_end='ff', gate=1.0)
    o.add('vc', t + 48, 'C3:h G2:h C3:h Eb3:h', vel='mf', vel_end='ff', gate=1.0)
    o.add('hn', t + 52, '(C4 Eb4 G4):w', vel='mf', gate=1.0)

    # b15-16: FULL MOTTO, ff, brass in octaves; strings blaze
    o.tempo(t + 56, 50, 'Allargando')
    motto = 'G4:q C5:q Eb5:q D5:q D5:w'
    o.add('tpt', t + 56, B(motto, 2), vel='ff', gate=1.0)
    o.add('tbn', t + 56, B(motto, 2), vel='ff', transpose=-12, gate=1.0)
    o.add('hn', t + 56, B(motto, 2), vel='ff', transpose=-12, gate=1.0)
    o.add('vln1', t + 56, trem('G5', 8, 0.5), vel='f', vel_end='ff', gate=1.0)
    o.add('vln2', t + 56, trem(['C5', 'Eb5'], 8, 0.5), vel='f', vel_end='ff', gate=1.0)
    o.add('vla', t + 56, trem(['C4', 'G4'], 8, 0.5), vel='f', vel_end='ff', gate=1.0)
    o.add('vc', t + 56, 'C2:w C2:w', vel='ff', gate=1.0)
    o.add('cb', t + 56, 'C2:w C2:w', vel='ff', gate=1.0)
    o.perc(t + 56, [('susp', 0.25)] * 16, vel='pp')
    o.add('fl', t + 60, 'C5:s D5:s Eb5:s F5:s G5:s Ab5:s B5:s C6:s '
                        'D6:s Eb6:s F6:s G6:s Ab6:s Bb6:s B6:s C7:s', vel='f', vel_end='ff')

def expo(o, t):
    o.tempo(t, 144, 'Allegro con fuoco')
    o.perc(t, 'crash:q', vel='ff')

    # ---- T1 group, bars 1-8: theme in violins over driving engine
    prog = [Cm, Cm, G7, Cm, Eb, Eb, G7, Cm]
    pump(o, t, prog, vel='f', pad_vel='mf')
    o.add('vln1', t, B(T1, 8), vel='f', vel_end='ff', accent_first=True)
    o.add('vln2', t, B(T1, 8), vel='f')
    o.add('fl', t + 16, B(' '.join(T1.split()[23:]), 4), vel='f')  # join at bar 5
    o.add('ob', t + 16, B(' '.join(T1.split()[23:]), 4), vel='f')
    o.add('timp', t, 'C3:q r:q r:h', vel='ff')
    o.add('timp', t + 28, 'G2:e G2:e C3:q r:h', vel='f')

    # ---- bars 9-12: counterstatement — theme in cellos/violas, violins counterline
    prog2 = [Cm, Ab, Fm, GM]
    for i, h in enumerate(prog2):
        bt = t + 32 + i * BAR
        o.add('cb', bt, [(h['bass'], 1.0)] * 4, vel='mf', gate=0.85)
        o.add('bsn', bt, [(h['bsn'], 2.0)] * 2, vel='mf', gate=0.95)
    o.add('vc', t + 32, B(' '.join(T1.split()[:23]), 4), vel='f', transpose=-12)
    o.add('vla', t + 32, B(' '.join(T1.split()[:23]), 4), vel='f', transpose=-12)
    counter = B('G5:e Eb5:e C5:e Eb5:e G5:e Eb5:e C6:e G5:e '
                'Ab5:e Eb5:e C5:e Eb5:e Ab5:e Eb5:e C6:e Ab5:e '
                'F5:e C5:e Ab4:e C5:e F5:e C5:e Ab5:e F5:e '
                'G5:e D5:e B4:e D5:e G5:e D5:e B5:e G5:e', 4)
    o.add('vln1', t + 32, counter, vel='mf')
    o.add('cl', t + 32, counter, vel='mp', transpose=-12)

    # ---- bars 13-16: cadential drive to half cadence
    prog3 = [Cm, Ab, Dh, GM]
    pump(o, t + 48, prog3, vel='ff', pad_vel='f', with_hn=True)
    cad = B('C6:q C6:e B5:e C6:q G5:q '
            'Ab5:q Ab5:e G5:e Ab5:q Eb5:q '
            'F5:q F5:e Eb5:e F5:q D5:q '
            'G5:w', 4)
    o.add('vln1', t + 48, cad, vel='ff')
    o.add('fl', t + 48, cad, vel='ff')
    o.add('ob', t + 48, cad, vel='f')
    o.add('tpt', t + 48, '(C5 Eb5):q r:q (C5 Eb5):q r:q (C5 Ab4):q r:q (C5 Ab4):q r:q '
                         '(D5 Ab4):q r:q (D5 B4):q r:q (D5 B4 G4):w', vel='f', gate=0.5)
    o.add('timp', t + 60, roll('G2', 4, 0.25), vel='mf', vel_end='f')

    # ---- transition, bars 17-24: sequence away, thin to pizzicato
    tt = t + 64
    o.add('vln1', tt, B(T1_HEAD), vel='f')
    o.add('vln2', tt, B(T1_HEAD), vel='f', transpose=-12)
    o.add('cb', tt, 'C2:q C2:q G2:q C2:q', vel='f', gate=0.85)
    o.add('vc', tt, [(p, 0.5) for p in Cm['vc'] * 2], vel='f', gate=0.8)
    o.add('ob', tt + 4, B(T1_HEAD), vel='mf', transpose=-2)        # Bb minor color
    o.add('bsn', tt + 4, 'Bb1:q Bb1:q F2:q Bb1:q', vel='mf', gate=0.85)
    o.add('vla', tt + 4, [(None, 0.5), (['F3', 'Bb3', 'Db4'], 0.5)] * 4, vel='mp', gate=0.6)
    o.add('cl', tt + 8, B(T1_HEAD), vel='mp', transpose=-4)        # Ab major color
    o.add('vc', tt + 8, 'Ab2:q Ab2:q Eb3:q Ab2:q', vel='mp', gate=0.85)
    o.add('bsn', tt + 12, 'F2:q Ab2:q Bb2:h', vel='mp')
    o.add('cl', tt + 12, 'F4:q Ab4:q Bb4:h', vel='mp', gate=1.0)
    # bars 21-24: dominant of Eb; pizzicato emerges
    o.program('vc', tt + 16, 45)
    o.program('cb', tt + 16, 45)
    o.program('vla', tt + 16, 45)
    o.add('cb', tt + 16, 'Bb1:q r:q Bb1:q r:q ' * 4, vel='mp', gate=0.5)
    o.add('vc', tt + 16, 'Bb2:q r:q F3:q r:q ' * 4, vel='mp', gate=0.5)
    o.add('fl', tt + 16, 'Bb5:e D6:e F6:e Ab6:e G6:e F6:e D6:e Bb5:e r:w', vel='mp', gate=0.7)
    o.add('hp', tt + 24, 'Bb2:e D3:e F3:e Ab3:e Bb3:e D4:e F4:e Ab4:e '
                         'Bb4:e Ab4:e F4:e D4:e Bb3:e Ab3:e F3:e D3:e', vel='mp', gate=1.0)

    # ---- T2, bars 25-32: woodwinds over pizzicato (Eb major)
    t2a = t + 96
    o.add('cl', t2a, B(T2, 8), vel='mf', gate=1.0)
    o.add('ob', t2a + 16, B(' '.join(T2.split()[14:]), 4), vel='mf', gate=1.0)
    t2_bass = ['Eb2', 'Eb2', 'Ab1', 'Bb1', 'Eb2', 'F2', 'Bb1', 'Eb2']
    t2_pads = [['G3', 'Bb3', 'Eb4'], ['G3', 'Bb3', 'Eb4'], ['Ab3', 'C4', 'Eb4'],
               ['F3', 'Bb3', 'D4'], ['G3', 'Bb3', 'Eb4'], ['Ab3', 'C4', 'F4'],
               ['F3', 'Ab3', 'D4'], ['G3', 'Bb3', 'Eb4']]
    for i in range(8):
        bt = t2a + i * BAR
        o.add('cb', bt, f'{t2_bass[i]}:q r:q {t2_bass[i]}:q r:q', vel='mp', gate=0.5)
        o.add('vc', bt, f"{t2_bass[i].replace('1', '2').replace('2', '3', 1) if False else t2_bass[i]}:q r:q r:h", vel='mp', gate=0.5, transpose=12)
        o.add('vla', bt, [(None, 1.0), (t2_pads[i], 1.0), (None, 1.0), (t2_pads[i], 1.0)], vel='mp', gate=0.5)

    # ---- T2 bars 33-40: strings espressivo (arco), warmer
    t2b = t2a + 32
    o.program('vc', t2b, 48)
    o.program('cb', t2b, 48)
    o.program('vla', t2b, 48)
    o.add('vln1', t2b, B(T2, 8), vel='mf', vel_end='f', gate=1.0)
    o.add('vln2', t2b, B(T2, 8), vel='mf', transpose=-12, gate=1.0)
    vc_counter = B('Eb3:h Bb3:q C4:q '
                   'Bb3:h Ab3:q G3:q '
                   'Ab3:h. Eb3:q '
                   'Bb3:h Bb2:h '
                   'Eb3:h F3:q G3:q '
                   'Ab3:h F3:h '
                   'Bb3:q Bb2:q D3:q Bb2:q '
                   'Eb3:w', 8)
    o.add('vc', t2b, vc_counter, vel='mf', gate=1.0)
    for i in range(8):
        o.add('cb', t2b + i * BAR, f'{t2_bass[i]}:h {t2_bass[i]}:h', vel='mp', gate=0.95)
        o.add('vla', t2b + i * BAR, [(t2_pads[i], 4.0)], vel='mp', gate=1.0)
    o.add('fl', t2b + 16, 'Bb5:h. Eb6:q G6:q. Ab6:e Bb6:q G6:q r:w r:w', vel='mp', gate=1.0)
    o.add('hp', t2b, 'Eb2:e Bb2:e G3:e Bb3:e Eb4:e Bb3:e G3:e Bb2:e ' * 2, vel='mp', gate=1.0)

    # ---- T2 climax, bars 41-48: tutti statement, full but warm
    t2c = t2b + 32
    o.add('vln1', t2c, B(T2, 8), vel='f', vel_end='ff', transpose=12, gate=1.0)
    o.add('fl', t2c, B(T2, 8), vel='ff', transpose=12, gate=1.0)
    o.add('ob', t2c, B(T2, 8), vel='f', gate=1.0)
    o.add('vln2', t2c, B(T2, 8), vel='f', gate=1.0)
    o.add('cl', t2c, B(T2, 8), vel='f', gate=1.0)
    hn_line = B('Eb4:h F4:h G4:h Eb4:h '
                'Ab4:h. G4:q F4:h Bb3:h '
                'Eb4:h F4:h Ab4:h F4:h '
                'Bb4:h G4:h Eb4:h. r:q', 8)
    o.add('hn', t2c, hn_line, vel='f', gate=1.0)
    for i in range(8):
        bt = t2c + i * BAR
        o.add('cb', bt, [(t2_bass[i], 1.0)] * 4, vel='f', gate=0.85)
        o.add('vc', bt, [(t2_bass[i], 0.5) for _ in range(8)], vel='f', gate=0.8, transpose=12)
        o.add('vla', bt, [(None, 0.5), (t2_pads[i], 0.5)] * 4, vel='mf', gate=0.6)
        o.add('bsn', bt, [(t2_bass[i], 2.0)] * 2, vel='mf', gate=0.95, transpose=12)
    o.add('timp', t2c + 28, roll('Eb2'.replace('Eb2', 'Eb3'), 4, 0.25), vel='mp', vel_end='f')
    o.perc(t2c + 16, 'crash:q', vel='f')

    # ---- codetta, bars 49-56: motto augmented in the bass under T2 wisps; turn dark
    cod = t2c + 32
    o.add('vc', cod, 'G2:h C3:h Eb3:h D3:h D3:w', vel='mp', gate=1.0)     # motto, augmented
    o.add('bsn', cod, 'G2:h C3:h Eb3:h D3:h D3:w', vel='mp', gate=1.0)
    o.add('cb', cod, 'Eb2:w Eb2:w Eb2:w Eb2:w', vel='p', gate=1.0)
    o.add('vln1', cod, 'Bb4:q. C5:e Eb5:q F5:q G5:h F5:q Eb5:q Eb5:w r:w', vel='mp', vel_end='p', gate=1.0)
    o.add('vln2', cod, '(G3 Bb3):w ' * 4, vel='p', gate=1.0)
    o.add('vla', cod, 'Eb4:w ' * 4, vel='p', gate=1.0)
    # darkening: Eb -> Ebm -> chromatic slip toward F minor (development)
    o.add('vln1', cod + 16, 'Gb4:w F4:w E4:w Eb4:h D4:h', vel='p', vel_end='pp', gate=1.0)
    o.add('vln2', cod + 16, 'Eb4:w Db4:w C4:w Bb3:w', vel='p', vel_end='pp', gate=1.0)
    o.add('vla', cod + 16, 'Bb3:w Ab3:w G3:w F3:w', vel='p', vel_end='pp', gate=1.0)
    o.add('vc', cod + 16, 'Eb3:w C3:w C3:w C3:h B2:h', vel='p', vel_end='pp', gate=1.0)
    o.add('cb', cod + 16, 'Eb2:w C2:w C2:w C2:h B1:h', vel='pp', gate=1.0)
    o.add('cl', cod + 24, 'G4:q C5:h Eb5:q D5:h C5:h', vel='pp', gate=1.0)   # motto whispers, almost resolves...
    o.add('timp', cod + 28, roll('C3', 4, 0.5), vel='ppp', vel_end='pp')

def dev(o, t):
    # ---- phase 1, bars 1-12 (pp, lost): motto wanders Fm / Db / Bbm
    o.add('cl', t, 'C4:q F4:h Ab4:q G4:w', vel='pp', gate=1.0)
    o.add('vc', t, 'F2:q r:q F2:q r:q ' * 2, vel='pp', gate=0.5)
    o.add('cb', t, 'F1:w F1:w', vel='pp', gate=1.0)
    o.add('bsn', t + 8, 'Ab2:q Db3:h F3:q Eb3:w', vel='pp', gate=1.0)
    o.add('vla', t + 8, trem(['Db4', 'F4'], 8, 0.5), vel='pp', gate=1.0)
    o.add('cb', t + 8, 'Db2:w Db2:w', vel='pp', gate=1.0)
    o.add('ob', t + 16, 'F4:q Bb4:h Db5:q C5:w', vel='p', gate=1.0)
    o.add('vc', t + 16, 'Bb2:q r:q F2:q r:q ' * 2, vel='pp', gate=0.5)
    o.add('hp', t + 16, 'Bb1:e F2:e Bb2:e Db3:e F3:e Db3:e Bb2:e F2:e ' * 2, vel='pp', gate=1.0)
    o.add('fl', t + 24, 'Db5:q Gb5:h Bb5:q Ab5:w', vel='p', gate=1.0)
    o.add('vln2', t + 24, trem(['Db4', 'Gb4'], 8, 0.5), vel='pp', gate=1.0)
    o.add('cb', t + 24, 'Gb2:w Gb2:w', vel='pp', gate=1.0)
    o.add('vln1', t + 32, 'F5:q Bb5:h Db6:q C6:h B5:h', vel='p', vel_end='mp', gate=1.0)
    o.add('vc', t + 32, 'Db3:w C3:h B2:h', vel='pp', vel_end='mp', gate=1.0)
    o.add('cb', t + 32, 'Db2:w C2:h B1:h', vel='pp', vel_end='mp', gate=1.0)
    o.add('vla', t + 40, 'C4:h D4:h', vel='mp', gate=1.0)
    o.add('bsn', t + 40, 'C3:h D3:h', vel='mp', gate=1.0)

    # ---- phase 2, bars 13-24: T1-head sequences climbing Fm -> Gm -> Ab -> Bb
    p2 = t + 48
    heads = [('F minor', -7, Fm), ('G minor', -5, Gm), ('A-flat', -4, Ab), ('B-flat', -2, Bb7)]
    vels = [('mp', 'mp'), ('mp', 'mf'), ('mf', 'f'), ('f', 'ff')]
    for i, (label, semi, h) in enumerate(heads):
        bt = p2 + i * 8
        v0, v1 = vels[i]
        head = transpose_events(parse(T1_HEAD), semi + 12)
        o.add('vln1', bt, head, vel=v0, vel_end=v1)
        o.add('vln2', bt, transpose_events(head, -12), vel=v0)
        if i >= 1:
            o.add('fl', bt + 4, head, vel=v1)
            o.add('ob', bt + 4, head, vel=v1)
        else:
            o.add('cl', bt + 4, head, vel=v1)
        o.add('cb', bt, [(h['bass'], 1.0)] * 8, vel=v0, vel_end=v1, gate=0.85)
        o.add('vc', bt, [(p, 0.5) for p in h['vc'] * 4], vel=v0, vel_end=v1, gate=0.8)
        o.add('vla', bt, [(None, 0.5), (h['pad'], 0.5)] * 8, vel=v0, gate=0.6)
        o.add('bsn', bt, [(h['bsn'], 2.0)] * 4, vel=v0, gate=0.95)
    # bars 21-24 overlap: fragmentation — 2-beat exchanges rising chromatically
    p2f = p2 + 32
    frag = 'Bb4:e Eb5:e Eb5:e Eb5:e'
    o.add('vln1', p2f, B(frag + ' ' + frag.replace('Bb4', 'B4').replace('Eb5', 'E5'), 1), vel='f')
    o.add('fl', p2f + 4, B(frag.replace('Bb4', 'C5').replace('Eb5', 'F5') + ' '
                           + frag.replace('Bb4', 'Db5').replace('Eb5', 'Gb5'), 1), vel='ff')
    o.add('vln1', p2f + 8, B(frag.replace('Bb4', 'D5').replace('Eb5', 'G5') + ' '
                             + frag.replace('Bb4', 'Eb5').replace('Eb5', 'Ab5'), 1), vel='ff')
    o.add('tpt', p2f + 12, B('F5:e Bb5:e Bb5:e Bb5:e Bb5:q Bb5:q', 1), vel='ff', gate=0.7)
    for i in range(4):
        bt = p2f + i * BAR
        o.add('vc', bt, trem('G2', 4, 0.5), vel='f', vel_end='ff', gate=0.9)
        o.add('cb', bt, 'G1:q G1:q G1:q G1:q', vel='f', gate=0.85)
        o.add('vla', bt, trem(['Db4', 'E4'], 4, 0.5), vel='f', gate=0.9)
    o.add('timp', p2f, roll('G2', 16, 0.25), vel='mf', vel_end='ff')

    # ---- phase 3, bars 25-36: brass stretto on the motto, ff
    p3 = t + 96
    stretto = 'G3:h C4:h Eb4:h D4:h D4:w'
    o.add('tbn', p3, B(stretto, 3), vel='ff', gate=1.0)
    o.add('hn', p3 + 2, B(stretto, 3), vel='ff', transpose=7, gate=1.0)
    o.add('tpt', p3 + 4, B(stretto, 3), vel='ff', transpose=12, gate=1.0)
    o.add('tbn', p3 + 16, B(stretto, 3), vel='ff', transpose=-5, gate=1.0)
    o.add('hn', p3 + 18, B(stretto, 3), vel='ff', transpose=2, gate=1.0)
    o.add('tpt', p3 + 20, B(stretto, 3), vel='ff', transpose=17, gate=1.0)
    churn = ['C3', 'Eb3', 'Gb3', 'A3']      # diminished churn
    for i in range(8):
        bt = p3 + i * BAR
        o.add('vc', bt, [(p, 0.5) for p in churn * 2], vel='f', gate=0.8)
        o.add('vln2', bt, [(p, 0.5) for p in ['C5', 'A4', 'Gb4', 'Eb4'] * 2], vel='f', gate=0.8)
        o.add('vla', bt, [(None, 0.5), (['Eb4', 'Gb4', 'A4'], 0.5)] * 4, vel='f', gate=0.6)
        o.add('cb', bt, 'C2:q C2:q Eb2:q Gb2:q' if i % 2 == 0 else 'A1:q A1:q C2:q Eb2:q', vel='f', gate=0.85)
    o.add('vln1', p3, R(B('C6:e B5:e C6:e Eb6:e D6:e C6:e B5:e D6:e', 1), 8), vel='f', vel_end='ff')
    # bars 33-36: collapse onto the dominant
    p3e = p3 + 32
    o.add('tbn', p3e, '(G2 D3 G3):w (G2 D3 G3):w (G2 B2 F3):w (G2 B2 F3):w', vel='ff', gate=1.0)
    o.add('hn', p3e, '(G3 B3 D4):w ' * 4, vel='f', gate=1.0)
    o.add('vc', p3e, trem('G2', 16, 0.5), vel='ff', gate=0.9)
    o.add('cb', p3e, 'G1:w ' * 4, vel='ff', gate=1.0)
    desc = B('G6:q F6:q E6:q Eb6:q D6:q Db6:q C6:q B5:q '
             'Bb5:q A5:q Ab5:q G5:q F#5:q G5:q Ab5:q B5:q', 4)
    o.add('vln1', p3e, desc, vel='ff', gate=0.9)
    o.add('fl', p3e, desc, vel='ff', gate=0.9)
    o.add('vln2', p3e, desc, vel='f', transpose=-12, gate=0.9)
    o.add('ob', p3e, desc, vel='f', transpose=-12, gate=0.9)

    # ---- phase 4, bars 37-44: dominant pedal, the dam about to break
    p4 = t + 144
    o.add('timp', p4, roll('G2', 32, 0.25), vel='mf', vel_end='ff')
    o.add('cb', p4, 'G1:w ' * 8, vel='f', vel_end='ff', gate=1.0)
    o.add('vc', p4, trem('G2', 32, 0.5), vel='f', vel_end='ff', gate=0.9)
    o.add('tbn', p4, '(G2 G3):w ' * 8, vel='f', vel_end='ff', gate=1.0)
    trill = ' '.join(['G5:s Ab5:s' for _ in range(8)])
    o.add('fl', p4, R(B(trill, 1), 4), vel='f', gate=0.9)
    o.add('ob', p4, R(B(trill, 1), 4), vel='f', gate=0.9)
    o.add('vln1', p4, R(B('G5:e D5:e B4:e D5:e G5:e D5:e B4:e D5:e', 1), 4), vel='f', gate=0.8)
    o.add('vln2', p4, R(B('D5:e B4:e G4:e B4:e D5:e B4:e G4:e B4:e', 1), 4), vel='f', gate=0.8)
    o.add('vla', p4, [(None, 0.5), (['G3', 'B3', 'F4'], 0.5)] * 16, vel='f', gate=0.6)
    # last 4 bars: unison surge up to the recapitulation
    surge = B('G2:h A2:h B2:h C3:h D3:h Eb3:h F3:q G3:q Ab3:q B3:q', 4)
    o.add('vc', p4 + 16, surge, vel='ff', gate=0.95)
    o.add('tbn', p4 + 16, surge, vel='ff', gate=0.95)
    o.add('bsn', p4 + 16, surge, vel='ff', gate=0.95, transpose=12)
    o.add('hn', p4 + 16, surge, vel='ff', gate=0.95, transpose=12)
    o.add('vln1', p4 + 16, R(B('G5:s Ab5:s G5:s Ab5:s', 0.25), 16), vel='ff', gate=0.9)
    o.add('fl', p4 + 16, R(B('G6:s Ab6:s G6:s Ab6:s', 0.25), 16), vel='ff', gate=0.9)
    o.perc(p4 + 28, [('susp', 0.25)] * 16, vel='p')

def recap(o, t):
    # ---- T1, tutti ff, compressed (12 bars: 8 theme + 4 cadence)
    o.perc(t, 'crash:q', vel='ff')
    prog = [Cm, Cm, G7, Cm, Eb, Eb, G7, Cm]
    pump(o, t, prog, vel='ff', pad_vel='f', with_hn=True)
    o.add('vln1', t, B(T1, 8), vel='ff', accent_first=True)
    o.add('vln2', t, B(T1, 8), vel='ff')
    o.add('fl', t, B(T1, 8), vel='ff', transpose=12)
    o.add('ob', t, B(T1, 8), vel='ff')
    o.add('cl', t, B(T1, 8), vel='f')
    o.add('tpt', t, 'C5:q r:q r:h r:w ' * 2 + '(C5 Eb5):q r:q (C5 Eb5):q r:q r:w r:w r:w', vel='ff', gate=0.5)
    o.add('timp', t, 'C3:q r:q r:h C3:q r:q r:h r:w r:w C3:q r:q r:h r:w G2:e G2:e G2:q r:h C3:q r:q r:h', vel='ff')
    cad = B('C6:q C6:e B5:e C6:q G5:q '
            'Ab5:q Ab5:e G5:e Ab5:q Eb5:q '
            'F5:q F5:e Eb5:e F5:q D5:q '
            'C5:q G4:q C5:q r:q', 4)
    pump(o, t + 32, [Cm, Ab, Dh, Cm], vel='ff', pad_vel='f', with_hn=True)
    o.add('vln1', t + 32, cad, vel='ff')
    o.add('fl', t + 32, cad, vel='ff')
    o.add('ob', t + 32, cad, vel='f')

    # ---- transition pivot to C major (8 bars): light dawns early
    tr = t + 48
    o.add('vln1', tr, B(T1_HEAD), vel='f')
    o.add('cl', tr + 4, B(T1_HEAD), vel='mf', transpose=5)        # F
    o.add('ob', tr + 8, B(T1_HEAD.replace('Eb5', 'E5'), 1), vel='mf', transpose=2)  # major color
    o.add('cb', tr, 'C2:q C2:q G2:q C2:q F2:q F2:q C3:q F2:q', vel='mf', gate=0.85)
    o.add('vc', tr, [(p, 0.5) for p in Cm['vc'] * 2] + [(p, 0.5) for p in FM['vc'] * 2], vel='mf', gate=0.8)
    o.add('vc', tr + 8, 'G2:h G2:h G2:h B2:h', vel='mp', gate=0.95)
    o.add('cb', tr + 8, 'G1:w G1:w', vel='mp', gate=1.0)
    o.add('vla', tr + 8, trem(['G3', 'B3', 'D4'], 8, 0.5), vel='mp', vel_end='p', gate=0.9)
    o.add('hp', tr + 24, 'G2:s B2:s D3:s G3:s B3:s D4:s G4:s B4:s D5:s G5:s B5:s D6:s G6:s B6:s D7:s G7:s', vel='mf', gate=1.0)
    o.add('fl', tr + 16, 'D6:q G5:h. E6:q G5:h.', vel='p', gate=1.0)
    o.add('vln2', tr + 16, 'B4:w C5:w', vel='p', gate=1.0)

    # ---- T2 in C MAJOR (16 bars): the foreshadowing of the Answer
    t2 = tr + 32
    T2C = transpose_events(parse(T2), 2)
    t2c_bass = ['C2', 'C2', 'F2', 'G2', 'C2', 'D2', 'G2', 'C2']
    t2c_pads = [['G3', 'C4', 'E4'], ['G3', 'C4', 'E4'], ['A3', 'C4', 'F4'],
                ['G3', 'B3', 'D4'], ['G3', 'C4', 'E4'], ['A3', 'D4', 'F4'],
                ['G3', 'B3', 'F4'], ['G3', 'C4', 'E4']]
    # first statement: winds, gentle
    o.add('ob', t2, T2C, vel='mp', gate=1.0)
    o.add('fl', t2 + 16, transpose_events(parse(' '.join(T2.split()[14:])), 2), vel='mp', gate=1.0)
    for i in range(8):
        bt = t2 + i * BAR
        o.add('cb', bt, f'{t2c_bass[i]}:q r:q {t2c_bass[i]}:q r:q', vel='p', gate=0.6)
        o.add('vc', bt, [(t2c_bass[i], 1.0), (None, 1.0), (t2c_bass[i], 1.0), (None, 1.0)], vel='p', gate=0.6, transpose=12)
        o.add('vla', bt, [(None, 1.0), (t2c_pads[i], 1.0), (None, 1.0), (t2c_pads[i], 1.0)], vel='p', gate=0.6)
    # second statement: strings sing it, fuller
    t2s = t2 + 32
    o.add('vln1', t2s, T2C, vel='mf', vel_end='f', gate=1.0)
    o.add('vln2', t2s, transpose_events(T2C, -12), vel='mf', gate=1.0)
    o.add('fl', t2s, T2C, vel='mf', gate=1.0)
    vc_line = B('C3:h G3:q A3:q G3:h E3:q C3:q F3:h. C3:q G3:h G2:h '
                'C3:h D3:q E3:q F3:h D3:h G3:q G2:q B2:q G2:q C3:w', 8)
    o.add('vc', t2s, vc_line, vel='mf', gate=1.0)
    for i in range(8):
        bt = t2s + i * BAR
        o.add('cb', bt, f'{t2c_bass[i]}:h {t2c_bass[i]}:h', vel='mp', gate=0.95)
        o.add('vla', bt, [(t2c_pads[i], 4.0)], vel='mp', gate=1.0)
        o.add('hn', bt, [([p for p in t2c_pads[i]], 4.0)], vel='p', gate=1.0)
    o.add('hp', t2s, 'C3:e G3:e E4:e G4:e C5:e G4:e E4:e G3:e ' * 2, vel='mp', gate=1.0)

    # ---- darkening (12 bars): the light withdraws; C -> Am -> Fm -> Cm
    dk = t2 + 64
    o.add('vln1', dk, 'E5:w D5:h C5:h C5:w B4:h C5:h', vel='mf', vel_end='mp', gate=1.0)
    o.add('vln2', dk, 'C5:w A4:w A4:w G4:w', vel='mp', gate=1.0)
    o.add('vla', dk, 'G4:w E4:w F4:w E4:w', vel='mp', gate=1.0)
    o.add('vc', dk, 'C3:w C3:w A2:w A2:w', vel='mp', gate=1.0)
    o.add('cb', dk, 'C2:w C2:w A1:w A1:w', vel='mp', gate=1.0)
    o.add('ob', dk + 8, 'E5:q C5:h A4:q A4:w', vel='mp', gate=1.0)
    # Fm shadow: Ab appears — the borrowed darkness
    o.add('vln1', dk + 16, 'C5:w C5:h Ab4:h', vel='mp', vel_end='p', gate=1.0)
    o.add('vln2', dk + 16, 'Ab4:w F4:w', vel='p', gate=1.0)
    o.add('vla', dk + 16, 'F4:w C4:w', vel='p', gate=1.0)
    o.add('vc', dk + 16, 'F2:w F2:w', vel='p', gate=1.0)
    o.add('cb', dk + 16, 'F1:w F1:w', vel='p', gate=1.0)
    o.add('cl', dk + 16, 'Ab4:q F4:h C4:q C4:w', vel='p', gate=1.0)
    # the motto rises from the bass, crescendo — storm returning
    o.add('vc', dk + 24, 'G2:q C3:h Eb3:q D3:w', vel='mp', vel_end='f', gate=1.0)
    o.add('bsn', dk + 24, 'G2:q C3:h Eb3:q D3:w', vel='mp', vel_end='f', gate=1.0)
    o.add('cb', dk + 24, 'C2:w G1:w', vel='mp', vel_end='f', gate=1.0)
    o.add('vla', dk + 24, trem(['C4', 'Eb4'], 8, 0.5), vel='p', vel_end='f', gate=0.9)
    o.add('vln2', dk + 24, trem('G4', 8, 0.5), vel='p', vel_end='f', gate=0.9)
    o.add('timp', dk + 32, roll('G2', 16, 0.25), vel='p', vel_end='ff')
    o.add('vln1', dk + 32, B('G5:q F5:q Eb5:q D5:q Eb5:q D5:q C5:q B4:q '
                             'C5:e D5:e Eb5:e F5:e G5:e Ab5:e B5:e C6:e D6:q B5:q G5:q B5:q', 4),
          vel='mf', vel_end='ff', gate=0.9)
    o.add('vc', dk + 32, 'G2:w G2:w G2:h G2:h G2:q G2:q G2:q G2:q', vel='f', gate=0.9)
    o.add('tbn', dk + 40, '(G2 B2 F3):h (G2 B2 F3):h', vel='f', vel_end='ff', gate=0.95)
    o.add('hn', dk + 40, '(B3 D4 F4):h (B3 D4 F4):h', vel='f', vel_end='ff', gate=0.95)

def coda(o, t):
    o.tempo(t, 152, 'Piu mosso')
    o.perc(t, 'crash:q', vel='ff')
    # bars 1-4: T1 head hammered over Cm | Ab | Fm | G
    prog = [Cm, Ab, Fm, GM]
    pump(o, t, prog, vel='ff', pad_vel='f', with_hn=True)
    o.add('vln1', t, B(T1_HEAD) + ' ' + B(T1_HEAD, 1), vel='ff')
    o.add('vln2', t, B(T1_HEAD) + ' ' + B(T1_HEAD, 1), vel='ff', transpose=-12)
    o.add('fl', t + 8, B(T1_HEAD), vel='ff', transpose=12)
    o.add('ob', t + 8, B(T1_HEAD), vel='ff')
    o.add('vln1', t + 8, B(T1_HEAD) + ' ' + B(T1_HEAD, 1), vel='ff')
    o.add('tpt', t + 12, 'G4:e C5:e C5:e C5:e D5:q B4:q', vel='ff', gate=0.6)

    # bars 5-8: rising fury — sequence the head up by step
    o.add('vln1', t + 16, transpose_events(parse(T1_HEAD), 1), vel='ff')       # Db
    o.add('fl', t + 16, transpose_events(parse(T1_HEAD), 13), vel='ff')
    o.add('vln1', t + 20, transpose_events(parse(T1_HEAD), 3), vel='ff')       # Eb
    o.add('fl', t + 20, transpose_events(parse(T1_HEAD), 15), vel='ff')
    o.add('vln1', t + 24, transpose_events(parse(T1_HEAD), 5), vel='ff')       # F
    o.add('fl', t + 24, transpose_events(parse(T1_HEAD), 17), vel='ff')
    o.add('vln1', t + 28, B('G5:e G5:e Ab5:e Ab5:e B5:e B5:e D6:e D6:e', 1), vel='ff')
    o.add('fl', t + 28, B('G6:e G6:e Ab6:e Ab6:e B6:e B6:e B6:e B6:e', 1), vel='ff')
    for i, h in enumerate([Db, Eb, Fm, G7]):
        bt = t + 16 + i * BAR
        o.add('cb', bt, [(h['bass'], 1.0)] * 4, vel='ff', gate=0.85)
        o.add('vc', bt, [(p, 0.5) for p in h['vc'] * 2], vel='ff', gate=0.8)
        o.add('vla', bt, [(None, 0.5), (h['pad'], 0.5)] * 4, vel='f', gate=0.6)
        o.add('bsn', bt, [(h['bsn'], 2.0)] * 2, vel='f', gate=0.95)
        o.add('tbn', bt, [(h['bsn'], 4.0)], vel='f', gate=1.0)
    o.add('timp', t + 16, roll('G2', 16, 0.25), vel='f', vel_end='ff')
    o.perc(t + 24, 'crash:h crash:h', vel='ff')

    # bars 9-11: THE MOTTO, unison, the whole orchestra in octaves
    m = t + 32
    motto = B('G4:h C5:h Eb5:h D5:h D5:w', 3)
    o.add('vln1', m, motto, vel='fff', transpose=12, gate=1.0)
    o.add('vln2', m, motto, vel='fff', gate=1.0)
    o.add('vla', m, motto, vel='fff', transpose=-12, gate=1.0)
    o.add('vc', m, motto, vel='fff', transpose=-24, gate=1.0)
    o.add('cb', m, motto, vel='fff', transpose=-24, gate=1.0)
    o.add('fl', m, motto, vel='fff', transpose=12, gate=1.0)
    o.add('ob', m, motto, vel='fff', transpose=12, gate=1.0)
    o.add('cl', m, motto, vel='fff', gate=1.0)
    o.add('bsn', m, motto, vel='fff', transpose=-24, gate=1.0)
    o.add('hn', m, motto, vel='fff', transpose=-12, gate=1.0)
    o.add('tpt', m, motto, vel='fff', gate=1.0)
    o.add('tbn', m, motto, vel='fff', transpose=-12, gate=1.0)
    o.add('timp', m, roll('G2', 4, 0.25) + roll('C3', 4, 0.25) + [('Eb3', 2.0), ('D3', 2.0)], vel='ff')
    o.add('timp', m + 8, roll('D3', 4, 0.5), vel='ff', vel_end='fff')
    o.perc(m, 'crash:w r:w r:w', vel='ff')

    # bars 12-14: no resolution — hammered G-C-D, then bare open fifth
    e = t + 44
    o.add('tpt', e, '(G4 C5 D5):q r:q (G4 C5 D5):q r:q', vel='fff', gate=0.4)
    o.add('hn', e, '(D4 G4 C5):q r:q (D4 G4 C5):q r:q', vel='fff', gate=0.4)
    o.add('tbn', e, '(G2 G3 D4):q r:q (G2 G3 D4):q r:q', vel='fff', gate=0.4)
    o.add('vln1', e, '(G5 D6):q r:q (G5 D6):q r:q', vel='fff', gate=0.4)
    o.add('vln2', e, '(G4 D5):q r:q (G4 D5):q r:q', vel='fff', gate=0.4)
    o.add('vla', e, '(G3 D4):q r:q (G3 D4):q r:q', vel='fff', gate=0.4)
    o.add('vc', e, 'G2:q r:q G2:q r:q', vel='fff', gate=0.4)
    o.add('cb', e, 'G1:q r:q G1:q r:q', vel='fff', gate=0.4)
    o.add('timp', e, 'G2:q r:q G2:q r:q', vel='fff')
    # final: open C-G — C-rooted, but the melodic D never fell home
    o.add('vln1', e + 4, '(G4 G5):w (G4 G5):h.', vel='fff', gate=1.0)
    o.add('vln2', e + 4, '(C4 G4):w (C4 G4):h.', vel='fff', gate=1.0)
    o.add('vla', e + 4, '(C3 G3):w (C3 G3):h.', vel='fff', gate=1.0)
    o.add('vc', e + 4, '(C2 G2):w (C2 G2):h.', vel='fff', gate=1.0)
    o.add('cb', e + 4, 'C2:w C2:h.', vel='fff', gate=1.0)
    o.add('tpt', e + 4, '(G4 C5):w (G4 C5):h.', vel='fff', gate=1.0)
    o.add('hn', e + 4, '(C4 G4):w (C4 G4):h.', vel='fff', gate=1.0)
    o.add('tbn', e + 4, '(C2 G2 C3):w (C2 G2 C3):h.', vel='fff', gate=1.0)
    o.add('bsn', e + 4, '(C2 C3):w (C2 C3):h.', vel='fff', gate=1.0)
    o.add('timp', e + 4, roll('C3', 7, 0.25), vel='fff')
    o.perc(e + 4, 'crash:q', vel='fff')
    o.perc(e + 4, 'bd:q r:h. bd:q r:h r:q', vel='ff')

# ================================================================ build

def compose(o: Orchestra, t0: float = 0.0) -> float:
    intro(o, t0)
    expo(o, t0 + 64)
    dev(o, t0 + 288)
    recap(o, t0 + 464)
    coda(o, t0 + 656)
    return t0 + 712

if __name__ == '__main__':
    o = Orchestra()
    end = compose(o, 0.0)
    os.makedirs('output', exist_ok=True)
    path = write_midi(o, 'output/mvt1.mid')
    print(midi_report(path))
    probs = check_ranges(o)
    print('range problems:', probs if probs else 'none')
    print('end offset:', end, 'ql; orchestra end:', o.end())
