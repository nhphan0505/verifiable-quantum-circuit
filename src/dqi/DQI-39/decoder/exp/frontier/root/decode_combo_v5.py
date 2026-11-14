"""Combined exact front-half improvements after the second agent wave."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'a05'), str(HERE.parent/'a07')]
import decode_combo_v4
import decode_local_forward_sheared
import decode_quantum_inverse_phase
import decode_correction_and
import decode_prefix_gauge
import scalar_projection_multi
import scalar_projection12

decode = decode_local_forward_sheared.install(decode_combo_v4.decode)
decode = decode_quantum_inverse_phase.install(decode)
decode = decode_correction_and.install(decode)
decode = decode_prefix_gauge.install(decode)
decode = scalar_projection_multi.install(decode, {9:5, 10:4, 11:3, 12:2, 13:1})
decode = scalar_projection12.install(decode)
for name in ('convert_safe', 'baseline'):
    assert decode.__globals__[name] is decode_combo_v4.decode.__globals__[name]
