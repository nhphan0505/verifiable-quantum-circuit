"""Exact front half with same-width initialized17 and linked-phase inverse tiers."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'a18'), str(HERE.parent/'a20')]
import decode_combo_v16
import decode_initialized17_retire_last
import initialized17_linked

wide = decode_initialized17_retire_last.install(decode_combo_v16.decode)
decode = initialized17_linked.install(wide)
for name in ('convert_safe', 'baseline', 'linear_words', 'matrix'):
    assert decode.__globals__[name] is decode_combo_v16.decode.__globals__[name]
