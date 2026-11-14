"""Exact front half with low-Taylor full-fold reverses."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'a11')]
import decode_combo_v8
import decode_low_crt

decode = decode_low_crt.install(decode_combo_v8.decode)
for name in ('convert_safe', 'baseline'):
    assert decode.__globals__[name] is decode_combo_v8.decode.__globals__[name]
