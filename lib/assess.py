"""Self-assessment: text report + pianoroll/dynamic-arc plots.

Merges the per-piece assessment scripts (riot's assess.py, spire's
analyze.py, the-window's validate.py) into one suite that reads a Piece
directly. Optionally overlays measured RMS loudness from a rendered WAV
(riot's closed feedback loop) under the designed arc.
"""

FAMILY_COLORS = {
    'winds': '#2a9d8f', 'brass': '#e76f51', 'strings': '#457b9d',
    'plucked': '#f4a261', 'keys': '#9b5de5', 'perc': '#7f7f7f',
    'synth': '#00b4d8', 'voice': '#e07a9e', 'other': '#888888',
}


def report(piece, out=print) -> bool:
    """Duration, tempo/section map, per-instrument ranges. True if clean."""
    from .pitch import pitch_name
    end = piece.end()
    dur = piece.seconds(end)
    out(f'{piece.title or "piece"}: {len(piece.notes)} notes, '
        f'{end:.1f} beats = {int(dur // 60)}:{dur % 60:04.1f}')
    tempi = piece.timeline.tempi()
    out('tempo map: ' + ', '.join(
        f'{bpm:g}bpm@{b:g}' + (f' ({txt})' if txt else '') for b, bpm, txt in tempi))
    if piece.marks:
        out('sections:')
        for label, b in sorted(piece.marks, key=lambda m: m[1]):
            s = piece.seconds(b)
            out(f'  {int(s // 60)}:{s % 60:04.1f}  beat {b:6.1f}  {label}')
    ok = True
    out('instruments:')
    for spec in piece.ensemble:
        notes = [n for n in piece.notes if n.inst == spec.key]
        if not notes:
            continue
        lo, hi = min(n.pitch for n in notes), max(n.pitch for n in notes)
        if spec.percussion:
            out(f'  OK  {spec.name:<18} {len(notes):5d} notes  (drum keys)')
            continue
        good = spec.lo <= lo and hi <= spec.hi
        ok = ok and good
        flag = 'OK ' if good else 'OUT'
        out(f'  {flag} {spec.name:<18} {len(notes):5d} notes  '
            f'{pitch_name(lo):>4}..{pitch_name(hi):<4} '
            f'(limit {pitch_name(spec.lo)}..{pitch_name(spec.hi)})')
    return ok


def pianoroll(piece, path: str, wav: str | None = None):
    """Pianoroll (family colors, opacity=velocity) over the dynamic arc.

    x-axis is real seconds via the tempo map. `wav`: optional rendered audio
    whose measured RMS is drawn under the designed arc for comparison.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    n_rows = 3 if wav else 2
    fig, axes = plt.subplots(n_rows, 1, figsize=(20, 10 if wav else 8),
                             sharex=True,
                             gridspec_kw=dict(height_ratios=[3] + [1] * (n_rows - 1),
                                              hspace=0.08))
    ax, ax_arc = axes[0], axes[1]

    for n in piece.notes:
        spec = piece.ensemble[n.inst]
        if spec.percussion:
            continue
        t0, t1 = piece.seconds(n.start), piece.seconds(n.start + n.dur)
        ax.plot([t0, t1], [n.pitch] * 2, lw=1.6,
                color=FAMILY_COLORS.get(spec.family, '#888'),
                alpha=0.3 + 0.55 * n.vel / 127, solid_capstyle='butt')
    pitches = [n.pitch for n in piece.notes
               if not piece.ensemble[n.inst].percussion] or [60]
    top = max(pitches) + 3
    for label, b in piece.marks:
        s = piece.seconds(b)
        for a in axes:
            a.axvline(s, color='k', lw=0.6, alpha=0.3)
        ax.text(s + 0.3, top, label, fontsize=8, va='bottom', alpha=0.8)
    ax.set_ylabel('MIDI pitch')
    ax.set_ylim(min(pitches) - 3, top + 4)
    ax.set_title(piece.title or 'piece')
    fams = {piece.ensemble[n.inst].family for n in piece.notes}
    ax.legend(handles=[plt.Line2D([0], [0], color=FAMILY_COLORS[f], lw=3, label=f)
                       for f in sorted(fams) if f in FAMILY_COLORS],
              loc='lower right', ncol=4, fontsize=8, framealpha=0.9)

    # designed arc: mean velocity + note density per 2s bucket
    end_s = piece.seconds(piece.end())
    starts = np.array([piece.seconds(n.start) for n in piece.notes])
    vels = np.array([n.vel for n in piece.notes])
    bins = np.arange(0.0, end_s + 2.0, 2.0)
    idx = np.digitize(starts, bins)
    mean_v = [vels[idx == i].mean() if (idx == i).any() else 0
              for i in range(1, len(bins))]
    dens = [(idx == i).sum() / 2.0 for i in range(1, len(bins))]
    ax_arc.fill_between(bins[:-1], mean_v, alpha=0.5, color='#e76f51',
                        label='mean velocity')
    ax_arc.plot(bins[:-1], np.array(dens) * 2, color='#457b9d', lw=1,
                label='notes/s ×2')
    ax_arc.set_ylabel('designed arc')
    ax_arc.legend(loc='upper left', fontsize=8)

    if wav:
        import wave as wavemod
        w = wavemod.open(wav)
        sr, nf, nch = w.getframerate(), w.getnframes(), w.getnchannels()
        sig = np.frombuffer(w.readframes(nf), dtype=np.int16)
        sig = sig.reshape(-1, nch).mean(axis=1) / 32768
        win = int(sr * 0.25)
        nwin = len(sig) // win
        rms = np.sqrt((sig[: nwin * win].reshape(-1, win) ** 2).mean(axis=1))
        db = 20 * np.log10(np.maximum(rms, 1e-6))
        axes[2].fill_between(np.arange(nwin) * 0.25, -60, db, color='#444', alpha=0.85)
        axes[2].set_ylim(-48, -6)
        axes[2].set_ylabel('measured dBFS')

    axes[-1].set_xlabel('seconds')
    axes[-1].set_xlim(0, end_s)
    fig.savefig(path, dpi=100, bbox_inches='tight')
    plt.close(fig)
    return path
