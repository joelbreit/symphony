"""Groove and humanization, applied at write time.

Swing is a piecewise-linear time warp (Royal Street Rattler's approach —
warps starts *and* ends, so durations breathe with the feel) rather than a
nudge of offbeat notes. Humanize gives each instrument family its own
timing looseness plus per-player lean (High Street Riot's approach), and
is driven by a seeded RNG so builds stay deterministic.
"""
import math
from dataclasses import dataclass, field


def swing_warp(t: float, amount: float = 0.62, unit: float = 1.0) -> float:
    """Warp time so each `unit`'s midpoint lands at `amount` of the unit.

    amount 0.5 = straight, 0.62 = light swing, 2/3 = triplet swing.
    Default unit=1.0 swings eighth notes within each quarter-note beat.
    """
    u = t / unit
    base = math.floor(u)
    frac = u - base
    if frac <= 0.5:
        w = frac * (amount / 0.5)
    else:
        w = amount + (frac - 0.5) * ((1.0 - amount) / 0.5)
    return (base + w) * unit


@dataclass
class Humanize:
    """Timing/velocity jitter profile. All times in beats."""
    timing: float = 0.015          # loose players (horns, strings, winds)
    tight_timing: float = 0.006    # rhythm section
    tight_families: tuple = ('perc', 'plucked', 'keys')
    vel: int = 3                   # +- velocity jitter
    lean: dict = field(default_factory=dict)     # inst key -> constant offset
    timing_overrides: dict = field(default_factory=dict)  # inst key -> jitter

    def jitter_for(self, inst) -> float:
        if inst.key in self.timing_overrides:
            return self.timing_overrides[inst.key]
        return self.tight_timing if inst.family in self.tight_families else self.timing


DEFAULT_HUMANIZE = Humanize()


def apply_groove(notes, ensemble, rng, swing=None, humanize=DEFAULT_HUMANIZE,
                 swing_unit: float = 1.0):
    """Return groove-adjusted copies of Note events (originals untouched)."""
    out = []
    for n in notes:
        start, dur = n.start, n.dur
        if swing is not None and n.swing:
            t1 = swing_warp(start + dur, swing, swing_unit)
            start = swing_warp(start, swing, swing_unit)
            dur = max(0.05, t1 - start)
        if humanize is not None:
            inst = ensemble[n.inst]
            jit = humanize.jitter_for(inst)
            start = max(0.0, start + humanize.lean.get(n.inst, 0.0)
                        + rng.uniform(-jit, jit))
            vel = max(1, min(127, n.vel + rng.randint(-humanize.vel, humanize.vel)))
        else:
            vel = n.vel
        out.append(n.replace(start=start, dur=dur, vel=vel))
    return out


def trim_overlaps(notes, channel_of, gap: float = 0.02, min_dur: float = 0.03):
    """Same-pitch overlaps on one channel are ambiguous MIDI (every lineage
    got bitten by this); trim the earlier note so each pair re-articulates.
    Mutates and returns `notes`."""
    by_key = {}
    for n in notes:
        by_key.setdefault((channel_of(n.inst), n.pitch), []).append(n)
    for seq in by_key.values():
        seq.sort(key=lambda n: n.start)
        for a, b in zip(seq, seq[1:]):
            if a.start + a.dur > b.start - gap:
                a.dur = max(min_dur, b.start - gap - a.start)
    return notes
