"""Exact front half with full polynomial folds and narrow scalar leaves."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / 'a08')]
import decode_combo_v7
import decode_fullfold
import preserve_streams

decode = decode_fullfold.install(decode_combo_v7.decode, prefix_gauge=True)
decode = preserve_streams.install(decode)
for name in ('convert_safe', 'baseline'):
    assert decode.__globals__[name] is decode_combo_v7.decode.__globals__[name]
