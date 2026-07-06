"""Worked example + end-to-end exercise of the toolkit: `python -m lib.demo`.

Builds two miniatures into lib/demo_output/ (gitignored):
  - orchestra_etude.mid — 3/4 dawn into a 4/4 dance: DSL melodies with bar
    guards, textures, CC11 hairpins on held strings, pizz/arco program
    switch, meter + tempo changes, marks/cues -> marks.json.
  - blues_etude.mid — 12-bar F blues for the dixieland preset: chord charts
    driving tuba/banjo, fit() voice leading, jazz idioms (smear, falloff,
    curl, scoop, press roll), swung + humanized write.

Both are validated with assess.report and plotted with assess.pianoroll.
"""
import os

from . import assess, figures
from .chords import chord_at, fit, parse_chord, voicing
from .dsl import B, R
from .ensemble import dixieland, orchestra
from .midiwrite import midi_report
from .piece import Piece


# ================================================================ orchestra

def orchestra_etude() -> Piece:
    p = Piece(orchestra(), seed=21, title='Étude I — Dawn Dance')
    p.meter(0, 3, 4)
    p.tempo(0, 63, 'calm')

    # -- dawn: 8 bars of 3/4, C minor ------------------------------------
    p.mark('dawn', 0)
    for b in range(1, 9):                      # strings pad, whole bars
        t = p.bar(b)
        p.add('vc', t, '(C3 G3):h.', vel='pp', gate=1.0)
        p.add('vla', t, 'Eb4:h.', vel='pp', gate=1.0)
        p.add('vln2', t, 'G4:h.', vel='pp', gate=1.0)
    for inst in ('vc', 'vla', 'vln2'):         # swell on the held pad
        p.hairpin(inst, p.bar(5), p.bar(8), 50, 100)
        p.cc(inst, p.bar(9), 11, 110)          # reset before the dance
    for b in (1, 3, 5, 7):
        figures.harp_arp(p, 'hp', ['C3', 'G3', 'C4', 'Eb4', 'G4'], p.bar(b),
                         vel='p')
    dawn_tune = B('G5:h Eb5:q F5:h D5:q Eb5:h C5:q D5:h.', 4, meter=(3, 4))
    p.add('fl', p.bar(3), dawn_tune, vel='p', vel_end='mf')
    p.add('ob', p.bar(7), 'Eb5:h C5:q D5:h.', vel='p')
    figures.roll(p, 'timp', 'C3', p.bar(8), 3.0, 30, 96)
    figures.cym_swell(p, p.bar(8), 3.0, 20, 84)

    # -- the dance: 4/4, quicker ------------------------------------------
    dance0 = p.bar(9)                          # beat 24
    p.meter(dance0, 4, 4)
    p.tempo(dance0, 132, 'the dance')
    p.mark('the dance', dance0)
    p.cue('dance', dance0)

    theme = B('C5:e D5:e Eb5:e F5:e G5:q Eb5:q '
              'F5:e G5:e Ab5:e F5:e G5:h', 2)
    p.add('vln1', p.bar(9), R(theme, 2), vel='mf', accent_first=True)
    p.add('vln1', p.bar(13), R(theme, 2), vel='f', transpose=5)
    p.add('fl', p.bar(15), theme, vel='f', transpose=12)

    p.program('vc', dance0, 45)                # cellos go pizzicato
    bassline = {9: 'C', 10: 'C', 11: 'F', 12: 'G', 13: 'F', 14: 'F',
                15: 'Ab', 16: 'G'}
    for b, root in bassline.items():
        _, bass_pc, pcs = parse_chord(root if root != 'G' else 'G7')
        r = fit(bass_pc, 'C2', 'C3')
        p.add('vc', p.bar(b), [(r + 12, 1), (r + 12, 1), (fit(pcs[2], 48, 60), 1),
                               (r + 12, 1)], vel='mf', gate=0.5)
        p.add('cb', p.bar(b), [(r, 1), (None, 1), (r, 1), (None, 1)], vel='mf')
    p.program('vc', p.bar(17), 48)             # arco again for the close

    for b in (10, 12, 14):                     # horn/trumpet offbeat stabs
        p.add('hn', p.bar(b, 1.5), '(C4 Eb4 G4):e', vel='f', gate=0.6)
        p.add('tpt', p.bar(b, 3.5), '(G4 C5):e', vel='f', gate=0.6)
    p.add('vln2', p.bar(13), figures.trem('G4', 8.0), vel='mp')
    p.add('vla', p.bar(13), figures.ost('C4:e G3:e', 8), vel='mp')
    for b in range(9, 17):
        p.perc(p.bar(b), 'bd:q r:q tri:q r:q', vel='mp')

    p.mark('the climb', p.bar(15))
    p.cue('climax', p.bar(17))

    # -- the close: two rit. bars, one long chord --------------------------
    p.mark('the close', p.bar(17))
    p.tempo(p.bar(17), 100, 'rit.')
    p.tempo(p.bar(18), 76)
    close = p.bar(17)
    p.add('vc', close, '(C3 G3):w (C3 G3):w', vel='mf', gate=1.0)
    p.add('vla', close, '(Eb4 G4):w (Eb4 G4):w', vel='mf', gate=1.0)
    p.add('vln2', close, 'C5:w C5:w', vel='mf', gate=1.0)
    p.add('vln1', close, 'G5:w Eb5:w', vel='mf', gate=1.0)
    for inst in ('vc', 'vla', 'vln2', 'vln1'):
        p.hairpin(inst, close, p.bar(19) - 0.5, 105, 30)
    figures.harp_arp(p, 'hp', ['C2', 'G2', 'C3', 'G3', 'C4', 'Eb4', 'G4', 'C5'],
                     close, vel='p')
    p.perc(close, 'tamtam:w', vel='pp')
    return p


