#!/usr/bin/env python3
"""
HIGH STREET RIOT
A vamp-jam for an oversized Dixieland band, in loving memory of running out of songs.

G minor. 4/4 swung. The sousaphone leads; everyone else piles on.

Form (124 bars):
  1   The shrug        sousa alone, the riff born fully formed
  5   The pile-on I    + drums (press roll -> two-beat), banjo chunk
  9   The pile-on II   + trombones laddering 3rds above the riff
  13  The shout        full band; horn stabs interlock with the riff's breaths
  21  The wail         the anthem: screamed descents over Gm-Gm-Cm-D7#9
  29  The floor drop   sousa + banjo + hats only
  33  Trombone lead    rude, smeared; pads creep in behind
  45  Cornet lead      declamatory hammering; bones stab back
  57  Clarinet lead    over the iv vamp (Cm), rockets up D7, ladder rebuilds
  69  The argument     bone vs cornet trade twos, everyone butts in, all-at-once
  81  The stomp        stop-time: Gm and Ab9 slams against the riff (the riot chord)
  93  The collapse     full choke; drums alone; sousa mutters back in
  97  The riot         riff 8va + anthem on top + cluster hammers + Ab9->Gm slams
  121 The wink         dead stop / sousa snarl lick alone / two stabs / one fat G
"""
import json
import random
import subprocess
import sys
from pathlib import Path

import music21 as m21
from music21 import stream, note, chord, tempo, instrument, meter, key as m21key

random.seed(1924)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

BAR = 4.0          # quarterLengths per bar
SWING = 0.12       # offbeat 8ths land at +0.62 of the beat (light, 160bpm-appropriate)

# ---------------------------------------------------------------- event store
# Each part is a list of dicts: {off, pitches[(name|midi)], dur, vel}
PARTS = {p: [] for p in
         ["cornet", "clarinet", "sax", "bone1", "bone2", "sousa", "banjo", "drums"]}

def off(bar, beat):
    """bar is 1-indexed, beat is 0..3.99 within the bar."""
    return (bar - 1) * BAR + beat

def N(part, bar, beat, dur, pitches, vel):
    """Add a note/chord. pitches: str | int | list of either."""
    if not isinstance(pitches, list):
        pitches = [pitches]
    PARTS[part].append(dict(off=off(bar, beat), dur=dur, pitches=pitches, vel=int(vel)))

# GM drum map
KICK, SNARE, STICK, HATC, HATP, HATO = 36, 38, 37, 42, 44, 46
RIDE, BELL, CRASH, CRASH2 = 51, 53, 49, 57
TOMF, TOML, TOMM, TOMH, COWB, WBH, WBL = 41, 43, 47, 50, 56, 76, 77

def D(bar, beat, drum, vel, dur=0.25):
    N("drums", bar, beat, dur, drum, vel)

# ------------------------------------------------------------- idiom helpers
def smear_into(part, bar, beat, target, vel, n=3):
    """Tailgate smear: fast chromatic 32nds rising into a target downbeat."""
    t = m21.pitch.Pitch(target)
    for i in range(n, 0, -1):
        p = m21.pitch.Pitch()
        p.midi = t.midi - i
        N(part, bar, beat - 0.125 * i, 0.12, p.nameWithOctave, vel - 14 - 4 * i)

def falloff(part, bar, beat, from_pitch, vel, n=4):
    """Brass fall: loose descending chromatics after a held note ends."""
    f = m21.pitch.Pitch(from_pitch)
    for i in range(1, n + 1):
        p = m21.pitch.Pitch()
        p.midi = f.midi - i
        N(part, bar, beat + 0.11 * (i - 1), 0.1, p.nameWithOctave, max(28, vel - 16 - 9 * i))

def curl(part, bar, beat, target, vel):
    """Clarinet curl: quick upper-lower turn into a held target."""
    t = m21.pitch.Pitch(target)
    up, dn = m21.pitch.Pitch(), m21.pitch.Pitch()
    up.midi, dn.midi = t.midi + 2, t.midi - 1
    N(part, bar, beat, 0.125, up.nameWithOctave, vel - 18)
    N(part, bar, beat + 0.125, 0.125, t.nameWithOctave, vel - 12)
    N(part, bar, beat + 0.25, 0.125, dn.nameWithOctave, vel - 15)
    N(part, bar, beat + 0.375, 0.125, t.nameWithOctave, vel - 6)

def trill(part, bar, beat, a, b, total, vel):
    """32nd-note alternation a-b-a-b..."""
    t, step = 0.0, 0.125
    i = 0
    while t < total - 1e-6:
        N(part, bar, beat + t, step, a if i % 2 == 0 else b, vel - (4 if i % 2 else 0) - i)
        t += step
        i += 1

# ------------------------------------------------------------------ THE RIFF
# bar A (strut up):  G . . G  Bb C C# D     bar B (snarl down):  D . . Db C Bb C F#
RIFF_A = [(0.0, 1.25, "G", 112), (1.5, 0.5, "G", 96), (2.0, 0.5, "B-", 100),
          (2.5, 0.5, "C+", 98), (3.0, 0.5, "C#+", 104), (3.5, 0.5, "D+", 108)]
RIFF_B = [(0.0, 1.25, "D+", 112), (1.5, 0.5, "D-+", 106), (2.0, 0.5, "C+", 100),
          (2.5, 0.5, "B-", 96), (3.0, 0.5, "C+", 100), (3.5, 0.5, "F#", 110)]

def riff_pitch(token, root_midi):
    """Decode riff token relative to a root. Suffix '+' = the octave row above root.
    Tokens are degrees of the riff shape: G(root) B-(b3) C(4) C#(#4) D(5) D-(b5) F#(maj7 below).
    """
    base = {"G": 0, "B-": 3, "C": 5, "C#": 6, "D": 7, "D-": 6, "F#": -1}
    tok = token[:-1] if token.endswith("+") else token
    p = m21.pitch.Pitch()
    p.midi = root_midi + base[tok]
    return p.nameWithOctave

def add_riff(part, bar, root="G2", vel_scale=1.0, both=True, octave=0):
    """Write the 2-bar riff starting at `bar`, transposed so `root` is the tonic."""
    rm = m21.pitch.Pitch(root).midi + 12 * octave
    for beat, dur, tok, vel in RIFF_A:
        N(part, bar, beat, dur, riff_pitch(tok, rm), min(122, vel * vel_scale))
    if both:
        for beat, dur, tok, vel in RIFF_B:
            N(part, bar + 1, beat, dur, riff_pitch(tok, rm), min(122, vel * vel_scale))

def sousa_twobeat(bar, a="G2", b="D2", vel=96, pickup=None):
    N("sousa", bar, 0.0, 0.95, a, vel)
    N("sousa", bar, 2.0, 0.95, b, vel - 6)
    if pickup:
        N("sousa", bar, 3.5, 0.5, pickup, vel - 4)

# ------------------------------------------------------------------- rhythm section
GM6   = ["G3", "B-3", "D4", "E4"]
CM6   = ["G3", "C4", "E-4", "A4"]
D7c   = ["F#3", "A3", "C4", "D4"]
AB9   = ["A-3", "C4", "G-4", "B-4"]
GM69  = ["G3", "B-3", "E4", "A4"]

def banjo_bar(bar, voicing=GM6, vel=80, tremolo=False):
    if tremolo:
        for k in range(16):
            N("banjo", bar, k * 0.25, 0.22, voicing,
              vel + (10 if k % 4 == 2 else 0) - (4 if k % 2 else 0))
        return
    for beat in range(4):
        v = vel + (13 if beat % 2 == 1 else 0)          # 2 & 4 accents
        for i, s in enumerate(voicing):                  # tiny strum roll
            N("banjo", bar, beat + i * 0.013, 0.55 if beat % 2 else 0.38, s, v - i * 3)

def drums_twobeat(bar, vel=72, hat=True):
    D(bar, 0.0, KICK, vel + 16, 0.4)
    D(bar, 2.0, KICK, vel + 8, 0.4)
    D(bar, 1.0, WBH, vel + 14)
    D(bar, 3.0, WBL, vel + 16)
    if hat:
        for k in range(8):
            b = k * 0.5
            D(bar, b, HATC, vel - 22 + (10 if b in (1.0, 3.0) else 0) - (6 if k % 2 else 0))

