"""Close a complete ordinary jet's forward HMR token at its output.

This is a source-preserving character oracle, not a decoder result. All
arguments and masks are in the canonical polynomial GF(2^24) basis.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'playbook/kit'),str(ROOT/'playbook/kit/decoder'),
             str(ROOT/'exp/new/a15'),str(ROOT/'exp/r-main/narrow240')]
from exp.decoder.common import ar,zero_hold,zero_free
from exp.noscratch.schedules import norm_xor_noscratch
from exp.arithmetic.lowwidth import classical_transpose
from phase_narrow import phase_inverse12_quantum10


def close_canonical(b,u,v,token):
    """Pay mu·inv0(u)+mv·v/(u+[u=0])²+fz·[u=0].

    The field registers and classical token are preserved. Every new HMR
    character is repaid within this call, including the u=0 fiber.
    """
    mu,mv,fz=token
    to,back,K=ar.tower(24)
    square=tuple(ar.square_columns(24))
    sqrt=tuple(ar.inverse_columns(square))
    mv_square=classical_transpose(b,mv,square)
    ar.linear_inplace(b,u,to)
    N=b.alloc_qubits(12)
    norm_xor_noscratch(b,u,N,K)
    L=b.alloc_qubits(12)

    def coefficient(h,aux):
        for j in ar.bits(h):b.cx(mu[j],aux)
        f=ar.field(24)
        for i,wire in enumerate(v):
            for j in ar.bits(f.mul(1<<i,h)):b.ccx(mv_square[j],wire,aux)

    def traverse(mask=None):
        aux=b.alloc_qubits(1)[0]
        work=b.alloc_qubits(1)[0] if mask is None else None
        cm=b.alloc_bits(1)[0] if mask is not None else None
        b.cx(u[12:],u[:12])
        for seg in (0,1):
            source=u[12*seg:12*(seg+1)]
            for form,vec in ar.tensor(12):
                h=ar.apply(back,vec<<(12*seg))
                indices=list(ar.bits(form));pivot=indices[0]
                for j in indices[1:]:b.cx(source[j],source[pivot])
                coefficient(h,aux)
                if mask is None:
                    b.init_and(source[pivot],aux,work)
                    for j in indices:b.cx(work,L[j])
                    b.del_and(source[pivot],aux,work)
                else:
                    b.bit_store(cm,False)
                    for j in indices:b.cx(mask[j],cm)
                    b.ccz(source[pivot],aux,cm)
                coefficient(h,aux)
                for j in reversed(indices[1:]):b.cx(source[j],source[pivot])
        b.cx(u[12:],u[:12])
        if mask is None:b.free(work)
        else:b.free(cm)
        b.free(aux)

    ar.linear_inplace(b,v,sqrt)
    traverse()
    ar.linear_inplace(b,v,square)
    phase_inverse12_quantum10(b,N,L)
    lm=b.alloc_bits(12);b.hmr(L,lm);b.free(L)
    ar._erase_norm(b,u,N,K);b.free(N)
    ar.linear_inplace(b,v,sqrt)
    traverse(lm)
    ar.linear_inplace(b,v,square)
    b.free(lm);b.free(mv_square)
    ar.linear_inplace(b,u,back)
    # inv0(0)=0 made the rational character above zero. The safe-square
    # completion instead leaves v unchanged at u=0, so repay that fiber.
    ladder=zero_hold(b,u);zero=ladder[-1]
    b.cz(zero,fz[0])
    b.ccz(zero,v,mv)
    zero_free(b,u,ladder)


def close_decoder_basis(b,u,v,token):
    to,back,_=ar.extension_columns(None)
    ar.linear_inplace(b,u,to);ar.linear_inplace(b,v,to)
    close_canonical(b,u,v,token)
    ar.linear_inplace(b,u,back);ar.linear_inplace(b,v,back)


def clear_token(b,token):
    for mask in token:b.bit_store(mask,False)
