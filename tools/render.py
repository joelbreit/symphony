#!/usr/bin/env python3
"""MIDI in, packaged audio out — one command instead of two incantations.

    .venv/bin/python tools/render.py pieces-src/still-turning/output/*.mid \
        --id still-turning

Every piece README repeats the same fluidsynth and afconvert lines by hand,
each with a slightly different gain, and the audio/visual sync in the web
player depends on rendering *the MIDI that was converted*. This does the pair,
finds the soundfont, measures the result, and puts the file where the package
expects it.

It also picks the gain for you. Render, measure the true peak, and if it is
clipping or badly under-level, re-render with a corrected gain — which is what
everyone was doing by hand and eyeballing fluidsynth's warnings for.

Positional arguments are MIDI files **in movement order**; with `--id` they
become `audio/mvt1.m4a`, `audio/mvt2.m4a`, … in that piece's web package.
Without it, the audio lands beside the MIDI.

The WAV is kept next to the MIDI (it is gitignored) so `assess.pianoroll(...,
wav=...)` can draw the measured arc under the designed one; `--no-wav` deletes
it afterwards.
"""
import argparse
import math
import pathlib
import shutil
import subprocess
import sys
import wave

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET_PEAK_DB = -6.0          # aim here; a piano piece wants headroom
CLIP_DB = -0.5
QUIET_DB = -16.0


def find_soundfont(explicit=None) -> pathlib.Path:
    if explicit:
        return pathlib.Path(explicit).expanduser()
    import os
    if os.environ.get('SOUNDFONT'):
        return pathlib.Path(os.environ['SOUNDFONT']).expanduser()
    for d in (ROOT.parent / 'soundfonts', ROOT / 'soundfonts', ROOT.parent):
        hits = sorted(d.glob('*.sf2')) + sorted(d.glob('*.sf3'))
        if hits:
            return hits[0]
    raise SystemExit('no soundfont found: pass --soundfont, set $SOUNDFONT, or '
                     'put one in ../soundfonts/ (any GM bank; the published '
                     'renders used GeneralUser GS)')


def peak_db(path: pathlib.Path) -> float:
    with wave.open(str(path)) as w:
        n, width = w.getnframes(), w.getsampwidth()
        if width != 2:
            return float('nan')
        peak, chunk = 0, 1 << 20
        while n > 0:
            raw = w.readframes(min(chunk, n))
            if not raw:
                break
            n -= min(chunk, n)
            peak = max(peak, max(abs(int.from_bytes(raw[i:i + 2], 'little',
                                                    signed=True))
                                 for i in range(0, len(raw) - 1, 2)))
    return 20 * math.log10(peak / 32768) if peak else -120.0


def fluidsynth(midi: pathlib.Path, wav: pathlib.Path, sf: pathlib.Path,
               gain: float):
    subprocess.run(['fluidsynth', '-ni', '-g', f'{gain:.3f}', '-r', '44100',
                    '-F', str(wav), str(sf), str(midi)],
                   check=True, capture_output=True)


def encode(wav: pathlib.Path, out: pathlib.Path, bitrate: int):
    out.parent.mkdir(parents=True, exist_ok=True)
    if shutil.which('afconvert'):
        subprocess.run(['afconvert', '-f', 'm4af', '-d', 'aac',
                        '-b', str(bitrate), str(wav), str(out)], check=True)
    elif shutil.which('ffmpeg'):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(wav),
                        '-c:a', 'aac', '-b:a', f'{bitrate // 1000}k',
                        str(out)], check=True)
    else:
        raise SystemExit('need afconvert (macOS) or ffmpeg to encode')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('midi', nargs='+', type=pathlib.Path,
                    help='MIDI files, in movement order')
    ap.add_argument('--id', help='web piece id: audio lands in its package')
    ap.add_argument('--gain', type=float, default=None,
                    help='fluidsynth gain; default is chosen by measurement')
    ap.add_argument('--soundfont')
    ap.add_argument('--bitrate', type=int, default=160000)
    ap.add_argument('--no-wav', action='store_true',
                    help='delete the intermediate WAV (keeps it by default so '
                         'assess.pianoroll can measure the render)')
    args = ap.parse_args()

    sf = find_soundfont(args.soundfont)
    print(f'soundfont: {sf.name}')
    for i, midi in enumerate(args.midi, start=1):
        if not midi.exists():
            raise SystemExit(f'no such MIDI: {midi}')
        wav = midi.with_suffix('.wav')
        gain = args.gain if args.gain is not None else 0.55
        fluidsynth(midi, wav, sf, gain)
        pk = peak_db(wav)
        if args.gain is None and (pk > CLIP_DB or pk < QUIET_DB):
            gain = max(0.05, min(4.0, gain * 10 ** ((TARGET_PEAK_DB - pk) / 20)))
            print(f'  {midi.name}: peak {pk:+.1f} dBFS at gain '
                  f'{0.55:.2f} — re-rendering at {gain:.2f}')
            fluidsynth(midi, wav, sf, gain)
            pk = peak_db(wav)
        flag = '  CLIPPING' if pk > CLIP_DB else ''
        out = (ROOT / 'web/public/pieces' / args.id / 'audio' / f'mvt{i}.m4a'
               if args.id else midi.with_suffix('.m4a'))
        encode(wav, out, args.bitrate)
        size = out.stat().st_size / 1e6
        print(f'  {midi.name} -> {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}'
              f'  gain {gain:.2f}, peak {pk:+.1f} dBFS, {size:.1f} MB{flag}')
        if args.no_wav:
            wav.unlink(missing_ok=True)
    if args.id:
        print(f'\nnow re-run tools/midi_to_piece.py --id {args.id} … so the '
              f'note data comes from these same MIDI files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
