"""Self-tests for the toolkit: `python -m lib.tests` (exits nonzero on failure).

Plain asserts, no test framework — same spirit as the pieces' own guards.
"""
import os
import sys
import tempfile
from fractions import Fraction

from . import assess, figures
from .chords import chord_at, fit, parse_chord, voicing
from .dsl import B, R, parse, total_beats, transpose
from .ensemble import DRUMS, Ensemble, Instrument, dixieland, orchestra, \
    rhythm_section, solo_piano
from .groove import Humanize, swing_warp
from .midiwrite import midi_report, write_midi
from .piece import DYN, Piece
from .pitch import midi, pitch_name
from .timeline import Timeline


def test_pitch():
    assert midi('C4') == 60 and midi('A4') == 69
    assert midi('Bb3') == 58 and midi('F#2') == 42 and midi('Eb5') == 75
    assert midi('C##4') == 62 and midi('Cbb4') == 58
    assert midi('A0') == 21 and midi('C-1') == 0
    assert midi(64) == 64
    assert pitch_name(70) == 'A#4' and pitch_name(60) == 'C4'


def test_dsl():
    ev = parse('G4:q Eb5:e r:h')
    assert ev == [(67, Fraction(1)), (75, Fraction(1, 2)), (None, Fraction(2))]
    ev = parse('(C3 E3 G3):h.')
    assert ev == [([48, 52, 55], Fraction(3))]
    assert parse('C4:t C4:t C4:t')[0][1] * 3 == 1     # triplet exactness
    assert parse('C4:1.5') == [(60, Fraction(3, 2))]
    assert total_beats('C4:q D4:q E4:h') == 4.0
    assert R('C4:q', 3) == 'C4:q C4:q C4:q'
    assert total_beats(R('C4:q r:q', 4)) == 8.0
    B('C4:w C4:w', 2)                                  # 2 bars of 4/4: passes
    B('C4:h. C4:h.', 2, meter=(3, 4))                  # 2 bars of 3/4: passes
    try:
        B('C4:w C4:h', 2)
        raise SystemExit('B() should have raised')
    except AssertionError:
        pass
    assert transpose('C4:q', 7) == [(67, Fraction(1))]
    assert transpose([([60, 64], 1)], -12) == [([48, 52], Fraction(1))]


def test_chords():
    root, bass, pcs = parse_chord('D7')
    assert (root, bass) == (2, 2) and pcs == [2, 6, 9, 0]
    root, bass, pcs = parse_chord('F/C')
    assert (root, bass) == (5, 0)
    assert parse_chord('Bdim7')[2] == [11, 2, 5, 8]
    assert parse_chord('Ebmaj7')[0] == 3
    try:
        parse_chord('Cxyz')
        raise SystemExit('parse_chord should have raised')
    except ValueError:
        pass
    chart = ['F7', ('Gm7', 'C7')]
    assert chord_at(chart, 0) == 'F7'
    assert chord_at(chart, 1, half=1) == 'C7'
    assert chord_at(chart, 2) == 'F7'                  # wraps
    assert fit(0, 60, 72, near=65) == 60               # C nearest 65 in range
    assert fit(0, 60, 72) in (60, 72)
    assert fit(7, 'C4', 'C5', near='A4') == 67
    v = voicing('C7', 48, 65)
    assert v == sorted(set(v)) and all(48 <= p <= 65 for p in v)
    assert {p % 12 for p in v} == {0, 4, 7, 10}


def test_timeline():
    tl = Timeline()
    assert tl.seconds(4) == 2.0                        # default 120bpm
    tl.tempo(0, 120)
    tl.tempo(8, 60)
    assert tl.seconds(8) == 4.0
    assert tl.seconds(12) == 8.0
    assert tl.bpm_at(7.9) == 120 and tl.bpm_at(8) == 60
    tl2 = Timeline()
    tl2.meter(0, 3, 4)
    tl2.meter(9, 4, 4)
    assert tl2.bar_start(1) == 0.0
    assert tl2.bar_start(2) == 3.0
    assert tl2.bar_start(4) == 9.0                     # first 4/4 bar
    assert tl2.bar_start(5) == 13.0
    assert tl2.bar(2, 1.5) == 4.5
    assert tl2.bar_length(1) == 3.0 and tl2.bar_length(4) == 4.0


