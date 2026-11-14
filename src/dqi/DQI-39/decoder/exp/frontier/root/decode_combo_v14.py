"""Exact front half with fused quantum/classical retained-norm characters."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'a16')]
import decode_combo_v13
import decode_partial_many

decode = decode_partial_many.install(decode_combo_v13.decode)
for name in ('synthesize', 'convert_safe', 'baseline'):
    assert decode.__globals__[name] is decode_combo_v13.decode.__globals__[name]