def drums_fourfloor(bar, vel=92, crash=False, ride=True):
    for beat in range(4):
        D(bar, beat, KICK, vel + (8 if beat == 0 else 0), 0.4)
    D(bar, 1.0, SNARE, vel + 10)
    D(bar, 3.0, SNARE, vel + 12)
    D(bar, 1.75, SNARE, max(20, vel - 52))   # ghosts
    D(bar, 3.75, SNARE, max(20, vel - 50))
    if ride:
        for k in range(8):
            b = k * 0.5
            D(bar, b, RIDE, vel - 26 + (8 if k % 2 == 0 else 0))
        D(bar, 2.0, BELL, vel - 8)
    if crash:
        D(bar, 0.0, CRASH, vel + 14, 1.5)

def drum_fill(bar, startbeat=2.0, vel=86, big=False):
    """Snare ruff into the next downbeat; big version walks the toms."""
    seq = [SNARE, SNARE, TOMH, SNARE, TOMM, TOMM, TOMF, TOMF] if big else \
          [SNARE] * 5 + [TOMM, TOMF, TOMF]
    n = len(seq)
    span = 4.0 - startbeat
    for i, dr in enumerate(seq):
        D(bar, startbeat + span * i / n, dr, vel - 18 + int(20 * i / n))

def press_roll(bar, beats=(0.0, 2.0), vel0=26, vel1=64):
    t0, t1 = beats
    k, t = 0, t0
    while t < t1 - 1e-6:
        # dur 0.18 keeps roll strokes under the swing threshold (rolls stay even)
        D(bar, t, SNARE, vel0 + int((vel1 - vel0) * (t - t0) / (t1 - t0)) + (3 if k % 2 else 0),
          dur=0.18)
        t += 0.125
        k += 1

# ============================================================== THE SECTIONS
SHRUG, PILE1, PILE2, SHOUT, WAIL, FLOOR = 1, 5, 9, 13, 21, 29
BONESOLO, CORNSOLO, CLARSOLO, ARGUE = 33, 45, 57, 69
STOMP, COLLAPSE, RIOT, TAG = 81, 93, 97, 121
END = 125  # first bar after the music

# ---- 1-4 THE SHRUG: sousa alone, twice through, confident -------------------
for c in range(2):
    add_riff("sousa", SHRUG + 2 * c, vel_scale=0.97 + 0.03 * c)

# ---- 5-8 PILE-ON I: drums sneak in with a press roll, banjo chunks ----------
for c in range(2):
    add_riff("sousa", PILE1 + 2 * c, vel_scale=1.0)
press_roll(PILE1, (0.0, 1.75), 24, 60)
D(PILE1, 2.0, WBH, 70); D(PILE1, 3.0, WBL, 76)
for k in range(4):
    D(PILE1, 2.0 + k * 0.5, HATC, 44 + (6 if k % 2 == 0 else 0))
for b in range(PILE1 + 1, PILE2):
    drums_twobeat(b, 70 + 2 * (b - PILE1))
for b in range(PILE1, PILE2):
    banjo_bar(b, GM6, 74 + 2 * (b - PILE1))

# ---- 9-12 PILE-ON II: trombones ladder up in 3rds, clarinet curls in --------
for c in range(2):
    add_riff("sousa", PILE2 + 2 * c, vel_scale=1.02)
    add_riff("bone2", PILE2 + 2 * c, root="G3", vel_scale=0.82)  # riff 8va
for b in range(PILE2, SHOUT):
    drums_twobeat(b, 76)
    banjo_bar(b, GM6, 82)
drum_fill(SHOUT - 1, 3.0, 84)
# bone1: parallel 3rds above the riff, entering halfway (bars 11-12)
b1 = PILE2 + 2
for beat, dur, p, v in [(0.0, 1.25, "B-3", 88), (1.5, 0.5, "B-3", 76), (2.0, 0.5, "D4", 80),
                        (2.5, 0.5, "E-4", 78), (3.0, 0.5, "E4", 84), (3.5, 0.5, "F4", 88)]:
    N("bone1", b1, beat, dur, p, v)
for beat, dur, p, v in [(0.0, 1.25, "F4", 90), (1.5, 0.5, "E4", 86), (2.0, 0.5, "E-4", 80),
                        (2.5, 0.5, "D4", 76), (3.0, 0.5, "E-4", 80), (3.5, 0.5, "A3", 88)]:
    N("bone1", b1 + 1, beat, dur, p, v)
curl("clarinet", PILE2 + 3, 2.0, "F#5", 88)
N("clarinet", PILE2 + 3, 2.5, 1.5, "F#5", 90)   # hangs on the leading tone -> shout

# ---- 13-20 THE SHOUT: cornet calls, the gang answers in the riff's breaths --
calls = [
    # (pickup_prev_beat, [(beat, dur, pitch, vel)...])  one call per 2-bar cell
    (("D4", 3.5), [(0.0, 1.0, "G4", 104), (1.5, 0.5, "B-4", 98), (2.0, 1.5, "D5", 108)]),
    (("D4", 3.5), [(0.0, 0.5, "G4", 102), (0.5, 0.5, "G4", 98), (1.5, 0.5, "B-4", 100),
                   (2.0, 0.75, "D5", 106), (2.75, 1.0, "E-5", 110)]),
    (("F4", 3.5), [(0.0, 1.0, "B-4", 106), (1.5, 0.5, "C5", 100), (2.0, 0.5, "D5", 104),
                   (2.5, 0.5, "D-5", 112), (3.0, 1.0, "C5", 104)]),
    (("G4", 3.5), [(0.0, 0.5, "B-4", 104), (0.5, 0.5, "C5", 102), (1.0, 0.5, "C#5", 106),
                   (1.5, 1.25, "D5", 112), (3.0, 0.5, "B-4", 100), (3.5, 0.5, "C5", 104)]),
]
GANG = dict(bone1="D4", bone2="F3", sax="B-3", clarinet="D5")  # stab voicing
for c in range(4):
    bar = SHOUT + 2 * c
    add_riff("sousa", bar, vel_scale=1.05)
    banjo_bar(bar, GM6, 86); banjo_bar(bar + 1, GM6, 86)
    drums_twobeat(bar, 80 + 2 * c); drums_twobeat(bar + 1, 80 + 2 * c)
    (pk, pkb), phr = calls[c]
    if bar > SHOUT or True:
        N("cornet", bar - 1, pkb, 0.5, pk, 92)
    for beat, dur, p, v in phr:
        N("cornet", bar, beat, dur, p, v)
    if c in (0, 1):
        falloff("cornet", bar, phr[-1][0] + phr[-1][1], phr[-1][2], phr[-1][3])
    # the gang: "HEY!" in the riff's breaths
    if c >= 1:
        for inst, p in GANG.items():
            N(inst, bar, 1.0, 0.35, p, 96 + 3 * c)
    for inst, p in GANG.items():
        N(inst, bar + 1, 1.0, 0.35, p, 100 + 3 * c)
        if c >= 1:
            N(inst, bar + 1, 2.5, 0.3, p, 90 + 3 * c)
            N(inst, bar + 1, 3.0, 0.3, p, 96 + 3 * c)
    if c >= 2:  # bones double the snarl tail up the octave: rude unison with the boss
        N("bone1", bar + 1, 1.5, 1.0, "D-4", 102)
        N("bone2", bar + 1, 1.5, 1.0, "D-3", 100)
drum_fill(WAIL - 1, 2.5, 90, big=True)

