"""Deeper Focus — C minor, 120 bpm. A heartbeat to work over.

Second take on this scene, composed from the measurements in
research/: 
a static C root all session long, an unbroken sub pulse in quarters at 120 that
*feels* like 60, a bass that talks in offbeat sixteenths with semitone
slide-approaches, hats in straight eighths, quiet blips on the e's and a's
with composed delay echoes, and a drone voiced like the overtone series of
one long C (G, E, Bb, D as whisper partials). Harmony never moves; all
change is texture. The dissonance budget is near zero: every layer draws
from C–D–Eb–G–Bb, so any subset in any phase alignment stays consonant.

Stem map: bed 16 bars (always on) · pulse 8×2 · acid 10×2 · ticks 6×2 ·
blip 14×2. LCM(16,8,10,6,14) = 1680 bars ≈ 56 min before the combined
state recurs. All loops are integer bars, and the engine re-enters layers
on the shared bar grid, so the sixteenth lattice stays locked scene-wide.

Seam craft per layer (docs/02): bed puts a voice group across the seam
through the tail window over an instant-attack organ anchor; pulse and
ticks are grid layers whose lattice meets itself at the boundary (pulse-a
ends on an "and-a" pickup that resolves onto the next iteration's downbeat);
acid and blip are sparse layers that keep the file head and tail silent.
"""
import loopcraft

BPM = 120
ID = 'deeper-focus'
KEY = 'C minor'

META = dict(
    title='Deeper Focus',
    concept='a heartbeat to work over, deep underground.',
    accent='#5f7d99',
    about=[
        'Deeper Focus is a basement room with a pulse: quarter-note sub '
        'bass at 120 that the body reads as a resting heart at 60, hats '
        'ticking straight eighths high above it, and a bass voice that '
        'speaks in offbeat sixteenths — on the e’s and a’s — '
        'sliding into its notes from a semitone below. The root is C for '
        'the whole session; what changes is never the chord, only the '
        'weather around the pulse.',
        'The design is measured, not guessed: it follows an analysis of a '
        'commercial focus soundscape (see research/) — '
        'pulse patterns quantized from the sub band, the five-layer '
        'vocabulary, echo blips, and a drone voiced as the overtone series '
        'of one long C. Five loops of 16, 8, 10, 6 and 14 bars share one '
        'sixteenth grid but realign only once an hour.',
    ],
)


# --------------------------------------------------------------- bed (16)
def bed(p):
    """One long C, voiced as its own overtone series.

    The organ anchor is the constant (instant attack, seam-proof); the pad
    breathes in two overlapped groups, each carrying root-and-fifth weight
    plus one whisper partial — E4 (5th harmonic) in group A, Bb3 (7th) in
    group B — so the color tilts slowly between major-third light and
    dominant-seventh dusk without a chord ever changing."""
    L = loopcraft.loop_beats(16)                       # 64 beats, 32 s
    p.note('floor', 0, 'C2', L, vel=44, gate=1.0)
    p.note('floor', 0, 'G2', L, vel=36, gate=1.0)
    p.cc('floor', 0, 11, 88)
    # breath A: bars 1-10, root voices + 5th-harmonic glow
    p.note('bed', 0, 'C3', 36, vel=54, gate=1.0)
    p.note('bed', 0, 'G3', 36, vel=46, gate=1.0)
    p.note('bed', 0, 'E4', 36, vel=24, gate=1.0)
    # breath B: bar 8 through the seam into the tail (ends at L+8 exactly)
    p.note('bed', 28, 'G2', 44, vel=52, gate=1.0)
    p.note('bed', 28, 'D3', 44, vel=44, gate=1.0)
    p.note('bed', 28, 'Bb3', 44, vel=24, gate=1.0)
    # one slow breath per loop, exact round trip
    p.hairpin('bed', 0, 32, 84, 96)
    p.hairpin('bed', 32, L, 96, 84)


# --------------------------------------------------------------- pulse (8)
def _thump(p, beat, vel):
    p.note('pulse', beat, 'C2', 1.0, vel=vel, gate=0.45)


