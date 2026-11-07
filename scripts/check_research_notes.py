"""Require a nonempty note.md beside every research resource before merge.

Run python scripts/check_research_notes.py from any directory. This validates
all four tracks, independent of branch name; raw-only local drafts may fail it.
Scientific accuracy and readiness still require independent review.
"""

from pathlib import Path


def check(root):
    errors = []
    for track in ('invsqrt', 'dqi', 'dfthcsos', 'shared'):
        for kind in ('papers', 'discussions'):
            parent = root / 'research' / track / kind
            if not parent.is_dir():
                continue
            for source in parent.iterdir():
                if source.name.startswith('.'):
                    continue
                if not source.is_dir():
                    errors.append(f'{source.relative_to(root)}: resource must be inside a source directory with note.md')
                    continue
                note = source / 'note.md'
                if not note.is_file() or note.is_symlink():
                    errors.append(f'{source.relative_to(root)}: missing regular note.md; PDF/link-only resources cannot merge')
                    continue
                try:
                    if not note.read_text(encoding='utf-8-sig').strip():
                        errors.append(f'{note.relative_to(root)}: note.md is empty')
                except (UnicodeError, OSError) as exc:
                    errors.append(f'{note.relative_to(root)}: cannot read note.md: {exc}')
    return errors


if __name__ == '__main__':
    problems = check(Path(__file__).resolve().parents[1])
    for problem in problems:
        print(f'ERROR: {problem}')
    print(f'Research note checks: {len(problems)} error(s)')
    raise SystemExit(bool(problems))
