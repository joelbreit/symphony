"""Engraved-score export for "The Box Is Full".

    ../../.venv/bin/python export_score.py    (from pieces-src/the-box-is-full/)

Writes web/public/pieces/the-box-is-full/score.musicxml and adds the "score"
field to the movement entry in piece.json so the web player shows the score
toggle (Player.tsx resolves it relative to the piece dir).

READ-ONLY over the frozen music21 lineage: nothing in compose/ changes and the
shipped MIDI is untouched. The piece is rebuilt in-process through a recording
subclass of Orchestra that captures the *pre-gate* symbolic layer — exact
quarterLength onsets and nominal (written) durations — the same
performance/notation split lib/notation.py makes for lib-built pieces.
Humanization in compose/common.py is velocity-only (RNG only ever perturbs
`v`), so onsets and durations need no de-jittering; `gate` shortens only the
*sounded* duration, which belongs to the MIDI, not to the page.

Cleanup applied for engraving:
  - the unpitched percussion part (drum kit + woodblock) is omitted; timpani,
    being pitched, is kept;
  - notes doubled across add() calls at the same (onset, duration) fold into
    one chord per staff; what still overlaps becomes voices;
  - GM program-change artifacts (45 pizz. / 48 arco) never reach the score;
    the intent they encode is kept as italic text at the switch offsets;
  - key signatures follow the game: G minor home, E-flat major for the rye
    field, then the climb's ratchets (A minor, B minor), D major for the
    TETRIS blaze, and G minor from the trapdoor to the end (the source spells
    accidentals directly and carries no KeySignature objects);
  - MetronomeMarks and TimeSignatures come from the very objects that drove
    the MIDI build — tempi on the top staff (Verovio reads them from there),
    meters on every staff — so the timemap matches the rendered audio;
  - section marks that no tempo text already announces become text directions;
  - voices are renumbered 1-based (music21 counts them from 0, and Verovio
    drops "layer 0" entirely — which silently doubles every affected measure's
    playback length) and rest-only extra voices are dropped;
  - part/instrument ids are fixed strings, so the export is byte-deterministic
    (music21 randomizes them otherwise);
  - every staff is padded with rests to the end rounded up to a half beat, so
    makeNotation never fabricates monster-tuplet tail rests;
  - the harp is engraved on a grand staff split at middle C.

Tremolos are sounded notes in the source and stay written out.

With SCORE_LANDMARKS=<path> set, also dumps (qstamp, midi, seconds) probes for
the headless Verovio sync check.
"""
import json
import math
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE / 'compose'))

from lib import notation_m21 as N     # the shared music21 engraving bridge
from music21 import clef, metadata, stream

from common import ROSTER, Orchestra, _as_events, transpose_events
import box

PKG = ROOT / 'web' / 'public' / 'pieces' / 'the-box-is-full'

SECTIONS = (box.s0_insert_cartridge, box.s1_strut, box.s2_sweat,
            box.s3_rye_field, box.s4_climb, box.s5_tetris,
            box.s6_bottom_drops, box.s7_kill_screen, box.s8_score_screen)

# staff order = ROSTER order (already a standard orchestral layout)
CLEFS = {
    'fl': clef.TrebleClef, 'ob': clef.TrebleClef, 'cl': clef.TrebleClef,
    'bsn': clef.BassClef, 'hn': clef.TrebleClef, 'tpt': clef.TrebleClef,
    'tbn': clef.BassClef, 'timp': clef.BassClef, 'sq': clef.TrebleClef,
    'vln1': clef.TrebleClef, 'vln2': clef.TrebleClef, 'vla': clef.AltoClef,
    'vc': clef.BassClef, 'cb': clef.BassClef,
}
GRAND_STAFF = ('hp',)                  # two staves split at middle C
SKIP = ('perc',)                       # unpitched percussion: not engraved

NotationOrchestra = N.recorder(Orchestra, ROSTER, _as_events, transpose_events)


