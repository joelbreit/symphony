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
import re
from fractions import Fraction

from music21 import chord as m21chord
from music21 import clef, dynamics, expressions, instrument
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


# Velocity is the dynamic in this system (a piano cannot crescendo a struck
# note, so `lib` writes loudness as velocity and the page has to read it back
# out). Band edges are the midpoints between lib.piece.DYN's values.
_DYN_BANDS = ((32, 'ppp'), (42, 'pp'), (54, 'p'), (66, 'mp'),
              (79, 'mf'), (93, 'f'), (106, 'ff'), (128, 'fff'))


def _band(v: float) -> str:
    for hi, name in _DYN_BANDS:
        if v < hi:
            return name
    return 'fff'


def _effective_vel(n) -> float:
    """Velocity corrected for register, because velocity is a keystroke and
    a dynamic is a loudness.

    The same force at the top of a keyboard produces far less sound than in
    the middle — which is why a composer writing for a sampler ends up pushing
    the top octave hard to make it speak at all. Read back literally, that
    reads as `mf` on a page where the composer meant a distant ping. The
    correction is one band at the very top and nothing elsewhere: low notes
    carry perfectly well on their own.
    """
    if n.pitch > 84:                       # above C6
        return n.vel - 12 * min(1.0, (n.pitch - 84) / 21.0)
    return n.vel


