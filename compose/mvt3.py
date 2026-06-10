"""Movement III — What the Light Holds.

A-flat major, Adagio cantabile. Attention as love. The theme opens with
the motto in MAJOR (Eb-Ab-C-Bb) — the almost-answer, still denied its
final note. At the climax the C-minor motto interrupts: the memory of
mortality. Serenity is regained, but the cadence is left leaning toward
the finale: the last chord carries C on top.

Layout (ql from t0, 4 ql per bar, q=56):
    0- 64  A: the theme (16 bars)
   64-112  B: woodwind dialogue, wandering warmth (12 bars)
  112-168  A': climax and interruption (14 bars)
  168-216  coda: light, evaded resolution (12 bars)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compose.common import (Orchestra, write_midi, midi_report, check_ranges,
                            total_ql, transpose_events, parse, trem, roll)

BAR = 4.0

def B(dsl, n=1):
    got = total_ql(dsl)
    assert abs(got - 4.0 * n) < 1e-6, f'bad bar sum {got} != {4*n}: {dsl[:60]}'
    return dsl

# The hymn theme, 16 bars. Phrase 1 rises from the major motto;
# phrase 2 soars and finds its only full close.
HYMN_P1 = (
    'Eb4:q Ab4:h C5:q '
    'Bb4:h. C5:q '
    'Db5:q. C5:e Bb4:q Ab4:q '
    'Ab4:h G4:h '
    'Eb4:q Ab4:h C5:q '
    'Bb4:h. Db5:q '
    'C5:q F5:q. Eb5:e Db5:q '
    'Eb5:h. r:q'
)
HYMN_P2 = (
    'C5:q Eb5:h Ab5:q '
    'G5:h. F5:q '
    'Eb5:q. F5:e G5:q Eb5:q '
    'F5:h Db5:h '
    'Bb4:q Eb5:h G5:q '
    'Ab5:h G5:q F5:q '
    'Eb5:q C5:q Db5:q Bb4:q '
    'Ab4:w'
)

def section_A(o, t):
    o.timesig(t, '4/4')
    o.tempo(t, 56, 'Adagio cantabile')

    # phrase 1: violins sing; bass descends Ab-G-F-Eb in tenths
    o.add('vln1', t, B(HYMN_P1, 8), vel='mp', gate=1.0)
    o.add('vln2', t, 'C4:w Bb3:w Ab3:w Bb3:h Bb3:h '
                     'C4:w C4:w Db4:h Db4:h Bb3:h Bb3:h', vel='p', gate=1.0)
    o.add('vla', t, 'Eb4:w Eb4:w Db4:w Db4:h Bb3:h '
                    'Eb4:w Eb4:h E4:h F4:h F4:h Eb4:h Db4:h', vel='p', gate=1.0)
    o.add('vc', t, 'Ab2:h. Eb3:q G2:h Bb2:h F2:h Ab2:h Eb3:h Eb2:h '
                   'Ab2:h. C3:q G2:h C3:h Db3:h Bb2:h Eb3:h Eb3:h', vel='p', gate=1.0)
    o.add('cb', t, 'Ab1:w G1:w F1:w Eb2:w Ab1:w G1:w Db2:h Bb1:h Eb2:w', vel='pp', gate=1.0)

    # phrase 2: cellos double the tune an octave down; flute halo; harp moves
    t2 = t + 32
    o.add('vln1', t2, B(HYMN_P2, 8), vel='mf', gate=1.0)
    o.add('vc', t2, B(HYMN_P2, 8), vel='mp', gate=1.0, transpose=-12)
    o.add('fl', t2 + 0, 'r:w r:w r:w r:w r:h Eb6:h C6:h Db6:q Eb6:q Eb6:q C6:q Db6:q Bb5:q Ab5:w',
          vel='p', gate=1.0)
    o.add('vln2', t2, 'Ab3:w Bb3:w C4:w Db4:w Eb4:h Db4:h C4:h Db4:h Ab3:h Bb3:h C4:w', vel='p', gate=1.0)
    o.add('vla', t2, 'F4:w Eb4:w G4:h Eb4:h F4:w G4:h Bb4:h Ab4:h F4:h Eb4:h Db4:h Eb4:w', vel='p', gate=1.0)
    o.add('cb', t2, 'F2:w Eb2:w C2:w Db2:w Eb2:w Db2:w Bb1:h Eb2:h Ab1:w', vel='pp', gate=1.0)
    o.add('cl', t2, '(Ab3 C4):w (G3 Bb3):w (G3 C4):w (Ab3 Db4):w (G3 Bb3):w '
                    '(Ab3 Db4):w (Ab3 Db4):h (G3 Bb3):h (Ab3 C4):w', vel='pp', gate=1.0)
    o.add('hp', t2, 'F2:e C3:e Ab3:e C4:e F4:e C4:e Ab3:e C3:e '
                    'Eb2:e Bb2:e G3:e Bb3:e Eb4:e Bb3:e G3:e Bb2:e '
                    'C2:e G2:e Eb3:e G3:e C4:e G3:e Eb3:e G2:e '
                    'Db2:e Ab2:e F3:e Ab3:e Db4:e Ab3:e F3:e Ab2:e '
                    'Eb2:e Bb2:e G3:e Bb3:e Eb4:e Bb3:e G3:e Bb2:e '
                    'Db2:e Ab2:e F3:e Ab3:e Db4:e Ab3:e F3:e Ab2:e '
                    'Bb1:e F2:e Db3:e F3:e Eb3:e Bb2:e Eb2:e Bb1:e '
                    'Ab1:e Eb2:e C3:e Eb3:e Ab3:e Eb3:e C3:e Eb2:e', vel='pp', gate=1.0)
    o.add('bsn', t2 + 28, 'Eb3:h Eb2:h', vel='pp', gate=1.0)

def section_B(o, t):
    # wandering warmth: Db, then B-flat minor, an F minor shadow, back to V
    # oboe sigh in Db
    o.add('ob', t, 'F4:q Bb4:h Db5:q C5:h Ab4:h', vel='mp', gate=1.0)
    o.add('hp', t, 'Db2:e Ab2:e F3:e Ab3:e Db4:e Ab3:e F3:e Ab2:e ' * 2, vel='pp', gate=1.0)
    o.add('vc', t, 'Db3:q r:q Ab2:q r:q Db3:q r:q Ab2:q r:q', vel='pp', gate=0.5)
    o.add('cb', t, 'Db2:w Db2:w', vel='pp', gate=1.0)
    # clarinet answers, bending to B-flat minor
    o.add('cl', t + 8, 'Db5:q F5:h Db5:q C5:h Bb4:h', vel='mp', gate=1.0)
    o.add('hp', t + 8, 'Bb1:e F2:e Db3:e F3:e Bb3:e F3:e Db3:e F2:e ' * 2, vel='pp', gate=1.0)
    o.add('vc', t + 8, 'Bb2:q r:q F2:q r:q Bb2:q r:q F2:q r:q', vel='pp', gate=0.5)
    o.add('cb', t + 8, 'Bb1:w F1:w', vel='pp', gate=1.0)
    # flute lifts toward the light again
    o.add('fl', t + 16, 'Bb5:q Eb6:h Bb5:q Ab5:h F5:h', vel='mp', gate=1.0)
    o.add('hp', t + 16, 'Eb2:e Bb2:e G3:e Bb3:e Eb4:e Bb3:e G3:e Bb2:e ' * 2, vel='pp', gate=1.0)
    o.add('vc', t + 16, 'Eb3:q r:q Bb2:q r:q Eb3:q r:q Bb2:q r:q', vel='pp', gate=0.5)
    o.add('cb', t + 16, 'Eb2:w Eb2:w', vel='pp', gate=1.0)
    # strings re-enter: the F-minor shadow (the first hint of the end)
    s = t + 24
    o.add('vln1', s, 'Ab4:q C5:h Eb5:q Db5:h C5:h', vel='mp', gate=1.0)
    o.add('vln2', s, 'F4:w F4:h Ab4:h', vel='p', gate=1.0)
    o.add('vla', s, 'C4:w Db4:w', vel='p', gate=1.0)
    o.add('vc', s, 'F2:h C3:h Bb2:h Ab2:h', vel='p', gate=1.0)
    o.add('cb', s, 'F1:w Bb1:w', vel='pp', gate=1.0)
    o.add('bsn', s, 'F3:w Bb2:w', vel='pp', gate=1.0)
    # rising sequence toward the dominant — hope gathering
    o.add('vln1', s + 8, 'Bb4:q Db5:h F5:q Eb5:h Db5:h', vel='mf', gate=1.0)
    o.add('vln2', s + 8, 'Gb4:w Gb4:h F4:h', vel='mp', gate=1.0)
    o.add('vla', s + 8, 'Db4:w C4:h Ab3:h', vel='mp', gate=1.0)
    o.add('vc', s + 8, 'Bb2:h Gb3:h F3:h Db3:h', vel='mp', gate=1.0)
    o.add('cb', s + 8, 'Gb2:w F2:w', vel='p', gate=1.0)
    # dominant: Eb7, the air brightens; little inner motions
    d = s + 16
    o.add('vln1', d, 'Eb5:q Ab5:h G5:q F5:h Eb5:h', vel='mf', gate=1.0)
    o.add('vln2', d, 'Bb4:w Ab4:h Bb4:h', vel='mp', gate=1.0)
    o.add('vla', d, 'G4:h Ab4:h Db4:h Bb3:h', vel='mp', gate=1.0)
    o.add('vc', d, 'Eb3:h Db3:h Bb2:h Eb3:h', vel='mp', gate=1.0)
    o.add('cb', d, 'Eb2:w Eb2:w', vel='p', gate=1.0)
    o.add('hn', d, '(G3 Bb3):w (Ab3 Bb3):h (G3 Bb3):h', vel='pp', gate=1.0)

def section_A2(o, t):
    # the full-hearted restatement: theme in octaves, tutti warmth
    o.tempo(t, 60, 'Poco piu mosso, con anima')
    o.add('vln1', t, B(HYMN_P1, 8), vel='f', transpose=12, gate=1.0)
    o.add('vln2', t, B(HYMN_P1, 8), vel='f', gate=1.0)
    o.add('fl', t, B(HYMN_P1, 8), vel='mf', transpose=12, gate=1.0)
    o.add('ob', t, B(HYMN_P1, 8), vel='mf', gate=1.0)
    o.add('cl', t, B(HYMN_P1, 8), vel='mf', gate=1.0)
    hn_counter = B('Ab3:h C4:h Eb4:h Db4:h Db4:h C4:q Bb3:q Bb3:h Bb3:h '
                   'Ab3:h C4:h Eb4:h E4:h F4:h Ab4:h G4:h G4:h', 8)
    o.add('hn', t, hn_counter, vel='mf', gate=1.0)
    o.add('vla', t, 'Eb4:w Eb4:w Db4:w Db4:h Bb3:h Eb4:w Eb4:h E4:h F4:h F4:h Eb4:h Db4:h',
          vel='mf', gate=1.0)
    o.add('vc', t, 'Ab2:h. Eb3:q G2:h Bb2:h F2:h Ab2:h Eb3:h Eb2:h '
                   'Ab2:h. C3:q G2:h C3:h Db3:h Bb2:h Eb3:h Eb3:h', vel='mf', gate=1.0)
    o.add('cb', t, 'Ab1:w G1:w F1:w Eb2:w Ab1:w G1:w Db2:h Bb1:h Eb2:w', vel='mp', gate=1.0)
    o.add('hp', t, 'Ab2:e Eb3:e C4:e Eb4:e Ab4:e Eb4:e C4:e Eb3:e ' * 8, vel='mp', gate=1.0)
    o.add('bsn', t, 'Ab2:w G2:w F2:w Eb3:w Ab2:w G2:w Db3:h Bb2:h Eb3:w', vel='mp', gate=1.0)

    # the soar — phrase 2 first half, blooming toward the peak
    t2 = t + 32
    o.add('vln1', t2, B(' '.join(HYMN_P2.split()[:11]), 4), vel='f', vel_end='ff', transpose=12, gate=1.0)
    o.add('vln2', t2, B(' '.join(HYMN_P2.split()[:11]), 4), vel='f', gate=1.0)
    o.add('fl', t2, B(' '.join(HYMN_P2.split()[:11]), 4), vel='f', transpose=12, gate=1.0)
    o.add('ob', t2, B(' '.join(HYMN_P2.split()[:11]), 4), vel='f', gate=1.0)
    o.add('vc', t2, B(' '.join(HYMN_P2.split()[:11]), 4), vel='f', gate=1.0, transpose=-12)
    o.add('vla', t2, 'F4:w Eb4:w G4:h Eb4:h F4:w', vel='mf', gate=1.0)
    o.add('cb', t2, 'F2:w Eb2:w C2:w Db2:w', vel='mf', gate=1.0)
    o.add('bsn', t2, 'F2:w Eb2:w C2:w Db2:w', vel='mf', gate=1.0, transpose=12)
    o.add('hn', t2, '(Ab3 C4):w (Bb3 Eb4):w (C4 Eb4):w (Db4 F4):w', vel='mf', gate=1.0)
    o.add('hp', t2, 'F2:e C3:e Ab3:e C4:e F4:e C4:e Ab3:e C3:e '
                    'Eb2:e Bb2:e G3:e Bb3:e Eb4:e Bb3:e G3:e Bb2:e '
                    'C2:e G2:e Eb3:e G3:e C4:e G3:e Eb3:e G2:e '
                    'Db2:e Ab2:e F3:e Ab3:e Db4:e Ab3:e F3:e Ab2:e', vel='mp', gate=1.0)
    o.add('timp', t2 + 12, roll('Db3', 4, 0.5), vel='pp', vel_end='mf')

    # THE INTERRUPTION: at the height of the phrase, the minor motto.
    # The warmth halts on a huge suspended chord; the brass remember C minor.
    x = t2 + 16
    o.add('vln1', x, '(Db5 Ab5):q r:q. r:e r:h', vel='ff', gate=0.6)
    o.add('vln2', x, '(Db4 F4):q r:q. r:e r:h', vel='ff', gate=0.6)
    o.add('vla', x, '(Ab3 Db4):q r:q. r:e r:h', vel='ff', gate=0.6)
    o.add('vc', x, 'Db3:q r:q. r:e r:h', vel='ff', gate=0.6)
    o.add('cb', x, 'Db2:q r:q. r:e r:h', vel='ff', gate=0.6)
    o.perc(x, 'tamtam:q', vel='mp')
    # silence... then the motto, cold, in C minor — quarter = grave weight
    o.add('tpt', x + 4, 'G4:h C5:h Eb5:h D5:h D5:w', vel='f', gate=1.0)
    o.add('tbn', x + 4, 'G3:h C4:h Eb4:h D4:h D4:w', vel='f', gate=1.0)
    o.add('hn', x + 4, 'G3:h C4:h Eb4:h D4:h D4:w', vel='f', gate=1.0)
    o.add('vc', x + 4, trem('C3', 16, 0.5), vel='p', vel_end='mf', gate=0.9)
    o.add('cb', x + 4, 'C2:w C2:w C2:w C2:w', vel='p', vel_end='mf', gate=1.0)
    o.add('vla', x + 4, trem(['G3', 'C4'], 16, 0.5), vel='p', vel_end='mf', gate=0.9)
    o.add('timp', x + 4, roll('C3', 16, 0.5), vel='pp', vel_end='mp')
    # aftermath: the D hangs in the trumpet, the harmony slides away beneath it
    o.add('vln2', x + 20, '(Ab3 C4):w (Ab3 Db4):w', vel='pp', gate=1.0)
    o.add('vla', x + 20, '(F3 Ab3):w (F3 Ab3):w', vel='pp', gate=1.0)
    o.add('vc', x + 20, 'F2:w Db3:w', vel='pp', gate=1.0)
    o.add('cb', x + 20, 'F1:w Db2:w', vel='pp', gate=1.0)

def coda(o, t):
    o.tempo(t, 52, 'Tranquillo')
    # serenity regained: fragments of the hymn over a tonic pedal;
    # the celesta enters for the first time — points of light
    o.add('vln1', t, 'Eb4:q Ab4:h C5:q Bb4:h. C5:q Db5:q. C5:e Bb4:q Ab4:q Ab4:h G4:h',
          vel='p', gate=1.0)
    o.add('vln2', t, 'C4:w Bb3:w Ab3:w Bb3:h Bb3:h', vel='pp', gate=1.0)
    o.add('vla', t, 'Eb4:w Eb4:w Db4:w Db4:h Bb3:h', vel='pp', gate=1.0)
    o.add('vc', t, 'Ab2:w Ab2:w Ab2:w Ab2:h Eb2:h', vel='pp', gate=1.0)
    o.add('cb', t, 'Ab1:w Ab1:w Ab1:w Ab1:w', vel='pp', gate=1.0)
    o.add('cel', t + 2, 'Eb5:q Ab5:h C6:q r:w', vel='pp', gate=1.0)
    o.add('cel', t + 10, 'C6:q Eb6:h Ab6:q r:h', vel='pp', gate=1.0)
    # the evaded cadence: IV - V - (deceptive) vi ... then settling anyway
    s = t + 16
    o.add('vln1', s, 'Db5:h Eb5:h F5:w', vel='p', gate=1.0)            # IV V -> vi: the light leans
    o.add('vln2', s, 'Ab4:h G4:h Ab4:w', vel='pp', gate=1.0)
    o.add('vla', s, 'F4:h Db4:h C4:w', vel='pp', gate=1.0)
    o.add('vc', s, 'Db3:h Eb3:h F3:w', vel='pp', gate=1.0)
    o.add('cb', s, 'Db2:h Eb2:h F2:w', vel='pp', gate=1.0)
    o.add('ob', s + 4, 'F5:h. Eb5:q', vel='pp', gate=1.0)
    # second try: it doesn't cadence so much as alight — Ab with C on top
    s2 = s + 8
    o.add('vln1', s2, 'Eb5:h Db5:h C5:8', vel='pp', gate=1.0)
    o.add('vln2', s2, 'Ab4:h Ab4:h Ab4:8', vel='pp', gate=1.0)
    o.add('vla', s2, 'Eb4:h F4:h Eb4:8', vel='pp', gate=1.0)
    o.add('vc', s2, 'C3:h Db3:h C3:8', vel='pp', gate=1.0)
    o.add('cb', s2, 'Ab1:w Ab1:8', vel='ppp', gate=1.0)
    o.add('hn', s2 + 4, '(Ab3 Eb4):8', vel='ppp', gate=1.0)
    o.add('cl', s2 + 4, '(Eb4 G4):8', vel='ppp', gate=1.0)
    # the celesta speaks the major motto once more, unresolved, like a question
    # asked gently this time
    o.add('cel', s2 + 12, 'Eb6:q Ab6:h C7:q Bb6:6 r:h', vel='pp', gate=1.0)
    o.add('hp', s2 + 12, 'Ab2:e Eb3:e C4:e Eb4:e Ab4:e C5:e Eb5:e Ab5:e r:w r:w r:w', vel='pp', gate=1.0)
    o.add('hp', s2 + 20, '(Ab2 Eb3 Ab3 C4):w', vel='ppp', gate=1.0)

def compose(o: Orchestra, t0: float = 0.0) -> float:
    section_A(o, t0)
    section_B(o, t0 + 64)
    section_A2(o, t0 + 112)
    coda(o, t0 + 168)
    return t0 + 216

if __name__ == '__main__':
    o = Orchestra()
    end = compose(o, 0.0)
    os.makedirs('output', exist_ok=True)
    path = write_midi(o, 'output/mvt3.mid')
    print(midi_report(path))
    probs = check_ranges(o)
    print('range problems:', probs if probs else 'none')
    print('end offset:', end, 'ql; orchestra end:', o.end())
