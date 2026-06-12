"""Visual self-assessment: piano roll, velocity arc, instrument activity."""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from compose import build
from score import CHANNEL_NAMES, RANGES, PERC

FAMILY_COLORS = {
    0: "#2a9d8f", 1: "#2a9d8f", 2: "#2a9d8f", 3: "#2a9d8f",      # winds
    4: "#e76f51", 5: "#e76f51", 6: "#e76f51", 7: "#e76f51",      # brass
    8: "#7b2cbf", 9: "#7b2cbf",                                  # perc
    10: "#1d3557", 11: "#1d3557", 12: "#457b9d", 13: "#457b9d",  # strings
    14: "#457b9d", 15: "#f4a261",                                # harp/bells
}


def main():
    s, sections, end = build()
    out = os.path.join(os.path.dirname(__file__), "..", "out")

    # ---------------- piano roll
    fig, ax = plt.subplots(figsize=(22, 9))
    for ch, pitch, start, dur, vel in s.notes:
        if ch == PERC:
            continue
        ax.barh(pitch, dur, left=start, height=0.8,
                color=FAMILY_COLORS[ch], alpha=0.25 + 0.55 * vel / 127,
                linewidth=0)
    for name, beat in sections:
        ax.axvline(beat, color="#888", lw=0.7, ls="--")
        ax.text(beat + 1, 103, name, fontsize=8, rotation=0, va="bottom")
    ax.set_xlabel("beat"); ax.set_ylabel("MIDI pitch")
    ax.set_title("The Unfinished Spire — piano roll "
                 "(teal=winds, red=brass, blue=strings, orange=harp/bells)")
    ax.set_xlim(0, end); ax.set_ylim(20, 108)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "piano_roll.png"), dpi=85)

    # ---------------- velocity arc + density
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(22, 7), sharex=True)
    starts = np.array([n[2] for n in s.notes])
    vels = np.array([n[4] for n in s.notes])
    bins = np.arange(0, end + 4, 4)
    idx = np.digitize(starts, bins)
    mean_v = [vels[idx == i].mean() if (idx == i).any() else 0
              for i in range(1, len(bins))]
    max_v = [vels[idx == i].max() if (idx == i).any() else 0
             for i in range(1, len(bins))]
    dens = [(idx == i).sum() for i in range(1, len(bins))]
    ax1.fill_between(bins[:-1], mean_v, alpha=0.5, color="#e76f51",
                     label="mean velocity / bar")
    ax1.plot(bins[:-1], max_v, color="#9d0208", lw=1, label="max velocity")
    ax2.fill_between(bins[:-1], dens, alpha=0.6, color="#1d3557")
    ax2.set_ylabel("notes / bar"); ax1.set_ylabel("velocity")
    ax1.legend(loc="upper left", fontsize=8)
    for name, beat in sections:
        for ax in (ax1, ax2):
            ax.axvline(beat, color="#888", lw=0.7, ls="--")
        ax1.text(beat + 1, 122, name.split(".")[0], fontsize=8)
    ax1.set_title("dynamic arc (top) and texture density (bottom)")
    ax1.set_ylim(0, 130)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "dynamics.png"), dpi=85)

    # ---------------- per-instrument report
    print(f"{'instrument':<12} {'notes':>6}  {'lo..hi (allowed)':<26} busy-span")
    for ch in range(16):
        notes = [n for n in s.notes if n[0] == ch]
        if not notes:
            continue
        ps = [n[1] for n in notes]
        t0 = min(n[2] for n in notes); t1 = max(n[2] + n[3] for n in notes)
        if ch == PERC:
            rng = "(drum keys)"
        else:
            lo, hi = RANGES[ch]
            rng = f"{min(ps)}..{max(ps)} ({lo}..{hi})"
        print(f"{CHANNEL_NAMES[ch]:<12} {len(notes):>6}  {rng:<26} "
              f"beats {t0:5.0f}-{t1:5.0f}")
    print("plots saved: out/piano_roll.png, out/dynamics.png")


if __name__ == "__main__":
    main()
