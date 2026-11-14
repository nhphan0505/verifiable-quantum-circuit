"""Three-shear remaining-node update with every source paid and restored.

Ui and Vi are held in existing data banks.  Vi temporarily becomes
W=inv0(Vi+Im(Ui)); Ui's low half temporarily stores gamma.  Only the
12-bit delta word is newly retained, and one initialized inverse of it
serves every target scale.  This is a reversible all-input completion;
the Hermite Schur interpretation requires Delta != 0.
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'exp/next/a22'), str(ROOT/'exp/next/a02')]
from nonlinear_pair import ar, inverse_apply, scale, closed_inverse
from exp.mul99.kernels import mul24_xor99_zero


def source_product(b, source, target, out, t, pair=True, q_inverse=1):
    """out += ev(source,t)*target/q; no private quantum word."""
    lo,hi=source[:12],source[12:]
    field=ar.field(12)
    cols=tuple(field.mul(t,1<<j) for j in range(12))
    ar.linear_xor(b,hi,lo,cols)
    if q_inverse != 1:
        c=tuple(field.mul(q_inverse,1<<j) for j in range(12))
        back=tuple(ar.inverse_columns(c))
        ar.linear_inplace(b,lo,c)
        if pair:ar.linear_inplace(b,hi,c)
    if pair:mul24_xor99_zero(b,source,target,out,2048)
    else:ar.mul_xor0(b,lo,target,out)
    if q_inverse != 1:
        if pair:ar.linear_inplace(b,hi,back)
        ar.linear_inplace(b,lo,back)
    ar.linear_xor(b,hi,lo,cols)


def gamma_xor(b, ui, W):
    a=ui[12:]
    square=tuple(ar.field(12).square(1<<j) for j in range(12))
    back=tuple(ar.inverse_columns(square))
    ar.linear_inplace(b,a,square)
    b.cx(W[12:],W[:12])
    ar.mul_xor0(b,a,W[:12],ui[:12])
    b.cx(W[12:],W[:12])
    ar.linear_inplace(b,a,back)


def update(b, ui, vi, A, B, real_a=None, real_b=None,
           offsets=None, real_offset=64, reverse=False):
    """Update existing homogeneous A/B banks, restoring both jet sources.

    A,B are remaining extension pairs, at y=t+beta.  The optional ordinary
    node is y=real_offset.  Nodes at the removed pair t=0,1 are excluded.
    """
    assert len(ui)==len(vi)==24 and len(A)==len(B)
    offsets=list(offsets or range(2,2+2*len(A),2))
    assert len(offsets)==len(A) and all(t not in (0,1) for t in offsets)
    rows=list(zip(A,B,offsets,[True]*len(A)))
    if real_a is not None:
        assert real_b is not None
        rows.append((real_a,real_b,real_offset,False))
    f=ar.field(12)
    def old_shears():
        for aa,bb,t,pair in rows:
            source_product(b,ui,bb,aa,t,pair)
    if not reverse:old_shears()
    b.cx(ui[12:],vi[:12])
    closed_inverse(b,vi)
    delta=b.alloc_qubits(12)
    b.x(delta[0])
    ar.mul_xor0(b,ui[12:],vi[12:],delta)

    def action(di):
        gamma_xor(b,ui,vi)
        scale(b,ui[:12],delta,di,True)
        # ui now contains (gamma,a); vi contains (d,e).
        for aa,bb,t,pair in (reversed(rows) if reverse else rows):
            q=f.square(t)^t^(0 if pair else 2048)
            assert q
            if reverse:source_product(b,ui,bb,aa,t,pair)
            if reverse:
                if pair:
                    scale(b,bb[:12],delta,di,False)
                    scale(b,bb[12:],delta,di,False)
                else:scale(b,bb,delta,di,False)
            source_product(b,vi,aa,bb,t,pair,f.invert(q))
            if not reverse:
                if pair:
                    scale(b,bb[:12],delta,di,True)
                    scale(b,bb[12:],delta,di,True)
                else:scale(b,bb,delta,di,True)
                source_product(b,ui,bb,aa,t,pair)
        scale(b,ui[:12],delta,di,False)
        gamma_xor(b,ui,vi)
    inverse_apply(b,delta,action)
    ar.mul_xor0(b,ui[12:],vi[12:],delta)
    b.x(delta[0]);b.free(delta)
    closed_inverse(b,vi)
    b.cx(ui[12:],vi[:12])
    if reverse:old_shears()
