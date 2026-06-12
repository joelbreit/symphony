"""THE UNFINISHED SPIRE — An Anthem for Builders.

E-flat major, 4/4, ~6 minutes. Eight sections, built per docs/03-structure.md.
Run:  python src/compose.py  -> out/anthem.mid
"""

from score import (Score, P, Ps, ramp,
                   PP, Pdyn, MP, MF, F, FF, FFF,
                   FL, OB, CL, BN, HN, TP, TB, TU, TI, PERC,
                   V1, V2, VA, VC, CB, HARP, BELLS,
                   BD, SD, CRASH, TRI)

# ============================================================ THEMES

# The Summons: rising 4th + two steps, long-short-short-long.
SUMMONS = [("Bb3", 2), ("Eb4", 1), ("F4", 1), ("G4", 4)]

# The Anthem, strain A (8 bars). Harmony: I vi IV V | I ii7 V7 I
ANTHEM_A = [
    ("Eb4", 1.5), ("F4", 0.5), ("G4", 1), ("Bb4", 1),
    ("C5", 2), ("Bb4", 1), ("G4", 1),
    ("Ab4", 1.5), ("Bb4", 0.5), ("C5", 1), ("Ab4", 1),
    ("F4", 3), (None, 1),
    ("Eb4", 1.5), ("F4", 0.5), ("G4", 1), ("Bb4", 1),
    ("C5", 1), ("Eb5", 1), ("D5", 1), ("C5", 1),
    ("Bb4", 1.5), ("Ab4", 0.5), ("G4", 1), ("F4", 1),
    ("Eb4", 3), (None, 1),
]

# Strain B — the lift (8 bars). IV I6 vi V/V | IVadd9 I64-V7 I IV-I
ANTHEM_B = [
    ("C5", 1.5), ("D5", 0.5), ("Eb5", 1), ("C5", 1),
    ("Bb4", 2), ("C5", 1), ("D5", 1),
    ("Eb5", 1.5), ("D5", 0.5), ("C5", 1), ("Bb4", 1),
    ("F5", 2), ("F5", 1), ("G5", 1),
    ("G5", 1.5), ("F5", 0.5), ("Eb5", 1), ("C5", 1),
    ("F5", 1.5), ("Eb5", 0.5), ("D5", 1), ("F5", 1),
    ("Eb5", 3), (None, 1),
    ("G4", 1), ("F4", 1), ("Eb4", 2),
]

# The Doubt theme, overlay form: composed against strain A's changes.
# (At the apotheosis this sounds an octave lower in horns+celli.)
DOUBT = [
    ("G5", 3), ("F5", 1),
    ("Eb5", 2), ("D5", 1), ("C5", 1),
    ("C5", 1.5), ("D5", 0.5), ("Eb5", 2),
    ("D5", 3), ("Bb4", 1),
    ("G4", 3), ("Ab4", 1),
    ("Ab4", 2), ("F4", 1), ("Eb4", 1),
    ("F4", 2), ("G4", 1), ("Bb4", 1),
    ("G4", 4),
]

# Countersubject for strain B at the apotheosis (slower ascent, converges).
COUNTER_B = [
    ("Eb4", 3), ("F4", 1),
    ("G4", 2), ("Ab4", 1), ("Bb4", 1),
    ("C5", 3), ("G4", 1),
    ("A4", 2), ("C5", 2),
    ("Bb4", 3), ("Ab4", 1),
    ("Bb4", 2), ("Ab4", 1), ("F4", 1),
    ("G4", 3), (None, 1),
    ("Eb4", 1), ("F4", 1), ("Eb4", 2),
]

# Bell change-ring (within tubular-bell range C4..F5).
RING = ["G4", "Eb4", "F4", "Bb4"]


# ============================================================ SECTION I — DAWN
# 16 bars, q=69 accel 76. Mist over the site; the Summons; first light.

def dawn(s, t0):
    s.tempo(t0, 69)
    s.tempo(t0 + 32, 72)
    s.tempo(t0 + 56, 76)
    B = lambda b: t0 + 4 * b

    # Low pedal: celli from bar 1, basses join bar 5; slow breathing swells.
    for i in range(8):
        v = ramp(30, 50, i, 8)
        s.note(VC, "Eb2", B(2 * i), 8, v)
        if i >= 2:
            s.note(CB, "Eb2", B(2 * i), 8, v - 4)
    for i in range(7):  # violas, bar 3 on
        s.note(VA, "G3", B(2 + 2 * i), 8, ramp(28, 46, i, 7))

    # Violin mist: slow-shifting color tones above.
    v2_colors = [("Bb3", "Eb4"), ("Bb3", "F4"), ("C4", "Eb4"), ("Bb3", "D4")]
    for i, (a, b) in enumerate(v2_colors):
        s.chord(V2, Ps(a, b), B(2 + 4 * i)
                if i < 3 else B(14), 8, ramp(30, 44, i, 4), spread=0.08)
    for i, p in enumerate(["Bb4", "C5", "Bb4"]):
        s.note(V1, p, B(4 + 4 * i), 8, ramp(30, 42, i, 3))

    # Harp: rising arpeggios every two bars, reaching higher as light grows.
    arps = [Ps("Eb2", "Bb2", "Eb3", "G3", "Bb3", "Eb4"),
            Ps("Eb2", "Bb2", "Eb3", "G3", "Bb3", "Eb4"),
            Ps("Eb2", "Bb2", "G3", "Bb3", "Eb4", "G4"),
            Ps("Eb3", "G3", "Bb3", "Eb4", "G4", "Bb4"),
            Ps("Eb3", "G3", "Bb3", "Eb4", "G4", "Bb4"),
            Ps("Eb3", "Bb3", "Eb4", "G4", "Bb4", "Eb5")]
    for i, notes in enumerate(arps):
        s.harp_arp(notes, B(2 * i) + (0 if i % 2 else 0.0), 0.5,
                   ramp(34, 56, i, 6))

    # The Summons — solo horn, bar 5; answered by soft trumpet, bar 9.
    s.line(HN, SUMMONS, B(4), MP + 4)
    s.line(TP, [("Eb4", 2), ("Ab4", 1), ("Bb4", 1), ("C5", 4)], B(8), Pdyn)

    # Woodwind flickers — birdsong over the site.
    s.line(FL, [("Bb5", 0.25), ("C6", 0.25), ("Bb5", 0.5), ("G5", 1.5)],
           B(6) + 2, Pdyn)
    s.line(OB, [("F5", 0.5), ("Eb5", 0.5), ("C5", 1.5)], B(10) + 1, Pdyn)
    s.line(CL, [("Eb4", 0.25), ("F4", 0.25), ("G4", 0.5), ("Bb4", 2)],
           B(12) + 2, MP - 6)

    # Bar 13: the Summons again, extended, mf — work is truly beginning.
    s.line(HN, [("Bb3", 2), ("Eb4", 1), ("F4", 1),
                ("G4", 2), ("Ab4", 1), ("Bb4", 1)], B(12), MF)

    # Final rise into the Anthem.
    s.line(V1, [("Bb4", 2), ("C5", 2), ("D5", 4)], B(14), MP, MF)
    s.note(V2, "F4", B(14), 8, MP)
    s.note(VA, "Ab3", B(14), 8, MP)
    s.roll(TI, P("Eb2"), B(14), 8, PP, F)
    s.cym_swell(B(15), 4, 18, 64)
    return t0 + 64


