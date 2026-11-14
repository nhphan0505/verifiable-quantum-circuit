"""Delay the top source until the payload division has released its output.

This is a new schedule; the four earlier stage candidates are frozen.
"""
from functools import partial
from retired_top_block import *
from split_top_block import split_coefficient_product
from dirty_top_block import DirtyTopOverlap
from sqrt_top_block import SqrtTopOverlap,LateSqrtTopOverlap

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
    with b.mark('reconstruct_top'):source.restore_top_at_consumer(b,words)
    top=source.state['top']
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


def make_return(first=16,last=8,source_type=DirtyTopOverlap,defer_inverse=True):
    source=source_type(first,last)
    def return_node(b,words,gi,token,reference=old,narrow=None):
        spec=reference.groups[gi]
        N=combine(words[spec['word']:spec['word']+2]);L=combine(words[spec['word']+2:spec['word']+4])
        F=token['pole'];heads=[words[2*i:2*i+2]for i in range(2*gi)]
        params=[];delta=1;corr=0
        for i in range(2*gi):
            q=reference.ks[i]^spec['kap'];params.append((q,corr));delta=mul(delta,q);corr^=inv(q)
        assert corr==0
        with b.mark('block_source'):(a,c),restore=source.prepare(b,words,gi,reference)
        if defer_inverse and 'inverse_debts' not in source.state:
            source.state.update(defer_inverse=True,inverse_debts=[])
        with b.mark('retire_top_before_gauge'):source.retire_top_before_gauge(b,gi)
        with b.mark('column_recovery'):
            D=b.alloc_qubits(24)
            b.cx(F,N[0]);mul24_xor99(b,c,N,D,K);b.cx(F,N[0])
            b.cx(a,D);b.ccx(F,a,D);scalepair(b,D,inv(delta))
        with b.mark('block_source_return'):restore()
        with b.mark('payload_unnormalize'):
            b.cx(F,N[0]);reference.external_square24(b,L,True)
            divide_pair_and_invert(b,[N,L],D,token['norm']);reference.external_square24(b,L)
        with b.mark('pole_retirement'):
            b.ccx(F,N,D);m=b.alloc_bits(1);b.hmr(F,m[0]);b.free(F)
            phase_zero(b,D,m[0]);b.free(m)
        with b.mark('inverse_traversal'):
            for i in reversed(range(3,len(heads))):
                q,corr=params[i]
                reference.external_chain_step(b,heads[i],N,D,L,q,spec['c'],corr,True)
            if source.state['flag'] is None:source.state['flag']=zero_flag(b,combine(words[2:4]))
            with b.mark('two_head_block'):two_head_return(b,words,gi,N,D,L,params,source,reference)
            q0=params[0][0];scalepair(b,N,inv(q0));b.swap(N,D);scalepair(b,L,inv(q0))
            ah,hh=heads[0];cx(b,hh,ah,spec['c']);b.cx(combine(heads[0]),N);cx(b,hh,ah,spec['c'])
            b.cx(hh,L[:12]);b.x(D[0]);b.free(D)
        if gi==last:
            with b.mark('final_head_decode'):
                h1,h2=words[2:4],words[4:6]
                source._decode(b,h1,h2);source._retire_top(b,h1,h2)
                f=source.state['flag']
                if defer_inverse:
                    with b.mark('shared_inverse_characters'):
                        close_inverse_debts(b,h1,f,source.state.pop('inverse_debts'))
                m=b.alloc_bits(1);b.hmr(f,m[0]);b.free(f)
                fd=source.state.pop('flag_debt');b.cx(fd,m);b.free(fd)
                phase_zero(b,combine(h1),m[0]);b.free(m);source.state=None
    return return_node,source

make_sqrt_return=partial(make_return,source_type=SqrtTopOverlap)
make_late_sqrt_return=partial(make_return,source_type=LateSqrtTopOverlap)
