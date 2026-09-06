#!/usr/bin/env python3
"""Engraved-score export for "High Street Riot".

    ../../.venv/bin/python export_score.py    (from pieces-src/high-street-riot/)

Writes web/public/pieces/high-street-riot/score.musicxml and adds
"score": "score.musicxml" to the movement entry in piece.json, so the web
player's score view can render the jam next to the piano roll.

READ-ONLY over the frozen music21 lineage. Importing src/compose.py runs its
module-level composition (that is how the piece is written: every section
appends events to compose.PARTS at import time) but never calls main(), so
humanize_and_swing(), build_score() -> MIDI and postprocess_midi() never touch
output/. The shipped MIDI is unchanged.

The symbolic layer this reads is therefore *pre-swing, pre-humanization*:
straight eighths, no velocity or onset jitter. Swing is a performance
transform in this piece (humanize_and_swing pushes offbeat 8ths +0.12 ql), so
the score correctly engraves straight eighths under a "heavy swing" direction,
the way a real Dixieland chart is written.

Cleanup applied for engraving (the source's numbers are MIDI-sounded values,
not notatable ones):

  - onsets snapped to the 32nd-note grid (1/8 ql). Only two things in the
    source are off that grid and both are performance detail, not rhythm:
    the banjo's 0.013-ql strum spread (snaps back into one chord) and the
    brass falloff's 0.11-ql chromatic spacing (becomes even 32nds).
  - durations snapped to the nearest notatable value (0.38 -> 1/2,
    0.95 -> 1, 1.9 -> 2, ...) and then clamped to the next onset in the part,
    so each staff stays single-voice — no MIDI gate/overlap artifacts.
  - simultaneous events in one part fold into a chord (banjo strums, unisons).
  - gaps filled with beat-aligned rests rather than one long rest per gap,
    so no measure sprouts a triple-dotted rest.
  - the unpitched percussion part (drum kit) is omitted; MIDI programs,
    channels and velocities are dropped (plain Instrument objects, concert
    pitch — this is a C score, matching the piano roll).
  - key signature (2 flats) and 4/4 kept on every staff; the three
    MetronomeMarks come from the frozen build_score() itself, so Verovio's
    timemap is driven by exactly the tempo map that rendered the audio.
  - section names go in as text directions on the top staff.
  - the stream is padded to a half-beat boundary before makeNotation, which
    keeps the last measure from sprouting monster-tuplet rests. (Here the
    music already ends on bar 124's barline, ql 496.)

Set SCORE_LANDMARKS=<path> to also dump landmark onsets (qstamp + seconds
from the tempo map) for the headless Verovio sync check.
"""
import json
import math
import os
import pathlib
import sys
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE / 'src'))

from lib import notation_m21 as N     # the shared music21 engraving bridge
from music21 import chord as m21chord
from music21 import clef, metadata, note, stream, tempo

import compose as C          # module-level import composes the piece into PARTS

PKG = ROOT / 'web' / 'public' / 'pieces' / 'high-street-riot'

# frozen-build fingerprint: event counts per part, straight from the source
EXPECTED_COUNTS = {'cornet': 307, 'clarinet': 309, 'sax': 176, 'bone1': 327,
                   'bone2': 247, 'sousa': 639, 'banjo': 1521, 'drums': 1562}
END_QL = Fraction(C.END - 1) * 4        # 124 bars

# top-to-bottom Dixieland score order (drums omitted: unpitched percussion)
ORDER = [('clarinet', clef.TrebleClef), ('cornet', clef.TrebleClef),
         ('sax', clef.TrebleClef), ('bone1', clef.BassClef),
         ('bone2', clef.BassClef), ('banjo', clef.TrebleClef),
         ('sousa', clef.BassClef)]