def test_swing():
    assert swing_warp(0.0, 0.62) == 0.0
    assert abs(swing_warp(0.5, 0.62) - 0.62) < 1e-9
    assert abs(swing_warp(1.0, 0.62) - 1.0) < 1e-9
    assert abs(swing_warp(2.25, 0.62) - 2.31) < 1e-9
    assert abs(swing_warp(0.5, 2 / 3) - 2 / 3) < 1e-9  # triplet feel
    assert swing_warp(3.0, 0.5) == 3.0                 # straight = identity


def test_ensembles():
    for ens in (orchestra(), dixieland(), rhythm_section(), solo_piano()):
        chans = list(ens.channels.values())
        melodic = [c for k, c in ens.channels.items() if not ens[k].percussion]
        assert len(set(melodic)) == len(melodic), f'{ens.name}: channel clash'
        assert all(c != 9 for c in melodic)
        assert all(ens[k].percussion for k, c in ens.channels.items() if c == 9)
        assert all(0 <= c <= 15 for c in chans)
    try:
        Ensemble([Instrument(f'i{n}', f'I{n}') for n in range(16)])
        raise SystemExit('Ensemble should have raised (16 melodic > 15 channels)')
    except ValueError:
        pass
    assert DRUMS['kick'] == 36 and DRUMS['tamtam'] == DRUMS['china'] == 52


