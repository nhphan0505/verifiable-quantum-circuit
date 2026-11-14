"""Exact front half with an additional initialized scalar inverse tier."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'a17')]
import decode_combo_v14
import decode_initialized19

decode = decode_initialized19.install(decode_combo_v14.decode)
for name in ('convert_safe', 'baseline'):
    assert decode.__globals__[name] is decode_combo_v14.decode.__globals__[name]
