"""Regenerate every piece's engraved score, from the repo root:

    .venv/bin/python tools/export_scores.py            # all of them
    .venv/bin/python tools/export_scores.py perigee    # just one

Runs each pieces-src/<slug>/export_score.py in its own directory (they use
relative output paths) and reports the sync drift each one prints. A piece
without an export_score.py has no score by design — the two midiutil pieces
have no symbolic layer to engrave from.

Run this after changing lib/notation.py or any piece's compose source, and
after `tools/midi_to_piece.py --force`, which rewrites the manifest.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / '.venv' / 'bin' / 'python'


def main():
    wanted = set(sys.argv[1:])
    scripts = sorted(ROOT.glob('pieces-src/*/export_score.py'))
    if wanted:
        scripts = [s for s in scripts if s.parent.name in wanted]
        missing = wanted - {s.parent.name for s in scripts}
        if missing:
            sys.exit(f'no export_score.py for: {", ".join(sorted(missing))}')

    failed = []
    for script in scripts:
        slug = script.parent.name
        print(f'--- {slug}')
        r = subprocess.run([str(PY), script.name], cwd=script.parent,
                           capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode:
            sys.stdout.write(r.stderr)
            failed.append(slug)

    print(f'\n{len(scripts) - len(failed)}/{len(scripts)} scores exported')
    if failed:
        sys.exit(f'failed: {", ".join(failed)}')


if __name__ == '__main__':
    main()
