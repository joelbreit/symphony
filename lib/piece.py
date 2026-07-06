"""The Piece: an event store + timeline + roster, with fail-fast guards.

Authoring model (the best of all four lineages):
  - notes enter via the DSL or (pitch, dur) events at absolute beat offsets;
  - velocities are named dynamics with optional ramps (vel -> vel_end);
  - range violations raise at entry (the-unfinished-spire's discipline);
  - section marks / named cues are first-class and export to marks.json
    (the-box-is-full's web-manifest bridge);
  - CC curves (expression hairpins on held notes), sustain pedal, and pitch
    bends are first-class — the capability the music21 lineage never had.

Everything is deterministic: one seed in the constructor.
"""
import json
import random
from dataclasses import dataclass, replace as _dc_replace
from fractions import Fraction

from . import dsl
from .ensemble import DRUMS, Ensemble
from .pitch import pitch_name
from .timeline import Timeline

DYN = {
    'ppp': 28, 'pp': 36, 'p': 48, 'mp': 60,
    'mf': 72, 'f': 86, 'ff': 100, 'fff': 112,
}


def vel_of(v) -> int:
    return DYN[v] if isinstance(v, str) else int(v)


@dataclass
class Note:
    inst: str
    pitch: int
    start: float
    dur: float
    vel: int
    swing: bool = True

    def replace(self, **kw):
        return _dc_replace(self, **kw)


