"""Scene palettes: one small synth ensemble per scene, as data.

All stems of a scene share one ensemble so channels, pans, and ranges stay
consistent across layers; a stem simply leaves the other instruments silent
(the writer skips instruments with no events). GM programs are 0-based
(88 = new age pad, 89 = warm pad, 92 = bowed glass, 4 = e-piano,
108 = kalimba). Reverb stays modest — the release tail must decay inside
the ~3 s window the loop engine leaves it (docs/02, rule 7).
"""
from lib.ensemble import Ensemble, I


def focus() -> Ensemble:
    """A dorian, 72 bpm — steady, present, lightly pulsing."""
    return Ensemble([
        I('bed',    'Bed (warm pad)',      89, 'A1', 'A5', 'synth',   64),
        I('floor',  'Bed floor (organ)',   16, 'A1', 'A5', 'synth',   64, 70),
        I('padmid', 'Harmony (warm pad)',  89, 'G2', 'E5', 'synth',   54),
        I('halo',   'Halo (halo pad)',     94, 'E4', 'C7', 'synth',   74),
        I('motif',  'Motif (e-piano)',      4, 'C3', 'E6', 'keys',    40),
        I('pulse',  'Pulse (kalimba)',    108, 'C4', 'C7', 'plucked', 88),
    ], name='focus', reverb=30)


def deeper_focus() -> Ensemble:
    """D dorian, 60 bpm — the same room later at night, a fifth lower.

    Same proven patches as focus (89 warm pad, 16 organ anchor, 94 halo,
    4 e-piano) sunk a register, plus one new voice: a fingered bass whose
    natural pluck-decay makes it seam-proof for the slow tide pulse."""
    return Ensemble([
        I('bed',    'Bed (warm pad)',       89, 'A1', 'A5', 'synth',   64),
        I('floor',  'Bed floor (organ)',    16, 'A1', 'A5', 'synth',   64, 66),
        I('padlow', 'Harmony (warm pad)',   89, 'E2', 'C5', 'synth',   56),
        I('haze',   'Haze (halo pad)',      94, 'E4', 'C7', 'synth',   72),
        I('murmur', 'Murmur (e-piano)',      4, 'C2', 'C6', 'keys',    44),
        I('tide',   'Tide (fingered bass)', 33, 'C1', 'D3', 'plucked', 60),
    ], name='deeper-focus', reverb=30)
