"""Exact completed in-place tower arithmetic with at most two clean bits.

This is a width experiment.  Every gate is coherent; the routines return
no HMR debt.  Costs must be obtained from a complete decoder, not this file.
"""
from pathlib import Path
from functools import lru_cache
import json
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'playbook/kit'),str(ROOT/'playbook/kit/decoder')]
from exp.arithmetic import field as ar
from exp.noscratch.kernels import mul_xor_noscratch

PERMS=json.loads((ROOT/'exp/r-main/narrow240/permutations3.json').read_text())


def permutation3(b,x,name,reverse=False):
    gates=PERMS[name]['gates']
    for gate in reversed(gates) if reverse else gates:
        getattr(b,gate[0])(*(x[i] for i in gate[1:]))


def linear_ops(columns):
    n=len(columns)
    rows=[sum(((c>>i)&1)<<j for j,c in enumerate(columns)) for i in range(n)]
    ops=[]
    for j in range(n):
        p=next(i for i in range(j,n) if rows[i]>>j&1)
        if p!=j:
            rows[p],rows[j]=rows[j],rows[p];ops.append(('swap',p,j))
        for i in range(n):
            if i!=j and rows[i]>>j&1:
                rows[i]^=rows[j];ops.append(('cx',j,i))
    return tuple(reversed(ops))


def controlled_linear(b,x,columns,F):
    for op,i,j in linear_ops(columns):
        if op=='cx':b.ccx(F,x[i],x[j])
        else:b.cswap(F,x[i],x[j])


def constant_scale(b,x,c,F=None):
    cols=tuple(ar.field(len(x)).mul(c,1<<j) for j in range(len(x)))
    if F is None:ar.linear_inplace(b,x,cols)
    else:controlled_linear(b,x,cols,F)


def mcx_dirty(b,controls,target,borrow):
    """Toggle target by AND(controls), restore arbitrary borrowed bits."""
    n=len(controls)
    if n==1:b.cx(controls[0],target);return
    if n==2:b.ccx(controls[0],controls[1],target);return
    work=list(borrow[:n-2]);assert len(work)==n-2
    for first in (True,False):
        if first:b.ccx(controls[0],controls[1],work[0])
        for j in range(1,n-2):b.ccx(work[j-1],controls[j+1],work[j])
        b.ccx(work[-1],controls[-1],target)
        for j in reversed(range(1,n-2)):b.ccx(work[j-1],controls[j+1],work[j])
        if first:b.ccx(controls[0],controls[1],work[0])


def zero_toggle(b,x,F,borrow):
    b.x(x);mcx_dirty(b,x,F,borrow);b.x(x)


def trace(n,x):
    f=ar.field(n);v=x;t=0
    for _ in range(n):t^=v;v=f.square(v)
    return t


@lru_cache(None)
def chart_data(n,K):
    f=ar.field(n)
    qF=next(v for v in range(1,1<<n) if trace(n,v)==0)
    cols=tuple((f.square(1<<i)^(1<<i))|((i==0)<<n) for i in range(n))+(K^qF,)
    back=tuple(ar.inverse_columns(cols))
    return cols,back,qF


def chart(b,r,F,K,reverse=False):
    cols,back,qF=chart_data(len(r),K)
    if reverse:
        b.gf2_iadd(K,target=r);ar.linear_inplace(b,list(r)+[F],back)
    else:
        ar.linear_inplace(b,list(r)+[F],cols);b.gf2_iadd(K,target=r)
    return qF


def scale3(b,x,y):
    """x *= y+[y=0], preserving y, no additional qubit."""
    f=ar.field(3)
    permutation3(b,y,'log')
    alpha=tuple(f.mul(2,1<<i) for i in range(3))
    for j in range(3):
        pre=tuple(f.pow(1<<i,1<<((3-j)%3)) for i in range(3))
        post=tuple(f.pow(1<<i,1<<j) for i in range(3))
        ar.linear_inplace(b,x,pre)
        controlled_linear(b,x,alpha,y[j])
        ar.linear_inplace(b,x,post)
    permutation3(b,y,'log',True)


def inverse(b,x):
    """inv0 in place; GF64 needs one clean bit, GF4096 two."""
    n=len(x)
    if n==3:permutation3(b,x,'inverse');return
    assert n in (6,12)
    m=n//2;to,back,K=ar.tower(n);ar.linear_inplace(b,x,to)
    r,g=x[:m],x[m:]
    F=b.alloc_qubits(1)[0];zero_toggle(b,g,F,r);b.cswap(F,r,g)
    inverse(b,g);scale(b,r,g)
    qF=chart(b,r,F,K)
    inverse(b,r);scale(b,g,r);inverse(b,r)
    chart(b,r,F,K,True)
    b.x(r[0]);b.cx(F,r[0])
    scale(b,r,g)
    constant_scale(b,g,qF,F)
    b.cswap(F,r,g)
    zero_toggle(b,g,F,r);b.free(F)
    ar.linear_inplace(b,x,back)


def scale(b,x,y):
    """Completed in-place multiplication, preserving source, all inputs."""
    n=len(x);assert len(y)==n
    if n==3:scale3(b,x,y);return
    assert n in (6,12)
    m=n//2;to,back,K=ar.tower(n)
    ar.linear_inplace(b,x,to);ar.linear_inplace(b,y,to)
    a,z=x[:m],x[m:];r,g=y[:m],y[m:]
    F=b.alloc_qubits(1)[0];zero_toggle(b,g,F,r);b.cswap(F,r,g)
    inverse(b,g);scale(b,r,g);inverse(b,g)
    b.cx(z,a);mul_xor_noscratch(b,r,z,a)
    qF=chart(b,r,F,K);scale(b,z,r);chart(b,r,F,K,True)
    mul_xor_noscratch(b,r,a,z);b.swap(a,z)
    # For F=1, undo [[0,qF],[1,1]] on the target pair.
    f=ar.field(m);qi=f.invert(qF)
    cols=tuple((f.mul(qi,1<<j))| (f.mul(qi,1<<j)<<m) for j in range(m)) + tuple(1<<j for j in range(m))
    controlled_linear(b,x,cols,F)
    scale(b,a,g);scale(b,z,g)
    scale(b,r,g);b.cswap(F,r,g)
    zero_toggle(b,g,F,r);b.free(F)
    ar.linear_inplace(b,y,back);ar.linear_inplace(b,x,back)


def stream(b,x):
    inverse(b,x)
    mask=b.alloc_bits(len(x));b.bit_store(mask,False)
    return mask


def scale_defer(b,x,y):
    """For proved-nonzero y, replaces measured scaling with a unitary map."""
    scale(b,x,y)
    mask=b.alloc_bits(len(x));b.bit_store(mask,False)
    return mask


def inverse_phase(b,x,mask):
    """An exact scalar inverse character with the same two-clean bound."""
    inverse(b,x);b.cz(x,mask);inverse(b,x)
