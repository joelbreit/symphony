#!/usr/bin/env python3
"""Self-assessment: pianoroll + measured dynamic arc vs. the designed one."""
import json
import wave
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import music21 as m21

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
EVENTS = json.loads((OUT / "events.json").read_text())

SECTIONS = [(1, "shrug"), (5, "pile I"), (9, "pile II"), (13, "SHOUT"), (21, "WAIL"),
            (29, "floor"), (33, "bone solo"), (45, "cornet solo"), (57, "clar solo"),
            (69, "ARGUMENT"), (81, "STOMP"), (93, "collapse"), (97, "RIOT"), (121, "wink"),
            (125, "")]
TEMPI = [(1, 160), (81, 156), (97, 164)]   # bar -> bpm

COLORS = dict(cornet="#d62728", clarinet="#9467bd", sax="#2ca02c", bone1="#ff7f0e",
              bone2="#bc6c25", sousa="#1f77b4", banjo="#7f7f7f", drums="#17becf")

def bar_to_sec(bar):
    """Absolute seconds at the start of `bar` (1-indexed), honoring tempo changes."""
    t, prev_bar, prev_bpm = 0.0, 1, TEMPI[0][1]
    for b, bpm in TEMPI[1:] + [(bar, None)]:
        bb = min(b, bar)
        t += (bb - prev_bar) * 4 * 60.0 / prev_bpm
        if bb == bar:
            return t
        prev_bar, prev_bpm = b, bpm
    return t

def midi_of(p):
    return p if isinstance(p, int) else m21.pitch.Pitch(p).midi

# ---------------------------------------------------------------- pianoroll
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(20, 11), sharex=True,
                              gridspec_kw=dict(height_ratios=[3, 1], hspace=0.06))
for name, evs in EVENTS.items():
    if name == "drums":
        continue
    for e in evs:
        for p in e["pitches"]:
            ax.plot([e["off"] / 4 + 1, (e["off"] + e["dur"]) / 4 + 1],
                    [midi_of(p)] * 2, lw=1.6, color=COLORS[name],
                    alpha=0.35 + 0.5 * e["vel"] / 122, solid_capstyle="butt")
for b, label in SECTIONS[:-1]:
    ax.axvline(b, color="k", lw=0.6, alpha=0.35)
    ax.text(b + 0.15, 89, label, fontsize=9, rotation=0, va="bottom", alpha=0.8)
ax.set_ylabel("MIDI pitch")
ax.set_ylim(24, 94)
ax.set_xlim(1, 125)
ax.set_title("High Street Riot — pianoroll (color = instrument, opacity = velocity)")
handles = [plt.Line2D([0], [0], color=c, lw=3, label=n) for n, c in COLORS.items() if n != "drums"]
ax.legend(handles=handles, loc="lower right", ncol=4, fontsize=9, framealpha=0.9)

# ------------------------------------------------- measured loudness envelope
w = wave.open(str(OUT / "high_street_riot.wav"))
sr, nf = w.getframerate(), w.getnframes()
sig = np.frombuffer(w.readframes(nf), dtype=np.int16).reshape(-1, 2).mean(axis=1) / 32768
win = int(sr * 0.25)
nwin = len(sig) // win
rms = np.sqrt((sig[: nwin * win].reshape(-1, win) ** 2).mean(axis=1))
db = 20 * np.log10(np.maximum(rms, 1e-6))
tt = np.arange(nwin) * 0.25
# map seconds -> bar for the shared x axis
bar_edges = [bar_to_sec(b) for b in range(1, 126)]
bars_axis = np.interp(tt, bar_edges, np.arange(1, 126))
ax2.fill_between(bars_axis, -60, db, color="#444", alpha=0.85)
for b, label in SECTIONS[:-1]:
    ax2.axvline(b, color="k", lw=0.6, alpha=0.35)
ax2.set_ylim(-48, -6)
ax2.set_ylabel("RMS dBFS")
ax2.set_xlabel("bar")
fig.savefig(OUT / "pianoroll.png", dpi=110, bbox_inches="tight")
print("wrote output/pianoroll.png")

# ----------------------------------------------------------- numeric report
print("\nsection loudness (mean RMS dBFS):")
for (b0, label), (b1, _) in zip(SECTIONS[:-1], SECTIONS[1:]):
    s0, s1 = bar_to_sec(b0), bar_to_sec(b1)
    m = (tt >= s0) & (tt < s1)
    if m.any():
        print(f"  {label:12s} bars {b0:>3}-{b1 - 1:<3} {db[m].mean():6.1f} dB")

# sousa top = B-3: practical sousaphone ceiling; the D-riff's brief A3 at the
# climaxes is the tuba player's own wail, and it's earned
RANGES = dict(cornet=("F#3", "D6"), clarinet=("E3", "G6"), sax=("A-2", "E-5"),
              bone1=("E2", "B-4"), bone2=("E2", "B-4"), sousa=("E1", "B-3"),
              banjo=("C3", "C6"))
print("\nrange check:")
ok = True
for name, evs in EVENTS.items():
    if name == "drums":
        continue
    mm = [midi_of(p) for e in evs for p in e["pitches"]]
    lo, hi = min(mm), max(mm)
    rlo, rhi = (m21.pitch.Pitch(x).midi for x in RANGES[name])
    flag = "OK " if (lo >= rlo and hi <= rhi) else "OUT"
    if flag == "OUT":
        ok = False
    print(f"  {flag} {name:9s} {m21.pitch.Pitch(midi=lo).nameWithOctave:>4} .. "
          f"{m21.pitch.Pitch(midi=hi).nameWithOctave:<4} (limit {RANGES[name][0]}..{RANGES[name][1]})")
print("\nall ranges OK" if ok else "\nRANGE VIOLATIONS — fix before shipping")