# ====================================================== SECTION II — THE ANTHEM
# 24 bars, q=92. Theme once (horns+celli, hymn beneath), strain B repeated tutti.

# Accompaniment voicings per bar: (bassoon, contrabass, viola, clarinet)
ACC_A = [
    (("Eb2", "Bb2"), "Eb2", ("G3", "Bb3"), ("Bb3",)),
    (("C2", "G2"),  "C2",  ("G3", "C4"),  ("C4", "Eb4")),
    (("Ab2", "Eb3"), "Ab2", ("Ab3", "C4"), ("Eb4",)),
    (("Bb2", "F3"), "Bb2", ("F3", "Bb3"), ("D4", "F4")),
    (("Eb2", "Bb2"), "Eb2", ("G3", "Bb3"), ("Bb3", "Eb4")),
    (("F2", "C3"),  "F2",  ("Ab3", "C4"), ("C4", "Eb4")),
    (("Bb2", "F3"), "Bb2", ("F3", "Ab3"), ("D4",)),
    (("Eb2", "Bb2"), "Eb2", ("G3", "Bb3"), ("Bb3",)),
]
ACC_B = [
    (("Ab2", "Eb3"), "Ab2", ("C4", "Eb4"), ("Eb4", "Ab4")),
    (("G2", "Eb3"), "G2",  ("Bb3", "Eb4"), ("G4",)),
    (("C3", "G3"),  "C2",  ("G3", "Eb4"), ("G4", "C5")),
    (("F2", "C3"),  "F2",  ("A3", "Eb4"), ("C5", "Eb5")),
    (("Ab2", "Eb3"), "Ab2", ("C4", "Eb4"), ("Bb4", "C5")),
    (("Bb2", "G3"), "Bb2", ("Eb4", "G4"), ("Bb4",)),
    (("Eb2", "Bb2"), "Eb2", ("G3", "Eb4"), ("G4", "Bb4")),
    (("Ab2", "Eb3"), "Ab2", ("Ab3", "C4"), ("Ab4",)),
]


def hymn_bar(s, t, acc, vel, lush=False):
    bsn, cb, va, cl = acc
    s.chord(BN, Ps(*bsn), t, 4, vel - 8)
    s.note(CB, cb, t, 2, vel - 8)
    s.note(CB, cb, t + 2, 2, vel - 14)
    s.chord(VA, Ps(*va), t, 4, vel - 6, spread=0.04)
    s.chord(CL, Ps(*cl), t, 4, vel - 12, spread=0.04)
    if lush:
        s.chord(TB, [P(bsn[0]) + 12, P(bsn[1]) + 12], t, 4, vel - 10)


def the_anthem(s, t0):
    s.tempo(t0, 92)
    B = lambda b: t0 + 4 * b

    # --- bars 1-8: strain A, mf — melody in horns and celli.
    s.line(HN, ANTHEM_A, B(0), MF + 6)
    s.line(VC, ANTHEM_A, B(0), MF + 2)
    for i, acc in enumerate(ACC_A):
        hymn_bar(s, B(i), acc, MF)
    for b in (0, 2, 4, 6):
        s.harp_arp(Ps("Eb2", "Bb2", "G3", "Bb3", "Eb4"), B(b), 0.25, MP)

    # --- bars 9-16: strain B, mf -> f. Violin II joins; Vln I at the climax.
    s.line(HN, ANTHEM_B, B(8), F, oct_shift=-1)   # horns warm it from below
    s.line(VC, ANTHEM_B, B(8), F - 4)
    s.line(V2, ANTHEM_B, B(8), MF)
    s.line(V1, ANTHEM_B[16:], B(12), F)        # from the G5 climax bar
    for i, acc in enumerate(ACC_B):
        hymn_bar(s, B(8 + i), acc, MF + 6)
    s.roll(TI, P("Bb2"), B(7) + 2, 2, Pdyn, MP)
    for b, p in ((8, "Ab2"), (10, "C3"), (12, "Ab2")):
        s.note(TI, p, B(b), 1, MP, jitter=False)
    s.roll(TI, P("Bb2"), B(13), 4, MP, F)
    s.note(TI, "Eb3", B(14), 2, F, jitter=False)
    s.chord(TB, Ps("Bb2", "F3", "D4"), B(13), 4, MF)
    s.chord(TB, Ps("Eb3", "Bb3", "G4"), B(14), 8, MF)

    # --- bars 17-24: strain B again, f -> ff, tutti. Violins/flute up the octave.
    s.line(V1, ANTHEM_B, B(16), FF - 6, oct_shift=1)
    s.line(FL, ANTHEM_B, B(16), F, oct_shift=1)
    s.line(OB, ANTHEM_B, B(16), F)
    s.line(V2, ANTHEM_B, B(16), F)
    s.line(HN, ANTHEM_B, B(16), F + 4, oct_shift=-1)
    s.line(VC, ANTHEM_B, B(16), F)
    for i, acc in enumerate(ACC_B):
        hymn_bar(s, B(16 + i), acc, F + 4, lush=True)
        s.harp_arp(Ps(acc[1])[0:1] + [P(acc[0][0]) + 12, P(acc[0][1]) + 12,
                                      P(acc[2][0]) + 12], B(16 + i), 0.25, MF)
    tpt_support = [("Eb4", "G4"), ("Eb4", "G4"), ("Eb4", "G4"), ("Eb4", "A4"),
                   ("Eb4", "Ab4"), ("D4", "F4"), ("Eb4", "G4"), ("Eb4", "Ab4")]
    for i, dyad in enumerate(tpt_support):
        s.chord(TP, Ps(*dyad), B(16 + i), 4, MF - 4)
    s.note(TU, "Eb2", B(16), 4, MF - 6)
    s.note(TU, "C2", B(18), 4, MF - 6)
    s.note(TU, "F2", B(19), 4, MF - 6)
    s.note(TU, "Bb1", B(21) + 2, 2, MF)
    s.note(TU, "Eb2", B(22), 8, MF)
    for b, p in ((16, "Ab2"), (17, "G2"), (18, "C3"), (19, "F3"), (20, "Ab2")):
        s.note(TI, p, B(b), 1, MF, jitter=False)
    s.roll(TI, P("Bb2"), B(21), 4, F, FF - 8)
    s.note(TI, "Eb3", B(22), 2, FF - 6, jitter=False)
    s.hit(CRASH, B(22), F)
    # Plagal tail diminuendo; snare taps usher in the work.
    s.hit(SD, B(23) + 3.0, MP)
    s.hit(SD, B(23) + 3.5, MP + 6)
    return t0 + 96


# ====================================================== SECTION III — THE WORK
# 20 bars, q=126, C minor -> E-flat. Motoric; many hands, one gesture.

OSTINATO_C = [("G4", "Eb4", "G4", "C5"), ("G4", "F4", "G4", "B3")]
OSTINATO_EB = [("Bb4", "G4", "Bb4", "Eb5"), ("Bb4", "Ab4", "Bb4", "D5")]
ACCENTS = [10, -14, -8, 6, -14, 0, -14, 2]  # offsets on 8th-note grid


def ostinato_bar(s, ch, t, cell, base):
    eighths = [cell[0], cell[1], cell[2], cell[3]] * 2
    for i, p in enumerate(eighths):
        s.note(ch, p, t + 0.5 * i, 0.5, base + ACCENTS[i], jitter=False)


