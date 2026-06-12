"""Deeper validation of the assembled symphony.

Gates: duration, channel/program integrity, and a coarse dynamic-arc
profile (mean velocity + note density per 30s bucket) to confirm the
climaxes and hushes land where the form says they should.
"""
import sys

import mido

def profile(path):
    mid = mido.MidiFile(path)
    print(f'{path}: {mid.length/60:.2f} min')
    chans = set()
    progs = {}
    events = []          # (abs_seconds, velocity)
    for tr in mid.tracks:
        t_ticks = 0
        for m in tr:
            t_ticks += m.time
            if m.type == 'program_change':
                progs.setdefault(m.channel, set()).add(m.program)
            if hasattr(m, 'channel'):
                chans.add(m.channel)
    # absolute seconds need merged tempo map: iterate the file (mido does this)
    t = 0.0
    for m in mid:
        t += m.time
        if m.type == 'note_on' and m.velocity > 0:
            events.append((t, m.velocity))
    print(f'channels used: {sorted(chans)} ({len(chans)})')
    print(f'programs by channel: ' + ', '.join(f'{c}:{sorted(p)}' for c, p in sorted(progs.items())))
    print(f'total note-ons: {len(events)}')
    print('\ndynamic arc (30s buckets): time  notes/s  mean-vel')
    bucket = 30.0
    n_buckets = int(t / bucket) + 1
    for i in range(n_buckets):
        sel = [v for (tt, v) in events if i * bucket <= tt < (i + 1) * bucket]
        if not sel:
            print(f'  {i*bucket/60:5.1f}m  silent')
            continue
        bar = '#' * int(sum(sel) / len(sel) / 4)
        print(f'  {i*bucket/60:5.1f}m  {len(sel)/bucket:6.1f}  {sum(sel)/len(sel):5.1f}  {bar}')

if __name__ == '__main__':
    profile(sys.argv[1] if len(sys.argv) > 1 else 'output/symphony_full.mid')
