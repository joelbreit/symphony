#!/usr/bin/env python3
"""Did I break anything? — the check to run after touching `lib/`.

    .venv/bin/python tools/check_all.py

Three things, in the order they will bite you:

1. **The toolkit self-tests** (`python -m lib.tests`).
2. **Every lib-built piece still builds** — each piece's `src/compose.py`,
   run from its own directory, with its gates and range gates.
3. **And builds *the same*.** Every generator here is seeded and deterministic,
   so a rebuild that changes one byte of MIDI means a lib change altered
   somebody's finished music. That is the failure mode a test suite will not
   catch and a listener will: the published audio and the regenerated MIDI
   drift apart, and the web player's note highlighting slides off the sound.

Scores are checked separately by `tools/export_scores.py`, which re-engraves
every piece and reports the worst sync drift. Run that too when you touch
`lib/notation.py`.

The frozen music21/midiutil pieces (the-window, the-box-is-full,
high-street-riot, the-unfinished-spire, royal-street-rattler) are not built
here: they do not depend on `lib/` at all.
"""
import argparse
import hashlib
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / '.venv' / 'bin' / 'python'

# lib-built pieces: (slug, build script relative to the piece dir)
PIECES = [
    ('perigee', 'src/compose.py'),
    ('the-punch-line', 'src/compose.py'),
    ('cut-loose', 'src/compose.py'),
    ('majority-rules', 'src/compose.py'),
    ('still-turning', 'src/compose.py'),
]


def digest(d: pathlib.Path) -> dict:
    return {p.name: hashlib.md5(p.read_bytes()).hexdigest()
            for p in sorted(d.glob('*.mid'))}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--skip-tests', action='store_true')
    ap.add_argument('pieces', nargs='*', help='only these slugs')
    args = ap.parse_args()
    failures = []

    if not args.skip_tests:
        print('== lib self-tests')
        r = subprocess.run([str(PY), '-m', 'lib.tests'], cwd=ROOT,
                           capture_output=True, text=True)
        tail = (r.stdout or r.stderr).strip().splitlines()[-1:] or ['(no output)']
        print(f'   {tail[0]}')
        if r.returncode:
            failures.append('lib.tests')
            for line in (r.stdout or '').splitlines():
                if line.startswith('FAIL'):
                    print(f'   {line}')

    todo = [p for p in PIECES if not args.pieces or p[0] in args.pieces]
    print(f'\n== {len(todo)} lib-built piece(s)')
    for slug, script in todo:
        d = ROOT / 'pieces-src' / slug
        out = d / 'output'
        before = digest(out)
        r = subprocess.run([str(PY), script], cwd=d, capture_output=True,
                           text=True)
        after = digest(out)
        if r.returncode:
            failures.append(f'{slug} (build failed)')
            print(f'   FAIL  {slug}: build exited {r.returncode}')
            for line in (r.stdout or '').splitlines():
                if 'GATE' in line or 'OUT ' in line or 'error' in line:
                    print(f'         {line.strip()}')
            print(f'         {(r.stderr or "").strip().splitlines()[-1:]}')
            continue
        changed = [k for k in after if before.get(k) != after[k]]
        if not before:
            print(f'   ok    {slug}: built {len(after)} file(s) (nothing to '
                  f'compare against)')
        elif changed:
            failures.append(f'{slug} (output changed: {", ".join(changed)})')
            print(f'   DIFF  {slug}: {", ".join(changed)} changed — a lib '
                  f'change altered finished music. Re-render and re-package, '
                  f'or undo.')
        else:
            print(f'   ok    {slug}: {len(after)} file(s), byte-identical')

    print()
    if failures:
        print(f'{len(failures)} problem(s): ' + '; '.join(failures))
        return 1
    print('all clear — and run tools/export_scores.py if you touched notation')
    return 0


if __name__ == '__main__':
    sys.exit(main())