def snare_bar(s, t, base):
    for off, dv in ((0, 6), (1, -16), (1.5, -10), (2, 0), (2.75, -18),
                    (3, -8), (3.5, -4)):
        s.hit(SD, t + off, base + dv)


def the_work(s, t0):
    s.tempo(t0, 126)
    B = lambda b: t0 + 4 * b
    # Pizzicato low strings for the motor.
    s.mf.addProgramChange(VC, VC, t0 - 0.1, 45)
    s.mf.addProgramChange(CB, CB, t0 - 0.1, 45)

    walk = ["C3", "G2", "C3", "Eb3", "C3", "G2", "Ab2", "B2"]
    for bar in range(8):                       # bars 1-8 motor, p -> mp
        cell = OSTINATO_C[bar % 2]
        ostinato_bar(s, V2, B(bar), cell, 52 + 2 * bar)
        if bar >= 2:
            for k in range(4):
                s.note(VA, ["Eb3", "G3"][k % 2], B(bar) + k + 0.5, 0.5,
                       50 + 2 * bar, jitter=False)
        for k in range(4):
            s.note(VC, walk[(4 * bar + k) % 8], B(bar) + k, 0.9, 56 + 2 * bar,
                   jitter=False)
        s.note(CB, "C2" if bar % 2 == 0 else "G2", B(bar), 4, 50 + 2 * bar)
        for k in range(8):
            s.note(BN, ["C3", "G2"][k % 2], B(bar) + 0.5 * k, 0.4,
                   48 + 2 * bar, jitter=False)
        if bar >= 4:
            snare_bar(s, B(bar), 40 + 2 * bar)

    # The Summons in stretto: cl -> ob -> fl, one beat apart (bars 5-8).
    s.line(CL, [("G3", 1), ("C4", 0.5), ("D4", 0.5), ("Eb4", 2)], B(4), MP)
    s.line(OB, [("C4", 1), ("F4", 0.5), ("G4", 0.5), ("Ab4", 2)], B(4) + 1, MP)
    s.line(FL, [("G4", 1), ("C5", 0.5), ("D5", 0.5), ("Eb5", 2)], B(4) + 2, MP + 4)
    s.line(CL, [("D4", 1), ("G4", 0.5), ("A4", 0.5), ("Bb4", 2)], B(6), MP + 4)
    s.line(OB, [("Bb3", 1), ("Eb4", 0.5), ("F4", 0.5), ("G4", 2)], B(6) + 1, MP + 4)
    s.line(FL, [("Eb5", 1), ("Ab5", 0.5), ("Bb5", 0.5), ("C6", 2)], B(6) + 2, MF)

    for bar in range(8, 12):                   # bars 9-12: brass joins, mf
        cell = OSTINATO_C[bar % 2]
        ostinato_bar(s, V2, B(bar), cell, 64)
        if bar >= 10:
            ostinato_bar(s, V1, B(bar), [p[:-1] + str(int(p[-1]) + 1)
                                         for p in cell], 66)
        for k in range(4):
            s.note(VA, ["Eb3", "G3"][k % 2], B(bar) + k + 0.5, 0.5, 62,
                   jitter=False)
            s.note(VC, walk[(4 * bar + k) % 8], B(bar) + k, 0.9, 66, jitter=False)
        s.note(CB, "C2" if bar % 2 == 0 else "G2", B(bar), 4, 60)
        for k in range(8):
            s.note(BN, ["C3", "G2"][k % 2], B(bar) + 0.5 * k, 0.4, 58,
                   jitter=False)
        snare_bar(s, B(bar), 52)
        s.hit(BD, B(bar), 60)
        for beat in (1.5, 3.5):                # offbeat brass punches
            s.chord(HN, Ps("G3", "D4"), B(bar) + beat, 0.4, MF, spread=0)
            s.chord(TB, Ps("C3", "G3"), B(bar) + beat, 0.4, MF - 6, spread=0)
    s.line(TP, [("G4", 1), ("C5", 0.5), ("D5", 0.5), ("Eb5", 2)], B(8), F)
    s.line(TP, [("C4", 1), ("F4", 0.5), ("G4", 0.5), ("Ab4", 2)], B(10), F - 6)

    for bar in range(12, 16):                  # bars 13-16: E-flat sunshine, f
        cell = OSTINATO_EB[bar % 2]
        ostinato_bar(s, V2, B(bar), cell, 70)
        ostinato_bar(s, V1, B(bar), [p[:-1] + str(int(p[-1]) + 1)
                                     for p in cell], 72)
        for k in range(4):
            s.note(VA, ["G3", "Bb3"][k % 2], B(bar) + k + 0.5, 0.5, 66,
                   jitter=False)
            s.note(VC, ["Eb3", "Bb2", "Eb3", "G3"][k], B(bar) + k, 0.9, 70,
                   jitter=False)
        s.note(CB, "Eb2" if bar % 2 == 0 else "Bb2", B(bar), 4, 64)
        snare_bar(s, B(bar), 56)
        s.hit(BD, B(bar), 64)
        for k in range(8):
            s.hit(TRI, B(bar) + 0.5 * k, 40 if k % 2 else 52)
    s.line(FL, [("Bb4", 1), ("Eb5", 0.5), ("F5", 0.5), ("G5", 2),
                ("Bb5", 1), ("Eb5", 0.5), ("F5", 0.5), ("G5", 1), ("Bb5", 2)],
           B(12), F + 6)
    s.line(OB, [("Bb4", 1), ("Eb5", 0.5), ("F5", 0.5), ("G5", 2)], B(12), F)
    s.line(HN, [("Bb3", 1), ("Eb4", 0.5), ("F4", 0.5), ("G4", 2)], B(14), F)
    run = [P("Eb3") + i for i in
           [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24, 26]]
    for i, p in enumerate(run):                # harp rip up E-flat major
        s.note(HARP, p, B(14) + 2 + i * 0.125, 0.2, ramp(MP, F, i, 16),
               jitter=False)

    # Bars 17-18: hemiola — 3-beat chords across the barline, everyone.
    hem = [("Eb", Ps("Eb3", "Bb3", "G4"), Ps("Eb2", "Bb2"), "Eb5"),
           ("Bb/D", Ps("D3", "Bb3", "F4"), Ps("Bb1", "F2"), "D5"),
           ("Cm7", Ps("C3", "G3", "Eb4"), Ps("C2", "G2"), "C5"),
           ("Ab", Ps("Ab2", "Eb3", "C4"), Ps("Ab1", "Eb2"), "Eb5"),
           ("Bb", Ps("Bb2", "F3", "D4"), Ps("Bb1", "F2"), "F5")]
    t = B(16)
    for i, (_, mid, low, top) in enumerate(hem):
        d = 1.5 if i < 4 else 2.0
        s.chord(TB, mid, t, d, FF - 8, spread=0)
        s.chord(HN, [m + 12 for m in mid[:2]], t, d, FF - 6, spread=0)
        s.chord(TP, [P(top)], t, d, FF - 10, spread=0)  # unison punch
        s.chord(BN, [p + 12 for p in low], t, d, F, spread=0)
        s.note(TU, low[0], t, d, F)
        s.note(CB, low[0] + 12, t, d, F)
        s.note(VC, low[1] + 12, t, d, F + 4)
        s.chord(V1, [P(top) + 12], t, d, FF - 6)
        s.chord(V2, [P(top)], t, d, FF - 8)
        s.chord(VA, mid[1:], t, d, F, spread=0)
        s.note(TI, low[0] + (12 if low[0] < P("D2") else 0), t, d, F,
               jitter=False)
        s.hit(BD, t, F)
        t += d

    # Bars 19-20: Eb7 — the door opens inward (V7 of A-flat), ritardando.
    s.tempo(B(18), 116)
    s.tempo(B(19), 96)
    eb7_low = Ps("Eb3", "Bb3", "Db4")
    s.chord(TB, eb7_low, B(18), 8, F)
    s.note(TU, "Eb2", B(18), 8, F - 6)
    s.chord(HN, Ps("G4", "Db5"), B(18), 8, F)
    s.chord(TP, Ps("Bb4", "Eb5"), B(18), 4, F - 6)
    s.snare_roll(B(18), 6, F, PP)
    s.roll(TI, P("Eb3"), B(18), 8, F, PP)
    s.line(V1, [("Bb4", 1), ("C5", 1), ("Db5", 1), ("Eb5", 1),
                ("F5", 2), ("G5", 2)], B(18), F, MP)
    s.note(V2, "Eb4", B(18), 8, MF)
    s.note(VA, "Bb3", B(18), 8, MF)
    s.note(VC, "Eb3", B(18), 8, MF)
    s.note(CB, "Eb2", B(18), 8, MF)
    s.chord(CL, Ps("G4", "Db5"), B(19), 4, MP)
    s.note(FL, "Eb6", B(19), 4, MP)
    return t0 + 80


