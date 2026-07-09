"""Focus — A dorian, 72 bpm. Steady, present, lightly pulsing.

Stem map (docs/03): bed 16 bars (always on) · pad-mid 10×2 · halo 12×2 ·
motif 14×2 · pulse 8×2. Loop lengths pairwise non-multiple, so the combined
state recurs only every LCM(16,10,12,14,8) = 1680 bars ≈ 93 minutes.

Harmonic cycle: Am – C – G – D (all diatonic to A dorian, no leading tone);
the bed's A–E fifth reads as home under all four, and every layer is
pan-diatonic so any subset in any phase alignment stays consonant.

Seam craft per layer (docs/02): continuous layers (bed, pads, halo) put a
voice group across the seam through the tail window; sparse layers (motif)
keep the file head and tail silent instead; grid layers (pulse) rely on the
eighth-note grid meeting itself exactly at the boundary.
"""
from lib import R, voicing

import loopcraft

BPM = 72
ID = 'focus'
KEY = 'A dorian'

META = dict(
    title='Focus',
    concept='one steady line of attention, held.',
    accent='#8fb7c9',
    about=[
        'Focus is a room to work inside: a floor of warm pad and organ, '
        'harmony that circulates without ever needing to arrive, a kalimba '
        'keeping a pulse you can lean on, and an electric piano that '
        'occasionally crosses the window.',
        'Five layers loop on cycles of 16, 10, 12, 14 and 8 bars — pairwise '
        'non-multiple, so their alignment never repeats inside a working '
        'session. A quiet conductor drifts their levels, rests them, and '
        'swaps their variants; the weather changes, the room stays.',
    ],
)


# --------------------------------------------------------------- bed (16)
def bed(p):
    """The floor: A–E open fifth breathing in two overlapped groups.

    Seam continuity by construction (docs/02, rule 2): the low group starts
    at bar 8 and rings two bars past the loop end, so it is still sounding
    under the next iteration's head while the upper group's slow pad attack
    swells in; the organ is the constant instant-attack anchor."""
    L = loopcraft.loop_beats(16)                       # 64 beats, 53.3 s
    # constant anchor — instant attack, so its seam break is inaudible
    p.note('floor', 0, 'A2', L, vel=52, gate=1.0)
    p.note('floor', 0, 'E3', L, vel=44, gate=1.0)
    p.cc('floor', 0, 11, 92)
    # breath A: upper voices, bars 1-9, soft attack under breath B's ring
    p.note('bed', 0, 'E3', 36, vel=58, gate=1.0)
    p.note('bed', 0, 'A3', 36, vel=52, gate=1.0)
    p.note('bed', 8, 'A4', 20, vel=36, gate=1.0)       # faint octave, bars 3-7
    # breath B: lower voices, bar 8 through the seam into the tail
    p.note('bed', 28, 'E2', 44, vel=62, gate=1.0)
    p.note('bed', 28, 'A2', 44, vel=58, gate=1.0)
    # one gentle channel-wide breath per loop, exact round trip
    p.hairpin('bed', 0, 32, 88, 104)
    p.hairpin('bed', 32, L, 104, 88)


