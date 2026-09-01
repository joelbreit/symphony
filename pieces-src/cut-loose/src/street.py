"""Second-line idioms as code (docs/02) — piece-local.

The two drummers (dirge cadence, street beat, answers, breaks, the
whistle), the sousaphone (dirge halves, two-beat, walking four), the
riffing horns, the obbligato and tailgate generators, block harmony for
the shout chorus, band stabs, and the vibrato that is the dirge's grief.
Everything writes through the Piece so the swing/humanize pass at write
time applies uniformly; micro-timed figures (rolls, smears) write
swing=False themselves.
"""
import pathlib
import sys
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib import figures
from lib.chords import chord_at, fit, parse_chord, voicing
from lib.dsl import events as _events
from lib.pitch import midi

SN, BD = 'snare', 'bassdrum'
WHISTLE_LONG, WHISTLE_SHORT = 72, 71        # GM drum map (not in lib.DRUMS)
BASS_LO, BASS_HI = 'Eb1', 'Eb3'             # sousaphone

# chord-scales for the obbligato's stepwise runs
_SCALES = {
    '': (0, 2, 4, 5, 7, 9, 11), '6': (0, 2, 4, 5, 7, 9, 11),
    'maj7': (0, 2, 4, 5, 7, 9, 11),
    '7': (0, 2, 4, 5, 7, 9, 10), '9': (0, 2, 4, 5, 7, 9, 10),
    'm': (0, 2, 3, 5, 7, 8, 10), 'm7': (0, 2, 3, 5, 7, 9, 10),
    'm6': (0, 2, 3, 5, 7, 9, 10),
    'dim7': (0, 2, 3, 5, 6, 8, 9, 11), 'dim': (0, 2, 3, 5, 6, 8, 9, 11),
}


def _quality(sym: str) -> str:
    sym = sym.split('/')[0]
    i = 1
    while i < len(sym) and sym[i] in '#b':
        i += 1
    return sym[i:]


def scale_of(sym: str):
    root = parse_chord(sym)[0]
    return [(root + iv) % 12 for iv in _SCALES.get(_quality(sym), _SCALES['7'])]