# ================================================ SECTION IV — THE SINGLE VOICE
# 16 bars, q=78, A-flat major. One mason, alone: will any of this matter?

DOUBT_SOLO = [                                  # oboe form, kept >= C4
    ("C5", 3), ("Bb4", 1),
    ("Ab4", 2), ("G4", 1), ("F4", 1),
    ("F4", 1.25), ("G4", 0.25), ("Ab4", 0.5), ("Ab4", 2),
    ("G4", 3), ("Eb4", 1),
    ("C4", 3), ("Db4", 1),
    ("Db4", 2), ("Eb4", 1), ("C4", 1),
    ("C4", 1.5), ("Db4", 0.5), ("Eb4", 1), ("F4", 1),
    ("Eb4", 3), (None, 1),
]

CUSHION = [  # (cello, viola, vln2-from-bar5) per bar, A-flat world
    (("Ab2", "Eb3"), ("C4", "Eb4"), ("Eb4", "Ab4")),
    (("F2", "C3"), ("Ab3", "C4"), ("C4", "F4")),
    (("Db3", "Ab3"), ("Db4", "F4"), ("F4", "Ab4")),
    (("Eb3", "Bb3"), ("Db4", "Eb4"), ("Eb4", "G4")),
]


def single_voice(s, t0):
    s.tempo(t0, 78)
    B = lambda b: t0 + 4 * b
    s.mf.addProgramChange(VC, VC, t0 - 0.05, 48)   # arco again
    s.mf.addProgramChange(CB, CB, t0 - 0.05, 48)

    for bar in range(16):                      # string cushion, breathing
        vc, va, v2 = CUSHION[bar % 4]
        swell = 4 if bar % 4 in (1, 2) else 0
        s.chord(VC, Ps(*vc), B(bar), 4, 40 + swell, spread=0.05)
        s.chord(VA, Ps(*va), B(bar), 4, 38 + swell, spread=0.05)
        s.note(CB, vc[0][:-1] + "1" if vc[0][-1] == "2" else vc[0][:-1] + "2",
               B(bar), 4, 36)
        if bar >= 4:
            s.chord(V2, Ps(*v2), B(bar), 4, 36 + swell, spread=0.07)
        if bar >= 8:
            s.note(V1, "Eb5" if bar % 2 == 0 else "C5", B(bar), 4, 34)
        if bar % 2 == 0:
            s.harp_arp(Ps(vc[0], va[0], va[1], v2[0] if bar >= 4 else va[1]),
                       B(bar), 0.5, 40)

    # The oboe sings (bars 1-8).
    s.line(OB, DOUBT_SOLO, B(0), MP + 6)

    # Flute takes it an octave up; clarinet in gentle sixths (bars 9-14).
    s.line(FL, [(p if p is None else p[:-1] + str(int(p[-1]) + 1), d)
                for p, d in DOUBT_SOLO[:10]], B(8), MP + 2)
    s.line(CL, [("Eb5", 3), ("Db5", 1), ("C5", 2), ("Bb4", 1), ("Ab4", 1),
                ("Ab4", 2), ("C5", 2)], B(8), MP - 6)
    # Small climax and sigh (bars 13-16).
    s.line(FL, [("Eb6", 2), ("F6", 1), ("Eb6", 1),
                ("C6", 1.5), ("Bb5", 0.5), ("Ab5", 2)], B(12), MF, MP)
    s.line(OB, [("C5", 2), ("Bb4", 1), ("G4", 1), ("Ab4", 4)], B(14), MP, Pdyn)
    s.line(HN, [("Eb3", 1), ("Ab3", 3)], B(13), Pdyn)   # far-off rising 4th
    s.tempo(B(14), 70)
    s.tempo(B(15), 64)
    s.harp_arp(Ps("Ab1", "Eb2", "C3", "Ab3", "C4", "Eb4", "Ab4"), B(15), 0.4, 42)
    return t0 + 64


# ================================================= SECTION V — THE LONG NIGHT
# 14 bars + G.P., C minor, q=126->138. Lament ground; the call, failing.

