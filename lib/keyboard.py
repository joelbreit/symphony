"""Keyboard playability: hand assignment, span and reach audit.

A piece for solo piano can claim to be playable or it can be checked. This
checks. Notes are grouped into onsets, each onset is split into a left and a
right hand (no crossing), and every hand is measured for the things that
actually stop a pianist:

  - **span** — the interval from the hand's lowest to highest note. A 9th is
    the practical ceiling for most hands; a 10th is a stretch a lot of
    players cannot make; beyond that it must be rolled.
  - **fingers** — more than five notes in one hand at one instant.
  - **reach** — how far a hand has to travel between consecutive onsets, in
    the real seconds the tempo map allows for the jump.

Assumptions, stated because they matter:

  - Only *onsets* are audited. A note already sounding is assumed to be held
    by the sustain pedal, not by a finger — true for pedalled writing, which
    is nearly all of it, and false for a held inner voice under moving
    fingers. The audit is a floor, not a proof.
  - Onsets closer together than `roll_gap` are one *gesture* — a rolled
    chord, a grace note, a spread octave. A gesture is never measured as a
    grab: the hand travels through it, so only the travel speed and a loose
    outer bound apply. This is the difference between "play these six notes
    at once" (often impossible) and "roll them" (usually easy).

    from lib import keyboard
    keyboard.report(piece)          # prints; returns True if clean
"""
from dataclasses import dataclass

from .pitch import pitch_name

# A hand's span, in semitones. Octave = 12.
COMFORTABLE = 12      # anyone
STRETCH = 14          # a 10th: many players, not all
IMPOSSIBLE = 15       # must be rolled or redistributed
ROLLED = 40           # outer bound on one rolled sweep: three octaves and a
                      # bit. A roll is not a grab — the hand travels through
                      # it — so what limits it is speed, checked separately.

MAX_FINGERS = 5

# Reach heuristic: a hand can cross this many semitones in this many seconds.
# Calibrated to a fast but reliable leap (two octaves in ~0.15 s); anything
# beyond is a flourish, not a guarantee.
REACH_SEMITONES_PER_SEC = 160.0
REACH_FREE = 12       # a hand shifts an octave almost instantly; below this
                      # distance the speed limit does not apply

# Onsets within this many seconds are one gesture (a roll, a grace, a spread
# octave) rather than two chords the hand has to travel between.
ROLL_GAP = 0.06


@dataclass
class Onset:
    beat: float
    seconds: float
    lh: list          # midi pitches, ascending
    rh: list


@dataclass
class Issue:
    kind: str         # 'span' | 'fingers' | 'reach'
    beat: float
    seconds: float
    hand: str         # 'L' | 'R'
    detail: str
    severity: str     # 'error' | 'warn'


def group_onsets(notes, tol: float = 0.03):
    """[(beat, [pitches])] — notes within `tol` beats of each other fold in."""
    out = []
    for n in sorted(notes, key=lambda n: (n.start, n.pitch)):
        if out and n.start - out[-1][0] <= tol:
            out[-1][1].append(n.pitch)
        else:
            out.append((n.start, [n.pitch]))
    return [(b, sorted(set(ps))) for b, ps in out]


def split_hands(pitches, prev_lh=None, prev_rh=None):
    """Split ascending `pitches` into (left, right) with no hand crossing.

    Every split point is scored; the best one keeps both spans legal, both
    hands under five fingers, and — as a tiebreak — near where the hands
    already were, so the assignment is continuous rather than flapping.
    """
    ps = sorted(pitches)
    if len(ps) == 1:
        # one note: give it to whichever hand is closer to it
        if prev_lh and prev_rh:
            dl = min(abs(ps[0] - p) for p in prev_lh)
            dr = min(abs(ps[0] - p) for p in prev_rh)
            return (ps, []) if dl <= dr else ([], ps)
        return (ps, []) if ps[0] < 60 else ([], ps)

    best, best_score = None, None
    for i in range(len(ps) + 1):
        lh, rh = ps[:i], ps[i:]
        spans = [(h[-1] - h[0]) if len(h) > 1 else 0 for h in (lh, rh)]
        counts = [len(lh), len(rh)]
        score = (
            sum(max(0, s - STRETCH) * 100 for s in spans)          # illegal spans
            + sum(max(0, c - MAX_FINGERS) * 100 for c in counts)   # too many fingers
            + sum(max(0, s - COMFORTABLE) * 3 for s in spans)      # stretches
            + _continuity_cost(lh, rh, prev_lh, prev_rh)
            + _register_bias(lh, rh)               # tiebreak only
        )
        if best_score is None or score < best_score:
            best, best_score = (lh, rh), score
    return best


def _continuity_cost(lh, rh, prev_lh, prev_rh):
    cost = 0.0
    for hand, prev in ((lh, prev_lh), (rh, prev_rh)):
        if hand and prev:
            cost += abs(_center(hand) - _center(prev)) * 0.05
        elif hand and prev is not None and not prev:
            cost += 1.0        # a hand that was idle has to come back
    return cost