def _chord_at_beat(chart, t0, t):
    """Chart lookup for an absolute beat, honoring split bars."""
    rel = float(t) - float(t0)
    bar = int(rel // 4)
    return chord_at(chart, bar, 0 if rel - 4 * bar < 2 else 1)


# ------------------------------------------------------------ sousaphone

def _root_fifth(sym, near):
    root_pc, bass_pc, _ = parse_chord(sym)
    r = fit(bass_pc, BASS_LO, BASS_HI, near=near)
    alt_pc = (root_pc + 7) % 12 if bass_pc == root_pc else root_pc
    f = fit(alt_pc, BASS_LO, BASS_HI, near=r)
    return r, f


def _walk(cur, target, sym):
    """Four quarter notes from `cur` landing on `target` next bar."""
    lo, hi = midi(BASS_LO), midi(BASS_HI)
    if target == cur:
        if cur - 5 >= lo:
            steps = [cur, cur - 5, cur - 3, cur - 1]        # 1 5 6 7 | 1
        else:
            steps = [cur, cur + 7, cur + 9, cur + 11]
    elif target > cur:
        steps = [cur, target - 3, target - 2, target - 1]  # chromatic up
    else:
        steps = [cur, target + 3, target + 2, target + 1]  # chromatic down
    return [max(lo, min(hi, s)) for s in steps]


def dirge_bass(p, t0, chart, n_bars, vel=64, near='Eb2', walk_every=4,
               next_sym=None):
    """Half notes — root on 1, fifth on 3 — and a quarter-note walk into
    each new phrase. The pace of the procession."""
    for i in range(n_bars):
        bt = t0 + 4 * i
        sym1, sym2 = chord_at(chart, i), chord_at(chart, i, 1)
        r, f = _root_fifth(sym1, near)
        if sym2 != sym1:
            f = fit(parse_chord(sym2)[1], BASS_LO, BASS_HI, near=r)
        nxt = chord_at(chart, i + 1) if i < n_bars - 1 else next_sym
        if walk_every and i % walk_every == walk_every - 1 and nxt:
            target = fit(parse_chord(nxt)[1], BASS_LO, BASS_HI, near=r)
            steps = _walk(r, target, sym1)
            if sym2 != sym1:
                steps[2] = f
            for k, q in enumerate(steps):
                p.note('sousa', bt + k, q, 1.0, vel=vel - 3 + 2 * k, gate=0.9)
            near = steps[-1]
        else:
            p.note('sousa', bt, r, 2, vel=vel, gate=0.94)
            p.note('sousa', bt + 2, f, 2, vel=vel - 8, gate=0.94)
            near = r
    return near


def two_beat(p, t0, chart, n_bars, vel=96, near='Eb2', walk_every=4,
             next_sym=None, four=False):
    """Two-beat: root on 1, fifth on 3, a walk into every phrase turn.
    four=True walks four-to-the-bar (the out-chorus lift)."""
    for i in range(n_bars):
        bt = t0 + 4 * i
        sym1, sym2 = chord_at(chart, i), chord_at(chart, i, 1)
        r, f = _root_fifth(sym1, near)
        if sym2 != sym1:
            f = fit(parse_chord(sym2)[1], BASS_LO, BASS_HI, near=r)
        nxt = chord_at(chart, i + 1) if i < n_bars - 1 else next_sym
        phrase_turn = walk_every and i % walk_every == walk_every - 1
        if nxt and (four or phrase_turn):
            target = fit(parse_chord(nxt)[1], BASS_LO, BASS_HI, near=r)
            steps = _walk(r, target, sym1)
            if sym2 != sym1:
                steps[2] = f
            for k, q in enumerate(steps):
                p.note('sousa', bt + k, q, 0.8, vel=vel - 4 + 2 * k, gate=0.85)
            near = steps[-1]
        elif four:
            for k, q in enumerate([r, f, r, f]):
                p.note('sousa', bt + k, q, 0.8, vel=vel - (0 if k % 2 == 0 else 8),
                       gate=0.85)
            near = r
        else:
            p.note('sousa', bt, r, 0.9, vel=vel, gate=0.85)
            p.note('sousa', bt + 2, f, 0.9, vel=vel - 8, gate=0.85)
            near = r
    return near


# ------------------------------------------------------------ the drummers

def dirge_cadence(p, t0, n_bars, vel=52, cymbal_every=4, roll_every=1):
    """Bass drum on 1 and 3; muffled snare: a tap on 2, a buzz through
    the and-of-3, a roll through beat 4 swelling into the next downbeat."""
    for i in range(n_bars):
        bt = t0 + 4 * i
        p.perc(bt, [('kick', 1)], vel=vel + 18, inst=BD)
        p.perc(bt + 2, [('kick', 1)], vel=vel + 4, inst=BD)
        if cymbal_every and i % cymbal_every == 0:
            p.perc(bt, [('crash', 2)], vel=vel - 12, inst=BD)
        p.perc(bt + 1, [('sn', 0.3)], vel=vel - 10, inst=SN)
        figures.perc_roll(p, 'sn', bt + 2.5, 0.5, vel - 26, vel - 18,
                          unit=1 / 16, inst=SN)
        if i % roll_every == 0:
            figures.perc_roll(p, 'sn', bt + 3.0, 1.0, vel - 22, vel + 2,
                              unit=1 / 16, inst=SN)
        else:
            p.perc(bt + 3, [('sn', 0.3)], vel=vel - 12, inst=SN)


# snare cells for the street beat: (beat offset, drum, velocity offset)
_SN_CELLS = [
    [(0.0, 'sn', -8), (1.0, 'sn', 8), (1.5, 'sn', -18), (2.0, 'sn', -6),
     (2.5, 'sn', -16), (3.0, 'sn', 10), (3.75, 'sn', -12)],
    [(0.5, 'sn', -12), (1.0, 'sn', 8), (1.75, 'sn', -16), (2.0, 'sn', -4),
     (2.5, 'sn', -14), (3.0, 'sn', 10), (3.5, 'rim', -8), (3.75, 'sn', -10)],
    [(0.0, 'sn', -6), (0.75, 'sn', -16), (1.0, 'sn', 8), (2.0, 'sn', -8),
     (2.5, 'sn', -12), (3.0, 'sn', 10), (3.5, 'rim', -10)],
    [(0.0, 'sn', -8), (1.0, 'sn', 8), (1.5, 'rim', -10), (2.5, 'sn', -12),
     (2.75, 'sn', -14), (3.0, 'sn', 10), (3.5, 'sn', -12)],
]
_BD_CELLS = [
    [(0.0, 8), (1.5, -8), (3.0, 0)],            # boom — ba-boom: 1, and-of-2, 4
    [(0.0, 8), (2.5, -8), (3.0, 0)],
]
_FILLS = [
    [(2.0, 'sn', 0), (2.25, 'sn', -8), (2.5, 'sn', -4), (2.75, 'sn', -8),
     (3.0, 'sn', 6), (3.5, 'sn', 2), (3.75, 'sn', 12)],
    [(2.0, 'sn', 4), (2.5, 'rim', 0), (2.75, 'sn', -6), (3.0, 'sn', 8),
     (3.25, 'sn', -6), (3.5, 'sn', 0), (3.75, 'sn', 12)],
]


def _cell(p, t, cell, vel, inst):
    for off, key, dv in cell:
        p.perc(t + off, [(key, 0.25)], vel=max(1, min(127, vel + dv)),
               inst=inst)


def street_beat(p, t0, n_bars, vel=84, snare=True, bd=True, cym=True,
                fill_every=4, crash_first=True, cell0=0):
    """The second-line street beat, bar by bar."""
    for i in range(n_bars):
        bt = t0 + 4 * i
        if bd:
            _cell(p, bt, [(o, 'kick', dv) for o, dv in _BD_CELLS[(cell0 + i // 2) % 2]],
                  vel, BD)
            if cym:
                for b in (1.0, 3.0):
                    p.perc(bt + b, [('hhc', 0.3)], vel=vel - 30, inst=BD)
            if crash_first and i == 0:
                p.perc(bt, [('crash', 1.5)], vel=vel + 4, inst=BD)
        if snare:
            fill = fill_every and i % fill_every == fill_every - 1
            cell = _SN_CELLS[(cell0 + i) % len(_SN_CELLS)]
            if fill:
                cell = [c for c in cell if c[0] < 2.0] + _FILLS[(i // fill_every) % 2]
            _cell(p, bt, cell, vel, SN)
            if i % 2 == 1 and not fill:
                figures.press_roll(p, bt + 4.0, vel + 6, n=4, inst=SN)


def snare_answer(p, t, vel=96, variant=0):
    """Two beats of snare drum answering the horns (shout chorus)."""
    cells = [
        [(0.0, 'sn', 10), (0.5, 'sn', -6), (0.75, 'sn', -6), (1.0, 'sn', 6),
         (1.5, 'rim', 0), (1.75, 'sn', -4)],
        [(0.0, 'sn', 8), (0.25, 'sn', -10), (0.5, 'sn', -4), (1.0, 'sn', 10),
         (1.25, 'sn', -10), (1.5, 'sn', 0), (1.75, 'sn', 6)],
        [(0.0, 'rim', 4), (0.5, 'sn', 8), (1.0, 'rim', 2), (1.25, 'sn', -6),
         (1.5, 'sn', 10), (1.75, 'sn', 0)],
        [(0.0, 'sn', 10), (0.25, 'sn', -8), (0.5, 'sn', -8), (0.75, 'sn', -8),
         (1.0, 'sn', 12), (1.5, 'sn', 4), (1.75, 'sn', 8)],
    ]
    _cell(p, t, cells[variant % len(cells)], vel, SN)
    p.perc(t, [('kick', 0.3)], vel=vel - 4, inst=BD)
    p.perc(t + 1.5, [('kick', 0.3)], vel=vel - 10, inst=BD)


def snare_solo(p, t0, n_bars, vel=88):
    """The roll-off after the whistle: the snare drummer alone, building."""
    for i in range(n_bars):
        bt = t0 + 4 * i
        v = vel + 4 * i
        if i == 0:
            figures.perc_roll(p, 'sn', bt, 1.0, v - 30, v, unit=1 / 8, inst=SN)
            _cell(p, bt, [(1.0, 'sn', 8), (1.5, 'sn', -12), (2.0, 'sn', -4),
                          (2.5, 'sn', -12), (3.0, 'sn', 10), (3.75, 'sn', -8)], v, SN)
        elif i == 1:
            _cell(p, bt, _SN_CELLS[1], v, SN)
        else:
            _cell(p, bt, _SN_CELLS[(i + 1) % 4], v, SN)
        if i % 2 == 1:
            figures.press_roll(p, bt + 4.0, v + 8, n=5, inst=SN)


def drum_break(p, t0, n_bars, vel=100):
    """Bars of the two drummers alone — snare talk over the bass drum."""
    talk = [
        [(0.0, 'sn', 10), (0.5, 'sn', -6), (1.0, 'sn', -6), (1.5, 'sn', 8),
         (2.0, 'rim', 0), (2.5, 'sn', -8), (2.75, 'sn', -8), (3.0, 'sn', 12),
         (3.5, 'rim', -2)],
        [(0.0, 'sn', 6), (0.25, 'sn', -10), (0.5, 'sn', -10), (0.75, 'sn', -10),
         (1.0, 'sn', 12), (1.5, 'sn', 0), (2.0, 'sn', 4), (2.5, 'sn', -4),
         (2.75, 'sn', -4), (3.0, 'sn', 10), (3.25, 'sn', -6), (3.5, 'sn', 0),
         (3.75, 'sn', 8)],
    ]
    for i in range(n_bars):
        bt = t0 + 4 * i
        _cell(p, bt, talk[i % 2], vel, SN)
        _cell(p, bt, [(o, 'kick', dv) for o, dv in _BD_CELLS[i % 2]], vel - 6, BD)
        if i == n_bars - 1:
            figures.press_roll(p, bt + 4.0, vel + 10, n=6, inst=SN)


def whistle(p, t):
    """The grand marshal: one long, two short. Write at the dirge tempo."""
    p.perc(t, [(WHISTLE_LONG, 1.0)], vel=127, inst=SN, swing=False)
    p.perc(t + 1.3, [(WHISTLE_SHORT, 0.3)], vel=127, inst=SN, swing=False)
    p.perc(t + 1.65, [(WHISTLE_SHORT, 0.3)], vel=127, inst=SN, swing=False)


# ------------------------------------------------------------ the horns

STAB_ZONES = {'cornet': ('Bb4', 'Bb5'), 'clarinet': ('Eb5', 'Eb6'),
              'alto': ('Eb4', 'Eb5'), 'tbn': ('Bb2', 'Bb3')}
STAB_TONE = {'tbn': 0, 'alto': 1, 'cornet': 2, 'clarinet': 1}


def stab(p, t, sym, vel=96, dur=0.5, who=('clarinet', 'alto', 'tbn'),
         sousa=True, drums=True, near=None):
    """One band hit — roots low, thirds in the middle, fifth on top."""
    _, bass_pc, pcs = parse_chord(sym)
    for inst in who:
        lo, hi = STAB_ZONES[inst]
        idx = STAB_TONE[inst]
        if inst == 'clarinet' and len(pcs) > 3:
            idx = 3                                  # the seventh, up top
        pc = pcs[idx % len(pcs)]
        p.note(inst, t, fit(pc, lo, hi, near=near), dur,
               vel=vel - (10 if inst == 'clarinet' else 0), gate=0.9)
    if sousa:
        p.note('sousa', t, fit(bass_pc, 'Eb1', 'Bb2', near='Bb1'),
               min(dur + 0.2, 1.0), vel=vel + 2, gate=0.9)
    if drums:
        p.perc(t, [('kick', 0.3)], vel=vel, inst=BD)
        p.perc(t, [('sn', 0.3)], vel=vel - 10, inst=SN)


RIFF_RHYTHMS = {
    'offbeats': ((1.5, 0.5), (3.5, 0.5)),
    'charleston': ((0.0, 0.75), (1.5, 0.5)),
    'push': ((2.5, 0.5), (3.5, 1.0)),
    'and-of-4': ((3.5, 1.0),),
}


def riff(p, inst, t0, chart, n_bars, lo, hi, rhythm='offbeats', vel=70,
         tones=(1, 2), near=None, every=1):
    """Chord-tone stabs behind a lead — the brass-band engine. Voice-led."""
    cur = near
    pattern = RIFF_RHYTHMS[rhythm] if isinstance(rhythm, str) else rhythm
    for i in range(n_bars):
        if i % every:
            continue
        for k, (pos, d) in enumerate(pattern):
            sym = chord_at(chart, i, 0 if pos < 2 else 1)
            pcs = parse_chord(sym)[2]
            pc = pcs[tones[k % len(tones)] % len(pcs)]
            q = fit(pc, lo, hi, near=cur)
            p.note(inst, t0 + 4 * i + pos, q, d, vel=vel, gate=0.6)
            cur = q
    return cur


def pads(p, inst, t0, chart, n_bars, lo, hi, vel=48, tone=1, near=None):
    """Long guide tones (one per bar) behind a soloist."""
    cur = near
    for i in range(n_bars):
        pcs = parse_chord(chord_at(chart, i))[2]
        q = fit(pcs[tone % len(pcs)], lo, hi, near=cur)
        p.note(inst, t0 + 4 * i, q, 3.8, vel=vel, gate=0.97)
        cur = q


def _fit_in(pc, lo, hi, near):
    """fit() that refuses instead of guessing when nothing fits in [lo, hi]."""
    cands = [q for q in range(int(lo), int(hi) + 1) if q % 12 == pc % 12]
    if not cands:
        return None
    return min(cands, key=lambda q: abs(q - near))


def _lead_profile(lead, t0):
    """(onsets, max pitch) per half-bar from a lead's DSL/events."""
    prof = {}
    t = Fraction(0)
    for pch, d in _events(lead):
        if pch is not None:
            top = max(pch) if isinstance(pch, list) else pch
            key = (int(t // 4), 0 if t % 4 < 2 else 1)
            n, m = prof.get(key, (0, 0))
            prof[key] = (n + 1, max(m, top))
        t += d
    return prof


def obbligato(p, t0, chart, n_bars, lead, lo='Eb5', hi='F6', anchor='C6',
              energy=0.5, vel=72, inst='clarinet', hold_prob=0.6):
    """Clarinet filigree: runs when the lead holds or rests, sustains above
    it when it moves. Four run types (docs/02): arpeggio, scale passage in
    the chord's scale, triplet turn, chromatic enclosure."""
    rng = p.rng
    lo_m, hi_m, anchor_m = midi(lo), midi(hi), midi(anchor)
    prof = _lead_profile(lead, t0)
    cur = anchor_m
    for b in range(n_bars):
        for half in (0, 1):
            t = t0 + 4 * b + 2 * half
            n_on, top = prof.get((b, half), (0, 0))
            floor = max(lo_m, top + 3) if n_on else lo_m
            sym = chord_at(chart, b, half)
            pcs = parse_chord(sym)[2]
            if n_on >= 2:                          # lead busy: hold or rest
                if rng.random() < hold_prob:
                    pc = pcs[rng.choice((1, 2)) % len(pcs)]
                    q = _fit_in(pc, floor, hi_m, cur + 2)
                    if q is not None:
                        p.note(inst, t, q, 1.9, vel=vel - 14, gate=0.95)
                        cur = q
                continue
            if rng.random() > 0.5 + 0.45 * energy:
                continue
            kind = rng.choices(['arp', 'scale', 'turn', 'enclose'],
                               weights=[3, 3, 1 + 2 * energy, 2])[0]
            direction = 1 if cur < anchor_m else -1
            if rng.random() < 0.3:
                direction = -direction
            evs = []
            F = lambda pc, near: (_fit_in(pc, floor, hi_m, near)
                                  or _fit_in(pc, lo_m, hi_m, near))
            if kind == 'arp':
                q = F(pcs[0], cur + direction * 3)
                for i in range(4):
                    evs.append((q, 0.5))
                    q = F(pcs[(i + 1) % len(pcs)],
                          q + direction * rng.choice((3, 4, 5)))
            elif kind == 'scale':
                sc = scale_of(sym)
                q = F(pcs[rng.choice((0, 1, 2)) % len(pcs)], cur)
                for i in range(4):
                    evs.append((q, 0.5))
                    step = direction
                    q2 = q + step
                    while q2 % 12 not in sc:
                        q2 += step
                    if not (floor <= q2 <= hi_m):
                        direction = -direction
                        q2 = q - step
                        while q2 % 12 not in sc:
                            q2 -= step
                    q = q2
            elif kind == 'turn':
                q = F(pcs[rng.choice((1, 2)) % len(pcs)], cur)
                sc = scale_of(sym)
                up = q + 1
                while up % 12 not in sc:
                    up += 1
                dn = q - 1
                while dn % 12 not in sc:
                    dn -= 1
                evs = [(up, Fraction(1, 3)), (q, Fraction(1, 3)),
                       (dn, Fraction(1, 3)), (q, 1.0)]
            else:                                   # enclosure
                q = F(pcs[rng.choice((0, 2)) % len(pcs)], cur + direction * 2)
                evs = [(q + 1, 0.5), (q - 1, 0.5), (q, 1.0)]
            if any(q is None for q, _ in evs):
                continue
            evs = [(q - 12 if q > hi_m else q + 12 if q < lo_m else q, d)
                   for q, d in evs]
            if rng.random() < 0.3 * energy and evs[0][0] + 1 <= hi_m:
                p.note(inst, t - 0.5, evs[0][0] + 1, 0.4, vel=vel - 18)
            p.add(inst, t, evs, vel=vel + rng.randint(-3, 3), gate=0.85,
                  accent_first=(kind != 'turn'))
            cur = evs[-1][0]


def tailgate(p, t0, chart, n_bars, vel=78, density=0.8, lo='Bb2', hi='F4',
             near='F3', inst='tbn'):
    """Trombone counterline: voice-led guide tones, smears into phrase
    downbeats, a chromatic push into the next phrase."""
    rng = p.rng
    cur = midi(near)
    for b in range(n_bars):
        sym = chord_at(chart, b)
        _, _, pcs = parse_chord(sym)
        guide = fit(rng.choice((pcs[1], pcs[0], pcs[-1])), lo, hi, near=cur)
        cur = guide
        t = t0 + 4 * b
        if rng.random() > density:
            continue
        if b % 4 == 0:
            figures.smear_into(p, inst, guide, t, vel - 4, n=3)
            figures.scoop(p, inst, t)
            p.note(inst, t, guide, 1.8, vel=vel + 8)
            sym2 = chord_at(chart, b, 1)
            p2 = fit(parse_chord(sym2)[2][0], lo, hi, near=guide - 2)
            p.note(inst, t + 2, p2, 1.4, vel=vel - 4)
            cur = p2
        elif b % 4 == 3:
            nxt = chord_at(chart, b + 1)
            tgt = fit(parse_chord(nxt)[2][1], lo, hi, near=cur)
            p.note(inst, t, guide, 1.4, vel=vel)
            p.note(inst, t + 2.5, tgt + 1, 0.45, vel=vel - 8)
            p.note(inst, t + 3.0, tgt, 0.9, vel=vel + 4)
            cur = tgt
        else:
            p.note(inst, t, guide, 2.8, vel=vel - 2)
            if rng.random() < 0.5:
                p2 = fit(pcs[2 % len(pcs)], lo, hi, near=guide + 3)
                p.note(inst, t + 3, p2, 0.9, vel=vel - 6)
                cur = p2


def block_harmony(p, t0, chart, line, vel, lead='cornet', above='clarinet',
                  below='alto', gate=0.8):
    """Shout-chorus harmony: the lead line plus a chord tone above and one
    below on every note, voice-led by proximity, kept inside ranges."""
    p.add(lead, t0, line, vel=vel, gate=gate)
    ens = p.ensemble
    t = Fraction(t0)
    for pch, d in _events(line):
        if pch is not None:
            c = max(pch) if isinstance(pch, list) else pch
            pcs = parse_chord(_chord_at_beat(chart, t0, t))[2]
            up = [q for q in range(c + 3, c + 10)
                  if q % 12 in pcs and ens[above].lo <= q <= ens[above].hi]
            if up:
                a = min(up)
            else:
                dn = [q for q in range(c - 9, c - 2)
                      if q % 12 in pcs and ens[above].lo <= q <= ens[above].hi]
                a = max(dn) if dn else None
            lo_c = [q for q in range(c - 9, c - 2)
                    if q % 12 in pcs and ens[below].lo <= q <= ens[below].hi
                    and q != a]
            if not lo_c:
                lo_c = [q for q in range(c - 16, c - 9)
                        if q % 12 in pcs and ens[below].lo <= q <= ens[below].hi]
            b_ = max(lo_c) if lo_c else None
            if a is not None:
                p.note(above, float(t), a, d, vel=vel - 10, gate=gate)
            if b_ is not None:
                p.note(below, float(t), b_, d, vel=vel - 6, gate=gate)
        t += d


def unison(p, t0, line, vel, parts):
    """The same line in several horns at octave offsets: [(inst, shift, dv)]."""
    for inst, shift, dv in parts:
        p.add(inst, t0, line, vel=vel + dv, transpose=shift, gate=0.85)


# ------------------------------------------------------------ the lungs

def cry(p, inst, t0, t1, depth=100, rise=1.0):
    """Wide vibrato (CC1) — the dirge's grief. Rises in over `rise` beats,
    off at t1. Measured: 127 gives about ±37 cents on this soundfont."""
    p.cc(inst, t0, 1, round(depth * 0.5))
    p.hairpin(inst, t0, t0 + rise, round(depth * 0.5), depth, controller=1,
              step=0.25)
    p.cc(inst, t1, 1, 0)


def dry(p, t, insts=('cornet', 'clarinet', 'alto', 'tbn')):
    """No vibrato, full expression: reset before the second line."""
    for inst in insts:
        p.cc(inst, t, 1, 0)
        p.cc(inst, t, 11, 112)