def _smooth(series, w: int = 3) -> list:
    """Centred median over w bars, skipping empty ones — kills the flicker of
    a median sitting on a band edge without moving any real change."""
    out = []
    for i in range(len(series)):
        vals = [v for v in series[max(0, i - w // 2): i + w // 2 + 1]
                if v is not None]
        out.append(sorted(vals)[len(vals) // 2] if vals else None)
    return out


def _bar_offsets(timeline, beat0: float, beat1: float) -> list:
    """Relative offsets of every bar line inside the window, meter-aware."""
    out, n = [], 1
    while n < 100000:
        b = timeline.bar_start(n)
        if b >= beat1:
            break
        if b >= beat0:
            out.append(b - beat0)
        n += 1
    return out


def _dynamic_plan(notes_rel, bars, min_gap: int = 4, ramp_bars: int = 3,
                  ramp_span: int = 9, max_wedge_bars: int = 8):
    """(marks, wedges) for one instrument, from its velocities.

    marks: [(offset, 'mf'), ...] — a band change that has held long enough to
    be worth printing. wedges: [(offset0, offset1, 'cresc'|'dim'), ...] where
    the velocity moved monotonically far enough across enough bars to be a
    hairpin rather than a step. A ramp longer than `max_wedge_bars` keeps its
    arrival and loses its tail: a hairpin drawn across a whole system reads as
    an underline, and the last eight bars are where the growth is heard.

    Per-bar velocity is the *median* of the notes starting in that bar, not
    the mean: an accompaniment of forty quiet sixteenths under four loud
    melody notes is quiet, and the mean says otherwise.
    """
    if not bars or not notes_rel:
        return [], []
    edges = list(bars) + [float('inf')]
    per_bar, k = [], 0
    ns = sorted(notes_rel, key=lambda n: n.start)
    for i in range(len(bars)):
        lo, hi = edges[i], edges[i + 1]
        vs = []
        while k < len(ns) and ns[k].start < lo:
            k += 1
        j = k
        while j < len(ns) and ns[j].start < hi:
            vs.append(_effective_vel(ns[j]))
            j += 1
        per_bar.append(sorted(vs)[len(vs) // 2] if vs else None)
    per_bar = _smooth(per_bar)

    marks, wedges = [], []
    last_band, last_i = None, -min_gap
    run_start, prev_i = None, None
    for i, v in enumerate(per_bar):
        if v is None:
            continue
        # a hairpin is a monotonic run of bar medians, wide enough to matter;
        # when the direction turns, the run restarts at the turn
        if run_start is None or prev_i is None:
            run_start = i
        elif (v - per_bar[prev_i]) * (per_bar[prev_i] - per_bar[run_start]) < 0:
            run_start = prev_i
        prev_i = i
        band = _band(v)
        # a band has to hold to be worth printing: one bar dipping over an
        # edge is not a dynamic, it is a note
        nxt = next((per_bar[j] for j in range(i + 1, len(per_bar))
                    if per_bar[j] is not None), None)
        if band != last_band and nxt is not None and _band(nxt) != band:
            continue
        if band != last_band and i - last_i >= min_gap:
            if (run_start is not None and i - run_start >= ramp_bars
                    and abs(v - per_bar[run_start]) >= ramp_span):
                w0 = max(run_start, i - max_wedge_bars)
                wedges.append((bars[w0], bars[i],
                               'cresc' if v > per_bar[run_start] else 'dim'))
            marks.append((bars[i], band))
            last_band, last_i, run_start = band, i, i
    return marks, wedges


def _beam_groups(notes):
    """Runs of notes joined by a primary (level-1) beam."""
    group = []
    for el in notes:
        bl = getattr(el, 'beams', None)
        b = None
        if bl is not None and bl.beamsList:
            b = next((x for x in bl.beamsList if x.number == 1), None)
        kind = b.type if b is not None else None
        if kind == 'start':
            group = [el]
        elif kind in ('continue', 'stop') and group:
            group.append(el)
            if kind == 'stop':
                yield group
                group = []
        else:
            group = []


def _join_secondary_beams(st):
    """Four sixteenths in one beat are one double beam, not two pairs.

    music21 breaks the *secondary* beams of a group at the eighth-note
    subdivision — the primary beam runs the whole beat, the 16th beam stops
    and restarts halfway — which engraves as two pairs of two and is what a
    reader sees first. Modern practice beams the beat solid, so within each
    primary group every deeper beam is made continuous wherever both
    neighbours carry that level. Where they do not (a genuine eighth in the
    middle of sixteenths), the break stays: it is real there.

    Only groups no longer than one beat are touched. A beam that spans two
    beats *should* break its secondary at the beat, and music21 gets that
    case right.
    """
    from music21 import meter as m21meter
    fixed = 0
    for m in st.getElementsByClass(stream.Measure):
        ts = m.timeSignature or next(
            iter(st.getElementsByClass(m21meter.TimeSignature)), None)
        beat = float(ts.beatDuration.quarterLength) if ts is not None else 1.0
        for holder in (list(m.voices) or [m]):
            for group in _beam_groups(holder.notes):
                span = sum(float(el.duration.quarterLength) for el in group)
                if span > beat + 1e-6:
                    continue
                levels = [max((b.number for b in el.beams.beamsList), default=0)
                          for el in group]
                for k in range(2, max(levels, default=0) + 1):
                    has = [lv >= k for lv in levels]
                    for i, el in enumerate(group):
                        if not has[i]:
                            continue
                        prev = i > 0 and has[i - 1]
                        nxt = i < len(group) - 1 and has[i + 1]
                        if prev and nxt:
                            want, direction = 'continue', None
                        elif nxt:
                            want, direction = 'start', None
                        elif prev:
                            want, direction = 'stop', None
                        else:
                            want = 'partial'
                            direction = 'right' if i == 0 else 'left'
                        b = next(x for x in el.beams.beamsList if x.number == k)
                        if b.type != want or b.direction != direction:
                            b.type, b.direction = want, direction
                            fixed += 1
    return fixed


def _fill_staff(st, items, spell_at, window_len: float):
    """Insert written notes/chords into a music21 stream, pad with rests,
    and let makeNotation build measures/ties/beams."""
    placed = []
    for o, pitches, wd in items:
        names = [spell_at(p, o) for p in pitches]
        el = note.Note(names[0]) if len(names) == 1 else m21chord.Chord(names)
        el.quarterLength = wd
        st.insert(float(o), el)
        placed.append((float(o), el))
    st.makeRests(refStreamOrTimeRange=[0.0, window_len], fillGaps=True,
                 inPlace=True)
    st.makeNotation(inPlace=True)
    # makeVoices() numbers voices from 0, and Verovio rejects "layer 0": the
    # orphaned notes then stretch their measure to twice its written length,
    # which reads as the score sliding seconds out of sync with the audio
    for m in st.getElementsByClass(stream.Measure):
        for i, v in enumerate(m.voices):
            v.id = i + 1
    _join_secondary_beams(st)
    return placed


def to_score(piece, insts=None, keys=None, beat0=0.0, beat1=None, title=None,
             composer='Claude', min_nom: float = 0.2, chord_tol: float = 0.12,
             grand_staff=None, dyn: bool = True) -> stream.Score:
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
    dyn: print dynamics and hairpins, read back out of the velocities. On a
        grand staff they go on the lower staff, which is where Verovio puts
        them between the two — the piano convention.
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
        title=title or piece.title, composer=composer)

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

        marks, wedges = _dynamic_plan(
            [n.replace(start=n.start - beat0) for n in mine],
            _bar_offsets(tl, beat0, beat1)) if dyn else ([], [])

        built = []
        for si, (st, notes_, fixed_clef) in enumerate(staves):
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
            # one instrument, one set of dynamics: the lower staff of a grand
            # staff carries them, everything else carries its own
            if dyn and si == len(staves) - 1:
                for off, name in marks:
                    d = dynamics.Dynamic(name)
                    d.placement = 'below'
                    st.insert(float(off), d)
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
            placed = _fill_staff(st, items, spell_at, window)
            if dyn and si == len(staves) - 1:
                _hang_wedges(st, placed, wedges)
            built.append(st)

        for st in built:
            sc.insert(0, st)
        if len(built) == 2:
            sc.insert(0, layout.StaffGroup(built, symbol='brace',
                                           barTogether=True))
    return sc


def _hang_wedges(st, placed, wedges):
    """Attach hairpin spanners to the real notes at each end of a ramp.

    A wedge with no note under one of its ends is dropped rather than
    guessed at: a hairpin that starts in a rest is worse than no hairpin.
    """
    if not placed:
        return
    # sort by offset only: two elements can share one, and music21 objects
    # are not orderable against each other
    placed = sorted(placed, key=lambda x: x[0])
    offs = [o for o, _ in placed]
    for o0, o1, kind in wedges:
        a = next((el for o, el in placed if o >= o0 - 1e-9), None)
        b = next((el for o, el in reversed(placed) if o <= o1 + 1e-9), None)
        if a is None or b is None or a is b or offs[0] > o1 or offs[-1] < o0:
            continue
        sp = dynamics.Crescendo() if kind == 'cresc' else dynamics.Diminuendo()
        sp.addSpannedElements([a, b])
        sp.placement = 'below'
        st.insert(0, sp)


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
    beat0 = float(kw.get('beat0') or 0.0)
    beat1 = float(kw.get('beat1') or piece.end())
    tl = piece.timeline
    _restore_exact_tempi([tl.bpm_at(beat0)] + [bpm for b, bpm, _ in tl.tempi()
                                              if beat0 < b < beat1], path)
    return path


def _restore_exact_tempi(bpms, path) -> int:
    """Put the un-rounded tempi back into the written MusicXML.

    music21 exports `<per-minute>` and `<sound tempo="...">` as whole numbers.
    For the usual integer tempo that is invisible; for a piece whose tempo is
    set by something in the world — 134.5996 bpm, one 3/4 bar per rotation of
    a pulsar — the rounding is a *drift*, and it grows without bound: about a
    second lost over five minutes, which is a second of the score highlighting
    the wrong bar. So rewrite both, in document order, from the marks the
    score actually carries. `<sound>` drives playback and the timemap and gets
    full precision; `<per-minute>` is what a reader sees and gets one decimal.
    """
    if path is None:
        return 0
    marks = [float(b) for b in bpms]
    if not marks or all(b.is_integer() for b in marks):
        return 0
    p = pathlib.Path(path)
    text = p.read_text()

    def rewrite(txt, pattern, fmt):
        seen = [0]

        def one(m):
            v = marks[min(seen[0], len(marks) - 1)]
            seen[0] += 1
            whole = m.group(0)
            a = m.start(1) - m.start(0)
            b = m.end(1) - m.start(0)
            return whole[:a] + fmt(v) + whole[b:]
        return re.sub(pattern, one, txt)

    text = rewrite(text, r'<per-minute>([0-9.]+)</per-minute>',
                   lambda v: f'{v:g}' if float(v).is_integer() else f'{v:.1f}')
    text = rewrite(text, r'<sound tempo="([0-9.]+)"', lambda v: f'{v:.4f}')
    p.write_text(text)
    return len(marks)


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