# ---- 21-28 THE WAIL: the anthem ---------------------------------------------
# harmony: bars 21-24 Gm (riff), 25-26 Cm (riff on C), 27-28 D7#9 (riff on D)
ANTHEM = [  # (bar_offset, beat, dur, cornet_pitch, vel)
    (0, 0.0, 3.0, "D5", 110), (0, 3.5, 0.5, "C5", 96),
    (1, 0.0, 1.0, "B-4", 102), (1, 1.0, 0.5, "C5", 98), (1, 1.5, 1.5, "D-5", 112),
    (1, 3.0, 0.5, "C5", 100), (1, 3.5, 0.5, "B-4", 96),
    (2, 0.0, 2.0, "G4", 100), (2, 2.0, 0.5, "B-4", 98), (2, 2.5, 0.5, "C5", 100),
    (2, 3.0, 0.5, "C#5", 104), (2, 3.5, 0.5, "D5", 108),
    (3, 0.0, 2.5, "D5", 112), (3, 3.5, 0.5, "E-5", 106),
    (4, 0.0, 2.5, "E-5", 112), (4, 2.5, 0.5, "D5", 100), (4, 3.0, 1.0, "C5", 102),
    (5, 0.0, 2.0, "G5", 116), (5, 2.0, 0.5, "F5", 104), (5, 2.5, 0.5, "E-5", 102),
    (5, 3.0, 1.0, "D5", 104),
    (6, 0.0, 2.0, "F5", 114), (6, 2.0, 1.0, "E-5", 108), (6, 3.0, 1.0, "C5", 102),
    (7, 0.0, 0.5, "E-5", 104), (7, 0.5, 0.5, "D5", 100), (7, 1.0, 0.5, "C5", 98),
    (7, 1.5, 0.5, "B-4", 96), (7, 2.0, 2.0, "A-4", 114),  # the pincer: Ab above...
]
def write_anthem(bar0, cornet=True, clar8va=True, sax8vb=True, vmul=1.0):
    for bo, beat, dur, p, v in ANTHEM:
        v = min(122, v * vmul)
        if cornet:
            N("cornet", bar0 + bo, beat, dur, p, v)
        if sax8vb:
            pp = m21.pitch.Pitch(p); pp.midi -= 12
            N("sax", bar0 + bo, beat, dur, pp.nameWithOctave, v - 14)
        if clar8va:
            pp = m21.pitch.Pitch(p)
            if pp.midi + 12 <= m21.pitch.Pitch("E-6").midi:
                pp.midi += 12
                N("clarinet", bar0 + bo, beat, dur, pp.nameWithOctave, v - 16)
    if cornet:
        falloff("cornet", bar0 + 0, 3.0, "D5", 100)   # fall out of the first scream
        falloff("cornet", bar0 + 3, 2.5, "D5", 102)
def anthem_rhythm_bed(bar0, vmul=1.0, banjo=True):
    """Riff + banjo under one 8-bar anthem cycle."""
    add_riff("sousa", bar0, "G2", 1.06 * vmul)
    add_riff("sousa", bar0 + 2, "G2", 1.06 * vmul)
    add_riff("sousa", bar0 + 4, "C3", 1.04 * vmul)     # the riff transposes: iv
    add_riff("sousa", bar0 + 6, "D3", 1.08 * vmul)     # and V. the cell IS the changes
    if banjo:
        for i in range(4):
            banjo_bar(bar0 + i, GM6, 88)
        banjo_bar(bar0 + 4, CM6, 88); banjo_bar(bar0 + 5, CM6, 88)
        banjo_bar(bar0 + 6, D7c, 90); banjo_bar(bar0 + 7, D7c, 92)

write_anthem(WAIL)
anthem_rhythm_bed(WAIL)
# clarinet shake instead of parallel at the G5 peak bar (G6 would be glass-shatter)
trill("clarinet", WAIL + 5, 0.0, "C6", "D6", 1.5, 96)
N("clarinet", WAIL + 5, 2.0, 2.0, "B-5", 92)
# trombones: tailgate answers, then pads, then the pincer's other jaw
for c in (0, 1):
    smear_into("bone1", WAIL + 2 * c + 1, 0.0, "F3", 96)
    N("bone1", WAIL + 2 * c + 1, 0.0, 1.5, "F3", 98)
    N("bone2", WAIL + 2 * c + 1, 0.0, 1.5, "D3", 94)
    N("bone1", WAIL + 2 * c + 1, 1.5, 1.0, "D-4", 104)  # lean on the snarl with the boss
    N("bone2", WAIL + 2 * c + 1, 1.5, 1.0, "D-3", 100)
N("bone1", WAIL + 4, 0.0, 4.0, "G3", 88); N("bone2", WAIL + 4, 0.0, 4.0, "E-3", 86)
N("bone1", WAIL + 5, 0.0, 4.0, "G3", 90); N("bone2", WAIL + 5, 0.0, 4.0, "E-3", 88)
N("bone1", WAIL + 6, 0.0, 4.0, "C4", 92); N("bone2", WAIL + 6, 0.0, 4.0, "F#3", 90)
N("bone1", WAIL + 7, 0.0, 2.0, "C4", 94); N("bone1", WAIL + 7, 2.0, 2.0, "B-3", 96)
N("bone2", WAIL + 7, 0.0, 2.0, "F#3", 92); N("bone2", WAIL + 7, 2.0, 2.0, "F#3", 96)
drums_twobeat(WAIL, 84); D(WAIL, 0.0, CRASH, 100, 1.5)
for b in range(WAIL + 1, WAIL + 7):
    drums_twobeat(b, 84 + (b - WAIL))
drum_fill(WAIL + 3, 3.0, 86)
drum_fill(WAIL + 7, 2.0, 92, big=True)
D(WAIL + 7, 0.0, KICK, 96, 0.4); D(WAIL + 7, 1.0, SNARE, 92)

# ---- 29-32 THE FLOOR DROP: subito — just the vamp, naked --------------------
for c in range(2):
    add_riff("sousa", FLOOR + 2 * c, vel_scale=0.78)
for b in range(FLOOR, BONESOLO):
    banjo_bar(b, GM6, 58)
    for k in range(8):
        D(b, k * 0.5, HATC, 36 + (8 if k % 4 == 2 else 0) - (5 if k % 2 else 0))
    D(b, 1.0, HATP, 44); D(b, 3.0, HATP, 46)

# ---- 33-44 TROMBONE LEAD: rude, smeared, talks in short barks ---------------
for b in range(BONESOLO, BONESOLO + 8):     # sousa simplifies to 2-beat under the solo
    pk = "F#2" if (b - BONESOLO) % 4 == 3 else None
    sousa_twobeat(b, "G2", "D2", 88, pickup=pk)
add_riff("sousa", BONESOLO + 8, vel_scale=0.96)   # riff returns: "wrap it up"
add_riff("sousa", BONESOLO + 10, vel_scale=1.0)
for b in range(BONESOLO, CORNSOLO):
    banjo_bar(b, GM6, 64 + (b - BONESOLO))
    drums_twobeat(b, 64 + (b - BONESOLO), hat=True)
drum_fill(BONESOLO + 7, 3.0, 78)
drum_fill(CORNSOLO - 1, 2.5, 84)

SOLO_BONE = [
    (0, [(1.5, 1.0, "G3", 100, "smear"), (3.0, 0.5, "F3", 92), (3.5, 0.5, "D3", 90)]),
    (1, [(0.0, 1.5, "B-2", 98), (2.5, 0.5, "C3", 92), (3.0, 0.75, "D-3", 104),
         (3.75, 0.25, "C3", 88)]),
    (2, [(0.0, 2.0, "G2", 100), (2.5, 0.25, "G2", 88), (2.75, 0.25, "G2", 90),
         (3.0, 0.5, "G2", 96), (3.5, 0.5, "B-2", 94)]),
    (3, [(0.0, 1.5, "D3", 102, "smear"), (3.0, 0.5, "F3", 94), (3.5, 0.5, "F#3", 100)]),
    (4, [(0.0, 0.5, "G3", 104), (1.0, 0.5, "G3", 98), (1.5, 0.5, "G3", 100),
         (2.0, 1.0, "B-3", 104), (3.0, 0.75, "A-3", 110), (3.75, 0.25, "G3", 92)]),
    (5, [(0.0, 0.5, "F3", 96), (0.5, 0.5, "D3", 92), (1.0, 0.75, "E-3", 98),
         (1.75, 0.25, "D3", 88), (2.0, 0.5, "C3", 92), (2.5, 0.5, "B-2", 90),
         (3.0, 1.0, "C3", 94)]),
    (6, [(0.5, 1.5, "D-3", 108), (2.0, 0.5, "C3", 94), (2.5, 0.5, "B-2", 92),
         (3.0, 1.0, "G2", 96)]),
    (7, [(1.0, 0.5, "F2", 90), (1.5, 0.5, "F#2", 96), (2.0, 0.5, "G2", 98),
         (2.5, 0.5, "B-2", 96), (3.0, 0.5, "C3", 98), (3.5, 0.5, "D3", 102)]),
    (8, [(0.0, 2.0, "D4", 108, "smear", "fall"), (3.0, 1.0, "B-3", 100)]),
    (9, [(0.0, 1.5, "C4", 104), (2.0, 1.0, "D-4", 110), (3.0, 1.0, "C4", 100)]),
    (10, [(0.0, 0.5, "G3", 102), (0.5, 0.5, "G3", 98), (1.0, 0.5, "G3", 100),
          (2.0, 1.0, "F3", 96), (3.0, 1.0, "G3", 100)]),
    (11, [(0.0, 1.0, "B-3", 104, "smear"), (1.5, 0.5, "G3", 96), (2.0, 2.0, "F#3", 108)]),
]
for bo, notes_ in SOLO_BONE:
    for item in notes_:
        beat, dur, p, v = item[:4]
        if "smear" in item[4:]:
            smear_into("bone1", BONESOLO + bo, beat, p, v)
        N("bone1", BONESOLO + bo, beat, dur, p, v)
        if "fall" in item[4:]:
            falloff("bone1", BONESOLO + bo, beat + dur, p, v)