def long_night(s, t0):
    s.tempo(t0, 126)
    B = lambda b: t0 + 4 * b
    ground = [("C", 2), ("Bb", 2), ("A", 2), ("Ab", 2), ("G", 4)]

    for cyc in range(3):                       # three turns of the ground
        t = B(3 * cyc)
        base = 44 + 14 * cyc
        for name, d in ground:
            s.note(VC, name + "3" if name in ("C", "Bb") and False else name + "2",
                   t, d, base)
            s.note(CB, name + "1" if name not in ("C",) else "C2", t, d, base - 4)
            t += d

    s.roll(TI, P("C3"), B(0), 8, PP, Pdyn)
    s.line(BN, [("C4", 3), ("Bb3", 1), ("Ab3", 2), ("G3", 2), ("G3", 3),
                (None, 1)], B(0), MP)          # doubt, gone dark

    # Cycle 2: tremolo mist, the inverted summons (muted trumpet), ghost taps.
    s.tremolo(VA, P("Eb4"), B(3), 12, 36)
    s.line(TP, [("G4", 2), ("D4", 1), ("C4", 1), ("B3", 3), (None, 1)],
           B(3), Pdyn + 4)
    for off in (0.5, 2.75, 5.5, 8.25, 10.5):
        s.hit(SD, B(3) + off, 28)
    s.note(CL, "G3", B(3), 12, 38)

    # Cycle 3: chromatic violins, brass swells, diminished stabs.
    s.tremolo(VA, P("Eb4"), B(6), 12, 48)
    s.tremolo(V2, P("G4"), B(6), 12, 44)
    chrom = ["G4", "Ab4", "A4", "Bb4", "B4", "C5", "Db5", "D5",
             "Eb5", "E5", "F5", "F#5"]
    for i, p in enumerate(chrom):
        s.note(V1, p, B(6) + i, 1, ramp(MP, F, i, 12), jitter=False)
    s.chord(TB, Ps("C3", "G3"), B(6), 4, MP)
    s.chord(TB, Ps("C3", "G3"), B(7), 8, MF)
    s.note(TU, "C2", B(6), 12, MP)
    s.chord(HN, Ps("B3", "D4", "F4", "Ab4"), B(7) + 2, 0.5, F, spread=0)
    s.chord(HN, Ps("D4", "F4", "Ab4", "B4"), B(8) + 2, 0.5, F + 6, spread=0)
    s.line(BN, [("C3", 2), ("B2", 2), ("Bb2", 2), ("A2", 2), ("Ab2", 4)],
           B(6), MF)

    s.tempo(B(9), 132)
    # Bars 10-11: diminished ladder, chromatic ascent, the dark crest.
    dim = [Ps("B3", "D4", "F4", "Ab4"), Ps("D4", "F4", "Ab4", "B4"),
           Ps("F4", "Ab4", "B4", "D5"), Ps("Ab4", "B4", "D5", "F5")]
    for i, ch_ in enumerate(dim):
        t = B(9) + 2 * i
        s.chord(TP, ch_, t, 2, FF - 12 + 3 * i, spread=0)
        s.chord(TB, [p - 12 for p in ch_[:3]], t, 2, FF - 14 + 3 * i, spread=0)
    climb = [P("G4") + i for i in range(16)]
    for i, p in enumerate(climb):
        v = ramp(F, FF, i, 16)
        s.note(V1, p, B(9) + 0.5 * i, 0.5, v, jitter=False)
        s.note(V2, p - 12, B(9) + 0.5 * i, 0.5, v - 6, jitter=False)
        s.note(VA, p - 12, B(9) + 0.5 * i, 0.5, v - 8, jitter=False)
    s.roll(TI, P("C3"), B(9), 8, MF, FF)
    s.hit(BD, B(9), F)
    s.hit(BD, B(10), F + 8)
    s.snare_roll(B(10), 4, MF, FF)
    for k in range(8):
        s.note(VC, ["C3", "G2"][k % 2], B(9) + k, 1, F, jitter=False)
        s.note(CB, ["C2", "G1"][k % 2], B(9) + k, 1, F - 6, jitter=False)

    # Bar 12: German sixth -> I 6/4. Bar 13-14: dominant pedal, fff, then CUT.
    s.tempo(B(11), 138)
    ger = Ps("B2", "Eb3", "Gb3", "A3")
    s.chord(TB, ger, B(11), 2, FFF - 8, spread=0)
    s.chord(HN, Ps("Eb4", "A4"), B(11), 2, FFF - 8, spread=0)
    s.chord(TP, Ps("Gb4", "B4", "Eb5"), B(11), 2, FFF - 8, spread=0)
    s.note(TU, "B1", B(11), 2, FF)
    s.chord(V1, Ps("Gb5", "B5"), B(11), 2, FF, spread=0)
    s.chord(TB, Ps("Bb2", "Eb3", "G3"), B(11) + 2, 2, FFF - 6, spread=0)
    s.chord(HN, Ps("Eb4", "Bb4"), B(11) + 2, 2, FFF - 6, spread=0)
    s.chord(TP, Ps("G4", "Eb5"), B(11) + 2, 2, FFF - 6, spread=0)
    s.note(TU, "Bb1", B(11) + 2, 2, FF)
    s.chord(V1, Ps("G5", "Bb5"), B(11) + 2, 2, FF, spread=0)
    s.hit(CRASH, B(11), FF)

    for bar in (12, 13):                       # dominant pedal
        s.chord(TB, Ps("Bb2", "F3", "Ab3"), B(bar), 4, FFF - 4, spread=0)
        s.chord(HN, Ps("D4", "F4", "Bb4"), B(bar), 4, FFF - 4, spread=0)
        s.chord(TP, Ps("Bb4", "D5", "F5"), B(bar), 4, FFF - 4, spread=0)
        s.note(TU, "Bb1", B(bar), 4, FF)
        churn = ["Bb4", "Ab4", "G4", "F4"] * 4
        for i, p in enumerate(churn):
            s.note(V1, p, B(bar) + i * 0.25, 0.25, FF, jitter=False)
            s.note(V2, p, B(bar) + i * 0.25, 0.25, FF - 8, jitter=False)
            s.note(VA, P(p) - 12, B(bar) + i * 0.25, 0.25, FF - 10,
                   jitter=False)
        s.note(VC, "Bb2", B(bar), 4, FF)
        s.note(CB, "Bb1", B(bar), 4, FF - 4)
    s.roll(TI, P("Bb2"), B(12), 7.5, F, FFF)
    s.snare_roll(B(12), 7.5, F, FFF)
    s.hit(CRASH, B(12), FF + 6)
    # The cut: nothing on beat 4 of bar 14. Then the G.P. — a bar of silence.
    s.tempo(B(14), 66)
    return t0 + 60                             # 14 bars + 1 G.P. bar


# ==================================================== SECTION VI — THE SUNRISE
# 6 bars, q=63. V7 resolves deceptively to C-flat major: the awe chord. Bells.