def pulse_a(p):
    """Joel's heard pattern: three bars of plain quarters, then the fourth
    bar splits its last beat into eighths; the second cell adds an "and-a"
    sixteenth pickup that resolves onto the next iteration's downbeat."""
    for bar in range(8):
        base = bar * 4
        p.note('pulse', base, 'C1', 1.0, vel=56, gate=0.4)   # sub double
        split = bar in (3, 7)
        for b in range(3 if split else 4):
            _thump(p, base + b, 80 if b == 0 else 76)
        if split:
            p.note('pulse', base + 3, 'C2', 0.5, vel=74, gate=0.45)
            p.note('pulse', base + 3.5, 'C2', 0.5, vel=70, gate=0.45)
    p.note('pulse', 31.75, 'C2', 0.25, vel=58, gate=0.5)     # pickup at seam


def pulse_b(p):
    """The recharge-segment reading: quarters with a ghost sixteenth on the
    "a" of beat one — X..X|X...|X...|X... — and the same split fourth bar."""
    for bar in range(8):
        base = bar * 4
        p.note('pulse', base, 'C1', 1.0, vel=54, gate=0.4)
        split = bar in (3, 7)
        for b in range(3 if split else 4):
            _thump(p, base + b, 78 if b == 0 else 74)
        p.note('pulse', base + 0.75, 'C2', 0.25, vel=52, gate=0.5)  # ghost
        if split:
            p.note('pulse', base + 3, 'C2', 0.5, vel=72, gate=0.45)
            p.note('pulse', base + 3.5, 'C2', 0.5, vel=68, gate=0.45)


# --------------------------------------------------------------- acid (10)
def _line(p, events):
    """(beat, pitch, vel, dur) tuples; grace notes are just short low-vel
    neighbors a 32nd before the target — the GM stand-in for a 303 slide."""
    for beat, pitch, vel, dur in events:
        p.note('acid', beat, pitch, dur, vel=vel, gate=0.5)


def acid_a(p):
    """Offbeat sixteenths around the pulse's quarters: slots 3 and 7 of the
    eight-sixteenth cycle, phrases every two bars, head and tail silent."""
    _line(p, [
        (4.75, 'C2', 62, 0.5), (5.5, 'C2', 58, 0.25),
        (6.625, 'B1', 40, 0.125), (6.75, 'C2', 64, 0.5),

        (12.75, 'C2', 60, 0.25), (13.75, 'Bb1', 54, 0.25),
        (14.5, 'C2', 62, 0.5), (15.25, 'Eb2', 56, 0.25), (15.75, 'C2', 58, 0.25),

        (20.5, 'C2', 58, 0.5), (21.75, 'C2', 62, 0.25),
        (22.75, 'G2', 50, 0.25), (23.5, 'C2', 60, 0.5),

        (28.625, 'C#2', 40, 0.125), (28.75, 'C2', 64, 0.5),
        (30.5, 'C2', 58, 0.5), (32.75, 'Bb1', 54, 0.25), (34.5, 'C2', 60, 1.0),
    ])


def acid_b(p):
    """Sparser and duskier: longer rests, more slides, one ninth (D2)."""
    _line(p, [
        (8.75, 'C2', 60, 0.5), (9.5, 'Eb2', 52, 0.25), (10.75, 'C2', 62, 0.5),

        (18.625, 'B1', 38, 0.125), (18.75, 'C2', 62, 0.5),
        (20.75, 'Bb1', 52, 0.25), (21.5, 'C2', 58, 0.5),

        (28.75, 'C2', 60, 0.25), (29.5, 'D2', 50, 0.25),
        (30.75, 'C2', 62, 0.5), (32.5, 'C2', 54, 1.0),
    ])


# --------------------------------------------------------------- ticks (6)
def ticks_a(p):
    """Straight eighths on the closed hat — X.X.X.X. — with a maracas grain
    on the "a" of beats two and four. A grid layer: seam-proof by lattice."""
    L = int(loopcraft.loop_beats(6))                   # 24 beats
    for beat in range(L):
        p.note('ticks', beat, 42, 0.25, vel=30)
        p.note('ticks', beat + 0.5, 42, 0.25, vel=22)
    for bar in range(6):
        p.note('ticks', bar * 4 + 1.75, 70, 0.25, vel=18)
        p.note('ticks', bar * 4 + 3.75, 70, 0.25, vel=18)


