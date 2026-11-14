"""Exact front half with the narrow isotopy scalar producer."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_combo_v6
import decode_cached_leaf20
decode = decode_cached_leaf20.install(decode_combo_v6.decode)
for name in ('convert_safe', 'baseline'):
    assert decode.__globals__[name] is decode_combo_v6.decode.__globals__[name]
