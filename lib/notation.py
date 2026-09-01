"""Notation export — clean engraved score from the *pre-humanized* symbolic
layer, for viewing while listening.

The MIDI written by lib.midiwrite is a rendering: swing, timing jitter, gate,
and velocity are baked in at write time. None of that belongs in a score, so
this module never looks at the MIDI. It reads the platonic layer the Piece
already holds — note starts, *nominal* durations (Note.nom, pre-gate), the
tempo/meter map, section marks — and rebuilds engraved rhythm from it.

The performance/notation split, made explicit:

  - **Ornament gestures are performance, not notation.** Mordents, latigos,
    smears write sub-`min_nom` notes at off-grid offsets; they are dropped
    (a future pass could render them as grace-note glyphs).
  - **Strums/rolls are chords.** Same-instrument notes staggered within
    `chord_tol` of an onset fold back into one chord at the first onset.
  - **DSL durations are trusted exactly.** A nominal that is a notatable
    value (denominator 1/2/4/8/3/6 in beats) is written as-is; a following
    written rest (`r:e` breaths) is thereby preserved.
  - **Ad-hoc float durations are shorthand.** A non-notatable nominal (0.3,
    0.225…) is a detached articulation: written as the full gap to the next
    onset when it covers most of it (repeated 0.3s every 0.5 → eighths),
    else snapped to the nearest plain value with rests filling the gap.

Pitch spelling: the DSL collapses names to MIDI ints at parse time, so ints
are re-spelled against a key (or a list of (beat, key) regions for pieces
that modulate) — scale degrees from the key, chromatic notes as the standard
alterations (raised 3/4/6/7 and flat 2 in minor; flat 3/6/7, raised 4, flat 2
in major).

Output is MusicXML; Verovio renders it (in-browser for the web player, or via
render_svg here). music21 does measures, rests, ties, and beams.
"""
import json
import math
import pathlib
from fractions import Fraction

from music21 import chord as m21chord
from music21 import clef, expressions, instrument
from music21 import key as m21key
from music21 import layout, metadata, meter, note, stream, tempo

_LETTER_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

# chromatic (non-scale) pitch-classes as alterations of scale degrees:
# (degree, alter) — minor raises 3/4/6/7 and flats 2; major flats 3/6/7,
# raises 4, and flats 2.
_ALTERATIONS = {
    'minor': [(2, -1), (3, +1), (4, +1), (6, +1), (7, +1)],
    'major': [(2, -1), (3, -1), (4, +1), (6, -1), (7, -1)],
}

# plain written values a performance-shorthand duration may snap to (beats)
_SNAP_DURS = [Fraction(1, 8), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4),
              Fraction(1), Fraction(3, 2), Fraction(2), Fraction(3),
              Fraction(4), Fraction(6), Fraction(8)]

_ONSET_GRID = Fraction(1, 24)     # sixteenths, triplets, and dots all land


def _spell_map(key: str) -> dict:
    """pitch-class -> (letter, alter) for spelling MIDI ints in `key`."""
    k = m21key.Key(key)
    scale = k.pitches[:-1]                     # 7 degrees
    out = {p.pitchClass: (p.step, int(p.alter or 0)) for p in scale}
    for deg, alt in _ALTERATIONS[k.mode]:
        base = scale[deg - 1]
        pc = (base.pitchClass + alt) % 12
        if pc not in out:
            out[pc] = (base.step, int(base.alter or 0) + alt)
    return out


def _spell(m: int, smap: dict) -> str:
    letter, alter = smap[m % 12]
    natural = m - alter                        # midi of the natural letter
    octave = natural // 12 - 1
    acc = '-' * -alter if alter < 0 else '#' * alter
    return f'{letter}{acc}{octave}'


def _key_regions(keys):
    """'a' or [(beat, 'a'), (144, 'c'), ...] -> sorted region list."""
    if isinstance(keys, str):
        return [(0.0, keys)]
    return sorted(((float(b), k) for b, k in keys), key=lambda r: r[0])


def _region_at(regions, beat):
    cur = regions[0][1]
    for b, k in regions:
        if b > beat:
            break
        cur = k
    return cur


