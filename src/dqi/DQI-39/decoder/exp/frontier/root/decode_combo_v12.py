"""Exact front half with six-fresh inverse and paired inverse characters."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'a14'), str(HERE.parent/'a16')]
import decode_combo_v11
import decode_inverse20_12
import decode_pair

decode = decode_inverse20_12.install(decode_combo_v11.decode)
decode = decode_pair.install(decode)
for name in ('convert_safe', 'baseline'):
    assert decode.__globals__[name] is decode_combo_v11.decode.__globals__[name]
