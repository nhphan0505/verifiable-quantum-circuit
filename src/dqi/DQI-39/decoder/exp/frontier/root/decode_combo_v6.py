"""Exact front-half combination including flag-free scalar caches."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_combo_v5
import decode_flagfree_cached
import decode_stream12_cached

decode = decode_flagfree_cached.install(decode_combo_v5.decode)
decode = decode_stream12_cached.install(decode)
for name in ('convert_safe', 'baseline'):
    assert decode.__globals__[name] is decode_combo_v5.decode.__globals__[name]
