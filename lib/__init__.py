"""Shared composition toolkit for new pieces.

Extracted from the four generator lineages after five compositions; the
shipped pieces stay frozen on their own code — new pieces start here.
See lib/README.md for the tour, lib/demo.py for a worked example, and run
`python -m lib.tests` after changing anything in here.
"""
from .chords import QUAL, chord_at, fit, parse_chord, voicing
from .dsl import B, R, parse, total_beats, transpose
from .ensemble import DRUMS, Ensemble, Instrument, dixieland, orchestra, \
    rhythm_section, solo_piano
from .groove import Humanize, swing_warp
from .midiwrite import midi_report
from .piece import DYN, Note, Piece, vel_of
from .pitch import midi, pitch_name
from .timeline import Timeline

__all__ = [
    'B', 'DRUMS', 'DYN', 'Ensemble', 'Humanize', 'Instrument', 'Note',
    'Piece', 'QUAL', 'R', 'Timeline', 'chord_at', 'dixieland', 'fit',
    'midi', 'midi_report', 'orchestra', 'parse', 'parse_chord', 'pitch_name',
    'rhythm_section', 'solo_piano', 'swing_warp', 'total_beats', 'transpose',
    'vel_of', 'voicing',
]
