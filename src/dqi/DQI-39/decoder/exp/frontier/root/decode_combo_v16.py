"""Exact front half with the additional scoped nonzero scalar stream."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'a17')]
import decode_combo_v15
import decode_nonzero19_stream

decode = decode_nonzero19_stream.install(decode_combo_v15.decode)
for name in ('synthesize', 'convert_safe', 'baseline'):
    assert decode.__globals__[name] is decode_combo_v15.decode.__globals__[name]
