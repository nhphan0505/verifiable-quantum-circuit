"""The supplied base, with only its Python graph-copy loader memoized.

No circuit function is substituted.  The two pure queries in private_rebind
depend only on an immutable filename/code object within one graph-copy call.
Memoizing them leaves all returned function graphs and emitted gates intact.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'playbook/kit'),
               str(ROOT / 'exp/r-main/narrow240'), str(ROOT)]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from loader_cache import install
install()

import decode_q8q9 as base
decode = base.decode
