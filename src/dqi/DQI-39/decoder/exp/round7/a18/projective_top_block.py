"""A completed projective source for the polynomial top.

Normalize H1 only inside the top consumer. Both chart-zero and every
inverse/ratio character are accumulated and repaid once at the final head.
"""
from functools import partial
from consumer_top_block import make_return as _make_return
from retired_top_block import *
from virtual_norm12 import encoded_norm12
from lowclean import controlled_linear
from core90 import affine_inverse_g_character


class ProjectiveTopOverlap(RetiredTopOverlap):
    def _start(self,b,words,gi):
        super()._start(b,words,gi)
        self.state.update(projective_debts=[mask_zero(b,12),mask_zero(b,12),mask_zero(b,1)])

    def restore_top_at_consumer(self,b,words):
        assert self.state['top'] is None
        h1,p=words[2:4],words[4:6];r,g=h1
        if self.state['flag'] is None:self.state['flag']=zero_flag(b,combine(h1))
        F=self.state['flag'];J=zero_flag(b,g)
        b.cswap(J,r,g);b.cx(F,g[0])
        gi=b.alloc_qubits(12);b.cx(g,gi)
        gm=inverse_stream_noscratch(b,gi);b.cz(g,gm);b.free(gm)
        out=b.alloc_qubits(12);ar.mul_xor0(b,r,gi,out)
        m=b.alloc_bits(12);b.hmr(r,m);b.swap(r,out);b.free(out)
        ar.phase_product(b,r,g,m);b.free(m)
        t=b.alloc_qubits(12);b.cx(p[0],t);ar.mul_xor0(b,p[1],r,t)
        with encoded_norm12(b,r,K) as apply:apply([t],True)
        f=ar.field(12);controlled_linear(b,t,[f.mul(K,1<<j)for j in range(12)],J)
        b.ccx(J,p[0],t)
        im=b.alloc_bits(12);b.hmr(gi,im);b.free(gi)
        b.cx(im,self.state['projective_debts'][0]);b.free(im)
        out=b.alloc_qubits(12);ar.mul_xor0(b,r,g,out)
        rm=b.alloc_bits(12);b.hmr(r,rm);b.swap(r,out);b.free(out)
        b.cx(rm,self.state['projective_debts'][1]);b.free(rm)
        b.cx(F,g[0]);b.cswap(J,r,g)
        jm=b.alloc_bits(1);b.hmr(J,jm[0]);b.free(J)
        b.cx(jm,self.state['projective_debts'][2]);b.free(jm)
        self.state['top']=t

    def _retire_top(self,b,h1,h2):
        super()._retire_top(b,h1,h2)
        r,g=h1;F=self.state['flag'];J=zero_flag(b,g)
        b.cswap(J,r,g);b.cx(F,g[0])
        im,rm,jm=self.state.pop('projective_debts');zero=mask_zero(b,12)
        affine_inverse_g_character(b,r,g,dict(i=im,r=rm,h=zero))
        b.free(im);b.free(rm);b.free(zero)
        b.cx(F,g[0]);b.cswap(J,r,g)
        m=b.alloc_bits(1);b.hmr(J,m[0]);b.free(J)
        b.cx(m,jm);b.free(m);phase_zero(b,g,jm[0]);b.free(jm)


make_return=partial(_make_return,source_type=ProjectiveTopOverlap)