class Piece:
    def __init__(self, ensemble: Ensemble, seed: int = 1, title: str = ''):
        self.ensemble = ensemble
        self.title = title
        self.seed = seed
        self.rng = random.Random(seed)   # for compositional choices
        self.timeline = Timeline()
        self.notes: list[Note] = []
        self.ccs: list[tuple] = []       # (inst, beat, controller, value)
        self.bends: list[tuple] = []     # (inst, beat, raw -8192..8191)
        self.programs: list[tuple] = []  # (inst, beat, program)
        self.marks: list[tuple] = []     # (label, beat) section boundaries
        self.cues: dict[str, float] = {} # named instants

    # -- conductor -----------------------------------------------------
    def tempo(self, beat, bpm, text=None):
        self.timeline.tempo(beat, bpm, text)

    def meter(self, beat, num, den):
        self.timeline.meter(beat, num, den)

    def bar(self, bar: int, beat: float = 0.0) -> float:
        return self.timeline.bar(bar, beat)

    def seconds(self, beat) -> float:
        return self.timeline.seconds(beat)

    def mark(self, label: str, beat):
        self.marks.append((label, float(beat)))

    def cue(self, name: str, beat):
        self.cues[name] = float(beat)

    # -- notes -----------------------------------------------------------
    def add(self, inst: str, start, notes, vel='mf', vel_end=None,
            gate: float = 0.95, transpose: int = 0, accent_first: bool = False,
            swing: bool = True, check_range: bool = True) -> float:
        """Insert events at absolute beat `start`. Returns the end beat.

        notes: DSL string or [(pitch, dur), ...]. vel/vel_end: dynamic names
        or ints; vel_end ramps across the span. gate: fraction of each
        duration actually sounded (staccato ~0.5, legato 1.0).
        """
        spec = self.ensemble[inst]
        events = dsl.events(notes)
        if transpose:
            events = dsl.transpose(events, transpose)
        v0, v1 = vel_of(vel), vel_of(vel_end) if vel_end is not None else vel_of(vel)
        n_sounding = sum(1 for p, _ in events if p is not None)
        t = Fraction(start).limit_denominator(96)
        idx = 0
        for p, d in events:
            if p is not None:
                frac = idx / (n_sounding - 1) if n_sounding > 1 else 0.0
                v = round(v0 + (v1 - v0) * frac)
                if accent_first and idx == 0:
                    v += 8
                v = max(1, min(127, v))
                pitches = p if isinstance(p, list) else [p]
                for pp in pitches:
                    if check_range and not spec.percussion and not (spec.lo <= pp <= spec.hi):
                        raise ValueError(
                            f'{spec.name}: {pitch_name(pp)} (midi {pp}) at beat '
                            f'{float(t)} outside range {pitch_name(spec.lo)}-'
                            f'{pitch_name(spec.hi)}')
                    self.notes.append(Note(inst, pp, float(t),
                                           float(d * Fraction(gate).limit_denominator(20)),
                                           v, swing))
                idx += 1
            t += d
        return float(t)

    def note(self, inst, start, pitch, dur, vel='mf', **kw) -> float:
        return self.add(inst, start, [(pitch, dur)], vel=vel, **kw)

    def perc(self, start, pattern, vel='mf', inst=None, swing=True) -> float:
        """'kick:q r:e sn:e' with GM drum names, or [(key|midi, dur), ...]."""
        if inst is None:
            inst = next((i.key for i in self.ensemble if i.percussion), None)
            if inst is None:
                raise ValueError('ensemble has no percussion instrument')
        events = []
        if isinstance(pattern, str):
            for tok in pattern.split():
                k, d = tok.rsplit(':', 1)
                if k != 'r' and k not in DRUMS:
                    raise KeyError(f'unknown drum key {k!r} (see lib.ensemble.DRUMS)')
                events.append((None if k == 'r' else DRUMS[k], dsl._dur(d)))
        else:
            events = [(DRUMS[k] if isinstance(k, str) else k, d) for k, d in pattern]
        return self.add(inst, start, events, vel=vel, gate=1.0, swing=swing)

    # -- control -----------------------------------------------------------
    def program(self, inst: str, beat, program: int):
        """GM program switch mid-part (e.g. strings 45=pizzicato, 48=arco)."""
        self.programs.append((inst, float(beat), program))

    def cc(self, inst: str, beat, controller: int, value: int):
        self.ccs.append((inst, float(beat), controller, max(0, min(127, int(value)))))

    def hairpin(self, inst: str, t0, t1, v0: int, v1: int,
                controller: int = 11, step: float = 0.25):
        """CC curve from v0 to v1 across [t0, t1] — crescendo on held notes.

        Uses CC11 (expression) by default. NOTE: the value persists after t1;
        follow a decrescendo with a reset (cc(inst, t, 11, 110)) before the
        next passage, or start the next hairpin from where this one ended.
        """
        n = max(2, int(round((t1 - t0) / step)) + 1)
        for i in range(n):
            frac = i / (n - 1)
            self.cc(inst, t0 + (t1 - t0) * frac, controller,
                    round(v0 + (v1 - v0) * frac))

    def pedal(self, inst: str, t0, t1):
        """Sustain pedal (CC64) down at t0, up at t1."""
        self.cc(inst, t0, 64, 127)
        self.cc(inst, t1, 64, 0)

    def bend(self, inst: str, beat, semitones: float, bend_range: float = 2.0):
        """Pitch bend in semitones (synth bend range assumed +-2)."""
        raw = max(-8192, min(8191, int(semitones / bend_range * 8192)))
        self.bends.append((inst, float(beat), raw))

    # -- assembly -----------------------------------------------------------
    def end(self) -> float:
        return max((n.start + n.dur for n in self.notes), default=0.0)

    def marks_dict(self) -> dict:
        """The marks.json schema the web packaging uses (see PIECES.md)."""
        return {
            'sections': [[round(self.seconds(b), 2), label]
                         for label, b in sorted(self.marks, key=lambda m: m[1])],
            'cues': {k: round(self.seconds(v), 2) for k, v in self.cues.items()},
            'end': round(self.seconds(self.end()), 2),
        }

    def write_marks(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.marks_dict(), f, indent=1)
        return path

    def write(self, path: str, swing=None, humanize='default') -> str:
        """Write the MIDI file. swing: None or offbeat position (0.62 light,
        2/3 triplet). humanize: 'default', None, or a groove.Humanize."""
        from .midiwrite import write_midi
        return write_midi(self, path, swing=swing, humanize=humanize)
