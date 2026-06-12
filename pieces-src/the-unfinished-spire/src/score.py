"""Score: a thin composition framework over MIDIUtil.

Absolute-beat note placement, global tempo map, per-instrument range
validation, deterministic humanization, and reusable orchestral figures
(rolls, swells, hairpin ramps).
"""

import random
from midiutil import MIDIFile

# ---------------------------------------------------------------- pitches

_STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def P(name):
    """'Eb4' -> 63 (C4 = 60)."""
    step = _STEP[name[0]]
    i = 1
    while i < len(name) and name[i] in "b#":
        step += 1 if name[i] == "#" else -1
        i += 1
    return step + 12 * (int(name[i:]) + 1)


def Ps(*names):
    return [P(n) for n in names]


# ---------------------------------------------------------------- dynamics

PP, Pdyn, MP, MF, F, FF, FFF = 32, 45, 58, 72, 88, 104, 116


def ramp(v0, v1, i, n):
    """Velocity for note i of n along a linear hairpin v0 -> v1."""
    if n <= 1:
        return int(v1)
    return int(round(v0 + (v1 - v0) * i / (n - 1)))


# ---------------------------------------------------------------- channels

FL, OB, CL, BN, HN, TP, TB, TU, TI, PERC = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
V1, V2, VA, VC, CB, HARP = 10, 11, 12, 13, 14, 15
BELLS = HARP  # same channel, program change at the Sunrise

CHANNEL_NAMES = {
    FL: "Flute", OB: "Oboe", CL: "Clarinet", BN: "Bassoon", HN: "Horns",
    TP: "Trumpets", TB: "Trombones", TU: "Tuba", TI: "Timpani",
    PERC: "Percussion", V1: "Violin I", V2: "Violin II", VA: "Viola",
    VC: "Cello", CB: "Contrabass", HARP: "Harp/Bells",
}

PROGRAMS = {FL: 73, OB: 68, CL: 71, BN: 70, HN: 60, TP: 56, TB: 57, TU: 58,
            TI: 47, V1: 48, V2: 48, VA: 48, VC: 48, CB: 48, HARP: 46}
PANS = {FL: 55, OB: 68, CL: 48, BN: 72, HN: 38, TP: 70, TB: 78, TU: 82,
        TI: 60, PERC: 64, V1: 30, V2: 45, VA: 75, VC: 88, CB: 95, HARP: 35}

# Sounding ranges (inclusive MIDI), enforced on every note.
RANGES = {
    FL: (P("C4"), P("C7")), OB: (P("Bb3"), P("G6")), CL: (P("D3"), P("G6")),
    BN: (P("Bb1"), P("Eb5")), HN: (P("F2"), P("F5")), TP: (P("E3"), P("Bb5")),
    TB: (P("E2"), P("Bb4")), TU: (P("D1"), P("F4")), TI: (P("D2"), P("C4")),
    V1: (P("G3"), P("B6")), V2: (P("G3"), P("E6")), VA: (P("C3"), P("C6")),
    VC: (P("C2"), P("A5")), CB: (P("E1"), P("G4")),
    HARP: (P("C1"), P("G7")),
}
BELL_RANGE = (P("C4"), P("F5"))  # tubular bells, enforced after the program change

# GM percussion keys (channel 9)
BD, SD, CRASH, CRASH2, TRI = 36, 38, 49, 57, 81


