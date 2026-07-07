"""Roy G. Biv — a rain-to-rainbow jubilee for seven-color band.

One continuous scene, ~3:10, and the roll IS the picture (docs/01, 02):
gray morning -> storm (rain, two lightning bolts, invisible thunder) ->
the seven-stripe arch -> a strut into the sun.

    ../../../.venv/bin/python src/compose.py     (from pieces-src/roy-g-biv/)
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib import Piece, assess, figures, midi_report

import grooves
import scene
from band import STRIPES, spectrum
from scene import arch, arch_slope, b, s, step, stripe_pitch, stripe_vel

OUT = pathlib.Path(__file__).resolve().parents[1] / 'output'

# Scene clock, in beats (120 bpm: beat = 0.5 s; docs/02 beat map).
STORM, BOLT1, BOLT2 = 32, 57, 89
TURN, RAINBOW, OUTRO, SUN = 112, 122, 316, 351
ENTER = {k: RAINBOW + 4 * k for k in range(7)}       # choir first, org last
EXIT = {k: 314 - 4 * k for k in range(7)}            # org first, choir lands last

F1, G1, A1, Bb1, C2, D2, E2, F2 = 29, 31, 33, 34, 36, 38, 40, 41


# ------------------------------------------------------------ 1: the weather
def gray_morning(p):
    p.mark('a gray morning', 0)
    scene.cloud(p, 'cloud', 2, 26, 75, 85, 26)
    scene.cloud(p, 'cloud', 16, 50, 74, 84, 29)
    grooves.brushes(p, 0, 8)
    for i in range(8):                       # pale ground, already continuous
        other = D2 if i % 2 == 0 else A1
        p.add('bass', 4 * i, [(D2, 2), (D2, 1), (other, 1)], vel=36 + i,
              gate=1.0)


def rain_density(t):
    if t < 16:
        return 0.0
    if t < STORM:
        return 0.08 + 0.16 * (t - 16) / 16           # first drips
    if t < BOLT1:
        return 0.26 + 0.22 * (t - STORM) / 25        # settling in
    if t < BOLT2:
        return 0.50 + 0.12 * (t - BOLT1) / 32        # steady rain
    if t < 104:
        return 0.85                                  # the downpour
    if t < 118:
        return max(0.05, 0.85 - 0.8 * (t - 104) / 12)
    return 0.0


def storm(p):
    p.mark('the storm', STORM)
    scene.rain(p, 16, 118, rain_density)
    # bass: brooding D-minor pulse, thickening with the rain
    for i in range(14):                              # b32-88, quarters
        bt = STORM + 4 * i
        low = Bb1 if i % 4 == 3 else D2
        p.add('bass', bt, [(D2, 1), (D2, 1), (A1, 1), (low, 1)],
              vel=48 + i, gate=0.96)
    for i in range(6):                               # b88-112, eighth pushes
        bt = 88 + 4 * i
        row = [D2, D2, C2, C2] if i % 2 == 0 else [Bb1, Bb1, A1, A1]
        p.add('bass', bt, [(n, 0.5) for n in row for _ in (0, 1)][:8],
              vel=62 + i, gate=0.85)
    grooves.storm_kit(p, STORM, 6, 0.15)
    grooves.storm_kit(p, 56, 8, 0.4)
    # lightning, then thunder — light before sound
    end1 = scene.bolt(p, BOLT1, 76, 48)
    grooves.thunder(p, end1 + 0.75)
    p.cue('lightning', BOLT1)
    end2 = scene.bolt(p, BOLT2, 80, 44)
    grooves.thunder(p, end2 + 0.6, big=True)
    p.cue('the big one', BOLT2)
    grooves.storm_kit(p, 96, 4, 0.8)                 # downpour groove


def the_turn(p):
    for i, pitch in enumerate((D2, C2, Bb1, A1, G1, F1)):   # walk down home
        p.note('bass', 116 + i, pitch, 1, vel=56 + 3 * i, gate=0.9)
    grooves.brushes(p, TURN, 1, vel=20)
    figures.press_roll(p, RAINBOW, 96)
    p.add('choir', 120.5, [(57, 0.5), (60, 1.0)], vel=72, vel_end=80)


# ------------------------------------------------------------ 2: the rainbow
RIP = [(j * 0.5, 0.5) for j in range(8)]
STRUT_R = [(0, 0.75), (0.75, 0.75), (1.5, 1.0), (2.5, 0.5), (3.0, 1.0)]
SHOUT_A = [(0, 0.5), (0.5, 0.5), (1.0, 1.0), (2.0, 0.5), (2.5, 0.5), (3.0, 1.0)]
SHOUT_B = [(0, 0.75), (0.75, 0.25), (1.0, 0.5), (1.5, 0.5), (2.0, 0.5),
           (2.5, 0.25), (2.75, 0.25), (3.0, 1.0)]


def bar_rhythm(bt, i):
    sl = arch_slope(s(bt + 2))
    if sl > 1.1:
        return RIP                                   # entry/exit rips
    if sl > 0.22:
        return STRUT_R                               # the climb/descent
    return SHOUT_A if i % 2 == 0 else SHOUT_B        # crown shout


def rainbow(p):
    p.mark('Roy G. Biv', RAINBOW)
    scene.cloud(p, 'cloud', 57, 77, 53, 68, 26)      # hides the entries
    scene.cloud(p, 'cloud', 141, 163, 53, 68, 26)    # hides the exits
    for i, bt in enumerate(range(RAINBOW, 314, 4)):
        rhythm = bar_rhythm(bt, i)
        for k, key in enumerate(STRIPES):
            for off, d in rhythm:
                tt = bt + off
                if not (ENTER[k] <= tt < EXIT[k]):
                    continue
                p.note(key, tt, stripe_pitch(s(tt), k), d,
                       vel=stripe_vel(s(tt)) + (2 if k == 0 else 0),
                       gate=0.97)
        if i == 24:
            p.cue('white light, split (F13)', bt)
    for k, key in enumerate(STRIPES):                # land into the cloud
        p.note(key, EXIT[k], stripe_pitch(s(EXIT[k]), k), 3.0, vel=70,
               gate=0.98)
    # the ground walks the changes underneath
    plan = [(122, F1), (138, Bb1), (146, F1), (154, D2), (162, Bb1),
            (170, C2), (178, F1), (194, F1), (242, D2), (258, Bb1),
            (274, C2), (290, F1), (316, F1)]
    for (t0, r), (t1, r_next) in zip(plan, plan[1:]):
        for bt in range(int(t0), int(t1), 4):
            lv = max(0.0, (arch(s(bt)) - scene.ARCH_FOOT) / scene.ARCH_RY)
            v = 74 + int(20 * lv)
            fifth = r + 7 if r + 7 <= F2 else r - 5
            appr = r_next + (1 if r_next < r else -1)
            last_bar = bt + 4 >= t1
            p.add('bass', bt,
                  [(r, 1.0), (fifth, 0.5), (r, 1.0),
                   (appr if last_bar else r, 0.5), (appr if last_bar else fifth, 0.5)],
                  vel=v, gate=0.9)
    grooves.strut(p, RAINBOW, 48,
                  level=lambda bt: max(0.15, min(1.0, (arch(s(bt)) - 62) / 24)))


# ------------------------------------------------------------ 3: sun & strut
LICK = [(0, 0.75, F1), (0.75, 0.25, F1), (1.0, 0.5, A1), (1.5, 0.5, Bb1),
        (2.0, 0.75, C2), (3.0, 0.5, Bb1), (3.5, 0.5, G1), (4.0, 0.75, F1),
        (5.0, 0.5, F2), (5.5, 0.5, E2), (6.0, 0.5, D2), (6.5, 0.5, C2),
        (7.0, 1.0, F1)]


def bass_lick(p, t, vel):
    for off, d, pitch in LICK:
        p.note('bass', t + off, pitch, d, vel=vel, gate=0.9)


def outro(p):
    p.mark('strut into the sun', OUTRO)
    bass_lick(p, OUTRO, 88)                          # bass takes fours...
    for k in range(8):
        p.perc(OUTRO + 0.5 * k * 2, 'hhc:e', vel=42)
        p.perc(OUTRO + 4 * (k // 4), 'kick:q', vel=60)
    grooves.drum_break(p, 324, 2)                    # ...the kit answers
    for k in range(8):
        p.note('bass', 324 + k, F1, 0.4, vel=54, gate=0.8)
    bass_lick(p, 332, 92)
    grooves.strut(p, 332, 2, level=0.55)
    for off, d, pitch, v in ((0, 2, F1, 60), (2, 2, C2, 56), (4, 2, F1, 52),
                             (6, 2, Bb1, 48), (8, 4, F1, 46)):
        p.note('bass', 340 + off, pitch, d, vel=v, gate=0.98)
    for k in range(8):                               # ground rests in the sun
        p.note('bass', 352 + 2 * k, F1, 1.2, vel=42, gate=1.0)


def sun(p):
    p.cue('the sun', SUN)
    scene.sun(p)
    grooves.sunshine(p, SUN + 1, 22)
    p.note('bass', 368, F1, 8, vel=62, gate=1.0)     # the last warm ground
    p.perc(368, 'kick:q', vel=56)
    p.perc(368, 'crash:h', vel=44)


def build() -> Piece:
    p = Piece(spectrum(), seed=1666,                 # Newton splits the light
              title='Roy G. Biv — a rain-to-rainbow jubilee')
    p.tempo(0, scene.BPM, 'with weather')
    p.meter(0, 4, 4)
    gray_morning(p)
    storm(p)
    the_turn(p)
    rainbow(p)
    outro(p)
    sun(p)
    return p


def main():
    p = build()
    OUT.mkdir(exist_ok=True)
    ok = assess.report(p)
    p.write(str(OUT / 'roy_g_biv.mid'), swing=0.58)
    p.write_marks(str(OUT / 'marks.json'))
    wav = OUT / 'roy_g_biv.wav'
    assess.pianoroll(p, str(OUT / 'roll.png'),
                     wav=str(wav) if wav.exists() else None,
                     legend_loc='upper center', lw=2.4)
    print()
    print(midi_report(str(OUT / 'roy_g_biv.mid')))
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