def ticks_b(p):
    """The night reading: everything displaced to the offbeat, plus a soft
    pedal hat on beat three of each bar."""
    L = int(loopcraft.loop_beats(6))
    for beat in range(L):
        p.note('ticks', beat + 0.5, 42, 0.25, vel=24)
    for bar in range(6):
        p.note('ticks', bar * 4 + 2, 44, 0.25, vel=20)


# --------------------------------------------------------------- blip (14)
def _echo(p, at, pitch, vel, n=3):
    """A blip and its composed delay trail: dotted-eighth echoes, -8ish dB
    per repeat. The echoes are score events so the visualization shows them."""
    for k in range(n):
        p.note('blip', at + 0.75 * k, pitch, 0.4,
               vel=max(16, round(vel * 0.6 ** k)), gate=0.9)


def blip_a(p):
    """The "e-and-a" voice: two-note figures on offbeat sixteenths, four
    phrases per loop, everything from C minor pentatonic plus the ninth."""
    _echo(p, 8.25, 'D4', 46, n=3)
    _echo(p, 8.75, 'C4', 40, n=2)

    _echo(p, 20.5, 'Eb4', 44, n=3)
    _echo(p, 21.25, 'D4', 38, n=2)

    _echo(p, 32.25, 'G4', 42, n=3)
    _echo(p, 33.0, 'Eb4', 36, n=2)

    _echo(p, 44.75, 'C4', 40, n=2)
    _echo(p, 45.5, 'D4', 34, n=2)


def blip_b(p):
    """Higher and scarcer: the same voice further off in the dark."""
    _echo(p, 12.25, 'G4', 42, n=3)
    _echo(p, 12.75, 'Bb4', 36, n=2)

    _echo(p, 28.5, 'D5', 40, n=3)
    _echo(p, 29.25, 'Bb4', 34, n=2)

    _echo(p, 40.75, 'G4', 40, n=2)
    _echo(p, 41.5, 'F4', 34, n=2)


# ------------------------------------------------------------------ stems
_LAYERS = {
    'bed':   dict(id='bed', name='drone', role='bed', always=True,
                  gain=0.78, gainRange=[0.62, 0.88], minOn=60, minOff=0),
    'pulse': dict(id='pulse', name='pulse', role='bass',
                  gain=0.66, gainRange=[0.52, 0.78], minOn=120, minOff=15),
    'acid':  dict(id='acid', name='bass voice', role='melody',
                  gain=0.50, gainRange=[0.34, 0.62], minOn=40, minOff=30),
    'ticks': dict(id='ticks', name='ticks', role='texture',
                  gain=0.40, gainRange=[0.26, 0.52], minOn=45, minOff=30),
    'blip':  dict(id='blip', name='blips', role='melody',
                  gain=0.52, gainRange=[0.34, 0.66], minOn=30, minOff=35),
}

STEMS = [
    dict(slot='bed',   variant='a', bars=16, build=bed,     seed=120001, layer=_LAYERS['bed']),
    dict(slot='pulse', variant='a', bars=8,  build=pulse_a, seed=120011, layer=_LAYERS['pulse']),
    dict(slot='pulse', variant='b', bars=8,  build=pulse_b, seed=120012, layer=_LAYERS['pulse']),
    dict(slot='acid',  variant='a', bars=10, build=acid_a,  seed=120021, layer=_LAYERS['acid']),
    dict(slot='acid',  variant='b', bars=10, build=acid_b,  seed=120022, layer=_LAYERS['acid']),
    dict(slot='ticks', variant='a', bars=6,  build=ticks_a, seed=120031, layer=_LAYERS['ticks']),
    dict(slot='ticks', variant='b', bars=6,  build=ticks_b, seed=120032, layer=_LAYERS['ticks']),
    dict(slot='blip',  variant='a', bars=14, build=blip_a,  seed=120041, layer=_LAYERS['blip']),
    dict(slot='blip',  variant='b', bars=14, build=blip_b,  seed=120042, layer=_LAYERS['blip']),
]
