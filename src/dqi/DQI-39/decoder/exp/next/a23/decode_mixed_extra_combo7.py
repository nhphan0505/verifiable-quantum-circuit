"""Combo7 plus seven certified189T mixed-place homogeneous product charts."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import decode_mixed_combo7 as prior
from joint_mixed_extra import install
EXTRA_MIXED_CHAIN_EDITS=install(prior.decode)
decode=prior.decode
