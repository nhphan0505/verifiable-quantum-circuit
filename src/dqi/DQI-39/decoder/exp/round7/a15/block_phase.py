"""One norm source for the nine different inverse-Y characters.

Y=u+h*x is the same safe polynomial throughout. At beta_j=c_j+x,
Norm(Y(beta_j))=Norm(Y(x))+(c_j^2+c_j)*h^2. The latter correction is
linear, so a single twelve-bit norm serves all nine exact phase kernels.
"""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'exp/round7/a12')]
from overlap_prefix import *
from exp.noscratch.schedules import norm_xor_noscratch,classical_transpose
from exp.jet24.kernel import phase_inverse12_quantum64


def close_inverse_debts(b,h1,F,debts):
    y=combine(h1);u,h=h1;f=ar.field(12)
    b.cx(F,u[0]);n=b.alloc_qubits(12);norm_xor_noscratch(b,y,n,K)
    for ct,delta,q0,mask in debts:
        # q0/Y is a constant-linear image of 1/Y.
        cols=[f.mul(q0,1<<j)for j in range(12)]
        m0=classical_transpose(b,mask[:12],cols)
        m1=classical_transpose(b,mask[12:],cols)
        b.free(mask)
        adjust=[f.mul(delta,f.square(1<<j))for j in range(12)]
        ar.linear_xor(b,h,n,adjust);cx(b,h,u,ct)
        weight=b.alloc_qubits(12)
        def coeff():
            for j in range(12):
                for i in range(12):
                    for r in ar.bits(f.mul(1<<i,1<<j)):
                        b.ccx(m0[r],u[i],weight[j]);b.ccx(m0[r],h[i],weight[j]);b.ccx(m1[r],h[i],weight[j])
        coeff();phase_inverse12_quantum64(b,n,weight);coeff();b.free(weight)
        cx(b,h,u,ct);ar.linear_xor(b,h,n,adjust);b.free(m0);b.free(m1)
    ar._erase_norm(b,y,n,K);b.free(n);b.cx(F,u[0])