class Score:
    def __init__(self, seed=11):
        self.mf = MIDIFile(16, adjust_origin=False)
        self.rng = random.Random(seed)
        self.tempo_map = []          # (beat, bpm) sorted
        self.notes = []              # (ch, pitch, start, dur, vel) for analysis
        self.bell_start = None       # beat where ch15 becomes tubular bells
        self.shapes = []             # (beat0, beat1, vel_delta) phrase contours
        for ch in range(16):
            self.mf.addTrackName(ch, 0, CHANNEL_NAMES.get(ch, f"ch{ch}"))
            if ch != PERC:
                self.mf.addProgramChange(ch, ch, 0, PROGRAMS[ch])
            self.mf.addControllerEvent(ch, ch, 0, 10, PANS[ch])
            self.mf.addControllerEvent(ch, ch, 0, 91, 78)   # hall reverb
            self.mf.addControllerEvent(ch, ch, 0, 7, 100)   # channel volume

    # -------------------------------------------------------- conducting

    def tempo(self, beat, bpm):
        self.tempo_map.append((beat, bpm))
        self.mf.addTempo(0, beat, bpm)

    def to_bells(self, beat):
        """Switch channel 15 from harp to tubular bells."""
        self.bell_start = beat
        self.mf.addProgramChange(BELLS, BELLS, beat - 0.05, 14)

    def shape(self, beat0, beat1, delta):
        """Velocity contour: add delta to every note starting in [beat0, beat1)."""
        self.shapes.append((beat0, beat1, delta))

    def seconds_at(self, beat):
        """Real time of an absolute beat under the tempo map."""
        tm = sorted(self.tempo_map)
        t, last_beat, last_bpm = 0.0, 0.0, tm[0][1]
        for b, bpm in tm:
            if b >= beat:
                break
            t += (b - last_beat) * 60.0 / last_bpm
            last_beat, last_bpm = b, bpm
        return t + (beat - last_beat) * 60.0 / last_bpm

    # -------------------------------------------------------- core notes

    def note(self, ch, pitch, start, dur, vel, jitter=True):
        if isinstance(pitch, str):
            pitch = P(pitch)
        if ch != PERC:
            lo, hi = RANGES[ch]
            if ch == BELLS and self.bell_start is not None and start >= self.bell_start:
                lo, hi = BELL_RANGE
            assert lo <= pitch <= hi, (
                f"{CHANNEL_NAMES[ch]} out of range: {pitch} at beat {start} "
                f"(allowed {lo}-{hi})")
        for b0, b1, dv in self.shapes:
            if b0 <= start < b1:
                vel += dv
        vel = max(1, min(127, int(vel)))
        if jitter:
            start = start + self.rng.uniform(0.0, 0.018)
            vel = max(1, min(127, vel + self.rng.randint(-3, 3)))
        dur = max(0.05, dur * 0.985)  # shave: avoid same-pitch overlap quirks
        self.mf.addNote(ch, ch, pitch, start, dur, vel)
        self.notes.append((ch, pitch, start, dur, vel))
        return start + dur

    def chord(self, ch, pitches, start, dur, vel, spread=0.02):
        """Sustained chord; slight upward strum-stagger for warmth."""
        for i, p in enumerate(pitches):
            self.note(ch, p, start + i * spread, dur - i * spread, vel)

    def line(self, ch, seq, start, vel, vel_end=None, oct_shift=0):
        """Melodic line: seq of (pitch_name|None, dur_beats).

        None = rest. Velocity ramps v->vel_end across the line if given.
        Returns end beat.
        """
        notes = [s for s in seq if s[0] is not None]
        n, i, t = len(notes), 0, start
        for pitch, dur in seq:
            if pitch is not None:
                v = ramp(vel, vel_end, i, n) if vel_end is not None else vel
                p = (P(pitch) if isinstance(pitch, str) else pitch) + 12 * oct_shift
                self.note(ch, p, t, dur, v)
                i += 1
            t += dur
        return t

    # -------------------------------------------------------- figures

    def roll(self, ch, pitch, start, dur, v0, v1, rate=0.125):
        """Timpani/snare-style roll: repeated notes with a hairpin."""
        n = max(2, int(dur / rate))
        for i in range(n):
            self.note(ch, pitch, start + i * rate, rate * 0.95,
                      ramp(v0, v1, i, n), jitter=False)

    def snare_roll(self, start, dur, v0, v1):
        self.roll(PERC, SD, start, dur, v0, v1, rate=0.125)

    def cym_swell(self, start, dur, v0, v1):
        """Suspended-cymbal crescendo: soft fast crash retriggers."""
        n = max(2, int(dur / 0.25))
        for i in range(n):
            self.note(PERC, CRASH, start + i * 0.25, 0.24,
                      ramp(v0, v1, i, n), jitter=False)

    def hit(self, key, start, vel):
        self.note(PERC, key, start, 0.2, vel, jitter=False)

    def tremolo(self, ch, pitch, start, dur, vel, rate=0.25):
        n = max(1, int(dur / rate))
        for i in range(n):
            self.note(ch, pitch, start + i * rate, rate, vel, jitter=False)

    def harp_arp(self, pitches, start, step, vel, dur=None):
        """Rising broken chord on the harp channel (duplicates dropped)."""
        seen = set()
        for i, p in enumerate(pitches):
            if p in seen:
                continue
            seen.add(p)
            self.note(HARP, p, start + i * step, dur or step * 1.9, vel)

    # -------------------------------------------------------- output

    def save(self, path):
        with open(path, "wb") as fh:
            self.mf.writeFile(fh)
