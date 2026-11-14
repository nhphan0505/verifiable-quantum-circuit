"""Exact front half with all current accepted arithmetic and replay changes."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'a11'), str(HERE.parent/'a12')]
import decode_combo_v9
import decode_inverse_retained
import decode_outer_alias_constant
import decode_virtual_leader
import decode_outer35
import decode_companion_preserve

decode = decode_inverse_retained.install(decode_combo_v9.decode)
decode = decode_outer_alias_constant.install(decode)
decode = decode_virtual_leader.install(decode)
decode = decode_outer35.install(decode)
decode = decode_companion_preserve.install(decode, with_norm=True, ceiling=889)
for name in ('convert_safe', 'baseline'):
    assert decode.__globals__[name] is decode_combo_v9.decode.__globals__[name]
