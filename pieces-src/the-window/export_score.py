"""Engraved-score export for 'The Window' — one MusicXML per movement.

    ../../.venv/bin/python export_score.py    (from pieces-src/the-window/)

Writes web/public/pieces/the-window/mvt{1..4}.musicxml and adds the
"score" field to each movement entry in piece.json so the web player
shows the score toggle (Player.tsx resolves it relative to the piece dir).

READ-ONLY over the frozen generator: this script never modifies
common.py / themes.py / mvt*.py behavior or the shipped MIDI. It composes
each movement in-process through a recording subclass of Orchestra that
captures the *pre-gate, pre-humanization* symbolic layer — exact
quarterLength onsets and nominal durations — the same
performance/notation split lib/notation.py makes for lib-built pieces.
(Humanization in common.py is velocity-only, so onsets need no cleanup;
gate only shortens the *sounded* duration, which belongs to the MIDI,
not the score.)

The engraving machinery itself lives in lib/notation_m21.py, shared with
the other two music21-lineage pieces; what stays here is what is true of
this symphony in particular — its roster, clefs, per-movement keys, and
the four-movement packaging.

Cleanup applied for engraving:
  - unpitched percussion part omitted (timpani kept);
  - notes doubled across add() calls at the same (onset, duration) are
    folded into one chord (per part); remaining overlaps become voices;
  - program-change artifacts (GM 45/48) are stripped; the pizz./arco
    intent they encode is kept as text directions at the switch offsets;
  - home key signatures added per movement (the source spells accidentals
    directly and carries no KeySignature objects); mvt4 changes to
    C major at the Answer (ql 368);
  - each part is padded with rests to the movement end rounded up to a
    half beat, so makeNotation never fabricates monster-tuplet tail rests;
  - voices are renumbered 1-based (Verovio drops "layer 0" wholesale, which
    doubles the affected measures) and voices holding nothing but rests are
    dropped — no notes are lost, only redundant stacked rests;
  - MetronomeMarks (same offsets/numbers/texts as the MIDI build) go into
    the top part, TimeSignatures into every part — Verovio's timemap is
    then driven by exactly the tempo map that generated the audio.

Tremolos/trills are sounded notes in the source and stay written out.

Also writes <scratchpad>/landmarks.json (if SCORE_LANDMARKS is set to a
path) with (qstamp, midi, seconds) probes per movement for the headless
Verovio sync check.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from lib import notation_m21 as N     # the shared music21 engraving bridge
from music21 import clef, metadata, stream

from common import ROSTER, Orchestra, _as_events, transpose_events
from export_web import MOVEMENTS, make_seconds, tempo_map

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PIECE_DIR = os.path.join(ROOT, 'web', 'public', 'pieces', 'the-window')

# staff order = ROSTER order (standard orchestral layout already)
CLEFS = {
    'fl': clef.TrebleClef, 'ob': clef.TrebleClef, 'cl': clef.TrebleClef,
    'bsn': clef.BassClef, 'hn': clef.TrebleClef, 'tpt': clef.TrebleClef,
    'tbn': clef.BassClef, 'timp': clef.BassClef, 'cel': clef.TrebleClef,
    'vln1': clef.TrebleClef, 'vln2': clef.TrebleClef, 'vla': clef.AltoClef,
    'vc': clef.BassClef, 'cb': clef.BassClef,
}
GRAND_STAFF = ('hp',)                  # two staves split at middle C

# home keys per movement; source streams carry no KeySignature objects
KEYS = {
    'mvt1': [(0, 'c')],
    'mvt2': [(0, 'g')],
    'mvt3': [(0, 'A-')],
    'mvt4': [(0, 'c'), (368, 'C')],    # C major from the Answer
}

NotationOrchestra = N.recorder(Orchestra, ROSTER, _as_events, transpose_events)


def export_movement(mv, landmarks_out=None):
    o = NotationOrchestra()
    end_ql = mv['mod'].compose(o, 0.0)
    # guard tail: half-beat window keeps makeNotation off monster tuplets
    window = math.ceil(float(end_ql) * 2) / 2

    # conductor events, from the same source objects that made the MIDI
    conductor = N.conductor_from(o.parts['vln1'])

    sc = stream.Score()
    sc.metadata = metadata.Metadata(
        title=f"The Window — {mv['num']}. {mv['title']}", composer='Claude')
    # omit_empty=False: a symphony keeps its staff layout across movements,
    # so the celesta stays on the page (resting) in the two it sits out
    staves = N.orchestral_score(sc, ROSTER, o, clefs=CLEFS, window=window,
                                conductor=conductor, keys=KEYS[mv['id']],
                                grand_staff=GRAND_STAFF, omit_empty=False)

    path = os.path.join(PIECE_DIR, f"{mv['id']}.musicxml")
    sc.write('musicxml', fp=path)

    # landmarks for the headless Verovio sync check: integer-ql note onsets
    if landmarks_out is not None:
        to_sec = make_seconds(tempo_map(o))
        probes = []
        pool = sorted((t, ps[0].midi) for nm in ('vln1', 'fl', 'vc', 'tpt')
                      for t, ps, d in N.merged_events(o.rec[nm])
                      if t.denominator == 1)
        if pool:
            span = float(pool[-1][0])
            for frac in (0.02, 0.2, 0.4, 0.6, 0.8, 0.98):
                q, midi = min(pool, key=lambda e: abs(float(e[0]) - frac * span))
                probes.append({'qstamp': float(q), 'midi': midi,
                               'sec': to_sec(float(q))})
        landmarks_out[mv['id']] = probes

    n_measures = len(sc.parts[0].getElementsByClass(stream.Measure))
    size = os.path.getsize(path)
    with open(path) as f:
        tmods = f.read().count('<time-modification>')
    print(f"{mv['id']}: {n_measures} measures, {staves} staves, "
          f"{size / 1e6:.2f} MB, {tmods} time-modifications -> {path}")
    N.verify(path, make_seconds(tempo_map(o)), label=mv['id'])
    return path


def main():
    landmarks = {}
    for mv in MOVEMENTS:
        export_movement(mv, landmarks)

    lm_path = os.environ.get('SCORE_LANDMARKS')
    if lm_path:
        with open(lm_path, 'w') as f:
            json.dump(landmarks, f, indent=1)
        print('wrote landmarks ->', lm_path)

    N.register_score(PIECE_DIR, {mv['id']: f"{mv['id']}.musicxml"
                                 for mv in MOVEMENTS})


if __name__ == '__main__':
    main()
