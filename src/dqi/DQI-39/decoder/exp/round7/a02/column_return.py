"""One homogeneous return with a fully constructed and erased column.

This is a whole-stage experiment, initially with a generous width.  The
column source replaces the old companion/scalar-replay mechanism; it is
included in the decoder and never supplied by the checker.
"""
from pathlib import Path
import sys
H=Path(__file__).resolve().parent; ROOT=H.parents[2]
sys.path[:0]=[str(H),str(ROOT/'exp/next/a08'),str(ROOT/'playbook/kit'),
             str(ROOT/'playbook/kit/decoder')]
import banked_column
from gauge_return import (old, close_inverse_character, zero_mask,
                          inverse24_reverse209, norm_xor_noscratch,
                          multiply_forward99, mul24_xor99, phase_product24,
                          phase_zero)
from exp.decoder.common import *
from close_chart import close_chart_character


def return_node(b,words,gi,token,reference=old,narrow=False):
    spec=reference.groups[gi]
    N=combine(words[spec['word']:spec['word']+2])
    L=combine(words[spec['word']+2:spec['word']+4])
    F=token['pole']
    heads=[words[2*i:2*i+2] for i in range(2*gi)]
    params=[];corr=0;delta=1
    for i in range(2*gi):
        q=reference.ks[i]^spec['kap'];assert q
        params.append((q,corr));corr^=inv(q);delta=mul(delta,q)
    assert corr==0
    with b.mark('column_source'):
        (a,c),restore=banked_column.prepare(b,words,gi,reference)
    with b.mark('column_recovery'):
        ell=b.alloc_qubits(24)
        b.cx(F,N[0]);mul24_xor99(b,c,N,ell,K);b.cx(F,N[0])
        b.cx(a,ell);b.ccx(F,a,ell);scalepair(b,ell,inv(delta))
    with b.mark('column_source_return'):
        restore()
    if narrow:
        from narrow_gauge import invert24, scale_pair, divide_pair, divide_pair_and_invert, close_chart
        if narrow in ('shared','fused','tokenfused'):
            with b.mark('payload_unnormalize'):
                b.cx(F,N[0])
                reference.external_square24(b,L,True)
                if narrow in ('fused','tokenfused'):
                    divide_pair_and_invert(b,[N,L],ell,token['norm'] if narrow=='tokenfused' else None)
                else:divide_pair(b,[N,L],ell)
                reference.external_square24(b,L)
        if narrow not in ('fused','tokenfused'):
            with b.mark('gauge_inverse'):invert24(b,ell)
        D=ell
        if narrow not in ('shared','fused','tokenfused'):
            with b.mark('payload_unnormalize'):
                b.cx(F,N[0])
                reference.external_square24(b,L,True)
                scale_pair(b,[N,L],D)
                reference.external_square24(b,L)
        if narrow!='tokenfused':
            with b.mark('old_token_closure'):
                assert isinstance(token['norm'],dict) and 'gauge' not in token
                close_chart(b,D,token['norm'])
    else:
        with b.mark('gauge_inverse'):
            D=b.alloc_qubits(24);b.cx(ell,D)
            inverse24_reverse209(b,D,zero_mask(b),K)
        with b.mark('payload_unnormalize'):
            b.cx(F,N[0])
            nm=multiply_forward99(b,N,D,K)
            phase_product24(b,N,ell,nm,K);b.free(nm)
            reference.external_square24(b,D);reference.external_square24(b,ell)
            lm=multiply_forward99(b,L,D,K)
            phase_product24(b,L,ell,lm,K);b.free(lm)
            reference.external_square24(b,ell,True);reference.external_square24(b,D,True)
            em=b.alloc_bits(24);b.hmr(ell,em);b.free(ell)
            close_inverse_character(b,D,em);b.free(em)
        with b.mark('old_token_closure'):
            if isinstance(token['norm'],dict):
                close_chart_character(b,D,token['norm'])
                assert 'gauge' not in token
            else:
                b.cz(D,token['gauge']);b.free(token['gauge'])
                norm=b.alloc_qubits(12);norm_xor_noscratch(b,D,norm,K)
                old.phase_inverse34(b,norm,token['norm']);b.free(token['norm'])
                ar._erase_norm(b,D,norm,K);b.free(norm)
    with b.mark('pole_retirement'):
        b.ccx(F,N,D)
        fm=b.alloc_bits(1);b.hmr(F,fm[0]);b.free(F)
        phase_zero(b,D,fm[0]);b.free(fm)
    with b.mark('inverse_traversal'):
        for head,(q,corr) in reversed(list(zip(heads,params))[1:]):
            reference.external_chain_step(b,head,N,D,L,q,spec['c'],corr,True)
        q0=params[0][0]
        scalepair(b,N,inv(q0));b.swap(N,D);scalepair(b,L,inv(q0))
        ah,hh=heads[0]
        cx(b,hh,ah,spec['c']);b.cx(combine(heads[0]),N);cx(b,hh,ah,spec['c'])
        b.cx(hh,L[:12]);b.x(D[0]);b.free(D)
