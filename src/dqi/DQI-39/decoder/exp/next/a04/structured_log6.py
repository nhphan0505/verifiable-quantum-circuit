"""Exact67-Toffoli six-bit GF64 logarithm, with zero encoded63.

No qubit is allocated and no measurement or phase is used. Every borrowed
wire belongs to the six source wires and is returned within its helper.
The inverse is the reversed X/CX/CCX/SWAP transcript.
"""
from pathlib import Path
import sys,itertools
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'exp/new/a23'),str(ROOT/'exp/new/a16'),str(ROOT/'exp/new/a10'),str(ROOT/'exp/new/a07')]
from packed_chart import residue_chart6,ar
from mod7 import add_mod7
from lowclean import mcx_dirty
from lowclean_norm5 import transvection_data


def _linear(rows,x):return sum(((r&x).bit_count()&1)<<i for i,r in enumerate(rows))
def _columns(rows):return tuple(sum(((r>>j)&1)<<i for i,r in enumerate(rows)) for j in range(3))
def _affine(table):
 c=table[0];cols=tuple(table[1<<j]^c for j in range(3))
 return (c,cols) if all(table[x]==c^ar.apply(cols,x) for x in range(8)) else None


def transpose3(b,x,a,z):
    """Exchange any two three-bit states using one affine-conjugated CCX."""
    d=a^z
    u=next(r for r in range(1,8) if not (r&d).bit_count()%2)
    v=next(r for r in range(1,8) if r!=u and not (r&d).bit_count()%2)
    w=next(r for r in range(1,8) if (r&d).bit_count()%2)
    cols=_columns((u,v,w));back=tuple(ar.inverse_columns(cols))
    constant=_linear((u,v,w),a)^3
    ar.linear_inplace(b,x,cols);b.gf2_iadd(constant,target=x)
    b.ccx(x[0],x[1],x[2])
    b.gf2_iadd(constant,target=x);ar.linear_inplace(b,x,back)


def _perm_certificate(table):
    trans=list(itertools.combinations(range(8),2))
    for depth in range(3):
        for seq in itertools.product(trans,repeat=depth):
            p=list(table)
            for a,z in seq:p[a],p[z]=p[z],p[a]
            aff=_affine(p)
            if aff is not None:return seq,aff
    raise ValueError('Permutation needs more than two transpositions')

T_TABLE=(6,1,0,7,3,4,2,5)
DEC_TABLE=(6,0,1,2,3,4,5,7)
T_CERT=_perm_certificate(T_TABLE)
DEC_CERT=_perm_certificate(DEC_TABLE)
assert len(T_CERT[0])==1 and len(DEC_CERT[0])==2


def perm3(b,x,cert):
    seq,(constant,columns)=cert
    for a,z in seq:transpose3(b,x,a,z)
    ar.linear_inplace(b,x,columns);b.gf2_iadd(constant,target=x)


def _majority(b,a,c,d):
    b.cx(a,c);b.cx(a,d);b.ccx(c,d,a)


def _unmajority(b,a,c,d):
    b.ccx(c,d,a);b.cx(a,d);b.cx(a,c)


def suffix_cycle(b,u,j):
    """For each u, cycle j through u,u+1,...,7; leave lower j fixed.11T."""
    b.x(u[2]);mcx_dirty(b,[j[0],j[1],u[2]],j[2],[u[0]]);b.x(u[2])
    b.x(u[1:]);_majority(b,u[1],u[2],j[2])
    b.ccx(j[0],u[1],j[1])
    _unmajority(b,u[1],u[2],j[2]);b.x(u[1:])
    b.x(u);_majority(b,u[1],j[1],u[0]);_majority(b,u[2],j[2],u[1])
    b.cx(u[2],j[0])
    _unmajority(b,u[2],j[2],u[1]);_unmajority(b,u[1],j[1],u[0]);b.x(u)


def pack_crt(b,t,j):
    """j<7: output9j+t+1; j=7: output9t.18T, six wires."""
    b.ccx(t[0],t[1],t[2]);b.cx(t[0],t[1]);b.x(t[0])
    mcx_dirty(b,[j[0],t[0],t[1]],t[2],[j[1]])
    b.ccx(j[0],t[0],t[1]);b.cx(j[0],t[0])
    b.ccx(j[1],t[1],t[2]);b.cx(j[1],t[1]);b.cx(j[2],t[2])
    suffix_cycle(b,t,j)


TRANSVECTIONS={'U':(1,2),'V':(2,1),'W1':(2,4),'W2':(7,6)}
EXCEPTION_SEQUENCE=(('W1',2),('W2',2),('U',0),('V',1),('U',0),('V',1),('W2',2),('W1',2),('V',1),('U',0),('V',1),('U',0))
COMPILED={name:transvection_data(a,v) for name,(a,v) in TRANSVECTIONS.items()}


def exception_row(b,t,j):
    """Apply q=[3,0,5,6,4,1,7,2] to t iff j=7, in14T."""
    transpose3(b,t,4,7);b.x(t)
    for name,k in EXCEPTION_SEQUENCE:
        cols,back=COMPILED[name]
        ar.linear_inplace(b,t,cols);b.ccx(j[k],t[0],t[1]);ar.linear_inplace(b,t,back)
    b.x(t);transpose3(b,t,4,7)


class _Tape:
    def __init__(self):self.ops=[]
    def __getattr__(self,name):
        def call(*args,**kwargs):self.ops.append((name,args,kwargs))
        return call


def _forward(b,y):
    residue_chart6(b,y)
    t,j=y[:3],y[3:]
    perm3(b,t,T_CERT)
    add_mod7(b,j,t,True)
    perm3(b,j,DEC_CERT)
    b.swap(j[0],j[1]);b.swap(j[1],j[2])
    exception_row(b,t,j)
    pack_crt(b,t,j)


def logarithm(b,y,inverse=False):
    assert len(y)==6
    if not inverse:_forward(b,y);return
    tape=_Tape();_forward(tape,y)
    for name,args,kwargs in reversed(tape.ops):getattr(b,name)(*args,**kwargs)
