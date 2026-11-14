"""Completed coefficient return with the whole relative-trace phase return."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(ROOT/'exp/round7/a21'), str(ROOT)]
import decode_trace_merged_product_companion as matched_normalization
from decode_norm_deferred_flag_unsynthesis import decode
INSTALLATION = matched_normalization.INSTALLATION
