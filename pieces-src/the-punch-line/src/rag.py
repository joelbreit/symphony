"""Ragtime idioms as code (docs/02) — the left hand's law, piece-local.

The stride engine writes the oom-pah from a chord chart: bass notes (roots
and fifths, octaves at arrivals) on the beats, dry close-voiced chords off
the beats, never syncopated. Stop-time, walking octaves, crushes, and the
octave-doubler live here too. Everything writes with swing=False — ragtime
is straight time, and the piece is written with swing=None anyway.

All durations in beats (quarter notes); one 2/4 bar = 2 beats.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from lib import dsl
from lib.chords import chord_at, fit, parse_chord, voicing
from lib.pitch import midi

PNO = 'piano'

# Register zones (docs/02 §3)
BASS_LO, BASS_HI = 'Ab1', 'Bb2'      # the "oom": roots and fifths
CHORD_LO, CHORD_HI = 'G3', 'G4'      # the "pah": dry close voicings

AB_MAJOR = {8, 10, 0, 1, 3, 5, 7}    # pitch classes of Ab major


def _bass_pitch(sym: str, near) -> int:
    _, bass_pc, _ = parse_chord(sym)
    return fit(bass_pc, BASS_LO, BASS_HI, near=near)


def _fifth_pitch(sym: str, near) -> int:
    root_pc, bass_pc, _ = parse_chord(sym)
    if bass_pc != root_pc:            # slash chord: honor the written bass
        return fit(bass_pc, BASS_LO, BASS_HI, near=near)
    return fit((root_pc + 7) % 12, BASS_LO, BASS_HI, near=near)


def stride(p, t0, chart, n_bars, vel=78, near='Ab2', oct_bass='arrivals',
           double=False, chord_lo=CHORD_LO, chord_hi=CHORD_HI):
    """The oom-pah over `chart`, one entry per bar ((a, b) splits a bar).

    oct_bass: True = octave basses throughout, 'arrivals' = octaves on
    phrase downbeats (every 4th bar), False = single notes. double=True
    adds a second bass octave below — the doctored roll's third hand.
    chord_lo/hi move the after-beat zone (the trio drops it a third so
    the sixths above stay clear). Returns the last bass pitch (chain it
    into the next call's `near`).
    """
    chord_vel = vel - 14
    for i in range(n_bars):
        bt = t0 + 2 * i
        sym1 = chord_at(chart, i)
        sym2 = chord_at(chart, i, half=1)
        b1 = _bass_pitch(sym1, near)
        b2 = _bass_pitch(sym2, b1) if sym2 != sym1 else _fifth_pitch(sym1, b1)
        big = oct_bass is True or (oct_bass == 'arrivals' and i % 4 == 0)
        for off, bp, v in ((0.0, b1, vel + 3), (1.0, b2, vel - 2)):
            pitches = [bp, bp + 12] if big else [bp]
            if double and bp - 12 >= midi('A0'):
                pitches = sorted({bp - 12, *pitches})
            p.add(PNO, bt + off, [(pitches, 0.5)], vel=v, gate=0.8,
                  swing=False)
        for off, sym, v in ((0.5, sym1, chord_vel), (1.5, sym2, chord_vel - 3)):
            p.add(PNO, bt + off, [(voicing(sym, chord_lo, chord_hi), 0.5)],
                  vel=v, gate=0.55, swing=False)
        near = b2
    return near


def stoptime(p, t0, chart, n_bars, vel=92):
    """Downbeat-only stabs — the grid stops, the silence does the work."""
    b = None
    for i in range(n_bars):
        sym = chord_at(chart, i)
        b = _bass_pitch(sym, b or 'Ab2')
        stack = sorted({b, b + 12, *voicing(sym, CHORD_LO, CHORD_HI)})
        p.add(PNO, t0 + 2 * i, [(stack, 0.5)], vel=vel, gate=0.5, swing=False)


def walk_oct(p, t0, pitches, vel=78, unit=0.5, vel_step=2):
    """Walking broken octaves in eighths — stride's seam-filler."""
    for i, name in enumerate(pitches):
        r = midi(name)
        p.add(PNO, t0 + i * unit, [([r, r + 12], unit)],
              vel=vel + vel_step * i, gate=0.85, swing=False)


def crush(p, t, pitch, vel):
    """Acciaccatura: a semitone crushed into a note starting at `t`.
    Write the main note yourself; this adds only the grace."""
    p.note(PNO, t - 0.09, midi(pitch) - 1, 0.09, vel=max(20, vel - 18),
           swing=False)


def octify(notes, shift=-12):
    """Double a melodic line at `shift` semitones (chords widen too)."""
    out = []
    for pch, d in dsl.events(notes):
        if pch is None:
            out.append((None, d))
        else:
            grp = pch if isinstance(pch, list) else [pch]
            out.append((sorted({*grp, *(x + shift for x in grp)}), d))
    return out


def scale_run(p, t0, lo, hi, vel=96, vel_end=112, unit=0.25, down=False):
    """Ab-major scale run between two pitches — the impossible register
    sweep of the doctored roll. Returns its end beat."""
    seq = [pp for pp in range(midi(lo), midi(hi) + 1) if pp % 12 in AB_MAJOR]
    if down:
        seq = seq[::-1]
    for i, pp in enumerate(seq):
        v = round(vel + (vel_end - vel) * i / max(1, len(seq) - 1))
        p.note(PNO, t0 + i * unit, pp, unit * 0.9, vel=v, swing=False)
    return t0 + len(seq) * unit


def roll_chord(p, t, pitches, dur, vel, spread=0.045):
    """Rolled chord, bottom-up, written as sounded notes."""
    for i, name in enumerate(sorted(midi(x) for x in pitches)):
        p.note(PNO, t + i * spread, name, max(0.1, dur - i * spread),
               vel=min(127, vel + i), swing=False)
