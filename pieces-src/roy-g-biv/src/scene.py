"""Scene geometry: the roll's (seconds, pitch) plane as a drawing surface.

Everything visual is declared here in the roll's own axes — seconds and
MIDI pitch — and converted to beats at the call site (one tempo, 120 bpm,
so 2 beats per second, docs/02). The music stays in charge: every shape is
made of scale tones, grids, and figures a player could play.

A found rhyme: D-minor pentatonic (the rain) and F-major pentatonic (the
sun) are the same five pitch classes {D F G A C}. The storm and the sun
use identical material — only context changes.
"""
import math

BPM = 120
BEATS_PER_SEC = BPM / 60.0


def b(sec: float) -> float:
    """seconds -> beats (one fixed tempo, by design)."""
    return sec * BEATS_PER_SEC


def s(beat: float) -> float:
    return beat / BEATS_PER_SEC


# ------------------------------------------------------------ pitch lattices
_MAJ = (0, 2, 4, 5, 7, 9, 10)              # F major: F G A Bb C D E (as pcs of C)
SCALE = [p for p in range(21, 109) if p % 12 in _MAJ]
PENT = [p for p in range(21, 109) if p % 12 in (5, 7, 9, 0, 2)]  # F G A C D


def snap(p: float) -> int:
    """Nearest F-major tone (ties resolve downward)."""
    return min(SCALE, key=lambda q: (abs(q - p), q > p))


def step(p: float, n: int) -> int:
    """n diatonic steps away from the tone nearest p."""
    return SCALE[SCALE.index(snap(p)) + n]


def snap_pent(p: float) -> int:
    return min(PENT, key=lambda q: (abs(q - p), q > p))


def pent_step(p: float, n: int) -> int:
    return PENT[PENT.index(snap_pent(p)) + n]


# ------------------------------------------------------------ the arch
# Top stripe (choir): ellipse in (seconds, pitch); stripe k plays the same
# curve 2k diatonic steps lower (constant band spacing, docs/02).
ARCH_CX, ARCH_RX = 109.0, 48.0      # seconds
ARCH_FOOT, ARCH_RY = 62.0, 24.0     # pitch: D4 feet, D6 crown


def arch(t_sec: float) -> float:
    u = max(-1.0, min(1.0, (t_sec - ARCH_CX) / ARCH_RX))
    return ARCH_FOOT + ARCH_RY * math.sqrt(1.0 - u * u)


def arch_slope(t_sec: float) -> float:
    """|d pitch / d second| — picks the stripes' rhythm (rip/strut/shout)."""
    u = max(-0.998, min(0.998, (t_sec - ARCH_CX) / ARCH_RX))
    return abs(ARCH_RY * u / (ARCH_RX * math.sqrt(1.0 - u * u)))


def stripe_pitch(t_sec: float, k: int) -> int:
    return step(arch(t_sec), -2 * k)


def stripe_vel(t_sec: float) -> int:
    """Saturation = altitude = loudness: ~84 at the feet, ~104 at the crown."""
    return 84 + int(round((arch(t_sec) - ARCH_FOOT) * 0.85))


# ------------------------------------------------------------ weather
def cloud(p, inst, x0, x1, lo, hi, vel, seg=(5.0, 9.0)):
    """A pale blob: ragged ellipse of long tremolo-patch rows (gray).

    Rows every 2 semitones; each row is a few long segments with small
    gaps, widths following the ellipse so the blob reads rounded.
    """
    cx, cy = (x0 + x1) / 2.0, (lo + hi) / 2.0
    rx, ry = (x1 - x0) / 2.0, (hi - lo) / 2.0
    for pitch in range(int(lo), int(hi) + 1, 2):
        dy = (pitch - cy) / ry
        if abs(dy) >= 1.0:
            continue
        w = rx * math.sqrt(1.0 - dy * dy)
        t = b(cx - w * p.rng.uniform(0.82, 1.0))
        t_end = b(cx + w * p.rng.uniform(0.82, 1.0))
        while t < t_end - 1.0:
            d = min(p.rng.uniform(*seg), t_end - t)
            p.note(inst, t, pitch, d - 0.2, vel=vel + p.rng.randint(-3, 3),
                   gate=1.0, swing=False)
            t += d


