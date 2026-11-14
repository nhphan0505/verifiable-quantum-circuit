"""Combined exact front half, including proved-nonzero consuming inverses."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
KIT_ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(HERE.parent / 'a03'), str(HERE.parent / 'a04'),
               str(KIT_ROOT / 'exp/r-main/narrow240')]
import decode_combo as supplied
import jet_norm6_front
import inverse_consume17_front
import nonzero_consume16
import decode_shared_correction_front
import decode_local_norm_partial
import decode_local_forward

decode = supplied.decode
for component in (jet_norm6_front, decode_shared_correction_front,
                  decode_local_norm_partial, decode_local_forward,
                  inverse_consume17_front, nonzero_consume16):
    decode = component.install(decode)
for name in ('convert_safe', 'baseline'):
    assert decode.__globals__[name] is supplied.decode.__globals__[name]