SECTIONS = [(C.SHRUG, 'the shrug'), (C.PILE1, 'the pile-on'),
            (C.SHOUT, 'the shout'), (C.WAIL, 'the wail — the anthem'),
            (C.FLOOR, 'the floor drop'), (C.BONESOLO, 'trombone lead'),
            (C.CORNSOLO, 'cornet lead'), (C.CLARSOLO, 'clarinet lead'),
            (C.ARGUE, 'the argument'), (C.STOMP, 'the stomp — stop-time'),
            (C.COLLAPSE, 'the collapse'), (C.RIOT, 'the riot'),
            (C.TAG, 'the wink')]

GRID = 8                                # onsets on the 32nd-note grid
# notatable written lengths. 5/4 and 3/8 are deliberately absent: the source's
# lengths are sounded ones (the riff head is 1.25, a banjo chunk 0.38), and
# keeping them would engrave the vamp as quarter-tied-to-32nd + 32nd rest and
# dotted-eighth chunks. Rounded to 1 and 1/2 they read as the chart they are.
DURS = [Fraction(n, d) for n, d in
        ((1, 8), (1, 4), (1, 2), (3, 4), (1, 1), (3, 2),
         (2, 1), (5, 2), (3, 1), (4, 1), (6, 1), (8, 1))]


def q_onset(x: float) -> Fraction:
    return Fraction(round(x * GRID), GRID)


def q_dur(x: float) -> Fraction:
    return min(DURS, key=lambda d: (abs(float(d) - x), d))


def fit(d: Fraction, gap: Fraction) -> Fraction:
    """Largest notatable duration that fits before the next onset."""
    if d <= gap:
        return d
    ok = [x for x in DURS if x <= gap]
    return max(ok) if ok else gap


REST_DURS = [Fraction(n, d) for n, d in
             ((4, 1), (2, 1), (1, 1), (1, 2), (1, 4), (1, 8))]


def rests(start: Fraction, end: Fraction):
    """Beat-aligned rests filling [start, end) — no multi-dotted monsters."""
    t = start
    while t < end:
        d = next((x for x in REST_DURS if t % x == 0 and t + x <= end),
                 Fraction(1, 8))
        yield t, d
        t += d


def midi_of(p):
    return p if isinstance(p, int) else C.m21.pitch.Pitch(p).midi


def engravable(events):
    """(onset, [pitch tokens], duration) — quantized, chorded, non-overlapping."""
    by_onset = {}
    for e in events:
        t = q_onset(e['off'])
        slot = by_onset.setdefault(t, {'dur': Fraction(0), 'pitches': {}})
        slot['dur'] = max(slot['dur'], q_dur(e['dur']))
        for p in e['pitches']:
            slot['pitches'].setdefault(midi_of(p), p)
    out = []
    onsets = sorted(by_onset)
    for i, t in enumerate(onsets):
        slot = by_onset[t]
        gap = (onsets[i + 1] if i + 1 < len(onsets) else END_QL) - t
        out.append((t, list(slot['pitches'].values()), fit(slot['dur'], gap)))
    return out


def build_staff(name, fixed_clef, events, window, conductor, dyn_source=None):
    """One chart staff: the shared frame, then this piece's own rests.

    Rests are written explicitly and beat-aligned rather than left to
    makeRests, which would fill a gap with a single triple-dotted monster.

    `dyn_source` is this part's raw slot list, which already carries `vel` —
    the riot never went through a recording Orchestra, so its dynamics are
    read straight off the chart it was written from.
    """
    p = N.staff(name, C.DISPLAY[name], fixed_clef,
                keys=[(0, 'g')], meters=[(0, '4/4')],
                tempi=conductor.get('tempi', ()),
                texts=conductor.get('texts', ()))
    placed = []
    cursor = Fraction(0)
    for t, pitches, d in events:
        for rt, rd in rests(cursor, t):
            r = note.Rest()
            r.duration.quarterLength = rd
            p.insert(rt, r)
        el = (note.Note(pitches[0]) if len(pitches) == 1
              else m21chord.Chord(sorted(pitches, key=midi_of)))
        el.duration.quarterLength = d
        p.insert(t, el)
        placed.append((float(t), el))
        cursor = t + d
    for rt, rd in rests(cursor, window):
        r = note.Rest()
        r.duration.quarterLength = rd
        p.insert(rt, r)
    if dyn_source:
        vels = [(float(sl['off']), int(sl['vel']),
                 max(midi_of(x) for x in sl['pitches']))
                for sl in dyn_source if sl.get('pitches')]
        marks, wedges = N.dynamics_for(vels, N.bars_from_meters([(0, '4/4')],
                                                                window))
        N.apply_dynamics(p, marks, wedges, placed)
    return N.finish(p, window, voices=False)


