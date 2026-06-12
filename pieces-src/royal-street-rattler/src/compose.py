#!/usr/bin/env python3
"""
ROYAL STREET RATTLER
A Dixieland jazz composition — F major / D minor / Bb major, 198 bpm, ~3:45.

The piece is data: melodies and solos are hand-composed event lists,
accompaniment (banjo, sousaphone, drums, clarinet obbligato, trombone
tailgate counterlines) is realized by small constrained generators that
follow the chord charts. Swing + humanization applied at write time.

Composed June 2026. The streetcar is the hook; the band is the city.
"""

import random
from midiutil import MIDIFile

RNG = random.Random(1924)

TEMPO = 198
SWING = 0.575          # offbeat eighths land at 57.5% of the beat (light, fast swing)
BEATS_PER_BAR = 4

# ---------------------------------------------------------------- tracks
TPT, CLA, TBN, SAX, TUBA, BANJO, DRUMS = range(7)
TRACK_INFO = [
    # (name, channel, GM program, CC7 vol, CC10 pan)
    ("Trumpet (lead)",      0, 56, 105, 64),
    ("Clarinet",            1, 71,  92, 84),
    ("Trombone (tailgate)", 2, 57, 100, 44),
    ("Tenor Sax",           3, 66, 104, 76),
    ("Sousaphone",          4, 58, 105, 60),
    ("Banjo",               5,105,  85, 50),
    ("Drums",               9,  0, 100, 64),
]
CH = {i: TRACK_INFO[i][1] for i in range(7)}

# GM percussion
KICK, SNARE, STICK, CRASH, CRASH2 = 36, 38, 37, 49, 57
WB_HI, WB_LO, COWBELL, TOM_LO, TOM_HI, RIDE = 76, 77, 56, 45, 50, 51

EVENTS = []   # dicts: tr, ch, p, t (beats), d, v, swing, post (post-swing offset)
BENDS = []    # (track, channel, t, value)

def ev(tr, p, t, d, v, swing=True, post=0.0):
    EVENTS.append(dict(tr=tr, ch=CH[tr], p=p, t=t, d=max(0.05, d),
                       v=max(20, min(127, int(v))), swing=swing, post=post))

# ---------------------------------------------------------------- pitch & chords
_PC = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def N(name):
    """'Bb4' -> 58.  C4 = 60."""
    pc = _PC[name[0]]; i = 1
    while name[i] in '#b':
        pc += 1 if name[i] == '#' else -1; i += 1
    return 12 * (int(name[i:]) + 1) + pc

QUAL = {'': (0,4,7), 'm': (0,3,7), '7': (0,4,7,10), 'm7': (0,3,7,10),
        'dim7': (0,3,6,9), '6': (0,4,7,9)}

def parse_chord(sym):
    """'F/C' -> (root_pc, bass_pc, [pcs]).  Bass defaults to root."""
    if '/' in sym:
        sym, bass = sym.split('/')
        bass_pc = _PC[bass[0]] + (1 if bass[1:] == '#' else -1 if bass[1:] == 'b' else 0)
    else:
        bass_pc = None
    root_pc = _PC[sym[0]]; i = 1
    while i < len(sym) and sym[i] in '#b':
        root_pc += 1 if sym[i] == '#' else -1; i += 1
    root_pc %= 12
    pcs = [(root_pc + iv) % 12 for iv in QUAL[sym[i:]]]
    return root_pc, (root_pc if bass_pc is None else bass_pc % 12), pcs

def chord_at(chart, bar, half=0):
    entry = chart[bar % len(chart)]
    if isinstance(entry, tuple):
        return entry[half]
    return entry

