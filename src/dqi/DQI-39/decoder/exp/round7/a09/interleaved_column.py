"""Source-complete column return with the two reverse sweeps interleaved.

The H1 head remains the column's second coordinate until both sweeps have
passed head2. It is restored before the homogeneous traversal uses head1.
This is an exact full replacement, initially retaining a wide bridge.
"""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'exp/round7/a02')]
from column_return import old
from narrow_gauge import divide_pair_and_invert
from exp.decoder.common import combine,cx,mul,inv,scalepair,K
from exp.mul99.schedules import mul24_xor99
from exp.arithmetic.division import phase_zero


def prepare(b,words,gi,reference):
    spec=reference.groups[gi]
    heads=[words[2*i:2*i+2] for i in range(2*gi)]
    qs=[reference.ks[i]^spec['kap'] for i in range(2*gi)]
    a=b.alloc_qubits(24)
    for j in range(12):
        if qs[1]>>j&1:b.x(a[j])
    c=combine(heads[1])
    cx(b,heads[1][1],heads[1][0],spec['c'])
    for i in range(2,len(heads)):
        reference.external_scalar_step(b,heads[i],a,c,qs[i],spec['c'])
    return a,c,heads,qs


def return_node(b,words,gi,token,reference=old,narrow=None):
    spec=reference.groups[gi]
    N=combine(words[spec['word']:spec['word']+2])
    L=combine(words[spec['word']+2:spec['word']+4])
    F=token['pole']
    with b.mark('column_source'):
        a,c,heads,qs=prepare(b,words,gi,reference)
    delta=1;corr=0;params=[]
    for q in qs:
        params.append((q,corr));delta=mul(delta,q);corr^=inv(q)
    assert corr==0
    with b.mark('column_recovery'):
        D=b.alloc_qubits(24)
        b.cx(F,N[0]);mul24_xor99(b,c,N,D,K);b.cx(F,N[0])
        b.cx(a,D);b.ccx(F,a,D);scalepair(b,D,inv(delta))
    with b.mark('payload_unnormalize'):
        b.cx(F,N[0]);reference.external_square24(b,L,True)
        divide_pair_and_invert(b,[N,L],D,token['norm'])
        reference.external_square24(b,L)
    with b.mark('pole_retirement'):
        b.ccx(F,N,D)
        mask=b.alloc_bits(1);b.hmr(F,mask[0]);b.free(F)
        phase_zero(b,D,mask[0]);b.free(mask)
    with b.mark('interleaved_reverse'):
        for i in reversed(range(2,len(heads))):
            q,corr=params[i]
            reference.external_chain_step(b,heads[i],N,D,L,q,spec['c'],corr,True)
            reference.external_scalar_step(b,heads[i],a,c,q,spec['c'],True)
        cx(b,heads[1][1],heads[1][0],spec['c'])
        for j in range(12):
            if qs[1]>>j&1:b.x(a[j])
        b.free(a)
        q,corr=params[1]
        reference.external_chain_step(b,heads[1],N,D,L,q,spec['c'],corr,True)
        q0=qs[0]
        scalepair(b,N,inv(q0));b.swap(N,D);scalepair(b,L,inv(q0))
        ah,hh=heads[0]
        cx(b,hh,ah,spec['c']);b.cx(combine(heads[0]),N);cx(b,hh,ah,spec['c'])
        b.cx(hh,L[:12]);b.x(D[0]);b.free(D)
