"""Convert MIDI file(s) into a piece package for the web player.

Usage:
    python tools/midi_to_piece.py --id my-piece --title "My Piece" \
        --composer "Name" path/to/mvt1.mid [path/to/mvt2.mid ...]

One MIDI file per movement, in order. Writes:
    web/public/pieces/<id>/notes/<mvtN>.json    (always regenerated)
    web/public/pieces/<id>/piece.json           (skeleton; only if absent,
                                                 unless --force — hand edits
                                                 to the manifest are preserved)
and rebuilds web/public/pieces/index.json.

Audio is NOT generated here. Render each movement from the SAME MIDI files
(sync depends on it), e.g.:
    fluidsynth -ni -g 0.5 -r 44100 -F /tmp/m.wav <soundfont>.sf2 mvt1.mid
    afconvert -f m4af -d aac -b 160000 /tmp/m.wav \
        web/public/pieces/<id>/audio/mvt1.m4a

Requires: pip install mido
"""
import argparse
import json
import os
import re
import sys

import mido

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from midi_to_score import dump_manifest, write_scores

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIECES_DIR = os.path.join(ROOT, 'web', 'public', 'pieces')

ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']

def family_for(program: int | None, is_drum: bool) -> str:
    if is_drum:
        return 'color'
    if program is None:
        return 'other'
    if 40 <= program <= 51 or program in (24, 25, 32, 33, 34, 35):  # strings, guitars, basses
        return 'strings'
    if 56 <= program <= 63:
        return 'brass'
    if 64 <= program <= 79:
        return 'winds'
    if 80 <= program <= 103:
        return 'other'          # synth leads/pads
    if program in (46, 47) or 8 <= program <= 15 or 104 <= program <= 119:
        return 'color'          # harp, timpani, chromatic & ethnic percussion
    if 0 <= program <= 7 or 16 <= program <= 23:
        return 'keys'
    if 52 <= program <= 55:
        return 'voices'
    return 'other'

def slug(name: str) -> str:
    s = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return s or 'track'

def extract(path: str):
    """Return (track_infos, notes) where notes use a local track index."""
    mid = mido.MidiFile(path)
    tpb = mid.ticks_per_beat

    # global tempo map in absolute ticks; last event at a given tick wins,
    # and the 120bpm default applies only if nothing is set at tick 0
    raw = []
    for tr in mid.tracks:
        tick = 0
        for msg in tr:
            tick += msg.time
            if msg.type == 'set_tempo':
                raw.append((tick, msg.tempo))
    by_tick: dict[int, int] = {}
    for tick, us in sorted(raw, key=lambda x: x[0]):
        by_tick[tick] = us
    if 0 not in by_tick:
        by_tick[0] = 500000
    tempos = sorted(by_tick.items())

    anchors = []           # (tick, sec, us_per_beat)
    sec = 0.0
    for i, (tick, us) in enumerate(tempos):
        if i > 0:
            ptick, pus = tempos[i - 1]
            sec += (tick - ptick) / tpb * pus / 1e6
        anchors.append((tick, sec, us))

    def to_sec(tick: int) -> float:
        for (atick, asec, aus) in reversed(anchors):
            if tick >= atick:
                return asec + (tick - atick) / tpb * aus / 1e6
        return tick / tpb * anchors[0][2] / 1e6

    tracks = []
    notes = []
    for tr in mid.tracks:
        name = next((m.name for m in tr if m.type == 'track_name'), None)
        program = None
        is_drum = False
        tick = 0
        # FIFO per (channel, pitch): same-pitch notes can overlap (humanized
        # repeats, drum rolls), so a single slot would drop every second one
        active: dict[tuple, list] = {}
        count = 0
        for msg in tr:
            tick += msg.time
            if msg.type == 'program_change' and program is None:
                program = msg.program
            if hasattr(msg, 'channel') and msg.channel == 9:
                is_drum = True
            if msg.type == 'note_on' and msg.velocity > 0:
                active.setdefault((msg.channel, msg.note), []).append((tick, msg.velocity))
            elif msg.type in ('note_off', 'note_on'):
                key = (getattr(msg, 'channel', 0), getattr(msg, 'note', 0))
                if active.get(key):
                    t0, vel = active[key].pop(0)
                    notes.append([round(to_sec(t0), 3),
                                  round(max(to_sec(tick) - to_sec(t0), 0.05), 3),
                                  msg.note, len(tracks), vel])
                    count += 1
        # stranded note_ons (no note_off anywhere — some generators omit it
        # for one-shot percussion): the synth still plays the hit, so emit
        # a minimum-length note rather than dropping it
        for (_ch, pitch), pending in active.items():
            for t0, vel in pending:
                notes.append([round(to_sec(t0), 3), 0.05, pitch, len(tracks), vel])
                count += 1
        if count > 0:
            tracks.append({'name': name or f'Track {len(tracks) + 1}',
                           'program': program, 'drum': is_drum, 'count': count})
        else:
            # track produced no notes; remap any notes pointing past it (none do,
            # since we only append the track after counting) — just skip it.
            notes = [n for n in notes if n[3] != len(tracks)]
    dur = max((n[0] + n[1] for n in notes), default=0.0)
    return tracks, notes, dur