def sunrise(s, t0):
    s.tempo(t0, 63)
    B = lambda b: t0 + 4 * b
    s.to_bells(t0)

    # Bar 1: C-flat major, strings alone, pp -> the first bell.
    s.chord(VC, Ps("Cb3", "Gb3"), B(0), 4, PP, spread=0.06)
    s.note(VA, "Eb4", B(0), 4, PP)
    s.note(V2, "Gb4", B(0), 4, PP)
    s.note(V1, "Cb5", B(0), 4, PP + 4)
    s.note(CB, "Cb2", B(0), 8, PP)
    s.note(BELLS, "Cb5", B(0), 3.9, MF + 2, jitter=False)  # the first bell

    # Bar 2: horns and woodwinds bloom into it, crescendo.
    s.chord(HN, Ps("Cb4", "Eb4", "Gb4"), B(1), 4, MP, spread=0.05)
    s.chord(CL, Ps("Eb4", "Gb4"), B(1), 4, MP - 6)
    s.note(FL, "Eb5", B(1), 4, MP)
    s.note(OB, "Gb5", B(1), 4, MP - 4)
    s.note(BELLS, "Cb5", B(1), 5, MF, jitter=False)
    s.note(BELLS, "Gb4", B(1) + 2, 4, MF - 8, jitter=False)
    for ch_, ps in ((VC, ("Cb3", "Gb3")), (VA, ("Eb4",)), (V2, ("Gb4",)),
                    (V1, ("Cb5",))):
        s.chord(ch_, Ps(*ps), B(1), 4, MF)

    # Bar 3: B-flat sus — homeward gravity; the change-ring begins.
    s.chord(TB, Ps("Bb2", "F3"), B(2), 4, MF)
    s.chord(HN, Ps("Eb4", "F4"), B(2), 4, MF + 6)
    s.chord(TP, Ps("Bb4", "Eb5"), B(2), 4, MF)
    s.chord(VC, Ps("Bb2", "F3"), B(2), 4, MF + 4)
    s.note(VA, "Eb4", B(2), 4, MF)
    s.chord(V2, Ps("F4", "Bb4"), B(2), 4, MF)
    s.note(V1, "Eb5", B(2), 4, MF + 4)
    s.note(CB, "Bb1", B(2), 4, MF)
    for i, p in enumerate(RING):
        s.note(BELLS, p, B(2) + i, 0.95, F - 6, jitter=False)

    # Bar 4: B-flat 7; woodwind light floods up two octaves.
    s.chord(TB, Ps("Bb2", "F3", "Ab3"), B(3), 4, F)
    s.chord(HN, Ps("D4", "F4", "Bb4"), B(3), 4, F)
    s.chord(TP, Ps("Bb4", "D5"), B(3), 4, F - 4)
    s.note(TU, "Bb1", B(3), 4, MF)
    bb_scale = [0, 2, 4, 5, 7, 9, 10, 12, 14, 16, 17, 19, 21, 22, 24]
    for i, semi in enumerate(bb_scale):
        v = ramp(MP, FF - 8, i, len(bb_scale))
        s.note(FL, P("Bb4") + semi, B(3) + i * 0.25, 0.3, v, jitter=False)
        s.note(CL, P("Bb3") + semi, B(3) + i * 0.25, 0.3, v - 8, jitter=False)
    s.roll(TI, P("Bb2"), B(3), 4, MF, F)
    for i, p in enumerate(RING * 2):
        s.note(BELLS, p, B(3) + i * 0.5, 0.45, F, jitter=False)
    for ch_, p in ((VC, "Bb2"), (VA, "F4"), (V2, "Bb4"), (V1, "D5"), (CB, "Bb1")):
        s.note(ch_, p, B(3), 4, F)

    # Bars 5-6: the dominant, broadening — everyone leaning toward E-flat.
    s.tempo(B(4), 58)
    s.chord(TB, Ps("Bb2", "F3", "Ab3"), B(4), 8, F + 6)
    s.note(TU, "Bb1", B(4), 8, F)
    s.chord(HN, Ps("D4", "F4", "Bb4"), B(4), 8, F + 8)
    s.chord(TP, Ps("Bb4", "D5", "F5"), B(4), 8, F + 4)
    s.line(V1, [("F5", 1), ("G5", 1), ("Ab5", 1), ("Bb5", 1)], B(4), F, FF)
    s.line(V2, [("D5", 1), ("Eb5", 1), ("F5", 1), ("G5", 1)], B(4), F - 6, FF - 8)
    s.note(VA, "Bb3", B(4), 8, F)
    s.chord(VC, Ps("Bb2", "Ab3"), B(4), 8, F)
    s.note(CB, "Bb1", B(4), 8, F)
    s.line(FL, [("Bb6", 2), ("Ab6", 1), ("F6", 1)], B(4), FF - 8)
    s.line(OB, [("Bb5", 2), ("Ab5", 1), ("F5", 1)], B(4), F)
    s.snare_roll(B(5), 4, MP, FF)
    s.roll(TI, P("Bb2"), B(5), 4, F, FFF - 8)
    s.cym_swell(B(5), 4, 24, 86)
    s.note(BELLS, "Bb4", B(4), 4, FF - 10, jitter=False)
    s.note(BELLS, "F4", B(5), 1, FF - 10, jitter=False)
    s.note(BELLS, "Bb4", B(5) + 2, 2, FF, jitter=False)
    return t0 + 24


# ================================================== SECTION VII — APOTHEOSIS
# 18 bars, q=86. The anthem, fff — and the doubt-theme inside it, transfigured.

PILLARS_A = [  # per strain-A bar: trombone triad, tuba/bass root
    (("Eb3", "Bb3", "G4"), "Eb2"), (("C3", "G3", "Eb4"), "C2"),
    (("Ab2", "Eb3", "C4"), "Ab1"), (("Bb2", "F3", "D4"), "Bb1"),
    (("Eb3", "Bb3", "G4"), "Eb2"), (("F3", "C4", "Eb4"), "F2"),
    (("Bb2", "F3", "Ab3"), "Bb1"), (("Eb3", "G3", "Bb3"), "Eb2"),
]
PILLARS_B = [
    (("Ab2", "Eb3", "C4"), "Ab1"), (("G3", "Eb4", "Bb3"), "Eb2"),
    (("C3", "G3", "Eb4"), "C2"), (("F3", "C4", "A3"), "F2"),
    (("Ab2", "Eb3", "C4"), "Ab1"), (("Bb2", "F3", "Ab3"), "Bb1"),
    (("Eb3", "Bb3", "G4"), "Eb2"), (("Ab2", "Eb3", "C4"), "Ab1"),
]
TIMP_ROOTS = {"Eb2": P("Eb2"), "C2": P("C3"), "Ab1": P("Ab2"),
              "Bb1": P("Bb2"), "F2": P("F3"), "Eb3": P("Eb3")}


