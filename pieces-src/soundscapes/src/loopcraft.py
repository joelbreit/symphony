"""The loop-stem harness: what makes a stem safe to loop (docs/02).

A stem is a short Piece whose musical body is exactly `bars` bars long; the
rendered file is body + release/reverb tail, and the web engine overlaps
iterations so the tail is the crossfade. `finish()` enforces the seam rules
fail-fast, in the spirit of the range guards, then pads the MIDI past the
loop end so fluidsynth renders the tail instead of cutting it at the last
note-off.
"""
import pathlib
import subprocess
import wave

from lib import Piece

ROOT = pathlib.Path(__file__).resolve().parents[3]
SF2_DEFAULT = ROOT / 'pieces-src/the-unfinished-spire/assets/GeneralUserGS.sf2'

BEATS_PER_BAR = 4          # every scene is in 4/4
ATTACK_VEL_CAP = 84        # rule 5: no hard transient near beat 0
TAIL_BEATS = 8.0           # tail window: seam-crossing voices + release live here


def loop_beats(bars: int) -> float:
    return bars * BEATS_PER_BAR


def loop_seconds(bars: int, bpm: float) -> float:
    return bars * BEATS_PER_BAR * 60.0 / bpm


def new_stem(ensemble, scene: str, slot: str, variant: str,
             bars: int, bpm: float, seed: int) -> Piece:
    p = Piece(ensemble, seed=seed, title=f'{scene} {slot}-{variant}')
    p.tempo(0, bpm)
    p.meter(0, BEATS_PER_BAR, 4)
    return p


def finish(p: Piece, bars: int) -> Piece:
    """Assert the seam rules (docs/02), then pad the tail render window."""
    end = loop_beats(bars)
    for n in p.notes:
        assert n.start < end, \
            f'{n.inst}: onset at beat {n.start} >= loop end {end}'
        assert n.start + n.dur <= end + TAIL_BEATS + 1e-6, \
            f'{n.inst}: note rings past the tail window ({n.start}+{n.dur})'
        if n.start < 0.5:
            assert n.vel <= ATTACK_VEL_CAP, \
                f'{n.inst}: vel {n.vel} at beat {n.start} — soften the file head'
    curves: dict[tuple, list] = {}
    for inst, beat, ctrl, val in p.ccs:
        curves.setdefault((inst, ctrl), []).append((beat, val))
    for (inst, ctrl), evs in sorted(curves.items()):
        evs.sort()
        assert evs[-1][0] <= end, f'{inst}: CC{ctrl} after loop end'
        if ctrl == 11:
            drift = evs[-1][1] - evs[0][1]
            assert 0 <= drift <= 14, \
                f'{inst}: CC11 seam drift {drift} ({evs[0][1]} -> {evs[-1][1]}); ' \
                'end at the start value or a notch above (docs/02, rule 3)'
        if ctrl == 64:
            assert evs[-1][1] == 0, f'{inst}: pedal down across the seam'
    for inst in sorted({n.inst for n in p.notes}):
        cc11 = curves.get((inst, 11))
        p.cc(inst, end + TAIL_BEATS, 11, cc11[-1][1] if cc11 else 110)
    return p


# ------------------------------------------------------------- rendering

def render_wav(mid_path, wav_path, sf2=None, gain=0.5) -> str:
    """fluidsynth render; returns stderr so callers can watch for clipping."""
    sf2 = pathlib.Path(sf2 or SF2_DEFAULT)
    if not sf2.exists():
        raise FileNotFoundError(f'soundfont not found: {sf2} (use --sf2 or $SF2)')
    r = subprocess.run(
        ['fluidsynth', '-ni', '-g', str(gain), '-r', '44100',
         '-F', str(wav_path), str(sf2), str(mid_path)],
        capture_output=True, text=True, check=True)
    return r.stderr


def encode_m4a(wav_path, m4a_path) -> None:
    pathlib.Path(m4a_path).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['afconvert', '-f', 'm4af', '-d', 'aac', '-b', '160000',
                    str(wav_path), str(m4a_path)],
                   capture_output=True, text=True, check=True)


def wav_seconds(path) -> float:
    with wave.open(str(path), 'rb') as w:
        return w.getnframes() / w.getframerate()
