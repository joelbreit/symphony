"""Motivate — E aeolian, 104 bpm. The building-montage scene (docs/05).

Composed music, not weather: every stem realizes the same 16-bar harmonic
form, and all loop lengths are multiples of it, so any combination of
playing layers is always on the same bar of the same progression. That
coordination is what buys real harmony, a real theme, and counterpoint —
the things the phase-drift scenes structurally could not have. Endless
variation comes from the conductor instead: variants are alternate composed
realizations of the form, rests/returns snap to the cycle (quantizeBars),
and the seam of every loop is written as a resolution, not a cut.

THE FORM (one chord per bar):

    | Em | C | G | D |   statement          (the "axis" anthem row)
    | Em | C | G | D |   restatement
    | Am7 | Bm7 | C | D | the riser — roots climb stepwise
    | Em | C | G | D |   peak and return

Bar 16's D resolves stepwise up into bar 1's Em, so the loop *is* a
cadence: the theme ends on F# and lands on E across the seam; the bass
walks A–B–C–D up the scale and arrives on E at the loop point.

Stem map: ground 16 (always) · engine 16×2 (always) · strings 16×2 ·
theme 32×2 (horns / celli) · descant 32 flute + 16 celesta. Dynamics stay
mp–mf: the montage is determined, not triumphant — it has to survive an
hour of someone else's work.

Seam craft (docs/02): bass, piano, celesta and marcato strings are grid /
decay layers, seam-proof by nature; legato strings ring their last chord
through the tail window; the themes cross the seam melodically (F# -> E);
flute keeps the file head and final bar silent.
"""
from lib import B, fit, parse_chord, voicing

import loopcraft

BPM = 104
ID = 'motivate'
KEY = 'E aeolian'

META = dict(
    title='Motivate',
    concept='a building montage that never cuts away.',
    accent='#c9a34e',
    about=[
        'Motivate is the soundtrack of a montage: a bass that walks with '
        'intent, a piano engine turning over the changes, strings that '
        'swell through a four-bar riser, and a theme — stated by horns, '
        'answered by celli — that climbs more than it settles. Every '
        'sixteen bars the harmony leans stepwise back into home, so the '
        'loop is a resolution, never a cut.',
        'Unlike the Focus rooms, every layer here plays the same form: '
        'variants are alternate performances of it, sections return only '
        'on its downbeat, and a quiet conductor decides which parts of '
        'the arrangement are on. The montage keeps building; it never '
        'arrives, and it never stops.',
    ],
)

# One chord per bar; every stem reads from this chart (docs/05).
CHART = ['Em', 'C', 'G', 'D',
         'Em', 'C', 'G', 'D',
         'Am7', 'Bm7', 'C', 'D',
         'Em', 'C', 'G', 'D']

CYCLE = 16  # bars in the form


# -------------------------------------------------------------- ground (16)
GROUND = (
    'E2:q. E2:e B1:q E2:q '    # Em — the dotted figure is the scene's stride
    'C2:q. C2:e G1:q C2:q '    # C
    'G1:q. G1:e D2:q G1:q '    # G
    'D2:q. D2:e A1:q D2:q '    # D
    'E2:q. E2:e B1:q E2:q '    # Em
    'C2:q. C2:e G1:q C2:q '    # C
    'G1:q. G1:e D2:q B1:q '    # G — B walks down toward the riser
    'D2:q. D2:e A1:q D2:q '    # D
    'A1:q. A1:e E2:q A1:q '    # Am7 — the riser: roots climb
    'B1:q. B1:e F#2:q B1:q '   # Bm7
    'C2:q. C2:e G2:q C2:q '    # C
    'D2:q D2:q C2:q B1:q '     # D — turn, stepping down to relaunch
    'E2:q. E2:e B1:q E2:q '    # Em — peak row
    'C2:q. C2:e G1:q C2:q '    # C
    'G1:q. G1:e B1:q D2:q '    # G — begins the climb home
    'A1:q B1:q C2:q D2:q'      # D — walks up through the seam onto E
)


def ground(p):
    """The stride: a bass line with real contour on the changes; pluck
    decay is seam-proof, and bar 16 walks scalewise into bar 1's E."""
    B(GROUND, 16)
    p.add('bass', 0, GROUND, vel=58, gate=0.95)


