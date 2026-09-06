"""Engraving bridge for the frozen music21 pieces.

`lib.notation` engraves a `lib.Piece`, which carries a clean symbolic layer by
construction. The older music21 pieces (the-window, the-box-is-full,
high-street-riot) have no such layer: their generators write music21 streams
directly, and their scores have to be recovered by re-running the frozen
generator and recording what it *meant* before the MIDI write baked in gate,
velocity, and (in the riot's case) swing.

That recovery is per-lineage, but almost all of it turned out to be the same
code three times over. This module holds the shared half — the recording
Orchestra subclass, chord folding, the staff frame, the rest/voice/measure
finishing pass, the orchestral assembly loop, the manifest patch, and the
sync gate — leaving each piece's export_score.py to say only what is true of
that piece: its roster, clefs, keys, and whatever its own generator did that
notation has to undo.

Nothing here writes MIDI or touches a frozen generator; these pieces are
published and their audio is fixed.
"""
import json
import pathlib
from fractions import Fraction

from music21 import chord as m21chord
from music21 import clef as m21clef
from music21 import dynamics as m21dynamics
from music21 import expressions, instrument
from music21 import key as m21key
from music21 import layout, meter, note
from music21 import pitch as m21pitch
from music21 import stream, tempo as m21tempo

from .notation import check_sync

PIZZ_TEXT = {45: 'pizz.', 48: 'arco'}     # GM program switches, as directions

_pitch_cache: dict = {}


def P(p) -> m21pitch.Pitch:
    """Cached Pitch from a MIDI int or a name ('Eb5') — these exports build
    hundreds of thousands of them."""
    if p not in _pitch_cache:
        _pitch_cache[p] = (m21pitch.Pitch(midi=p) if isinstance(p, int)
                           else m21pitch.Pitch(p))
    return _pitch_cache[p]


def recorder(base, roster, as_events, transpose_events):
    """A recording subclass of a frozen `Orchestra`.

    Composing through it captures the platonic layer — exact quarterLength
    onsets and nominal durations, before gate and humanization — while the
    frozen movement/section code runs unchanged and still builds its normal
    streams. Each lineage passes its own base class and DSL helpers.

    rec[name]  : (onset Fraction, pitch tokens, nominal dur Fraction)
    vels[name] : (onset, velocity, top pitch) — the *platonic* velocity, the
        ramp without the humanizer's jitter, which is what a dynamic mark
        means. Computed here rather than read back, so the frozen code's RNG
        stream is not touched and its MIDI does not move.
    arco[name] : (onset, 'pizz.'|'arco') from program switches
    """

    class NotationOrchestra(base):
        def __init__(self):
            super().__init__()
            self.rec = {name: [] for name in roster}
            self.vels = {name: [] for name in roster}
            self.arco = {name: [] for name in roster}

        def add(self, name, offset, notes, vel='mf', gate: float = 0.95,
                vel_end=None, transpose: int = 0, accent_first: bool = False):
            events = as_events(notes)
            if transpose:
                events = transpose_events(events, transpose)
            t = Fraction(offset).limit_denominator(96)
            v0 = _vel_of(vel)
            v1 = _vel_of(vel_end) if vel_end is not None else v0
            n_sounding = sum(1 for p, _ in events if p is not None)
            idx = 0
            for p, d in events:
                d = Fraction(d).limit_denominator(96)
                if p is not None and name in self.rec:
                    toks = p if isinstance(p, list) else [p]
                    self.rec[name].append((t, toks, d))
                    frac = idx / (n_sounding - 1) if n_sounding > 1 else 0.0
                    v = round(v0 + (v1 - v0) * frac) + (
                        8 if accent_first and idx == 0 else 0)
                    self.vels[name].append(
                        (float(t), max(1, min(127, v)),
                         max(P(x).midi for x in toks)))
                if p is not None:
                    idx += 1
                t += d
            return super().add(name, offset, notes, vel=vel, gate=gate,
                               vel_end=vel_end, transpose=transpose,
                               accent_first=accent_first)

        def program(self, name, offset, prog):
            text = PIZZ_TEXT.get(prog)
            if text is not None and name in self.arco:
                self.arco[name].append(
                    (Fraction(offset).limit_denominator(96), text))
            super().program(name, offset, prog)

    return NotationOrchestra


