"""Tempo map + meter map: beats <-> seconds <-> bars.

All positions are absolute beats (quarter notes) from 0. The tempo map
converts beats to real seconds (every lineage reimplemented this; here it
lives once). The meter map makes bar addressing meter-aware, so 3/4, 6/8,
and meter changes all work — place meter changes on bar boundaries.
"""


class Timeline:
    def __init__(self, bpm: float = 120.0, meter=(4, 4)):
        self._tempi = {0.0: (bpm, None)}      # beat -> (bpm, text)
        self._meters = {0.0: meter}           # beat -> (num, den)

    # -- authoring ---------------------------------------------------------
    def tempo(self, beat: float, bpm: float, text: str | None = None):
        self._tempi[float(beat)] = (float(bpm), text)

    def meter(self, beat: float, num: int, den: int):
        self._meters[float(beat)] = (num, den)

    # -- queries -----------------------------------------------------------
    def tempi(self):
        """Sorted [(beat, bpm, text)]."""
        return [(b, v[0], v[1]) for b, v in sorted(self._tempi.items())]

    def meters(self):
        """Sorted [(beat, num, den)]."""
        return [(b, num, den) for b, (num, den) in sorted(self._meters.items())]

    def bpm_at(self, beat: float) -> float:
        bpm = self.tempi()[0][1]
        for b, v, _ in self.tempi():
            if b > beat:
                break
            bpm = v
        return bpm

    def seconds(self, beat: float) -> float:
        """Real time of an absolute beat under the tempo map."""
        segs = self.tempi()
        sec = 0.0
        for i, (b0, bpm, _) in enumerate(segs):
            b1 = segs[i + 1][0] if i + 1 < len(segs) else None
            if b1 is None or beat <= b1:
                return sec + max(0.0, beat - b0) * 60.0 / bpm
            sec += (b1 - b0) * 60.0 / bpm
        return sec

    def bar_start(self, bar: int) -> float:
        """Absolute beat where 1-indexed `bar` begins, honoring meter changes."""
        segs = self.meters()
        remaining = bar - 1
        for i, (b0, num, den) in enumerate(segs):
            bar_len = num * 4.0 / den
            b1 = segs[i + 1][0] if i + 1 < len(segs) else None
            if b1 is None:
                return b0 + remaining * bar_len
            n_bars = int(round((b1 - b0) / bar_len))
            if remaining < n_bars:
                return b0 + remaining * bar_len
            remaining -= n_bars
        raise AssertionError('unreachable')

    def bar(self, bar: int, beat: float = 0.0) -> float:
        """(bar, beats-within-bar) -> absolute beat. Bars are 1-indexed."""
        return self.bar_start(bar) + beat

    def bar_length(self, bar: int) -> float:
        b = self.bar_start(bar)
        num, den = self.meters()[0][1:]
        for b0, n, d in self.meters():
            if b0 > b:
                break
            num, den = n, d
        return num * 4.0 / den