def _notatable(f: Fraction) -> bool:
    """Written note values: plain/dotted binary and triplets (incl. tied
    composites music21 can split, e.g. 5/2). Excludes performance floats."""
    return f > 0 and f.denominator in (1, 2, 3, 4, 6, 8)


def _snap_dur(x: float) -> Fraction:
    return min(_SNAP_DURS, key=lambda v: abs(float(v) - x))


def _items(notes, min_nom: float, chord_tol: float):
    """Cluster one staff's notes into [(onset, [pitches], nom)] — ornaments
    dropped, strum staggers folded into chords at the cluster's first onset."""
    keep = sorted((n for n in notes if (n.nom or n.dur) >= min_nom),
                  key=lambda n: n.start)
    items = []
    for n in keep:
        if items and n.start - items[-1][0] <= chord_tol:
            _, pitches, nom = items[-1]
            if n.pitch not in pitches:
                pitches.append(n.pitch)
            items[-1][2] = max(nom, n.nom or n.dur)
        else:
            items.append([n.start, [n.pitch], n.nom or n.dur])
    # snap onsets to the grid after clustering (strum head = the true beat)
    out = []
    for start, pitches, nom in items:
        o = round(Fraction(start).limit_denominator(96) / _ONSET_GRID) * _ONSET_GRID
        if out and o == out[-1][0]:            # grid collision: merge
            for p in pitches:
                if p not in out[-1][1]:
                    out[-1][1].append(p)
            out[-1][2] = max(out[-1][2], nom)
        else:
            out.append([o, pitches, nom])
    return out


def _written(items, end: Fraction):
    """[(onset, pitches, written_dur)] — the trust/fill/snap rules."""
    out = []
    for i, (o, pitches, nom) in enumerate(items):
        gap = (items[i + 1][0] if i + 1 < len(items) else end) - o
        if gap <= 0:
            continue
        nf = Fraction(nom).limit_denominator(96)
        if _notatable(nf):
            wd = min(nf, gap)                  # trust the DSL value exactly
        elif nom >= 0.5 * float(gap) and float(gap) <= 2 * nom:
            wd = gap                           # detached shorthand: fill
        else:
            wd = min(_snap_dur(nom), gap)      # articulated: snap + rest
        if wd > 0:
            out.append((o, pitches, wd))
    return out


def _fill_staff(st, items, spell_at, window_len: float):
    """Insert written notes/chords into a music21 stream, pad with rests,
    and let makeNotation build measures/ties/beams."""
    for o, pitches, wd in items:
        names = [spell_at(p, o) for p in pitches]
        el = note.Note(names[0]) if len(names) == 1 else m21chord.Chord(names)
        el.quarterLength = wd
        st.insert(float(o), el)
    st.makeRests(refStreamOrTimeRange=[0.0, window_len], fillGaps=True,
                 inPlace=True)
    st.makeNotation(inPlace=True)
    # makeVoices() numbers voices from 0, and Verovio rejects "layer 0": the
    # orphaned notes then stretch their measure to twice its written length,
    # which reads as the score sliding seconds out of sync with the audio
    for m in st.getElementsByClass(stream.Measure):
        for i, v in enumerate(m.voices):
            v.id = i + 1


