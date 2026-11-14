"""Erase the constant endpoint of the column return by its exact character.

The final source undo reaches a=q2*H1, c=q1+H2*H1. Its c register can
be measured and restored from a instead of computing the final99T product.
"""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'exp/round7/a02')]
from interleaved_column import prepare as prepare_parts
from exp.decoder.common import combine,cx,scalepair,inv,K
from exp.arithmetic.division import phase_product24


def finish(b,a,c,heads,qs,spec):
    scalepair(b,a,inv(qs[2]))
    mask=b.alloc_bits(24);b.hmr(c,mask)
    ah,hh=heads[2];cx(b,hh,ah,spec['c'])
    phase_product24(b,combine(heads[2]),a,mask,K)
    cx(b,hh,ah,spec['c'])
    for j in range(12):
        if qs[1]>>j&1:b.z(mask[j])
    b.free(mask)
    b.cx(a,c);b.cx(c,a);b.free(a)
    cx(b,heads[1][1],heads[1][0],spec['c'])


def prepare(b,words,gi,reference):
    a,c,heads,qs=prepare_parts(b,words,gi,reference)
    spec=reference.groups[gi]
    def restore():
        for i in reversed(range(3,len(heads))):
            reference.external_scalar_step(b,heads[i],a,c,qs[i],spec['c'],True)
        finish(b,a,c,heads,qs,spec)
    return (a,c),restore
