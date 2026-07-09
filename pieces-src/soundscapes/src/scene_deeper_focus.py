"""Deeper Focus — D dorian, 60 bpm. Further down: darker, slower, tidal.

The same room as Focus, later at night: the center sinks a fifth (A -> D),
the clock slows (72 -> 60), the kalimba pulse becomes a half-note bass tide,
and the harmony moves three chords per cycle instead of four. Everything
stays dorian — the raised sixth keeps the dark from turning sad.

Stem map: bed 16 bars (always on) · pad-low 12×2 · haze 14×2 · murmur 10×2 ·
tide 8×2. Same pairwise-non-multiple bar set as Focus reassigned, so the
combined state recurs only every LCM(16,12,14,10,8) = 1680 bars ≈ 112 min.

Seam craft per layer (docs/02): bed and pad-low put a voice group across the
seam through the tail window; haze's last dyad crosses; murmur keeps the
file head and tail silent; tide is a grid layer whose half-note lattice
meets itself at the boundary, and a plucked bass decays on its own — no
sustain to break.
"""
from lib import R, voicing

import loopcraft

BPM = 60
ID = 'deeper-focus'
KEY = 'D dorian'

META = dict(
    title='Deeper Focus',
    concept='further down, where the work does itself.',
    accent='#6d94ad',
    about=[
        'Deeper Focus is the same room as Focus, later at night: the floor '
        'drops a fifth to D, the clock slows to sixty, and in place of the '
        'kalimba a bass rocks between root and fifth like a tide against a '
        'hull. Harmony circulates in threes — Dm, F, C — never arriving, '
        'never needing to.',
        'Five layers loop on cycles of 16, 12, 14, 10 and 8 bars, pairwise '
        'non-multiple, so their alignment never repeats inside a working '
        'session. The conductor is quieter here too: it drifts levels and '
        'rests voices, and the room mostly just breathes.',
    ],
)


# --------------------------------------------------------------- bed (16)
def bed(p):
    """The floor: D–A open fifth breathing in two overlapped groups.

    Same construction as the focus bed (docs/02, rule 2): the low group
    starts at bar 8 and rings two bars past the loop end under the next
    head's slow attack; the organ is the instant-attack constant."""
    L = loopcraft.loop_beats(16)                       # 64 beats, 64 s
    p.note('floor', 0, 'D2', L, vel=50, gate=1.0)
    p.note('floor', 0, 'A2', L, vel=42, gate=1.0)
    p.cc('floor', 0, 11, 92)
    # breath A: upper voices, bars 1-9
    p.note('bed', 0, 'A3', 36, vel=56, gate=1.0)
    p.note('bed', 0, 'D3', 36, vel=52, gate=1.0)
    p.note('bed', 8, 'D4', 20, vel=34, gate=1.0)       # faint octave color
    # breath B: low voices, bar 8 through the seam into the tail
    p.note('bed', 28, 'D2', 44, vel=60, gate=1.0)
    p.note('bed', 28, 'A2', 44, vel=56, gate=1.0)
    # one slow breath per loop, exact round trip
    p.hairpin('bed', 0, 32, 84, 98)
    p.hairpin('bed', 32, L, 98, 84)