def build_written():
    """Rebuild the piece, recording the written layer. Emits no MIDI."""
    o = NotationOrchestra()
    t = 0.0
    for section in SECTIONS:
        t = section(o, t)
    return o, t


def seconds_fn(tempos):
    """Exact quarterLength -> seconds over the piece's tempo map."""
    ts = sorted(tempos)
    assert ts and ts[0][0] == 0.0, 'expected a tempo mark at offset 0'

    def to_sec(q: float) -> float:
        sec = 0.0
        for i, (off, bpm) in enumerate(ts):
            nxt = ts[i + 1][0] if i + 1 < len(ts) else float('inf')
            if q <= off:
                break
            sec += (min(q, nxt) - off) * 60.0 / bpm
        return sec
    return to_sec


def key_regions(o):
    """(offset, key name) for the piece's key areas, from its marks/cues."""
    marks = {label: off for label, off in o.marks}
    return [
        (0.0, 'g'),
        (marks['the rye field (music B)'], 'E-'),
        (marks['the climb — levels 5 · 6 · 7'], 'g'),
        (o.cues['level6'], 'a'),
        (o.cues['level7'], 'b'),
        (o.cues['tetris'], 'D'),
        (marks['the bottom drops'], 'g'),
    ]


def export(o, end_ql, landmarks_out=None):
    # guard tail: a half-beat window keeps makeNotation off monster tuplets
    window = math.ceil(float(end_ql) * 2) / 2

    # the frozen lineage parks the conductor events on vln1
    conductor = N.conductor_from(o.parts['vln1'])
    # section marks that no tempo text already announces
    spoken = {off for off, _, text in conductor['tempi'] if text}
    conductor['texts'] = [
        (off, label) for label, off in sorted(o.marks, key=lambda m: m[1])
        if off not in spoken]

    sc = stream.Score()
    sc.metadata = metadata.Metadata(
        title='The Box Is Full — one game', composer='Claude')
    staves = N.orchestral_score(sc, ROSTER, o, clefs=CLEFS, window=window,
                                conductor=conductor, keys=key_regions(o),
                                grand_staff=GRAND_STAFF, skip=SKIP)

    path = PKG / 'score.musicxml'
    sc.write('musicxml', fp=str(path))

    # landmarks for the headless Verovio sync check: integer-ql onsets spread
    # across the piece, with the seconds the audio's tempo map puts them at
    if landmarks_out is not None:
        to_sec = seconds_fn(o.tempos)
        pool = sorted({(t, ps[0].midi)
                       for nm in ('vln1', 'sq', 'vc', 'tpt', 'fl')
                       for t, ps, d in N.merged_events(o.rec[nm])
                       if t.denominator == 1})
        span = float(pool[-1][0])
        for frac in (0.02, 0.2, 0.4, 0.6, 0.8, 0.98):
            q, midi = min(pool, key=lambda e: abs(float(e[0]) - frac * span))
            landmarks_out.append({'qstamp': float(q), 'midi': midi,
                                  'sec': to_sec(float(q))})

    n_measures = len(sc.parts[0].getElementsByClass(stream.Measure))
    size = path.stat().st_size
    tmods = path.read_text().count('<time-modification>')
    print(f'wrote {path}\n  {n_measures} measures, {staves} staves, '
          f'{size / 1e6:.2f} MB, {tmods} time-modifications, '
          f'window {window} ql (end {float(end_ql)})')

    N.verify(path, seconds_fn(o.tempos))
    return path


def main():
    o, end_ql = build_written()
    landmarks = [] if os.environ.get('SCORE_LANDMARKS') else None
    export(o, end_ql, landmarks)
    if landmarks is not None:
        with open(os.environ['SCORE_LANDMARKS'], 'w') as f:
            json.dump(landmarks, f, indent=1)
        print('wrote landmarks ->', os.environ['SCORE_LANDMARKS'])
    N.register_score(PKG, {'mvt1': 'score.musicxml'})


if __name__ == '__main__':
    main()