def fit(pc, lo, hi, near=None):
    """Place pitch-class in [lo,hi], optionally nearest to `near`."""
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc % 12]
    if not cands:
        return lo + ((pc - lo) % 12)
    if near is None:
        return cands[len(cands)//2]
    return min(cands, key=lambda p: abs(p - near))

# ---------------------------------------------------------------- charts
A_CHART = ['F','F','D7','D7','G7','G7','C7','C7',
           'F','F7','Bb','Bdim7','F/C','D7',('G7','C7'),'F']
A_CHART_TURN = A_CHART[:15] + [('F','C7')]
B_CHART = ['Dm','A7','Dm','A7','Dm','Dm/C','Bb7','A7',
           'Dm','D7','Gm','Gm','Dm',('Bb7','A7'),'Dm','C7']
TRIO = ['Bb','Bb','F7','F7','F7','F7','Bb','Bb7',
        'Eb','Edim7','Bb/F','G7','C7','F7','Bb','F7']
TRIO_FINAL = TRIO[:15] + ['Bb']

# ---------------------------------------------------------------- helpers
def bt(bar, beat):
    """(bar, 1-based beat) -> absolute beats."""
    return bar * BEATS_PER_BAR + (beat - 1.0)

def play(tr, phrases, bar0, base_vel, transpose=0, layback=0.0):
    """phrases: list of (bar, beat, dur, 'Name4' or midi, accent 0..2)."""
    for (bar, beat, dur, pitch, acc) in phrases:
        p = (N(pitch) if isinstance(pitch, str) else pitch) + transpose
        v = base_vel + (0, 11, 19)[acc] + RNG.randint(-4, 4)
        ev(tr, p, bt(bar0 + bar, beat) + layback, dur * 0.96, v)

def scoop(tr, t):
    """Pitch-bend scoop into a note starting at t (bend range ±2 semitones)."""
    BENDS.append((tr, CH[tr], t - 0.03, -2400))
    BENDS.append((tr, CH[tr], t + 0.10, -1100))
    BENDS.append((tr, CH[tr], t + 0.22, 0))

def smear_into(tr, bar, beat, target, n=3, vel=70, bar0=0):
    """Chromatic tailgate run-up into a downbeat note."""
    t0 = bt(bar0 + bar, beat)
    for i in range(n):
        ev(tr, target - (n - i), t0 - (n - i) * 0.17, 0.15, vel - 6 * (n - i),
           swing=False)

def trill(tr, p, t, d, v, step=2):
    """Alternating 16ths, ends on main pitch held."""
    n = int(d / 0.25) - 1
    for i in range(max(0, n)):
        ev(tr, p + (step if i % 2 else 0), t + i * 0.25, 0.22, v - 8 - (i % 2) * 6)
    ev(tr, p, t + max(0, n) * 0.25, d - max(0, n) * 0.25, v)

def roll(t, vel_end, n=5):
    """Snare press-roll crescendo into time t."""
    for i in range(n):
        ev(DRUMS, SNARE, t - (n - i) * 0.09, 0.07, int(vel_end * (0.35 + 0.1 * i)),
           swing=False)

# ---------------------------------------------------------------- rhythm section
def banjo(chart, bar0, nbars, vel=66, hot=False):
    for b in range(nbars):
        for beat in range(4):
            sym = chord_at(chart, b, half=0 if beat < 2 else 1)
            _, bass, pcs = parse_chord(sym)
            voicing = sorted({fit(pc, 50, 64, near=57) for pc in pcs})
            base = vel + (8 if beat % 2 else 0) + (6 if hot else 0)
            t = bt(bar0 + b, beat + 1)
            for i, p in enumerate(voicing):
                ev(BANJO, p, t, 0.4, base - i * 2 + RNG.randint(-3, 3),
                   post=i * 0.018)

def tuba(chart, bar0, nbars, vel=92, walking=False, next_sym=None):
    """Two-beat bass: root on 1, fifth on 3; quarter-note walkups at phrase ends.
    walking=True -> four-to-the-bar (out-chorus lift)."""
    LO, HI = 28, 46
    for b in range(nbars):
        sym1 = chord_at(chart, b, 0); sym2 = chord_at(chart, b, 1)
        root_pc, bass_pc, pcs = parse_chord(sym1)
        r2_pc = parse_chord(sym2)[1]
        nxt = next_sym if b == nbars - 1 else chord_at(chart, b + 1, 0)
        nxt_pc = parse_chord(nxt)[1] if nxt else bass_pc
        root = fit(bass_pc, LO, HI - 4)
        fifth_pc = (parse_chord(sym2)[0] + 7) % 12 if sym1 == sym2 else r2_pc
        is_walk_bar = (b % 4 == 3) and (nxt is not None)
        t = bt(bar0 + b, 1)
        if walking or is_walk_bar:
            target = fit(nxt_pc, LO, HI, near=root)
            steps = []
            cur = root
            diff = target - cur
            if abs(diff) <= 1 or diff == 0:
                steps = [cur, cur + 2, cur + 4 if diff <= 0 else cur - 1,
                         target + (1 if diff <= 0 else -1)]
            else:
                sgn = 1 if diff > 0 else -1
                mid = cur + (diff // 2)
                steps = [cur, fit(pcs[1 % len(pcs)], LO, HI, near=mid),
                         target - 2 * sgn, target - 1 * sgn]
            for i, p in enumerate(steps):
                pp = max(LO, min(HI, p))
                ev(TUBA, pp, t + i, 0.8, vel - 4 + i * 3 + RNG.randint(-3, 3))
        else:
            ev(TUBA, root, t, 0.85, vel + RNG.randint(-3, 3))
            ev(TUBA, fit(fifth_pc, LO, HI, near=root), t + 2, 0.85,
               vel - 6 + RNG.randint(-3, 3))

WB_PATTERNS = [
    [(1, WB_HI, 0), (1.75, WB_HI, -14), (2.5, WB_LO, 4), (3, WB_HI, -8), (4.5, WB_HI, -10)],
    [(1.5, WB_HI, -8), (2, WB_LO, 0), (3, WB_HI, -10), (3.5, WB_HI, -14), (4, WB_LO, 2)],
]

def drums(bar0, nbars, style='normal', crash_first=True):
    for b in range(nbars):
        t0 = bt(bar0 + b, 1)
        if style == 'silent':
            continue
        if crash_first and b == 0:
            ev(DRUMS, CRASH, t0, 1.0, 96)
        if style in ('normal', 'hot', 'trio', 'solo'):
            kv = dict(normal=80, hot=84, trio=76, solo=64)[style]
            ev(DRUMS, KICK, t0, 0.3, kv + RNG.randint(-3, 3))
            ev(DRUMS, KICK, t0 + 2, 0.3, kv - 5 + RNG.randint(-3, 3))
            if style == 'hot':
                ev(DRUMS, KICK, t0 + 1, 0.3, kv - 14)
                ev(DRUMS, KICK, t0 + 3, 0.3, kv - 14)
            sn = SNARE if style != 'solo' else STICK
            sv = dict(normal=72, hot=92, trio=66, solo=58)[style]
            if style in ('normal', 'trio') and RNG.random() < 0.3:
                roll(t0 + 1, sv)
            ev(DRUMS, sn, t0 + 1, 0.3, sv + RNG.randint(-4, 4))
            ev(DRUMS, sn, t0 + 3, 0.3, sv + 2 + RNG.randint(-4, 4))
            if style in ('trio', 'hot') or (style == 'normal' and RNG.random() < 0.45):
                for (beat, inst, dv) in WB_PATTERNS[b % 2]:
                    ev(DRUMS, inst, t0 + beat - 1, 0.2, 58 + dv + RNG.randint(-4, 4))
            if style == 'hot' and b % 4 == 3:
                roll(t0 + 4, 96)
        elif style == 'stoptime':
            ev(DRUMS, KICK, t0, 0.3, 88)
            ev(DRUMS, SNARE, t0, 0.3, 80)

def stab(chart_sym, bar, beat, dur=0.5, vel=88, bar0=0, who=(TBN, CLA), tuba_too=True):
    """Band chord hit (for stop-time, intros, tags)."""
    root_pc, bass_pc, pcs = parse_chord(chart_sym)
    t = bt(bar0 + bar, beat)
    if TBN in who:
        ev(TBN, fit(pcs[0], 45, 57), t, dur, vel)
    if CLA in who:
        ev(CLA, fit(pcs[1], 76, 88), t, dur, vel - 10)
    if TPT in who:
        ev(TPT, fit(pcs[2 % len(pcs)], 67, 79), t, dur, vel + 4)
    if SAX in who:
        ev(SAX, fit(pcs[1], 55, 67), t, dur, vel - 6)
    _, _, pcs2 = parse_chord(chart_sym)
    voicing = sorted({fit(pc, 50, 64, near=57) for pc in pcs2})
    for i, p in enumerate(voicing):
        ev(BANJO, p, t, min(dur, 0.5), vel - 14, post=i * 0.018)
    if tuba_too:
        ev(TUBA, fit(bass_pc, 28, 42), t, min(dur + 0.2, 1.0), vel + 2)
    ev(DRUMS, KICK, t, 0.3, vel)
    ev(DRUMS, SNARE, t, 0.3, vel - 12)

# ---------------------------------------------------------------- generators
def obbligato(chart, bar0, nbars, melody, anchor=79, energy=0.5, vel=72):
    """Clarinet filigree: runs when the lead holds, sustains above when it moves.
    melody: list of (bar, beat, dur, pitch) used to find holes & ceiling."""
    bar_notes = {}
    for (bar, beat, dur, pitch, *_ ) in melody:
        p = N(pitch) if isinstance(pitch, str) else pitch
        bar_notes.setdefault(bar, []).append((beat, dur, p))
    cur = anchor
    for b in range(nbars):
        notes = bar_notes.get(b, [])
        for half in (0, 1):
            h0, h1 = (1.0, 3.0) if half == 0 else (3.0, 5.0)
            moving = [n for n in notes if h0 <= n[0] < h1]
            ceiling = max([p for (_, _, p) in notes] + [anchor - 7])
            sym = chord_at(chart, b, half)
            _, _, pcs = parse_chord(sym)
            t = bt(bar0 + b, h0)
            if len(moving) >= 2:                      # lead is busy -> sustain or rest
                if half == 0 and RNG.random() < 0.75:
                    p = fit(pcs[RNG.choice((1, 2))], max(72, ceiling + 3), 91, near=cur + 2)
                    ev(CLA, p, t, 1.9, vel - 14 + RNG.randint(-4, 4))
                    cur = p
            else:                                     # lead holds -> run
                if RNG.random() < (0.55 + 0.4 * energy):
                    direction = 1 if cur < anchor else -1
                    if RNG.random() < 0.3:
                        direction = -direction
                    run_pcs = pcs * 3
                    p = fit(pcs[0], 72, 91, near=cur + direction * 3)
                    seq = []
                    for i in range(4):
                        seq.append(p)
                        nxt_pc = run_pcs[(run_pcs.index(p % 12) + 1) if p % 12 in run_pcs else 0]
                        step = direction * RNG.choice((3, 4, 5))
                        p = fit(pcs[(i + 1) % len(pcs)], 72, 91, near=p + step)
                    if RNG.random() < 0.35 * energy and seq[0] < 88:
                        ev(CLA, seq[0] + 1, t - 0.5, 0.45, vel - 18)  # chromatic approach
                    for i, p2 in enumerate(seq):
                        ev(CLA, p2, t + i * 0.5, 0.45, vel + (8 if i == 3 else 0)
                           + RNG.randint(-5, 5))
                    cur = seq[-1]

def tailgate(chart, bar0, nbars, vel=78, density=0.8):
    """Trombone counterline: voice-led guide tones, smears at phrase tops."""
    LO, HI = 43, 62
    cur = 50
    for b in range(nbars):
        sym = chord_at(chart, b, 0)
        root_pc, _, pcs = parse_chord(sym)
        guide = fit(RNG.choice((pcs[1], pcs[0], pcs[-1])), LO, HI, near=cur)
        cur = guide
        t = bt(bar0 + b, 1)
        if RNG.random() > density:
            continue
        if b % 4 == 0:
            smear_into(TBN, b, 1, guide, n=3, vel=vel - 4, bar0=bar0)
            ev(TBN, guide, t, 1.8, vel + 8)
            scoop(TBN, t)
            sym2 = chord_at(chart, b, 1)
            p2 = fit(parse_chord(sym2)[2][0], LO, HI, near=guide - 2)
            ev(TBN, p2, t + 2, 1.4, vel - 4)
            cur = p2
        elif b % 4 == 3:
            nxt = chord_at(chart, (b + 1) % len(chart), 0)
            tgt = fit(parse_chord(nxt)[2][1], LO, HI, near=cur)
            ev(TBN, guide, t, 1.4, vel)
            ev(TBN, tgt + 1, t + 2.5, 0.45, vel - 8)
            ev(TBN, tgt, t + 3.0, 0.9, vel + 4)
            cur = tgt
        else:
            ev(TBN, guide, t, 2.8, vel - 2)
            if RNG.random() < 0.5:
                p2 = fit(pcs[2 % len(pcs)], LO, HI, near=guide + 3)
                ev(TBN, p2, t + 3, 0.9, vel - 6)
                cur = p2

# ================================================================ SECTIONS
SECTIONS = []
_cursor = 0
def section(name, nbars):
    global _cursor
    SECTIONS.append((name, _cursor, nbars))
    start = _cursor
    _cursor += nbars
    return start

# ---------------------------------------------------------------- 1. INTRO (8)
s = section("Intro — streetcar bell & fanfare", 8)
# streetcar bell + woodblock rattle (the hook, stated by percussion first)
ev(DRUMS, COWBELL, bt(s, 1), 0.5, 96); ev(DRUMS, COWBELL, bt(s, 3), 0.5, 80)
ev(DRUMS, COWBELL, bt(s + 1, 1), 0.5, 88)
for i, beat in enumerate((1, 1.5, 2)):
    ev(DRUMS, WB_HI, bt(s + 1, beat), 0.2, 62 + i * 4)
ev(DRUMS, WB_LO, bt(s + 1, 2.5), 0.3, 84)
ev(DRUMS, COWBELL, bt(s + 1, 4), 0.4, 70)
# trumpet fanfare break (bars 3-4)
play(TPT, [
    (2, 1, .5, 'C4', 0), (2, 1.5, .5, 'F4', 0), (2, 2, .5, 'A4', 0),
    (2, 2.5, 1.5, 'C5', 2), (2, 4, .5, 'A4', 0), (2, 4.5, .5, 'C5', 0),
    (3, 1, 1, 'F5', 2), (3, 2, .5, 'C5', 0), (3, 2.5, .5, 'A4', 0),
    (3, 3, .5, 'Ab4', 1), (3, 3.5, 1.5, 'A4', 1),
], s, 98)
# band answers: turnaround hits (bars 5-6)
for (bar, beat, sym) in ((4, 1, 'F'), (4, 3, 'D7'), (5, 1, 'G7'), (5, 3, 'C7')):
    stab(sym, bar, beat, dur=0.6, vel=92, bar0=s, who=(TBN, CLA, TPT))
ev(DRUMS, CRASH, bt(s + 4, 1), 1, 92)
# unison break: all horns in octaves run up to the head (bars 7-8)
BREAK_LINE = [(6, 1 + i * 0.5, .5, p, 0) for i, p in
              enumerate(('C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'Bb4', 'B4'))]
BREAK_LINE += [(7, 1, 1.2, 'C5', 2)]
play(TPT, BREAK_LINE, s, 96)
play(CLA, BREAK_LINE, s, 84, transpose=12)
play(TBN, BREAK_LINE, s, 88, transpose=-12)
roll(bt(s + 7, 4.6), 100, n=6)

# ---------------------------------------------------------------- the A melody
def a_melody(pickup=True, turnaround_pickup=False):
    m = []
    if pickup:
        m += [(-1, 3.5, .5, 'C4', 0), (-1, 4, .5, 'D4', 0), (-1, 4.5, .5, 'E4', 1)]
    m += [
        # phrase 1 — the rattle
        (0, 1, .5, 'F4', 1), (0, 1.5, .5, 'F4', 0), (0, 2, .5, 'F4', 0),
        (0, 2.5, 1.5, 'A4', 2), (0, 4.5, .5, 'C5', 0),
        (1, 1, .5, 'D5', 1), (1, 1.5, .5, 'C5', 0), (1, 2, .5, 'A4', 0),
        (1, 2.5, 1.5, 'F4', 1),
        (2, 1, .5, 'A4', 1), (2, 1.5, .5, 'A4', 0), (2, 2, .5, 'A4', 0),
        (2, 2.5, 1.5, 'F#4', 2), (2, 4.5, .5, 'D4', 0),
        (3, 1, 1, 'A4', 1), (3, 2.5, .5, 'F#4', 0), (3, 3, 1.5, 'D5', 1),
        # phrase 2 — down the G7 hill, half cadence
        (4, 1, .5, 'D5', 1), (4, 1.5, .5, 'B4', 0), (4, 2, .5, 'G4', 0),
        (4, 2.5, 1.5, 'E4', 1),
        (5, 1, .5, 'F4', 0), (5, 1.5, .5, 'G4', 0), (5, 2, .5, 'A4', 0),
        (5, 2.5, 1.5, 'B4', 1), (5, 4.5, .5, 'C5', 0),
        (6, 1, .5, 'C5', 1), (6, 1.5, .5, 'C5', 0), (6, 2, .5, 'C5', 0),
        (6, 2.5, 1.5, 'Bb4', 2),
        (7, 1, .5, 'A4', 0), (7, 1.5, .5, 'G4', 0), (7, 2, 1, 'E4', 0),
        # phrase 3 — climb to the peak
        (8, 1, .5, 'F4', 1), (8, 1.5, .5, 'F4', 0), (8, 2, .5, 'F4', 0),
        (8, 2.5, 1.5, 'A4', 2), (8, 4.5, .5, 'C5', 0),
        (9, 1, .5, 'D5', 1), (9, 1.5, .5, 'C5', 0), (9, 2, .5, 'A4', 0),
        (9, 2.5, 1.5, 'Eb5', 2),
        (10, 1, .5, 'D5', 1), (10, 1.5, .5, 'Bb4', 0), (10, 2, .5, 'D5', 0),
        (10, 2.5, 1.5, 'F5', 2),
        (11, 1, .5, 'F5', 1), (11, 1.5, .5, 'D5', 0), (11, 2, .5, 'B4', 0),
        (11, 2.5, 1.5, 'Ab4', 1),
        # phrase 4 — strut home
        (12, 1, 1, 'A4', 1), (12, 3, .5, 'A4', 0), (12, 3.5, .5, 'Bb4', 0),
        (12, 4, .5, 'B4', 0), (12, 4.5, .5, 'C5', 1),
        (13, 1, .5, 'D5', 1), (13, 1.5, .5, 'D5', 0), (13, 2, .5, 'D5', 0),
        (13, 2.5, 1.5, 'C5', 2),
        (14, 1, .5, 'B4', 0), (14, 1.5, .5, 'D5', 0), (14, 2, .5, 'B4', 0),
        (14, 2.5, .5, 'G4', 0), (14, 3, .5, 'Bb4', 1), (14, 3.5, .5, 'G4', 0),
        (14, 4, .5, 'E4', 0),
        (15, 1, .5, 'G4', 0), (15, 1.5, .5, 'Ab4', 0), (15, 2, 1.6, 'A4', 1),
    ]
    if turnaround_pickup:
        m += [(15, 3.5, .5, 'C4', 0), (15, 4, .5, 'D4', 0), (15, 4.5, .5, 'E4', 1)]
    return m

# clarinet break fill in bar 8 of A strain (over the C7 half cadence)
A_CLAR_BREAK = [
    (7, 3, .5, 'E5', 1), (7, 3.5, .5, 'G5', 0), (7, 4, .5, 'Bb5', 0),
    (7, 4.5, .5, 'C6', 1),
]

# ---------------------------------------------------------------- 2. HEAD x2 (32)
s = section("Head 1 — The Strut (trumpet lead)", 16)
mel1 = a_melody(pickup=True, turnaround_pickup=True)
play(TPT, mel1, s, 97)
play(CLA, A_CLAR_BREAK, s, 86)
obbligato(A_CHART_TURN, s, 16, mel1 + A_CLAR_BREAK, anchor=79, energy=0.4)
tailgate(A_CHART_TURN, s, 16, vel=76, density=0.75)
banjo(A_CHART_TURN, s, 16)
tuba(A_CHART_TURN, s, 16, next_sym='F')
drums(s, 16, 'normal')

s = section("Head 2 — clarinet takes the lead", 16)
mel2 = a_melody(pickup=False)
play(CLA, mel2, s, 88, transpose=12)
play(CLA, [(7, 3, .5, 'E5', 1), (7, 3.5, .5, 'G5', 0), (7, 4, .5, 'Bb5', 0),
           (7, 4.5, .5, 'C6', 1)], s, 86)
# trumpet sits out 8 bars, then punches the rattle rhythm on guide tones
for (bar, sym, pname) in ((8, 'F', 'C5'), (10, 'Bb', 'D5'), (12, 'F/C', 'C5'),
                          (13, 'D7', 'D5')):
    play(TPT, [(bar, 1, .5, pname, 1), (bar, 1.5, .5, pname, 0),
               (bar, 2, .5, pname, 0), (bar, 2.5, 1.5, pname, 1)], s, 88)
# 15 bars only: the trombonist breathes before his B-strain pickup
tailgate(A_CHART, s, 15, vel=78, density=0.85)
banjo(A_CHART, s, 16)
tuba(A_CHART, s, 16, next_sym='Dm')
drums(s, 16, 'normal', crash_first=False)

# ---------------------------------------------------------------- 3. B STRAIN (16)
s = section("B strain — Balcony Shadows (trombone)", 16)
TBN_B = [
    (-1, 4, .5, 'A2', 0), (-1, 4.5, .5, 'C3', 0),
    (0, 1, 1.5, 'D3', 1), (0, 2.5, .5, 'F3', 0), (0, 3, 1, 'A3', 1), (0, 4, 1, 'F3', 0),
    (1, 1, 2, 'E3', 1), (1, 3, 1, 'C#3', 0), (1, 4, 1, 'A2', 0),
    (2, 1, 1.5, 'D3', 1), (2, 2.5, .5, 'F3', 0), (2, 3, 1, 'A3', 0),
    (2, 4, .5, 'G3', 0), (2, 4.5, .5, 'F3', 0),
    (3, 1, 3, 'E3', 1), (3, 4, .5, 'E3', 0), (3, 4.5, .5, 'G3', 0),
    (4, 1, .5, 'A3', 1), (4, 1.5, .5, 'A3', 0), (4, 2, .5, 'A3', 0),
    (4, 2.5, 1.5, 'F3', 1),                       # the rattle, in the cellar
    (5, 1, .5, 'A3', 0), (5, 1.5, .5, 'G3', 0), (5, 2, .5, 'F3', 0),
    (5, 2.5, 1.5, 'E3', 0),
    (6, 1, .5, 'D3', 0), (6, 1.5, .5, 'F3', 0), (6, 2, .5, 'Ab3', 1),
    (6, 2.5, 1.5, 'Bb3', 2),
    (7, 1, 1, 'A3', 1), (7, 2, .5, 'G3', 0), (7, 2.5, .5, 'E3', 0), (7, 3, 1, 'C#3', 1),
    (8, 1, 1.5, 'D3', 1), (8, 2.5, .5, 'F3', 0), (8, 3, 1, 'A3', 0), (8, 4, 1, 'C4', 1),
    (9, 1, 2, 'D4', 2), (9, 3, .5, 'C4', 0), (9, 3.5, .5, 'A3', 0),
    (10, 1, 1.5, 'Bb3', 1), (10, 2.5, .5, 'G3', 0), (10, 3, 1, 'D3', 0), (10, 4, 1, 'G3', 0),
    (11, 1, .5, 'Bb3', 0), (11, 1.5, .5, 'Bb3', 0), (11, 2, .5, 'Bb3', 0),
    (11, 2.5, 1.5, 'G3', 1),
    (12, 1, 1, 'F3', 1), (12, 2, .5, 'E3', 0), (12, 2.5, .5, 'D3', 0), (12, 3, 2, 'A3', 1),
    (13, 1, 1, 'Bb3', 1), (13, 2, .5, 'Ab3', 0), (13, 2.5, .5, 'F3', 0), (13, 3, 1.5, 'E3', 1),
    (14, 1, 1, 'D3', 1), (14, 2, .5, 'F3', 0), (14, 2.5, .5, 'A3', 0),
    (14, 3, .5, 'D4', 1), (14, 3.5, .5, 'C4', 0), (14, 4, .5, 'A3', 0),
    (15, 1, 1.5, 'G3', 1), (15, 2.5, .5, 'E3', 0), (15, 3, 1, 'C3', 0),
    (15, 4, .5, 'Bb2', 0), (15, 4.5, .5, 'C3', 0),
]
play(TBN, TBN_B, s, 92)
scoop(TBN, bt(s + 1, 1)); scoop(TBN, bt(s + 3, 1)); scoop(TBN, bt(s + 9, 1))
smear_into(TBN, 9, 1, N('D4'), n=4, vel=80, bar0=s)
# clarinet shadows: echoes in the trombone's breathing room (high, plaintive)
play(CLA, [
    (1, 3.5, .5, 'A5', 0), (1, 4, .5, 'G5', 0), (1, 4.5, .5, 'E5', 0),
    (3, 1, 2, 'A5', 0),
    (5, 3.5, .5, 'A5', 0), (5, 4, .5, 'G5', 0), (5, 4.5, .5, 'F5', 0),
    (7, 1, 1.5, 'G5', 1), (7, 3, 1, 'E5', 0),
    (9, 1, 2, 'F#5', 1), (9, 3, 1, 'D5', 0),
    (12, 3, .5, 'D5', 0), (12, 3.5, .5, 'E5', 0), (12, 4, .5, 'F5', 0), (12, 4.5, .5, 'A5', 0),
    (15, 1, 1.5, 'E5', 1), (15, 3, 1.5, 'C5', 0),
], s, 78)
# trumpet: tight backbeat punches in the second half only
for bar in (9, 11, 13):
    sym = chord_at(B_CHART, bar, 0)
    p = fit(parse_chord(sym)[2][1], 67, 76)
    ev(TPT, p, bt(s + bar, 2.5), 0.4, 84)
    ev(TPT, p, bt(s + bar, 4.5), 0.4, 80)
banjo(B_CHART, s, 16)
tuba(B_CHART, s, 16, next_sym='F')
drums(s, 16, 'normal')

# ---------------------------------------------------------------- 4. HEAD 3 (16)
s = section("Head 3 — The Strut returns", 16)
mel3 = a_melody(pickup=True)
play(TPT, mel3, s, 100)
play(CLA, A_CLAR_BREAK, s, 88)
obbligato(A_CHART, s, 16, mel3 + A_CLAR_BREAK, anchor=81, energy=0.6, vel=74)
tailgate(A_CHART, s, 16, vel=80, density=0.85)
banjo(A_CHART, s, 16, vel=70)
tuba(A_CHART, s, 16, next_sym='F7')
drums(s, 16, 'normal')

# ---------------------------------------------------------------- 5. MODULATION (4)
s = section("Modulation — F7 hits, clarinet break", 4)
for (bar, beats) in ((0, (1, 1.5, 2)), (1, (1, 1.5, 2))):
    for i, beat in enumerate(beats):
        stab('F7', bar, beat, dur=0.4 if i < 2 else 1.2, vel=90 + i * 3, bar0=s,
             who=(TBN, CLA, TPT))
ev(DRUMS, CRASH, bt(s, 1), 1, 90)
# 2-bar clarinet break, alone, cascading into Bb
play(CLA, [
    (2, 1, .5, 'F6', 2), (2, 1.5, .5, 'Eb6', 0), (2, 2, .5, 'C6', 0),
    (2, 2.5, .5, 'A5', 0), (2, 3, .5, 'F5', 0), (2, 3.5, .5, 'Eb5', 0),
    (2, 4, .5, 'C5', 0), (2, 4.5, .5, 'A4', 0),
    (3, 1, 1, 'Bb4', 1), (3, 2.5, .5, 'Bb4', 0), (3, 3, .5, 'C5', 0),
    (3, 3.5, .5, 'D5', 0), (3, 4, .5, 'F5', 0), (3, 4.5, .5, 'G5', 0),
], s, 88)

# ---------------------------------------------------------------- the TRIO melody
TRIO_MEL = [
    (-1, 4, .5, 'F4', 0), (-1, 4.5, .5, 'G4', 0),
    (0, 1, 1.5, 'D5', 1), (0, 2.5, .5, 'C5', 0), (0, 3, 1, 'Bb4', 0), (0, 4, 1, 'G4', 0),
    (1, 1, 2.5, 'F4', 1), (1, 4, .5, 'F4', 0), (1, 4.5, .5, 'G4', 0),
    (2, 1, 1.5, 'A4', 1), (2, 2.5, .5, 'G4', 0), (2, 3, 1, 'F4', 0), (2, 4, 1, 'C5', 1),
    (3, 1, 2, 'C5', 1), (3, 3.5, .5, 'Bb4', 0), (3, 4, .5, 'A4', 0), (3, 4.5, .5, 'G4', 0),
    (4, 1, 1.5, 'A4', 0), (4, 2.5, .5, 'F4', 0), (4, 3, 1, 'Eb5', 1), (4, 4, 1, 'C5', 0),
    (5, 1, 2, 'C5', 0), (5, 3, .5, 'A4', 0), (5, 3.5, .5, 'F4', 0),
    (5, 4, .5, 'G4', 0), (5, 4.5, .5, 'A4', 0),
    (6, 1, 1.5, 'Bb4', 1), (6, 2.5, .5, 'D5', 0), (6, 3, 2, 'F5', 1),
    (7, 1, .5, 'F5', 0), (7, 1.5, .5, 'D5', 0), (7, 2, .5, 'Bb4', 0),
    (7, 2.5, 1.5, 'Ab4', 2),
    (8, 1, 1.5, 'G4', 1), (8, 2.5, .5, 'Bb4', 0), (8, 3, 1, 'Eb5', 1), (8, 4, 1, 'Bb4', 0),
    (9, 1, 1.5, 'Db5', 1), (9, 2.5, .5, 'Bb4', 0), (9, 3, 1, 'G4', 0), (9, 4, 1, 'E4', 0),
    (10, 1, 1, 'F4', 0), (10, 2, .5, 'Bb4', 0), (10, 2.5, .5, 'D5', 0), (10, 3, 1.5, 'F5', 1),
    (11, 1, .5, 'D5', 0), (11, 1.5, .5, 'B4', 1), (11, 2, .5, 'G4', 0),
    (11, 2.5, 1.5, 'F5', 2),
    (12, 1, .5, 'E5', 1), (12, 1.5, .5, 'C5', 0), (12, 2, .5, 'G4', 0),
    (12, 2.5, 1.5, 'Bb4', 1),
    (13, 1, .5, 'A4', 0), (13, 1.5, .5, 'C5', 0), (13, 2, .5, 'Eb5', 0),
    (13, 2.5, 1.5, 'C5', 1),
    (14, 1, .5, 'Bb4', 1), (14, 1.5, .5, 'Bb4', 0), (14, 2, .5, 'Bb4', 0),
    (14, 2.5, 1.5, 'D5', 2),                       # rattle callback!
    (15, 1, 1, 'C5', 0), (15, 2, .5, 'A4', 0), (15, 2.5, .5, 'F4', 0), (15, 3, 1, 'G4', 0),
]

# ---------------------------------------------------------------- 6. TRIO THEME (16)
s = section("Trio — Out to the River", 16)
play(TPT, TRIO_MEL, s, 94)
obbligato(TRIO, s, 16, TRIO_MEL, anchor=80, energy=0.45, vel=70)
tailgate(TRIO, s, 16, vel=72, density=0.7)
banjo(TRIO, s, 16, vel=62)
tuba(TRIO, s, 16, vel=88, next_sym='Bb')
drums(s, 16, 'trio')

# ---------------------------------------------------------------- 7. CLARINET SOLO (16)
s = section("Clarinet solo", 16)
play(CLA, [
    (-1, 3.5, .5, 'Bb4', 0), (-1, 4, .5, 'D5', 0), (-1, 4.5, .5, 'F5', 0),
    (0, 1, .5, 'Bb5', 1), (0, 1.5, .5, 'A5', 0), (0, 2, .5, 'Bb5', 0),
    (0, 2.5, 1, 'F5', 1), (0, 4, .5, 'D5', 0), (0, 4.5, .5, 'F5', 0),
    (1, 1, 1.5, 'G5', 1), (1, 2.5, .5, 'F5', 0), (1, 3, .5, 'D5', 0),
    (1, 3.5, .5, 'Bb4', 0), (1, 4, 1, 'C5', 0),
    (2, 1, 1, 'C5', 0), (2, 2, .5, 'Eb5', 1), (2, 2.5, .5, 'D5', 0),
    (2, 3, .5, 'C5', 0), (2, 3.5, .5, 'A4', 0), (2, 4, 1, 'F5', 1),
    (3, 1, .5, 'E5', 0), (3, 1.5, .5, 'Eb5', 0), (3, 2, .5, 'D5', 0),
    (3, 2.5, .5, 'Db5', 0), (3, 3, 1, 'C5', 1), (3, 4, .5, 'A4', 0), (3, 4.5, .5, 'C5', 0),
    (4, 1, .5, 'Eb5', 0), (4, 1.5, .5, 'C5', 0), (4, 2, .5, 'A4', 0),
    (4, 2.5, 1, 'F5', 1), (4, 4, .5, 'Eb5', 0), (4, 4.5, .5, 'C5', 0),
    (5, 1, .5, 'A5', 1), (5, 1.5, .5, 'G5', 0), (5, 2, .5, 'F5', 0),
    (5, 2.5, .5, 'Eb5', 0), (5, 3, .5, 'D5', 0), (5, 3.5, .5, 'C5', 0),
    (5, 4, .5, 'Bb4', 0), (5, 4.5, .5, 'A4', 0),
    (6, 1, .5, 'Bb4', 0), (6, 1.5, .5, 'D5', 0), (6, 2, .5, 'F5', 0),
    (6, 2.5, 1.5, 'Bb5', 2),                       # the rip
    (7, 1, .5, 'Bb5', 0), (7, 1.5, .5, 'Ab5', 1), (7, 2, .5, 'F5', 0),
    (7, 2.5, .5, 'D5', 0), (7, 3, 1, 'F5', 0), (7, 4, .5, 'Eb5', 0), (7, 4.5, .5, 'D5', 0),
], s, 88)
trill(CLA, N('Bb5'), bt(s + 8, 1), 2.0, 88, step=2)
play(CLA, [
    (8, 3, .5, 'G5', 0), (8, 3.5, .5, 'Eb5', 0), (8, 4, .5, 'Bb4', 0), (8, 4.5, .5, 'Db5', 0),
    (9, 1, .5, 'E5', 0), (9, 1.5, .5, 'G5', 0), (9, 2, .5, 'Bb5', 0),
    (9, 2.5, .5, 'Db6', 1), (9, 3, 1, 'C6', 0), (9, 4, .5, 'Bb5', 0), (9, 4.5, .5, 'G5', 0),
    (10, 1, 1, 'F5', 0), (10, 2, .5, 'D5', 0), (10, 2.5, .5, 'F5', 0),
    (10, 3, .5, 'Bb5', 0), (10, 3.5, 1.5, 'D6', 1),
    (11, 1, 1.5, 'D6', 1), (11, 2.5, .5, 'B5', 0), (11, 3, .5, 'G5', 0),
    (11, 3.5, .5, 'F5', 0), (11, 4, .5, 'D5', 0), (11, 4.5, .5, 'B4', 0),
    (12, 1, .5, 'C5', 0), (12, 1.5, .5, 'E5', 0), (12, 2, .5, 'G5', 0),
    (12, 2.5, .5, 'Bb5', 1), (12, 3, 1, 'A5', 0), (12, 4, .5, 'G5', 0), (12, 4.5, .5, 'E5', 0),
    (13, 1, .5, 'F5', 0), (13, 1.5, .5, 'Eb5', 0), (13, 2, .5, 'C5', 0),
    (13, 2.5, .5, 'A4', 0), (13, 3, .5, 'C5', 0), (13, 3.5, .5, 'Eb5', 0),
    (13, 4, .5, 'F5', 0), (13, 4.5, .5, 'A5', 0),
    (14, 1, .5, 'F5', 1), (14, 1.5, .5, 'F5', 0), (14, 2, .5, 'F5', 0),
    (14, 2.5, 1.5, 'D5', 1),                       # rattle quote
    (15, 1, .5, 'Bb4', 0), (15, 1.5, .5, 'C5', 0), (15, 2, .5, 'D5', 0),
    (15, 2.5, .5, 'F5', 0), (15, 3, 1.5, 'Bb5', 1),
], s, 88)
banjo(TRIO, s, 16, vel=60)
tuba(TRIO, s, 16, vel=86, next_sym='Bb')
drums(s, 16, 'solo', crash_first=False)

# ---------------------------------------------------------------- 8. SAX SOLO (16)
s = section("Tenor sax solo", 16)
play(SAX, [
    (-1, 4, .5, 'F3', 0), (-1, 4.5, .5, 'Bb3', 0),
    (0, 1, 2.5, 'D4', 1), (0, 4, .5, 'F4', 0), (0, 4.5, .5, 'D4', 0),
    (1, 1, .5, 'F4', 1), (1, 1.5, .5, 'D4', 0), (1, 2, 1.5, 'Bb3', 0),
    (1, 4, .5, 'Ab3', 1), (1, 4.5, .5, 'Bb3', 0),
    (2, 1, 2, 'C4', 1), (2, 3, .5, 'Eb4', 0), (2, 3.5, .5, 'C4', 0), (2, 4, 1, 'A3', 0),
    (3, 1, .5, 'F3', 0), (3, 1.5, .5, 'A3', 0), (3, 2, .5, 'C4', 0), (3, 2.5, 1.5, 'Eb4', 1),
    (4, 1, 1, 'C4', 0), (4, 2.5, .5, 'C4', 0), (4, 3, .5, 'Db4', 1),
    (4, 3.5, .5, 'C4', 0), (4, 4, .5, 'Bb3', 0), (4, 4.5, .5, 'A3', 0),
    (5, 1, 2.5, 'G3', 0), (5, 3.5, .5, 'A3', 0), (5, 4, .5, 'C4', 0), (5, 4.5, .5, 'Eb4', 0),
    (6, 1, 1.5, 'D4', 1), (6, 2.5, .5, 'Bb3', 0), (6, 3, 1.5, 'F4', 1),
    (7, 1, .5, 'F4', 0), (7, 1.5, .5, 'Ab4', 2), (7, 2, 1.5, 'F4', 0),
    (7, 4, .5, 'D4', 0), (7, 4.5, .5, 'F4', 0),
    (8, 1, 2, 'G4', 1), (8, 3, .5, 'Bb4', 1), (8, 3.5, .5, 'G4', 0), (8, 4, 1, 'Eb4', 0),
    (9, 1, 1, 'E4', 0), (9, 2, .5, 'Db4', 0), (9, 2.5, .5, 'Bb3', 0), (9, 3, 1.5, 'G3', 0),
    (10, 1, .5, 'Bb3', 0), (10, 1.5, .5, 'D4', 0), (10, 2, 1.5, 'F4', 1),
    (10, 4, .5, 'D4', 0), (10, 4.5, .5, 'Bb3', 0),
    (11, 1, 1, 'B3', 1), (11, 2, .5, 'D4', 0), (11, 2.5, .5, 'F4', 0), (11, 3, 1.5, 'G4', 1),
    (12, 1, .5, 'G4', 1), (12, 1.5, .5, 'E4', 0), (12, 2, .5, 'G4', 0),
    (12, 2.5, .5, 'E4', 0), (12, 3, 1, 'C4', 0), (12, 4, .5, 'Bb3', 0),
    (13, 1, .5, 'A3', 0), (13, 1.5, .5, 'C4', 0), (13, 2, .5, 'Eb4', 0), (13, 2.5, 1.5, 'C4', 1),
    (14, 1, .5, 'Bb3', 1), (14, 1.5, .5, 'Bb3', 0), (14, 2, .5, 'Bb3', 0),
    (14, 2.5, 1.5, 'D4', 1),                       # rattle, smoky
    (15, 1, 1, 'F4', 1), (15, 2, .5, 'Eb4', 0), (15, 2.5, .5, 'D4', 0),
    (15, 3, .5, 'C4', 0), (15, 3.5, .5, 'Bb3', 0), (15, 4, 1, 'G3', 0),
], s, 96, layback=0.035)
# horn pads behind the back half of the sax story
for b in range(8, 16):
    sym = chord_at(TRIO, b, 0)
    _, _, pcs = parse_chord(sym)
    t = bt(s + b, 1)
    ev(TBN, fit(pcs[0], 45, 55), t, 3.8, 48)
    ev(TPT, fit(pcs[1], 64, 74), t, 3.8, 44)
    ev(CLA, fit(pcs[2 % len(pcs)], 76, 86), t, 3.8, 40)
banjo(TRIO, s, 16, vel=60)
tuba(TRIO, s, 16, vel=86, next_sym='Bb')
drums(s, 16, 'solo', crash_first=False)

# ---------------------------------------------------------------- 9. TRUMPET SOLO (16)
s = section("Trumpet solo — stop-time, then full band", 16)
play(TPT, [
    (0, 1.5, .5, 'F5', 2), (0, 2, .5, 'D5', 0), (0, 2.5, .5, 'Bb4', 0), (0, 3, 1.5, 'C5', 1),
    (1, 2, .5, 'C5', 0), (1, 2.5, .5, 'D5', 0), (1, 3, .5, 'C5', 0),
    (1, 3.5, .5, 'A4', 0), (1, 4, 1, 'F4', 0),
    (2, 1.5, 1, 'A4', 1), (2, 3, .5, 'C5', 0), (2, 3.5, .5, 'Eb5', 1), (2, 4, 1, 'C5', 0),
    (3, 2, .5, 'F5', 1), (3, 2.5, .5, 'Eb5', 0), (3, 3, .5, 'C5', 0),
    (3, 3.5, .5, 'A4', 0), (3, 4, .5, 'G4', 0), (3, 4.5, .5, 'F4', 0),
    (4, 1.5, .5, 'C5', 0), (4, 2, .5, 'C5', 0), (4, 2.5, .5, 'C5', 0), (4, 3, 1.5, 'A4', 1),
    (5, 2, 1, 'Eb5', 1), (5, 3.5, .5, 'C5', 0), (5, 4, .5, 'A4', 0), (5, 4.5, .5, 'C5', 0),
    (6, 1.5, .5, 'D5', 0), (6, 2, .5, 'F5', 1), (6, 2.5, 1, 'D5', 0),
    (6, 4, .5, 'Bb4', 0), (6, 4.5, .5, 'D5', 0),
    (7, 1, .5, 'F5', 1), (7, 1.5, .5, 'Ab5', 2), (7, 2, 2, 'F5', 1),
    # full band returns
    (8, 1, 1.5, 'G5', 2), (8, 2.5, .5, 'Eb5', 0), (8, 3, 1, 'Bb4', 0), (8, 4, 1, 'Eb5', 0),
    (9, 1, .5, 'E5', 0), (9, 1.5, .5, 'G5', 1), (9, 2, 1, 'G5', 0), (9, 3, 1, 'Db5', 0),
    (9, 4, .5, 'C5', 0), (9, 4.5, .5, 'Bb4', 0),
    (10, 1, .5, 'D5', 0), (10, 1.5, .5, 'D5', 0), (10, 2, .5, 'D5', 0), (10, 2.5, 1.5, 'F5', 1),
    (11, 1, .5, 'F5', 0), (11, 1.5, .5, 'D5', 0), (11, 2, .5, 'B4', 0), (11, 2.5, 1.5, 'G5', 2),
    (12, 1, 2, 'A5', 2), (12, 3, .5, 'G5', 0), (12, 3.5, .5, 'E5', 0), (12, 4, .5, 'C5', 0),
    (13, 1, .5, 'Eb5', 1), (13, 1.5, .5, 'C5', 0), (13, 2, .5, 'A4', 0),
    (13, 2.5, .5, 'C5', 0), (13, 3, .5, 'Eb5', 0), (13, 3.5, .5, 'F5', 0), (13, 4, .5, 'G5', 1),
    (14, 1, 2, 'Bb5', 2), (14, 3, .5, 'G5', 0), (14, 3.5, .5, 'F5', 0), (14, 4, .5, 'D5', 0),
    (15, 1, .5, 'F5', 0), (15, 1.5, .5, 'Eb5', 0), (15, 2, .5, 'D5', 0),
    (15, 2.5, .5, 'C5', 0), (15, 3, 1, 'Bb4', 1),
], s, 102)
scoop(TPT, bt(s + 12, 1)); scoop(TPT, bt(s + 14, 1))
# stop-time: band hits beat 1 only, bars 1-8
for b in range(8):
    stab(chord_at(TRIO, b, 0), b, 1, dur=0.5, vel=84, bar0=s, who=(TBN, CLA))
    drums(s + b, 1, 'stoptime', crash_first=False)
# bars 9-16: full rhythm + backing riff in 6ths (clarinet over trombone)
banjo(TRIO, s + 8, 8, vel=64)
tuba([TRIO[i] for i in range(8, 16)], s + 8, 8, vel=90, next_sym='Bb')
drums(s + 8, 8, 'normal')
for b in range(8, 16):
    sym = chord_at(TRIO, b, 0)
    _, _, pcs = parse_chord(sym)
    for (beat, dur) in ((2.5, 0.4), (4, 0.4)):
        ev(TBN, fit(pcs[0], 45, 57), bt(s + b, beat), dur, 68)
        ev(CLA, fit(pcs[1], 74, 84), bt(s + b, beat), dur, 60)

# ---------------------------------------------------------------- 10. DRUM BREAK (4)
s = section("Drum break — the rattle as a drum solo", 4)
ev(DRUMS, SNARE, bt(s, 1), .2, 96); ev(DRUMS, SNARE, bt(s, 1.5), .2, 78)
ev(DRUMS, SNARE, bt(s, 2), .2, 84); ev(DRUMS, WB_LO, bt(s, 2.5), .3, 96)
ev(DRUMS, WB_HI, bt(s, 3.5), .2, 70); ev(DRUMS, COWBELL, bt(s, 4), .3, 88)
ev(DRUMS, COWBELL, bt(s, 4.5), .3, 72)
ev(DRUMS, WB_HI, bt(s + 1, 1), .2, 80); ev(DRUMS, WB_HI, bt(s + 1, 1.5), .2, 66)
ev(DRUMS, WB_LO, bt(s + 1, 2), .2, 88); ev(DRUMS, SNARE, bt(s + 1, 2.5), .2, 92)
ev(DRUMS, KICK, bt(s + 1, 3), .3, 86); ev(DRUMS, SNARE, bt(s + 1, 4), .2, 70)
ev(DRUMS, SNARE, bt(s + 1, 4.5), .2, 84)
ev(DRUMS, TOM_HI, bt(s + 2, 1), .2, 88); ev(DRUMS, TOM_HI, bt(s + 2, 1.5), .2, 72)
ev(DRUMS, TOM_LO, bt(s + 2, 2), .2, 90); ev(DRUMS, SNARE, bt(s + 2, 2.5), .2, 80)
ev(DRUMS, TOM_HI, bt(s + 2, 3), .2, 84); ev(DRUMS, TOM_LO, bt(s + 2, 3.5), .2, 88)
ev(DRUMS, KICK, bt(s + 2, 4), .3, 92); ev(DRUMS, COWBELL, bt(s + 2, 4.5), .3, 80)
for i in range(8):                                  # bar 4: roll up the hill
    ev(DRUMS, SNARE, bt(s + 3, 1) + i * 0.25, .2, 52 + i * 6, swing=False)
ev(DRUMS, SNARE, bt(s + 3, 3), .2, 100)
ev(DRUMS, WB_LO, bt(s + 3, 3.5), .2, 92)
ev(DRUMS, SNARE, bt(s + 3, 4), .2, 104); ev(DRUMS, SNARE, bt(s + 3, 4.5), .2, 110)

# ---------------------------------------------------------------- 11. SHOUT CHORUS (16)
s = section("Shout chorus — band riffs", 16)
def riff_bars(bar):
    """Two-bar riff mapped onto the chord of the moment."""
    sym_a = chord_at(TRIO, bar, 0); sym_b = chord_at(TRIO, bar + 1, 0)
    _, _, pa = parse_chord(sym_a); _, _, pb = parse_chord(sym_b)
    third_a = fit(pa[1], 70, 80); fifth_a = fit(pa[2 % len(pa)], 72, 82, near=third_a + 4)
    root_b = fit(pb[0], 70, 80, near=third_a)
    tpt = [(bar, 1.5, .5, third_a, 1), (bar, 2.5, .5, third_a, 1), (bar, 3.5, 1.0, fifth_a, 2),
           (bar + 1, 1.5, .5, fifth_a, 1), (bar + 1, 2.5, .5, third_a, 0),
           (bar + 1, 3, 1.0, root_b, 1)]
    for (b2, beat, dur, p, acc) in tpt:
        v = 100 + (0, 8, 14)[acc]
        ev(TPT, p, bt(s + b2, beat), dur, v)
        cla_p = fit(pa[2 % len(pa)] if p == third_a else pa[1], p + 5, p + 16)
        ev(CLA, cla_p, bt(s + b2, beat), dur, v - 18)
    # trombone answers in the gap (beat 4+ of second bar)
    _, _, pn = parse_chord(chord_at(TRIO, (bar + 2) % 16, 0))
    tgt = fit(pn[0], 45, 57)
    ev(TBN, tgt + 1, bt(s + bar + 1, 4), 0.45, 84)
    ev(TBN, tgt, bt(s + bar + 1, 4.5), 0.5, 92)
for bar in range(0, 14, 2):
    riff_bars(bar)
# bars 15-16: full-band unison rattle launches the out chorus
for tr, base, vel in ((TPT, 'Bb4', 104), (CLA, 'Bb5', 88), (TBN, 'Bb3', 94), (SAX, 'Bb3', 90)):
    play(tr, [(14, 1, .5, base, 1), (14, 1.5, .5, base, 0), (14, 2, .5, base, 0),
              (14, 2.5, 1.5, {'Bb4': 'D5', 'Bb5': 'D6', 'Bb3': 'D4'}[base], 2),
              (15, 1, .5, {'Bb4': 'F5', 'Bb5': 'F6', 'Bb3': 'F4'}[base], 1),
              (15, 2, .5, {'Bb4': 'D5', 'Bb5': 'D6', 'Bb3': 'D4'}[base], 0),
              (15, 3, 1, base, 1)], s, vel)
banjo(TRIO, s, 16, vel=70, hot=True)
tuba(TRIO, s, 16, vel=96, next_sym='Bb')
drums(s, 16, 'hot')

# ---------------------------------------------------------------- 12. OUT CHORUS (16)
s = section("Out chorus — collective improvisation, full boil", 16)
OUT_TPT = [
    (0, 1, .5, 'F5', 1), (0, 1.5, .5, 'F5', 0), (0, 2, .5, 'F5', 0),
    (0, 2.5, 1.5, 'D5', 1), (0, 4.5, .5, 'F5', 0),
    (1, 1, 1.5, 'G5', 2), (1, 2.5, .5, 'F5', 0), (1, 3, 1, 'D5', 0), (1, 4, 1, 'Bb4', 0),
    (2, 1, .5, 'A4', 0), (2, 1.5, .5, 'C5', 0), (2, 2, .5, 'Eb5', 0), (2, 2.5, 1.5, 'F5', 1),
    (3, 1, .5, 'F5', 0), (3, 1.5, .5, 'Eb5', 0), (3, 2, .5, 'C5', 0),
    (3, 2.5, 1.5, 'A4', 0), (3, 4, .5, 'F4', 0), (3, 4.5, .5, 'A4', 0),
    (4, 1, .5, 'C5', 0), (4, 1.5, .5, 'C5', 0), (4, 2, .5, 'C5', 0), (4, 2.5, 1.5, 'Eb5', 1),
    (5, 1, .5, 'Eb5', 0), (5, 1.5, .5, 'C5', 0), (5, 2, .5, 'A4', 0),
    (5, 2.5, 1.5, 'C5', 0), (5, 4.5, .5, 'Bb4', 0),
    (6, 1, .5, 'D5', 0), (6, 1.5, .5, 'F5', 1), (6, 2, .5, 'D5', 0), (6, 2.5, 1.5, 'F5', 1),
    (7, 1, .5, 'F5', 0), (7, 1.5, .5, 'Ab5', 2), (7, 2, 1.5, 'F5', 0),
    (7, 4, .5, 'Eb5', 0), (7, 4.5, .5, 'D5', 0),
    (8, 1, 1.5, 'G5', 1), (8, 2.5, .5, 'Bb5', 2), (8, 3, 1, 'G5', 0), (8, 4, 1, 'Eb5', 0),
    (9, 1, .5, 'E5', 0), (9, 1.5, .5, 'G5', 0), (9, 2, 1, 'Bb5', 1), (9, 3, 1, 'Db5', 0),
    (9, 4, .5, 'E5', 0), (9, 4.5, .5, 'G5', 0),
    (10, 1, .5, 'F5', 0), (10, 1.5, .5, 'F5', 0), (10, 2, .5, 'F5', 0), (10, 2.5, 1.5, 'D5', 0),
    (11, 1, .5, 'D5', 0), (11, 1.5, .5, 'F5', 0), (11, 2, .5, 'B4', 0), (11, 2.5, 1.5, 'G5', 1),
    (12, 1, .5, 'G5', 0), (12, 1.5, .5, 'E5', 0), (12, 2, .5, 'C5', 0), (12, 2.5, 1.5, 'A5', 2),
    (13, 1, .5, 'A5', 0), (13, 1.5, .5, 'G5', 0), (13, 2, .5, 'F5', 0),
    (13, 2.5, .5, 'Eb5', 0), (13, 3, .5, 'C5', 0), (13, 3.5, .5, 'A4', 0),
    (13, 4, .5, 'C5', 0), (13, 4.5, .5, 'Eb5', 0),
    (14, 1, .5, 'Bb5', 2), (14, 1.5, .5, 'Bb5', 1), (14, 2, .5, 'Bb5', 1),
    (14, 2.5, 1.5, 'G5', 1),                       # the rattle at the peak
    (15, 1, .5, 'F5', 0), (15, 1.5, .5, 'D5', 0), (15, 2, .5, 'Bb4', 0),
    (15, 2.5, .5, 'C5', 0), (15, 3, .5, 'D5', 0), (15, 3.5, .5, 'F5', 0),
    (15, 4, .5, 'G5', 0), (15, 4.5, .5, 'A5', 1),
]
play(TPT, OUT_TPT, s, 104)
obbligato(TRIO_FINAL, s, 16, OUT_TPT, anchor=84, energy=0.9, vel=78)
tailgate(TRIO_FINAL, s, 16, vel=86, density=0.95)
# sax joins the trombone register with guide-tone riffs
for b in range(0, 16, 2):
    sym = chord_at(TRIO_FINAL, b, 0)
    _, _, pcs = parse_chord(sym)
    p = fit(pcs[1], 53, 65)
    ev(SAX, p, bt(s + b, 3.5), 0.4, 78)
    ev(SAX, p, bt(s + b, 4.5), 0.4, 74)
    ev(SAX, fit(pcs[0], 53, 65, near=p), bt(s + b + 1, 1), 1.4, 82)
banjo(TRIO_FINAL, s, 16, vel=72, hot=True)
tuba(TRIO_FINAL, s, 8, vel=96, next_sym='Eb')
tuba([TRIO_FINAL[i] for i in range(8, 16)], s + 8, 8, vel=100, walking=True,
     next_sym='Bb')
drums(s, 16, 'hot')

# ---------------------------------------------------------------- 13. TAG (9)
s = section("Tag — three breaks and out", 9)
def tag_hits(bar):
    stab('Bb', bar, 1, dur=0.6, vel=98, bar0=s, who=(TBN, CLA, TPT, SAX))
    stab('G7', bar, 3, dur=0.6, vel=96, bar0=s, who=(TBN, CLA, TPT, SAX))
    ev(DRUMS, CRASH, bt(s + bar, 1), 0.8, 88)
tag_hits(0)
play(TBN, [                                        # trombone break (C7 -> F7)
    (1, 1, .5, 'E3', 1), (1, 1.5, .5, 'G3', 0), (1, 2, .5, 'Bb3', 0),
    (1, 2.5, .5, 'A3', 0), (1, 3, .5, 'F3', 0), (1, 3.5, .5, 'Eb3', 0),
    (1, 4, .5, 'C3', 0), (1, 4.5, .5, 'A2', 0),
], s, 94)
tag_hits(2)
play(CLA, [                                        # clarinet break
    (3, 1, .5, 'C6', 1), (3, 1.5, .5, 'Bb5', 0), (3, 2, .5, 'G5', 0),
    (3, 2.5, .5, 'E5', 0), (3, 3, .5, 'F5', 0), (3, 3.5, .5, 'A5', 0),
    (3, 4, .5, 'C6', 0), (3, 4.5, .5, 'Eb6', 1),
], s, 90)
tag_hits(4)
play(TPT, [                                        # trumpet break
    (5, 1, .5, 'G5', 1), (5, 1.5, .5, 'E5', 0), (5, 2, .5, 'C5', 0),
    (5, 2.5, .5, 'E5', 0), (5, 3, .5, 'G5', 0), (5, 3.5, .5, 'A5', 1),
    (5, 4, .5, 'Eb5', 0), (5, 4.5, .5, 'C5', 0),
], s, 102)
# final phrase: the whole band plays the rattle one last time...
for tr, base, vel in ((TPT, 'Bb4', 106), (CLA, 'Bb5', 90), (TBN, 'Bb3', 96), (SAX, 'Bb3', 92)):
    up = {'Bb4': 'D5', 'Bb5': 'D6', 'Bb3': 'D4'}[base]
    play(tr, [(6, 1, .5, base, 1), (6, 1.5, .5, base, 0), (6, 2, .5, base, 0),
              (6, 2.5, 1.5, up, 2), (6, 4.5, .5, base, 1)], s, vel)
banjo(['Bb', 'Bb'], s + 6, 1, vel=74, hot=True)
tuba(['Bb'], s + 6, 1, vel=98, next_sym=None)
drums(s + 6, 1, 'hot', crash_first=False)
# ...two short hits and the big final chord
for (beat, dur, vel) in ((1, 0.4, 100), (2, 0.4, 102)):
    stab('Bb', 7, beat, dur=dur, vel=vel, bar0=s, who=(TBN, CLA, TPT, SAX))
ev(TPT, N('Bb5'), bt(s + 7, 2.5), 2.4, 112)
trill(CLA, N('F6'), bt(s + 7, 2.5), 2.4, 92)
ev(TBN, N('Bb3'), bt(s + 7, 2.5), 2.4, 100); scoop(TBN, bt(s + 7, 2.5))
ev(SAX, N('D4'), bt(s + 7, 2.5), 2.4, 96)
ev(TUBA, N('Bb1'), bt(s + 7, 2.5), 2.4, 102)
ev(DRUMS, CRASH, bt(s + 7, 2.5), 2, 104); ev(DRUMS, KICK, bt(s + 7, 2.5), .5, 100)
roll(bt(s + 7, 2.5), 92, n=4)
# ...and the sousaphone plop, the streetcar rounding the corner
ev(TUBA, N('Bb1'), bt(s + 8, 2), 0.5, 96)
ev(DRUMS, KICK, bt(s + 8, 2), 0.3, 88)
ev(DRUMS, WB_LO, bt(s + 8, 2), 0.3, 80)
for i, p in enumerate(sorted({fit(pc, 50, 64, near=57) for pc in parse_chord('Bb')[2]})):
    ev(BANJO, p, bt(s + 8, 2), 0.4, 70 - i * 2, post=i * 0.018)

TOTAL_BARS = _cursor

# ================================================================ RENDER
def swing_map(t):
    base = int(t // 1)
    frac = t - base
    if frac <= 0.5:
        return base + frac * (SWING / 0.5)
    return base + SWING + (frac - 0.5) * ((1 - SWING) / 0.5)

def render(path):
    mf = MIDIFile(7, deinterleave=False)
    mf.addTempo(0, 0, TEMPO)
    mf.addTimeSignature(0, 0, 4, 2, 24)
    for i, (name, ch, prog, vol, pan) in enumerate(TRACK_INFO):
        mf.addTrackName(i, 0, name)
        if ch != 9:
            mf.addProgramChange(i, ch, 0, prog)
        mf.addControllerEvent(i, ch, 0, 7, vol)
        mf.addControllerEvent(i, ch, 0, 10, pan)
        mf.addControllerEvent(i, ch, 0, 91, 38)
    timed = []
    for e in EVENTS:
        if e['swing']:
            t0 = swing_map(e['t']); t1 = swing_map(e['t'] + e['d'])
        else:
            t0, t1 = e['t'], e['t'] + e['d']
        t0 += e['post']
        jit = 0.006 if e['tr'] in (TUBA, BANJO, DRUMS) else 0.013
        t0 = max(0.0, t0 + RNG.uniform(-jit, jit))
        timed.append([e['tr'], e['ch'], e['p'], t0, max(0.05, t1 - t0), e['v']])
    # trim tails so a re-attacked pitch never overlaps itself (synth stutter)
    by_pitch = {}
    for ev2 in timed:
        if ev2[0] != DRUMS:
            by_pitch.setdefault((ev2[0], ev2[2]), []).append(ev2)
    for group in by_pitch.values():
        group.sort(key=lambda x: x[3])
        for a, b in zip(group, group[1:]):
            if a[3] + a[4] > b[3] - 0.02:
                a[4] = max(0.05, b[3] - 0.02 - a[3])
    for (tr, ch, p, t0, d, v) in timed:
        mf.addNote(tr, ch, p, t0, d, max(20, min(127, v + RNG.randint(-3, 3))))
    for (tr, ch, t, val) in BENDS:
        mf.addPitchWheelEvent(tr, ch, max(0.0, swing_map(t)), val)
    with open(path, 'wb') as f:
        mf.writeFile(f)

def report():
    print(f"ROYAL STREET RATTLER — {TOTAL_BARS} bars @ {TEMPO}bpm "
          f"= {TOTAL_BARS * 4 * 60 / TEMPO:.0f}s")
    print(f"{len(EVENTS)} note events\n")
    print("Section map:")
    for (name, start, nbars) in SECTIONS:
        t = start * 4 * 60 / TEMPO
        print(f"  {int(t // 60)}:{t % 60:04.1f}  bar {start + 1:>3}  ({nbars:>2} bars)  {name}")
    LIMITS = {TPT: (52, 82), CLA: (52, 96), TBN: (40, 70), SAX: (44, 77),
              TUBA: (26, 48), BANJO: (45, 70)}
    names = {i: TRACK_INFO[i][0] for i in range(7)}
    print("\nRange check:")
    ok = True
    for tr in sorted(LIMITS):
        ps = [e['p'] for e in EVENTS if e['tr'] == tr]
        lo, hi = min(ps), max(ps)
        flag = "OK " if LIMITS[tr][0] <= lo and hi <= LIMITS[tr][1] else "VIOLATION"
        if flag != "OK ":
            ok = False
        print(f"  {flag} {names[tr]:<22} {lo}..{hi} (limit {LIMITS[tr][0]}..{LIMITS[tr][1]})")
    return ok

if __name__ == '__main__':
    import os, sys
    out = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, 'royal_street_rattler.mid')
    render(path)
    ok = report()
    print(f"\nWrote {os.path.abspath(path)}")
    sys.exit(0 if ok else 1)
