"""Load the supplied prior helpers, with only the four audited entry changes.

This module avoids duplicating the supplied arithmetic in the delivered entry.
All newly developed arithmetic is installed separately on a private graph.
"""
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = KIT_ROOT / 'prior/decode_backhalf_q7.py'


def _carried_source():
    source = SOURCE_PATH.read_text()
    edits = (
        ('ROOT = Path(__file__).resolve().parent', 'ROOT = KIT_ROOT'),
        ("BASE_DIR/'decode_retimed.py'", "BASE_DIR/'decode_combo.py'"),
        ('baseline = SimpleNamespace(**dict(vars(base.ref.baseline), scan=scan))',
         "baseline = SimpleNamespace(**dict(vars(base.decode.__globals__['baseline']), scan=scan))"),
        ('\ndecode = install_factorized_boundary(decode)\n', '\n'),
    )
    for before, after in edits:
        assert source.count(before) == 1, before
        source = source.replace(before, after)
    return source


exec(compile(_carried_source(), str(SOURCE_PATH), 'exec'), globals())