# pads creep in behind the last 4 bars (the band can't help itself)
N("bone2", BONESOLO + 8, 0.0, 4.0, "D3", 70); N("sax", BONESOLO + 8, 0.0, 4.0, "F3", 66)
N("bone2", BONESOLO + 9, 0.0, 4.0, "D3", 74); N("sax", BONESOLO + 9, 0.0, 4.0, "F3", 70)
N("bone2", BONESOLO + 10, 0.0, 4.0, "E-3", 78); N("sax", BONESOLO + 10, 0.0, 4.0, "G3", 74)
N("bone2", BONESOLO + 11, 0.0, 4.0, "D3", 82); N("sax", BONESOLO + 11, 0.0, 4.0, "F3", 78)

# ---- 45-56 CORNET LEAD: the ego. hammered repeats and high rips -------------
for b in range(CORNSOLO, CORNSOLO + 8):
    pk = "F#2" if (b - CORNSOLO) % 4 == 3 else None
    sousa_twobeat(b, "G2", "D2", 90, pickup=pk)
add_riff("sousa", CORNSOLO + 8, vel_scale=1.0)
add_riff("sousa", CORNSOLO + 10, vel_scale=1.04)
for b in range(CORNSOLO, CLARSOLO):
    banjo_bar(b, GM6, 70 + (b - CORNSOLO))
    drums_twobeat(b, 70 + (b - CORNSOLO))
drum_fill(CORNSOLO + 7, 3.0, 82)
drum_fill(CLARSOLO - 1, 2.0, 88, big=True)

SOLO_CORNET = [
    (0, [(0.5, 0.5, "G4", 100), (1.0, 0.5, "G4", 102), (1.5, 0.5, "G4", 104),
         (2.0, 1.0, "G4", 108), (3.0, 1.0, "B-4", 104)]),
    (1, [(0.0, 1.5, "D5", 110, "fall"), (2.5, 0.5, "C5", 96), (3.0, 0.5, "B-4", 94),
         (3.5, 0.5, "C5", 98)]),
    (2, [(0.0, 0.5, "D5", 106), (0.5, 0.5, "D5", 102), (1.0, 0.5, "E-5", 108),
         (1.5, 0.5, "D5", 102), (2.0, 0.5, "C5", 98), (2.5, 0.5, "B-4", 96),
         (3.0, 1.0, "G4", 100)]),
    (3, [(1.0, 0.5, "F4", 92), (1.5, 0.5, "F#4", 98), (2.0, 0.5, "G4", 100),
         (2.5, 0.5, "B-4", 100), (3.0, 0.5, "C5", 102), (3.5, 0.5, "C#5", 106)]),
    (4, [(0.0, 2.0, "D5", 112, "fall"), (2.5, 0.5, "D5", 100), (3.0, 1.0, "D5", 106)]),
    (5, [(0.0, 1.0, "F5", 112), (1.0, 0.5, "E-5", 104), (1.5, 0.5, "D5", 100),
         (2.0, 0.5, "C5", 98), (2.5, 1.0, "D-5", 110), (3.5, 0.5, "C5", 96)]),
    (6, [(0.0, 0.75, "B-4", 102), (0.75, 0.25, "G4", 92), (1.0, 0.5, "B-4", 100),
         (1.5, 0.5, "C5", 100), (2.0, 0.5, "D5", 104), (2.5, 0.5, "G4", 94),
         (3.0, 0.5, "B-4", 100), (3.5, 0.5, "C5", 102)]),
    (7, [(0.0, 0.5, "D5", 106), (1.0, 0.5, "E-5", 108), (2.0, 0.5, "E5", 110),
         (3.0, 1.0, "F5", 112)]),
    (8, [(0.0, 2.5, "G5", 118, "fall"), (3.0, 0.5, "F5", 104), (3.5, 0.5, "D5", 100)]),
    (9, [(0.0, 0.5, "E-5", 104), (0.5, 0.5, "D5", 100), (1.0, 1.0, "D-5", 112),
         (2.0, 0.5, "C5", 98), (2.5, 0.5, "B-4", 96), (3.0, 1.0, "C5", 100)]),
    (10, [(0.0, 0.5, "D5", 106), (0.5, 0.5, "D5", 108), (1.0, 0.5, "D5", 110),
          (1.5, 0.5, "D5", 112), (2.0, 2.0, "D5", 114)]),
    (11, [(0.0, 1.5, "D-5", 114), (2.0, 0.75, "C5", 102), (2.75, 0.25, "B-4", 94),
          (3.0, 0.5, "A4", 96), (3.5, 0.5, "A-4", 102)]),
]
for bo, notes_ in SOLO_CORNET:
    for item in notes_:
        beat, dur, p, v = item[:4]
        N("cornet", CORNSOLO + bo, beat, dur, p, v)
        if "fall" in item[4:]:
            falloff("cornet", CORNSOLO + bo, beat + dur, p, v)
# bones stab back behind the second half (shout-backs return)
for c in range(2, 6):
    bar = CORNSOLO + 2 * c
    N("bone1", bar, 1.0, 0.35, "D4", 88); N("bone2", bar, 1.0, 0.35, "F3", 86)
    N("bone1", bar + 1, 1.0, 0.35, "D4", 92); N("bone2", bar + 1, 1.0, 0.35, "F3", 90)
    N("bone1", bar + 1, 2.5, 0.3, "E-4", 88); N("bone2", bar + 1, 2.5, 0.3, "G3", 86)
curl("clarinet", CORNSOLO + 10, 2.0, "D6", 92)
N("clarinet", CORNSOLO + 10, 2.5, 1.5, "D6", 96)   # shriek photobomb
N("clarinet", CORNSOLO + 11, 0.0, 1.5, "D-6", 100)

# ---- 57-68 CLARINET LEAD: over the iv vamp, rockets up D7, ladder rebuilds --
add_riff("sousa", CLARSOLO, "C3", 1.0)        # the riff moves to C minor
add_riff("sousa", CLARSOLO + 2, "C3", 1.0)
add_riff("sousa", CLARSOLO + 4, "C3", 1.02)
sousa_twobeat(CLARSOLO + 6, "D3", "A2", 94)   # D pedal climb
sousa_twobeat(CLARSOLO + 7, "D3", "C3", 96, pickup="C#3")
add_riff("sousa", CLARSOLO + 8, "G2", 1.04)   # home, ladder rebuilding
add_riff("sousa", CLARSOLO + 10, "G2", 1.06)
for b in range(CLARSOLO, CLARSOLO + 6):
    banjo_bar(b, CM6, 74 + (b - CLARSOLO))
    drums_twobeat(b, 74 + (b - CLARSOLO))
banjo_bar(CLARSOLO + 6, D7c, 82); banjo_bar(CLARSOLO + 7, D7c, 86)
drums_twobeat(CLARSOLO + 6, 82); drums_twobeat(CLARSOLO + 7, 84)
drum_fill(CLARSOLO + 7, 2.5, 86)
for b in range(CLARSOLO + 8, ARGUE):
    banjo_bar(b, GM6, 84)
    drums_twobeat(b, 84 + (b - CLARSOLO - 8))
drum_fill(ARGUE - 1, 2.0, 92, big=True)