def to_score(piece, insts=None, keys=None, beat0=0.0, beat1=None, title=None,
             min_nom: float = 0.2, chord_tol: float = 0.12,
             grand_staff=None) -> stream.Score:
    """Build a clean music21 Score for `insts` over [beat0, beat1) beats.

    Everything defaults off the Piece itself, so a piece that declares its
    keys (`piece.key(beat, 'a')`) and a roster with `grand=True` on its
    keyboards needs no arguments at all:

    insts: instrument keys in staff order (top to bottom); default is roster
        order, which is already score order. Percussion is skipped.
    keys: one key string or [(beat, key), ...] regions for modulating pieces;
        default is the piece's declared key regions (C major if it declared
        none — a wrong key signature on the page is the symptom).
    grand_staff: instrument keys engraved on two staves split at middle C;
        default is every roster instrument marked `grand=True`.
    """
    if insts is None:
        insts = [i.key for i in piece.ensemble if not i.percussion]
    if keys is None:
        keys = getattr(piece, 'key_regions', lambda: [(0.0, 'C')])()
    if grand_staff is None:
        grand_staff = tuple(i.key for i in piece.ensemble if i.grand)
    if beat1 is None:
        beat1 = piece.end()
    # round the window up to a half-beat: a piece that cuts mid-gesture
    # otherwise leaves an unnotatable tail, which music21 pads with
    # monster-tuplet rests (80:59 256ths) whose numerals Verovio prints
    window = math.ceil(float(beat1 - beat0) * 2) / 2
    tl = piece.timeline
    regions = _key_regions(keys)
    smaps = {k: _spell_map(k) for _, k in regions}

    def spell_at(midi_pitch, rel_onset):
        k = _region_at(regions, beat0 + float(rel_onset))
        return _spell(midi_pitch, smaps[k])

    # conductor events within the window, as relative offsets
    key_marks = [(0.0, _region_at(regions, beat0))] + [
        (b - beat0, k) for b, k in regions if beat0 < b < beat1]
    meter_marks = [(0.0, _meter_at(tl, beat0))] + [
        (b - beat0, (n, d)) for b, n, d in tl.meters() if beat0 < b < beat1]
    tempo_marks = [(0.0, tl.bpm_at(beat0), None)] + [
        (b - beat0, bpm, text) for b, bpm, text in tl.tempi()
        if beat0 < b < beat1]

    sc = stream.Score()
    sc.metadata = metadata.Metadata(
        title=title or piece.title, composer='Claude')

    first = True
    for ikey in insts:
        spec = piece.ensemble[ikey]
        if spec.percussion:
            continue
        mine = [n for n in piece.notes
                if n.inst == ikey and beat0 <= n.start < beat1]
        staves = []                                # (stream, notes, fixed_clef)
        if ikey in grand_staff:
            rh = [n for n in mine if n.pitch >= 60]
            lh = [n for n in mine if n.pitch < 60]
            staves = [(stream.PartStaff(id=f'{ikey}-rh'), rh, clef.TrebleClef()),
                      (stream.PartStaff(id=f'{ikey}-lh'), lh, clef.BassClef())]
        else:
            staves = [(stream.Part(id=ikey), mine, None)]

        built = []
        for st, notes_, fixed_clef in staves:
            st.partName = spec.name
            inst = instrument.Instrument()
            inst.partName = spec.name
            # pin the ids: music21 invents random hashes otherwise, and a
            # re-export that differs only in noise defeats reading the diff
            inst.partId = f'P-{st.id}'
            inst.instrumentId = f'I-{st.id}'
            st.insert(0, inst)
            for off, (n, d) in meter_marks:
                st.insert(off, meter.TimeSignature(f'{n}/{d}'))
            for off, k in key_marks:
                st.insert(off, m21key.KeySignature(m21key.Key(k).sharps))
            if first:
                for off, bpm, text in tempo_marks:
                    st.insert(off, tempo.MetronomeMark(
                        number=round(bpm), text=text))
                for label, b in sorted(piece.marks, key=lambda m: m[1]):
                    if beat0 <= b < beat1:
                        st.insert(b - beat0, expressions.TextExpression(label))
                first = False
            shifted = [n.replace(start=n.start - beat0) for n in notes_]
            items = _written(_items(shifted, min_nom, chord_tol),
                             Fraction(window).limit_denominator(96))
            if fixed_clef is not None:
                st.insert(0, fixed_clef)
            elif items:
                lo = min(min(p for p in pitches) for _, pitches, _ in items)
                hi = max(max(p for p in pitches) for _, pitches, _ in items)
                st.insert(0, clef.BassClef() if (lo + hi) / 2 < 60
                          else clef.TrebleClef())
            _fill_staff(st, items, spell_at, window)
            built.append(st)

        for st in built:
            sc.insert(0, st)
        if len(built) == 2:
            sc.insert(0, layout.StaffGroup(built, symbol='brace',
                                           barTogether=True))
    return sc


def _meter_at(timeline, beat):
    num, den = timeline.meters()[0][1:]
    for b, n, d in timeline.meters():
        if b > beat:
            break
        num, den = n, d
    return num, den


def to_musicxml(piece, insts=None, path=None, **kw) -> str:
    """Write [beat0, beat1) as MusicXML. kw passed to to_score()."""
    sc = to_score(piece, insts, **kw)
    sc.write('musicxml', fp=path)
    return path


