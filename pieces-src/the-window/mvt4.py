"""Movement IV — Through.

C minor -> C major. The ending faced and passed through. Storm; a striving
march that collapses twice; the chorale breakthrough — the ANSWER
(G-C-E-D-C), the motto granted its final note at last; an apotheosis
combining the first movement's theme in major with the Answer; and a coda
in which the music dissolves back into the fragments it came from.
The window closes. The last sound is a single high C.

Layout (ql from t0, 4 ql per bar):
    0- 80  storm (20 bars, q=138)
   80-368  striving march, two collapses, the gathering (72 bars)
  368-456  chorale: the Answer (22 bars, q=84)
  456-616  apotheosis (40 bars, q=144)
  616-672  coda: lento lucente (14 bars, q=48)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import (Orchestra, write_midi, midi_report, check_ranges,
                            total_ql, transpose_events, parse, trem, roll)

BAR = 4.0

def B(dsl, n=1):
    got = total_ql(dsl)
    assert abs(got - 4.0 * n) < 1e-6, f'bad bar sum {got} != {4*n}: {dsl[:60]}'
    return dsl

def R(dsl, times):
    return ' '.join([dsl] * times)

# the striving march — rises in steps, falls back, rises again
MARCH = (
    'C4:q. D4:e Eb4:q F4:q '
    'G4:h F4:q Eb4:q '
    'D4:q. Eb4:e F4:q G4:q '
    'Ab4:h G4:q F4:q '
    'Eb4:q. F4:e G4:q Ab4:q '
    'Bb4:h Ab4:q G4:q '
    'F4:q D4:q Eb4:q B3:q '
    'C4:h. r:q'
)

# Movement I's theme 1, transformed to C MAJOR for the apotheosis
T1_MAJOR = (
    'G4:e C5:e C5:e C5:e E5:e D5:e C5:e D5:e '
    'E5:e F5:e G5:h. '
    'F5:e E5:e D5:e C5:e B4:e C5:e D5:e B4:e '
    'C5:q G4:q E4:q G4:q '
    'C5:e F5:e F5:e F5:e A5:e G5:e F5:e G5:e '
    'A5:e B5:e C6:h. '
    'A5:e G5:e F5:e E5:e D5:e C5:e B4:e D5:e '
    'C5:q E5:q G5:q C6:q'
)

# THE ANSWER, melodic line for the chorale (two 3-bar phrases + echoes)
ANSWER_A = 'G4:h C5:h E5:h D5:h C5:w C5:w'
ANSWER_B = 'C5:h D5:h E5:h G5:h C6:w C6:w'

def storm(o, t):
    o.timesig(t, '4/4')
    o.tempo(t, 138, 'Allegro agitato')

    # bars 1-8: the old darkness, but churning — motto fragments in canon
    o.add('vln2', t, trem(['G4', 'C5'], 16, 0.5), vel='mf', vel_end='f', gate=0.9)
    o.add('vla', t, trem(['Eb4', 'G4'], 16, 0.5), vel='mf', vel_end='f', gate=0.9)
    o.add('cb', t, 'C2:h C2:h C2:h B1:h C2:h C2:h Ab1:h G1:h', vel='f', gate=0.9)
    o.add('vc', t, 'G2:q C3:q. r:e Eb3:q D3:5 r:h. G2:q C3:h.', vel='f', gate=0.95)
    o.add('tbn', t + 2, 'G2:q C3:h. r:w r:q Eb3:q D3:h r:w', vel='f', gate=0.95)
    o.add('ob', t + 4, 'Eb5:q D5:h. r:w Eb5:q D5:q Eb5:q D5:q r:w', vel='f', gate=0.9)
    o.add('hn', t + 8, 'G3:q C4:q Eb4:q D4:q D4:w', vel='f', gate=0.95)
    o.add('timp', t, roll('C3', 8, 0.5), vel='mp', vel_end='f')
    o.add('vln1', t + 8, B('G5:e C6:e B5:e C6:e Eb6:e D6:e C6:e D6:e', 1) + ' '
                         + B('Eb6:e D6:e C6:e B5:e C6:e D6:e B5:e G5:e', 1), vel='f', gate=0.85)
    # bars 9-16: chromatic descent — the ground giving way
    s = t + 32
    desc = B('C6:q B5:q Bb5:q A5:q Ab5:q G5:q Gb5:q F5:q '
             'E5:q Eb5:q D5:q Db5:q C5:q B4:q C5:q D5:q', 4)
    o.add('vln1', s, desc, vel='ff', gate=0.9)
    o.add('fl', s, desc, vel='f', gate=0.9)
    o.add('vln2', s, trem(['F4', 'Ab4'], 8, 0.5) + trem(['E4', 'G4'], 8, 0.5), vel='f', gate=0.9)
    o.add('vla', s, trem(['B3', 'D4'], 8, 0.5) + trem(['Bb3', 'Db4'], 8, 0.5), vel='f', gate=0.9)
    o.add('vc', s, 'Ab2:h G2:h Gb2:h F2:h E2:h Eb2:h D2:h G2:h', vel='ff', gate=0.9)
    o.add('cb', s, 'Ab1:h G1:h Gb1:h F1:h E1:h Eb2:h D2:h G1:h', vel='ff', gate=0.9)
    o.add('bsn', s, 'Ab2:h G2:h Gb2:h F2:h E2:h Eb2:h D2:h G2:h', vel='f', gate=0.9)
    o.add('tpt', s + 8, 'G4:q C5:q Eb5:q D5:q D5:h. r:q', vel='ff', gate=0.9)
    o.add('tbn', s + 8, 'G2:q C3:q Eb3:q D3:q D3:h. r:q', vel='ff', gate=0.9)
    # bars 17-20: hammering half-cadence — the cliff edge
    c = t + 64
    o.add('vln1', c, '(D5 G5):e r:e (D5 G5):e r:e (D5 G5):e r:e (D5 G5):e r:e ' * 2, vel='ff', gate=0.5)
    o.add('vln2', c, '(B4 D5):e r:e (B4 D5):e r:e (B4 D5):e r:e (B4 D5):e r:e ' * 2, vel='ff', gate=0.5)
    o.add('vla', c, '(G3 F4):e r:e (G3 F4):e r:e (G3 F4):e r:e (G3 F4):e r:e ' * 2, vel='ff', gate=0.5)
    o.add('vc', c, 'G2:e r:e G2:e r:e G2:e r:e G2:e r:e ' * 2, vel='ff', gate=0.5)
    o.add('cb', c, 'G1:e r:e G1:e r:e G1:e r:e G1:e r:e ' * 2, vel='ff', gate=0.5)
    o.add('tbn', c + 8, '(G2 B2 F3):w (G2 B2 F3):h r:h', vel='ff', gate=0.95)
    o.add('hn', c + 8, '(B3 D4 F4):w (B3 D4 F4):h r:h', vel='ff', gate=0.95)
    o.add('timp', c + 8, roll('G2', 6, 0.25) + [(None, 2.0)], vel='f', vel_end='ff')
    o.perc(c + 8, 'crash:q', vel='ff')

def striving(o, t):
    # unit 1 (bars 1-8): the march, low and quiet — out of the wreckage
    o.add('vc', t, B(MARCH, 8), vel='mp', gate=0.9, transpose=-12)
    o.add('bsn', t, B(MARCH, 8), vel='mp', gate=0.9, transpose=-12)
    o.add('cb', t, 'C2:q r:q G1:q r:q ' * 7 + 'C2:q r:q C2:q r:q', vel='p', gate=0.5)
    o.add('timp', t, 'C3:q r:h. ' * 4 + 'G2:q r:h. ' * 3 + 'C3:q r:q C3:q r:q', vel='p')

    # unit 2 (9-16): violas join with a counter-melody; clarinets color
    u2 = t + 32
    o.add('vc', u2, B(MARCH, 8), vel='mf', gate=0.9, transpose=-12)
    o.add('bsn', u2, B(MARCH, 8), vel='mf', gate=0.9, transpose=-12)
    counter = B('G4:h Eb4:q F4:q G4:q Ab4:q G4:h '
                'F4:h D4:q Eb4:q F4:q G4:q F4:h '
                'G4:h Ab4:q Bb4:q C5:q Bb4:q Ab4:h '
                'G4:q F4:q G4:q D4:q Eb4:h. r:q', 8)
    o.add('vla', u2, counter, vel='mf', gate=0.95)
    o.add('cl', u2, B(MARCH, 8), vel='mp', gate=0.9)
    o.add('cb', u2, 'C2:q r:q G1:q r:q ' * 7 + 'C2:q r:q C2:q r:q', vel='mp', gate=0.5)
    o.add('timp', u2, 'C3:q r:h. ' * 4 + 'G2:q r:h. ' * 3 + 'C3:q r:q C3:q r:q', vel='mp')

    # unit 3 (17-24): violins lift the march an octave; horns punch
    u3 = t + 64
    o.add('vln1', u3, B(MARCH, 8), vel='f', gate=0.9, transpose=12)
    o.add('vln2', u3, B(MARCH, 8), vel='f', gate=0.9)
    o.add('vla', u3, counter, vel='f', gate=0.95)
    o.add('vc', u3, B(MARCH, 8), vel='f', gate=0.9, transpose=-12)
    o.add('ob', u3, B(MARCH, 8), vel='mf', gate=0.9, transpose=12)
    o.add('cb', u3, 'C2:q C2:q G1:q G1:q ' * 7 + 'C2:q C2:q G2:q G2:q', vel='mf', gate=0.7)
    o.add('hn', u3 + 4, '(C4 Eb4):q r:q (C4 Eb4):q r:q r:w ' * 2, vel='f', gate=0.5)
    o.add('hn', u3 + 20, '(D4 F4):q r:q (D4 F4):q r:q r:w (Eb4 G4):q r:q (Eb4 G4):q r:q r:w', vel='f', gate=0.5)
    o.add('timp', u3, 'C3:q r:q C3:q r:q ' * 8, vel='mf')

    # unit 4 (25-32): COLLAPSE #1 — diminished crash, scattering; regroup in Eb
    u4 = t + 96
    o.add('vln1', u4, '(B4 D5 Ab5):q r:q (B4 D5 Ab5):q r:q (B4 D5 Ab5):e r:e r:h.', vel='ff', gate=0.4)
    o.add('vln2', u4, '(Ab4 B4 D5):q r:q (Ab4 B4 D5):q r:q (Ab4 B4 D5):e r:e r:h.', vel='ff', gate=0.4)
    o.add('vla', u4, '(D4 F4 Ab4):q r:q (D4 F4 Ab4):q r:q (D4 F4 Ab4):e r:e r:h.', vel='ff', gate=0.4)
    o.add('vc', u4, 'B2:q r:q B2:q r:q B2:e r:e r:h.', vel='ff', gate=0.4)
    o.add('cb', u4, 'B1:q r:q B1:q r:q B1:e r:e r:h.', vel='ff', gate=0.4)
    o.add('tbn', u4, '(B2 Ab3 D4):q r:q (B2 Ab3 D4):q r:q (B2 Ab3 D4):e r:e r:h.', vel='ff', gate=0.4)
    o.add('timp', u4, 'B2:q r:q B2:q r:q B2:e r:e r:h.', vel='ff')
    o.perc(u4, 'crash:q r:h.', vel='ff')
    # fragments scatter, pp — the march limps in E-flat
    o.add('fl', u4 + 9, 'Ab5:e G5:e F5:e Eb5:e D5:q r:q', vel='p', gate=0.6)
    o.add('cl', u4 + 13, 'F5:e Eb5:e D5:e C5:e B4:q r:q', vel='p', gate=0.6)
    o.add('vc', u4 + 16, transpose_events(parse(' '.join(MARCH.split()[:7])), -9), vel='mp', gate=0.9)
    o.add('vc', u4 + 24, transpose_events(parse(' '.join(MARCH.split()[7:14])), -9), vel='mp', gate=0.9)
    o.add('cb', u4 + 16, 'Eb2:q r:q Bb1:q r:q ' * 4, vel='p', gate=0.5)

    # units 5-6 (33-48): rebuild — sequence the march upward, Eb -> F minor -> G
    u5 = t + 128
    o.add('vc', u5, B(MARCH, 8), vel='mf', gate=0.9, transpose=3)
    o.add('bsn', u5, B(MARCH, 8), vel='mf', gate=0.9, transpose=3)
    o.add('vla', u5, counter, vel='mf', gate=0.95, transpose=3)
    o.add('cb', u5, 'Eb2:q r:q Bb1:q r:q ' * 7 + 'Eb2:q r:q Eb2:q r:q', vel='mp', gate=0.5)
    u6 = t + 160
    o.add('vln1', u6, B(MARCH, 8), vel='f', vel_end='ff', gate=0.9, transpose=17)
    o.add('vln2', u6, B(MARCH, 8), vel='f', gate=0.9, transpose=5)
    o.add('vc', u6, B(MARCH, 8), vel='f', gate=0.9, transpose=-7)
    o.add('ob', u6, B(MARCH, 8), vel='f', gate=0.9, transpose=5)
    o.add('fl', u6, B(MARCH, 8), vel='f', gate=0.9, transpose=17)
    o.add('cb', u6, 'F2:q C2:q F2:q C2:q ' * 8, vel='f', gate=0.7)
    o.add('hn', u6 + 16, '(C4 F4):q r:q (C4 F4):q r:q r:w ' * 2, vel='f', gate=0.5)
    o.add('timp', u6 + 24, roll('C3', 8, 0.5), vel='mf', vel_end='f')

    # unit 7 (49-56): COLLAPSE #2 — the big one; B-natural chaos, then silence
    u7 = t + 192
    o.add('vln1', u7, R('(F5 B5):e r:e', 4) + ' ' + R('(E5 Bb5):e r:e', 4) + ' '
                      + R('(Eb5 A5):e r:e', 4) + ' (D5 Ab5):q r:q (D5 Ab5):q r:q', vel='ff', gate=0.4)
    o.add('vln2', u7, R('(B4 F5):e r:e', 4) + ' ' + R('(Bb4 E5):e r:e', 4) + ' '
                      + R('(A4 Eb5):e r:e', 4) + ' (Ab4 D5):q r:q (Ab4 D5):q r:q', vel='ff', gate=0.4)
    o.add('vla', u7, trem(['B3', 'F4'], 4, 0.5) + trem(['Bb3', 'E4'], 4, 0.5)
                     + trem(['A3', 'Eb4'], 4, 0.5) + trem(['Ab3', 'D4'], 4, 0.5), vel='ff', gate=0.9)
    o.add('vc', u7, 'B2:w Bb2:w A2:w Ab2:w', vel='ff', gate=0.9)
    o.add('cb', u7, 'B1:w Bb1:w A1:w Ab1:w', vel='ff', gate=0.9)
    o.add('tbn', u7, '(B2 F3):w (Bb2 E3):w (A2 Eb3):w (Ab2 D3):w', vel='ff', gate=0.9)
    o.add('tpt', u7, 'B4:q r:q B4:q r:q Bb4:q r:q Bb4:q r:q A4:q r:q A4:q r:q Ab4:q Ab4:q Ab4:q Ab4:q',
          vel='ff', gate=0.5)
    o.add('timp', u7 + 12, roll('G2', 4, 0.25), vel='ff', vel_end='fff')
    o.perc(u7, 'crash:q r:h. r:w r:w tamtam:w', vel='ff')
    # ...and the wreckage settles onto a bare G — almost nothing left
    o.add('vc', u7 + 16, 'G2:w G2:w G2:w G2:w', vel='p', vel_end='pp', gate=1.0)
    o.add('cb', u7 + 16, 'G1:w G1:w G1:w G1:w', vel='p', vel_end='pp', gate=1.0)
    o.add('timp', u7 + 16, roll('G2', 16, 1.0), vel='pp')

    # units 8-9 (57-72): the gathering — fragments return, but E-natural
    # creeps in among them: the major third arriving from far away
    u8 = t + 256
    o.add('vc', u8, 'G2:q C3:h. r:w', vel='pp', gate=1.0)
    o.add('ob', u8 + 8, 'Eb5:q D5:h. r:w', vel='pp', gate=1.0)
    o.add('cl', u8 + 16, 'E4:q D4:h. r:w', vel='p', gate=1.0)          # E natural!
    o.add('fl', u8 + 24, 'G5:q C6:q E6:q D6:q D6:w', vel='p', vel_end='mp', gate=1.0)
    o.add('vln2', u8, trem('G3', 32, 0.5), vel='pp', vel_end='mp', gate=0.9)
    o.add('cb', u8, 'G1:w ' * 8, vel='pp', vel_end='mp', gate=1.0)
    o.add('hp', u8 + 12, 'G2:e B2:e D3:e G3:e B3:e D4:e G4:e B4:e r:w', vel='pp', gate=1.0)
    u9 = t + 288
    o.add('vln1', u9, B('G4:h B4:h C5:h D5:h E5:h F5:h G5:h A5:h '
                        'B5:h C6:h D6:q C6:q B5:q A5:q G5:h G5:h G5:w', 8),
          vel='mp', vel_end='ff', gate=0.95)
    o.add('vln2', u9, B('G3:w G3:w B3:w C4:w D4:w E4:w F4:h D4:h G4:w', 8), vel='mp', vel_end='f', gate=0.95)
    o.add('vla', u9, B('D4:w E4:w G4:w A4:w B4:w C5:w B4:h B4:h B4:w', 8), vel='mp', vel_end='f', gate=0.95)
    o.add('vc', u9, B('G2:w G2:w G2:w G2:w G2:w G2:w G2:h G2:h G2:w', 8), vel='mp', vel_end='f', gate=0.95)
    o.add('cb', u9, 'G1:w ' * 8, vel='mp', vel_end='f', gate=1.0)
    o.add('bsn', u9 + 16, 'G2:w A2:w B2:h D3:h G2:w', vel='mf', vel_end='f', gate=0.95)
    o.add('hn', u9 + 16, '(B3 D4):w (C4 E4):w (B3 F4):h (B3 F4):h (B3 D4):w', vel='mf', vel_end='f', gate=1.0)
    o.add('cl', u9 + 16, 'D5:h E5:h F5:h E5:q D5:q E5:h D5:h D5:w', vel='mf', gate=0.95)
    o.add('fl', u9 + 24, 'B5:q C6:q D6:q C6:q B5:h B5:h', vel='f', gate=0.95)
    o.add('timp', u9 + 24, roll('G2', 8, 0.25), vel='mf', vel_end='ff')
    o.perc(u9 + 28, [('susp', 0.25)] * 16, vel='p')

def chorale(o, t):
    o.tempo(t, 84, 'Maestoso luminoso')
    # THE ANSWER — first statement: brass choir alone, like dawn hitting
    o.perc(t, 'crash:q', vel='f')
    o.add('tpt', t, B(ANSWER_A, 4), vel='f', gate=1.0)
    o.add('hn', t, B('D4:h E4:h G4:h G4:h G4:h E4:h E4:w', 4), vel='f', gate=1.0)
    o.add('tbn', t, B('(G2 B3):h (C3 G3):h (C3 A3):h (B2 G3):h (C3 G3):w (C3 E3):w', 4), vel='f', gate=1.0)
    o.add('timp', t, 'G2:q r:h. C3:q r:h. r:w C3:q r:h.', vel='f')
    # strings answer with a rising arpeggio wash
    o.add('vln1', t + 12, 'r:h C5:e E5:e G5:e C6:e', vel='mf', gate=0.9)
    o.add('hp', t + 12, 'C3:e G3:e C4:e E4:e G4:e C5:e E5:e G5:e', vel='mf', gate=1.0)
    # second statement: full orchestra, strings carry the melody in octaves
    s = t + 16
    o.add('vln1', s, B(ANSWER_A, 4), vel='ff', transpose=12, gate=1.0)
    o.add('vln2', s, B(ANSWER_A, 4), vel='ff', gate=1.0)
    o.add('fl', s, B(ANSWER_A, 4), vel='f', transpose=12, gate=1.0)
    o.add('ob', s, B(ANSWER_A, 4), vel='f', gate=1.0)
    o.add('tpt', s, B(ANSWER_A, 4), vel='f', gate=1.0)
    o.add('vla', s, B('D4:h E4:h G4:h G4:h G4:h E4:h E4:w', 4), vel='f', gate=1.0)
    o.add('cl', s, B('D4:h E4:h G4:h G4:h G4:h E4:h E4:w', 4), vel='f', gate=1.0)
    o.add('vc', s, 'G2:h C3:h A2:h B2:h C3:w F2:h G2:h', vel='f', gate=1.0)
    o.add('cb', s, 'G1:h C2:h A1:h B1:h C2:w F1:h G1:h', vel='f', gate=1.0)
    o.add('tbn', s, B('(G2 B3):h (C3 G3):h (A2 A3):h (B2 G3):h (C3 G3):w (F2 F3):h (G2 F3):h', 4),
          vel='f', gate=1.0)
    o.add('bsn', s, 'G2:h C3:h A2:h B2:h C3:w F2:h G2:h', vel='f', gate=1.0)
    o.add('hn', s, B('D4:h E4:h E4:h D4:h E4:w F4:h D4:h', 4), vel='f', gate=1.0)
    o.add('timp', s, 'G2:q r:h. C3:q r:h. C3:q r:h. G2:h G2:h', vel='f')
    o.add('hp', s + 8, 'C3:e E3:e G3:e C4:e E4:e G4:e C5:e E5:e ' * 2, vel='mf', gate=1.0)
    # phrase B: higher, wider — and the bVI glow remembering the slow movement
    p = s + 16
    o.add('vln1', p, B(ANSWER_B, 4), vel='ff', transpose=12, gate=1.0)
    o.add('vln2', p, B(ANSWER_B, 4), vel='ff', gate=1.0)
    o.add('fl', p, B(ANSWER_B, 4), vel='ff', transpose=12, gate=1.0)
    o.add('ob', p, B(ANSWER_B, 4), vel='f', gate=1.0)
    o.add('tpt', p, B(ANSWER_B, 4), vel='ff', gate=1.0)
    o.add('vla', p, B('E4:h F4:h G4:h E4:h G4:w E4:w', 4), vel='f', gate=1.0)
    o.add('vc', p, 'C3:h B2:h A2:h E3:h F3:h G3:h C3:w', vel='f', gate=1.0)
    o.add('cb', p, 'C2:h B1:h A1:h E2:h F2:h G2:h C2:w', vel='f', gate=1.0)
    o.add('tbn', p, '(C3 G3):h (B2 G3):h (A2 E3):h (E3 B3):h (F3 C4):h (G2 G3):h (C3 G3):w',
          vel='f', gate=1.0)
    o.add('hn', p, 'G4:h G4:h E4:h E4:h F4:h D4:h E4:w', vel='f', gate=1.0)
    o.add('bsn', p, 'C3:h B2:h A2:h E3:h F3:h G3:h C3:w', vel='f', gate=1.0)
    o.add('timp', p + 12, roll('G2', 2, 0.25) + [('C3', 2.0)], vel='f')
    o.perc(p + 12, 'crash:h r:h', vel='f')
    # extension: Ab major appears — the slow movement's key blessing the Answer —
    # then the broadest cadence in the piece
    e = p + 16
    o.add('vln1', e, '(C5 Ab5):w (C5 Ab5):h (Bb4 G5):h (C5 F5):h (B4 F5):h (C5 E5):w (C5 E5):h r:h',
          vel='f', gate=1.0)
    o.add('vln2', e, '(Ab4 Eb5):w (Ab4 Eb5):h (Eb4 Bb4):h (F4 A4):h (D4 G4):h (E4 G4):w (E4 G4):h r:h', vel='f', gate=1.0)
    o.add('vla', e, '(Eb4 C5):w (Eb4 C5):h (G4 Db5):h (A4 C5):h (G4 B4):h (G4 C5):w (G4 C5):h r:h',
          vel='f', gate=1.0)
    o.add('vc', e, 'Ab2:w Ab2:h Eb3:h F3:h G3:h C3:w C3:h r:h', vel='f', gate=1.0)
    o.add('cb', e, 'Ab1:w Ab1:h Eb2:h F2:h G2:h C2:w C2:h r:h', vel='f', gate=1.0)
    o.add('hn', e, '(C4 Eb4):w (C4 Eb4):h (Bb3 Db4):h (A3 C4):h (B3 D4):h (C4 E4):w (C4 E4):h r:h',
          vel='f', gate=1.0)
    o.add('tbn', e, '(Ab2 Eb3):w (Ab2 Eb3):h (Bb2 G3):h (F2 C3):h (G2 D3):h (C3 G3):w (C3 G3):h r:h',
          vel='f', gate=1.0)
    o.add('bsn', e, 'Ab2:w Ab2:h Bb2:h F2:h G2:h C3:w C3:h r:h', vel='mf', gate=1.0)
    o.add('fl', e + 8, 'F6:h G6:h E6:w E6:h r:h', vel='f', gate=1.0)
    o.add('timp', e + 8, 'F3:h G2:h C3:w C3:h r:h', vel='f')
    o.add('hp', e + 16, 'C2:e G2:e C3:e E3:e G3:e C4:e E4:e G4:e C5:e E5:e G5:e C6:e E6:e G6:e C7:e r:e',
          vel='mf', gate=1.0)
    # ...and a breath: the Answer echoed pianissimo before the apotheosis
    g = e + 20
    o.add('vln1', g, 'G4:h C5:h E5:h D5:h C5:w C5:w', vel='p', gate=1.0)
    o.add('vln2', g, 'D4:h E4:h G4:h G4:h G4:w E4:w', vel='pp', gate=1.0)
    o.add('vla', g, 'B3:h C4:h C4:h B3:h C4:w C4:w', vel='pp', gate=1.0)
    o.add('vc', g, 'G2:h C3:h A2:h G2:h C3:w C3:w', vel='pp', gate=1.0)
    o.add('cb', g, 'G1:w A1:h G1:h C2:w C2:w', vel='pp', gate=1.0)
    o.add('cl', g + 8, 'E4:h D4:h E4:w', vel='pp', gate=1.0)

def apotheosis(o, t):
    o.tempo(t, 144, 'Allegro glorioso')
    CMa = dict(bass='C2', vc=['C3', 'G3', 'C4', 'G3'], pad=['G3', 'C4', 'E4'])
    FMa = dict(bass='F2', vc=['F2', 'C3', 'F3', 'C3'], pad=['A3', 'C4', 'F4'])
    GMa = dict(bass='G2', vc=['G2', 'D3', 'G3', 'D3'], pad=['G3', 'B3', 'D4'])
    Am_ = dict(bass='A1', vc=['A2', 'E3', 'A3', 'E3'], pad=['A3', 'C4', 'E4'])

    def engine(prog, tt, vel='ff', pad_vel='f'):
        for i, h in enumerate(prog):
            bt = tt + i * BAR
            o.add('cb', bt, [(h['bass'], 1.0)] * 4, vel=vel, gate=0.85)
            o.add('vc', bt, [(p, 0.5) for p in h['vc'] * 2], vel=vel, gate=0.8)
            o.add('vla', bt, [(None, 0.5), (h['pad'], 0.5)] * 4, vel=pad_vel, gate=0.6)

    # bars 1-8: T1 in C major, violins blazing, the Answer in brass halves
    engine([CMa, CMa, GMa, CMa, FMa, FMa, GMa, CMa], t)
    o.add('vln1', t, B(T1_MAJOR, 8), vel='ff', accent_first=True)
    o.add('vln2', t, B(T1_MAJOR, 8), vel='f')
    o.add('fl', t, B(T1_MAJOR, 8), vel='ff', transpose=12)
    o.add('tpt', t, B(R('r:w', 2) + ' G4:h C5:h E5:h D5:h C5:w ' + R('r:w', 3), 8), vel='f', gate=1.0)
    o.add('hn', t, B(R('r:w', 2) + ' D4:h E4:h G4:h G4:h G4:w ' + R('r:w', 3), 8), vel='f', gate=1.0)
    o.add('timp', t, 'C3:q r:h. r:w G2:q r:h. C3:q r:h. F3:q r:h. r:w G2:q r:h. C3:q r:h.', vel='ff')
    o.add('bsn', t, 'C3:h G2:h C3:h E3:h G2:h B2:h C3:h G2:h F2:h A2:h F2:h C3:h G2:h G2:h C3:h C3:h',
          vel='f', gate=0.95)

    # bars 9-16: swap — the Answer soars in strings, T1-major chatters in winds
    s = t + 32
    engine([CMa, Am_, FMa, GMa, CMa, FMa, GMa, CMa], s, vel='ff', pad_vel='f')
    o.add('vln1', s, B(ANSWER_A + ' ' + 'G5:h E5:h C5:h D5:h E5:h G5:h C6:w', 8), vel='ff', transpose=12, gate=0.95)
    o.add('vln2', s, B(ANSWER_A + ' ' + 'G5:h E5:h C5:h D5:h E5:h G5:h C6:w', 8), vel='ff', gate=0.95)
    o.add('ob', s, B(' '.join(T1_MAJOR.split()[:23]), 4), vel='f')
    o.add('fl', s + 16, B(' '.join(T1_MAJOR.split()[:23]), 4), vel='f', transpose=12)
    o.add('hn', s, B('D4:h E4:h G4:h G4:h G4:h E4:h E4:w '
                     'E4:h C4:h E4:h F4:h G4:h G4:h E4:w', 8), vel='f', gate=1.0)
    o.add('timp', s, 'C3:q r:h. r:w F3:q r:h. G2:q r:h. C3:q r:h. F3:q r:h. G2:q r:h. C3:q r:h.', vel='f')

    # bars 17-24: combined — T1 head + Answer in canon, scale flourishes
    c = t + 64
    engine([CMa, FMa, CMa, Am_, FMa, GMa, CMa, GMa], c)
    o.add('vln1', c, B(' '.join(T1_MAJOR.split()[:23]), 4), vel='ff')
    o.add('tpt', c + 2, 'G4:h C5:h E5:h D5:h C5:h r:h', vel='ff', gate=0.95)
    o.add('vln1', c + 16, B('C6:e B5:e A5:e G5:e F5:e E5:e D5:e C5:e '
                            'D5:e E5:e F5:e G5:e A5:e B5:e C6:e D6:e '
                            'E6:q C6:q G5:q E5:q '
                            'D6:q B5:q G5:q D5:q', 4), vel='ff', gate=0.9)
    o.add('fl', c + 16, B('C7:e B6:e A6:e G6:e F6:e E6:e D6:e C6:e '
                          'D6:e E6:e F6:e G6:e A6:e B6:e C7:q '
                          'E6:q C6:q G5:q E5:q '
                          'D6:q B5:q G5:q D5:q', 4), vel='ff', gate=0.9)
    o.add('tbn', c + 18, 'G2:h C3:h E3:h D3:h C3:h C3:h C3:h', vel='f', gate=0.95)
    o.add('timp', c + 24, roll('G2', 8, 0.5), vel='f', vel_end='ff')

    # bars 25-32: the LAST QUESTION — the minor motto flashes once more...
    # and this time it resolves. D falls to C in full light.
    q = t + 96
    o.add('tpt', q, 'G4:h C5:h Eb5:h D5:h', vel='ff', gate=1.0)            # the old question
    o.add('tbn', q, 'G2:h C3:h Eb3:h D3:h', vel='ff', gate=1.0)
    o.add('hn', q, 'G3:h C4:h Eb4:h D4:h', vel='ff', gate=1.0)
    o.add('vln1', q, trem(['G4', 'C5'], 8, 0.5), vel='f', vel_end='ff', gate=0.9)
    o.add('vln2', q, trem(['Eb4', 'G4'], 8, 0.5), vel='f', gate=0.9)
    o.add('vla', q, trem(['C4', 'G4'], 8, 0.5), vel='f', gate=0.9)
    o.add('vc', q, 'C3:h C3:h G2:h G2:h', vel='ff', gate=0.9)
    o.add('cb', q, 'C2:h C2:h G1:h G1:h', vel='ff', gate=0.9)
    o.add('timp', q, roll('C3', 8, 0.5), vel='f', vel_end='ff')
    # ...the D held over everything... and then: C. In C MAJOR. Resolved.
    o.add('tpt', q + 8, 'D5:w D5:h. C5:q C5:w C5:w', vel='ff', gate=1.0)
    o.add('tbn', q + 8, 'D3:w D3:h. C3:q (C3 G3 E4):w (C3 G3 E4):w', vel='ff', gate=1.0)
    o.add('hn', q + 8, 'D4:w D4:h. C4:q (C4 E4 G4):w (C4 E4 G4):w', vel='ff', gate=1.0)
    o.add('vln1', q + 8, trem('D5', 4, 0.5) + trem('D5', 3, 0.5) + [('C5', 0.5)] + trem(['C5', 'E5'], 8, 0.5),
          vel='ff', gate=0.9)
    o.add('vln2', q + 8, trem('B4', 4, 0.5) + trem('B4', 3, 0.5) + [('C5', 0.5)] + trem(['G4', 'C5'], 8, 0.5),
          vel='ff', gate=0.9)
    o.add('vla', q + 8, trem(['G3', 'F4'], 4, 0.5) + trem(['G3', 'F4'], 3, 0.5) + [(['G3', 'E4'], 0.5)]
                        + trem(['E4', 'G4'], 8, 0.5), vel='f', gate=0.9)
    o.add('vc', q + 8, 'G2:w G2:h. C3:q C3:w C3:w', vel='ff', gate=0.95)
    o.add('cb', q + 8, 'G1:w G1:h. C2:q C2:w C2:w', vel='ff', gate=0.95)
    o.add('fl', q + 12, 'r:h. C6:q C6:e D6:e E6:e G6:e E6:e D6:e C6:e D6:e C6:w', vel='ff', gate=0.9)
    o.add('timp', q + 8, roll('G2', 7, 0.5) + [('C3', 0.5)] + roll('C3', 8, 1.0), vel='ff')
    o.perc(q + 15, 'crash:q', vel='fff')

    # bars 33-40: cadential broadening — the grandest plagal-then-authentic close
    b = t + 128
    o.tempo(b, 120, 'Largamente')
    o.add('vln1', b, '(E5 C6):w (F5 C6):w (E5 C6):h (D5 B5):h (E5 C6):w '
                     '(F5 A5):h (F5 D6):h (E5 C6):h (G5 E6):h (G5 C6):w r:w', vel='fff', gate=1.0)
    o.add('vln2', b, '(G4 E5):w (A4 F5):w (G4 E5):h (G4 D5):h (G4 E5):w '
                     '(A4 C5):h (B4 F5):h (G4 G5):h (C5 C6):h (E5 G5):w r:w', vel='ff', gate=1.0)
    o.add('vla', b, 'G4:w F4:w G4:h G4:h G4:w F4:h G4:h E4:h E4:h (G4 E5):w r:w', vel='ff', gate=1.0)
    o.add('vc', b, 'C3:w F2:w C3:h G2:h C3:w F2:h G2:h C3:h C3:h C3:w r:w', vel='ff', gate=1.0)
    o.add('cb', b, 'C2:w F1:w C2:h G1:h C2:w F1:h G1:h C2:h C2:h C2:w r:w', vel='ff', gate=1.0)
    o.add('tpt', b, '(C5 E5):w (C5 F5):w (C5 E5):h (B4 D5):h (C5 E5):w '
                    '(C5 F5):h (B4 D5):h (C5 E5):h (C5 G5):h (C5 E5):w r:w', vel='fff', gate=1.0)
    o.add('hn', b, '(E4 G4):w (F4 A4):w (E4 G4):h (D4 G4):h (E4 G4):w '
                   '(F4 A4):h (D4 G4):h (E4 G4):h (E4 G4):h (E4 G4):w r:w', vel='ff', gate=1.0)
    o.add('tbn', b, '(C3 G3 E4):w (F2 C3 A3):w (C3 G3):h (G2 D3):h (C3 G3 E4):w '
                    '(F2 C3):h (G2 D3):h (C3 G3):h (C3 G3):h (C3 G3 E4):w r:w', vel='fff', gate=1.0)
    o.add('bsn', b, 'C3:w F2:w C3:h G2:h C3:w F2:h G2:h C3:h C3:h C3:w r:w', vel='ff', gate=1.0)
    o.add('fl', b, 'C6:w C6:w C6:h B5:h C6:w A5:h B5:h C6:h E6:h C6:w r:w', vel='ff', gate=1.0)
    o.add('ob', b, 'E5:w F5:w E5:h D5:h E5:w F5:h D5:h E5:h G5:h E5:w r:w', vel='ff', gate=1.0)
    o.add('cl', b, 'G4:w A4:w G4:h G4:h G4:w A4:h G4:h G4:h C5:h G4:w r:w', vel='ff', gate=1.0)
    o.add('timp', b, roll('C3', 4, 0.5) + roll('F3', 4, 0.5) + [('C3', 2.0), ('G2', 2.0)]
                     + roll('C3', 4, 0.5) + [('F3', 2.0), ('G2', 2.0), ('C3', 2.0), ('C3', 2.0)]
                     + roll('C3', 4, 0.25) + [(None, 4.0)], vel='ff')
    o.perc(b, 'crash:w r:w r:w r:w crash:w r:w r:w bd:q r:h. r:w r:w', vel='ff')
    o.add('hp', b + 16, 'C3:e E3:e G3:e C4:e E4:e G4:e C5:e E5:e G5:e C6:e E6:e G6:e C7:q.', vel='f', gate=1.0)

def coda(o, t):
    # Lento lucente: the hush. The window begins to close — in peace.
    o.tempo(t, 48, 'Lento lucente')
    # bars 1-3: the C major pad assembles exactly like the symphony's first
    # darkness — but in light
    o.add('cb', t, 'C2:w C2:w C2:w', vel='pp', gate=1.0)
    o.add('vc', t, '(C3 G3):w (C3 G3):w (C3 G3):w', vel='pp', gate=1.0)
    o.add('vla', t, 'r:w E4:w E4:w', vel='pp', gate=1.0)
    o.add('vln2', t, 'r:w r:w G4:w', vel='ppp', gate=1.0)
    o.add('timp', t, roll('C3', 4, 0.5), vel='pp', vel_end='ppp')
    # bars 4-6: the cello speaks the Answer, low and complete — first time
    # the resolution is heard quietly, like something understood
    o.add('vc', t + 12, 'G2:q C3:h E3:q D3:h C3:h C3:w', vel='p', gate=1.0)
    o.add('hp', t + 12, 'C3:e G3:e E4:e G4:e r:h r:w r:w', vel='pp', gate=1.0)
    o.add('vln1', t + 12, 'r:w E5:w D5:h C5:h', vel='ppp', gate=1.0)
    # bars 7-10: celesta and flute give the Answer to the high air
    o.add('cel', t + 24, 'G5:q C6:h E6:q D6:h C6:h C6:w r:w', vel='pp', gate=1.0)
    o.add('fl', t + 24, 'G5:q C6:h E6:q D6:h C6:h C6:w r:w', vel='ppp', gate=1.0)
    o.add('vln2', t + 24, 'G4:w G4:w G4:w E4:w', vel='ppp', gate=1.0)
    o.add('vla', t + 24, 'E4:w E4:w C4:w C4:w', vel='ppp', gate=1.0)
    o.add('vc', t + 24, '(C3 G3):w (C3 G3):w (C3 G3):w (C3 G3):w', vel='ppp', gate=1.0)
    o.add('cb', t + 24, 'C2:w C2:w C2:w C2:w', vel='ppp', gate=1.0)
    # bars 11-14: the last tokens of light. A single high C remains — then gone.
    e = t + 40
    o.add('hp', e, 'C3:e E3:e G3:e C4:e E4:e G4:e C5:e E5:e r:w r:w r:w', vel='pp', gate=1.0)
    o.add('cel', e + 4, 'G6:q C7:h. r:w', vel='pp', gate=1.0)
    o.add('vln1', e, 'E5:w C5:w (C5 E5 G5):w (C5 E5 G5):w', vel='ppp', gate=1.0)
    o.add('vln2', e, 'C5:w G4:w (E4 G4):w (E4 G4):w', vel='ppp', gate=1.0)
    o.add('vla', e, 'G4:w E4:w (G3 C4):w (G3 C4):w', vel='ppp', gate=1.0)
    o.add('vc', e, '(C3 G3):w (C3 G3):w (C2 G2):w (C2 G2):w', vel='ppp', gate=1.0)
    o.add('cb', e, 'C2:w C2:w C2:w C2:w', vel='ppp', gate=1.0)
    o.add('cel', e + 12, 'C7:w', vel='pp', gate=1.0)
    o.add('hp', e + 12, 'C2:q (C4 C5):h.', vel='ppp', gate=1.0)

def compose(o: Orchestra, t0: float = 0.0) -> float:
    storm(o, t0)
    striving(o, t0 + 80)
    chorale(o, t0 + 368)
    apotheosis(o, t0 + 456)
    coda(o, t0 + 616)
    return t0 + 672

if __name__ == '__main__':
    o = Orchestra()
    end = compose(o, 0.0)
    os.makedirs('output', exist_ok=True)
    path = write_midi(o, 'output/mvt4.mid')
    print(midi_report(path))
    probs = check_ranges(o)
    print('range problems:', probs if probs else 'none')
    print('end offset:', end, 'ql; orchestra end:', o.end())
