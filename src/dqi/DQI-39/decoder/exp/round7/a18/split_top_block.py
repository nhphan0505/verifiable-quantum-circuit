"""Top retirement plus a twelve-wire derivative coefficient consumer."""
from types import FunctionType
import retired_top_block as prior
from retired_top_block import *


def scaleword(b,v,k):
    f=ar.field(12);ar.linear_inplace(b,v,[f.mul(k,1<<j)for j in range(12)])


def split_coefficient_product(b,h1,p,top,F,ct,delta,N,L):
    """Add (Clo+x*Chi)*N with one twelve-bit C bank, fully paid."""
    u,h=h1;C=b.alloc_qubits(12)
    ar.mul_xor0(b,h,top,C)
    # x*C*(Nlo+x*Nhi)=K*C*Nhi+x*C*(Nlo+Nhi).
    scaleword(b,N[12:],K);ar.mul_xor0(b,C,N[12:],L[:12]);scaleword(b,N[12:],inv(K))
    b.cx(N[12:],N[:12]);ar.mul_xor0(b,C,N[:12],L[12:]);b.cx(N[12:],N[:12])
    if ct^delta:scaleword(b,C,ct^delta)
    else:
        m=b.alloc_bits(12);b.hmr(C,m);ar.phase_product(b,h,top,m);b.free(m)
    ar.mul_xor0(b,h,p[0],C)
    b.cx(F,u[0]);b.cx(top,p[1]);ar.mul_xor0(b,u,p[1],C);b.cx(top,p[1]);b.cx(F,u[0])
    ar.mul_xor0(b,C,N[:12],L[:12]);ar.mul_xor0(b,C,N[12:],L[12:])
    m=b.alloc_bits(12);b.hmr(C,m);b.free(C)
    ar.phase_product(b,h,p[0],m)
    b.cx(F,u[0]);b.cx(top,p[1]);ar.phase_product(b,u,p[1],m);b.cx(top,p[1]);b.cx(F,u[0])
    f=ar.field(12);extra=classical_transpose(b,m,[f.mul(ct^delta,1<<j)for j in range(12)])
    ar.phase_product(b,h,top,extra);b.free(extra);b.free(m)

def two_head_return(b,words,gi,N,D,L,params,source,reference):
    h1,p=words[2:4],words[4:6]
    F=source.state['flag'];top=source.state['top']
    spec=reference.groups[gi];ct=spec['c'];delta=spec['kap']^K
    q0=params[0][0];q1=params[1][0];q2=params[2][0]
    assert q0==q1 and params[2][1]==0
    # a=N2/(q2*Y), a+(1+F)*v=q0/Y.
    scalepair(b,N,inv(q2));cx(b,h1[1],h1[0],ct);b.cx(F,h1[0][0])
    divide_lowwidth369(b,N,combine(h1),K)
    b.cx(F,h1[0][0]);cx(b,h1[1],h1[0],ct)
    product_frame(b,p,top,ct,delta)
    mul24_xor99(b,combine(p),N,D,K)
    product_unframe(b,p,top,ct,delta)
    scalepair(b,D,inv(q0)) # D=v is the exact old affine payload.

    # L0=L2/(q0*q2)+C*a^2/q0+(H1/q0+h1)*v^2.
    scalepair(b,L,inv(mul(q0,q2)))
    reference.external_square24(b,N);scalepair(b,N,inv(q0))
    split_coefficient_product(b,h1,p,top,F,ct,delta,N,L)
    scalepair(b,N,q0);reference.external_square24(b,N,True)
    reference.external_square24(b,D)
    reference.external_corrected_product(b,h1,D,L,ct,inv(q0))
    reference.external_square24(b,D,True)

    # This measured coordinate is a known inverse-Y function plus v.
    m=b.alloc_bits(24);b.hmr(N,m)
    b.cz(D,m);b.ccz(F,D,m)
    if source.state.get('defer_inverse'):
        source.state['inverse_debts'].append((ct,delta,q0,m))
    else:
        cx(b,h1[1],h1[0],ct);b.cx(F,h1[0][0]);scalepair(b,combine(h1),inv(q0))
        close_inverse_character(b,combine(h1),m)
        scalepair(b,combine(h1),q0);b.cx(F,h1[0][0]);cx(b,h1[1],h1[0],ct)
        b.free(m)
    b.gf2_iadd(q0,target=N[:12])


_scope=dict(prior.make_return.__globals__,two_head_return=two_head_return)
make_return=FunctionType(prior.make_return.__code__,_scope,'make_return',prior.make_return.__defaults__,prior.make_return.__closure__)
make_return.__kwdefaults__=prior.make_return.__kwdefaults__
