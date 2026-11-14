"""Exact front half with the clipped-divider nonzero retained inverse."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'a14')]
import decode_combo_v12
import decode_retained19

decode = decode_retained19.install(decode_combo_v12.decode)
for name in ('extraction', 'convert_safe', 'baseline'):
    assert decode.__globals__[name] is decode_combo_v12.decode.__globals__[name]
