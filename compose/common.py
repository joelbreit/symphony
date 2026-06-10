"""Shared composition framework for Symphony No. 1 'The Window'.

Offsets are music21 quarterLengths throughout. Real time is driven by
MetronomeMarks inserted via Orchestra.tempo().
"""
from __future__ import annotations

import random
from fractions import Fraction

from music21 import chord as m21chord
from music21 import instrument, meter, note, stream, tempo

RNG = random.Random(21)  # deterministic builds

# ---------------------------------------------------------------- dynamics

DYN = {
    'ppp': 28, 'pp': 36, 'p': 48, 'mp': 60,
    'mf': 72, 'f': 86, 'ff': 100, 'fff': 112,
}

def vel_of(v):
    return DYN[v] if isinstance(v, str) else int(v)

# ---------------------------------------------------------------- note DSL

DUR = {
    'w': 4.0, 'h': 2.0, 'q': 1.0, 'e': 0.5, 's': 0.25,
    'w.': 6.0, 'h.': 3.0, 'q.': 1.5, 'e.': 0.75,
    't': Fraction(1, 3), 'tq': Fraction(2, 3),
}

def _pitch(tok: str) -> str:
    """'Eb5' -> 'E-5', 'F#4' -> 'F#4' (music21 spelling)."""
    if len(tok) >= 3 and tok[1] == 'b':
        return tok[0] + '-' + tok[2:]
    return tok

def _dur(tok: str):
    if tok in DUR:
        return DUR[tok]
    return float(tok)

def parse(dsl: str):
    """Parse 'G4:q (C3 G3):h r:e' into [(pitch|None|list, ql), ...]."""
    out = []
    s = dsl.split()
    i = 0
    while i < len(s):
        tok = s[i]
        if tok.startswith('('):
            # collect until token containing ')'
            grp = [tok[1:]]
            while ')' not in grp[-1]:
                i += 1
                grp.append(s[i])
            last, dur_part = grp[-1].split(')')
            grp[-1] = last
            grp = [g for g in grp if g]
            ql = _dur(dur_part.lstrip(':'))
            out.append(([_pitch(p) for p in grp], ql))
        else:
            p, d = tok.rsplit(':', 1)
            ql = _dur(d)
            out.append((None if p == 'r' else _pitch(p), ql))
        i += 1
    return out

def _as_events(notes):
    return parse(notes) if isinstance(notes, str) else list(notes)

def total_ql(notes) -> float:
    return float(sum(Fraction(d).limit_denominator(96) for _, d in _as_events(notes)))

def transpose_events(events, semitones: int):
    from music21 import pitch as m21pitch
    out = []
    for p, d in _as_events(events):
        if p is None:
            out.append((None, d))
        elif isinstance(p, list):
            out.append(([m21pitch.Pitch(x).transpose(semitones).nameWithOctave for x in p], d))
        elif isinstance(p, int):
            out.append((p + semitones, d))
        else:
            out.append((m21pitch.Pitch(p).transpose(semitones).nameWithOctave, d))
    return out

# ---------------------------------------------------------------- textures

def trem(pitches, total: float, unit: float = 0.5):
    """Measured tremolo: repeat pitch/chord every `unit` for `total` ql."""
    n = int(round(total / unit))
    return [(pitches, unit)] * n

def ost(pattern, repeats: int):
    return _as_events(pattern) * repeats

def arp(pitches, unit: float, total: float, direction: str = 'up'):
    """Cycle through pitches every `unit` ql for `total` ql."""
    seq = list(pitches)
    if direction == 'updown':
        seq = seq + seq[-2:0:-1]
    n = int(round(total / unit))
    return [(_pitch(seq[i % len(seq)]), unit) for i in range(n)]

def roll(pitch, total: float, unit: float = 0.25):
    return trem(pitch, total, unit)

# ---------------------------------------------------------------- orchestra

# name -> (label, GM program, midi channel, lo, hi)  pitch range guards
ROSTER = {
    'fl':   ('Flutes',          73,  0, 60, 96),
    'ob':   ('Oboes',           68,  1, 58, 89),
    'cl':   ('Clarinets',       71,  2, 50, 91),
    'bsn':  ('Bassoons',        70,  3, 34, 75),
    'hn':   ('Horns',           60,  4, 35, 77),
    'tpt':  ('Trumpets',        56,  5, 52, 84),
    'tbn':  ('Trombones & Tuba', 57, 6, 26, 72),
    'timp': ('Timpani',         47,  7, 38, 57),
    'hp':   ('Harp',            46,  8, 24, 103),
    'cel':  ('Celesta',          8, 10, 60, 108),
    'vln1': ('Violin I',        48, 11, 55, 100),
    'vln2': ('Violin II',       48, 12, 55, 88),
    'vla':  ('Viola',           48, 13, 48, 88),
    'vc':   ('Cello',           48, 14, 36, 81),
    'cb':   ('Contrabass',      48, 15, 28, 55),
}

PERC_KEYS = {'bd': 35, 'crash': 49, 'crash2': 57, 'tamtam': 52, 'susp': 55, 'tri': 81}