# ----------------------------------------------------------- pad-mid (10)
def _pad_cycle(p, chords, onsets, durs, lo, hi, vel):
    """The cycle as overlapping pad chords; the last rings into the tail."""
    near = None
    for sym, at, dur in zip(chords, onsets, durs):
        v = voicing(sym, lo, hi, near=near)
        p.add('padmid', at, [(v, dur)], vel=vel, gate=1.0)
        near = v[len(v) // 2]


def pad_mid_a(p):
    L = loopcraft.loop_beats(10)                       # 40 beats
    _pad_cycle(p, ['Am9', 'Cmaj7', 'G', 'D'],
               [0, 10, 20, 30], [12, 12, 12, 18], 'A2', 'E4', 62)
    p.hairpin('padmid', 0, 20, 88, 102)
    p.hairpin('padmid', 20, L, 102, 88)


def pad_mid_b(p):
    L = loopcraft.loop_beats(10)
    _pad_cycle(p, ['Am7', 'C6', 'Gadd9', 'D'],
               [0, 12, 22, 32], [14, 12, 12, 16], 'B2', 'G4', 58)
    p.hairpin('padmid', 0, 24, 86, 100)
    p.hairpin('padmid', 24, L, 100, 86)


# -------------------------------------------------------------- halo (12)
def _halo_dyads(p, dyads, vel_hi):
    """High bowed-glass dyads; the last one crosses the seam."""
    for (a, b), at, dur, dv in dyads:
        p.add('halo', at, [([a, b], dur)], vel=vel_hi + dv, gate=1.0)


def halo_a(p):
    L = loopcraft.loop_beats(12)                       # 48 beats
    _halo_dyads(p, [
        (('E5', 'B5'), 2, 10, 0),
        (('D5', 'A5'), 14, 10, -4),
        (('G5', 'D6'), 26, 10, -2),
        (('A5', 'E6'), 40, 14, -6),                    # rings to 54, in the tail
    ], 62)
    p.hairpin('halo', 0, 24, 84, 98)
    p.hairpin('halo', 24, L, 98, 84)


def halo_b(p):
    L = loopcraft.loop_beats(12)
    _halo_dyads(p, [
        (('A4', 'E5'), 4, 8, 0),
        (('B4', 'F#5'), 16, 8, -3),
        (('E5', 'A5'), 28, 8, -1),
        (('G4', 'D5'), 36, 5, -5),
        (('E5', 'B5'), 42, 12, -4),                    # rings to 54
    ], 60)
    p.hairpin('halo', 0, 24, 84, 96)
    p.hairpin('halo', 24, L, 96, 84)


# ------------------------------------------------------------- motif (14)
def _phrases(p, phrases, vel):
    """E-piano fragments with long rests; head and tail stay silent, which
    is a sparse layer's whole seam strategy."""
    for at, dsl_line in phrases:
        end = p.add('motif', at, dsl_line, vel=vel, gate=0.95)
        p.pedal('motif', at, min(end + 1.0, at + 8.0))


def motif_a(p):
    _phrases(p, [
        (6,  'E4:q G4:q A4:h.'),
        (26, 'C5:q A4:q G4:q E4:h'),
        (44, 'D4:q E4:q G4:w'),
    ], 58)


def motif_b(p):
    _phrases(p, [
        (8,  'A4:q B4:q D5:h.'),
        (28, 'E5:q D5:q B4:q A4:h'),
        (44, 'G4:q E4:q A4:w'),
    ], 56)


# -------------------------------------------------------------- pulse (8)
def pulse_a(p):
    cell = ('A4:e C5:e E5:e r:e D5:e C5:e r:e A4:e '
            'E5:e r:e G5:e E5:e r:e D5:e C5:e r:e')    # 2 bars
    p.add('pulse', 0, R(cell, 4), vel=46, gate=0.9)


def pulse_b(p):
    cell = ('E5:e r:e A4:e r:e C5:e r:e B4:e r:e '
            'D5:e r:e E5:e r:e A4:e r:e G4:e r:e')     # 2 bars, sparser
    p.add('pulse', 0, R(cell, 4), vel=44, gate=0.9)


# ------------------------------------------------------------------ stems
_LAYERS = {
    'bed':     dict(id='bed', name='bed', role='bed', always=True,
                    gain=0.80, gainRange=[0.65, 0.90], minOn=60, minOff=0),
    'pad-mid': dict(id='pad-mid', name='harmony', role='pad',
                    gain=0.60, gainRange=[0.40, 0.75], minOn=45, minOff=20),
    'halo':    dict(id='halo', name='halo', role='pad',
                    gain=0.50, gainRange=[0.30, 0.65], minOn=40, minOff=25),
    'motif':   dict(id='motif', name='motif', role='melody',
                    gain=0.55, gainRange=[0.35, 0.70], minOn=30, minOff=30),
    'pulse':   dict(id='pulse', name='pulse', role='texture',
                    gain=0.45, gainRange=[0.30, 0.60], minOn=45, minOff=40),
}

STEMS = [
    dict(slot='bed',     variant='a', bars=16, build=bed,       seed=72001, layer=_LAYERS['bed']),
    dict(slot='pad-mid', variant='a', bars=10, build=pad_mid_a, seed=72011, layer=_LAYERS['pad-mid']),
    dict(slot='pad-mid', variant='b', bars=10, build=pad_mid_b, seed=72012, layer=_LAYERS['pad-mid']),
    dict(slot='halo',    variant='a', bars=12, build=halo_a,    seed=72021, layer=_LAYERS['halo']),
    dict(slot='halo',    variant='b', bars=12, build=halo_b,    seed=72022, layer=_LAYERS['halo']),
    dict(slot='motif',   variant='a', bars=14, build=motif_a,   seed=72031, layer=_LAYERS['motif']),
    dict(slot='motif',   variant='b', bars=14, build=motif_b,   seed=72032, layer=_LAYERS['motif']),
    dict(slot='pulse',   variant='a', bars=8,  build=pulse_a,   seed=72041, layer=_LAYERS['pulse']),
    dict(slot='pulse',   variant='b', bars=8,  build=pulse_b,   seed=72042, layer=_LAYERS['pulse']),
]