def _register_bias(lh, rh):
    """Tiny pull toward each hand's own side of middle C — decides ties at
    the start and for hands with no history, and is far too small to fight
    the continuity term once the hands are established."""
    return 0.001 * (sum(max(0, 60 - p) for p in rh)
                    + sum(max(0, p - 60) for p in lh))


def _center(pitches):
    return sum(pitches) / len(pitches)


def assign(piece, inst: str = None, tol: float = 0.03):
    """[Onset] for one instrument, hands assigned in time order."""
    if inst is None:
        inst = next(i.key for i in piece.ensemble if not i.percussion)
    notes = [n for n in piece.notes if n.inst == inst]
    out, prev_lh, prev_rh = [], None, None
    for beat, pitches in group_onsets(notes, tol):
        lh, rh = split_hands(pitches, prev_lh, prev_rh)
        out.append(Onset(beat, piece.seconds(beat), lh, rh))
        prev_lh, prev_rh = lh or prev_lh, rh or prev_rh
    return out


def gestures(onsets, roll_gap: float = ROLL_GAP) -> list:
    """Group onsets into gestures: a rolled chord is one motion, not five."""
    out = []
    for o in onsets:
        if out and o.seconds - out[-1][-1].seconds <= roll_gap:
            out[-1].append(o)
        else:
            out.append([o])
    return out


def audit(piece, inst: str = None, tol: float = 0.03,
          roll_gap: float = ROLL_GAP) -> list:
    """[Issue] — every span, finger-count and reach problem, in time order."""
    issues = []
    onsets = assign(piece, inst, tol)
    rolled = {id(o) for grp in gestures(onsets, roll_gap) if len(grp) > 1
              for o in grp}
    last = {'L': None, 'R': None}
    for o in onsets:
        for label, hand in (('L', o.lh), ('R', o.rh)):
            if not hand:
                continue
            span = hand[-1] - hand[0]
            if len(hand) > MAX_FINGERS:
                issues.append(Issue('fingers', o.beat, o.seconds, label,
                                    f'{len(hand)} notes at once', 'error'))
            if span >= IMPOSSIBLE:
                issues.append(Issue('span', o.beat, o.seconds, label,
                                    f'{span} semitones '
                                    f'({pitch_name(hand[0])}-{pitch_name(hand[-1])}), '
                                    f'{len(hand)} notes', 'error'))
            elif span > COMFORTABLE:
                issues.append(Issue('span', o.beat, o.seconds, label,
                                    f'{span} semitones '
                                    f'({pitch_name(hand[0])}-{pitch_name(hand[-1])})',
                                    'warn'))
            prev = last[label]
            if prev is not None:
                dt = o.seconds - prev[0]
                jump = max(0, hand[0] - prev[2], prev[1] - hand[-1])
                limit = max(REACH_FREE, REACH_SEMITONES_PER_SEC * dt)
                if dt > 0 and jump > limit:
                    issues.append(Issue(
                        'reach', o.beat, o.seconds, label,
                        f'{jump} semitones in {dt * 1000:.0f} ms '
                        f'(limit {limit:.0f})', 'error'))
            last[label] = (o.seconds, hand[0], hand[-1])

    for grp in gestures(onsets, roll_gap):
        if len(grp) < 2:
            continue
        for label in ('L', 'R'):
            notes = sorted(p for o in grp
                           for p in (o.lh if label == 'L' else o.rh))
            if notes and notes[-1] - notes[0] > ROLLED:
                issues.append(Issue('span', grp[0].beat, grp[0].seconds, label,
                                    f'one sweep across {notes[-1] - notes[0]} '
                                    f'semitones ({pitch_name(notes[0])}-'
                                    f'{pitch_name(notes[-1])})', 'error'))
    _ = rolled
    return sorted(issues, key=lambda i: i.seconds)


def report(piece, inst: str = None, tol: float = 0.03, out=print,
           max_lines: int = 12, roll_gap: float = ROLL_GAP) -> bool:
    """Print the audit. True if there are no errors (warnings are allowed)."""
    onsets = assign(piece, inst, tol)
    issues = audit(piece, inst, tol, roll_gap)
    errors = [i for i in issues if i.severity == 'error']
    warns = [i for i in issues if i.severity == 'warn']
    spans = [max((h[-1] - h[0]) if len(h) > 1 else 0 for h in (o.lh, o.rh))
             for o in onsets] or [0]
    out(f'playability: {len(onsets)} onsets, widest hand {max(spans)} semitones, '
        f'{len(errors)} errors, {len(warns)} stretches')
    for i in (errors + warns)[:max_lines]:
        out(f'  {i.severity:5s} {i.kind:7s} {i.hand}  '
            f'{int(i.seconds // 60)}:{i.seconds % 60:05.2f} (beat {i.beat:.2f})  '
            f'{i.detail}')
    if len(errors) + len(warns) > max_lines:
        out(f'  ... and {len(errors) + len(warns) - max_lines} more')
    return not errors