def tempi_from_frozen():
    """The MetronomeMarks the shipped MIDI was written with."""
    src = C.build_score()                    # in-memory only; nothing written
    marks = sorted((Fraction(mm.offset).limit_denominator(96), mm.number)
                   for mm in src.getElementsByClass(tempo.MetronomeMark))
    assert marks, 'no MetronomeMarks in the frozen score'
    return marks


def seconds_at(tempi, ql):
    """Wall-clock seconds of a quarterLength offset under the tempo map."""
    t, prev_off, prev_bpm = 0.0, 0.0, float(tempi[0][1])
    for off, bpm in tempi[1:]:
        off = float(off)
        if ql <= off:
            break
        t += (off - prev_off) * 60.0 / prev_bpm
        prev_off, prev_bpm = off, float(bpm)
    return t + (ql - prev_off) * 60.0 / prev_bpm


def main():
    counts = {k: len(v) for k, v in C.PARTS.items()}
    assert counts == EXPECTED_COUNTS, f'frozen build changed: {counts}'
    end = max(e['off'] + e['dur'] for v in C.PARTS.values() for e in v)
    assert end <= float(END_QL), f'music runs past bar {C.END - 1}: {end}'
    window = Fraction(math.ceil(float(END_QL) * 2), 2)   # half-beat tail guard

    tempi = tempi_from_frozen()
    conductor = {
        'tempi': tempi,
        'texts': [(Fraction(C.off(bar, 0)), text) for bar, text in SECTIONS],
    }

    sc = stream.Score()
    sc.metadata = metadata.Metadata(
        title='High Street Riot', movementName='High Street Riot',
        composer='Claude')

    staves, notes_out = 0, 0
    for i, (name, cl) in enumerate(ORDER):
        events = engravable(C.PARTS[name])
        if not events:                        # omit empty parts
            continue
        st = build_staff(name, cl, events, window,
                         conductor if i == 0 else {},   # conductor: top staff
                         dyn_source=C.PARTS[name])
        sc.insert(0, st)
        staves += 1
        notes_out += len(events)

    path = PKG / 'score.musicxml'
    sc.write('musicxml', fp=str(path))

    text = path.read_text()
    n_meas = len(sc.parts[0].getElementsByClass(stream.Measure))
    print(f'wrote {path}')
    print(f'  {staves} staves, {n_meas} measures, {notes_out} engraved events, '
          f'{path.stat().st_size / 1e6:.2f} MB, '
          f'{text.count("<time-modification>")} time-modifications')

    N.verify(path, lambda ql: seconds_at(tempi, ql))

    lm_path = os.environ.get('SCORE_LANDMARKS')
    if lm_path:
        probes = []
        for name in ('sousa', 'cornet', 'clarinet', 'bone1'):
            pool = [(t, midi_of(ps[0])) for t, ps, _ in engravable(C.PARTS[name])
                    if t.denominator == 1]
            span = float(pool[-1][0])
            for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
                q, midi = min(pool, key=lambda e: abs(float(e[0]) - frac * span))
                probes.append({'part': name, 'qstamp': float(q), 'midi': midi,
                               'sec': seconds_at(tempi, float(q))})
        pathlib.Path(lm_path).write_text(json.dumps(probes, indent=1))
        print('  landmarks ->', lm_path)

    N.register_score(PKG, {'mvt1': 'score.musicxml'})


if __name__ == '__main__':
    main()
