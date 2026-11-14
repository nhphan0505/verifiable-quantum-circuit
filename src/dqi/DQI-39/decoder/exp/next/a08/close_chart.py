"""Close the actual six-character chart transcript from its raw gauge.

The character contract is the one proved for frozen_chart.normalize and
preserved by BASE's exact substitutions and A07's retained inverses.
This reference keeps extra work registers; it is not a narrow schedule.
"""
from pathlib import Path
import sys
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path[:0]=[str(ROOT/'playbook/kit'),str(ROOT/'playbook/kit/decoder'),str(ROOT/'exp/r-main/narrow240')]
import frozen_chart as chart
from exp.decoder.common import *
from exp.arithmetic.division import zero_flag,phase_zero
from exp.jet24.pro_jet import cached_inverse,PLAN12
from exp.fold_cached_norm.phase34 import phase_inverse34


def close_chart_character(b,C,masks):
    """Apply the pending character of nonzero C; preserve C, consume masks.

    C=A+B*y. F=[B=0], g=B or A, r=A/B if B!=0 else 0,
    q=r²+r+K+(K+1)F. Arguments are g,1/g,gq,1/(gq),r,F.
    Every new temporary measurement is also paid before return.
    """
    assert set(masks)=={'g','i','h','t','r','f'}
    A,g=C[:12],C[12:]
    F=zero_flag(b,g);b.cswap(F,A,g)
    gi,z=cached_inverse(b,g,PLAN12,True)
    # g is nonzero because C is nonzero and the chart selected g.
    b.free(z)
    r=b.alloc_qubits(12);ar.mul_xor0(b,A,gi,r)
    for source,key in ((g,'g'),(gi,'i'),(r,'r')):
        b.cz(source,masks[key]);b.free(masks[key])
    b.cz(F,masks['f'][0]);b.free(masks['f'])
    qbit=b.alloc_qubits(1)[0];chart.chart_norm(b,r,F,qbit)
    h=b.alloc_qubits(12);ar.mul_xor0(b,g,r,h)
    b.cz(h,masks['h']);b.free(masks['h'])
    phase_inverse34(b,h,masks['t']);b.free(masks['t'])
    hm=b.alloc_bits(12);b.hmr(h,hm);b.free(h)
    ar.phase_product(b,g,r,hm);b.free(hm)
    chart.chart_norm(b,r,F,qbit,True);b.free(qbit)
    rm=b.alloc_bits(12);b.hmr(r,rm);b.free(r)
    ar.phase_product(b,A,gi,rm);b.free(rm)
    im=b.alloc_bits(12);b.hmr(gi,im);b.free(gi)
    phase_inverse34(b,g,im);b.free(im)
    b.cswap(F,A,g)
    fm=b.alloc_bits(1);b.hmr(F,fm[0]);b.free(F)
    phase_zero(b,g,fm[0]);b.free(fm)
