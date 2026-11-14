"""Retire the polynomial top, using a paid coherent no-clean norm source."""
from functools import partial
from pathlib import Path
import sys
from split_top_block import *
from split_top_block import make_return as _make_return
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'exp/next/a19'),str(ROOT/'exp/next/a13')]
from no_clean_source12_frobenius import source as norm_source


class DirtyTopOverlap(RetiredTopOverlap):
    def restore_top_at_consumer(self,b,words):
        assert self.state['top'] is None
        h1,p=words[2:4],words[4:6];u,h=h1
        if self.state['flag'] is None:self.state['flag']=zero_flag(b,combine(h1))
        f=self.state['flag'];b.cx(f,u[0]);y=combine(h1)
        t=b.alloc_qubits(12)
        ar.mul_xor0(b,h,p[0],t);ar.mul_xor0(b,u,p[1],t)
        out=b.alloc_qubits(12);ar.mul_xor0(b,h,t,out)
        m=b.alloc_bits(12);b.hmr(t,m);b.swap(t,out);b.free(out)
        ar.phase_product(b,h,p[0],m);ar.phase_product(b,u,p[1],m);b.free(m)
        n=b.alloc_qubits(12);norm_xor_noscratch(b,y,n,K)
        with norm_source(b,n,list(words[6][:8]),inverse=True) as apply:apply([t])
        ar._erase_norm(b,y,n,K);b.free(n);b.cx(f,u[0])
        self.state['top']=t


make_return=partial(_make_return,source_type=DirtyTopOverlap)
