"""Exact65T complete GF64 log, combining the two modular7 corrections.

The six nonzero parity coefficients of psi(r) are[1,1,0,4,2,5,3].
Controlled multiplication by their powers costs18T. No ancilla or HMR.
"""
from structured_log6 import *
from structured_log6 import _Tape,T_CERT,perm3,exception_row,pack_crt
from packed_chart import ratio_chart6,negate_mod7
from lowclean import permutation3,controlled_linear
PARITY_COEFFICIENTS=(1,1,0,4,2,5,3)


def correction(b,key,ratio):
    """Add psi=[2,1,4,4,2,5,2,4] mod7, fixing exceptional key7."""
    f=ar.field(3)
    permutation3(b,key,'log',True)
    ar.linear_inplace(b,key,tuple(f.mul(4,1<<i) for i in range(3)))
    for mask,e in enumerate(PARITY_COEFFICIENTS,1):
        if not e:continue
        bits=[i for i in range(3) if mask>>i&1];control=ratio[bits[0]]
        for i in bits[1:]:b.cx(ratio[i],control)
        if e in (1,2,4):alpha=2;j={1:0,2:1,4:2}[e]
        else:alpha=f.invert(2);j={6:0,5:1,3:2}[e]
        pre=tuple(f.pow(1<<i,1<<((3-j)%3)) for i in range(3))
        post=tuple(f.pow(1<<i,1<<j) for i in range(3))
        ar.linear_inplace(b,key,pre)
        controlled_linear(b,key,tuple(f.mul(alpha,1<<i) for i in range(3)),control)
        ar.linear_inplace(b,key,post)
        for i in reversed(bits[1:]):b.cx(ratio[i],control)
    permutation3(b,key,'log')


def _forward65(b,y):
    ratio_chart6(b,y)
    t,j=y[:3],y[3:]
    b.swap(j[0],j[1]);b.swap(j[1],j[2]);negate_mod7(b,j)
    correction(b,j,t)
    perm3(b,t,T_CERT)
    exception_row(b,t,j)
    pack_crt(b,t,j)


def logarithm(b,y,inverse=False):
    assert len(y)==6
    if not inverse:_forward65(b,y);return
    tape=_Tape();_forward65(tape,y)
    for name,args,kwargs in reversed(tape.ops):getattr(b,name)(*args,**kwargs)
