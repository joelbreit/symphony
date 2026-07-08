"""Convert a piece's MIDI into notation data for the web player's sheet-music mode.

Usage (piece package must already exist — run midi_to_piece.py first):
    python tools/midi_to_score.py --piece my-piece mvt1.mid [mvt2.mid ...]

One MIDI file per movement, in the manifest's movement order. Writes
    web/public/pieces/<id>/score/<mvtN>.json
and adds a "score" path to each movement in piece.json.

The score JSON is quantized notation data (not a performance): note starts and
durations snap to a sixteenth grid, expressed in integer units of a quarter
note / 24. A tempo map of [unit, second] anchors lets the player convert
audio time to score position, so the live cursor follows the real
(humanized, rubato) performance.

Requires: pip install mido
"""
import argparse
import json
import os
import re
import statistics
import sys

import mido

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIECES_DIR = os.path.join(ROOT, 'web', 'public', 'pieces')

UPQ = 24                 # units per quarter note
GRID = UPQ // 4          # sixteenth-note grid


def slug(name: str) -> str:
    s = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return s or 'track'


# ---------------------------------------------------------------- key parsing

MAJOR_FIFTHS = {'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F': -1}
LETTER_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def parse_key(text: str | None):
    """'Eb major', 'C minor → C major', 'G minor, stubbornly' -> (fifths, mode, tonic_pc).

    Only the first key named is used; mid-piece modulations show up as
    accidentals. Returns None if nothing parseable.
    """
    if not text:
        return None
    m = re.search(r'([A-G])\s*([b♭#♯]?)\s*(major|minor|maj|min|m\b)?', text)
    if not m:
        return None
    letter, acc, mode = m.group(1), m.group(2), (m.group(3) or 'major').lower()
    minor = mode.startswith('min') or mode == 'm'
    fifths = MAJOR_FIFTHS[letter]
    if acc in ('b', '♭'):
        fifths -= 7
    elif acc in ('#', '♯'):
        fifths += 7
    tonic_pc = (LETTER_PC[letter] + (-1 if acc in ('b', '♭') else 1 if acc in ('#', '♯') else 0)) % 12
    if minor:
        fifths -= 3
    if not -7 <= fifths <= 7:
        return None
    return fifths, ('minor' if minor else 'major'), tonic_pc


# Krumhansl-Schmuckler profiles, for when neither the manifest nor the MIDI
# names a key.
_MAJ = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
_MIN = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]


def infer_key(notes):
    hist = [0.0] * 12
    for (_t, dur, pitch, _v) in notes:
        hist[pitch % 12] += dur
    best = (float('-inf'), 0, 'major', 0)
    for tonic in range(12):
        for mode, prof in (('major', _MAJ), ('minor', _MIN)):
            score = sum(hist[(tonic + i) % 12] * prof[i] for i in range(12))
            if score > best[0]:
                best = (score, tonic, mode, tonic)
    _, tonic, mode, _ = best
    # fifths for the major key with this tonic: tonic_pc -> fifths via circle
    fifths = (tonic * 7) % 12
    if fifths > 6:
        fifths -= 12
    if mode == 'minor':
        fifths -= 3
    return fifths, mode, tonic


# ------------------------------------------------------------ MIDI extraction