SOLO_CLAR = [
    (0, [(0.0, 1.0, "G5", 100, "curl"), (1.0, 0.5, "E-5", 92), (1.5, 0.5, "F5", 94),
         (2.0, 0.5, "G5", 98), (2.5, 0.5, "A-5", 102), (3.0, 0.5, "G5", 96),
         (3.5, 0.5, "F5", 92)]),
    (1, [(0.0, 0.5, "E-5", 92), (0.5, 0.5, "D5", 90), (1.0, 1.0, "C5", 94),
         (2.5, 0.5, "G5", 96), (3.0, 0.5, "F#5", 102), (3.5, 0.5, "G5", 100)]),
    (2, [(0.0, 0.25, "C5", 88), (0.25, 0.25, "D5", 90), (0.5, 0.25, "E-5", 92),
         (0.75, 0.25, "F5", 94), (1.0, 0.25, "G5", 98), (1.25, 0.25, "A-5", 100),
         (1.5, 0.25, "G5", 96), (1.75, 0.25, "F5", 92), (2.0, 1.0, "E-5", 96),
         (3.0, 0.5, "D5", 90), (3.5, 0.5, "E-5", 92)]),
    (3, [(0.0, 0.5, "F5", 94), (0.5, 0.5, "G5", 98), (1.0, 1.5, "A-5", 106),
         (2.5, 0.5, "G5", 96), (3.0, 0.5, "E-5", 92), (3.5, 0.5, "C5", 90)]),
    (4, [("trill", 0.0, "C6", "D6", 1.5, 102), (1.5, 0.5, "B-5", 96), (2.0, 0.5, "G5", 94),
         (2.5, 0.5, "E-5", 92), (3.0, 1.0, "G5", 96)]),
    (5, [(0.0, 0.5, "E-5", 94), (0.5, 0.5, "C5", 90), (1.0, 1.0, "G4", 88),
         (2.0, 1.0, "B-4", 92), (3.0, 1.0, "C5", 96)]),
    (6, [(0.0, 0.5, "A4", 92), (0.5, 0.5, "C5", 94), (1.0, 0.5, "D5", 96),
         (1.5, 0.5, "E-5", 100), (2.0, 1.0, "F5", 106), (3.0, 0.5, "E-5", 98),
         (3.5, 0.5, "D5", 94)]),
    (7, [(0.0, 0.5, "C#5", 98), (0.5, 0.5, "D5", 96), (1.0, 0.5, "F5", 100),
         (1.5, 0.5, "A5", 104), (2.0, 0.5, "C6", 108), (2.5, 0.5, "C#6", 112),
         (3.0, 1.0, "D6", 114)]),
    (8, [(0.0, 2.0, "D6", 112, "fall"), (2.5, 0.5, "B-5", 100), (3.0, 0.5, "C6", 102),
         (3.5, 0.5, "D-6", 110)]),
    (9, [(0.0, 0.5, "C6", 102), (0.5, 0.5, "B-5", 98), (1.0, 1.5, "E-6", 116),
         (2.5, 0.5, "D6", 104), (3.0, 0.5, "C6", 100), (3.5, 0.5, "B-5", 96)]),
    (10, [(0.0, 0.25, "C6", 104), (0.25, 0.25, "B-5", 100), (0.5, 0.25, "A-5", 98),
          (0.75, 0.25, "G5", 96), (1.0, 0.25, "F5", 94), (1.25, 0.25, "G5", 92),
          (1.5, 0.25, "F5", 90), (1.75, 0.25, "E-5", 92), (2.0, 0.5, "D5", 94),
          (2.5, 0.5, "D-5", 104), (3.0, 0.5, "C5", 96), (3.5, 0.5, "B-4", 92)]),
    (11, [(0.0, 0.5, "G4", 92), (0.5, 0.5, "B-4", 94), (1.0, 0.5, "C5", 96),
          (1.5, 0.5, "C#5", 100), (2.0, 1.0, "D5", 104), (3.0, 0.5, "F5", 100),
          (3.5, 0.5, "F#5", 106)]),
]
for bo, notes_ in SOLO_CLAR:
    for item in notes_:
        if item[0] == "trill":
            _, beat, a, b_, total, v = item
            trill("clarinet", CLARSOLO + bo, beat, a, b_, total, v)
            continue
        beat, dur, p, v = item[:4]
        if "curl" in item[4:]:
            curl("clarinet", CLARSOLO + bo, beat - 0.5, p, v)
        N("clarinet", CLARSOLO + bo, beat, dur, p, v)
        if "fall" in item[4:]:
            falloff("clarinet", CLARSOLO + bo, beat + dur, p, v)
# the ladder rebuilds underneath (bars 65-68): bone2 riff 8va, bone1 3rds, sax pad
add_riff("bone2", CLARSOLO + 8, "G3", 0.78)
add_riff("bone2", CLARSOLO + 10, "G3", 0.84)
for beat, dur, p, v in [(0.0, 1.25, "B-3", 80), (1.5, 0.5, "B-3", 72), (2.0, 0.5, "D4", 76),
                        (2.5, 0.5, "E-4", 74), (3.0, 0.5, "E4", 78), (3.5, 0.5, "F4", 82)]:
    N("bone1", CLARSOLO + 10, beat, dur, p, v)
for beat, dur, p, v in [(0.0, 1.25, "F4", 84), (1.5, 0.5, "E4", 80), (2.0, 0.5, "E-4", 76),
                        (2.5, 0.5, "D4", 72), (3.0, 0.5, "E-4", 76), (3.5, 0.5, "A3", 82)]:
    N("bone1", CLARSOLO + 11, beat, dur, p, v)
N("sax", CLARSOLO + 8, 0.0, 4.0, "G3", 64); N("sax", CLARSOLO + 9, 0.0, 4.0, "B-3", 68)
N("sax", CLARSOLO + 10, 0.0, 4.0, "G3", 72); N("sax", CLARSOLO + 11, 0.0, 4.0, "B-3", 76)

# ---- 69-80 THE ARGUMENT: trading twos that stop taking turns ----------------
for c in range(6):
    add_riff("sousa", ARGUE + 2 * c, vel_scale=1.06)
    banjo_bar(ARGUE + 2 * c, GM6, 88); banjo_bar(ARGUE + 2 * c + 1, GM6, 88)
for b in range(ARGUE, STOMP):
    drums_twobeat(b, 86)
drum_fill(ARGUE + 3, 3.0, 86); drum_fill(ARGUE + 7, 3.0, 90)
drum_fill(STOMP - 1, 2.0, 96, big=True)
# bone statement (rude, low)
smear_into("bone1", ARGUE, 0.0, "B-3", 104)
for beat, dur, p, v in [(0.0, 1.0, "B-3", 106), (1.5, 0.5, "G3", 96), (2.0, 0.5, "G3", 98),
                        (2.5, 1.5, "A-3", 110)]:
    N("bone1", ARGUE, beat, dur, p, v)
for beat, dur, p, v in [(0.0, 0.5, "G3", 100), (0.5, 0.5, "F3", 94), (1.0, 1.0, "D-3", 106),
                        (2.0, 2.0, "G2", 102)]:
    N("bone1", ARGUE + 1, beat, dur, p, v)
# cornet comeback (high, clipped, mocking)
for beat, dur, p, v in [(0.0, 0.5, "D5", 106), (0.5, 0.5, "D5", 102), (1.0, 0.5, "D5", 104),
                        (2.0, 0.5, "E-5", 108), (2.5, 0.5, "D5", 102), (3.0, 1.0, "B-4", 100)]:
    N("cornet", ARGUE + 2, beat, dur, p, v)
for beat, dur, p, v in [(0.0, 1.0, "C5", 102), (1.5, 0.5, "C#5", 106), (2.0, 2.0, "D5", 112)]:
    N("cornet", ARGUE + 3, beat, dur, p, v)
falloff("cornet", ARGUE + 3, 4.0, "D5", 104)
# bone, ruder (bone2 joins in 3rds on the second bar)
smear_into("bone1", ARGUE + 4, 0.0, "D-4", 110)
for beat, dur, p, v in [(0.0, 1.5, "D-4", 112), (2.0, 0.5, "C4", 102), (2.5, 0.5, "B-3", 98),
                        (3.0, 1.0, "C4", 104)]:
    N("bone1", ARGUE + 4, beat, dur, p, v)
for beat, dur, p, v in [(0.0, 0.5, "G3", 104), (0.5, 0.5, "G3", 100), (1.0, 0.5, "G3", 102),
                        (1.5, 0.5, "F#3", 108), (2.0, 2.0, "G3", 106)]:
    N("bone1", ARGUE + 5, beat, dur, p, v)