def test_piece_add():
    p = Piece(solo_piano(), seed=3)
    end = p.add('piano', 0, 'C4:q E4:q G4:h', vel='p', vel_end='f')
    assert end == 4.0
    assert [n.vel for n in p.notes] == [DYN['p'], (DYN['p'] + DYN['f']) // 2, DYN['f']]
    assert p.notes[2].dur == 2 * 0.95                  # gate
    end = p.add('piano', end, [([60, 64, 67], 2)], gate=1.0)
    assert end == 6.0 and len(p.notes) == 6            # chord = 3 note events
    assert p.end() == 6.0
    try:
        p.add('piano', 0, 'C4:q', transpose=-60)
        raise SystemExit('range guard should have raised')
    except ValueError:
        pass
    p.add('piano', 0, [(5, 1)], check_range=False)     # bypass works
    p2 = Piece(dixieland(), seed=3)
    p2.perc(0, 'kick:q r:q sn:q r:q')
    assert [n.pitch for n in p2.notes] == [36, 38]
    try:
        p2.perc(0, 'nosuchdrum:q')
        raise SystemExit('perc should have raised')
    except KeyError:
        pass


def test_marks_and_expression():
    p = Piece(orchestra(), seed=1, title='t')
    p.tempo(0, 120)
    p.add('vln1', 0, 'C5:w C5:w', gate=1.0)
    p.mark('one', 0)
    p.mark('two', 4)
    p.cue('hit', 6)
    md = p.marks_dict()
    assert md['sections'] == [[0.0, 'one'], [2.0, 'two']]
    assert md['cues'] == {'hit': 3.0} and md['end'] == 4.0
    p.hairpin('vln1', 0, 2, 40, 100, step=0.5)
    vals = [v for (_, _, c, v) in p.ccs if c == 11]
    assert vals[0] == 40 and vals[-1] == 100 and len(vals) == 5
    p.pedal('vln1', 0, 4)
    assert [(c, v) for (_, _, c, v) in p.ccs if c == 64] == [(64, 127), (64, 0)]
    p.bend('vln1', 1.0, -2.0)
    assert p.bends[0][2] == -8192


def test_write_roundtrip():
    import mido
    p = Piece(dixieland(), seed=9, title='roundtrip')
    p.tempo(0, 160)
    p.meter(0, 4, 4)
    p.mark('head', 0)
    p.add('cornet', 0, 'C5:q D5:e E5:e G5:h')
    p.add('tuba', 0, 'F2:q r:q C3:q r:q')
    p.perc(0, 'kick:q sn:q kick:q sn:q')
    figures.scoop(p, 'cornet', 3.0)
    p.hairpin('cornet', 2, 4, 60, 110)
    with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR') or None) as td:
        path = os.path.join(td, 't.mid')
        p.write(path, swing=0.62)
        mid = mido.MidiFile(path)
        assert mid.type == 1
        names = [next((m.name for m in tr if m.type == 'track_name'), '?')
                 for tr in mid.tracks]
        assert names[0] == 'roundtrip'
        assert 'Cornet' in names and 'Tuba' in names and 'Drums' in names
        cond = mid.tracks[0]
        assert any(m.type == 'set_tempo' for m in cond)
        assert any(m.type == 'time_signature' for m in cond)
        assert any(m.type == 'marker' and m.text == 'head' for m in cond)
        for tr, name in zip(mid.tracks[1:], names[1:]):
            chans = {m.channel for m in tr if hasattr(m, 'channel')}
            assert len(chans) == 1, f'{name}: track spans channels {chans}'
            if name == 'Drums':
                assert chans == {9}
            ons = sum(1 for m in tr if m.type == 'note_on' and m.velocity > 0)
            offs = sum(1 for m in tr if m.type == 'note_off'
                       or (m.type == 'note_on' and m.velocity == 0))
            assert ons == offs and ons > 0
        cornet = mid.tracks[names.index('Cornet')]
        assert any(m.type == 'pitchwheel' for m in cornet)
        assert sum(1 for m in cornet if m.type == 'control_change'
                   and m.control == 11) >= 2
        assert all(any(m.type == 'control_change' and m.control == cc for m in tr)
                   for tr in mid.tracks[1:] for cc in (7, 10, 91))
        # determinism: same piece written twice is byte-identical
        path2 = os.path.join(td, 't2.mid')
        p.write(path2, swing=0.62)
        with open(path, 'rb') as a, open(path2, 'rb') as b:
            assert a.read() == b.read()
        assert 'Cornet' in midi_report(path)


def test_meta_text_sanitized():
    # MIDI meta text is latin-1; house style is full of em-dashes
    import mido
    p = Piece(solo_piano(), seed=5, title='Étude — “test”…')
    p.mark('the close — pp', 0)
    p.note('piano', 0, 'C4', 1)
    with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR') or None) as td:
        path = os.path.join(td, 'm.mid')
        p.write(path)
        cond = mido.MidiFile(path).tracks[0]
        assert next(m.name for m in cond if m.type == 'track_name') == 'Étude - "test"...'
        assert next(m.text for m in cond if m.type == 'marker') == 'the close - pp'


def test_overlap_trim():
    import mido
    p = Piece(solo_piano(), seed=2)
    p.note('piano', 0.0, 'C4', 2.0, gate=1.0)          # overlaps the next C4
    p.note('piano', 1.0, 'C4', 1.0, gate=1.0)
    with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR') or None) as td:
        path = os.path.join(td, 'o.mid')
        p.write(path, humanize=None)
        mid = mido.MidiFile(path)
        t, pending = 0, []
        for m in mid.tracks[1]:
            t += m.time
            if m.type == 'note_on' and m.velocity > 0:
                assert not pending, 'second note_on while first C4 still sounding'
                pending.append(t)
            elif m.type in ('note_off', 'note_on'):
                pending.pop()


def test_assess_and_figures():
    p = Piece(orchestra(), seed=4, title='figures')
    p.tempo(0, 100)
    p.add('vln1', 0, figures.trem('C5', 4.0), vel='p')
    p.add('hp', 0, figures.arp(['C3', 'G3', 'C4', 'E4'], 0.25, 4.0, 'updown'))
    p.add('vc', 0, figures.ost('C3:e G3:e', 4))
    figures.roll(p, 'timp', 'C3', 4.0, 2.0, 30, 90)
    figures.cym_swell(p, 4.0, 2.0, 20, 80)
    figures.harp_arp(p, 'hp', ['C3', 'E3', 'G3', 'C4'], 6.0, vel='f')
    figures.strum(p, 'vc', voicing('Cm', 48, 65), 6.0, 2.0, 'mf')
    figures.trill(p, 'fl', 'A5', 6.0, 2.0, 80)
    figures.smear_into(p, 'tbn', 'F3', 6.0, 80)
    figures.falloff(p, 'tpt', 'C5', 6.0, 90)
    figures.curl(p, 'cl', 'G4', 6.0, 80)
    figures.press_roll(p, 8.0, 90)
    assert assess.report(p, out=lambda *_: None)
    with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR') or None) as td:
        assert os.path.exists(assess.pianoroll(p, os.path.join(td, 'r.png')))


def main():
    tests = [(k, v) for k, v in sorted(globals().items())
             if k.startswith('test_') and callable(v)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f'  ok  {name}')
        except Exception as e:  # noqa: BLE001 — report and keep going
            failed += 1
            print(f'FAIL  {name}: {type(e).__name__}: {e}')
    print(f'{len(tests) - failed}/{len(tests)} passed')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