def extract(path: str):
    """Read one MIDI file -> (tracks, tempo_anchors).

    tracks: [{'name', 'drum', 'notes': [(start_units, dur_units, pitch, vel)]}]
      with starts/durations quantized to the sixteenth grid (min one sixteenth).
    tempo_anchors: [[units, seconds]] covering the whole movement.
    """
    mid = mido.MidiFile(path)
    tpb = mid.ticks_per_beat

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

    anchors = []                       # (tick, sec)
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

    def to_units(tick: int) -> int:
        return round(tick / tpb * UPQ / GRID) * GRID

    tracks = []
    max_tick = 0
    for tr in mid.tracks:
        name = next((m.name for m in tr if m.type == 'track_name'), None)
        is_drum = False
        tick = 0
        active: dict[tuple, list] = {}
        notes = []
        for msg in tr:
            tick += msg.time
            if hasattr(msg, 'channel') and msg.channel == 9:
                is_drum = True
            if msg.type == 'note_on' and msg.velocity > 0:
                active.setdefault((msg.channel, msg.note), []).append((tick, msg.velocity))
            elif msg.type in ('note_off', 'note_on'):
                key = (getattr(msg, 'channel', 0), getattr(msg, 'note', 0))
                if active.get(key):
                    t0, vel = active[key].pop(0)
                    start = to_units(t0)
                    dur = max(GRID, round((tick - t0) / tpb * UPQ / GRID) * GRID)
                    notes.append([start, dur, msg.note, vel])
                    max_tick = max(max_tick, tick)
        for (_ch, pitch), pending in active.items():
            for t0, vel in pending:
                notes.append([to_units(t0), GRID, pitch, vel])
                max_tick = max(max_tick, t0)
        if not notes:
            continue
        # same pitch landing on the same grid point after quantization: keep one
        seen = {}
        for n in sorted(notes, key=lambda x: (x[0], x[2], -x[1])):
            seen.setdefault((n[0], n[2]), n)
        notes = sorted(seen.values(), key=lambda x: (x[0], x[2]))
        tracks.append({'name': name or f'Track {len(tracks) + 1}',
                       'drum': is_drum, 'notes': notes})

    # tempo anchors in units, plus a final one at the end so the last
    # segment's slope is defined
    out_anchors = [[to_units(tick), round(sec_, 4)] for (tick, sec_, _us) in anchors]
    end_tick = max(max_tick, tempos[-1][0] + 1)
    end = [to_units(end_tick), round(to_sec(end_tick), 4)]
    if end[0] > out_anchors[-1][0]:
        out_anchors.append(end)
    # de-duplicate unit positions (quantization can collapse near ticks)
    dedup = []
    for a in out_anchors:
        if dedup and a[0] <= dedup[-1][0]:
            dedup[-1] = [dedup[-1][0], a[1]]
        else:
            dedup.append(a)
    return tracks, dedup


# ------------------------------------------------------------- clef inference

def infer_clef(track, inst) -> str:
    if track['drum']:
        return 'perc'
    pitches = sorted(n[2] for n in track['notes'])
    if not pitches:
        return 'treble'
    lo = pitches[max(0, int(len(pitches) * 0.08))]
    hi = pitches[min(len(pitches) - 1, int(len(pitches) * 0.92))]
    med = statistics.median(pitches)
    name = ((inst.get('name') or '') + ' ' + (inst.get('id') or '')).lower()
    if inst.get('family') == 'keys' or 'harp' in name or 'celesta' in name or 'piano' in name:
        if lo <= 53 and hi >= 64:
            return 'grand'
    if 'viola' in name and med >= 48:
        return 'alto'
    # low-voiced instruments never read treble; high passages take tenor clef
    if any(t in name for t in ('trombone', 'tuba', 'bassoon', 'cello',
                               'contrabass', 'sousaphone', 'timpani', 'bass')):
        return 'tenor' if med >= 62 else 'bass'
    if med < 56:
        return 'bass'
    return 'treble'


# ------------------------------------------------- track / instrument matching

def match_tracks(tracks, instruments):
    """Map each note-bearing track to a manifest instrument index.

    Track names slug-match instrument ids (midi_to_piece-built pieces) or
    instrument-name slugs; leftovers match fuzzily ("Viola" ~ "Violas",
    "Contrabass" ~ "Basses"), and only then by order. An instrument with no
    track in this movement (a part that rests the whole movement) is fine.
    """
    from difflib import SequenceMatcher
    by_id = {inst['id']: i for i, inst in enumerate(instruments)}
    by_name = {slug(inst.get('name', '')): i for i, inst in enumerate(instruments)}
    mapping = {}
    taken = set()
    for ti, tr in enumerate(tracks):
        s = slug(tr['name'])
        idx = by_id.get(s, by_name.get(s))
        if idx is not None and idx not in taken:
            mapping[ti] = idx
            taken.add(idx)
    # fuzzy pass, best pairs first
    pairs = []
    for ti in range(len(tracks)):
        if ti in mapping:
            continue
        ts = slug(tracks[ti]['name'])
        for i, inst in enumerate(instruments):
            if i in taken:
                continue
            r = max(SequenceMatcher(None, ts, slug(inst['id'])).ratio(),
                    SequenceMatcher(None, ts, slug(inst.get('name', ''))).ratio())
            pairs.append((r, ti, i))
    for r, ti, i in sorted(pairs, reverse=True):
        if r < 0.45 or ti in mapping or i in taken:
            continue
        mapping[ti] = i
        taken.add(i)
    unmatched_tracks = [ti for ti in range(len(tracks)) if ti not in mapping]
    unmatched_insts = [i for i in range(len(instruments)) if i not in taken]
    for ti, i in zip(unmatched_tracks, unmatched_insts):
        mapping[ti] = i
        print(f"  note: matched track '{tracks[ti]['name']}' to instrument "
              f"'{instruments[i]['id']}' by position")
    for ti in unmatched_tracks[len(unmatched_insts):]:
        print(f"  warning: no manifest instrument for track '{tracks[ti]['name']}' — skipped")
    return mapping