# ------------------------------------------------------------ packaging

def _package_dir(pkg) -> pathlib.Path:
    """A piece id ('perigee') or a path; ids resolve inside web/public."""
    p = pathlib.Path(pkg)
    if len(p.parts) == 1 and not p.exists():
        p = pathlib.Path(__file__).resolve().parents[1] / \
            'web' / 'public' / 'pieces' / pkg
    if not p.is_dir():
        raise FileNotFoundError(f'no such piece package: {p}')
    return p


def export(piece, pkg, movement=0, filename='score.musicxml',
           verify=True, max_drift=0.25, quiet=False, **kw) -> dict:
    """Engrave `piece` into a web piece package, in one call.

    Writes the MusicXML into the package, registers it on the movement in
    piece.json (which is what turns on the player's score toggle), and — the
    part worth having — checks the engraved rhythm back against the piece's
    own timeline before declaring success. A score that drifts is a score
    with a notation bug in it, and the drift is usually seconds, not
    milliseconds, so this catches it flatly.

    pkg: piece id ('perigee') or a path to the package directory.
    movement: index or movement id in piece.json.
    kw: passed through to to_score() (beat0/beat1 for one movement of many,
        min_nom, title, insts, keys, grand_staff...).

    Returns the report dict; raises if the drift gate fails.
    """
    pkg = _package_dir(pkg)
    path = pkg / filename
    to_musicxml(piece, path=str(path), **kw)
    report = {'path': str(path), 'kb': path.stat().st_size // 1024,
              'drift': None}

    manifest = pkg / 'piece.json'
    data = json.loads(manifest.read_text())
    movements = data['movements']
    mv = movements[movement] if isinstance(movement, int) else next(
        m for m in movements if m['id'] == movement)
    mv['score'] = filename
    manifest.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n')

    if verify:
        drift, at = check_sync(piece, str(path), beat0=kw.get('beat0', 0.0))
        report['drift'] = drift
        if drift is not None and drift > max_drift:
            raise ValueError(
                f'{path.name}: engraved score drifts {drift:.2f}s from the '
                f'piece timeline at {at:.1f}s — the score is not playable '
                f'against the audio. Usual causes: voices numbered from 0, '
                f'or a duration the notation rules mis-wrote.')
    if not quiet:
        d = report['drift']
        drift_txt = 'no verovio, unverified' if d is None else \
            f'worst sync drift {d * 1000:.0f} ms'
        print(f"wrote {path} ({report['kb']} KB, {drift_txt})")
        print(f"registered score on {mv['id']} in {manifest}")
    return report


def check_sync(clock, musicxml_path: str, beat0=0.0):
    """(worst drift in seconds, when) between the engraved score and the
    performance clock — the same comparison the web player makes at runtime,
    run headlessly here. (None, None) if verovio is unavailable.

    Verovio's timemap is what drives note highlighting in the player, so
    agreement here is agreement in the browser. `clock` is a Piece, or any
    seconds(beat) callable — the frozen music21 pieces have their own.
    """
    try:
        import verovio
    except ImportError:
        return None, None
    seconds = clock if callable(clock) else clock.seconds
    tk = verovio.toolkit()
    if not tk.loadFile(musicxml_path):
        raise ValueError(f'verovio could not parse {musicxml_path}')
    t0 = seconds(beat0)
    worst, at = 0.0, 0.0
    for e in tk.renderToTimemap({}):
        if not e.get('on'):
            continue
        expected = seconds(beat0 + e['qstamp']) - t0
        d = abs(e['tstamp'] / 1000.0 - expected)
        if d > worst:
            worst, at = d, expected
    return worst, at


def render_svg(musicxml_path: str, page=1, page_width=2100, scale=40) -> str:
    """MusicXML -> SVG string via Verovio (no browser, no external hosts)."""
    import verovio
    tk = verovio.toolkit()
    tk.setOptions({'pageWidth': page_width, 'scale': scale,
                   'adjustPageHeight': True, 'breaks': 'auto',
                   'footer': 'none', 'header': 'none'})
    tk.loadFile(musicxml_path)
    return tk.renderToSVG(page)