_DYN_NAMES = {'ppp': 28, 'pp': 36, 'p': 48, 'mp': 60,
              'mf': 72, 'f': 86, 'ff': 100, 'fff': 112}


def _vel_of(v) -> int:
    return _DYN_NAMES[v] if isinstance(v, str) else int(v)


def bars_from_meters(meters, window: float) -> list:
    """Bar-line offsets from the conductor's meter map — meter changes and
    all, because a dynamic belongs on a downbeat."""
    out, segs = [], sorted((float(o), ts) for o, ts in meters)
    if not segs:
        return out
    for i, (o, ts) in enumerate(segs):
        num, den = (int(x) for x in ts.split('/'))
        bar_len = num * 4.0 / den
        end = segs[i + 1][0] if i + 1 < len(segs) else float(window)
        t = o
        while t < end - 1e-9 and len(out) < 100000:
            out.append(t)
            t += bar_len
    return out


def dynamics_for(vels, bars):
    """(marks, wedges) for one instrument — the same reader `lib.notation`
    uses on the symbolic layer, fed the recorded velocities."""
    from types import SimpleNamespace

    from .notation import _dynamic_plan
    notes = [SimpleNamespace(start=t, vel=v, pitch=p) for t, v, p in vels]
    return _dynamic_plan(notes, bars)


def merged_events(rec):
    """Fold same-(onset, duration) entries into one chord; dedupe by midi.

    Doubling written as separate add() calls (the same line handed to two
    desks) is one chord on the page, not two notes at one offset.
    """
    by, order = {}, []
    for t, tokens, d in rec:
        k = (t, d)
        if k not in by:
            by[k] = {}
            order.append(k)
        for tok in tokens:
            p = P(tok)
            by[k].setdefault(p.midi, p)
    return sorted(((t, list(by[(t, d)].values()), d) for t, d in order),
                  key=lambda e: (e[0], e[2]))


def conductor_from(part):
    """{'meters', 'tempi'} read off the very stream that drove the MIDI, so
    Verovio's timemap is the tempo map that rendered the audio."""
    meters = [(float(ts.getOffsetInHierarchy(part)), ts.ratioString)
              for ts in part.recurse().getElementsByClass(meter.TimeSignature)]
    tempi = sorted((float(mm.getOffsetInHierarchy(part)), mm.number, mm.text)
                   for mm in part.recurse().getElementsByClass(
                       m21tempo.MetronomeMark))
    return {'meters': meters, 'tempi': tempi}


def staff(part_id, part_name, clef_cls, *, keys=(), meters=(), tempi=(),
          texts=()):
    """An empty staff with all its furniture: instrument, clef, key and time
    signatures, tempo marks, text directions.

    Plain Instrument objects on purpose — no GM programs or channels reach
    the page, and everything is concert pitch (these are C scores, matching
    the piano roll). Part and instrument ids are pinned: music21 randomizes
    them otherwise, and a re-export that differs only in noise can't be read
    as a diff.
    """
    st = (stream.PartStaff(id=part_id) if part_id.endswith(('-rh', '-lh'))
          else stream.Part(id=part_id))
    st.partName = part_name
    inst = instrument.Instrument()
    inst.partName = part_name
    inst.instrumentName = part_name
    inst.partId = f'P-{part_id}'
    inst.instrumentId = f'I-{part_id}'
    st.insert(0, inst)
    st.insert(0, clef_cls())
    for off, ks in keys:
        st.insert(Fraction(off).limit_denominator(96),
                  m21key.KeySignature(m21key.Key(ks).sharps))
    for off, ts in meters:
        st.insert(off, meter.TimeSignature(ts))
    for entry in tempi:
        off, num, text = entry if len(entry) == 3 else (*entry, None)
        st.insert(off, m21tempo.MetronomeMark(number=num, text=text))
    for off, text in texts:
        te = expressions.TextExpression(text)
        te.style.fontStyle = 'italic'
        st.insert(off, te)
    return st