def apotheosis(s, t0):
    s.tempo(t0, 86)
    B = lambda b: t0 + 4 * b

    # Phrase contour: arrival blazes, second phrase eases, the lift rebuilds.
    s.shape(B(4), B(8), -13)
    s.shape(B(8), B(10), -7)
    s.shape(B(10), B(12), -3)
    s.shape(B(15), B(18), +3)

    # ---- strain A (bars 1-8): anthem + doubt-counterpoint together at last.
    s.line(TP, ANTHEM_A, B(0), FF + 4)
    s.line(V1, ANTHEM_A, B(0), FF, oct_shift=1)
    s.line(FL, ANTHEM_A, B(0), FF - 6, oct_shift=1)
    s.line(OB, ANTHEM_A, B(0), FF - 8)
    s.line(V2, ANTHEM_A, B(0), FF - 6)
    s.line(HN, DOUBT, B(0), FF, oct_shift=-1)          # the private voice, proud
    s.line(VC, DOUBT, B(0), FF - 4, oct_shift=-1)
    s.line(VA, DOUBT, B(0), FF - 8, oct_shift=-1)

    for i, (tri, root) in enumerate(PILLARS_A):
        s.chord(TB, Ps(*tri), B(i), 4, FF - 6, spread=0.03)
        s.note(TU, root, B(i), 4, FF - 8)
        s.note(CB, P(root) + 12, B(i), 4, FF - 8)
        for k in range(4):                              # bassoon pulse
            s.note(BN, P(root) + 12 + (12 if k % 2 else 0), B(i) + k, 0.9,
                   F, jitter=False)
        if i not in (3, 7):                             # roll bars: no taps
            r = TIMP_ROOTS[root]
            s.note(TI, r, B(i), 1, FF - 6, jitter=False)
            s.note(TI, r, B(i) + 2, 1, FF - 12, jitter=False)
    s.hit(BD, B(0), FF)
    s.hit(CRASH, B(0), FF)
    s.roll(TI, P("Bb2"), B(3), 4, F, FF - 6)
    s.roll(TI, P("Eb3"), B(7), 4, F, FF - 6)
    for i, p in enumerate(RING):                        # bells in the breaths
        s.note(BELLS, p, B(3) + i, 1.2, F, jitter=False)
        s.note(BELLS, p, B(7) + i, 1.2, F, jitter=False)
    cl_run = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 21, 19, 16, 14, 12]
    for i, semi in enumerate(cl_run):                   # garland, bar 2 & 6
        s.note(CL, P("G3") + semi, B(1) + i * 0.25, 0.3, F + 2, jitter=False)
        s.note(CL, P("G3") + semi, B(5) + i * 0.25, 0.3, F + 2, jitter=False)

    # ---- strain B (bars 9-16): the lift, with the slow ascending counter.
    # (Plagal tails dropped: bars 15-18 are re-lit by the deceptive extension.)
    s.line(TP, ANTHEM_B[:-3], B(8), FF + 6)
    s.line(V1, ANTHEM_B[:-3], B(8), FF + 2, oct_shift=1)
    s.line(FL, ANTHEM_B[:-3], B(8), FF - 4, oct_shift=1)
    s.line(OB, ANTHEM_B[:-3], B(8), FF - 6)
    s.line(V2, ANTHEM_B[:-3], B(8), FF - 4)
    s.line(HN, COUNTER_B[:-3], B(8), FF)
    s.line(VC, COUNTER_B[:-3], B(8), FF - 4)
    s.line(VA, COUNTER_B[:-3], B(8), FF - 8)

    for i, (tri, root) in enumerate(PILLARS_B[:6]):
        s.chord(TB, Ps(*tri), B(8 + i), 4, FF - 4, spread=0.03)
        s.note(TU, root, B(8 + i), 4, FF - 6)
        s.note(CB, P(root) + 12, B(8 + i), 4, FF - 6)
        for k in range(4):
            s.note(BN, P(root) + 12 + (12 if k % 2 else 0), B(8 + i) + k, 0.9,
                   F + 4, jitter=False)
        if i != 5:                                      # bar 14 is a roll bar
            r = TIMP_ROOTS[root]
            s.note(TI, r, B(8 + i), 1, FF - 4, jitter=False)
            s.note(TI, r, B(8 + i) + 2, 1, FF - 10, jitter=False)
    s.hit(BD, B(8), FF + 4)
    s.hit(CRASH, B(8), FF + 4)
    s.hit(BD, B(12), FF + 4)
    s.hit(CRASH, B(12), FF)
    for bar in range(12, 16):                           # triangle sparkle
        for k in range(8):
            s.hit(TRI, B(bar) + 0.5 * k, 44 if k % 2 else 56)
    for i, semi in enumerate([0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 17, 16, 14, 12]):
        s.note(BN, P("Ab2") + semi, B(11) + i * 0.25, 0.3, MF + 4, jitter=False)
    s.roll(TI, P("Bb2"), B(13), 4, FF - 6, FF + 4)

    # ---- bars 15-18: deceptive shadow, then the broadening dominant.
    s.tempo(B(14), 86)
    # bar 15 was written into ANTHEM_B's cadence; now re-light it:
    # deceptive C minor under the melody's held E-flat (one last shadow)...
    s.chord(TB, Ps("C3", "G3", "Eb4"), B(14), 4, F, spread=0.04)
    s.note(TU, "C2", B(14), 4, F - 6)
    s.note(CB, "C2", B(14), 4, F - 6)
    s.note(TI, P("C3"), B(14), 2, F, jitter=False)
    # ...then IV, I 6/4, V7 — the door swings wide (bars 16-18).
    s.tempo(B(15), 80)
    s.tempo(B(16), 74)
    grand = [
        (Ps("Ab2", "Eb3", "C4"), "Ab1", Ps("Eb4", "Ab4", "C5"),
         Ps("Ab4", "C5", "Eb5"), Ps("Eb5", "Ab5"), "Ab2"),
        (Ps("Bb2", "G3", "Eb4"), "Eb2", Ps("Eb4", "G4", "Bb4"),
         Ps("G4", "Bb4", "Eb5"), Ps("G5", "Bb5"), "Eb3"),
        (Ps("Bb2", "F3", "Ab3"), "Bb1", Ps("D4", "F4", "Bb4"),
         Ps("F4", "Ab4", "D5"), Ps("F5", "Ab5"), "Bb2"),
    ]
    for i, (tbn, tu, hn, tp, hi, ti) in enumerate(grand):
        t = B(15 + i)
        dur = 4 if i < 2 else 3.0               # luftpause after the V7
        s.chord(TB, tbn, t, dur, FF, spread=0.03)
        s.note(TU, tu, t, dur, FF - 6)
        s.chord(HN, hn, t, dur, FF + 2, spread=0.03)
        s.chord(TP, tp, t, dur, FF, spread=0.03)
        s.chord(V1, [p + 12 for p in hi], t, dur, FF, spread=0.03)
        s.chord(V2, hi, t, dur, FF - 4, spread=0.03)
        s.chord(VA, hn, t, dur, FF - 6, spread=0.03)
        s.chord(VC, tbn, t, dur, FF - 2, spread=0.03)
        s.note(CB, P(tu) + 12, t, dur, FF - 4)
        s.note(FL, hi[-1] + 12, t, dur, FF - 8)
        s.note(OB, hi[-1], t, dur, FF - 10)
        s.note(CL, hi[0], t, dur, FF - 10)
        s.roll(TI, TIMP_ROOTS.get(ti, P(ti)) if isinstance(ti, str) else ti,
               t, dur, F, FF + 4)
    s.hit(CRASH, B(15), FF)
    s.hit(BD, B(15), FF)
    s.snare_roll(B(16), 7, F, FFF)
    s.note(BELLS, "Eb5", B(15), 2, FF, jitter=False)
    s.note(BELLS, "Bb4", B(16), 2, FF, jitter=False)
    s.note(BELLS, "Eb5", B(17), 2, FF, jitter=False)
    return t0 + 72


# ======================================================= SECTION VIII — CODA
# 12 bars. Hemiola peal; the far-off horn at dawn; the final blaze; bells last.

