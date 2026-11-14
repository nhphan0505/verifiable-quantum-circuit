"""Best complete decoder from the October 31 next-fall round.

The original decode_best.py remains the supplied reference.  All paths
are resolved relative to this file so the complete archive is portable.
"""
from pathlib import Path
import sys

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE / "exp" / "next" / "a23"))
from decode_mixed_extra_combo7 import decode

__all__ = ["decode"]