# -------------------------------------------------------------- engine (16)
def _engine(p, wave, vels):
    """Piano ostinato following the chart: 8 eighths per bar, voiced per
    chord (root / fifth / tenth region). Grid layer — the eighth lattice
    meets itself at the seam; the riser bars get a velocity lift."""
    for bar, sym in enumerate(CHART):
        _, _, pcs = parse_chord(sym)
        root = fit(pcs[0], 'E2', 'D3')
        fifth = fit(pcs[2], 'A2', 'G3', near=root + 7)
        tenth = fit(pcs[1], 'E3', 'D4', near=root + 16)
        high = fit(pcs[0], 'E3', 'D4', near=tenth)
        tones = dict(r=root, f=fifth, t=tenth, o=root + 12, h=high)
        lift = 6 if 8 <= bar <= 11 else 0
        for i, (tone, vel) in enumerate(zip(wave, vels)):
            p.note('piano', bar * 4 + i * 0.5, tones[tone], 0.5,
                   vel=vel + lift, gate=0.9)


def engine_a(p):
    # pulsing: low root anchored, tenth on the offbeats — the time-lapse cell
    _engine(p, 'rfthofth', [60, 46, 52, 46, 56, 46, 52, 46])


def engine_b(p):
    # rising arpeggio wave — the lift variant
    _engine(p, 'rfothtof', [58, 46, 50, 52, 54, 50, 48, 46])


