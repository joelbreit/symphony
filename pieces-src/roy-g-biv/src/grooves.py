"""The invisible rhythm section (docs/01): everything here is percussion,
and percussion never prints on the roll. The kit is free to cook under the
picture — brushes in the storm, the thunder itself, the second-line strut
under the rainbow, a last-laugh drum solo on the way to the sun.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib import figures


def brushes(p, t, bars, vel=24):
    """Gray-morning hiss: soft closed hats with a slow shaker breath."""
    for i in range(bars):
        bt = t + 4 * i
        for k in range(8):
            v = vel + (5 if k % 4 == 0 else 0) + p.rng.randint(-2, 2)
            p.perc(bt + 0.5 * k, 'hhc:e', vel=v)
        if i % 2 == 1:
            p.perc(bt + 2.0, 'shaker:q shaker:q', vel=vel + 4)


def storm_kit(p, t, bars, level=0.0):
    """The storm's pulse: hats, cross-stick backbeat, floor-tom mutter.
    level 0..1 scales weight (post-downpour it leans on kick + floor tom)."""
    for i in range(bars):
        bt = t + 4 * i
        base = 30 + int(26 * level)
        for k in range(8):
            v = base + (6 if k % 4 == 0 else 0) + p.rng.randint(-3, 3)
            p.perc(bt + 0.5 * k, 'hhc:e', vel=v)
        p.perc(bt + 1.0, 'rim:q', vel=base + 14)
        p.perc(bt + 3.0, 'rim:q', vel=base + 12)
        if level > 0.4:
            p.perc(bt + 0.0, 'kick:e', vel=base + 22)
            p.perc(bt + 2.5, 'kick:e', vel=base + 18)
            p.perc(bt + 3.5, 'tomf:e', vel=base + 10)
        if level > 0.7 and i % 2 == 1:
            p.perc(bt + 3.5, 'tomf2:s tomf:s', vel=base + 16)


def thunder(p, t, big=False):
    """What the lightning sounds like. Rolls arrive ~a beat after the bolt
    is drawn — light travels faster than sound."""
    if big:
        figures.perc_roll(p, 'tomf', t, 5.0, 40, 100)
        figures.perc_roll(p, 'tomf2', t + 0.4, 4.2, 34, 88)
        for off, v in ((0.0, 92), (1.75, 96), (3.0, 88)):
            p.perc(t + off, 'bd:q', vel=v)
        p.perc(t + 1.5, 'china:h', vel=86)
        p.perc(t + 4.0, 'crash:h', vel=70)
        p.perc(t + 4.6, 'vibraslap:q', vel=52)
    else:
        figures.perc_roll(p, 'tomf', t, 3.0, 34, 78)
        p.perc(t + 0.5, 'bd:q', vel=76)
        p.perc(t + 2.0, 'crash:h', vel=62)


def strut(p, t, bars, level=0.5):
    """Second-line strut under the rainbow. level 0..1 rides the arch:
    hats -> ride, ghosts thicken, claps and tambourine join at the crown."""
    for i in range(bars):
        bt = t + 4 * i
        lv = level(bt) if callable(level) else level
        acc = int(20 * lv)
        # kick: syncopated New Orleans-ish, varied by bar
        kicks = [0.0, 1.75, 2.5] if i % 2 == 0 else [0.0, 1.5, 2.75, 3.5]
        for off in kicks:
            p.perc(bt + off, 'kick:e', vel=78 + acc + p.rng.randint(-3, 3))
        # snare: backbeat + ghosts
        for off in (1.0, 3.0):
            p.perc(bt + off, 'sn:q', vel=84 + acc)
            if lv > 0.65:
                p.perc(bt + off, 'clap:q', vel=64 + acc)
        for off in (0.75, 2.25, 3.5):
            if p.rng.random() < 0.35 + 0.4 * lv:
                p.perc(bt + off, 'sn:s', vel=30 + p.rng.randint(0, 8))
        # top: hats low, ride high
        if lv < 0.55:
            for k in range(8):
                p.perc(bt + 0.5 * k, 'hhc:e', vel=52 + acc // 2
                       + (8 if k % 2 == 0 else 0))
            p.perc(bt + 3.5, 'hho:e', vel=50 + acc // 2)
        else:
            for k in range(8):
                key = 'ridebell' if k in (0, 5) else 'ride'
                p.perc(bt + 0.5 * k, f'{key}:e', vel=56 + acc // 2)
            for k in range(8):
                p.perc(bt + 0.5 * k, 'tamb:e', vel=40 + acc // 2
                       + (10 if k % 2 == 0 else 0))
        # seam dressing
        if i % 4 == 3:
            p.perc(bt + 3.0, 'sn:s sn:s tom2:s tomf:s', vel=70 + acc)
        if i % 8 == 0:
            p.perc(bt, 'crash:q', vel=72 + acc)


def drum_break(p, t, bars, vel=88):
    """The outro solo — the invisible man finally gets fours."""
    for i in range(bars):
        bt = t + 4 * i
        v = vel + 4 * i
        if i % 2 == 0:
            p.perc(bt, 'sn:e sn:s sn:s tom2:e tom1:e kick:e sn:e tomf:q',
                   vel=v)
            p.perc(bt + 3.0, 'hho:q', vel=v - 14)
        else:
            p.perc(bt, 'kick:e kick:e sn:s sn:s sn:e tom1:s tom2:s tomf:s '
                       'tomf2:s kick:e sn:e', vel=v)
            p.perc(bt + 3.5, 'crash:e', vel=v - 8)


def sunshine(p, t, dur):
    """Shaker glow + triangle dings for the coda."""
    k = 0
    while 0.5 * k < dur:
        v = max(16, 40 - int(24 * (0.5 * k) / dur))
        p.perc(t + 0.5 * k, 'shaker:e', vel=v)
        k += 1
    for off in (2.0, 8.0, 14.0):
        if off < dur:
            p.perc(t + off, 'tri:h', vel=44)
