"""Retire the old numerator before opening the shared norm bank.

The first selected half has a fully charged width-adaptive preserved source.
Its deferred shear is paid before the second old half is erased. The true
reciprocal gauge is restored, including every source mask, before the two
remaining payloads enter the common norm block.
"""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'exp/next/a07'),str(ROOT/'exp/next/a13'),
             str(ROOT/'exp/next/a19'),str(ROOT/'exp/r-main/narrow240')]
from direct_owned_companion import clone,forward_owner
from direct_deferred_companion import normalize_with_token,node_context
from direct_shared_companion import functions
from narrow_gauge import invert24,divide_pair_and_invert
from retained_core_safe27 import (ar,correct_subfield,merged_chart,scale_defer,
                                 inverse_stream_noscratch,linear_inverse_character,
                                 phase_inverse36_pivot)
from exp.arithmetic.division import phase_zero
from lowclean import zero_toggle
import log_source_cap898 as cap
import no_clean_source12_frobenius as borrowed


def normalize_first(b,N,D,L,R):
    r,g=D[:12],D[12:]
    F=b.alloc_qubits(1)[0];zero_toggle(b,g,F,r);b.cswap(F,r,g)
    correct_subfield(b,N,F)
    with b.mark('first_half_source'):
        if b.num_allocated_qubits>=892:
            with borrowed.source(b,g,L[:8],True) as apply:apply([N[12:]])
        else:
            with cap.source(b,g,True) as apply:apply([N[12:]])
    ar.mul_xor0(b,r,N[12:],N[:12])
    return 'a18_early_shared',F


def finish_factory(reference,scope):
    cx=scope['cx']
    def finish(b,D,F,forward,reverse,N,L,R,head,ct):
        assert reverse=='a18_early_shared'
        r,g=D[:12],D[12:];a,h=head;original=b.alloc_bits(24)
        with b.mark('early_old_numerator'):
            cx(b,h,a,ct);b.cx(a,N[12:]);cx(b,h,a,ct)
            b.hmr(N[12:],original[:12]);b.swap(N[12:],R[:12]);b.free(R[:12])
            rgm=inverse_stream_noscratch(b,g)
            rrm=scale_defer(b,r,g)
            rim=inverse_stream_noscratch(b,g)
            b.cz(g,rgm);b.free(rgm);ar.phase_product(b,r,g,rrm);b.free(rrm)
            merged_chart(b,r,F);gm=scale_defer(b,g,r);merged_chart(b,r,F,True)
            hm=inverse_stream_noscratch(b,g);vm=scale_defer(b,N[:12],g)
            linear_inverse_character(b,g,hm,[(N[:12],vm)]);b.free(hm);b.free(vm)
            b.x(r[0]);b.cx(F,r[0]);ar.phase_product(b,r,N[:12],original[:12])
            b.cx(h,N[:12]);b.hmr(N[:12],original[12:]);b.swap(N[:12],R[12:]);b.free(R[12:]);b.swap(N[:12],N[12:])
            b.cx(F,r[0]);b.x(r[0])
        with b.mark('direct_gauge_source_closure'):
            # g=t=1/(g_raw*q), r=a_raw/g_raw. Compute 1/g_raw=t*q
            # only after R has retired, then pay both actual source masks.
            merged_chart(b,r,F)
            v=b.alloc_qubits(12);ar.mul_xor0(b,g,r,v)
            b.cz(v,rim);b.free(rim);phase_inverse36_pivot(b,v,gm);b.free(gm)
            m=b.alloc_bits(12);b.hmr(v,m);b.free(v);ar.phase_product(b,g,r,m);b.free(m)
            merged_chart(b,r,F,True)
            b.x(r[0]);b.cx(F,r[0]);rm=scale_defer(b,r,g)
            zero=b.alloc_bits(12);b.bit_store(zero,False)
            linear_inverse_character(b,g,zero,[(r,rm)]);b.free(zero);b.free(rm)
            b.cswap(F,r,g);fm=b.alloc_bits(1);b.hmr(F,fm[0]);b.free(F)
            phase_zero(b,g,fm[0]);b.free(fm)
        b.cz(D,forward['gauge']);b.free(forward['gauge'])
        with b.mark('two_payload_shared_norm'):
            # This is a complete measured width trade: the real conversion
            # of C to1/C and all its signs precede the shared divider.
            invert24(b,D)
            reference.external_square24(b,L,True)
            divide_pair_and_invert(b,[N,L],D)
            reference.external_square24(b,L)
        b.cx(h,L[:12])
        return original
    return finish


def install(entry):
    seen=set();log=[]
    for fn in functions(entry):
        g=fn.__globals__
        if fn.__name__!='external_node_chain'or'finish_fused'not in fn.__code__.co_names:continue
        if id(g)in seen:continue
        seen.add(id(g));assert not fn.__closure__
        original=clone(fn,g);old_forward=g['forward_original'];selection=frozenset(g.get('SELECT',range(8,17)))
        new_forward=forward_owner(old_forward);reference=g['ref']
        def router(b,words,gi,reverse=False,token=None,normalizer=None,
                   _original=old_forward,_forward=new_forward,_select=selection):
            if not reverse and gi in _select:return _forward(b,words,gi,False,token,normalizer)
            return _original(b,words,gi,reverse,token,normalizer)
        context=dict(stack=[])
        g['forward_original']=router;g['finish_fused']=finish_factory(reference,g)
        g['normalize_three']=normalize_with_token(normalize_first,context)
        g.update(_a18_deferred_select=selection,_a18_deferred_context=context,_a18_deferred_original=original)
        fn.__code__=node_context.__code__
        log.append(dict(file=original.__code__.co_filename,select=sorted(selection)))
    assert log
    return log
