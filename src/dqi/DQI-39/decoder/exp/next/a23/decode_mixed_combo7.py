"""Combo7 plus four exact189T mixed-place homogeneous product charts."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'exp/next/root')]
import decode_combo7 as prior
from joint_mixed import install
MIXED_CHAIN_EDITS=install(prior.decode)
decode=prior.decode
