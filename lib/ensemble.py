"""Ensembles as data: instrument specs + roster presets.

An Instrument declares everything downstream code needs — GM program,
sounding range (fail-fast guarded at note entry), stage pan, mix volume,
family (drives humanize tightness and assessment colors). An Ensemble
assigns MIDI channels (percussion always 9) and is the only thing a Piece
needs to know about its players. New genres = new rosters, not new code.
"""
from dataclasses import dataclass

from .pitch import midi


@dataclass(frozen=True)
class Instrument:
    key: str                 # short handle used in composing code ('vln1')
    name: str                # MIDI track name / display name ('Violin I')
    program: int = 0         # GM program, 0-based; ignored for percussion
    lo: int = 0              # sounding range guard (MIDI), inclusive
    hi: int = 127
    family: str = 'other'    # winds|brass|strings|plucked|keys|perc|synth|voice|other
    pan: int = 64            # CC10 at t=0
    volume: int = 100        # CC7 at t=0
    percussion: bool = False # channel 9, pitches are GM drum keys
    grand: bool = False      # engraved on two staves split at middle C


def I(key, name, program, lo, hi, family, pan=64, volume=100, grand=False):
    return Instrument(key, name, program, midi(lo), midi(hi), family, pan,
                      volume, grand=grand)


class Ensemble:
    def __init__(self, instruments, name: str = 'ensemble', reverb: int = 40):
        self.name = name
        self.reverb = reverb
        self.instruments: dict[str, Instrument] = {}
        self.channels: dict[str, int] = {}
        melodic = [c for c in range(16) if c != 9]
        for inst in instruments:
            if inst.key in self.instruments:
                raise ValueError(f'duplicate instrument key {inst.key!r}')
            self.instruments[inst.key] = inst
            if inst.percussion:
                self.channels[inst.key] = 9
            else:
                if not melodic:
                    raise ValueError('more than 15 melodic instruments (out of MIDI channels)')
                self.channels[inst.key] = melodic.pop(0)

    def __getitem__(self, key: str) -> Instrument:
        return self.instruments[key]

    def __contains__(self, key: str) -> bool:
        return key in self.instruments

    def __iter__(self):
        return iter(self.instruments.values())

    def keys(self):
        return self.instruments.keys()


# GM drum map (channel 10), superset of the box/riot/rattler maps, with the
# aliases each lineage used ('tamtam'/'china', 'susp'/'splash').
DRUMS = {
    'bd': 35, 'kick': 36, 'rim': 37, 'sn': 38, 'clap': 39, 'esn': 40,
    'tomf': 41, 'hhc': 42, 'tomf2': 43, 'hhp': 44, 'tom1': 45, 'hho': 46,
    'tom2': 47, 'tom3': 48, 'crash': 49, 'tom4': 50, 'ride': 51,
    'china': 52, 'tamtam': 52, 'ridebell': 53, 'tamb': 54, 'splash': 55,
    'susp': 55, 'cowbell': 56, 'crash2': 57, 'vibraslap': 58, 'ride2': 59,
    'bongo_h': 60, 'bongo_l': 61, 'conga_mute': 62, 'conga_h': 63,
    'conga_l': 64, 'timbale_h': 65, 'timbale_l': 66, 'agogo_h': 67,
    'agogo_l': 68, 'cabasa': 69, 'maracas': 70, 'shaker': 70,
    'claves': 75, 'wbh': 76, 'wbl': 77, 'trimute': 80, 'tri': 81,
}


# -------------------------------------------------------------- presets

def orchestra() -> Ensemble:
    """The Window's full-orchestra roster: 15 pitched sections + percussion.

    Programs/ranges from the-window's ROSTER; pans follow stage seating
    (from the-unfinished-spire). Strings switch pizz/arco with
    piece.program(key, beat, 45|48).
    """
    return Ensemble([
        I('fl',   'Flutes',           73, 60, 96,  'winds',   55),
        I('ob',   'Oboes',            68, 58, 89,  'winds',   68),
        I('cl',   'Clarinets',        71, 50, 91,  'winds',   48),
        I('bsn',  'Bassoons',         70, 34, 75,  'winds',   72),
        I('hn',   'Horns',            60, 35, 77,  'brass',   38),
        I('tpt',  'Trumpets',         56, 52, 84,  'brass',   70),
        I('tbn',  'Trombones & Tuba', 57, 26, 72,  'brass',   78),
        I('timp', 'Timpani',          47, 38, 57,  'perc',    60),
        I('hp',   'Harp',             46, 24, 103, 'plucked', 35, grand=True),
        I('cel',  'Celesta',           8, 60, 108, 'keys',    45),
        I('vln1', 'Violin I',         48, 55, 100, 'strings', 30),
        I('vln2', 'Violin II',        48, 55, 88,  'strings', 45),
        I('vla',  'Viola',            48, 48, 88,  'strings', 75),
        I('vc',   'Cello',            48, 36, 81,  'strings', 88),
        I('cb',   'Contrabass',       48, 28, 55,  'strings', 95),
        Instrument('perc', 'Percussion', family='perc', percussion=True),
    ], name='orchestra', reverb=70)


def dixieland() -> Ensemble:
    """Seven-piece trad-jazz band (ranges from high-street-riot/rattler)."""
    return Ensemble([
        I('cornet',   'Cornet',     56, 54, 86, 'brass',   52),
        I('clarinet', 'Clarinet',   71, 52, 91, 'winds',   80, 90),
        I('tbn',      'Trombone',   57, 40, 72, 'brass',   44),
        I('sax',      'Tenor Sax',  66, 44, 75, 'winds',   36, 92),
        I('tuba',     'Tuba',       58, 26, 58, 'brass',   64, 110),
        I('banjo',    'Banjo',     105, 45, 72, 'plucked', 92, 78),
        Instrument('drums', 'Drums', family='perc', percussion=True),
    ], name='dixieland', reverb=28)


def rhythm_section() -> Ensemble:
    """Piano / guitar / upright bass / drums."""
    return Ensemble([
        I('piano',  'Piano',        0, 21, 108, 'keys',    54, grand=True),
        I('guitar', 'Guitar',      26, 40, 86,  'plucked', 80, 85),
        I('bass',   'Bass',        32, 28, 60,  'plucked', 60, 105),
        Instrument('drums', 'Drums', family='perc', percussion=True),
    ], name='rhythm section', reverb=25)


def solo_piano() -> Ensemble:
    return Ensemble([I('piano', 'Piano', 0, 21, 108, 'keys', grand=True)],
                    name='solo piano', reverb=45)
