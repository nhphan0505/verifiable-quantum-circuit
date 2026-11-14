"""Q898 candidate: borrowed Frobenius source, actual chain tensor, full cache.

Each installed component preserves the completed map and its character
interface. Whole checks determine the combined simultaneous width.
"""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(ROOT / 'exp/next/a19'),
               str(ROOT / 'exp/next/a20'), str(ROOT / 'exp/next/a03')]
import decode_frobenius_cap898 as prior
from conjugate_joint import install as install_chain
from install_cache_schedule import install as install_partial
from install_full_cache import install as install_full

CHAIN_EDITS = install_chain(prior.decode)
PARTIAL_EDITS = install_partial(prior.decode, forward_levels=(5,),
                               reverse_kinds={11: 't6', 5: 't6'})
FULL_EDITS, FULL_COUNTS = install_full(prior.decode, levels=(8,))
decode = prior.decode