def rebuild_index():
    entries = []
    for name in sorted(os.listdir(PIECES_DIR)):
        mpath = os.path.join(PIECES_DIR, name, 'piece.json')
        if not os.path.isfile(mpath):
            continue
        with open(mpath) as f:
            man = json.load(f)
        entries.append({
            'id': man['id'],
            'dir': f'pieces/{name}',
            'title': man['title'],
            'subtitle': man.get('subtitle'),
            'composer': man['composer'],
            'concept': man.get('concept'),
            'accent': (man.get('theme') or {}).get('accent'),
            'movements': len(man['movements']),
            'duration': round(sum(m['duration'] for m in man['movements']), 2),
        })
    with open(os.path.join(PIECES_DIR, 'index.json'), 'w') as f:
        json.dump({'pieces': entries}, f, separators=(',', ':'), ensure_ascii=False)
    return entries

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('midis', nargs='+', help='one MIDI file per movement, in order')
    ap.add_argument('--id', required=True, help='piece id (url-safe slug)')
    ap.add_argument('--title', required=True)
    ap.add_argument('--composer', required=True)
    ap.add_argument('--subtitle', default=None)
    ap.add_argument('--year', type=int, default=None)
    ap.add_argument('--force', action='store_true',
                    help='overwrite an existing piece.json (loses hand edits)')
    args = ap.parse_args()

    piece_dir = os.path.join(PIECES_DIR, args.id)
    os.makedirs(os.path.join(piece_dir, 'notes'), exist_ok=True)
    os.makedirs(os.path.join(piece_dir, 'audio'), exist_ok=True)

    # union of instruments across movements, keyed by track name
    instruments: list[dict] = []
    inst_by_name: dict[str, int] = {}
    movements = []

    for mi, midi_path in enumerate(args.midis):
        tracks, notes, dur = extract(midi_path)
        remap = {}
        for ti, tr in enumerate(tracks):
            if tr['name'] not in inst_by_name:
                inst_by_name[tr['name']] = len(instruments)
                instruments.append({
                    'id': slug(tr['name']),
                    'name': tr['name'],
                    'family': family_for(tr['program'], tr['drum']),
                })
            remap[ti] = inst_by_name[tr['name']]
        for n in notes:
            n[3] = remap[n[3]]
        notes.sort(key=lambda x: (x[0], x[2]))
        mvt_id = f'mvt{mi + 1}'
        with open(os.path.join(piece_dir, 'notes', f'{mvt_id}.json'), 'w') as f:
            json.dump(notes, f, separators=(',', ':'))
        base = os.path.splitext(os.path.basename(midi_path))[0]
        movements.append({
            'id': mvt_id,
            'num': ROMAN[mi] if len(args.midis) > 1 else '·',
            'title': base.replace('_', ' ').replace('-', ' ').title(),
            'duration': round(dur + 1.5, 2),   # small pad for reverb tail; correct by hand if needed
            'noteCount': len(notes),
            'audio': f'audio/{mvt_id}.m4a',
            'notes': f'notes/{mvt_id}.json',
            'sections': [[0, base.replace('_', ' ').replace('-', ' ')]],
        })
        print(f'{mvt_id}: {len(notes)} notes, {dur/60:.2f} min, '
              f'{len(tracks)} tracks ({midi_path})')

    # ensure unique instrument ids
    seen: dict[str, int] = {}
    for inst in instruments:
        if inst['id'] in seen:
            seen[inst['id']] += 1
            inst['id'] = f"{inst['id']}-{seen[inst['id']]}"
        else:
            seen[inst['id']] = 1

    manifest_path = os.path.join(piece_dir, 'piece.json')
    if os.path.exists(manifest_path) and not args.force:
        # keep the hand-edited manifest; refresh measured fields only
        with open(manifest_path) as f:
            man = json.load(f)
        old = {m['id']: m for m in man.get('movements', [])}
        for m in movements:
            if m['id'] in old:
                old[m['id']].update({k: m[k] for k in ('duration', 'noteCount', 'notes', 'audio')})
            else:
                man.setdefault('movements', []).append(m)
        if not man.get('instruments'):
            man['instruments'] = instruments
        dump_manifest(man, manifest_path)
        print('updated measured fields in existing piece.json (hand edits preserved)')
    else:
        man = {
            'schema': 1,
            'id': args.id,
            'title': args.title,
            'subtitle': args.subtitle,
            'composer': args.composer,
            'year': args.year,
            'concept': None,
            'about': [],
            'credits': [],
            'theme': {'accent': '#d9a84e'},
            'instruments': instruments,
            'movements': movements,
            'moments': [],
        }
        man = {k: v for k, v in man.items() if v is not None}
        dump_manifest(man, manifest_path)
        print(f'wrote skeleton {manifest_path} — now add concept/sections/about '
              f'(see PIECES.md)')

    # notation data for the player's sheet-music mode
    if write_scores(piece_dir, man, args.midis):
        dump_manifest(man, manifest_path)

    entries = rebuild_index()
    print(f'index has {len(entries)} piece(s)')
    print(f"don't forget audio: render each movement's MIDI to "
          f'{piece_dir}/audio/mvtN.m4a (see PIECES.md)')

if __name__ == '__main__':
    main()