for beat, dur, p, v in [(0.0, 0.5, "B-3", 92), (0.5, 0.5, "B-3", 88), (1.0, 0.5, "B-3", 90),
                        (1.5, 0.5, "A3", 96), (2.0, 2.0, "B-3", 94)]:
    N("bone2", ARGUE + 5, beat, dur, p, v)
# cornet + clarinet gang reply
for beat, dur, p, v in [(0.0, 0.5, "G4", 104), (0.5, 0.5, "B-4", 102), (1.0, 0.5, "C5", 104),
                        (1.5, 0.5, "C#5", 108), (2.0, 1.5, "D5", 112), (3.5, 0.5, "E-5", 108)]:
    N("cornet", ARGUE + 6, beat, dur, p, v)
    pp = m21.pitch.Pitch(p); pp.midi += 3 if p in ("C#5",) else 5  # rough upper 3rds/4ths
    N("clarinet", ARGUE + 6, beat, dur, pp.nameWithOctave, v - 12)
for beat, dur, p, v in [(0.0, 1.0, "D5", 110), (1.0, 0.5, "C5", 100), (1.5, 0.5, "B-4", 98),
                        (2.0, 2.0, "G4", 102)]:
    N("cornet", ARGUE + 7, beat, dur, p, v)
trill("clarinet", ARGUE + 7, 0.0, "F5", "G5", 1.0, 100)
N("clarinet", ARGUE + 7, 2.0, 2.0, "B-5", 98)
# sax honks in; bone interrupts before its turn (bar 77.5 = ARGUE+8 beat 2)
for beat, dur, p, v in [(0.0, 0.5, "G3", 100), (0.5, 0.5, "G3", 96), (1.0, 0.5, "B-3", 98),
                        (1.5, 0.5, "C4", 100), (2.0, 0.5, "C#4", 104), (2.5, 1.5, "D4", 108)]:
    N("sax", ARGUE + 8, beat, dur, p, v)
smear_into("bone1", ARGUE + 8, 2.0, "G3", 104)   # the interruption
N("bone1", ARGUE + 8, 2.0, 0.5, "G3", 106); N("bone1", ARGUE + 8, 2.5, 0.5, "G3", 102)
N("bone1", ARGUE + 8, 3.0, 1.0, "A-3", 112)
for beat, dur, p, v in [(0.0, 0.5, "D-4", 110), (0.5, 0.5, "C4", 100), (1.0, 0.5, "B-3", 96),
                        (1.5, 0.5, "C4", 100), (2.0, 1.5, "D4", 106)]:
    N("bone1", ARGUE + 9, beat, dur, p, v)
N("sax", ARGUE + 9, 2.0, 2.0, "F4", 100)        # sax won't back down either
N("cornet", ARGUE + 9, 3.0, 0.5, "F5", 106); N("cornet", ARGUE + 9, 3.5, 0.5, "F#5", 110)
# everyone at once (gridded chaos, each in its own register and rhythm slot)
for beat, dur, p, v in [(0.0, 1.0, "G5", 114), (1.5, 0.5, "F5", 104), (2.0, 1.0, "E-5", 108),
                        (3.0, 0.5, "D5", 102), (3.5, 0.5, "D-5", 110)]:
    N("cornet", ARGUE + 10, beat, dur, p, v)
for beat, dur, p, v in [(0.0, 0.5, "B-3", 104), (1.0, 0.5, "G3", 100), (1.5, 0.5, "A-3", 108),
                        (2.0, 0.5, "G3", 102), (3.0, 1.0, "F3", 100)]:
    N("bone1", ARGUE + 10, beat, dur, p, v)
for k in range(8):
    N("clarinet", ARGUE + 10, k * 0.5, 0.45,
      ["B-5", "C6", "D6", "C6", "B-5", "A-5", "G5", "F5"][k], 96 + (6 if k % 2 == 0 else 0))
N("sax", ARGUE + 10, 0.5, 0.5, "D4", 98); N("sax", ARGUE + 10, 2.5, 0.75, "D-4", 106)
for beat, dur, p, v in [(0.0, 0.5, "C5", 104), (0.5, 0.5, "B-4", 100), (1.0, 1.0, "A-4", 112),
                        (2.0, 2.0, "G4", 108)]:
    N("cornet", ARGUE + 11, beat, dur, p, v)
N("bone1", ARGUE + 11, 0.0, 1.0, "D-3", 108); N("bone1", ARGUE + 11, 2.0, 2.0, "D3", 104)
N("bone2", ARGUE + 11, 2.0, 2.0, "B-2", 100)
N("clarinet", ARGUE + 11, 0.0, 1.5, "E-6", 112)
N("clarinet", ARGUE + 11, 2.0, 2.0, "D6", 106)
N("sax", ARGUE + 11, 0.0, 0.5, "G3", 100); N("sax", ARGUE + 11, 2.0, 2.0, "F3", 96)

# ---- 81-92 THE STOMP: stop-time, the riot chord starts swinging -------------
GM_STAB = dict(cornet="G4", clarinet="D5", sax="B-3", bone1="D4", bone2="G3")
AB_STAB = dict(cornet="A-4", clarinet="E-5", sax="C4", bone1="E-4", bone2="A-3")
def stab(bar, beat, voicing, vel, dur=0.4):
    for inst, p in voicing.items():
        N(inst, bar, beat, dur, p, vel)
    N("banjo", bar, beat, dur, AB9 if voicing is AB_STAB else GM6, vel - 12)
for c in range(6):
    add_riff("sousa", STOMP + 2 * c, vel_scale=1.1)   # the riff does not stop
for b in range(STOMP, COLLAPSE):                       # four-on-the-floor toms + cowbell
    for beat in range(4):
        D(b, beat, TOMF, 88 + (10 if beat == 0 else 0), 0.5)
        D(b, beat, KICK, 92 + (8 if beat == 0 else 0), 0.5)
    D(b, 1.0, COWB, 92); D(b, 3.0, COWB, 96)
    D(b, 3.5, HATO, 70)
stab(STOMP, 0.0, GM_STAB, 112); stab(STOMP + 1, 0.0, GM_STAB, 110)
stab(STOMP + 2, 0.0, GM_STAB, 112); stab(STOMP + 3, 0.0, GM_STAB, 112)
stab(STOMP + 4, 0.0, GM_STAB, 114)
stab(STOMP + 5, 0.0, AB_STAB, 118)                    # the riot chord arrives
stab(STOMP + 6, 0.0, GM_STAB, 114); stab(STOMP + 7, 0.0, AB_STAB, 118)
stab(STOMP + 8, 0.0, AB_STAB, 118); stab(STOMP + 8, 2.5, AB_STAB, 114, 0.3)
stab(STOMP + 9, 0.0, GM_STAB, 116); stab(STOMP + 9, 2.5, AB_STAB, 118, 0.3)
stab(STOMP + 10, 0.0, AB_STAB, 120); stab(STOMP + 10, 2.0, GM_STAB, 116)
# bar 92: the climb — stabs on every beat walking up, drums opening up
CLIMB = [dict(cornet="G4", clarinet="D5", sax="B-3", bone1="D4", bone2="G3"),
         dict(cornet="A-4", clarinet="E-5", sax="C4", bone1="E-4", bone2="A-3"),
         dict(cornet="A4", clarinet="E5", sax="C#4", bone1="E4", bone2="A3"),
         dict(cornet="B-4", clarinet="F5", sax="D4", bone1="F4", bone2="B-3")]
for beat, vc in enumerate(CLIMB):
    stab(STOMP + 11, float(beat), vc, 112 + 3 * beat, 0.5)
drum_fill(STOMP + 11, 2.0, 100, big=True)

# ---- 93-96 THE COLLAPSE: choke, drum chatter, sousa mutters back ------------
for inst, p in dict(cornet="G5", clarinet="G5", sax="G4", bone1="G3", bone2="G2").items():
    N(inst, COLLAPSE, 0.0, 0.3, p, 118)
N("sousa", COLLAPSE, 0.0, 0.3, "G1", 118)
N("banjo", COLLAPSE, 0.0, 0.3, GM6, 100)
D(COLLAPSE, 0.0, CRASH, 116, 0.3); D(COLLAPSE, 0.0, KICK, 116, 0.3)
# drums alone: a talkative break
for beat, dr, v in [(1.5, SNARE, 60), (1.75, SNARE, 48), (2.0, SNARE, 78), (2.5, TOMM, 70),
                    (2.75, SNARE, 52), (3.0, KICK, 88), (3.5, SNARE, 82), (3.75, TOMF, 74)]:
    D(COLLAPSE, beat, dr, v)
