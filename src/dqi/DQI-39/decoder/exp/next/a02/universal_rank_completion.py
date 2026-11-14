"""A completed two-coordinate Hermite fiber map over GF(4096)^2.

Let y=s+t*beta, beta²+beta=K.  Away from t=1 and y=0 the raw map is
F(y)=(bar(y)+1)/y.  F collapses all y=s+beta to one; those are exactly
the common linear-padding coordinates of a two-node Hermite pivot.

This circuit is a permutation on ALL 2^24 inputs.  It agrees with F away
from the collapsed fiber and 0, maps the chosen canonical padding s=hc
to one, and puts the other padding values at the missing norm-one points.
It is a local normalized component, not a whole direct syndrome return.
"""
from schur_scalar import inverse_apply,scale,zero_toggle,ar
from exp.inverse12_escape.joint import inverse12_reverse67,inverse24_reverse209


def closed_inverse(b,x):
    """The existing matched reverse with zero incoming debt is phase clean."""
    m=b.alloc_bits(len(x));b.bit_store(m,False)
    if len(x)==12:inverse12_reverse67(b,x,m)
    else:
        assert len(x)==24
        inverse24_reverse209(b,x,m)


def swap_zero_canonical(b,y,hc=0):
    """The fixed transposition 0 <-> hc+beta, without retained flags."""
    pivot=y[12]
    for j in ar.bits(hc):b.cx(pivot,y[j])
    others=list(y[:12])+list(y[13:])
    F=b.alloc_qubits(1)[0]
    zero_toggle(b,others,F)
    b.cx(F,pivot)
    zero_toggle(b,others,F)
    b.free(F)
    for j in ar.bits(hc):b.cx(pivot,y[j])


def T(b,y):
    s,t=y[:12],y[12:]
    b.x(t[0])
    inverse_apply(b,t,lambda ti:scale(b,s,t,ti,True))
    closed_inverse(b,t)
    b.x(t[0])


def completed(b,y,reverse=False,hc=0):
    assert len(y)==24 and 0<=hc<4096
    if not reverse:
        swap_zero_canonical(b,y,hc)
        T(b,y)
        closed_inverse(b,y)
        b.x(y[0])
    else:
        b.x(y[0])
        closed_inverse(b,y)
        T(b,y)
        swap_zero_canonical(b,y,hc)
