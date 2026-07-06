"""Direct MIDI writer (mido) — no music21 score container.

Both music21 lineages ended up post-processing their MIDI with mido anyway
(channel remaps, CC injection, trombone splitting); writing directly makes
those hacks unnecessary and unlocks CCs and pitch bends as first-class
events. Format 1: track 0 is the conductor (tempo, meter, section markers),
then one track per instrument, named with the instrument's display name —
which is exactly what tools/midi_to_piece.py keys packages on.
"""
import mido

from .groove import DEFAULT_HUMANIZE, apply_groove, trim_overlaps

TPQ = 480

_META_SUBS = str.maketrans({'—': '-', '–': '-', '’': "'", '‘': "'",
                            '“': '"', '”': '"', '…': '...'})


def _meta_str(s: str) -> str:
    """MIDI meta text is latin-1 (mido raises on em-dashes etc.) — sanitize."""
    return s.translate(_META_SUBS).encode('latin-1', 'replace').decode('latin-1')


def write_midi(piece, path: str, swing=None, humanize='default') -> str:
    if humanize == 'default':
        humanize = DEFAULT_HUMANIZE
    ens = piece.ensemble
    # groove/humanize on copies, with a write-local RNG so writing twice
    # (or writing after more composing) is still byte-deterministic
    import random
    rng = random.Random(piece.seed ^ 0x5EED)
    notes = apply_groove(piece.notes, ens, rng, swing=swing, humanize=humanize)
    trim_overlaps(notes, channel_of=lambda k: ens.channels[k])

    mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)

    def ticks(beat: float) -> int:
        from .groove import swing_warp
        if swing is not None:
            beat = swing_warp(beat, swing)
        return max(0, round(beat * TPQ))

    # -- conductor track --------------------------------------------------
    cond = mido.MidiTrack()
    events = [(0, 0, mido.MetaMessage('track_name',
                                      name=_meta_str(piece.title or 'conductor'), time=0))]
    for beat, bpm, _text in piece.timeline.tempi():
        events.append((round(beat * TPQ), 1,
                       mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0)))
    for beat, num, den in piece.timeline.meters():
        events.append((round(beat * TPQ), 1,
                       mido.MetaMessage('time_signature', numerator=num,
                                        denominator=den, time=0)))
    for label, beat in piece.marks:
        events.append((round(beat * TPQ), 2,
                       mido.MetaMessage('marker', text=_meta_str(label), time=0)))
    _append_deltas(cond, events)
    mid.tracks.append(cond)

    # -- one track per instrument, in roster order --------------------------
    by_inst = {}
    for n in notes:
        by_inst.setdefault(n.inst, []).append(n)
    ccs_by, bends_by, progs_by = {}, {}, {}
    for inst, beat, ctrl, val in piece.ccs:
        ccs_by.setdefault(inst, []).append((beat, ctrl, val))
    for inst, beat, raw in piece.bends:
        bends_by.setdefault(inst, []).append((beat, raw))
    for inst, beat, prog in piece.programs:
        progs_by.setdefault(inst, []).append((beat, prog))

    for spec in ens:
        key = spec.key
        if not (by_inst.get(key) or ccs_by.get(key) or bends_by.get(key)):
            continue
        ch = ens.channels[key]
        tr = mido.MidiTrack()
        events = [(0, 0, mido.MetaMessage('track_name', name=_meta_str(spec.name),
                                          time=0))]
        if not spec.percussion:
            events.append((0, 1, mido.Message('program_change', channel=ch,
                                              program=spec.program, time=0)))
        events.append((0, 2, mido.Message('control_change', channel=ch,
                                          control=7, value=spec.volume, time=0)))
        events.append((0, 2, mido.Message('control_change', channel=ch,
                                          control=10, value=spec.pan, time=0)))
        events.append((0, 2, mido.Message('control_change', channel=ch,
                                          control=91, value=ens.reverb, time=0)))
        for beat, prog in progs_by.get(key, []):
            events.append((ticks(beat), 3, mido.Message('program_change', channel=ch,
                                                        program=prog, time=0)))
        for beat, ctrl, val in ccs_by.get(key, []):
            events.append((ticks(beat), 3, mido.Message('control_change', channel=ch,
                                                        control=ctrl, value=val, time=0)))
        for beat, raw in bends_by.get(key, []):
            events.append((ticks(beat), 3, mido.Message('pitchwheel', channel=ch,
                                                        pitch=raw, time=0)))
        for n in by_inst.get(key, []):
            t0 = max(0, round(n.start * TPQ))       # groove already applied
            t1 = max(t0 + 1, round((n.start + n.dur) * TPQ))
            events.append((t0, 5, mido.Message('note_on', channel=ch, note=n.pitch,
                                               velocity=n.vel, time=0)))
            events.append((t1, 4, mido.Message('note_off', channel=ch, note=n.pitch,
                                               velocity=0, time=0)))
        _append_deltas(tr, events)
        mid.tracks.append(tr)

    mid.save(path)
    return path


def _append_deltas(track, events):
    """events: (abs_tick, sort_rank, msg) — rank breaks ties (offs before ons)."""
    events.sort(key=lambda e: (e[0], e[1]))
    t = 0
    for tick, _rank, msg in events:
        msg.time = tick - t
        t = tick
        track.append(msg)
    track.append(mido.MetaMessage('end_of_track', time=0))


def midi_report(path: str) -> str:
    """Sanity report: duration, per-track note counts / ranges / channels."""
    mid = mido.MidiFile(path)
    lines = [f'{path}: {mid.length:.1f}s ({mid.length/60:.2f} min), '
             f'{len(mid.tracks)} tracks']
    for tr in mid.tracks:
        name = next((m.name for m in tr if m.type == 'track_name'), '?')
        notes = [m for m in tr if m.type == 'note_on' and m.velocity > 0]
        progs = sorted({m.program for m in tr if m.type == 'program_change'})
        chans = sorted({m.channel for m in tr if hasattr(m, 'channel')})
        if notes or progs:
            lo = min((m.note for m in notes), default=0)
            hi = max((m.note for m in notes), default=0)
            lines.append(f'  {name:18s} notes={len(notes):5d} range={lo}-{hi} '
                         f'prog={progs} ch={chans}')
    return '\n'.join(lines)
