"""Perigee — a tango for a falling satellite.

One continuous movement, ~5 minutes. The orbit is the form (docs/03):
three revolutions of apogee/perigee, each apogee shorter, each perigee
longer and hotter, then re-entry, the cut, and the weightless coda.

    ../../../.venv/bin/python src/compose.py     (from pieces-src/perigee/)
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib import B, Piece, assess, figures, midi, midi_report, voicing

import tango
from band import quintet
from themes import (CELL2, CELL2_HEADS, CELL4, CELL4_HEADS, CHORDS_A,
                    CHORDS_B, COUNTER_B, GESTURE, PHRASE_A1, PHRASE_A2,
                    PHRASE_B1, PHRASE_B2, RITMICO)

OUT = pathlib.Path(__file__).resolve().parents[1] / 'output'

# Section starts in absolute beats (all 4/4; docs/03 section map).
S0, S1, S2, S3, S4 = 0, 16, 80, 144, 184      # telemetry, A1, P1, A2, P2
S5, S6, S7, S8, S9 = 264, 288, 384, 448, 452  # A3, P3, re-entry, cut, after
END = 496


# ------------------------------------------------------------ 0: telemetry
def telemetry(p):
    p.tempo(S0, 66, 'adagio - a beacon, still healthy')
    p.mark('telemetry', S0)
    for i, at in enumerate([0, 6, 12]):                 # the ping
        p.note('pno', at, 'E6', 0.5, vel=44 - 4 * i, swing=False)
        p.pedal('pno', at, at + 3.5)
    p.add('cb', S0, 'A2:w A2:w A2:w A2:w', vel=36, gate=0.98)
    tango.golpe(p, 2.5, 'rim:e', vel=28)
    tango.golpe(p, 7.0, 'wbl:e', vel=26)
    tango.golpe(p, 11.5, 'rim:e', vel=26)
    tango.golpe(p, 14.75, 'claves:e', vel=24)
    figures.harp_arp(p, 'gtr', ['A2', 'E3', 'A3', 'B3', 'C4', 'E4'], 8,
                     step=0.25, vel=40)
    figures.scoop(p, 'vln', 12, semitones=1.0)          # bridge into apogee
    tango.sing(p, 'vln', 12, 'A5:w', vel=34, breathe=0.6)


# ---------------------------------------------- 1: apogee I — the full lyric
def apogee1(p):
    t = S1
    p.mark('apogee - the whole Earth at once', t)
    # bandoneon: the theme, complete, breathing
    tango.sing(p, 'bnd', t, PHRASE_A1, vel=46, vel_end=58)
    tango.sing(p, 'bnd', t + 16, PHRASE_A2, vel=58, vel_end=48)
    tango.sing(p, 'bnd', t + 32, PHRASE_B1, vel=60, vel_end=78)
    tango.sing(p, 'bnd', t + 48, PHRASE_B2, vel=74, vel_end=48)
    # guitar: broken chords, one bar each, slowly warming
    for i, sym in enumerate(CHORDS_A + CHORDS_B):
        v = voicing(sym, 'E3', 'C5')
        p.add('gtr', t + 4 * i, figures.arp(v, 0.5, 4.0, 'updown'),
              vel=44 + i, gate=0.9, swing=False)
    # bass: marcato en dos from bar 9 — the floor arrives late
    near = 'A2'
    for i, sym in enumerate((CHORDS_A + CHORDS_B)[4:]):
        near = tango.bass_endos(p, t + 16 + 4 * i, sym, vel=44, near=near)
    # violin: guide-tone countermelody under phrase B, with sighs
    figures.scoop(p, 'vln', t + 32, semitones=1.0)
    figures.scoop(p, 'vln', t + 42, semitones=1.0)
    tango.sing(p, 'vln', t + 32, COUNTER_B, vel=44, vel_end=56, breathe=0.7)
    # piano: rolled chords + pedal under phrase B only
    for i, sym in enumerate(CHORDS_B):
        figures.strum(p, 'pno', voicing(sym, 'C4', 'C5'), t + 32 + 4 * i,
                      3.0, 44, spread=0.03)
        p.pedal('pno', t + 32 + 4 * i, t + 36 + 4 * i - 0.15)


# ------------------------------------------- 2: perigee I — first low pass
def perigee1(p):
    t = S2
    p.tempo(t, 120, 'tango - first low pass')
    p.mark('first perigee - gravity says hello', t)
    p.cue('first arrastre', t)
    tango.full_voice(p, t - 0.25)
    ch = CHORDS_A * 2
    near = 'A2'
    for i in range(15):                                  # bar 16 is the break
        bt, sym = t + 4 * i, ch[i]
        if i % 4 == 0:
            tango.arrastre(p, bt, sym, vel=90)
        lift = 6 if i >= 8 else 0
        near = tango.bass_marcato(p, bt, sym, vel=86 + lift, near=near)
        tango.piano_marcato(p, bt, sym, vel=78 + lift)
        tango.guitar_comp(p, bt, sym, vel=62)
    # the theme recast ritmico: bandoneon, then violin an octave up
    p.add('bnd', t, RITMICO, vel=76, vel_end=88, gate=0.62)
    p.add('vln', t + 32, RITMICO, vel=88, vel_end=96, transpose=12, gate=0.62)
    for i in range(8):                                   # bnd stabs behind vln
        v = voicing(ch[8 + i], 'A3', 'A4')
        p.add('bnd', t + 32 + 4 * i + 1, [(v, 0.5)], vel=74, gate=0.5)
        p.add('bnd', t + 32 + 4 * i + 3, [(v, 0.5)], vel=68, gate=0.5)
    for k in range(4):                                   # tambor pops
        tango.golpe(p, t + 32 + 8 * k + 3.5, 'rim:e', vel=40)
    # bar 36: the break — sincopa hits, then the second apogee
    for at, sym, v in ((t + 60, 'Am', 96), (t + 61.5, 'Am', 90),
                       (t + 63, 'E7', 102)):
        tango.stab(p, at, sym, vel=v)
        p.add('pno', at, [(['A1', 'A2'] if sym == 'Am' else ['E2', 'E3'], 1)],
              vel=v, gate=0.5)
        p.note('cb', at, 'A1' if sym == 'Am' else 'E2', 1, vel=v + 2, gate=0.6)
        tango.golpe(p, at, 'wbh:e', vel=50)


# --------------------------------------------- 3: apogee II — shorter now
def apogee2(p):
    t = S3
    p.tempo(t, 72, 'meno - the far arc, shorter')
    p.mark('apogee, but shorter', t)
    # violin takes phrase A only, an octave up, in C minor
    for at in (t + 2, t + 10, t + 16):
        figures.scoop(p, 'vln', at, semitones=1.0)
    tango.sing(p, 'vln', t, PHRASE_A1, vel=48, vel_end=60, transpose=15)
    tango.sing(p, 'vln', t + 16, PHRASE_A2, vel=60, vel_end=44, transpose=15)
    ch = ['Cm', 'Bb', 'Ab', 'G7'] * 2
    for i, sym in enumerate(ch):                        # far, thin support
        bt = t + 4 * i
        v = voicing(sym, 'G3', 'F4', near='C4')
        p.add('bnd', bt, [(v, 4)], vel=38, gate=0.98)
        tango.bellows(p, 'bnd', bt, bt + 4, intensity=0.5)
        p.add('gtr', bt, figures.arp(voicing(sym, 'G2', 'G3'), 1.0, 4.0),
              vel=40, gate=0.9, swing=False)
        r = tango.fit_root(sym, 'C2', 'C3')
        p.add('pno', bt, [([r, r + 12], 4)], vel=38, gate=0.98)
        p.pedal('pno', bt, bt + 3.9)
    # bars 45-46: the invasion — the marcato arrives before the tempo does
    p.note('vln', t + 32, 'Eb6', 8, vel=52)
    tango.bellows(p, 'vln', t + 32, t + 40, intensity=1.2)
    for j, sym in enumerate(['Ab', 'G7']):
        r = tango.fit_root(sym, 'E1', 'D3', near='A1')
        for k in range(8):
            at = t + 32 + 4 * j + 0.5 * k
            p.note('cb', at, r, 0.3, vel=50 + 3 * k + 14 * j, swing=False)
            p.add('pno', at, [([r + 12, r + 24], 0.3)],
                  vel=46 + 3 * k + 14 * j, swing=False)
    tango.golpe(p, t + 38, 'rim:e rim:e rim:e rim:e', vel=34)


# ------------------------------------- 4: perigee II — longer, faster, lower
def perigee2(p):
    t = S4
    p.tempo(t, 132, 'piu mosso - the engine')
    p.mark('second perigee - longer, faster, lower', t)
    tango.full_voice(p, t - 0.25)
    ch = ['Cm', 'Ab', 'Bb', 'G7']
    tango.sincopa332(p, t, 'Cm', vel=82)                # engine alone, 2 bars
    tango.sincopa332(p, t + 4, 'Cm', vel=86, sym2='G7')
    for k in range(64):                                 # chicharra: cabasa,
        tango.golpe(p, t + 0.5 * k, [('cabasa', 0.4)],  # bars 47-54
                    vel=26 + (6 if k % 2 == 0 else 0))
    for i in range(16):                                 # bars 49-64
        bt, sym = t + 8 + 4 * i, ch[i % 4]
        if i % 4 == 0:
            tango.arrastre(p, bt, sym, vel=88)
        tango.sincopa332(p, bt, sym, vel=84 + i // 2, golpe_hit=(i % 2 == 1))
        tango.guitar_comp(p, bt, sym, vel=60, rhythm=(1.5, 3.0))
    # the trades: theme halved to a 4-bar cell, mordents arriving
    p.add('bnd', t + 8, CELL4, vel=72, vel_end=84, transpose=3, gate=0.7)
    p.add('vln', t + 24, CELL4, vel=84, vel_end=92, transpose=15, gate=0.7)
    for off, pitch in CELL4_HEADS:
        tango.mordent(p, 'vln', midi(pitch) + 15, t + 24 + off, 88)
    p.add('pno', t + 40, CELL4, vel=88, transpose=15, gate=0.7)
    p.add('pno', t + 40, CELL4, vel=78, transpose=3, gate=0.7)
    for off, pitch in CELL4_HEADS:
        tango.mordent(p, 'pno', midi(pitch) + 15, t + 40 + off, 86)
    p.add('bnd', t + 56, CELL4, vel=92, vel_end=98, transpose=3, gate=0.7)
    p.add('vln', t + 56, CELL4, vel=96, vel_end=102, transpose=15, gate=0.7)
    for off, pitch in CELL4_HEADS:
        tango.mordent(p, 'vln', midi(pitch) + 15, t + 56 + off, 96)
        tango.mordent(p, 'bnd', midi(pitch) + 3, t + 56 + off, 92)
    # bars 65-66: stop-time sincopa break, then air
    for at, sym, v, d in ((t + 72, 'Cm', 96, 0.5), (t + 72.5, 'Cm', 104, 1.0),
                          (t + 74, 'Cm', 94, 1.5), (t + 76, 'G7b9', 88, 2.0)):
        tango.stab(p, at, sym, vel=v, dur=d)
        root = 'C2' if sym == 'Cm' else 'G1'
        p.note('cb', at, root, d, vel=v, gate=0.9)
        p.add('pno', at, [([midi(root), midi(root) + 12], d)], vel=v - 4,
              gate=0.9)
        tango.golpe(p, at, 'wbh:e', vel=48)


# ----------------------------------------------- 5: apogee III — the last
def apogee3(p):
    t = S5
    p.tempo(t, 80, 'sospeso - the last apogee')
    p.mark('the last apogee', t)
    p.note('vln', t, 'Bb5', 8, vel=30)                  # a harmonic, alone
    tango.bellows(p, 'vln', t, t + 8, intensity=0.4)
    tango.sing(p, 'bnd', t + 4, GESTURE, vel=40, vel_end=50, transpose=6,
               breathe=1.1)
    # bar 70: the stall — the rise tries again and hangs
    p.add('bnd', t + 12, B('Eb5:e F5:e Gb5:h.', 1), vel=38, gate=0.98)
    p.cc('bnd', t + 12, 11, 90)
    p.hairpin('bnd', t + 13, t + 15.7, 90, 36)
    for i, sym in enumerate(['Ebm', 'Db', 'Ebm']):      # bars 68-70
        p.add('gtr', t + 4 + 4 * i, figures.arp(voicing(sym, 'G2', 'G3'),
              1.0, 4.0), vel=34, gate=0.9, swing=False)
    p.add('pno', t + 4, [(['Eb2', 'Eb3'], 8)], vel=34, gate=0.98)
    p.pedal('pno', t + 4, t + 16)
    # bars 71-72: invasion again — Bb pedal eighths, pp to f
    for k in range(16):
        at = t + 16 + 0.5 * k
        p.note('cb', at, 'Bb1', 0.3, vel=42 + 3 * k, swing=False)
        p.add('pno', at, [(['Bb2', 'Bb3'], 0.3)], vel=40 + 3 * k, swing=False)
    p.add('vln', t + 20, figures.trem('Bb4', 4.0, 0.5), vel=40, vel_end=70,
          gate=0.9)
    tango.golpe(p, t + 20, tango.R_('rim:e', 8), vel=36)


# --------------------------------------------- 6: perigee III — the heat
def perigee3(p):
    t = S6
    p.tempo(t, 144, 'feroce - the heat')
    p.mark('third perigee - the heat', t)
    tango.full_voice(p, t - 0.25)
    ch = ['Ebm', 'B', 'Db', 'Bb7']
    dstops = {'Ebm': ['Bb4', 'Gb5'], 'B': ['B4', 'F#5'],
              'Db': ['Ab4', 'F5'], 'Bb7': ['Ab4', 'D5']}
    near = 'Eb2'
    for i in range(4):                                  # bars 73-76: la yumba
        bt, sym = t + 4 * i, ch[i]
        near = tango.yumba(p, bt, sym, vel=94, near=near)
        v = voicing(sym, 'G3', 'A4')
        p.add('bnd', bt + 1.5, [(v, 0.5)], vel=76, gate=0.5)
        p.add('bnd', bt + 3.5, [(v, 0.5)], vel=70, gate=0.5)
        tango.guitar_comp(p, bt, sym, vel=66)
        if i % 2 == 1:
            tango.golpe(p, bt + 1.5, 'wbl:e', vel=36)
    # bars 77-82: the essence sequenced up the diminished ratchet
    seq = [('bnd', 6, t + 16, 88, ('Ebm', 'Bb7')),
           ('vln', 9, t + 24, 92, ('Gbm', 'Db7')),
           (None, 12, t + 32, 96, ('Am', 'E7'))]
    for inst, tr, at, v, syms in seq:
        insts = [inst] if inst else ['bnd', 'vln']
        for one in insts:
            p.add(one, at, CELL2, vel=v + (4 if one == 'vln' else 0),
                  vel_end=v + 6, transpose=tr, gate=0.75)
            for off, pitch in CELL2_HEADS:
                tango.mordent(p, one, midi(pitch) + tr, at + off, v)
        for j, sym in enumerate(syms):
            tango.sincopa332(p, at + 4 * j, sym, vel=88 + 2 * j)
            tango.guitar_comp(p, at + 4 * j, sym, vel=64)
    # bars 83-86: yumba returns ff, latigo crack, violin double stops
    tango.latigo(p, 'vln', 'Bb5', t + 40, vel=100)
    p.note('vln', t + 40, 'Bb5', 1.5, vel=102)
    for i in range(4):
        bt, sym = t + 40 + 4 * i, ch[i]
        near = tango.yumba(p, bt, sym, vel=102, near=near)
        tango.guitar_comp(p, bt, sym, vel=70)
        ds = dstops[sym]
        if not (i == 0):                                 # after the latigo bar
            p.add('vln', bt, [(ds, 1.5), (ds, 1.5), (ds, 1.0)], vel=92,
                  gate=0.6)
        p.add('bnd', bt, [(voicing(sym, 'G3', 'A4'), 1.5),
                          (voicing(sym, 'G3', 'A4'), 1.5),
                          (voicing(sym, 'G3', 'A4'), 1.0)], vel=86, gate=0.6)
    # bars 87-90: stretto over a Bb pedal — tumbling end over end
    for i in range(4):
        tango.sincopa332(p, t + 56 + 4 * i, 'Bb7', vel=96,
                         golpe_hit=(i % 2 == 1))
    p.add('pno', t + 56, CELL2, vel=98, transpose=18, gate=0.8)
    p.add('pno', t + 56, CELL2, vel=88, transpose=6, gate=0.8)
    p.add('vln', t + 58, CELL2, vel=98, transpose=9, gate=0.8)
    p.add('bnd', t + 60, CELL2, vel=98, transpose=12, gate=0.8)
    tango.golpe(p, t + 70, tango.R_('wbh:e wbl:e', 2), vel=46)
    # bars 91-96: the chromatic ratchet — dim7 planing, fragments in stretto
    frag = 'A4:s B4:s C5:s E5:s'
    roots = ['Gb1', 'G1', 'Ab1', 'A1', 'Bb1', 'B1']
    names = ['Gbdim7', 'Gdim7', 'Abdim7', 'Adim7', 'Bbdim7', 'Bdim7']
    for j in range(6):
        bt, r = t + 72 + 4 * j, midi(roots[j])
        for off, d in ((0.0, 1.5), (1.5, 1.5), (3.0, 1.0)):
            p.note('cb', bt + off, r, d, vel=98 + 2 * j, gate=0.7)
            p.add('pno', bt + off, [([r + 12, r + 24], d)], vel=96 + 2 * j,
                  gate=0.65)
        for off in (1.5, 3.0):
            tango.stab(p, bt + off, names[j], vel=94 + 2 * j, dur=0.75)
        inst, tr = ('bnd', 6 + j) if j % 2 == 0 else ('vln', 18 + j)
        p.add(inst, bt, frag, vel=100 + 2 * j, transpose=tr, gate=0.8)
        p.add(inst, bt + 2, frag, vel=102 + 2 * j, transpose=tr, gate=0.8)
        tango.golpe(p, bt, tango.R_('rim:e wbh:e', 2), vel=40 + 2 * j)
    tango.latigo(p, 'vln', 'E6', S7, vel=104, n=10)


# ------------------------------------------------------- 7: re-entry
def reentry(p):
    t = S7
    p.tempo(t, 152, 'toccata - re-entry')
    p.mark('re-entry', t)
    tango.full_voice(p, t - 0.25)
    cluster = voicing('E7b9', 'B3', 'A4')
    trem_lo = [(77, 0.25), (76, 0.25)] * 8              # F5-E5: the b9 burns
    trem_hi = [(89, 0.25), (88, 0.25)] * 8              # F6-E6
    for i in range(12):                                 # bars 97-108: hammer
        bt = t + 4 * i
        root = 28 if i % 2 == 0 else 40                 # E1 / E2
        for off, d in ((0.0, 1.5), (1.5, 1.5), (3.0, 1.0)):
            p.note('cb', bt + off, root, d, vel=100 + i, gate=0.7)
            p.add('pno', bt + off, [([28, 40], d)], vel=98 + i, gate=0.65)
        for off in (1.5, 3.0):
            p.add('pno', bt + off, [(cluster, 0.75)], vel=92 + i, gate=0.6)
        tango.guitar_comp(p, bt, 'E7b9', vel=72 + i, rhythm=(1.5, 3.0),
                          lo='B3', hi='A4')
        oct_pair = [64, 76] if i < 4 else ([76, 88] if i < 8 else [64, 76, 88])
        p.add('bnd', bt, [(oct_pair, 1.5), (oct_pair, 0.5), (oct_pair, 0.5),
                          (None, 0.5), (oct_pair, 1.0)],
              vel=88 + 2 * i, gate=0.6)
        if i >= 2:
            p.add('vln', bt, trem_lo if i < 8 else trem_hi, vel=74 + 3 * i,
                  gate=0.9)
        tango.golpe(p, bt, [('wbh', 1.5), ('wbh', 1.5), ('wbl', 1.0)],
                    vel=48 + 2 * i)
        if i >= 8:
            tango.golpe(p, bt, tango.R_('rim:e', 8), vel=40)
    # bars 109-112: the rocket — a unison climb that just stops
    def climb(start_pitch, at, unit, count, insts_tr):
        for k in range(count):
            for inst, tr in insts_tr:
                p.note(inst, at + unit * k, start_pitch + k + tr, unit * 0.9,
                       vel=min(120, 106 + k), swing=False)
    climb(52, t + 48, 0.5, 16, [('gtr', 0), ('bnd', 12), ('vln', 24),
                                ('pno', 0), ('pno', 12)])   # E3 up, 2 bars
    climb(68, t + 56, 0.25, 16, [('gtr', 0), ('bnd', 12), ('vln', 12),
                                 ('pno', 0), ('pno', 12)])  # G#4 up, 1 bar
    climb(84, t + 60, 0.25, 10, [('bnd', 0), ('vln', 0),
                                 ('pno', 12)])              # C6 up... and cut
    for off, d in ((48.0, 1.5), (49.5, 1.5), (51.0, 1.0), (52.0, 1.5),
                   (53.5, 1.5), (55.0, 1.0), (56.0, 1.5), (57.5, 1.5),
                   (59.0, 1.0), (60.0, 1.5), (61.5, 1.0)):
        p.note('cb', t + off, 28, d, vel=112, gate=0.7)     # gravity stays low
        tango.golpe(p, t + off, [('wbh', d)], vel=64)
    p.cue('loss of signal', t + 62.5)


# ------------------------------------------------- 8+9: the cut, and after
def after(p):
    p.tempo(S8, 76)
    p.mark('loss of signal', S7 + 62.5)
    t = S9
    p.tempo(t, 56, 'sospeso - weightless')
    p.mark('after - a trail of light', t)
    p.cue('no floor', t + 4)
    # the ping returns, slowing — a beacon the sky keeps for a minute
    for off, v in ((0, 48), (6, 44), (13, 40), (21, 36), (30, 32)):
        p.note('pno', t + off, 'E6', 0.5, vel=v, swing=False)
        p.pedal('pno', t + off, t + off + 4)
    # no double bass from here: no floor under it
    tango.sing(p, 'bnd', t + 4, PHRASE_A1, vel=48, vel_end=56, breathe=0.8)
    p.note('vln', t + 2, 'A6', 10, vel=34)
    tango.bellows(p, 'vln', t + 2, t + 12, intensity=0.3)
    p.note('vln', t + 18, 'E6', 8, vel=32)
    tango.bellows(p, 'vln', t + 18, t + 26, intensity=0.3)
    figures.harp_arp(p, 'gtr', ['A3', 'E4', 'B4', 'C5', 'E5'], t + 12,
                     step=0.5, vel=40)
    figures.harp_arp(p, 'gtr', ['A3', 'E4', 'C5', 'B5'], t + 24,
                     step=0.5, vel=36)
    # the chan-chan: two last blinks of a beacon
    for at, sym, v in ((t + 36, 'E7b9', 38), (t + 38, 'Am', 32)):
        p.add('pno', at, [(voicing(sym, 'G#3', 'F4'), 0.4)], vel=v, gate=1.0)
        p.add('gtr', at, [(voicing(sym, 'A3', 'B4'), 0.4)], vel=v - 2,
              gate=1.0)
        p.add('bnd', at, [(voicing(sym, 'G#3', 'F4'), 0.4)], vel=v - 4,
              gate=1.0)
        tango.golpe(p, at, 'rim:e', vel=20)
    p.note('pno', t + 41, 'E6', 0.5, vel=24, swing=False)   # one more ping
    p.pedal('pno', t + 41, END)


def build() -> Piece:
    p = Piece(quintet(), seed=1957,
              title='Perigee — a tango for a falling satellite')
    p.meter(0, 4, 4)
    telemetry(p)
    apogee1(p)
    perigee1(p)
    apogee2(p)
    perigee2(p)
    apogee3(p)
    perigee3(p)
    reentry(p)
    after(p)
    return p


def main():
    p = build()
    OUT.mkdir(exist_ok=True)
    ok = assess.report(p)
    p.write(str(OUT / 'perigee.mid'))
    p.write_marks(str(OUT / 'marks.json'))
    wav = OUT / 'perigee.wav'
    assess.pianoroll(p, str(OUT / 'roll.png'),
                     wav=str(wav) if wav.exists() else None)
    print()
    print(midi_report(str(OUT / 'perigee.mid')))
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
