"""The Box Is Full — one game on Korobeiniki, for orchestra and square wave.

Nine sections, one continuous movement, ~6 minutes. Run directly to build
output/the-box-is-full.mid plus output/marks.json (section/moment seconds).
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import (Orchestra, R, arp, check_ranges, midi_report, parse,
                    total_ql, transpose_events, trem, write_midi)
from themes import (A1, A1_BARS, A1_DT, A1_PLAIN, A2, A2_BARS, B, B_BARS,
                    B_D, B_EB, CH, OOMPAH, T_CELL, T_DT, T_INV, T_RETRO)

def Bq(dsl, n_bars):
    """Guard: a DSL string must span exactly n_bars of 4/4."""
    got = total_ql(dsl)
    assert got == 4 * n_bars, f'wanted {4*n_bars} ql, got {got}: {dsl[:60]}…'
    return dsl

# chord voicings used by comping/pads (around the staff)
COMP = {
    'D7': ['A3', 'C4', 'F#4'], 'Gm': ['Bb3', 'D4', 'G4'],
    'Cm': ['C4', 'Eb4', 'G4'], 'Bb': ['Bb3', 'D4', 'F4'],
}

def chord_tok(tones):
    return '(' + ' '.join(tones) + ')'

# ======================================================================
# §0  INSERT CARTRIDGE                          16 bars, q=92, G minor
# ======================================================================

def s0_insert_cartridge(o: Orchestra, t0: float) -> float:
    o.tempo(t0, 92, 'insert cartridge')
    o.timesig(t0, '4/4')
    o.mark('insert cartridge', t0)

    # strings begin pizzicato
    for s in ('vla', 'vc', 'cb'):
        o.program(s, t0, 45)

    # the timer: woodblock ticks, bars 1-14
    o.perc(t0, R('wbh:q wbl:q wbl:q wbl:q', 14), vel='pp')

    # falling tetromino cells, each locking with a low pizz + block thunk
    drops = [  # (bar, part, cell, transpose, vel, lock_note)
        (2,  'cl',  T_CELL,  0,   'p',  'D2'),
        (3,  'vla', T_CELL, -12,  'p',  'G2'),
        (4,  'fl',  T_INV,  +12,  'pp', 'D2'),
        (5,  'bsn', T_CELL, -19,  'mp', 'G2'),
        (6,  'ob',  T_RETRO, 0,   'p',  'D2'),
        (7,  'vc',  T_RETRO, -12, 'mp', 'G2'),
        (10, 'vla', T_CELL, -12,  'pp', 'D2'),
        (11, 'bsn', T_INV,  -24,  'pp', 'G2'),
    ]
    for bar, part, cell, tr, v, lock in drops:
        t = t0 + 4 * bar
        o.add(part, t, cell, vel=v, transpose=tr, gate=0.9)
        o.add('cb', t + 2.0, f'{lock}:q', vel='mp', gate=0.8)
        o.perc(t + 2.0, 'wbl:q', vel='mp')

    # the console boots: a power-on ding, then the theme as the cartridge
    # remembers it — four notes at a time
    o.cue('boot', t0 + 30)
    o.add('sq', t0 + 30, 'D4:s D5:e.', vel='mp', gate=0.9)
    o.add('sq', t0 + 32, Bq(A1, 4), vel='p', gate=0.8)

    # assembly: pedal + tremolos + accelerating tick into level 1
    for s in ('vla', 'vc', 'cb'):
        o.program(s, t0 + 46, 48)          # arco
    o.add('vc', t0 + 48, 'G2:w G2:w G2:w G2:w', vel='p', vel_end='f')
    o.add('cb', t0 + 48, 'G1:w G1:w G1:w G1:w', vel='p', vel_end='f')
    o.add('vla', t0 + 48, trem('D4', 16, 0.5), vel='pp', vel_end='f')
    o.add('vln2', t0 + 48, trem('Bb4', 16, 0.5), vel='pp', vel_end='f')
    o.add('vln1', t0 + 56, trem('D5', 8, 0.5), vel='p', vel_end='ff')
    o.add('hn', t0 + 48, '(D3 A3):w (D3 A3):w (D3 A3):w (D3 A3):w',
          vel='pp', vel_end='mf')
    o.add('timp', t0 + 56, trem('D3', 8, 0.25), vel='pp', vel_end='ff')
    o.perc(t0 + 56, R('wbh:e', 8), vel='p', )
    o.perc(t0 + 60, R('wbh:s', 16), vel='mf')
    o.perc(t0 + 56, R('splash:e', 16), vel='pp')
    return t0 + 64

# ======================================================================
# §1  LEVELS 1-2 — THE STRUT                  24 bars, q=138, G minor
# ======================================================================

def s1_strut(o: Orchestra, t0: float) -> float:
    o.tempo(t0, 138, 'level 1 — the strut')
    o.mark('level 1 — the peddler struts', t0)
    o.perc(t0, 'kick:q', vel='ff')
    o.perc(t0, 'crash:q', vel='f')
    bars = A1_BARS + A2_BARS

    def groove(t, n_bars, kick_v='p', sn=False):
        for i in range(n_bars):
            o.perc(t + 4 * i, 'kick:q r:q kick:q r:q', vel=kick_v)
            if sn:
                o.perc(t + 4 * i, 'r:q sn:q r:q sn:q', vel='mf')
            else:
                o.perc(t + 4 * i, 'r:q rim:q r:q rim:q', vel='p')
        o.perc(t, R('hhc:e', 8 * n_bars), vel='pp')

    def oompah(t, vols=('mp', 'mp')):
        for i, ch in enumerate(bars):
            o.add('cb', t + 4 * i, OOMPAH[ch], vel=vols[0], gate=0.7)
            o.add('bsn', t + 4 * i, OOMPAH[ch], vel=vols[1], gate=0.6,
                  transpose=12)

    def comping(t, parts=('vla', 'vln2'), vel='p', thin=False):
        for i, ch in enumerate(bars):
            tones = COMP[ch][:2] if thin else COMP[ch]
            tok = chord_tok(tones)
            for pt in parts:
                o.add(pt, t + 4 * i, f'r:q {tok}:q r:q {tok}:q',
                      vel=vel, gate=0.5)

    # pass 1: theme low — cocky, dry (thin chords keep the register clear)
    oompah(t0)
    comping(t0, thin=True)
    groove(t0, 8)
    o.add('vc', t0, Bq(A1, 4), vel='mf', transpose=-12, gate=0.9)
    o.add('vc', t0 + 16, Bq(A2, 4), vel='mf', transpose=-12, gate=0.9)
    o.add('cl', t0, A1, vel='mp', transpose=-12, gate=0.85)
    o.add('cl', t0 + 16, A2, vel='mp', transpose=-12, gate=0.85)

    # pass 2: melody up an octave, clarinet noodles
    t1 = t0 + 32
    oompah(t1)
    comping(t1)
    groove(t1, 8)
    o.add('vln1', t1, A1, vel='mf', gate=0.92)
    o.add('vln1', t1 + 16, A2, vel='mf', gate=0.92)
    o.add('ob', t1, A1, vel='mp', gate=0.9)
    o.add('ob', t1 + 16, A2, vel='mp', gate=0.9)
    o.add('vc', t1, 'D3:h A2:h G2:h D3:h D3:h A2:h G2:h Bb2:h '
                    'C3:h G2:h Bb2:h F2:h D3:h A2:h G2:h D3:h',
          vel='mp', gate=0.9)
    for i, ch in enumerate(bars):
        tones = CH[ch]
        run = ' '.join(f'r:e {tones[(i + k) % len(tones)]}4:e' for k in range(4))
        o.add('cl', t1 + 4 * i, run, vel='p', gate=0.6)

    # pass 3: brass punches, snare in, cello sings the B-theme head
    t2 = t0 + 64
    oompah(t2, vols=('mf', 'mf'))
    comping(t2, vel='mp')
    groove(t2, 8, kick_v='mf', sn=True)
    o.add('vln1', t2, A1, vel='f', gate=0.92)
    o.add('vln1', t2 + 16, A2, vel='f', gate=0.92)
    o.add('ob', t2, A1, vel='mf', gate=0.9)
    o.add('ob', t2 + 16, A2, vel='mf', gate=0.9)
    o.add('fl', t2, A1, vel='mf', transpose=12, gate=0.9)
    o.add('fl', t2 + 16, A2, vel='mf', transpose=12, gate=0.9)
    for i, ch in enumerate(bars):
        tok = chord_tok(COMP[ch])
        o.add('tpt', t2 + 4 * i, f'r:q {tok}:e r:e r:q {tok}:e r:e',
              vel='mf', gate=0.4)
        o.add('hn', t2 + 4 * i, f'r:q {tok}:e r:e r:q {tok}:e r:e',
              vel='mp', gate=0.4, transpose=-12)
        root = CH[ch][0]
        o.add('tbn', t2 + 4 * i, f'{root}2:q r:q {root}2:q r:q',
              vel='mf', gate=0.6)
    o.add('vc', t2, Bq('D4:h Bb3:h C4:h A3:h D4:h Bb3:h C4:h A3:h '
                       'D4:h Bb3:h C4:h A3:h D4:h Bb3:h C4:h D4:h', 8),
          vel='mf', gate=0.95)
    # fill into level 3
    o.perc(t0 + 94, 'sn:s sn:s sn:e tom4:e tom2:e tom1:q', vel='f')
    return t0 + 96

# ======================================================================
# §2  LEVELS 3-4 — FIRST SWEAT                24 bars, q=152, G minor
# ======================================================================

DRIVE_DYADS = {  # chord -> (vln2 dyad, vla dyad) for driving 8ths
    'D7': (('F#4', 'A4'), ('A3', 'C4')),
    'Gm': (('G4', 'Bb4'), ('Bb3', 'D4')),
    'Cm': (('G4', 'C5'), ('C4', 'Eb4')),
    'Bb': (('F4', 'Bb4'), ('Bb3', 'D4')),
}

def s2_sweat(o: Orchestra, t0: float) -> float:
    o.tempo(t0, 152, 'level 3')
    o.mark('level 3 — first sweat', t0)
    o.perc(t0, 'crash:q', vel='ff')
    for s in ('vln2', 'vla', 'cb'):
        o.program(s, t0, 48)               # all arco now
    bars = A1_BARS + A2_BARS

    def engine(t, vel='f'):
        """Two 8-bar engine passes: drive dyads, pumping bass, kit."""
        for i, ch in enumerate(bars):
            d2, dv = DRIVE_DYADS[ch]
            o.add('vln2', t + 4 * i, R(f'{chord_tok(d2)}:e', 8), vel=vel, gate=0.7)
            o.add('vla', t + 4 * i, R(f'{chord_tok(dv)}:e', 8), vel=vel, gate=0.7)
            r = CH[ch][0]
            o.add('vc', t + 4 * i,
                  f'{r}2:e {r}2:e {r}3:e {r}2:e {r}2:e {r}3:e {r}2:e {r}2:e',
                  vel=vel, gate=0.8)
            o.add('cb', t + 4 * i, R(f'{r}2:e', 8), vel=vel, gate=0.8)
            o.add('hn', t + 4 * i, f'{chord_tok(COMP[ch])}:h '
                                   f'{chord_tok(COMP[ch])}:h',
                  vel='mp', gate=0.9, transpose=-12)
            o.perc(t + 4 * i, 'kick:q kick:q kick:q kick:q', vel='f')
            o.perc(t + 4 * i, 'r:q sn:q r:q sn:q', vel='f')
        o.perc(t, R('hhc:e hhc:e hhc:e hhc:e hhc:e hhc:e hho:e hhc:e', 8),
               vel='mf')

    # pass 1
    engine(t0)
    o.add('vln1', t0, A1, vel='f', gate=0.92)
    o.add('vln1', t0 + 16, A2, vel='f', gate=0.92)
    o.add('fl', t0, A1, vel='f', transpose=12, gate=0.9)
    o.add('fl', t0 + 16, A2, vel='f', transpose=12, gate=0.9)
    o.add('ob', t0, A1, vel='mf', gate=0.9)
    o.add('ob', t0 + 16, A2, vel='mf', gate=0.9)

    # pass 2: trumpet stabs, tambourine, wind run fills
    t1 = t0 + 32
    engine(t1, vel='f')
    o.add('vln1', t1, A1, vel='ff', gate=0.92)
    o.add('vln1', t1 + 16, A2, vel='ff', gate=0.92)
    o.add('fl', t1, A1, vel='f', transpose=12, gate=0.9)
    o.add('fl', t1 + 16, A2, vel='f', transpose=12, gate=0.9)
    o.add('ob', t1, A1, vel='f', gate=0.9)
    o.add('ob', t1 + 16, A2, vel='f', gate=0.9)
    for i, ch in enumerate(bars):
        tok = chord_tok([p + '' for p in COMP[ch]])
        o.add('tpt', t1 + 4 * i, f'r:e {tok}:e r:e {tok}:e r:e {tok}:e r:e {tok}:e',
              vel='mf', gate=0.35)
    o.perc(t1, R('tamb:e', 64), vel='mp')
    o.add('cl', t1 + 14, 'D5:s Eb5:s F5:s G5:s A5:s Bb5:s C6:s D6:s', vel='mf', gate=0.8)
    o.add('cl', t1 + 30, 'G4:s A4:s Bb4:s C5:s D5:s Eb5:s F#5:s G5:s', vel='mf', gate=0.8)

    # stretto pile-up over a dominant pedal: pieces falling too fast
    t2 = t0 + 64
    o.add('vc', t2, R('D3:e D3:e D2:e D3:e', 6), vel='f', vel_end='ff', gate=0.8)
    o.add('cb', t2, R('D2:e D2:e D2:e D2:e', 6), vel='f', vel_end='ff', gate=0.8)
    o.add('timp', t2, trem('D3', 24, 0.25), vel='mf', vel_end='ff')
    o.add('vln2', t2, arp(['D4', 'Eb4'], 0.25, 24), vel='f', vel_end='ff', gate=0.9)
    o.add('vla', t2, arp(['D4', 'Eb4'], 0.25, 24), vel='f', vel_end='ff', gate=0.9)
    entries = [('tbn', -19, 'f'), ('hn', -12, 'f'), ('tpt', -7, 'f'),
               ('ob', 0, 'f'), ('fl', 5, 'ff'), ('vln1', 12, 'ff')]
    for k, (part, tr, v) in enumerate(entries):
        start = t2 + 2 * k
        reps = int((24 - 2 * k) // 4)
        for r_i in range(reps):
            o.add(part, start + 4 * r_i, T_CELL, vel=v, transpose=tr, gate=0.85)
    o.perc(t2 + 16, R('sn:s', 32), vel='mp')
    o.perc(t2, R('hhc:e', 48), vel='mf')

    # LINE CLEAR: hit, harp rip, trapdoor
    t3 = t0 + 88
    o.cue('clear1', t3)
    o.perc(t3, 'kick:q', vel='ff')
    o.perc(t3, 'crash:q', vel='ff')
    o.add('timp', t3, 'D3:q', vel='ff')
    gm_scale = ['G3', 'A3', 'Bb3', 'C4', 'D4', 'Eb4', 'F#4',
                'G4', 'A4', 'Bb4', 'C5', 'D5', 'Eb5', 'F#5',
                'G5', 'A5', 'Bb5', 'C6', 'D6', 'Eb6', 'F#6', 'G6']
    o.add('hp', t3, [(p, 0.125) for p in gm_scale] + [('G6', 1.25)],
          vel='mf', vel_end='ff', gate=1.0)
    o.add('vc', t3, 'G2:w G2:w', vel='p', vel_end='pp', gate=1.0)
    o.add('cb', t3, 'G1:w G1:w', vel='p', vel_end='pp', gate=1.0)
    o.perc(t3 + 4, 'wbh:q wbh:q wbh:q wbh:q', vel='pp')
    o.add('hp', t3 + 6, '(Eb4 G4 Bb4):h', vel='pp', gate=1.0)
    return t0 + 96

# ======================================================================
# §3  THE RYE FIELD (MUSIC B)              20 bars, q=72, E-flat major
# ======================================================================

EB_HARM = ['Eb', 'Bb7', 'Eb', 'Bb7', 'Eb', 'Bb7', 'Ab', 'Bb7']
EB_CH = {
    'Eb':  ['Eb3', 'G3', 'Bb3', 'Eb4', 'G4', 'Bb4'],
    'Bb7': ['Bb2', 'D3', 'F3', 'Ab3', 'D4', 'F4'],
    'Ab':  ['Ab2', 'C3', 'Eb3', 'Ab3', 'C4', 'Eb4'],
    'Cm':  ['C3', 'Eb3', 'G3', 'C4', 'Eb4', 'G4'],
}
EB_PAD = {  # (vc, vla, vln2)
    'Eb':  ('Eb3', 'Bb3', 'G4'),
    'Bb7': ('Bb2', 'Ab3', 'F4'),
    'Ab':  ('Ab2', 'C4', 'Eb4'),
    'Cm':  ('C3', 'G3', 'Eb4'),
}

def s3_rye_field(o: Orchestra, t0: float) -> float:
    o.tempo(t0, 72, 'the rye field')
    o.mark('the rye field (music B)', t0)

    harmony = ['Eb', 'Eb'] + EB_HARM + EB_HARM + ['Cm']   # bars 1-19
    for i, ch in enumerate(harmony):
        o.add('hp', t0 + 4 * i, arp(EB_CH[ch], 0.5, 4, 'updown'), vel='p', gate=0.95)
        vc_p, vla_p, vln2_p = EB_PAD[ch]
        o.add('vc', t0 + 4 * i, f'{vc_p}:w', vel='pp', gate=1.0)
        o.add('vla', t0 + 4 * i, f'{vla_p}:w', vel='pp', gate=1.0)
        o.add('vln2', t0 + 4 * i, f'{vln2_p}:w', vel='pp', gate=1.0)
    o.add('cb', t0 + 8, 'Eb2:w r:w Eb2:w r:w Eb2:w r:w Ab1:w Bb1:w',
          vel='pp', gate=1.0)
    o.add('cb', t0 + 40, 'Eb2:w r:w Eb2:w r:w Eb2:w r:w Ab1:w Bb1:w',
          vel='pp', gate=1.0)

    # a breath of wind over the field
    o.add('fl', t0, 'r:h Bb5:q G5:q', vel='pp', gate=0.9)

    # the horn sings the chorale
    o.add('hn', t0 + 8, Bq(B_EB, 8), vel='mp', gate=0.98)

    # violins take it up; the cello answers; the square wave dreams along
    t1 = t0 + 40
    o.add('vln1', t1, B_EB, vel='mp', vel_end='mf', transpose=12, gate=0.98)
    o.add('ob', t1 + 16, 'Bb4:h G4:h Ab4:h F4:h', vel='pp', gate=0.95)
    o.add('vc', t1, Bq(
        'Eb3:q F3:q G3:q Bb3:q Ab3:q G3:q F3:q D3:q '
        'Eb3:q D3:q Eb3:q G3:q F3:q Bb2:q D3:q F3:q '
        'G3:q Ab3:q Bb3:q G3:q Ab3:q Bb3:q C4:q Ab3:q '
        'G3:q Bb3:q Eb4:q C4:q Bb3:h F3:h', 8), vel='p', gate=0.95)
    o.cue('ring', t1 + 16)
    o.mark('the turquoise ring', t1 + 16)
    o.add('sq', t1 + 16, 'Bb5:h G5:h Ab5:h F5:h G5:q Bb5:q Eb6:h D6:w',
          vel='pp', gate=0.9)
    o.perc(t1 + 16, 'tri:h', vel='pp')

    # the darkening: C minor, then the dominant opens under the field
    t2 = t0 + 72
    o.add('ob', t2, 'G4:h Eb4:h', vel='p', gate=0.95)
    t3 = t2 + 4
    o.add('vc', t3, trem('D3', 4, 0.5), vel='pp', vel_end='f')
    o.add('vla', t3, trem('C4', 4, 0.5), vel='pp', vel_end='f')
    o.add('vln2', t3, trem('F#4', 4, 0.5), vel='pp', vel_end='f')
    o.add('vln1', t3, trem('A4', 4, 0.5), vel='pp', vel_end='f')
    o.add('cb', t3, 'D2:w', vel='pp', vel_end='mf', gate=1.0)
    o.add('timp', t3, trem('D3', 4, 0.25), vel='pp', vel_end='f')
    o.add('hn', t3, '(D3 A3):w', vel='pp', vel_end='mf', gate=1.0)
    o.perc(t3, 'wbh:e wbh:e wbh:e wbh:e wbh:s wbh:s wbh:s wbh:s '
               'wbh:s wbh:s wbh:s wbh:s', vel='mp')
    return t0 + 80

# ======================================================================
# §4  THE CLIMB — LEVELS 5 · 6 · 7        32 bars, 144/152/160, rising
# ======================================================================

def churn_bar(o, t, root, fifth, vel):
    o.add('vln2', t, R(f'{fifth}:e {root}:e', 4), vel=vel, gate=0.75)
    o.add('vla', t, R(f'{root}:e {fifth}:e', 4), vel=vel, gate=0.75,
          transpose=-12)

def s4_climb(o: Orchestra, t0: float) -> float:
    o.mark('the climb — levels 5 · 6 · 7', t0)

    # ---- LEVEL 5 (G minor, q=144) -----------------------------------
    o.tempo(t0, 144, 'level 5')
    o.perc(t0, 'kick:q', vel='ff')
    o.perc(t0, 'crash:q', vel='ff')
    o.add('timp', t0, 'G2:q', vel='ff')
    bars = A1_BARS + A2_BARS
    CHURN = {'D7': ('D4', 'A4'), 'Gm': ('D4', 'G4'),
             'Cm': ('Eb4', 'G4'), 'Bb': ('D4', 'F4')}
    for i, ch in enumerate(bars):
        root, fifth = CHURN[ch]
        churn_bar(o, t0 + 4 * i, root, fifth, 'f')
        r = CH[ch][0]
        o.add('vc', t0 + 4 * i, f'{r}3:q {r}3:q {r}3:e {r}3:e {r}2:q',
              vel='f', gate=0.85)
        o.add('cb', t0 + 4 * i, f'{r}2:q {r}2:q {r}2:e {r}2:e {r}1:q'
              if r in ('G', 'Bb') else f'{r}3:q {r}3:q {r}3:e {r}3:e {r}2:q',
              vel='f', gate=0.85)
        o.add('timp', t0 + 4 * i, f'{r}2:q r:q {r}2:q r:q'
              if r in ('G', 'A') else 'r:w', vel='mf')
        o.perc(t0 + 4 * i, 'kick:q kick:e kick:e kick:q kick:q', vel='f')
        o.perc(t0 + 4 * i, 'r:q sn:q r:q sn:q', vel='f')
    o.perc(t0, R('hhc:e', 64), vel='mf')
    o.add('hn', t0, A1, vel='f', transpose=-12, gate=0.9)
    o.add('hn', t0 + 16, A2, vel='f', transpose=-12, gate=0.9)
    o.add('tbn', t0, A1_PLAIN, vel='f', transpose=-12, gate=0.9)
    o.add('tbn', t0 + 16, A2, vel='f', transpose=-12, gate=0.9)

    # rising sequence + level-up
    t1 = t0 + 32
    seq = 'r:e C5:q Eb5:e G5:q F5:e Eb5:e'
    seq_h = ['Cm', 'D7', 'Bb']
    for k in range(3):
        o.add('vln1', t1 + 4 * k, seq, vel='f', transpose=2 * k, gate=0.9)
        o.add('ob', t1 + 4 * k, seq, vel='f', transpose=2 * k, gate=0.9)
        o.add('fl', t1 + 4 * k, seq, vel='f', transpose=2 * k + 12, gate=0.9)
        ch = seq_h[k]
        churn_bar(o, t1 + 4 * k, CHURN.get(ch, ('D4', 'A4'))[0],
                  CHURN.get(ch, ('D4', 'A4'))[1], 'f')
        r = CH[ch][0]
        o.add('vc', t1 + 4 * k, R(f'{r}3:e {r}2:e', 4), vel='f', gate=0.8)
        o.add('cb', t1 + 4 * k, R(f'{r}2:e {r}2:e', 4), vel='f', gate=0.8)
        o.perc(t1 + 4 * k, 'kick:q kick:q kick:q kick:q', vel='f')
        o.perc(t1 + 4 * k, 'r:q sn:q r:q sn:e sn:e', vel='f')
    # bar 12: the ratchet — V of A minor
    t2 = t1 + 12
    o.cue('level6', t2 + 4)
    o.add('tpt', t2, '(E4 G#4 B4 D5):w', vel='ff', gate=1.0)
    o.add('hn', t2, '(E3 G#3 B3):w', vel='ff', gate=1.0)
    o.add('tbn', t2, '(E2 B2):w', vel='ff', gate=1.0)
    o.add('timp', t2, trem('E3', 4, 0.25), vel='f', vel_end='ff')
    o.perc(t2, 'crash:q', vel='ff')
    o.perc(t2, R('sn:s', 16), vel='mp')
    o.add('fl', t2, 'E5:s F5:s F#5:s G5:s G#5:s A5:s A#5:s B5:s '
                    'C6:s C#6:s D6:s D#6:s E6:s F6:s F#6:s G#6:s',
          vel='f', vel_end='ff', gate=0.9)

    # ---- LEVEL 6 (A minor, q=152) -----------------------------------
    t3 = t2 + 4
    o.tempo(t3, 152, 'level 6')
    am_bars = [('Am', 'E4', 'A4'), ('E7', 'E4', 'B4'), ('Am', 'E4', 'A4'),
               ('E7', 'E4', 'B4'), ('Dm', 'F4', 'A4'), ('C', 'E4', 'G4'),
               ('E7', 'E4', 'B4'), ('Am', 'E4', 'A4')]
    roots = {'Am': 'A', 'E7': 'E', 'Dm': 'D', 'C': 'C'}
    for i, (ch, root, fifth) in enumerate(am_bars):
        churn_bar(o, t3 + 4 * i, root, fifth, 'f')
        r = roots[ch]
        o.add('vc', t3 + 4 * i,
              f'{r}2:e {r}2:e {r}3:e {r}2:e {r}2:e {r}3:e {r}2:e {r}2:e',
              vel='ff', gate=0.8)
        o.add('cb', t3 + 4 * i, R(f'{r}2:e', 8), vel='ff', gate=0.8)
        o.perc(t3 + 4 * i, 'kick:q kick:e kick:e kick:q kick:q', vel='ff')
        o.perc(t3 + 4 * i, 'r:q sn:q r:q sn:q', vel='ff')
    o.perc(t3, R('hhc:e hhc:e hhc:e hho:e', 16), vel='mf')
    o.add('tpt', t3, A1, vel='ff', transpose=2, gate=0.9)
    o.add('tpt', t3 + 16, A2, vel='ff', transpose=2, gate=0.9)
    o.add('timp', t3, R('A2:q r:q E3:q r:q', 8), vel='mf')
    # wind spirals
    for i in range(8):
        cyc = ['A5', 'B5', 'C6', 'B5'] if i % 2 == 0 else ['E5', 'F5', 'G5', 'F5']
        o.add('fl', t3 + 4 * i, arp(cyc, 0.25, 4), vel='mf', gate=0.85)
        o.add('cl', t3 + 4 * i, arp(cyc, 0.25, 4, 'updown'), vel='mf',
              gate=0.85, transpose=-12)
    # the stack appears
    o.add('tbn', t3, 'E3:w E3:w E3:w E3:w (E3 B3):w (E3 B3):w (E3 B3):w (E3 B3):w',
          vel='mp', vel_end='mf', gate=1.0)

    # break: hemiola + ratchet to B minor
    t4 = t3 + 32
    for off in (0, 1.5, 3, 4.5, 6):
        o.add('hn', t4 + off, '(A3 C4 E4):e.', vel='ff', gate=0.7)
        o.add('tpt', t4 + off, '(C5 E5):e.', vel='ff', gate=0.7)
        o.perc(t4 + off, 'sn:e.', vel='ff')
        o.perc(t4 + off, 'kick:e.', vel='ff')
    o.add('vc', t4, 'A2:e B2:e C3:e D3:e E3:e F#3:e G#3:e A#3:e', vel='ff', gate=0.85)
    o.add('cb', t4, 'A2:e B2:e C3:e D3:e E3:e F#3:e G#3:e A#3:e', vel='ff',
          gate=0.85, transpose=-12)
    o.cue('level7', t4 + 8)
    o.add('tpt', t4 + 7.5, '(F#4 A#4 C#5):e', vel='ff', gate=0.8)
    o.perc(t4 + 7.5, 'crash:e', vel='ff')

    # ---- LEVEL 7 (B minor, q=160): stretto + hemiola ----------------
    t5 = t4 + 8
    o.tempo(t5, 160, 'level 7')
    # pounding bass + timpani
    for i in range(8):
        o.add('vc', t5 + 4 * i, R('B2:e B2:e B3:e B2:e', 2), vel='ff', gate=0.8)
        o.add('cb', t5 + 4 * i, R('B1:e B1:e B2:e B1:e', 2), vel='ff', gate=0.8)
        o.add('bsn', t5 + 4 * i, R('B2:e B2:e B3:e B2:e', 2), vel='f', gate=0.8)
        o.perc(t5 + 4 * i, 'kick:e kick:e r:e kick:e kick:e kick:e r:e kick:e', vel='ff')
        o.perc(t5 + 4 * i, 'r:q sn:q r:e sn:e sn:e sn:e', vel='f')
    o.add('timp', t5, R('B2:q F#3:q', 16), vel='f')
    o.perc(t5, R('hhc:e', 64), vel='mf')
    # stretto entries of the cell in B minor, one per bar
    T_BM = 'F#5:q C#5:e D5:e E5:h'
    stretto = [('vln1', 0, 'ff'), ('ob', 0, 'f'), ('fl', 12, 'ff'),
               ('tpt', -12, 'ff'), ('vln1', 0, 'ff'), ('fl', 12, 'ff'),
               ('tpt', -12, 'ff'), ('ob', 0, 'f')]
    for i, (part, tr, v) in enumerate(stretto):
        o.add(part, t5 + 4 * i, T_BM, vel=v, transpose=tr, gate=0.85)
    # hemiola chops + the stack grows
    for b in range(0, 8, 2):
        for off in (0, 1.5, 3, 4.5, 6):
            o.add('hn', t5 + 4 * b + off, '(B3 D4 F#4):e.', vel='f', gate=0.6)
    o.add('tbn', t5, '(E3 B3):w (E3 B3):w (E3 B3):w (E3 B3):w '
                     '(E3 B3):w (E3 B3):w (E3 B3):w (E3 B3):w',
          vel='mf', gate=1.0)
    o.add('vla', t5 + 8, 'F#4:w F#4:w F#4:w F#4:w F#4:w F#4:w',
          vel='mf', vel_end='f', gate=1.0)

    # ascent into the clear: D major scale rising, everything swelling
    t6 = t5 + 32
    rise = ('B4:s C#5:s D5:s E5:s F#5:s G5:s A5:s B5:s '
            'C#6:s D6:s C#6:s B5:s A5:s B5:s C#6:s D6:s '
            'E6:s D6:s C#6:s D6:s E6:s F#6:s E6:s D6:s '
            'C#6:s D6:s E6:s F#6:s G6:s A6:s B6:s C#7:s')
    o.add('vln1', t6, Bq(rise, 2), vel='f', vel_end='ff', gate=0.9)
    o.add('fl', t6, rise.replace('C#7:s', 'B6:s'), vel='f', vel_end='ff', gate=0.9)
    o.add('ob', t6, 'B4:s C#5:s D5:s E5:s F#5:s G5:s A5:s B5:s '
                    'C#6:s D6:s C#6:s B5:s A5:s B5:s C#6:s D6:s '
                    'E6:s D6:s C#6:s D6:s E6:s F6:s E6:s D6:s '
                    'C#6:s D6:s E6:s F6:s r:q', vel='f', gate=0.9)
    o.add('hn', t6, '(A3 C#4 E4 G4):w (A3 C#4 E4 G4):w', vel='f', vel_end='ff', gate=1.0)
    o.add('tbn', t6, '(A2 E3):w (A2 E3):w', vel='f', vel_end='ff', gate=1.0)
    o.add('tpt', t6, '(A4 C#5):w (A4 C#5):w', vel='f', vel_end='ff', gate=1.0)
    o.add('timp', t6, trem('A2', 8, 0.25), vel='f', vel_end='ff')
    o.add('vc', t6, R('A2:e A2:e A3:e A2:e', 4), vel='ff', gate=0.8)
    o.add('cb', t6, R('A1:e A1:e A2:e A1:e', 4), vel='ff', gate=0.8)
    o.perc(t6, R('sn:s', 32), vel='f')
    o.perc(t6, 'kick:q kick:q kick:q kick:q kick:q kick:q kick:e kick:e', vel='ff')
    return t6 + 8

# ======================================================================
# §5  TETRIS! — four lines at once             12 bars, q=160, D major
# ======================================================================

D_CHURN = {'D': ('F#5', 'G5', 'A5', 'G5'), 'A7': ('C#5', 'D5', 'E5', 'D5'),
           'G': ('D5', 'E5', 'G5', 'E5')}
BD_HARM = ['D', 'A7', 'D', 'A7', 'D', 'A7', 'G', 'D']

def s5_tetris(o: Orchestra, t0: float) -> float:
    o.tempo(t0, 160, 'TETRIS!')
    o.mark('TETRIS! — four lines', t0)
    o.cue('tetris', t0)

    # the clear: one hit, four ascending lines cascading
    o.perc(t0, 'kick:q', vel='ff')
    o.perc(t0, 'china:q', vel='ff')
    o.add('timp', t0, trem('D3', 4, 0.25), vel='ff')
    o.add('tbn', t0, '(D3 A3):w', vel='ff', gate=1.0)
    o.add('hn', t0, '(D4 F#4 A4):w', vel='ff', gate=1.0)
    dmaj = ['D', 'E', 'F#', 'G', 'A', 'B', 'C#']
    def run(base_oct, start_deg=0):
        out = []
        octv = base_oct
        deg = start_deg
        for _ in range(8):
            out.append((f'{dmaj[deg]}{octv}', 0.25))
            deg += 1
            if deg >= 7:
                deg = 0
                octv += 1
        return out
    o.add('hp', t0, run(3) + [('D5', 2.0)], vel='f', gate=1.0)
    o.add('fl', t0 + 1, run(5) + [('D6', 1.0)], vel='f', gate=0.95)
    o.add('cl', t0 + 2, run(4) + [('D5', 2.0)], vel='f', gate=0.95)
    o.add('vln1', t0 + 3, run(5) + [('D6', 1.0)], vel='ff', gate=0.95)

    # the blaze: B theme in brass over churning strings; the theme's only
    # resolution in the whole piece — instantly mortgaged
    t1 = t0 + 4
    o.add('tpt', t1, Bq(B_D, 8), vel='fff', gate=0.95)
    o.add('hn', t1, B_D, vel='ff', gate=0.95)
    o.add('tbn', t1, B_D, vel='ff', transpose=-12, gate=0.95)
    o.add('ob', t1, B_D, vel='ff', transpose=12, gate=0.95)
    for i, ch in enumerate(BD_HARM):
        cyc = D_CHURN[ch]
        o.add('vln1', t1 + 4 * i, arp(list(cyc), 0.25, 4), vel='ff', gate=0.8)
        o.add('vln2', t1 + 4 * i, arp(list(cyc), 0.25, 4), vel='ff',
              gate=0.8, transpose=-12)
        o.add('vla', t1 + 4 * i, arp(list(cyc), 0.25, 4), vel='f',
              gate=0.8, transpose=-24)
        riff = 'A2:q E2:e F#2:e G2:q A2:q'
        o.add('vc', t1 + 4 * i, riff, vel='ff', gate=0.85)
        o.add('cb', t1 + 4 * i, riff, vel='ff', gate=0.85)
        o.add('bsn', t1 + 4 * i, riff, vel='ff', gate=0.85, transpose=12)
        o.perc(t1 + 4 * i, 'kick:q r:e kick:e kick:q r:q', vel='ff')
        o.perc(t1 + 4 * i, 'r:q sn:q r:q sn:q', vel='ff')
        if i % 2 == 0:
            o.perc(t1 + 4 * i, 'china:q', vel='ff')
    o.perc(t1, R('ride:e', 64), vel='mf')
    o.add('timp', t1, R('D3:q A2:q D3:q A2:q', 8), vel='ff')
    # high trills
    o.add('fl', t1 + 8, arp(['A6', 'B6'], 0.25, 8), vel='f', gate=0.9)
    o.add('fl', t1 + 24, arp(['A6', 'B6'], 0.25, 8), vel='ff', gate=0.9)

    # peak hold, then the snap
    t2 = t1 + 32
    o.add('tpt', t2, '(A4 D5 F#5):w (A4 D5 F#5):w', vel='fff', gate=1.0)
    o.add('hn', t2, '(F#4 A4):w (F#4 A4):w', vel='fff', gate=1.0)
    o.add('tbn', t2, '(D3 A3 D4):w (D3 A3 D4):w', vel='fff', gate=1.0)
    o.add('vln1', t2, arp(['D5', 'E5', 'F#5', 'A5'], 0.25, 8), vel='ff', gate=0.85)
    o.add('vln2', t2, arp(['A4', 'B4', 'C#5', 'E5'], 0.25, 8), vel='ff', gate=0.85)
    o.add('fl', t2, 'B5:q A5:q F#5:q A5:q B5:q D6:q A5:h', vel='ff', gate=0.9)
    o.add('vc', t2, R('D3:e D3:e D2:e D3:e', 4), vel='ff', gate=0.8)
    o.add('cb', t2, R('D2:e D2:e D3:e D2:e', 4), vel='ff', gate=0.8)
    o.add('timp', t2, trem('D3', 8, 0.5), vel='ff')
    o.perc(t2, 'crash:q r:h. crash:q r:h.', vel='ff')
    o.perc(t2, R('kick:q', 8), vel='ff')
    o.perc(t2 + 7, 'sn:s sn:s sn:e tom4:e tom1:e', vel='ff')
    return t2 + 8

# ======================================================================
# §6  THE BOTTOM DROPS                       4 bars, accel, D7 curdles
# ======================================================================

def s6_bottom_drops(o: Orchestra, t0: float) -> float:
    o.mark('the bottom drops', t0)
    o.tempo(t0, 164)
    # subito: tremolo D major hanging in the strings
    o.add('vln1', t0, trem('F#5', 8, 0.5), vel='p', gate=0.95)
    o.add('vln2', t0, trem('D5', 8, 0.5), vel='p', gate=0.95)
    o.add('vla', t0, trem('A4', 8, 0.5), vel='p', gate=0.95)
    o.add('cb', t0, 'D2:w D2:w D2:w D2:w', vel='pp', vel_end='f', gate=1.0)
    o.add('sq', t0, R('D5:e', 16), vel='pp', vel_end='mp', gate=0.5)
    o.perc(t0, R('hhc:e', 16), vel='pp')
    o.perc(t0, 'kick:q r:q kick:q r:q kick:q r:q kick:q r:q', vel='p')
    # the seventh, then the flat nine
    o.add('vc', t0 + 4, 'C3:w', vel='pp', vel_end='mp', gate=1.0)
    o.tempo(t0 + 8, 170)
    o.add('vc', t0 + 8, trem('Eb3', 8, 0.5), vel='mp', vel_end='ff', gate=0.95)
    o.add('vln1', t0 + 8, trem('Eb5', 8, 0.5), vel='mp', vel_end='ff', gate=0.95)
    o.add('vln2', t0 + 8, trem('C5', 8, 0.5), vel='mp', vel_end='ff', gate=0.95)
    o.add('vla', t0 + 8, trem('F#4', 8, 0.5), vel='mp', vel_end='ff', gate=0.95)
    o.add('timp', t0 + 8, trem('D3', 8, 0.25), vel='pp', vel_end='fff')
    o.perc(t0 + 8, R('sn:s', 32), vel='pp', )
    o.add('hn', t0 + 8, '(D3 F#3 C4):w (D3 F#3 C4 Eb4):w', vel='mp',
          vel_end='ff', gate=1.0)
    o.add('tbn', t0 + 12, '(D2 D3):w', vel='mf', vel_end='ff', gate=1.0)
    o.add('sq', t0 + 8, R('D5:s', 32), vel='mp', vel_end='f', gate=0.5)
    o.tempo(t0 + 12, 174)
    o.add('fl', t0 + 12, 'G4:s G#4:s A4:s A#4:s B4:s C5:s C#5:s D5:s '
                         'D#5:s E5:s F5:s F#5:s G5:s G#5:s A5:s A#5:s',
          vel='mf', vel_end='ff', gate=0.9)
    o.perc(t0 + 12, R('wbh:s', 16), vel='f')
    return t0 + 16

# ======================================================================
# §7  LEVEL 9 — KILL SCREEN              27 bars, q=176→188, G minor
# ======================================================================

CHROMA = ['G', 'Ab', 'A', 'Bb', 'B', 'C', 'C#', 'D']

def s7_kill_screen(o: Orchestra, t0: float) -> float:
    o.tempo(t0, 176, 'level 9 — kill screen')
    o.mark('level 9 — kill screen', t0)
    o.cue('killscreen', t0)

    def pound(t, root, n_bars, vel='ff'):
        # contrabass drops an octave only where its low range allows
        cb_tr = -12 if root in ('G', 'Ab', 'A', 'Bb', 'B') else 0
        for i in range(n_bars):
            pat = f'{root}2:e {root}2:e {root}3:e {root}2:e ' \
                  f'{root}2:e {root}3:e {root}2:e {root}2:e'
            o.add('vc', t + 4 * i, pat, vel=vel, gate=0.8)
            o.add('cb', t + 4 * i, pat, vel=vel, gate=0.8, transpose=cb_tr)
            o.add('bsn', t + 4 * i, pat, vel='f', gate=0.8)

    # bars 1-16: the chromatic rise, two bars per semitone
    for k, root in enumerate(CHROMA):
        pound(t0 + 8 * k, root, 2)
    # trombones hammer the roots on the beats for the first 8 bars
    for k in range(4):
        r = CHROMA[k]
        o.add('tbn', t0 + 8 * k, R(f'({r}2 {r}3):q', 8), vel='ff', gate=0.7)

    # kit: relentless
    for i in range(16):
        o.perc(t0 + 4 * i, 'kick:e kick:e kick:e kick:e kick:e kick:e kick:e kick:e',
               vel='ff')
        o.perc(t0 + 4 * i, 'r:e sn:e r:e sn:e r:e sn:e r:e sn:e', vel='f')
    o.perc(t0, R('hhc:s', 128), vel='mf')
    for i in range(0, 16, 4):
        o.perc(t0 + 4 * i, 'china:q', vel='ff')

    # bars 1-8: the theme at double time, ratcheting with the floor
    for j, tr in enumerate((0, 0, 2, 2)):
        t = t0 + 8 * j
        o.add('sq', t, Bq(A1_DT, 2), vel='ff', transpose=tr, gate=0.85)
        o.add('vln1', t, A1_DT, vel='ff', transpose=tr, gate=0.85)
        o.add('fl', t, A1_DT, vel='ff', transpose=tr + 12, gate=0.85)

    # bars 9-16: fragmentation — the machine loops straight while the
    # orchestra flails in three-eighth displacement
    t1 = t0 + 32
    o.tempo(t1, 180)
    for j in range(4):                      # machine: steady 2-ql grid
        tr = (4, 5, 6, 7)[j]
        for k in range(4):
            o.add('sq', t1 + 8 * j + 2 * k, T_DT, vel='ff', transpose=tr, gate=0.85)
    for j in range(4):                      # humans: displaced entries
        tr = (4, 5, 6, 7)[j]
        for off in (0, 1.5, 3, 4.5, 6):
            o.add('vln1', t1 + 8 * j + off, T_DT, vel='ff', transpose=tr, gate=0.85)
            if off in (0, 3, 6):
                o.add('fl', t1 + 8 * j + off, T_DT, vel='f', transpose=tr + 12,
                      gate=0.85)
            else:
                o.add('ob', t1 + 8 * j + off, T_DT, vel='f', transpose=tr, gate=0.85)
    # the stack starts holding through everything
    o.add('tbn', t1, 'D3:w D3:w (D3 Ab3):w (D3 Ab3):w '
                     '(D3 Ab3):w (D3 Ab3):w (D3 Ab3):w (D3 Ab3):w',
          vel='mf', vel_end='ff', gate=1.0)
    o.add('vla', t1 + 16, '(Eb4 E4):w (Eb4 E4):w (Eb4 E4):w (Eb4 E4):w',
          vel='mf', vel_end='ff', gate=1.0)
    for b in range(0, 8, 2):
        for off in (0, 1.5, 3, 4.5, 6):
            o.add('hn', t1 + 4 * b + off, '(G3 C4 F4):e.', vel='ff', gate=0.6)
            if off in (0, 3):
                o.perc(t1 + 4 * b + off, 'china:e.', vel='f')

    # bars 17-22: the alarm — falling fifth against the dominant floor
    t2 = t1 + 32
    o.tempo(t2, 184)
    pound(t2, 'D', 6, vel='ff')
    o.add('timp', t2, trem('D3', 24, 0.25), vel='f', vel_end='fff')
    alarm = 'D5:e A4:e'
    for k in range(12):
        o.add('sq', t2 + 2 * k, alarm, vel='ff', gate=0.8)
        o.add('vln1', t2 + 2 * k, alarm, vel='ff', gate=0.8)
        o.add('fl', t2 + 2 * k, alarm, vel='ff', transpose=12, gate=0.8)
    for off in [x * 1.5 for x in range(16)]:
        o.add('tpt', t2 + off, '(D5 A4):e.', vel='ff', gate=0.6)
        o.add('ob', t2 + off, 'D6:e.', vel='f', gate=0.6)
    o.add('hn', t2, '(B3 F4):w (B3 F4):w (B3 F4):w (B3 F4):w (B3 F4):w (B3 F4):w',
          vel='f', vel_end='ff', gate=1.0)
    o.add('tbn', t2, '(D3 Ab3):w (D3 Ab3):w (D3 Ab3):w (D3 Ab3):w (D3 Ab3):w (D3 Ab3):w',
          vel='ff', gate=1.0)
    o.add('vla', t2, '(Eb4 E4):w (Eb4 E4):w (Eb4 E4):w (Eb4 E4):w (Eb4 E4):w (Eb4 E4):w',
          vel='ff', gate=1.0)
    for i in range(6):
        o.perc(t2 + 4 * i, 'kick:e kick:e kick:e kick:e kick:e kick:e kick:e kick:e',
               vel='ff')
        o.perc(t2 + 4 * i, 'sn:e r:e sn:e sn:e r:e sn:e sn:e r:e', vel='ff')
        o.perc(t2 + 4 * i, 'china:q r:q china:q r:q', vel='f')

    # bars 23-24: the last ascent — everything climbs, nothing left to place
    t3 = t2 + 24
    o.tempo(t3, 188)
    chrom = [(62 + k, 0.25) for k in range(32)]              # D4 → A6
    o.add('vln1', t3, chrom, vel='f', vel_end='fff', gate=0.9)
    o.add('vln2', t3, [(57 + k, 0.25) for k in range(32)], vel='f',
          vel_end='fff', gate=0.9)
    o.add('fl', t3, [(74 + k, 0.25) for k in range(23)] + [(96, 2.25)],
          vel='f', vel_end='fff', gate=0.9)
    o.add('ob', t3, [(62 + k, 0.25) for k in range(28)] + [(None, 1.0)],
          vel='f', vel_end='fff', gate=0.9)
    o.add('cl', t3, [(56 + k, 0.25) for k in range(32)], vel='f',
          vel_end='fff', gate=0.9)
    o.add('hn', t3, '(D4 Eb4 F#4):w (D4 Eb4 F#4):w', vel='ff', vel_end='fff', gate=1.0)
    o.add('tpt', t3, '(A4 C5 D5):w (A4 C5 D5):w', vel='ff', vel_end='fff', gate=1.0)
    o.add('tbn', t3, '(D2 D3 Ab3):w (D2 D3 Ab3):w', vel='ff', vel_end='fff', gate=1.0)
    pound(t3, 'D', 2, vel='ff')
    o.add('timp', t3, trem('D3', 8, 0.25), vel='ff', vel_end='fff')
    o.perc(t3, R('sn:s', 32), vel='ff')
    o.perc(t3, R('kick:e', 16), vel='ff')

    # TOP OUT: the well, full — one chord, then nothing
    t4 = t3 + 8
    o.cue('topout', t4)
    o.mark('top out', t4)
    o.add('hp', t4 - 0.5, [(31 + k * 3, 0.0625) for k in range(8)], vel='ff', gate=1.0)
    stack = [
        ('cb',   [(31, 8.0)]),                       # G1
        ('vc',   [(['G2', 'D3'], 8.0)]),
        ('tbn',  [(['D3', 'Ab3'], 8.0)]),
        ('bsn',  [(['Bb2', 'F3'], 8.0)]),
        ('hn',   [(['D4', 'Eb4', 'F#4'], 8.0)]),
        ('tpt',  [(['A4', 'C5', 'D5'], 8.0)]),
        ('vla',  [(['Bb4', 'C#5'], 8.0)]),
        ('vln2', [(['D5', 'Eb5'], 8.0)]),
        ('vln1', [(['F#5', 'A5'], 8.0)]),
        ('ob',   [(['Bb5', 'C6'], 8.0)]),
        ('fl',   [(['D6', 'Eb6'], 8.0)]),
        ('sq',   [('D6', 8.0)]),
        ('hp',   [(['G2', 'D3', 'Ab3', 'Eb4', 'A4', 'C#5', 'G5'], 8.0)]),
    ]
    for part, ev in stack:
        o.add(part, t4, ev, vel='fff', gate=1.0)
    o.add('timp', t4, trem('G2', 8, 0.25), vel='fff')
    o.perc(t4, 'china:w china:w', vel='fff')
    o.perc(t4, 'crash:w crash:w', vel='ff')
    o.perc(t4, 'kick:q', vel='fff')

    # the cut, and four seconds of nothing
    t5 = t4 + 8
    o.tempo(t5, 60)
    return t5 + 4

# ======================================================================
# §8  SCORE SCREEN                        ~18 bars, q=64, Gm → D7 …
# ======================================================================

def s8_score_screen(o: Orchestra, t0: float) -> float:
    o.tempo(t0, 64, 'score screen')
    o.mark('score screen — the song goes on', t0)
    o.cue('gameover', t0)

    # the game-over jingle is the chorale, alone, in the machine's voice
    o.add('sq', t0, Bq(B, 8), vel='pp', gate=0.9)
    for b in range(4, 8):
        o.perc(t0 + 4 * b, 'wbl:q r:q r:h', vel='pp')

    # the peddler's verse: the patter slowed into a lament
    t1 = t0 + 32
    o.mark("the peddler's verse", t1)
    o.add('vc', t1, Bq(A1, 4), vel='p', transpose=-12, gate=0.97)
    pads = [('D7', 'D2', ['A3', 'C4'], 'F#4'), ('Gm', 'G2', ['Bb3', 'D4'], 'G4'),
            ('D7', 'D2', ['A3', 'C4'], 'F#4'), ('Gm', 'G2', ['Bb3', 'D4'], 'G4')]
    for i, (ch, cb_n, vla_n, vln2_n) in enumerate(pads):
        o.add('cb', t1 + 4 * i, f'{cb_n}:w', vel='pp', gate=1.0)
        o.add('vla', t1 + 4 * i, [(vla_n, 4.0)], vel='pp', gate=1.0)
        o.add('vln2', t1 + 4 * i, f'{vln2_n}:w', vel='pp', gate=1.0)
        o.add('hp', t1 + 4 * i, f'{cb_n}:q', vel='pp', gate=1.0)

    # the violin and the ghost sing the last phrase together
    t2 = t1 + 16
    last = 'D5:h Bb4:h C5:h A4:h Bb4:q D5:q G5:h F#5:w'
    o.add('vln1', t2, Bq(last, 4), vel='p', gate=0.98)
    o.add('sq', t2, last, vel='pp', gate=0.95)
    o.add('vc', t2, 'G3:h Bb3:h A3:h D3:h Bb3:h G3:h A3:w', vel='pp', gate=0.98)
    o.add('vla', t2, 'D4:w C4:w D4:w C4:w', vel='ppp', gate=1.0)
    o.add('cb', t2, 'G2:w D2:w G2:w D2:w', vel='ppp', gate=1.0)

    # the cadence that never lands: F# over D7, held
    t3 = t2 + 16
    o.add('vln1', t3, [('F#5', 8.0)], vel='pp', gate=1.0)
    o.add('sq', t3, [('F#5', 8.0)], vel='pp', gate=1.0)
    o.add('hn', t3, '(A3 C4):w (A3 C4):w', vel='ppp', gate=1.0)
    o.add('vc', t3, 'D3:w D3:w', vel='ppp', gate=1.0)
    o.add('cb', t3, 'D2:w D2:w', vel='ppp', gate=1.0)
    o.add('hp', t3 + 4, 'D2:e A2:e D3:e F#3:e A3:e C4:e D4:e r:e', vel='pp', gate=1.0)

    # press start: the next piece is already falling
    t4 = t3 + 8
    o.cue('press-start', t4)
    o.mark('press start', t4)
    o.perc(t4, 'wbh:q r:q wbh:q', vel='pp')
    return t4 + 4

# ======================================================================

def build(path='output/the-box-is-full.mid'):
    o = Orchestra()
    t = 0.0
    t = s0_insert_cartridge(o, t)
    t = s1_strut(o, t)
    t = s2_sweat(o, t)
    t = s3_rye_field(o, t)
    t = s4_climb(o, t)
    t = s5_tetris(o, t)
    t = s6_bottom_drops(o, t)
    t = s7_kill_screen(o, t)
    t = s8_score_screen(o, t)

    problems = check_ranges(o)
    if problems:
        print('RANGE PROBLEMS:')
        for p in problems:
            print('  ', p)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_midi(o, path)
    print(midi_report(path))
    print(f'\nend offset: {t} ql = {o.seconds(t):.1f}s ({o.seconds(t)/60:.2f} min)')

    marks = {
        'sections': [[round(o.seconds(off), 2), label] for label, off in o.marks],
        'cues': {k: round(o.seconds(v), 2) for k, v in o.cues.items()},
        'end': round(o.seconds(t), 2),
    }
    with open('output/marks.json', 'w') as f:
        json.dump(marks, f, indent=1)
    print(json.dumps(marks, indent=1))
    return o, t

if __name__ == '__main__':
    build()