# ---------------------------------------------------------------- conversion

def convert_movement(midi_path: str, instruments: list, key_text: str | None):
    """One MIDI file -> score dict (see schema in the module docstring)."""
    tracks, tempo_anchors = extract(midi_path)
    mapping = match_tracks(tracks, instruments)

    all_notes = [n for tr in tracks if not tr['drum'] for n in tr['notes']]
    key = parse_key(key_text) or infer_key(all_notes)
    fifths, mode, tonic = key

    parts = []
    for ti, tr in enumerate(tracks):
        if ti not in mapping:
            continue
        inst = instruments[mapping[ti]]
        parts.append({
            'i': mapping[ti],
            'clef': infer_clef(tr, inst),
            'notes': tr['notes'],
        })
    parts.sort(key=lambda p: p['i'])

    end_units = max((max(n[0] + n[1] for n in p['notes']) for p in parts), default=0)
    bar_units = 4 * UPQ                          # everything here is 4/4
    bars = max(1, -(-end_units // bar_units))

    return {
        'v': 1,
        'upq': UPQ,
        'num': 4,
        'den': 4,
        'fifths': fifths,
        'mode': mode,
        'tonic': tonic,
        'bars': bars,
        'tempos': tempo_anchors,
        'parts': parts,
    }


def _dump(o, ind: int) -> str:
    """json with 1-space indent, but scalar-only arrays stay on one line —
    matches how the checked-in manifests are hand-formatted."""
    if isinstance(o, dict):
        if not o:
            return '{}'
        inner = ',\n'.join(
            f'{" " * (ind + 1)}{json.dumps(k, ensure_ascii=False)}: {_dump(v, ind + 1)}'
            for k, v in o.items())
        return '{\n' + inner + '\n' + ' ' * ind + '}'
    if isinstance(o, list):
        if not o:
            return '[]'
        if all(not isinstance(x, (dict, list)) for x in o):
            s = '[' + ', '.join(json.dumps(x, ensure_ascii=False) for x in o) + ']'
            if len(s) <= 78:
                return s
        inner = ',\n'.join(f'{" " * (ind + 1)}{_dump(x, ind + 1)}' for x in o)
        return '[\n' + inner + '\n' + ' ' * ind + ']'
    return json.dumps(o, ensure_ascii=False)


def dump_manifest(manifest: dict, path: str):
    with open(path, 'w') as f:
        f.write(_dump(manifest, 0) + '\n')


def write_scores(piece_dir: str, manifest: dict, midi_paths: list[str]) -> bool:
    """Write score/<mvt>.json for each movement; set movements[].score.

    Returns True if the manifest dict was modified.
    """
    os.makedirs(os.path.join(piece_dir, 'score'), exist_ok=True)
    changed = False
    for mv, midi_path in zip(manifest['movements'], midi_paths):
        score = convert_movement(midi_path, manifest['instruments'], mv.get('key'))
        rel = f"score/{mv['id']}.json"
        with open(os.path.join(piece_dir, rel), 'w') as f:
            json.dump(score, f, separators=(',', ':'))
        if mv.get('score') != rel:
            mv['score'] = rel
            changed = True
        nnotes = sum(len(p['notes']) for p in score['parts'])
        print(f"{mv['id']}: {score['bars']} bars, {len(score['parts'])} parts, "
              f"{nnotes} notes, key fifths={score['fifths']} ({score['mode']}) "
              f"-> {rel}")
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('midis', nargs='+', help='one MIDI file per movement, in manifest order')
    ap.add_argument('--piece', required=True, help='piece id (directory under web/public/pieces)')
    args = ap.parse_args()

    piece_dir = os.path.join(PIECES_DIR, args.piece)
    manifest_path = os.path.join(piece_dir, 'piece.json')
    if not os.path.isfile(manifest_path):
        sys.exit(f'no manifest at {manifest_path} — run midi_to_piece.py first')
    with open(manifest_path) as f:
        manifest = json.load(f)
    if len(args.midis) != len(manifest['movements']):
        sys.exit(f"{len(args.midis)} MIDI file(s) for {len(manifest['movements'])} "
                 f'movement(s) — pass one per movement, in order')

    if write_scores(piece_dir, manifest, args.midis):
        dump_manifest(manifest, manifest_path)
        print('added score paths to piece.json')


if __name__ == '__main__':
    main()
