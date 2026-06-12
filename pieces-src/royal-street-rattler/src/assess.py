#!/usr/bin/env python3
"""Self-assessment: section-by-section energy arc, clipping, swing verification."""
import os, wave
import numpy as np
import mido

HERE = os.path.dirname(os.path.abspath(__file__))
WAV = os.path.join(HERE, '..', 'output', 'royal_street_rattler.wav')
MID = os.path.join(HERE, '..', 'output', 'royal_street_rattler.mid')

TEMPO = 198
SECTIONS = [
    (0, 'Intro'), (8, 'Head 1'), (24, 'Head 2'), (40, 'B strain'),
    (56, 'Head 3'), (72, 'Modulation'), (76, 'Trio theme'), (92, 'Clarinet solo'),
    (108, 'Sax solo'), (124, 'Trumpet solo'), (140, 'Drum break'), (144, 'Shout'),
    (160, 'Out chorus'), (176, 'Tag'), (185, 'END'),
]

with wave.open(WAV) as w:
    sr = w.getframerate()
    n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32)
    data = data.reshape(-1, w.getnchannels()).mean(axis=1) / 32768.0

dur = n / sr
print(f"audio: {dur:.1f}s ({int(dur//60)}:{dur%60:04.1f}), sr={sr}")
peak = np.abs(data).max()
print(f"peak amplitude: {peak:.3f} {'(CLIPPING!)' if peak > 0.99 else '(clean)'}\n")

print("Section energy arc (RMS, normalized to loudest):")
spb = 60 / TEMPO
rms_vals = []
for i in range(len(SECTIONS) - 1):
    b0, name = SECTIONS[i]
    b1 = SECTIONS[i + 1][0]
    s0, s1 = int(b0 * 4 * spb * sr), min(int(b1 * 4 * spb * sr), len(data))
    seg = data[s0:s1]
    rms = float(np.sqrt((seg ** 2).mean())) if len(seg) else 0.0
    rms_vals.append((name, rms))
mx = max(r for _, r in rms_vals)
for name, r in rms_vals:
    bar = '#' * int(40 * r / mx)
    print(f"  {name:<14} {r/mx:5.2f}  {bar}")

# swing verification: offbeat eighth placement in the trumpet track
print("\nSwing check (trumpet note onsets, fractional beat position):")
mid = mido.MidiFile(MID)
tpb = mid.ticks_per_beat
fracs = {}
for track in mid.tracks:
    if 'Trumpet' not in (track.name or ''):
        continue
    t = 0
    for msg in track:
        t += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            f = round((t / tpb) % 1, 2)
            bucket = round(f * 20) / 20
            fracs[bucket] = fracs.get(bucket, 0) + 1
for k in sorted(fracs):
    if fracs[k] > 5:
        print(f"  beat+{k:.2f}: {fracs[k]} notes")