# ------------------------------------------------------------- strings (16)
def _voicings(near0='B3'):
    near, out = near0, []
    for sym in CHART:
        v = voicing(sym, 'G3', 'G4', near=near)
        out.append(v)
        near = v[len(v) // 2]
    return out


def strings_a(p):
    """Legato: one close voicing per bar, overlapped, swelling through the
    riser; the last chord rings through the tail window (docs/02 rule 2)."""
    L = loopcraft.loop_beats(16)
    for bar, v in enumerate(_voicings()):
        dur = 12 if bar == 15 else 4.6
        p.add('str', bar * 4, [(v, dur)], vel=58, gate=1.0)
    p.hairpin('str', 0, 16, 86, 94)
    p.hairpin('str', 16, 32, 94, 88)
    p.hairpin('str', 32, 48, 88, 106)    # the riser
    p.hairpin('str', 48, 60, 106, 94)
    p.hairpin('str', 60, L, 94, 92)      # seam lands a notch above the start


def strings_b(p):
    """Marcato: pulsing quarter chords — the driving-strings variant.
    Grid layer; the quarter lattice meets itself at the seam."""
    for bar, v in enumerate(_voicings('G3')):
        vel = 62 if 8 <= bar <= 11 else 54
        for beat in range(4):
            p.add('str', bar * 4 + beat, [(v, 1)], vel=vel, gate=0.8)


# --------------------------------------------------------------- theme (32)
# The theme proper: stated in cycle 1, developed in cycle 2. Its last note
# (F#, the third of D) resolves stepwise onto the next iteration's first
# note (E) across the seam — the join is a cadence.

HORN_1 = (
    'E4:q. F#4:e G4:q A4:q '     # Em — the climb figure
    'B4:h A4:q G4:q '            # C
    'D4:q G4:q B4:q A4:q '       # G
    'F#4:h. r:q '                # D
    'E4:q. F#4:e G4:q B4:q '     # Em — sequence, reaching higher
    'C5:h B4:q A4:q '            # C
    'B4:q A4:q G4:q A4:q '       # G
    'F#4:h r:h '                 # D
    'A4:w '                      # Am7 — the riser: long tones, climbing
    'B4:w '                      # Bm7
    'C5:h D5:h '                 # C
    'D5:w '                      # D
    'E5:q. B4:e G4:q B4:q '      # Em — the peak
    'C5:h A4:h '                 # C
    'B4:q G4:q A4:q F#4:q '      # G
    'F#4:h. r:q'                 # D — F# leans across the seam onto E
)

HORN_2 = (
    'E4:e F#4:e G4:q. A4:e B4:q '  # Em — development: the figure in eighths
    'C5:q B4:e A4:e B4:h '         # C
    'B4:e A4:e G4:q D5:q B4:q '    # G
    'A4:h F#4:h '                  # D
    'B4:q. C5:e B4:q G4:q '        # Em
    'C5:q E5:q D5:q C5:q '         # C
    'D5:h B4:q G4:q '              # G
    'A4:q F#4:q A4:h '             # D
    'A4:q C5:q E5:h '              # Am7 — riser as arpeggios now
    'F#4:q B4:q D5:h '             # Bm7
    'G4:q C5:q E5:h '              # C
    'F#4:q A4:q D5:h '             # D
    'E5:h D5:q B4:q '              # Em — peak, then the wind-down
    'C5:h. A4:q '                  # C
    'G4:h B4:h '                   # G
    'A4:h F#4:h'                   # D — resolves to E across the seam
)


def theme_a(p):
    """Horns: statement then development."""
    B(HORN_1, 16)
    B(HORN_2, 16)
    L = loopcraft.loop_beats(32)
    p.add('hn', 0, HORN_1, vel=64, gate=0.95)
    p.add('hn', 64, HORN_2, vel=68, gate=0.95)
    p.cc('hn', 0, 11, 94)
    p.hairpin('hn', 32, 48, 94, 106)     # riser 1
    p.hairpin('hn', 48, 64, 106, 94)
    p.hairpin('hn', 96, 112, 94, 108)    # riser 2, a shade further
    p.hairpin('hn', 112, L, 108, 96)     # seam a notch above the start


CELLO_1 = (
    'E3:q G3:q B3:q. C4:e '      # Em — the answer theme: warmer, lower
    'C4:h B3:q G3:q '            # C
    'D4:h B3:q G3:q '            # G
    'A3:h. F#3:q '               # D
    'E3:q G3:q B3:q D4:q '       # Em
    'E4:h. C4:q '                # C
    'D4:q B3:q G3:q A3:q '       # G
    'F#3:h. r:q '                # D
    'A3:h. E4:q '                # Am7 — riser
    'D4:h. B3:q '                # Bm7
    'C4:h E4:h '                 # C
    'D4:h F#4:h '                # D
    'G4:h. E4:q '                # Em — peak
    'E4:q C4:q G3:h '            # C
    'B3:h D4:h '                 # G
    'A3:h F#3:h'                 # D — steps onto E across the seam
)

CELLO_2 = (
    'E3:e G3:e B3:q G3:q E3:q '    # Em — development: flowing eighths
    'C4:q E4:e D4:e C4:q G3:q '    # C
    'B3:q D4:q G3:h '              # G
    'A3:q F#3:q A3:h '             # D
    'B3:q G3:q E3:q G3:q '         # Em
    'A3:q C4:q E4:h '              # C
    'D4:q. C4:e B3:q G3:q '        # G
    'F#3:h A3:h '                  # D
    'A3:q E4:q C4:h '              # Am7 — riser
    'B3:q F#4:q D4:h '             # Bm7
    'C4:q G4:q E4:h '              # C
    'D4:q F#4:q A3:h '             # D
    'G4:h E4:q B3:q '              # Em — peak, then home
    'C4:h. G3:q '                  # C
    'G3:h B3:h '                   # G
    'A3:h F#3:h'                   # D — resolves to E across the seam
)


def theme_b(p):
    """Celli: the answer theme — same form, warmer register."""
    B(CELLO_1, 16)
    B(CELLO_2, 16)
    L = loopcraft.loop_beats(32)
    p.add('vc', 0, CELLO_1, vel=60, gate=0.97)
    p.add('vc', 64, CELLO_2, vel=64, gate=0.97)
    p.cc('vc', 0, 11, 94)
    p.hairpin('vc', 32, 48, 94, 104)
    p.hairpin('vc', 48, 64, 104, 94)
    p.hairpin('vc', 96, 112, 94, 106)
    p.hairpin('vc', 112, L, 106, 96)


# ------------------------------------------------------------- descant (32)
FLUTE_R1 = ('E5:h. F#5:q '    # Am7 — enters at the riser, doubling the climb
            'F#5:h. G5:q '    # Bm7
            'G5:h A5:h '      # C
            'B5:h. A5:q')     # D
FLUTE_P1 = ('B5:h G5:h '      # Em — hovering over the peak
            'A5:h E5:h '      # C
            'D5:h G5:h '      # G
            'F#5:w')          # D
FLUTE_R2 = ('E5:h. A5:q '     # Am7 — second riser, reaching further
            'B5:h. D6:q '     # Bm7
            'C6:h D6:h '      # C
            'D6:w')           # D
FLUTE_P2 = ('E6:h B5:h '      # Em — the highest point in the scene
            'C6:h. G5:q '     # C
            'B5:w '           # G
            'r:w')            # D — final bar silent: the seam strategy


def descant_a(p):
    """Flute: silent except at risers and peaks; head and tail silent."""
    for dsl in (FLUTE_R1, FLUTE_P1, FLUTE_R2, FLUTE_P2):
        B(dsl, 4)
    p.add('fl', 32, FLUTE_R1, vel=46, gate=0.9)
    p.add('fl', 48, FLUTE_P1, vel=48, gate=0.9)
    p.add('fl', 96, FLUTE_R2, vel=50, gate=0.9)
    p.add('fl', 112, FLUTE_P2, vel=50, gate=0.9)


def descant_b(p):
    """Celesta: glints on alternate downbeats — decay is seam-proof."""
    glints = [
        (0,  'E5:s G5:s B5:s E6:q'),    # Em
        (8,  'D5:s G5:s B5:s D6:q'),    # G
        (16, 'E5:s B5:s E6:s G6:q'),    # Em
        (24, 'B4:s D5:s G5:s B5:q'),    # G
        (32, 'A4:s C5:s E5:s A5:q'),    # Am7
        (40, 'C5:s E5:s G5:s C6:q'),    # C
        (48, 'E5:s G5:s B5:s E6:q'),    # Em
        (56, 'G5:s D5:s B4:s G4:q'),    # G — falling, into the seam
    ]
    for at, dsl in glints:
        p.add('cel', at, dsl, vel=52, gate=0.9)


# ------------------------------------------------------------------ stems
_LAYERS = {
    'ground':  dict(id='ground', name='ground', role='bed', always=True,
                    gain=0.60, gainRange=[0.48, 0.72], minOn=60, minOff=0,
                    quantizeBars=CYCLE),
    'engine':  dict(id='engine', name='engine', role='texture', always=True,
                    gain=0.52, gainRange=[0.38, 0.66], minOn=60, minOff=0,
                    quantizeBars=CYCLE),
    'strings': dict(id='strings', name='strings', role='pad',
                    gain=0.58, gainRange=[0.40, 0.72], minOn=60, minOff=25,
                    quantizeBars=CYCLE),
    'theme':   dict(id='theme', name='theme', role='melody',
                    gain=0.58, gainRange=[0.42, 0.70], minOn=75, minOff=45,
                    quantizeBars=CYCLE),
    'descant': dict(id='descant', name='descant', role='texture',
                    gain=0.40, gainRange=[0.26, 0.52], minOn=40, minOff=50,
                    quantizeBars=CYCLE),
}

STEMS = [
    dict(slot='ground',  variant='a', bars=16, build=ground,    seed=104001, layer=_LAYERS['ground']),
    dict(slot='engine',  variant='a', bars=16, build=engine_a,  seed=104011, layer=_LAYERS['engine']),
    dict(slot='engine',  variant='b', bars=16, build=engine_b,  seed=104012, layer=_LAYERS['engine']),
    dict(slot='strings', variant='a', bars=16, build=strings_a, seed=104021, layer=_LAYERS['strings']),
    dict(slot='strings', variant='b', bars=16, build=strings_b, seed=104022, layer=_LAYERS['strings']),
    dict(slot='theme',   variant='a', bars=32, build=theme_a,   seed=104031, layer=_LAYERS['theme']),
    dict(slot='theme',   variant='b', bars=32, build=theme_b,   seed=104032, layer=_LAYERS['theme']),
    dict(slot='descant', variant='a', bars=32, build=descant_a, seed=104041, layer=_LAYERS['descant']),
    dict(slot='descant', variant='b', bars=16, build=descant_b, seed=104042, layer=_LAYERS['descant']),
]