# ================================================================ blues

CHART = ['F7', 'Bb7', 'F7', 'F7', 'Bb7', 'Bb7', 'F7', 'F7',
         'C7', 'Bb7', 'F7', ('C7', 'F7')]

CORNET_CHORUS = [
    B('r:q C5:e D5:e F5:q D5:e F5:e A5:h. F5:q '
      'G5:e F5:e D5:e C5:e D5:q F5:q r:h r:q C5:q', 4),
    B('Bb4:e D5:e F5:q Ab5:q G5:e F5:e G5:e F5:e D5:e Bb4:e C5:h '
      'A5:q. F5:e A5:q C6:q A5:h F5:h', 4),
    B('G5:q E5:q G5:e A5:e G5:e E5:e F5:q D5:q F5:e G5:e F5:e D5:e '
      'C5:h. A4:q r:w', 4),
]

CLARINET_CHORUS = [
    B('r:h C6:e A5:e F5:e A5:e C6:q A5:e F5:e A5:h '
      'F5:e A5:e C6:e Eb6:e D6:q C6:q A5:h r:h', 4),
    B('D6:q Bb5:e G5:e Bb5:q D6:q F6:h. D6:q '
      'C6:e Bb5:e A5:e G5:e A5:q C6:q A5:w', 4),
    B('G5:q E5:e G5:e Bb5:q C6:q Bb5:e A5:e F5:e D5:e F5:h '
      'A5:h C6:h r:w', 4),
]


def two_beat_bass(p, inst, chart, bar0, nbars, lo='E1', hi='Bb2', vel=92):
    """Roots and fifths, quarter-note walkup into each 4-bar phrase turn."""
    prev = None
    for b in range(nbars):
        root_pc, bass_pc, pcs = parse_chord(chord_at(chart, b))
        root = fit(bass_pc, lo, hi, near=prev)
        t = p.bar(bar0 + b)
        if b % 4 == 3 and b < nbars - 1:
            nxt = fit(parse_chord(chord_at(chart, b + 1))[1], lo, hi, near=root)
            approach = nxt + (1 if nxt < root else -1)
            steps = [root, fit(pcs[1], lo, hi, near=root),
                     fit(pcs[2], lo, hi, near=nxt), approach]
            for i, q in enumerate(steps):
                p.note(inst, t + i, q, 0.8, vel=vel - 4 + 3 * i)
        else:
            fifth = fit((root_pc + 7) % 12, lo, hi, near=root)
            p.note(inst, t, root, 0.85, vel=vel)
            p.note(inst, t + 2, fifth, 0.85, vel=vel - 6)
        prev = root


def comp_banjo(p, chart, bar0, nbars, vel=62):
    for b in range(nbars):
        for beat in range(4):
            sym = chord_at(chart, b, 0 if beat < 2 else 1)
            v = voicing(sym, 50, 64, near=57)
            figures.strum(p, 'banjo', v, p.bar(bar0 + b, beat), 0.4,
                          vel + (9 if beat % 2 else 0), spread=0.018)


