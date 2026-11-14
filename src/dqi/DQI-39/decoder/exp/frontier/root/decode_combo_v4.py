"""Combined exact front half with cached initialized GF4096 producers."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_combo_v3
import decode_cached12
import decode_basic18
decode = decode_cached12.install(decode_combo_v3.decode)
decode = decode_basic18.install(decode)
for name in ('convert_safe', 'baseline'):
    assert decode.__globals__[name] is decode_combo_v3.decode.__globals__[name]
