#!/usr/bin/env python3
"""Piano-roll visualization of the piece for visual self-assessment."""
import os
import mido
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

HERE = os.path.dirname(os.path.abspath(__file__))
MID = os.path.join(HERE, '..', 'output', 'royal_street_rattler.mid')
PNG = os.path.join(HERE, '..', 'output', 'pianoroll.png')

COLORS = {
    'Trumpet (lead)': '#e63946',
    'Clarinet': '#f4a261',
    'Trombone (tailgate)': '#2a9d8f',
    'Tenor Sax': '#9b5de5',
    'Sousaphone': '#264653',
    'Banjo': '#a8a29a',
    'Drums': '#cdb4db',
}

SECTIONS = [
    (0, 'Intro'), (8, 'Head 1'), (24, 'Head 2'), (40, 'B strain'),
    (56, 'Head 3'), (72, 'Mod'), (76, 'Trio'), (92, 'Cl solo'),
    (108, 'Sax solo'), (124, 'Tpt solo'), (140, 'Drums'), (144, 'Shout'),
    (160, 'Out'), (176, 'Tag'),
]

mid = mido.MidiFile(MID)
tpb = mid.ticks_per_beat

fig, ax = plt.subplots(figsize=(22, 9))
for track in mid.tracks:
    name = track.name if track.name else 'Drums'
    color = COLORS.get(name, '#888888')
    t = 0
    active = {}
    for msg in track:
        t += msg.time
        beats = t / tpb
        if msg.type == 'note_on' and msg.velocity > 0:
            active[msg.note] = (beats, msg.velocity)
        elif msg.type in ('note_off', 'note_on'):
            if msg.note in active:
                start, vel = active.pop(msg.note)
                bar = start / 4
                if name == 'Drums':
                    ax.plot(bar, msg.note - 24, '.', color=color,
                            markersize=2, alpha=0.25 + 0.5 * vel / 127)
                else:
                    ax.barh(msg.note, (beats - start) / 4, left=bar, height=0.85,
                            color=color, alpha=0.35 + 0.6 * vel / 127, linewidth=0)

for (bar, label) in SECTIONS:
    ax.axvline(bar, color='#555', linewidth=0.6, alpha=0.5)
    ax.text(bar + 0.3, 99, label, fontsize=8, color='#333', rotation=0, va='top')

ax.set_xlim(0, 186)
ax.set_ylim(20, 100)
ax.set_xlabel('bar')
ax.set_ylabel('MIDI pitch')
ax.set_title('Royal Street Rattler — piano roll (drums shown low, dotted)')
handles = [mpatches.Patch(color=c, label=n) for n, c in COLORS.items()]
ax.legend(handles=handles, loc='lower right', fontsize=8, ncol=4)
ax.grid(axis='x', which='major', alpha=0.1)
plt.tight_layout()
plt.savefig(PNG, dpi=110)
print('wrote', os.path.abspath(PNG))