class Orchestra:
    def __init__(self):
        self.parts: dict[str, stream.Part] = {}
        self.ends: dict[str, float] = {}
        for name, (label, prog, chan, _, _) in ROSTER.items():
            p = stream.Part(id=name)
            p.partName = label
            inst = instrument.Instrument()
            inst.partName = label
            inst.instrumentName = label
            inst.midiProgram = prog
            inst.midiChannel = chan
            p.insert(0, inst)
            self.parts[name] = p
            self.ends[name] = 0.0
        perc = stream.Part(id='perc')
        perc.partName = 'Percussion'
        pinst = instrument.UnpitchedPercussion()
        pinst.partName = 'Percussion'
        perc.insert(0, pinst)
        self.parts['perc'] = perc
        self.ends['perc'] = 0.0

    # -- conductor events ------------------------------------------------
    def tempo(self, offset: float, bpm: float, text: str | None = None):
        mm = tempo.MetronomeMark(number=bpm, text=text)
        self.parts['vln1'].insert(offset, mm)

    def timesig(self, offset: float, ts: str):
        self.parts['vln1'].insert(offset, meter.TimeSignature(ts))

    def program(self, name: str, offset: float, prog: int):
        """Switch GM program mid-part (e.g. 45=pizzicato, 48=arco ensemble)."""
        label, _, chan, _, _ = ROSTER[name]
        inst = instrument.Instrument()
        inst.partName = label
        inst.instrumentName = label
        inst.midiProgram = prog
        inst.midiChannel = chan
        self.parts[name].insert(offset, inst)

    # -- writing notes ---------------------------------------------------
    def add(self, name: str, offset: float, notes, vel='mf', gate: float = 0.95,
            vel_end=None, transpose: int = 0, accent_first: bool = False):
        """Insert events at absolute offset. Returns end offset.

        vel/vel_end: dynamic names or ints; vel_end ramps across the span.
        gate: fraction of each duration actually sounded (staccato ~0.5).
        """
        part = self.parts[name]
        events = _as_events(notes)
        if transpose:
            events = transpose_events(events, transpose)
        v0 = vel_of(vel)
        v1 = vel_of(vel_end) if vel_end is not None else v0
        n_sounding = sum(1 for p, _ in events if p is not None)
        t = Fraction(offset).limit_denominator(96)
        idx = 0
        for p, d in events:
            d = Fraction(d).limit_denominator(96)
            if p is not None:
                frac = idx / max(1, n_sounding - 1) if n_sounding > 1 else 0.0
                v = round(v0 + (v1 - v0) * frac) + RNG.randint(-3, 3)
                if accent_first and idx == 0:
                    v += 8
                v = max(1, min(127, v))
                sounded = d * Fraction(gate).limit_denominator(20)
                if isinstance(p, list):
                    el = m21chord.Chord(p)
                elif isinstance(p, int):
                    el = note.Note()
                    el.pitch.midi = p
                else:
                    el = note.Note(p)
                el.duration.quarterLength = float(sounded)
                el.volume.velocity = v
                part.insert(float(t), el)
                idx += 1
            t += d
        end = float(t)
        self.ends[name] = max(self.ends[name], end)
        return end

    def perc(self, offset: float, notes, vel='mf'):
        """notes: DSL-like list of (key_name, ql) or 'crash:q r:q' style string."""
        events = []
        if isinstance(notes, str):
            for tok in notes.split():
                k, d = tok.rsplit(':', 1)
                events.append((None if k == 'r' else PERC_KEYS[k], _dur(d)))
        else:
            events = [(PERC_KEYS[k] if isinstance(k, str) else k, d) for k, d in notes]
        return self.add('perc', offset, events, vel=vel, gate=1.0)

    # -- assembly ----------------------------------------------------------
    def score(self) -> stream.Score:
        sc = stream.Score()
        for p in self.parts.values():
            sc.insert(0, p)
        return sc

    def end(self) -> float:
        return max(self.ends.values())

# ---------------------------------------------------------------- output

def write_midi(orch: Orchestra, path: str):
    sc = orch.score()
    sc.write('midi', fp=path)
    _remap_channels(path)
    return path

def _remap_channels(path: str):
    """music21 merges same-program parts onto one channel; force each named
    track onto its roster channel (and percussion onto channel 10)."""
    import mido
    by_label = {label: chan for label, _, chan, _, _ in ROSTER.values()}
    by_label['Percussion'] = 9
    mid = mido.MidiFile(path)
    for tr in mid.tracks:
        name = next((m.name for m in tr if m.type == 'track_name'), None)
        chan = by_label.get(name)
        if chan is not None:
            for m in tr:
                if hasattr(m, 'channel'):
                    m.channel = chan
    mid.save(path)

def midi_report(path: str) -> str:
    import mido
    mid = mido.MidiFile(path)
    lines = [f'{path}: {mid.length:.1f}s ({mid.length/60:.2f} min), {len(mid.tracks)} tracks']
    for tr in mid.tracks:
        name = next((m.name for m in tr if m.type == 'track_name'), '?')
        notes = [m for m in tr if m.type == 'note_on' and m.velocity > 0]
        progs = sorted({m.program for m in tr if m.type == 'program_change'})
        chans = sorted({m.channel for m in tr if hasattr(m, 'channel')})
        if notes or progs:
            lo = min((m.note for m in notes), default=0)
            hi = max((m.note for m in notes), default=0)
            lines.append(f'  {name:18s} notes={len(notes):5d} range={lo}-{hi} prog={progs} ch={chans}')
    return '\n'.join(lines)

def check_ranges(orch: Orchestra) -> list[str]:
    problems = []
    for name, (label, _, _, lo, hi) in ROSTER.items():
        for n in orch.parts[name].recurse().notes:
            for p in (n.pitches if hasattr(n, 'pitches') else [n.pitch]):
                if not (lo <= p.midi <= hi):
                    problems.append(f'{label}: {p.nameWithOctave} (midi {p.midi}) outside {lo}-{hi}')
    return sorted(set(problems))
