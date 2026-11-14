"""Full column return with measured constant source and payload endpoints."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'exp/round7/a02')]
from interleaved_column import old,combine,cx,mul,inv,scalepair,K,phase_zero,mul24_xor99
from narrow_gauge import divide_pair_and_invert
from exp.arithmetic.division import phase_product24
from column_erase_tail import prepare


def second_return(b,head,N,D,L,q,q0,ct,corr,reference):
    """Undo head1 when its previous numerator is the constant q0.

    After the swap, N=q0+H1*D. Measure N and pay that exact character;
    only the derivative product remains. No variable denominator is used.
    """
    scalepair(b,N,inv(q));b.swap(N,D);scalepair(b,L,inv(q))
    mask=b.alloc_bits(24);b.hmr(N,mask)
    ah,hh=head;cx(b,hh,ah,ct)
    phase_product24(b,combine(head),D,mask,K)
    cx(b,hh,ah,ct)
    for j in range(12):
        if q0>>j&1:b.z(mask[j]);b.x(N[j])
    b.free(mask)
    reference.external_square24(b,D)
    reference.external_corrected_product(b,head,D,L,ct,corr)
    reference.external_square24(b,D,True)


def return_node(b,words,gi,token,reference=old,narrow=None):
    spec=reference.groups[gi]
    N=combine(words[spec['word']:spec['word']+2])
    L=combine(words[spec['word']+2:spec['word']+4])
    F=token['pole'];heads=[words[2*i:2*i+2] for i in range(2*gi)]
    params=[];delta=1;corr=0
    for i in range(2*gi):
        q=reference.ks[i]^spec['kap'];params.append((q,corr))
        delta=mul(delta,q);corr^=inv(q)
    assert corr==0
    with b.mark('column_source'):(a,c),restore=prepare(b,words,gi,reference)
    with b.mark('column_recovery'):
        D=b.alloc_qubits(24)
        b.cx(F,N[0]);mul24_xor99(b,c,N,D,K);b.cx(F,N[0])
        b.cx(a,D);b.ccx(F,a,D);scalepair(b,D,inv(delta))
    with b.mark('column_source_return'):restore()
    with b.mark('payload_unnormalize'):
        b.cx(F,N[0]);reference.external_square24(b,L,True)
        divide_pair_and_invert(b,[N,L],D,token['norm'])
        reference.external_square24(b,L)
    with b.mark('pole_retirement'):
        b.ccx(F,N,D)
        mask=b.alloc_bits(1);b.hmr(F,mask[0]);b.free(F)
        phase_zero(b,D,mask[0]);b.free(mask)
    with b.mark('inverse_traversal'):
        for i in reversed(range(2,len(heads))):
            q,corr=params[i]
            reference.external_chain_step(b,heads[i],N,D,L,q,spec['c'],corr,True)
        q,corr=params[1];q0=params[0][0]
        second_return(b,heads[1],N,D,L,q,q0,spec['c'],corr,reference)
        scalepair(b,N,inv(q0));b.swap(N,D);scalepair(b,L,inv(q0))
        ah,hh=heads[0]
        cx(b,hh,ah,spec['c']);b.cx(combine(heads[0]),N);cx(b,hh,ah,spec['c'])
        b.cx(hh,L[:12]);b.x(D[0]);b.free(D)