def add_events(st, events, placed=None):
    """Insert (onset, [Pitch], duration) triples as notes and chords.

    `placed`, if given, collects (offset, element) so hairpin spanners can be
    attached to the notes at each end of a ramp."""
    for t, pitches, d in events:
        el = (note.Note(pitches[0]) if len(pitches) == 1
              else m21chord.Chord(pitches))
        el.duration.quarterLength = d
        st.insert(t, el)
        if placed is not None:
            placed.append((float(t), el))
    return st


def apply_dynamics(st, marks, wedges, placed):
    """Print the dynamics: marks into the staff, hairpins onto the notes.

    Must run before `finish()` — makeNotation is what files everything into
    measures, and a Dynamic inserted afterwards lands outside them."""
    from .notation import _hang_wedges
    for off, name in marks:
        d = m21dynamics.Dynamic(name)
        d.placement = 'below'
        st.insert(float(off), d)
    _hang_wedges(st, placed, wedges)
    return st


from .notation import _join_secondary_beams        # noqa: E402  (shared rule)


def finish(st, window, *, voices=True, collapse_rest_voices=True):
    """Rests, measures, beams — and the voice renumbering that keeps the
    score in sync.

    music21 numbers voices from 0, MusicXML voices are 1-based, and Verovio
    drops a `<voice>0</voice>` layer wholesale: its notes land outside any
    layer and stretch the bar, so every affected measure plays back at twice
    its written length. That reads as the score drifting seconds away from
    the audio while looking perfectly normal on the page.

    `window` should be the music's end rounded up to a half beat, or
    makeNotation fabricates monster-tuplet rests to fill the tail.
    """
    if voices:
        st.makeVoices(inPlace=True)
    st.makeRests(refStreamOrTimeRange=[0.0, float(window)], fillGaps=True,
                 inPlace=True)
    out = st.makeNotation(inPlace=False)
    for m in out.getElementsByClass(stream.Measure):
        vs = list(m.voices)
        if collapse_rest_voices and len(vs) > 1:
            sounding = [v for v in vs if v.notes]
            keep = sounding or vs[:1]          # a silent bar keeps one voice
            for v in vs:
                if v not in keep:
                    m.remove(v)
            vs = keep
        for i, v in enumerate(vs):
            v.id = i + 1
    _join_secondary_beams(out)
    return out


def grand_split(events):
    """Split events into right/left hand at middle C (harp, piano)."""
    rh = [(t, [p for p in ps if p.midi >= 60], d) for t, ps, d in events]
    lh = [(t, [p for p in ps if p.midi < 60], d) for t, ps, d in events]
    return [e for e in rh if e[1]], [e for e in lh if e[1]]


