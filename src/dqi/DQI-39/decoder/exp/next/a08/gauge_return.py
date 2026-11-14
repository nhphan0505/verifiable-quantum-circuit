"""Exact one-traversal homogeneous return, conditional on first-column sources.

Reference width, not a whole-decoder entry.  a,c must already contain the
first column of the original transfer matrix. They are preserved.  Their
construction, storage, and erasure are deliberately NOT included here.
Every supported forward token and every new measurement phase is closed.
Both the paired reference token and the six-character chart token are supported.
This is NOT an installed BASE replacement: the supplied column has no way in.
"""
from pathlib import Path
import sys
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path[:0]=[str(ROOT/'playbook/kit'),str(ROOT/'playbook/kit/decoder'),str(ROOT/'exp/r-main/narrow240'),str(H)]
from final_decoder import decode as old
from exp.decoder.common import *
from exp.mul99.kernels import mul24_xor99
from exp.mul99.schedules import multiply_forward99
from exp.arithmetic.division import phase_product24,phase_zero
from exp.noscratch.schedules import norm_xor_noscratch
from exp.inverse12_escape.joint import inverse24_reverse209
from exp.jet24.kernel import phase_inverse24_classical106
from clean_heads import zero_mask


def close_inverse_character(b,g,mask):
    """mask is expressed in the decoder's GF24 extension basis."""
    cols,back,_=ar.extension_columns(K)
    # Convert quantum g and the mask of its inverse into canonical GF24.
    from exp.arithmetic.lowwidth import classical_transpose
    canonical_mask=classical_transpose(b,mask,back)
    ar.linear_inplace(b,g,cols)
    phase_inverse24_classical106(b,g,canonical_mask)
    ar.linear_inplace(b,g,back)
    b.free(canonical_mask)


def return_node(b,words,gi,column,token):
    """Reverse old.external_node_chain using provided first column (a,c).

    Valid image includes arbitrary affine input jet, all head values, and
    both output charts.  q constants must be nonzero, as in the base.
    token is the actual unchanged forward token (pole,gauge,norm).
    """
    gspec=old.groups[gi]
    N=combine(words[gspec['word']:gspec['word']+2])
    L=combine(words[gspec['word']+2:gspec['word']+4])
    a,c=column;F=token['pole']
    heads=[words[2*i:2*i+2] for i in range(2*gi)]
    params=[];corr=0;delta=1
    for i in range(2*gi):
        q=old.ks[i]^gspec['kap'];assert q
        params.append((q,corr));corr^=inv(q);delta=mul(delta,q)
    assert corr==0
    with b.mark('column_recovery'):
        # ell = (c*(r+F)+a*(1+F))/delta, always nonzero on this image.
        ell=b.alloc_qubits(24)
        b.cx(F,N[0]);mul24_xor99(b,c,N,ell,K);b.cx(F,N[0])
        b.cx(a,ell);b.ccx(F,a,ell);scalepair(b,ell,inv(delta))
        D=b.alloc_qubits(24);b.cx(ell,D)
        inverse24_reverse209(b,D,zero_mask(b),K)  # D=g, fully closed inverse.
    with b.mark('payload_unnormalize'):
        # Unnormalize in the selected chart. The old values are uniquely
        # determined by the new values and retained ell, so HMR is uniform.
        b.cx(F,N[0])
        nm=multiply_forward99(b,N,D,K)
        phase_product24(b,N,ell,nm,K);b.free(nm)
        old.external_square24(b,D);old.external_square24(b,ell)
        lm=multiply_forward99(b,L,D,K)
        phase_product24(b,L,ell,lm,K);b.free(lm)
        old.external_square24(b,ell,True);old.external_square24(b,D,True)
        em=b.alloc_bits(24);b.hmr(ell,em);b.free(ell)
        close_inverse_character(b,D,em);b.free(em)
    with b.mark('old_token_closure'):
        # Exact closure of the original normalizer and discarded gauge.
        if isinstance(token['norm'],dict):
            from close_chart import close_chart_character
            close_chart_character(b,D,token['norm'])
            assert 'gauge' not in token
        else:
            b.cz(D,token['gauge']);b.free(token['gauge'])
            norm=b.alloc_qubits(12);norm_xor_noscratch(b,D,norm,K)
            old.phase_inverse34(b,norm,token['norm']);b.free(token['norm'])
            ar._erase_norm(b,D,norm,K);b.free(norm)
    with b.mark('pole_retirement'):
        # At a pole r=0, so N=g and this shear clears D. Else it leaves D=g.
        b.ccx(F,N,D)
        fm=b.alloc_bits(1);b.hmr(F,fm[0]);b.free(F)
        phase_zero(b,D,fm[0]);b.free(fm)
    with b.mark('inverse_traversal'):
        # A single full inverse homogeneous traversal, with the first affine
        # specialization written explicitly so its derivative corner is exact.
        for head,(q,corr) in reversed(list(zip(heads,params))[1:]):
            old.external_chain_step(b,head,N,D,L,q,gspec['c'],corr,True)
        q0=params[0][0]
        scalepair(b,N,inv(q0));b.swap(N,D);scalepair(b,L,inv(q0))
        ah,hh=heads[0]
        cx(b,hh,ah,gspec['c']);b.cx(combine(heads[0]),N);cx(b,hh,ah,gspec['c'])
        b.cx(hh,L[:12])
        b.x(D[0]);b.free(D)
