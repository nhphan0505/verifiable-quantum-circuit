"""q26's decoder with the pole flags carried along the return, at 892 qubits.

The carry goes on q22's nodes first, so that the round's patches wrap it, as
decode_carry.py does on q22. All paths are relative to this file.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / "exp/round7/root"), str(ROOT / "exp/next/carry")]
import decode_next_best as _base
from flag_carry import install
CARRY_LOG = install(_base.decode)
from decode_trace_merged_completed_return import decode

__all__ = ["decode"]