for beat, dr, v in [(0.0, KICK, 92), (0.5, SNARE, 66), (0.75, SNARE, 50), (1.0, TOMF, 84),
                    (1.5, SNARE, 72), (2.0, KICK, 90), (2.25, SNARE, 56), (2.5, SNARE, 88),
                    (3.0, TOMF, 86), (3.25, TOMM, 70), (3.5, SNARE, 92), (3.75, SNARE, 96)]:
    D(COLLAPSE + 1, beat, dr, v)
add_riff("sousa", COLLAPSE + 2, vel_scale=0.85)       # the mutter
for beat, dr, v in [(0.0, HATP, 60), (1.0, HATP, 58), (2.0, HATP, 60), (3.0, HATP, 62)]:
    D(COLLAPSE + 2, beat, dr, v)
for k in range(8):                                     # snare roll up into the riot
    D(COLLAPSE + 3, 2.0 + k * 0.25, SNARE, 50 + 9 * k, dur=0.18)
D(COLLAPSE + 3, 0.0, HATP, 62); D(COLLAPSE + 3, 1.0, HATP, 64)

# ---- 97-120 THE RIOT: everything, everywhere, all at once -------------------
def riot_bed(bar0, vmul=1.0, tremolo=False):
    """One 8-bar anthem cycle of full-tilt rhythm section + riff 8va brass."""
    anthem_rhythm_bed(bar0, vmul, banjo=not tremolo)
    add_riff("bone1", bar0, "G3", 0.92 * vmul)
    add_riff("bone1", bar0 + 2, "G3", 0.94 * vmul)
    add_riff("bone1", bar0 + 4, "C4", 0.92 * vmul)
    add_riff("bone1", bar0 + 6, "D4", 0.96 * vmul)
    add_riff("bone2", bar0, "G3", 0.9 * vmul)
    add_riff("bone2", bar0 + 2, "G3", 0.92 * vmul)
    add_riff("bone2", bar0 + 4, "C3", 0.92 * vmul)
    add_riff("bone2", bar0 + 6, "D3", 0.96 * vmul)
    for i in range(8):
        crash = i % 2 == 0
        drums_fourfloor(bar0 + i, 94 if i < 7 else 98, crash=crash)
    if tremolo:
        for i, vc in [(0, GM6), (1, GM6), (2, GM6), (3, GM6), (4, CM6), (5, CM6),
                      (6, D7c), (7, D7c)]:
            banjo_bar(bar0 + i, vc, 84, tremolo=True)

# cycle A: anthem in cornet+sax, riff 8va in bones
riot_bed(RIOT)
write_anthem(RIOT, cornet=True, clar8va=False, sax8vb=True, vmul=1.0)
trill("clarinet", RIOT, 0.0, "D6", "E-6", 2.0, 104)
N("clarinet", RIOT + 1, 1.5, 1.5, "D-6", 108)
N("clarinet", RIOT + 2, 0.0, 2.0, "B-5", 98)
trill("clarinet", RIOT + 3, 0.0, "D6", "E-6", 1.5, 106)
N("clarinet", RIOT + 4, 0.0, 2.5, "E-6", 110)
N("clarinet", RIOT + 5, 0.0, 2.0, "C6", 104)
N("clarinet", RIOT + 6, 0.0, 2.0, "F5", 106); N("clarinet", RIOT + 6, 2.0, 2.0, "A5", 104)
N("clarinet", RIOT + 7, 0.0, 1.0, "C6", 106); N("clarinet", RIOT + 7, 2.0, 2.0, "A-5", 112)
# cycle B: anthem again, clarinet on top 8va, banjo tremolo, heat rising
riot_bed(RIOT + 8, vmul=1.05, tremolo=True)
write_anthem(RIOT + 8, cornet=True, clar8va=True, sax8vb=True, vmul=1.06)
drum_fill(RIOT + 15, 2.0, 102, big=True)
# cycle C: the transcription's cluster hammers, then Ab9->Gm slams, then the rip
for i in range(4):                                    # 113-116: [Eb A D] hammers
    for beat in range(4):
        v = 104 + 2 * beat + 3 * i
        N("cornet", RIOT + 16 + i, float(beat), 0.6, "D5", min(122, v))
        N("clarinet", RIOT + 16 + i, float(beat), 0.6, "A5", min(120, v - 6))
        N("sax", RIOT + 16 + i, float(beat), 0.6, "E-4", min(120, v - 4))
        N("bone1", RIOT + 16 + i, float(beat), 0.6, "A3", min(120, v - 2))
        N("bone2", RIOT + 16 + i, float(beat), 0.6, "E-3", min(120, v - 2))
        N("sousa", RIOT + 16 + i, float(beat), 0.7, "G2" if beat % 2 == 0 else "G1", 116)
        N("banjo", RIOT + 16 + i, float(beat), 0.5, ["E-4", "A4", "D5"], 92)
        D(RIOT + 16 + i, beat, KICK, 104, 0.5); D(RIOT + 16 + i, beat, TOMF, 96, 0.5)
    D(RIOT + 16 + i, 0.0, CRASH if i % 2 == 0 else CRASH2, 108, 1.0)
    D(RIOT + 16 + i, 1.0, COWB, 96); D(RIOT + 16 + i, 3.0, COWB, 100)
AB_BIG = dict(cornet="E-5", clarinet="A-5", sax="C4", bone1="G-3", bone2="A-2")
GM_BIG = dict(cornet="D5", clarinet="G5", sax="B-3", bone1="G3", bone2="G2")
def big_slam(bar, beat, voicing, vel, dur=0.75):
    for inst, p in voicing.items():
        N(inst, bar, beat, dur, p, vel)
    N("banjo", bar, beat, dur, AB9 if voicing is AB_BIG else GM69, vel - 14)
    N("sousa", bar, beat, dur, "A-1" if voicing is AB_BIG else "G1", vel)
    D(bar, beat, KICK, vel, 0.5); D(bar, beat, CRASH if beat == 0 else CRASH2, vel - 4, 1.0)
big_slam(RIOT + 20, 0.0, AB_BIG, 116, 1.5); big_slam(RIOT + 20, 2.0, GM_BIG, 114, 1.5)
big_slam(RIOT + 21, 0.0, AB_BIG, 118, 1.0); big_slam(RIOT + 21, 1.5, GM_BIG, 114, 0.5)
big_slam(RIOT + 21, 2.0, AB_BIG, 118, 1.0); big_slam(RIOT + 21, 3.0, GM_BIG, 116, 1.0)
for beat, vc in [(0.0, AB_BIG), (1.0, GM_BIG), (2.0, AB_BIG), (3.0, GM_BIG)]:
    big_slam(RIOT + 22, beat, vc, 118, 0.6)
# bar 120: the whole band rips up a chromatic ladder together
RIP = ["F#", "G", "A-", "A", "B-", "B", "C", "C#"]
for k, name in enumerate(RIP):
    beat = k * 0.5
    v = 102 + 2 * k
    N("cornet", RIOT + 23, beat, 0.45, name + "5" if name in ("F#", "G", "A-", "A", "B-", "B") else name + "6", min(122, v + 4))
    N("clarinet", RIOT + 23, beat, 0.45, name + "5" if name in ("F#", "G", "A-", "A", "B-", "B") else name + "6", min(120, v))
    N("sax", RIOT + 23, beat, 0.45, name + "4", v - 4)
    N("bone1", RIOT + 23, beat, 0.45, name + "3" if name in ("F#", "G", "A-", "A", "B-", "B") else name + "4", v)
    N("bone2", RIOT + 23, beat, 0.45, name + "3", v - 2)
    N("sousa", RIOT + 23, beat, 0.45, name + "2", v)
    D(RIOT + 23, beat, SNARE, 80 + 4 * k)
    D(RIOT + 23, beat, KICK, 86 + 3 * k, 0.4)
D(RIOT + 23, 3.5, HATO, 96)

# ---- 121-124 THE WINK --------------------------------------------------------
# 121: the climb lands on ONE hit — then dead air
for inst, p in dict(cornet="D6", clarinet="D6", sax="D5", bone1="D4", bone2="D3").items():
    N(inst, TAG, 0.0, 0.35, p, 120)