def bolt(p, at_beat, top, bottom):
    """Lightning: guitar + harp in unison, a 32nd-note chromatic zigzag
    ripping down the sky. You see this; the thunder you only hear."""
    path, cur = [], top
    while cur > bottom + 9:
        down = p.rng.randint(15, 19)
        path.append(-down)
        cur -= down
        if cur <= bottom + 9:
            break
        up = p.rng.randint(5, 7)
        path.append(up)
        cur += up
    path.append(-(cur - bottom))
    pitches = [top]
    for seg_ in path:
        d = 1 if seg_ > 0 else -1
        for _ in range(abs(seg_)):
            pitches.append(pitches[-1] + d)
    t = at_beat
    for i, pitch in enumerate(pitches):     # chromatic 64ths: a solid jag
        v = 118 - int(12 * i / len(pitches))
        p.note('gtr', t, pitch, 0.22, vel=v, swing=False)
        p.note('harp', t, pitch, 0.22, vel=v, swing=False)
        t += 0.0625
    return t


def rain(p, t0, t1, density, lo=40, hi=73, vlo=56, vhi=82):
    """Pizzicato droplets (blue) on a 16th grid, D-minor pentatonic.

    density: beat -> probability per grid slot; the heavier the rain, the
    more drops fall as steep 4-dot streaks (rain reads as diagonals). Some
    bounce as plink-pairs. Durations are visual (a pizzicato decays
    regardless): ~0.25 beats renders a visible dot.
    """
    t = t0
    while t < t1:
        d_here = density(t)
        if p.rng.random() < d_here:
            pitch = snap_pent(p.rng.triangular(lo, hi, hi - 8))
            v = p.rng.randint(vlo, vhi)
            r = p.rng.random()
            if r < 0.25 + 0.55 * d_here and pitch > lo + 12:
                for j in range(4):                     # scale steps connect
                    p.note('rain', t + 0.125 * j, step(pitch, -j),
                           0.3, vel=max(40, v - 5 * j), swing=False)
            elif r < 0.57:                             # plink-pair bounce
                p.note('rain', t, pitch, 0.26, vel=v, swing=False)
                p.note('rain', t + 0.25, pitch, 0.26, vel=v - 12, swing=False)
            else:
                p.note('rain', t, pitch, 0.26, vel=v, swing=False)
        t += 0.25


# ------------------------------------------------------------ the sun
SUN_CX, SUN_CY = 181.0, 94.0        # seconds, pitch
SUN_RX, SUN_RY = 5.5, 7.0

# eight rays: (seconds, pitch, dur_beats) — all F/C/G pentatonic tones
RAYS = [
    (187.6, 96, 2.2), (170.9, 96, 2.2),                # E, W
    (185.6, 101, 1.0), (186.4, 103, 1.0),              # NE
    (175.2, 101, 1.0), (174.4, 103, 1.0),              # NW
    (180.4, 103, 0.8), (180.9, 105, 0.8),              # N
    (185.9, 89, 1.0), (175.1, 89, 1.0),                # SE, SW
]


def sun(p, vel=62):
    """The disc: two interleaved F-major harp sweeps (one rising, one
    falling) filling an ellipse dot by dot, with short rays around it.
    The last light of the piece."""
    t0, t1 = b(SUN_CX - SUN_RX), b(SUN_CX + SUN_RX)
    sweeps = [[SUN_CY - SUN_RY, 1], [SUN_CY + SUN_RY, -1]]
    t = t0
    while t < t1:
        u = (s(t) - SUN_CX) / SUN_RX
        h = SUN_RY * math.sqrt(max(0.0, 1.0 - u * u))
        if h >= 0.8:
            lo_, hi_ = SUN_CY - h, SUN_CY + h
            for sw in sweeps:
                sw[0] += sw[1] * 1.9
                if sw[0] > hi_:
                    sw[0], sw[1] = hi_, -1
                elif sw[0] < lo_:
                    sw[0], sw[1] = lo_, 1
                pitch = snap(max(lo_, min(hi_, sw[0])))
                v = vel + int(6 * (1 - abs(u))) + p.rng.randint(-3, 3)
                p.note('harp', t, pitch, 0.3, vel=v, swing=False)
        t += 0.125
    for x, pitch, d in RAYS:
        p.note('harp', b(x), pitch, d, vel=82, swing=False)