def coda(s, t0):
    s.tempo(t0, 82)
    B = lambda b: t0 + 4 * b

    # Bars 1-3: pealing hemiola — 3-beat chords ringing across the barline.
    peal = [
        (Ps("Eb3", "Bb3", "G4"), "Eb2", Ps("G4", "Bb4", "Eb5"), "Eb5", 3),
        (Ps("C3", "Ab3", "Eb4"), "Ab1", Ps("Ab4", "C5", "Eb5"), "C5", 3),
        (Ps("Bb2", "G3", "Eb4"), "Eb2", Ps("G4", "Bb4", "Eb5"), "Bb4", 3),
        (Ps("Ab2", "Eb3", "C4"), "Ab1", Ps("Ab4", "C5", "Eb5"), "C5", 2),
    ]
    t = B(0)
    for tbn, root, upper, bell, d in peal:
        s.chord(TB, tbn, t, d, FF, spread=0)
        s.note(TU, root, t, d, FF - 6)
        s.chord(HN, [p - 12 for p in upper], t, d, FF, spread=0)
        s.chord(TP, upper, t, d, FF - 2, spread=0)
        s.chord(V1, [p + 12 for p in upper], t, d, FF, spread=0)
        s.chord(V2, upper, t, d, FF - 4, spread=0)
        s.chord(VA, [p - 12 for p in upper], t, d, FF - 6, spread=0)
        s.chord(VC, tbn, t, d, FF - 4, spread=0)
        s.note(CB, P(root) + 12, t, d, FF - 6)
        s.note(BELLS, bell, t, d - 0.5, FF - 4, jitter=False)
        s.note(TI, TIMP_ROOTS[root], t, 1.5, FF, jitter=False)
        s.hit(BD, t, FF - 4)
        t += d
    # bar 3, beat 4: a quick climb to the cut.
    s.line(V1, [("F5", 0.5), ("G5", 0.5)], B(2) + 3, FF)
    s.line(FL, [("F6", 0.5), ("G6", 0.5)], B(2) + 3, FF - 6)

    # Bar 4: one great B-flat-7 — cut — timpani alone decays.
    s.chord(TB, Ps("Bb2", "F3", "Ab3"), B(3), 1.5, FFF - 4, spread=0)
    s.chord(HN, Ps("D4", "F4", "Bb4"), B(3), 1.5, FFF - 4, spread=0)
    s.chord(TP, Ps("Bb4", "D5", "F5"), B(3), 1.5, FFF - 4, spread=0)
    s.note(TU, "Bb1", B(3), 1.5, FF)
    s.chord(V1, Ps("Bb5", "D6"), B(3), 1.5, FF, spread=0)
    s.chord(V2, Ps("F5", "Bb5"), B(3), 1.5, FF - 4, spread=0)
    s.hit(CRASH, B(3), FFF - 8)
    s.hit(BD, B(3), FF)
    s.roll(TI, P("Bb2"), B(3) + 1.5, 2.5, FF, PP)

    # Bars 5-8: subito pp — the next morning. The Summons, far off.
    s.tempo(B(4), 64)
    for bar in range(4, 8):
        v = 30 + (bar - 4)
        s.note(V1, "Bb4", B(bar), 4, v)
        s.note(V1, "Eb5", B(bar) + 0.05, 4, v)
        s.note(V2, "G4", B(bar), 4, v)
        s.note(VA, "Bb3", B(bar), 4, v - 2)
        s.note(VC, "Eb3", B(bar), 4, v)
        s.note(CB, "Eb2", B(bar), 4, v - 2)
    s.line(HN, SUMMONS, B(4), MP)                       # at dawn, again
    s.line(FL, [("Eb5", 2), ("G4", 1), ("Ab4", 1)], B(6), Pdyn)
    s.line(CL, [("Eb4", 1), ("Ab4", 3)], B(7), Pdyn)
    s.note(BELLS, "Eb5", B(7), 4, Pdyn, jitter=False)   # a far city bell

    # Bars 9-12: the final ascent — Amen subdominant, dominant, blaze.
    s.tempo(B(8), 58)
    s.chord(VC, Ps("Ab2", "Eb3"), B(8), 4, F - 8)
    s.chord(VA, Ps("C4", "Eb4"), B(8), 4, F - 10)
    s.chord(V2, Ps("Ab4", "Bb4"), B(8), 4, F - 8)       # add9 shimmer
    s.chord(V1, Ps("C5", "Eb5"), B(8), 4, F - 6)
    s.note(CB, "Ab1", B(8), 4, F - 10)
    s.chord(HN, Ps("Ab3", "C4", "Eb4"), B(8), 4, F - 4, spread=0.05)
    s.chord(BN, Ps("Ab2", "Eb3"), B(8), 4, F - 8)
    s.roll(TI, P("Ab2"), B(8), 4, Pdyn, F)

    s.tempo(B(9), 54)
    s.chord(TB, Ps("Bb2", "F3", "Ab3"), B(9), 4, FF - 4, spread=0.04)
    s.note(TU, "Bb1", B(9), 4, FF - 8)
    s.chord(HN, Ps("D4", "F4", "Bb4"), B(9), 4, FF, spread=0.04)
    s.chord(TP, Ps("Bb4", "D5"), B(9), 4, FF - 4, spread=0.04)
    s.line(V1, [("Bb4", 1), ("C5", 1), ("D5", 1), ("F5", 1)], B(9), F, FF)
    s.line(V2, [("F4", 1), ("G4", 1), ("Ab4", 1), ("Bb4", 1)], B(9), F - 6, FF - 8)
    s.note(VA, "F4", B(9), 4, F)
    s.chord(VC, Ps("Bb2", "Ab3"), B(9), 4, F)
    s.note(CB, "Bb1", B(9), 4, F)
    s.snare_roll(B(9), 4, MP, FFF - 8)
    s.cym_swell(B(9), 4, 30, 96)
    s.roll(TI, P("Bb2"), B(9), 4, F, FFF)

    # The blaze: E-flat major across five octaves, two great waves.
    s.tempo(B(10), 48)
    s.tempo(B(11), 42)
    for bar, accent in ((10, 0), (11, 4)):
        t, v = B(bar), FFF - 4 + accent
        s.note(TU, "Eb1", t, 4, v - 8)
        s.chord(TB, Ps("Bb2", "Eb3", "G3"), t, 4, v - 4, spread=0.03)
        s.chord(HN, Ps("Eb4", "G4", "Bb4"), t, 4, v, spread=0.03)
        s.chord(TP, Ps("Bb4", "Eb5", "G5"), t, 4, v, spread=0.03)
        s.chord(BN, Ps("Eb2", "Bb2"), t, 4, v - 10)
        s.note(CB, "Eb2", t, 4, v - 6)
        s.chord(VC, Ps("Eb3", "Bb3"), t, 4, v - 4, spread=0.03)
        s.chord(VA, Ps("Eb4", "G4"), t, 4, v - 6, spread=0.03)
        s.chord(V2, Ps("Bb4", "Eb5"), t, 4, v - 4, spread=0.03)
        s.chord(V1, Ps("G5", "Eb6"), t, 4, v, spread=0.03)
        s.note(FL, "Eb6", t, 4, v - 6)
        s.note(OB, "Eb5", t, 4, v - 10)
        s.note(CL, "G5", t, 4, v - 10)
        s.hit(CRASH, t, v)
        s.hit(BD, t, v - 4)
    s.roll(TI, P("Eb2"), B(10), 8, FF, FFF + 4)
    s.note(BELLS, "Eb5", B(10), 1, FFF - 8, jitter=False)
    s.note(BELLS, "Bb4", B(10) + 1, 1, FFF - 12, jitter=False)
    s.note(BELLS, "Eb5", B(10) + 2, 2, FFF - 8, jitter=False)
    # The last bell rings alone into the silence after the cutoff.
    s.note(BELLS, "Eb5", B(11), 10, FFF, jitter=False)
    return t0 + 48 + 8                                  # + ring-out pad


# ============================================================ BUILD

def build():
    s = Score(seed=11)
    t = 0.0
    sections = []
    for name, fn in [("I. Dawn", dawn), ("II. The Anthem", the_anthem),
                     ("III. The Work", the_work),
                     ("IV. The Single Voice", single_voice),
                     ("V. The Long Night", long_night),
                     ("VI. The Sunrise", sunrise),
                     ("VII. Apotheosis", apotheosis), ("VIII. Coda", coda)]:
        sections.append((name, t))
        t = fn(s, t)
    return s, sections, t


if __name__ == "__main__":
    import os
    s, sections, end = build()
    out = os.path.join(os.path.dirname(__file__), "..", "out", "anthem.mid")
    s.save(out)
    print(f"notes: {len(s.notes)}")
    for name, beat in sections:
        m, sec = divmod(s.seconds_at(beat), 60)
        print(f"  {int(m)}:{sec:04.1f}  {name}")
    m, sec = divmod(s.seconds_at(end), 60)
    print(f"total: {int(m)}:{sec:04.1f}")
    print(f"saved: {os.path.abspath(out)}")
