"""Final exact Q898 composition with one additional shared evaluation chart."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(ROOT / 'exp/next/a20')]
import decode_combo6 as prior
from conjugate_extra import install
EXTRA_CHAIN_EDITS = install(prior.decode)
decode = prior.decode