N("sousa", TAG, 0.0, 0.35, "D2", 120)
N("banjo", TAG, 0.0, 0.35, ["D4", "A4", "D5"], 104)
D(TAG, 0.0, CRASH, 118, 0.3); D(TAG, 0.0, KICK, 118, 0.3)
# 122: sousa alone, the snarl lick, cheeky and quiet
for beat, dur, tok, vel in RIFF_B:
    N("sousa", TAG + 1, beat, dur, riff_pitch(tok, m21.pitch.Pitch("G2").midi), vel * 0.62)
# 123: two stabs — the riot chord, then home with a wink (Gm6/9)
for inst, p in dict(cornet="E-5", clarinet="A-5", sax="C4", bone1="G-3", bone2="A-2").items():
    N(inst, TAG + 2, 0.0, 0.5, p, 116)
N("sousa", TAG + 2, 0.0, 0.5, "A-1", 116); N("banjo", TAG + 2, 0.0, 0.5, AB9, 100)
D(TAG + 2, 0.0, KICK, 110, 0.4); D(TAG + 2, 0.0, CRASH2, 106, 0.5)
for inst, p in dict(cornet="D5", clarinet="A5", sax="E4", bone1="B-3", bone2="G2").items():
    N(inst, TAG + 2, 2.0, 0.6, p, 112)
N("sousa", TAG + 2, 2.0, 0.6, "G1", 112); N("banjo", TAG + 2, 2.0, 0.6, GM69, 98)
D(TAG + 2, 2.0, KICK, 104, 0.4); D(TAG + 2, 2.0, RIDE, 90)
# 124: one fat unison G... and the sousaphone gets the last word
for inst, p in dict(cornet="G5", clarinet="G5", sax="G4", bone1="G3", bone2="G2").items():
    N(inst, TAG + 3, 0.0, 1.9, p, 120)
N("sousa", TAG + 3, 0.0, 1.9, "G1", 120)
N("banjo", TAG + 3, 0.0, 1.9, ["G3", "D4", "G4", "B-4"], 104)
D(TAG + 3, 0.0, CRASH, 120, 1.8); D(TAG + 3, 0.0, KICK, 120, 0.5)
N("sousa", TAG + 3, 2.75, 0.3, "G1", 88)              # the plop. the wink.
D(TAG + 3, 2.75, KICK, 72, 0.2); D(TAG + 3, 2.75, HATP, 66)

# ================================================================ RENDERING
def humanize_and_swing():
    tight = {"sousa", "banjo", "drums"}
    for name, evs in PARTS.items():
        jit = 0.008 if name in tight else 0.018
        lean = {"sax": 0.012, "clarinet": -0.004}.get(name, 0.0)
        for e in evs:
            frac = e["off"] % 1.0
            if abs(frac - 0.5) < 1e-6 and e["dur"] >= 0.2:   # swing the offbeat 8ths
                e["off"] += SWING
                e["dur"] = max(0.1, e["dur"] - SWING)
            e["off"] = max(0.0, e["off"] + lean + random.uniform(-jit, jit))
            e["vel"] = int(max(20, min(122, e["vel"] + random.uniform(-5, 5))))
    # same-pitch overlaps on one channel are ambiguous MIDI (and jitter creates
    # them on repeated notes) — trim the earlier note so every pair re-articulates
    for name, evs in PARTS.items():
        by_pitch = {}
        for e in evs:
            for p in e["pitches"]:
                key = p if isinstance(p, int) else m21.pitch.Pitch(p).midi
                by_pitch.setdefault(key, []).append(e)
        for seq in by_pitch.values():
            seq.sort(key=lambda e: e["off"])
            for a, b in zip(seq, seq[1:]):
                if a["off"] + a["dur"] > b["off"] - 0.02:
                    a["dur"] = max(0.05, b["off"] - 0.02 - a["off"])

INSTRUMENTS = dict(
    cornet=(instrument.Trumpet, 56), clarinet=(instrument.Clarinet, 71),
    sax=(instrument.TenorSaxophone, 66), bone1=(instrument.Trombone, 57),
    bone2=(instrument.Trombone, 57), sousa=(instrument.Tuba, 58),
    banjo=(instrument.Banjo, 105),
)
DISPLAY = dict(cornet="Cornet", clarinet="Clarinet", sax="Tenor Sax",
               bone1="Trombone I", bone2="Trombone II", sousa="Sousaphone",
               banjo="Banjo", drums="Drums")

def build_score():
    sc = stream.Score()
    sc.insert(0, tempo.MetronomeMark(number=160))
    sc.insert(off(STOMP, 0), tempo.MetronomeMark(number=156))   # the stomp digs in
    sc.insert(off(RIOT, 0), tempo.MetronomeMark(number=164))    # the riot rushes. of course it does
    for name, evs in PARTS.items():
        part = stream.Part()
        part.partName = DISPLAY[name]
        if name == "drums":
            inst = instrument.UnpitchedPercussion()
            inst.midiChannel = 9
        else:
            cls, prog = INSTRUMENTS[name]
            inst = cls()
            inst.midiProgram = prog
        inst.instrumentName = DISPLAY[name]   # becomes the MIDI track name
        part.insert(0, inst)
        part.insert(0, meter.TimeSignature("4/4"))
        part.insert(0, m21key.KeySignature(-2))
        for e in evs:
            if len(e["pitches"]) == 1:
                p = e["pitches"][0]
                n = note.Note()
                if isinstance(p, int):
                    n.pitch.midi = p
                else:
                    n.pitch = m21.pitch.Pitch(p)
                n.quarterLength = e["dur"]
                n.volume.velocity = e["vel"]
                part.insert(e["off"], n)
            else:
                ch = chord.Chord(e["pitches"])
                ch.quarterLength = e["dur"]
                for nn in ch.notes:
                    nn.volume.velocity = e["vel"]
                part.insert(e["off"], ch)
        sc.insert(0, part)
    return sc

PAN = dict(cornet=52, clarinet=80, sax=36, bone1=44, bone2=86, sousa=64, banjo=92, drums=64)
VOL = dict(cornet=100, clarinet=86, sax=92, bone1=100, bone2=98, sousa=112, banjo=72, drums=98)

def postprocess_midi(path):
    """Pan/volume/reverb CCs per track, and split the two trombones onto
    separate channels (music21 gives same-instrument parts the same one)."""
    import mido
    mid = mido.MidiFile(str(path))
    used = {msg.channel for tr in mid.tracks for msg in tr if hasattr(msg, "channel")}
    free = next(c for c in range(16) if c != 9 and c not in used)
    for tr in mid.tracks:
        chan = None
        for msg in tr:
            if msg.type in ("note_on", "program_change"):
                chan = msg.channel
                break
        if chan is None:
            continue
        name = tr.name.strip().lower() if tr.name else ""
        keymap = {v.lower(): k for k, v in DISPLAY.items()}
        keymap.update({"trumpet": "cornet", "tenor saxophone": "sax",
                       "tuba": "sousa", "percussion": "drums"})
        keymap.update({p: p for p in PARTS})
        part = keymap.get(name)
        if part is None and name == "trombone":
            part = "bone1" if not postprocess_midi.seen_bone else "bone2"
            postprocess_midi.seen_bone = True
        if part == "bone2":
            for msg in tr:               # move the whole track to its own channel
                if hasattr(msg, "channel"):
                    msg.channel = free
            chan = free
        if part is None:
            continue
        tr.insert(0, mido.Message("control_change", channel=chan, control=10, value=PAN[part], time=0))
        tr.insert(0, mido.Message("control_change", channel=chan, control=7, value=VOL[part], time=0))
        tr.insert(0, mido.Message("control_change", channel=chan, control=91,
                                  value=24 if part != "drums" else 18, time=0))
    mid.save(str(path))
postprocess_midi.seen_bone = False

def main():
    humanize_and_swing()
    (OUT / "events.json").write_text(json.dumps(
        {k: v for k, v in PARTS.items()}, indent=None))
    total_bars = END - 1
    n_notes = sum(len(v) for v in PARTS.values())
    print(f"composed {total_bars} bars, {n_notes} events")
    sc = build_score()
    midpath = OUT / "high_street_riot.mid"
    sc.write("midi", fp=str(midpath))
    postprocess_midi(midpath)
    print(f"wrote {midpath}")

if __name__ == "__main__":
    main()
