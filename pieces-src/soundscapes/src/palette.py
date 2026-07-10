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


def motivate() -> Ensemble:
    """E aeolian, 104 bpm — the building-montage scene (docs/05).

    Not a synth palette: a small film-score ensemble, because this scene is
    composed music on a shared 16-bar form, not weather. Piano and plucked
    bass are the seam-proof motor; strings carry the swells (slow attack =
    soft seams by nature); horns and celli trade the theme; flute and
    celesta are the high color. Reverb modest so tails fit the loop window
    (docs/02, rule 7)."""
    return Ensemble([
        I('bass',  'Ground (fingered bass)', 33, 'D1', 'C3', 'plucked', 60, 105),
        I('piano', 'Engine (piano)',          0, 'A0', 'C7', 'keys',    50),
        I('str',   'Strings',                48, 'C2', 'C7', 'strings', 70),
        I('hn',    'Theme (horns)',          60, 'E2', 'F5', 'brass',   40),
        I('vc',    'Theme (celli)',          42, 'C2', 'A4', 'strings', 78),
        I('fl',    'Descant (flute)',        73, 'C5', 'C7', 'winds',   56, 90),
        I('cel',   'Descant (celesta)',       8, 'C4', 'C8', 'keys',    64, 90),
    ], name='motivate', reverb=32)
