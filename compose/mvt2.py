"""Movement II — The Garden of Forking Paths (Scherzo).

G minor, 3/4, one-in-a-bar presto. Branching possibility: deceptive
cadences as forks in the path; the motto mocked in diminution; a G major
musette trio — the warm branch; an ending that simply evaporates.

Layout (ql from t0, 3 ql per bar):
    0-240   scherzo A (80 bars, q=240)
  240-408   trio (56 bars, q=168)
  408-552   scherzo A' (48 bars, q=240)
  552-612   coda (20 bars)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compose.common import (Orchestra, write_midi, midi_report, check_ranges,
                            total_ql, transpose_events, parse, trem, roll)

BAR = 3.0

def B(dsl, n=1):
    got = total_ql(dsl)
    assert abs(got - 3.0 * n) < 1e-6, f'bad bar sum {got} != {3*n}: {dsl[:60]}'
    return dsl

def R(dsl, times):
    return ' '.join([dsl] * times)

def cell(p0, p1, p2, top=None):
    """One scherzo bar: falling-rising staccato arpeggio, 6 eighths."""
    top = top or (p0[:-1] + str(int(p0[-1]) + 1))
    return f'{p2}:e {p1}:e {p0}:e {p1}:e {p2}:e {top}:e'

# triads for the cell, [low, mid, high]
GmC  = ('G4', 'Bb4', 'D5')
BbC  = ('Bb4', 'D5', 'F5')
CmC  = ('C5', 'Eb5', 'G5')
D7C  = ('F#4', 'A4', 'D5')
EbC  = ('Eb4', 'G4', 'Bb4')
FC   = ('F4', 'A4', 'C5')
GMC  = ('G4', 'B4', 'D5')

# the motto in diminution, mocked — rising 4th, minor 3rd, the fall as a shrug
MOCK = 'D5:e G5:e Bb5:q A5:q'           # one bar of 3/4
MOCK_LOW = 'G3:e C4:e Eb4:q D4:q'

def pizz_bar(o, t, bass, chd, vel='p', third_beat=False):
    pat = f'{bass}:q r:q {bass}:q' if third_beat else f'{bass}:q r:h'
    o.add('cb', t, pat, vel=vel, gate=0.4)
    o.add('vc', t, pat, vel=vel, gate=0.4, transpose=12)
    o.add('vla', t, [(None, 1.0), (chd, 1.0), (chd, 1.0)], vel=vel, gate=0.4)

def scherzo_A(o, t):
    o.timesig(t, '3/4')
    o.tempo(t, 240, 'Presto leggiero')
    o.program('vc', t, 45)      # pizzicato engine
    o.program('cb', t, 45)
    o.program('vla', t, 45)

    # b1-8: the cell, violins alone with pizz floor
    o.add('vln1', t, B(cell(*GmC) + ' ' + cell(*GmC), 2), vel='p', gate=0.45)
    o.add('vln1', t + 6, B(cell(*D7C) + ' ' + cell(*GmC), 2), vel='p', gate=0.45)
    o.add('vln1', t + 12, B(R(cell(*GmC), 2), 2), vel='mp', gate=0.45)
    o.add('vln1', t + 18, B(cell(*D7C) + ' ' + cell(*GmC), 2), vel='mp', gate=0.45)
    chords = [GmC, GmC, D7C, GmC, GmC, GmC, D7C, GmC]
    basses = ['G2', 'G2', 'D2', 'G2', 'G2', 'G2', 'D2', 'G2']
    for i in range(8):
        pizz_bar(o, t + i * BAR, basses[i], list(chords[i][:3]), vel='p')

    # b9-16: answer up in B-flat, first fork hinted (Eb!)
    o.add('vln1', t + 24, B(cell(*BbC) + ' ' + cell(*BbC), 2), vel='mp', gate=0.45)
    o.add('vln2', t + 24, B(R('Bb3:e D4:e F4:e D4:e Bb3:e D4:e', 2), 2), vel='p', gate=0.45)
    o.add('vln1', t + 30, B(cell(*FC) + ' ' + cell(*BbC), 2), vel='mp', gate=0.45)
    o.add('vln1', t + 36, B(cell(*CmC) + ' ' + cell(*CmC), 2), vel='mp', gate=0.45)
    o.add('vln1', t + 42, B(cell(*D7C), 1), vel='mf', gate=0.45)
    o.add('vln1', t + 45, B('Eb5:q. G5:e Bb5:q', 1), vel='f', gate=0.6, accent_first=True)  # FORK: deceptive to Eb
    seq = [BbC, BbC, FC, BbC, CmC, CmC, D7C, EbC]
    sb = ['Bb2', 'Bb2', 'F2', 'Bb2', 'C3', 'C3', 'D3', 'Eb3']
    for i in range(8):
        pizz_bar(o, t + 24 + i * BAR, sb[i], list(seq[i][:3]), vel='p' if i < 6 else 'mf')

    # b17-24: woodwind chatter answers the fork, tiptoes back to G minor
    o.add('fl', t + 48, B(cell('Eb5', 'G5', 'Bb5'), 1), vel='mp', gate=0.45)
    o.add('ob', t + 51, B(cell('C5', 'Eb5', 'G5'), 1), vel='mp', gate=0.45)
    o.add('cl', t + 54, B(cell('A4', 'C5', 'Eb5'), 1), vel='mp', gate=0.45)
    o.add('fl', t + 57, B(cell('Bb4', 'D5', 'F5'), 1), vel='mp', gate=0.45)
    o.add('ob', t + 60, B(cell('G4', 'Bb4', 'D5'), 1), vel='mp', gate=0.45)
    o.add('cl', t + 63, B(cell('F#4', 'A4', 'C5'), 1), vel='mp', gate=0.45)
    o.add('fl', t + 66, B(cell(*GmC), 1), vel='mp', gate=0.45)
    o.add('bsn', t + 48, 'Eb3:q r:h C3:q r:h F3:q r:h Bb2:q r:h '
                         'Eb3:q r:h D3:q r:h D3:q r:h G2:q r:h', vel='p', gate=0.5)
    o.add('vln2', t + 69, B('D5:e Bb4:e G4:e Bb4:e D5:e F#5:e', 1), vel='mp', gate=0.45)

    # b25-40: the motto mocked — tossed between winds over sf string jabs
    m = t + 72
    o.add('ob', m, B(MOCK, 1), vel='mf', gate=0.5)
    o.add('cl', m + 6, B(MOCK, 1), vel='mf', gate=0.5, transpose=-5)
    o.add('fl', m + 12, B(MOCK, 1), vel='mf', gate=0.5, transpose=12)
    o.add('bsn', m + 18, B(MOCK_LOW, 1), vel='mf', gate=0.5)
    o.add('ob', m + 24, B(MOCK, 1), vel='f', gate=0.5, transpose=3)
    o.add('fl', m + 30, B(MOCK, 1), vel='f', gate=0.5, transpose=3)
    o.add('cl', m + 36, B(MOCK_LOW, 1), vel='f', gate=0.5, transpose=12)
    o.add('bsn', m + 42, B(MOCK_LOW, 1), vel='f', gate=0.5, transpose=-5)
    jabs = ['G2', 'D3', 'G3', 'C3', 'Eb3', 'A2', 'D3', 'G2',
            'Bb2', 'F3', 'Bb3', 'Eb3', 'G3', 'C3', 'F#3', 'G3']
    for i in range(16):
        bt = m + i * BAR
        o.add('vc', bt, f'{jabs[i]}:q r:h', vel='mf', gate=0.4)
        o.add('cb', bt, f'{jabs[i]}:q r:h', vel='mf', gate=0.4, transpose=-12)
        if i % 2 == 1:
            o.add('vla', bt, [(None, 1.0), (None, 0.5), (['C4', 'Eb4', 'A4'], 0.5), (None, 1.0)],
                  vel='f', gate=0.4, accent_first=True)
    o.add('timp', m + 21, 'D3:q r:h', vel='mf')
    o.add('timp', m + 45, 'G2:q r:h', vel='f')

    # b41-56: canon build — cell chased through the strings, arco now
    c = t + 120
    o.program('vc', c, 48)
    o.program('cb', c, 48)
    o.program('vla', c, 48)
    line = (cell(*GmC) + ' ' + cell(*GmC) + ' ' + cell(*BbC) + ' ' + cell(*BbC) + ' '
            + cell(*CmC) + ' ' + cell(*CmC) + ' ' + cell(*D7C) + ' ' + cell(*D7C))
    o.add('vln1', c, B(line, 8), vel='mp', vel_end='f', gate=0.5)
    o.add('vln2', c + 3, B(line, 8), vel='mp', vel_end='f', gate=0.5)
    o.add('vla', c + 6, B(line, 8), vel='mp', vel_end='f', gate=0.5, transpose=-12)
    o.add('vc', c + 9, B(line, 8), vel='mp', vel_end='f', gate=0.5, transpose=-24)
    o.add('cb', c, 'G2:q r:h ' * 4 + 'Bb2:q r:h ' * 4 + 'C3:q r:h ' * 4 + 'D3:q r:h ' * 2 + 'D3:q D3:q D3:q D3:q r:q r:q',
          vel='mp', vel_end='f', gate=0.6)
    o.add('fl', c + 24, B(line.split(' ', 24)[-1] if False else R(cell('D5', 'F#5', 'A5'), 2), 2), vel='f', gate=0.5)

    # b49-56 overlap: hemiola hammering (2-beat groups across the bar)
    hm = c + 24
    hemi = '(G4 Bb4 D5):q (G4 Bb4 D5):q (A4 C5 Eb5):q (A4 C5 Eb5):q (Bb4 D5 F5):q (Bb4 D5 F5):q '\
           '(C5 Eb5 G5):q (C5 Eb5 G5):q (D5 F#5 A5):q (D5 F#5 A5):q (D5 F#5 C6):q (D5 F#5 C6):q'
    o.add('ob', hm, B(hemi, 4), vel='f', gate=0.6)
    o.add('cl', hm, B(hemi, 4), vel='f', gate=0.6, transpose=-12)
    o.add('hn', hm, B('G3:q G3:q A3:q A3:q Bb3:q Bb3:q C4:q C4:q D4:q D4:q D4:q D4:q', 4), vel='f', gate=0.7)
    o.add('timp', hm + 9, 'D3:q D3:q D3:q', vel='f')

    # b57-72: full tutti romp, ff
    f = t + 168
    romp = (cell(*GmC) + ' ' + cell(*GmC) + ' ' + cell(*EbC) + ' ' + cell(*EbC) + ' '
            + cell(*CmC) + ' ' + cell(*GmC) + ' ' + cell(*D7C) + ' ' + cell(*GmC))
    o.add('vln1', f, B(romp, 8), vel='ff', gate=0.5)
    o.add('vln2', f, B(romp, 8), vel='f', gate=0.5)
    o.add('fl', f, B(romp, 8), vel='ff', gate=0.5, transpose=12)
    o.add('ob', f, B(romp, 8), vel='f', gate=0.5)
    rb = ['G2', 'G2', 'Eb2', 'Eb2', 'C2', 'C3', 'D3', 'G2']
    rc = [GmC, GmC, EbC, EbC, CmC, GmC, D7C, GmC]
    for i in range(8):
        bt = f + i * BAR
        o.add('cb', bt, f'{rb[i]}:q {rb[i]}:q {rb[i]}:q', vel='f', gate=0.6)
        o.add('vc', bt, f'{rb[i]}:q {rb[i]}:q {rb[i]}:q', vel='f', gate=0.6, transpose=12)
        o.add('vla', bt, [(None, 0.5), (list(rc[i][:3]), 0.5)] * 3, vel='f', gate=0.5)
        o.add('bsn', bt, f'{rb[i]}:h. ', vel='f', gate=0.9, transpose=12)
    o.add('tpt', f + 12, B('C5:q. Eb5:e G5:q G5:q F#5:q A5:q', 2), vel='ff', gate=0.6)
    o.add('timp', f, 'G2:q r:h r:h. r:h. r:h. C3:q r:h r:h. D3:q r:h G2:q r:h', vel='ff')
    o.perc(f, 'crash:q r:h', vel='f')
    # repeat the romp louder, hemiola cadence onto D
    f2 = f + 24
    o.add('vln1', f2, B(romp, 8), vel='ff', gate=0.5)
    o.add('vln2', f2, B(romp, 8), vel='ff', gate=0.5)
    o.add('fl', f2, B(romp, 8), vel='ff', gate=0.5, transpose=12)
    o.add('ob', f2, B(romp, 8), vel='ff', gate=0.5)
    o.add('cl', f2, B(romp, 8), vel='f', gate=0.5)
    for i in range(8):
        bt = f2 + i * BAR
        o.add('cb', bt, f'{rb[i]}:q {rb[i]}:q {rb[i]}:q', vel='ff', gate=0.6)
        o.add('vc', bt, f'{rb[i]}:q {rb[i]}:q {rb[i]}:q', vel='ff', gate=0.6, transpose=12)
        o.add('vla', bt, [(None, 0.5), (list(rc[i][:3]), 0.5)] * 3, vel='f', gate=0.5)
    o.add('hn', f2 + 18, '(D4 F#4 A4):q (D4 F#4 A4):q (D4 F#4 A4):q (D4 F#4 A4):h.', vel='ff', gate=0.8)
    o.add('tbn', f2 + 18, '(D3 A3 D4):q (D3 A3 D4):q (D3 A3 D4):q (D3 A3 D4):h.', vel='ff', gate=0.8)
    o.add('timp', f2 + 18, 'D3:q D3:q D3:q ' + 'D3:q r:h', vel='ff')

    # b73-80: sudden hush — the path pauses at the fork before the trio
    h = t + 216
    o.add('vln1', h, 'A4:h. r:h. A4:h. r:h.', vel='p', gate=0.8)
    o.add('vln2', h, 'F#4:h. r:h. F#4:h. r:h.', vel='p', gate=0.8)
    o.add('vla', h, 'D4:h. r:h. C4:h. r:h.', vel='p', gate=0.8)
    o.add('vc', h, 'D3:h. r:h. D3:h. r:h.', vel='p', gate=0.8)
    o.add('cb', h, 'D2:h. r:h. D2:h. r:h.', vel='p', gate=0.8)
    o.add('fl', h + 12, B('A5:e D6:e A5:q F#5:q', 1), vel='p', gate=0.5)
    o.add('cl', h + 15, B('D5:e A4:e F#4:e A4:e D4:q', 1), vel='pp', gate=0.5)
    o.add('hn', h + 18, 'D4:h. D4:h.', vel='pp', gate=1.0)

def trio(o, t):
    o.tempo(t, 168, 'Poco meno mosso, pastorale')
    # the warm branch: G major musette over a horn-and-bassoon drone
    o.add('hn', t, '(G3 D4):12 (G3 D4):12 (G3 D4):12 (G3 D4):12', vel='p', gate=1.0)
    o.add('bsn', t, '(G2 D3):12 (G2 D3):12 (G2 D3):12 (G2 D3):12', vel='p', gate=1.0)
    tune = ('D5:q. E5:e D5:q B4:q. A4:e B4:q D5:q E5:q G5:q F#5:h A5:q '
            'G5:q. F#5:e E5:q D5:q B4:q G4:q A4:q B4:q A4:q G4:h. ')
    o.add('fl', t, B(tune, 8), vel='mp', gate=0.9)
    o.add('vc', t, 'G3:q r:h ' * 2 + 'D3:q r:h ' * 2 + 'G3:q r:h ' * 2 + 'D3:q r:h G3:q r:h', vel='p', gate=0.5)
    # second phrase: oboe joins in thirds; violins shimmer
    t2 = t + 24
    o.add('fl', t2, B(tune, 8), vel='mp', gate=0.9)
    o.add('ob', t2, B(tune, 8), vel='mp', gate=0.9, transpose=-3)   # parallel... in G: thirds below
    o.add('vln1', t2, trem(['B4', 'D5'], 24, 0.5), vel='pp', gate=0.9)
    o.add('vln2', t2, trem('G4', 24, 0.5), vel='pp', gate=0.9)
    o.add('vc', t2, 'G3:q r:h ' * 2 + 'D3:q r:h ' * 2 + 'G3:q r:h ' * 2 + 'D3:q r:h G3:q r:h', vel='p', gate=0.5)
    # middle: clarinet takes a C major branch, a fork even here
    t3 = t + 48
    o.add('hn', t3, '(C4 G4):12 (C4 G4):12', vel='p', gate=1.0)
    o.add('bsn', t3, '(C3 G3):12 (C3 G3):12', vel='p', gate=1.0)
    ctune = ('G4:q. A4:e G4:q E4:q. D4:e E4:q G4:q A4:q C5:q B4:h D5:q '
             'C5:q. B4:e A4:q G4:q E4:q C4:q D4:q E4:q D4:q C4:h.')
    o.add('cl', t3, B(ctune, 8), vel='mp', gate=0.9)
    o.add('hp', t3, 'C3:e G3:e E4:e G4:e E4:e G3:e ' * 4, vel='pp', gate=1.0)
    # return: tune in violins, full warmth, then the drone dissolves
    t4 = t + 72
    o.add('hn', t4, '(G3 D4):12 (G3 D4):12 (G3 D4):12', vel='p', gate=1.0)
    o.add('bsn', t4, '(G2 D3):12 (G2 D3):12 (G2 D3):12', vel='p', gate=1.0)
    o.add('vln1', t4, B(tune, 8), vel='mf', gate=0.95)
    o.add('vln2', t4, B(tune, 8), vel='mp', gate=0.95, transpose=-12)
    o.add('fl', t4, B(tune, 8), vel='mp', gate=0.9, transpose=12)
    o.add('vla', t4, 'B3:12 B3:12', vel='pp', gate=1.0)
    o.add('vc', t4, 'G2:12 G2:12', vel='pp', gate=1.0)
    o.add('hp', t4, 'G2:e D3:e B3:e D4:e B3:e D3:e ' * 4, vel='pp', gate=1.0)
    # last 16 bars: fade; the cell tiptoes back in minor
    t5 = t + 96
    o.add('vln1', t5, 'B4:h. A4:h. G4:h. F#4:h.', vel='pp', gate=1.0)
    o.add('vla', t5, 'D4:h. D4:h. D4:h. D4:h.', vel='pp', gate=1.0)
    o.add('vc', t5, 'G2:12', vel='pp', gate=1.0)
    o.add('hn', t5, '(G3 D4):12', vel='pp', gate=1.0)
    o.add('cl', t5 + 12, B('D5:e Bb4:e G4:e Bb4:e D5:e G5:e', 1), vel='pp', gate=0.45)
    o.add('fl', t5 + 18, B('D5:e Bb4:e G4:e Bb4:e D5:e F#5:e', 1), vel='pp', gate=0.45)
    o.add('cb', t5 + 12, 'G2:q r:h D2:q r:h D2:q r:h D2:q r:h', vel='pp', gate=0.4)

def scherzo_A2(o, t):
    o.tempo(t, 240, 'Tempo primo')
    o.program('vc', t, 45)
    o.program('cb', t, 45)
    o.program('vla', t, 45)

    # b1-16: the cell returns, impatient — two keys at once almost
    o.add('vln1', t, B(R(cell(*GmC), 2), 2), vel='p', gate=0.45)
    o.add('vln1', t + 6, B(cell(*D7C) + ' ' + cell(*GmC), 2), vel='mp', gate=0.45)
    o.add('fl', t + 12, B(R(cell('G5', 'Bb5', 'D6'), 1), 1), vel='mp', gate=0.45)
    o.add('vln1', t + 15, B(cell(*BbC), 1), vel='mp', gate=0.45)
    o.add('ob', t + 18, B(cell('C5', 'Eb5', 'G5'), 1), vel='mp', gate=0.45)
    o.add('vln1', t + 21, B(cell(*D7C), 1), vel='mf', gate=0.45)
    o.add('vln1', t + 24, B(R(cell(*GmC), 2), 2), vel='mp', gate=0.45)
    o.add('cl', t + 30, B(MOCK, 1), vel='mf', gate=0.5)
    o.add('vln1', t + 33, B(MOCK, 1), vel='mf', gate=0.5, transpose=12)
    o.add('bsn', t + 36, B(MOCK_LOW, 1), vel='mf', gate=0.5)
    o.add('vln1', t + 39, B(cell(*D7C), 1), vel='mf', gate=0.45)
    o.add('vln1', t + 42, B(cell(*GmC) + ' ' + cell(*D7C), 2), vel='f', gate=0.45)
    basses = ['G2', 'G2', 'D2', 'G2', 'G3', 'Bb2', 'C3', 'D3',
              'G2', 'G2', 'C3', 'A2', 'G2', 'D3', 'G2', 'D2']
    chords = [GmC, GmC, D7C, GmC, GmC, BbC, CmC, D7C,
              GmC, GmC, CmC, D7C, GmC, D7C, GmC, D7C]
    for i in range(16):
        pizz_bar(o, t + i * BAR, basses[i], list(chords[i][:3]), vel='p' if i < 8 else 'mp')

    # b17-32: hemiola build straight to the false summit
    c = t + 48
    o.program('vc', c, 48)
    o.program('cb', c, 48)
    o.program('vla', c, 48)
    line = (cell(*GmC) + ' ' + cell(*BbC) + ' ' + cell(*CmC) + ' ' + cell(*D7C) + ' '
            + cell(*EbC) + ' ' + cell(*CmC) + ' ' + cell(*D7C) + ' ' + cell(*D7C))
    o.add('vln1', c, B(line, 8), vel='mf', vel_end='ff', gate=0.5)
    o.add('vln2', c + 3, B(line, 8), vel='mf', vel_end='ff', gate=0.5)
    o.add('vc', c + 6, B(line, 8), vel='mf', vel_end='ff', gate=0.5, transpose=-24)
    o.add('fl', c + 6, B(line, 8), vel='mf', vel_end='ff', gate=0.5, transpose=12)
    o.add('cb', c, 'G2:q r:h Bb2:q r:h C3:q r:h D3:q r:h Eb3:q r:h C3:q r:h D3:q D3:q D3:q D3:q D3:q D3:q',
          vel='mf', vel_end='ff', gate=0.6)
    hemi = '(G4 Bb4 D5):q (G4 Bb4 D5):q (A4 C5 Eb5):q (A4 C5 Eb5):q (Bb4 D5 F5):q (Bb4 D5 F5):q '\
           '(C5 Eb5 G5):q (C5 Eb5 G5):q (D5 F#5 A5):q (D5 F#5 A5):q (D5 F#5 C6):q (D5 F#5 C6):q'
    o.add('ob', c + 12, B(hemi, 4), vel='f', gate=0.6)
    o.add('hn', c + 12, B('G3:q G3:q A3:q A3:q Bb3:q Bb3:q C4:q C4:q D4:q D4:q D4:q D4:q', 4), vel='f', gate=0.7)
    o.add('timp', c + 18, 'D3:q D3:q D3:q D3:q D3:q D3:q', vel='f')

    # b33-48: the BIG FORK — deceptive cadence lands ff on E-flat major, twice,
    # before the path corrects itself
    d = t + 96
    o.add('vln1', d, '(Eb5 G5 Bb5):q r:q (Eb5 G5 Bb5):q r:h.', vel='ff', gate=0.5, accent_first=True)
    o.add('vln2', d, '(Eb4 G4 Bb4):q r:q (Eb4 G4 Bb4):q r:h.', vel='ff', gate=0.5)
    o.add('vla', d, '(Eb4 G4):q r:q (Eb4 G4):q r:h.', vel='ff', gate=0.5)
    o.add('vc', d, 'Eb3:q r:q Eb3:q r:h.', vel='ff', gate=0.5)
    o.add('cb', d, 'Eb2:q r:q Eb2:q r:h.', vel='ff', gate=0.5)
    o.add('hn', d, '(Eb4 G4 Bb4):q r:q (Eb4 G4 Bb4):q r:h.', vel='ff', gate=0.6)
    o.add('tbn', d, '(Eb3 Bb3 Eb4):q r:q (Eb3 Bb3 Eb4):q r:h.', vel='ff', gate=0.6)
    o.add('timp', d, 'Eb3:q r:q Eb3:q r:h.', vel='ff')
    o.perc(d, 'crash:q r:h r:h.', vel='ff')
    # giggling response — winds skitter down from the wrong chord
    o.add('fl', d + 6, B('Bb5:e G5:e Eb5:e G5:e Bb5:e Eb6:e ' + 'Bb5:e G5:e Eb5:e G5:e Bb5:e G5:e', 2), vel='mp', gate=0.45)
    o.add('cl', d + 12, B('G5:e Eb5:e Bb4:e Eb5:e G5:e Bb5:e', 1), vel='mp', gate=0.45)
    o.add('ob', d + 15, B('F5:e D5:e A4:e D5:e F5:e A5:e', 1), vel='mp', gate=0.45)   # pivot: F major -> D7
    # second fork attempt: B major!? — then snaps back
    d2 = d + 18
    o.add('vln1', d2, '(F#5 B5):q r:q (F#5 B5):q r:h.', vel='f', gate=0.5)
    o.add('vln2', d2, '(D#5 F#5):q r:q (D#5 F#5):q r:h.', vel='f', gate=0.5)
    o.add('vc', d2, 'B2:q r:q B2:q r:h.', vel='f', gate=0.5)
    o.add('cb', d2, 'B2:q r:q B2:q r:h.', vel='f', gate=0.5)
    o.add('fl', d2 + 6, B('B5:e F#5:e D#5:e F#5:e B5:e D#6:e', 1), vel='mp', gate=0.45)
    o.add('ob', d2 + 9, B('C6:e A5:e F#5:e A5:e C6:e D6:e', 1), vel='mf', gate=0.45)   # D7 reclaims
    # the path corrects: D pedal drive, 8 bars
    d3 = d2 + 12
    o.add('vln1', d3, B(R(cell(*D7C), 4), 4) + ' ' + B(R(cell('A4', 'C5', 'D5'), 4), 4), vel='f', vel_end='ff', gate=0.5)
    o.add('vln2', d3, B(R('D4:e A4:e D5:e A4:e D4:e A4:e', 8), 8), vel='f', gate=0.5)
    o.add('cb', d3, 'D3:q D3:q D3:q ' * 8, vel='f', vel_end='ff', gate=0.6)
    o.add('vc', d3, 'D3:q D3:q D3:q ' * 8, vel='f', vel_end='ff', gate=0.6, transpose=-12)
    o.add('timp', d3 + 12, roll('D3', 12, 0.25), vel='f', vel_end='ff')
    o.add('hn', d3 + 12, '(D4 F#4 C5):12', vel='f', gate=1.0)
    o.add('tpt', d3 + 18, 'D5:q D5:q D5:q D5:q D5:q D5:q', vel='ff', gate=0.5)

def coda(o, t):
    # evaporation: the garden closes its paths one by one
    o.add('vln1', t, B(cell(*GmC) + ' ' + cell(*GmC), 2), vel='f', gate=0.45)
    o.add('vln2', t, B(R('G3:e Bb3:e D4:e Bb3:e G3:e Bb3:e', 2), 2), vel='mf', gate=0.45)
    o.add('cb', t, 'G2:q r:h G2:q r:h', vel='mf', gate=0.5)
    o.add('timp', t, 'G2:q r:h r:h.', vel='mf')
    # fragments fall away, downward through the sections
    o.add('fl', t + 6, B(cell('G5', 'Bb5', 'D6'), 1), vel='mp', gate=0.45)
    o.add('ob', t + 9, B(cell('D5', 'G5', 'Bb5'), 1), vel='mp', gate=0.45)
    o.add('cl', t + 12, B(cell('Bb4', 'D5', 'G5'), 1), vel='p', gate=0.45)
    o.add('vln2', t + 15, B(cell(*GmC), 1), vel='p', gate=0.45)
    o.add('vla', t + 18, B(cell('D4', 'G4', 'Bb4'), 1), vel='p', gate=0.45)
    o.add('vc', t + 21, B(cell('G3', 'Bb3', 'D4'), 1), vel='pp', gate=0.45)
    o.add('bsn', t + 24, B(cell('G2', 'Bb2', 'D3'), 1), vel='pp', gate=0.45)
    o.program('vc', t + 27, 45)
    o.program('cb', t + 27, 45)
    # last wisps: pizzicato steps and a piccolo-light sigh, gone
    o.add('cb', t + 27, 'G2:q r:h D2:q r:h G2:q r:h r:h.', vel='pp', gate=0.4)
    o.add('vc', t + 30, 'D3:q r:h Bb2:q r:h r:h.', vel='pp', gate=0.4)
    o.add('fl', t + 36, B('D6:e Bb5:e G5:e Bb5:e D6:e G6:e', 1), vel='pp', gate=0.4)
    o.add('hp', t + 42, 'G3:e Bb3:e D4:e G4:e Bb4:e D5:e G5:q. r:h.', vel='pp', gate=1.0)
    o.add('vln1', t + 48, '(G4 D5):h.', vel='ppp', gate=1.0)
    o.add('vla', t + 48, 'Bb3:h.', vel='ppp', gate=1.0)
    o.add('vc', t + 51, 'G2:q r:h', vel='pp', gate=0.4)
    o.add('hp', t + 54, 'G2:q (G3 D4 G4):h', vel='pp', gate=1.0)

def compose(o: Orchestra, t0: float = 0.0) -> float:
    scherzo_A(o, t0)
    trio(o, t0 + 240)
    scherzo_A2(o, t0 + 408)
    coda(o, t0 + 552)
    return t0 + 612

if __name__ == '__main__':
    o = Orchestra()
    end = compose(o, 0.0)
    os.makedirs('output', exist_ok=True)
    path = write_midi(o, 'output/mvt2.mid')
    print(midi_report(path))
    probs = check_ranges(o)
    print('range problems:', probs if probs else 'none')
    print('end offset:', end, 'ql; orchestra end:', o.end())
