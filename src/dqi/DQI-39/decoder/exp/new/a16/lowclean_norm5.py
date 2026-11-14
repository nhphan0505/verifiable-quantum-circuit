"""Use a five-Toffoli GF8 completed norm multiplier.

All generic GF8 sources retain the original exact logarithm permutation.
The affine extension agrees with log on zero and all trace-one values.

Share nested denominator charts, with a borrowed linear norm flag.

The restricted GF64 norm-chart source has absolute trace one or is zero.
Its GF8 high component therefore has trace one or is zero. In the supplied
GF8 logarithm encoding, exactly the zero case has odd log parity on this
restricted set. A preserved log-source bit can temporarily hold this
parity for the chart and the target correction, then is restored by CX.
"""
from contextlib import contextmanager
import lowclean_bidirectional as old
from lowclean_bidirectional import ar,chart,zero_toggle,permutation3,controlled_linear,mul_xor_noscratch
from lowclean import PERMS,trace

AFFINE_LOG=(7,3,6)
AFFINE_LOG_INV=tuple(ar.inverse_columns(AFFINE_LOG))

def affine_log(b,y,reverse=False):
    if reverse:
        b.x(y);ar.linear_inplace(b,y,AFFINE_LOG_INV)
    else:
        ar.linear_inplace(b,y,AFFINE_LOG);b.x(y)

for value in range(8):
    if value==0 or trace(3,value)==1:
        assert (PERMS['log']['permutation'][value].bit_count()&1)==(value==0)
        affine=7
        for j in range(3):
            if (value>>j)&1:affine^=AFFINE_LOG[j]
        assert affine==PERMS['log']['permutation'][value]

NORM_GATES=((1,2,5),(2,3,3),(3,4,1),(2,6,7),(1,1,2))


def transvection_data(a,v):
    assert a and v and (a&v).bit_count()%2==0
    target=next(i for i in range(1,8) if (i&v).bit_count()%2)
    third=next(i for i in range(1,8) if not (i&v).bit_count()%2 and i!=a)
    rows=(a,target,third)
    cols=tuple(sum(((r>>j)&1)<<i for i,r in enumerate(rows)) for j in range(3))
    return cols,tuple(ar.inverse_columns(cols))


NORM_COMPILED=tuple((c,*transvection_data(a,v)) for c,a,v in NORM_GATES)
assert [trace(3,v) for v in range(8)]==[v&1 for v in range(8)]


def norm_scale3(b,x,y,inverse=False):
    # y is zero or has trace one. Its bits1,2 select 1,3,5,7;
    # zero and one both select the identity matrix.
    for c,cols,back in reversed(NORM_COMPILED) if inverse else NORM_COMPILED:
        control=y[1] if c&1 else y[2]
        if c==3:b.cx(y[2],control)
        ar.linear_inplace(b,x,cols)
        b.ccx(control,x[0],x[1])
        ar.linear_inplace(b,x,back)
        if c==3:b.cx(y[2],control)



@contextmanager
def paired_source(b,y,trace01=False):
    n=len(y)
    if n==3:
        f=ar.field(3)
        if trace01:
            def apply(targets,inverse=False):
                for x in targets:norm_scale3(b,x,y,inverse)
            yield apply
            return
        permutation3(b,y,'log')
        def apply(targets,inverse=False):
            alpha=f.invert(2) if inverse else 2
            cols=tuple(f.mul(alpha,1<<i) for i in range(3))
            for j in range(3):
                pre=tuple(f.pow(1<<i,1<<((3-j)%3)) for i in range(3))
                post=tuple(f.pow(1<<i,1<<j) for i in range(3))
                for x in targets:
                    ar.linear_inplace(b,x,pre);controlled_linear(b,x,cols,y[j]);ar.linear_inplace(b,x,post)
        yield apply
        permutation3(b,y,'log',True)
        return
    assert n in (6,12) and (not trace01 or n==6)
    m=n//2;to,back,K=ar.tower(n);ar.linear_inplace(b,y,to)
    r,g=y[:m],y[m:]
    if not trace01:
        F=b.alloc_qubits(1)[0];zero_toggle(b,g,F,r);b.cswap(F,r,g)
    with paired_source(b,g,trace01) as ga:
        ga([r],True)
        @contextmanager
        def flag():
            if trace01:
                # The restricted leaf keeps g in its raw field representation.
                # Trace_GF8(g) is bit0; on this domain, zero is its complement.
                b.x(g[0]);yield g[0];b.x(g[0])
            else:yield F
        cols=tuple((1<<j)|(1<<(m+j)) for j in range(m))+tuple(1<<j for j in range(m))
        invcols=tuple(ar.inverse_columns(cols))
        def apply(targets,inverse=False):
            for x in targets:ar.linear_inplace(b,x,to)
            halves=[(x[:m],x[m:]) for x in targets]
            if inverse:
                ga([v for pair in halves for v in pair],True)
                with flag() as f:
                    for x in targets:controlled_linear(b,x,invcols,f)
                for a,z in halves:b.swap(a,z);mul_xor_noscratch(b,r,a,z)
                with flag() as f:
                    chart(b,r,f,K);scale_many(b,[z for a,z in halves],r,True,True);chart(b,r,f,K,True)
                for a,z in halves:mul_xor_noscratch(b,r,z,a);b.cx(z,a)
            else:
                for a,z in halves:b.cx(z,a);mul_xor_noscratch(b,r,z,a)
                with flag() as f:
                    chart(b,r,f,K);scale_many(b,[z for a,z in halves],r,False,True);chart(b,r,f,K,True)
                for a,z in halves:mul_xor_noscratch(b,r,a,z);b.swap(a,z)
                with flag() as f:
                    for x in targets:controlled_linear(b,x,cols,f)
                ga([v for pair in halves for v in pair])
            for x in targets:ar.linear_inplace(b,x,back)
        yield apply
        ga([r])
    if not trace01:b.cswap(F,r,g);zero_toggle(b,g,F,r);b.free(F)
    ar.linear_inplace(b,y,back)


@contextmanager
def source(b,y,inverse=False):
    with paired_source(b,y) as apply:
        yield lambda targets:apply(targets,inverse)


def scale_many(b,targets,y,inverse=False,trace01=False):
    with paired_source(b,y,trace01) as apply:apply(targets,inverse)


def scale(b,x,y,inverse=False):scale_many(b,[x],y,inverse)
