"""Accepted port of the exact substitutions plus exact synthesis low products."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_subs_combined as base
import reverse_exact as exact
from exp.fold_joint import kernel as fold
replacements=dict(base.replacements)
replacements[id(fold.low_product)]=exact.low_product
decode=base.xsub.private_rebind(base.base.decode,replacements)
trailing=base.edited(decode.__globals__['extraction'],
    'D=b.alloc_qubits(12);b.x(D[0]);b.cswap(pole,N,D)',
    'D=b.alloc_qubits(12);b.x(D[0]);b.cx(pole,N[0]);b.cx(pole,D[0])')
decode=base.xsub.clone(decode,dict(decode.__globals__,extraction=trailing))
