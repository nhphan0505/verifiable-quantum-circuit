"""A normalized trace contraction: two GF4096 cubic phase tensors,84T.

The temporary two-payload change of coordinates has determinant one and is
implemented using classical-coefficient shears. No quantum bank is added.
"""
from functools import lru_cache
from classical_mask_merge import classical_linear, classical_product, classical_inverse, dual_columns
from exp.decoder.common import ar, K
from exp.mul99.kernels import mul24_xor99


@lru_cache(None)
def trace_rows():
    f = ar.field(12)
    def trace(v):
        r = 0
        for j in range(12): r ^= f.frobenius(v,j)
        assert r in (0,1)
        return r
    return tuple((sm, sum(trace(f.mul(v,1 << j)) << j for j in range(12)))
                 for sm,v in ar.tensor(12))


def trace_product12(b, x, y, z):
    for sm, tm in trace_rows():
        ii = list(ar.bits(sm)); jj = list(ar.bits(tm))
        assert ii and jj
        p, q = ii[0], jj[0]
        for j in ii[1:]: b.cx(x[j],x[p]); b.cx(y[j],y[p])
        for j in jj[1:]: b.cx(z[j],z[q])
        b.ccz(x[p],y[p],z[q])
        for j in reversed(jj[1:]): b.cx(z[j],z[q])
        for j in reversed(ii[1:]): b.cx(y[j],y[p]); b.cx(x[j],x[p])


def trace_product24_scalar(b, x, C, u):
    # Tr24(a+b*beta)=Tr12(b), beta²+beta=K.
    trace_product12(b,x[:12],C[12:],u)
    b.cx(C[12:],C[:12])
    trace_product12(b,x[12:],C[:12],u)
    b.cx(C[12:],C[:12])


def scale_pair(b, x, y, a, ai, reverse=False):
    if reverse: b.swap(x,y)
    mul24_xor99(b,y,ai,x,K)
    mul24_xor99(b,x,a,y,K)
    mul24_xor99(b,y,ai,x,K)
    if not reverse: b.swap(x,y)


def phase_pair(b, targets, C, u, masks, unused_phase_three_factor=None):
    assert len(targets) == len(masks) == 2
    x,y = targets; mx,my = masks
    a = classical_linear(b,mx,dual_columns())
    c = classical_linear(b,my,dual_columns())
    choose_second = b.alloc_bits(1)[0]
    b.bit_store(choose_second,False)
    for m in mx: b.bit_store(choose_second,True,control=m)
    b.x(choose_second)
    b.push_condition(choose_second)
    b.swap(a,c)
    b.swap(x,y)
    b.pop_condition()
    active = b.alloc_bits(1)[0]
    b.bit_store(active,False)
    for m in a: b.bit_store(active,True,control=m)
    ai = classical_inverse(b,a)
    ratio = classical_product(b,c,ai)
    b.push_condition(active)
    mul24_xor99(b,y,ratio,x,K)
    scale_pair(b,x,y,a,ai)
    trace_product24_scalar(b,x,C,u)
    scale_pair(b,x,y,a,ai,True)
    mul24_xor99(b,y,ratio,x,K)
    b.pop_condition()
    b.push_condition(choose_second)
    b.swap(x,y)
    b.pop_condition()
    for reg in (ratio,ai,active,choose_second,c,a): b.free(reg)
