"""Exact first transfer column using one existing head bank.

The first two factors send [1:0] to [q1:H1].  Thus H1 itself is
the second source bank; only the constant first bank is allocated.
No measurement, rank assumption, or nonzero variable assumption occurs.
"""
from pathlib import Path
import sys
H = Path(__file__).resolve().parent
ROOT = H.parents[2]
sys.path[:0] = [str(ROOT/'playbook/kit'),str(ROOT/'playbook/kit/decoder')]
from final_decoder import decode as ref
from exp.decoder.common import combine, cx, inv, scalepair


def prepare(b, words, gi, reference=ref):
    spec = reference.groups[gi]
    heads = [words[2*i:2*i+2] for i in range(2*gi)]
    assert len(heads) >= 2
    qs = [reference.ks[i]^spec['kap'] for i in range(2*gi)]
    assert all(qs)
    a = b.alloc_qubits(24)
    q1 = qs[1]
    for bit in range(12):
        if q1 >> bit & 1:
            b.x(a[bit])
    c = combine(heads[1])
    cx(b, heads[1][1], heads[1][0], spec['c'])
    for i in range(2,len(heads)):
        reference.external_scalar_step(b,heads[i],a,c,qs[i],spec['c'])

    def restore():
        for i in reversed(range(2,len(heads))):
            reference.external_scalar_step(b,heads[i],a,c,qs[i],spec['c'],True)
        cx(b, heads[1][1], heads[1][0], spec['c'])
        for bit in range(12):
            if q1 >> bit & 1:
                b.x(a[bit])
        b.free(a)
    return (a,c),restore
