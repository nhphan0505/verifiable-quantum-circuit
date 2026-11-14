"""Exact synthesis retention plus width-safe retained reverse chart v5."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_reverse as synth
import decode_subs_combined as kept
import retained_core_safe27 as retained

base, xsub = kept.base, kept.xsub
node = xsub.clone(retained.external_node_chain,
                 dict(retained.external_node_chain.__globals__,
                      terminal_two_phase=retained.full_core_phase))
node = kept.edited(node, 'D=b.alloc_qubits(24);b.x(D[0]);b.cswap(pole,N,D)',
                   'D=b.alloc_qubits(24);b.x(D[0]);b.cx(pole,N[0]);b.cx(pole,D[0])')
replacements = dict(synth.replacements)
replacements[id(base.chart_chain)] = xsub.private_rebind(node, replacements)
decode = xsub.private_rebind(base.decode, replacements)
trailing = kept.edited(decode.__globals__['extraction'],
                      'D=b.alloc_qubits(12);b.x(D[0]);b.cswap(pole,N,D)',
                      'D=b.alloc_qubits(12);b.x(D[0]);b.cx(pole,N[0]);b.cx(pole,D[0])')
decode = xsub.clone(decode, dict(decode.__globals__, extraction=trailing))