def orchestral_score(sc, roster, o, *, clefs, window, conductor, keys,
                     grand_staff=('hp',), skip=(), collapse_rest_voices=True,
                     omit_empty=True, dyn=True, out=print):
    """Fill `sc` with one staff per roster entry, in roster order.

    Tempo marks and section texts go on the top staff only (Verovio reads
    them from there); meters go on every staff. Instruments in `grand_staff`
    get two braced staves split at middle C. Returns the staff count.

    `omit_empty` drops instruments that never play — right for a one-movement
    score, wrong for a symphony whose staff layout should stay put from
    movement to movement.
    """
    meters = conductor['meters']
    bars = bars_from_meters(meters, window) if dyn else []
    first, staves = True, 0
    for name, spec in roster.items():
        if name in skip:
            continue
        label = spec[0]
        events = merged_events(o.rec[name])
        if not events and omit_empty:
            out(f'  (empty part omitted: {label})')
            continue
        texts = []                       # drop no-op repeats (arco after arco)
        for off, txt in sorted(o.arco[name]):
            if not texts or texts[-1][1] != txt:
                texts.append((off, txt))
        top = dict(conductor) if first else {'meters': meters}
        if name in grand_staff:
            rh, lh = grand_split(events)
            built = []
            for suffix, cl, ev, cond, tx in (
                    ('rh', m21clef.TrebleClef, rh, top, texts),
                    ('lh', m21clef.BassClef, lh, {'meters': meters}, ())):
                st = staff(f'{name}-{suffix}', label, cl, keys=keys,
                           meters=cond['meters'], tempi=cond.get('tempi', ()),
                           texts=list(cond.get('texts', ())) + list(tx))
                placed = []
                add_events(st, ev, placed)
                if dyn and suffix == 'lh':   # between the staves, as piano goes
                    marks, wedges = dynamics_for(o.vels[name], bars)
                    apply_dynamics(st, marks, wedges, placed)
                built.append(finish(st, window,
                                    collapse_rest_voices=collapse_rest_voices))
            for st in built:
                sc.insert(0, st)
            sc.insert(0, layout.StaffGroup(built, symbol='brace',
                                           barTogether=True))
            staves += 2
        else:
            st = staff(name, label, clefs[name], keys=keys,
                       meters=meters, tempi=top.get('tempi', ()),
                       texts=list(top.get('texts', ())) + list(texts))
            placed = []
            add_events(st, events, placed)
            if dyn:
                marks, wedges = dynamics_for(o.vels[name], bars)
                apply_dynamics(st, marks, wedges, placed)
            sc.insert(0, finish(st, window,
                                collapse_rest_voices=collapse_rest_voices))
            staves += 1
        first = False
    return staves


def register_score(pkg, scores: dict, out=print):
    """Add "score" to the named movements in piece.json — a textual patch, so
    the rest of the hand-tuned file keeps its formatting. Idempotent."""
    manifest = pathlib.Path(pkg) / 'piece.json'
    text = manifest.read_text()
    have = {m['id']: m.get('score') for m in json.loads(text)['movements']}
    changed = []
    for mvt_id, filename in scores.items():
        if mvt_id not in have:
            raise AssertionError(f'no {mvt_id} movement in {manifest}')
        if have[mvt_id] == filename:
            continue                                   # already registered
        if have[mvt_id]:
            raise AssertionError(
                f'{mvt_id} already points at {have[mvt_id]!r}, not {filename!r}'
                ' — resolve by hand rather than guessing')
        needle = f'"notes": "notes/{mvt_id}.json",'
        line_start = text.rindex('\n', 0, text.index(needle)) + 1
        indent = text[line_start:text.index(needle)]
        at = text.index(needle) + len(needle)
        text = text[:at] + f'\n{indent}"score": "{filename}",' + text[at:]
        changed.append(mvt_id)
    if not changed:
        out('piece.json already registers every score — left unchanged')
        return
    json.loads(text)                                   # still valid JSON
    manifest.write_text(text)
    out(f'patched {manifest} (score on {", ".join(changed)})')


def verify(path, seconds, label='', max_drift=0.25, out=print):
    """Gate: the engraved score must reproduce the frozen tempo map.

    A notation bug does not look wrong on the page — it looks like the score
    sliding out of step with the audio, so this is the check that matters.
    """
    drift, at = check_sync(seconds, str(path))
    if drift is None:
        return None
    if drift > max_drift:
        raise AssertionError(
            f'{label or path}: engraved score drifts {drift:.2f}s from the '
            f'frozen tempo map at {at:.1f}s')
    out(f'  worst sync drift {drift * 1000:.0f} ms')
    return drift