# ----------------------------------------------------------- pad-low (12)
def _pad_cycle(p, chords, onsets, durs, lo, hi, vel):
    """Three overlapping chords per cycle; the last rings into the tail."""
    near = None
    for sym, at, dur in zip(chords, onsets, durs):
        v = voicing(sym, lo, hi, near=near)
        p.add('padlow', at, [(v, dur)], vel=vel, gate=1.0)
        near = v[len(v) // 2]


def pad_low_a(p):
    L = loopcraft.loop_beats(12)                       # 48 beats
    _pad_cycle(p, ['Dm9', 'Fmaj7', 'C6'],
               [0, 16, 32], [18, 18, 22], 'G2', 'D4', 58)
    p.hairpin('padlow', 0, 24, 86, 98)
    p.hairpin('padlow', 24, L, 98, 86)


def pad_low_b(p):
    L = loopcraft.loop_beats(12)
    _pad_cycle(p, ['Dm7', 'Gadd9', 'Am7'],             # i - IV - v, the dorian IV
               [0, 14, 30], [16, 18, 24], 'A2', 'E4', 55)
    p.hairpin('padlow', 0, 24, 84, 96)
    p.hairpin('padlow', 24, L, 96, 84)


# -------------------------------------------------------------- haze (14)
def _haze_dyads(p, dyads, vel_hi):
    """High halo-pad dyads, sparser and softer than the focus halo; the
    last one crosses the seam."""
    for (a, b), at, dur, dv in dyads:
        p.add('haze', at, [([a, b], dur)], vel=vel_hi + dv, gate=1.0)


def haze_a(p):
    L = loopcraft.loop_beats(14)                       # 56 beats
    _haze_dyads(p, [
        (('D5', 'A5'), 4, 12, 0),
        (('E5', 'B5'), 22, 12, -3),
        (('G5', 'D6'), 38, 8, -5),
        (('A5', 'E6'), 46, 16, -6),                    # rings to 62, in the tail
    ], 54)
    p.hairpin('haze', 0, 28, 80, 92)
    p.hairpin('haze', 28, L, 92, 80)


def haze_b(p):
    L = loopcraft.loop_beats(14)
    _haze_dyads(p, [
        (('A4', 'E5'), 6, 10, 0),
        (('C5', 'G5'), 20, 10, -2),
        (('D5', 'A5'), 34, 10, -4),
        (('E5', 'B5'), 46, 14, -5),                    # rings to 60
    ], 52)
    p.hairpin('haze', 0, 28, 80, 90)
    p.hairpin('haze', 28, L, 90, 80)


# ------------------------------------------------------------ murmur (10)
def _phrases(p, phrases, vel):
    """Low e-piano fragments with long rests; head and tail stay silent,
    which is a sparse layer's whole seam strategy."""
    for at, dsl_line in phrases:
        end = p.add('murmur', at, dsl_line, vel=vel, gate=0.95)
        p.pedal('murmur', at, min(end + 1.0, at + 8.0))


def murmur_a(p):
    _phrases(p, [
        (5,  'A3:h F3:h D3:w'),
        (19, 'C4:h A3:h G3:w'),
        (31, 'E3:h D3:w'),
    ], 48)


def murmur_b(p):
    _phrases(p, [
        (7,  'D4:h C4:h A3:w'),
        (21, 'F3:h G3:h A3:w'),
        (33, 'E3:w'),
    ], 46)


# -------------------------------------------------------------- tide (8)
def _tide(p, cell, vel):
    """Half-note bass rocking on the bar grid; the lattice meets itself at
    the seam and a pluck decays on its own — nothing to break."""
    end = p.add('tide', 0, R(cell, 4), vel=vel, gate=1.0)
    assert end == loopcraft.loop_beats(8), f'tide cell is not 2 bars ({end})'


def tide_a(p):
    _tide(p, 'D2:h. r:q A1:h r:h', 46)                 # 2 bars


def tide_b(p):
    _tide(p, 'D2:h r:h A1:q D2:q r:h', 44)             # 2 bars, small answer


# ------------------------------------------------------------------ stems
_LAYERS = {
    'bed':     dict(id='bed', name='bed', role='bed', always=True,
                    gain=0.80, gainRange=[0.68, 0.90], minOn=60, minOff=0),
    'pad-low': dict(id='pad-low', name='harmony', role='pad',
                    gain=0.60, gainRange=[0.42, 0.72], minOn=45, minOff=20),
    'haze':    dict(id='haze', name='haze', role='pad',
                    gain=0.42, gainRange=[0.28, 0.55], minOn=40, minOff=30),
    'murmur':  dict(id='murmur', name='murmur', role='melody',
                    gain=0.50, gainRange=[0.32, 0.62], minOn=30, minOff=35),
    'tide':    dict(id='tide', name='tide', role='texture',
                    gain=0.50, gainRange=[0.34, 0.64], minOn=45, minOff=35),
}

STEMS = [
    dict(slot='bed',     variant='a', bars=16, build=bed,       seed=60001, layer=_LAYERS['bed']),
    dict(slot='pad-low', variant='a', bars=12, build=pad_low_a, seed=60011, layer=_LAYERS['pad-low']),
    dict(slot='pad-low', variant='b', bars=12, build=pad_low_b, seed=60012, layer=_LAYERS['pad-low']),
    dict(slot='haze',    variant='a', bars=14, build=haze_a,    seed=60021, layer=_LAYERS['haze']),
    dict(slot='haze',    variant='b', bars=14, build=haze_b,    seed=60022, layer=_LAYERS['haze']),
    dict(slot='murmur',  variant='a', bars=10, build=murmur_a,  seed=60031, layer=_LAYERS['murmur']),
    dict(slot='murmur',  variant='b', bars=10, build=murmur_b,  seed=60032, layer=_LAYERS['murmur']),
    dict(slot='tide',    variant='a', bars=8,  build=tide_a,    seed=60041, layer=_LAYERS['tide']),
    dict(slot='tide',    variant='b', bars=8,  build=tide_b,    seed=60042, layer=_LAYERS['tide']),
]