def swing_drums(p, bar0, nbars, vel=76):
    for b in range(nbars):
        t = p.bar(bar0 + b)
        p.perc(t, 'kick:q sn:q kick:q sn:q', vel=vel)
        if p.rng.random() < 0.4:
            p.perc(t + 1.5, 'wbh:e', vel=vel - 18)
        if b % 4 == 3:
            figures.press_roll(p, t + 4.0, vel + 14)


def blues_etude() -> Piece:
    p = Piece(dixieland(), seed=1924, title='Étude II — Scratch Blues')
    p.tempo(0, 152, 'easy swing')

    p.mark('intro', 0)                          # bars 1-4: vamp in
    two_beat_bass(p, 'tuba', ['F7'], 1, 4)
    comp_banjo(p, ['F7'], 1, 4, vel=56)
    swing_drums(p, 3, 2, vel=66)

    p.mark('chorus 1 — cornet', p.bar(5))       # bars 5-16
    two_beat_bass(p, 'tuba', CHART, 5, 12)
    comp_banjo(p, CHART, 5, 12)
    swing_drums(p, 5, 12)
    for i, phrase in enumerate(CORNET_CHORUS):
        p.add('cornet', p.bar(5 + 4 * i), phrase, vel='f')
    figures.smear_into(p, 'cornet', 'A5', p.bar(6), 86)
    figures.scoop(p, 'cornet', p.bar(7, 1.5))
    figures.falloff(p, 'cornet', 'C6', p.bar(12, 2.5), 96)

    p.mark('chorus 2 — clarinet over the top', p.bar(17))   # bars 17-28
    two_beat_bass(p, 'tuba', CHART, 17, 12)
    comp_banjo(p, CHART, 17, 12, vel=68)
    swing_drums(p, 17, 12, vel=84)
    for i, phrase in enumerate(CLARINET_CHORUS):
        p.add('clarinet', p.bar(17 + 4 * i), phrase, vel='f')
    figures.curl(p, 'clarinet', 'C6', p.bar(18, 2.0), 92)
    figures.trill(p, 'clarinet', 'F6', p.bar(22, 0.0), 2.0, 90, unit=0.125)
    prev = 52
    for b in range(12):                          # trombone guide tones
        _, _, pcs = parse_chord(chord_at(CHART, b))
        guide = fit(p.rng.choice((pcs[1], pcs[3 % len(pcs)])), 45, 62, near=prev)
        t = p.bar(17 + b)
        p.note('tbn', t, guide, 2.8, vel=68)
        if b % 4 == 0:
            figures.scoop(p, 'tbn', t)
        prev = guide

    p.mark('the tag', p.bar(29))                 # bars 29-30: stop-time out
    p.cue('tag', p.bar(29))
    for beat in (0.0, 2.0):
        t = p.bar(29, beat)
        figures.strum(p, 'banjo', voicing('F7', 50, 64), t, 0.5, 84)
        p.note('tuba', t, 'F1', 0.6, vel=100)
        p.perc(t, 'kick:e sn:e', vel=92)
    p.add('cornet', p.bar(29, 3.0), 'C5:e D5:e F5:e G5:e A5:q. F5:e F5:h',
          vel='ff')
    t_end = p.bar(30, 2.0)
    figures.strum(p, 'banjo', voicing('F6', 50, 66), t_end, 2.0, 88)
    p.note('tuba', t_end, 'F1', 2.0, vel=104)
    p.note('tbn', t_end, 'A3', 2.0, vel=88)
    p.note('clarinet', t_end, 'A5', 2.0, vel=84)
    p.note('cornet', t_end, 'F5', 2.0, vel=92)
    p.perc(t_end, 'crash:h', vel=96)
    return p


# ================================================================ build

def main(outdir=None):
    outdir = outdir or os.path.join(os.path.dirname(__file__), 'demo_output')
    os.makedirs(outdir, exist_ok=True)
    for piece, fname, swing in ((orchestra_etude(), 'orchestra_etude', None),
                                (blues_etude(), 'blues_etude', 0.62)):
        mid = os.path.join(outdir, f'{fname}.mid')
        piece.write(mid, swing=swing)
        piece.write_marks(os.path.join(outdir, f'{fname}.marks.json'))
        assess.pianoroll(piece, os.path.join(outdir, f'{fname}.png'))
        ok = assess.report(piece)
        print(midi_report(mid))
        print(f'{"clean" if ok else "RANGE PROBLEMS"} — wrote {mid}\n')


if __name__ == '__main__':
    main()
