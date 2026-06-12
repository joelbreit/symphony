"""Pipeline smoke test: instruments, tempo changes, velocities, percussion channel."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import Orchestra, write_midi, midi_report, check_ranges, trem, arp

o = Orchestra()
o.timesig(0, '4/4')
o.tempo(0, 100, 'Test moderato')

# bar 1-2: C minor chord swell in strings, flute scale, timpani roll
o.add('vln1', 0, 'G4:w G4:w', vel='p', vel_end='ff')
o.add('vln2', 0, '(Eb4 C4):w (Eb4 C4):w', vel='p', vel_end='ff')
o.add('vla', 0, 'C4:w G3:w', vel='p', vel_end='ff')
o.add('vc', 0, 'C3:w C3:w', vel='p', vel_end='ff')
o.add('cb', 0, 'C2:w C2:w', vel='p', vel_end='ff')
o.add('fl', 0, 'C5:e D5:e Eb5:e F5:e G5:e Ab5:e B5:e C6:e C6:h r:h', vel='mf')
o.add('timp', 0, trem('C3', 8.0, 0.25), vel='pp', vel_end='f')

# bar 3 (tempo change): brass chord + crash
o.tempo(8, 140, 'Test allegro')
o.add('hn', 8, '(C4 Eb4 G4):h', vel='ff')
o.add('tpt', 8, '(C5 G5):h', vel='ff')
o.add('tbn', 8, '(C3 G3 C4):h', vel='ff')
o.perc(8, 'crash:h', vel='ff')
o.add('hp', 8, arp(['C3', 'G3', 'C4', 'Eb4', 'G4', 'C5'], 0.25, 4.0), vel='mf')
o.add('cel', 10, 'G5:q C6:q Eb6:q D6:q', vel='mp')
o.add('ob', 10, 'Eb5:q D5:q', vel='mf')
o.add('cl', 10, 'C5:q B4:q', vel='mf')
o.add('bsn', 10, 'C3:h', vel='mf')

os.makedirs('output', exist_ok=True)
path = write_midi(o, 'output/smoke.mid')
print(midi_report(path))
probs = check_ranges(o)
print('range problems:', probs if probs else 'none')
print('end offset (ql):', o.end())
