"""Whole decoder with normalized common-mask trace repayment."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(ROOT)]
import decode_next_best as prior
from trace_merged_product_companion import install
INSTALLATION = install(prior.decode)
decode = prior.decode
