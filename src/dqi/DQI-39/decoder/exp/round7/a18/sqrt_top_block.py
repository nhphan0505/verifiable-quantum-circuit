"""Top source from a square-root numerator identity.

For safe Y=u+h*x and P=p0+p1*x, n=Norm(Y), the true polynomial top
is t=p1+(h*sqrt(p0+K*p1)+u*sqrt(p1))^2/n. This holds when h=0 too.
"""
from functools import partial
from retired_top_block import *
from retired_top_block import make_return as _make_return


class SqrtTopOverlap(RetiredTopOverlap):
    retire_through=8
    def _start(self,b,words,gi):
        super()._start(b,words,gi)
        self.state['sqrt_norm_debt']=mask_zero(b,12)

    def retire_top_before_gauge(self,b,gi):
        if gi>=self.retire_through:super().retire_top_before_gauge(b,gi)

    def restore_top_at_consumer(self,b,words):
        if self.state['top'] is not None:return
        h1,p=words[2:4],words[4:6];u,h=h1
        if self.state['flag'] is None:self.state['flag']=zero_flag(b,combine(h1))
        flag=self.state['flag'];b.cx(flag,u[0]);y=combine(h1);f=ar.field(12)
        sqrt=tuple(f.frobenius(1<<j,11)for j in range(12))
        square=tuple(f.square(1<<j)for j in range(12))
        n=b.alloc_qubits(12);norm_xor_noscratch(b,y,n,K)
        ar.linear_inplace(b,n,sqrt)
        nm=inverse_stream_noscratch(b,n)
        old=classical_transpose(b,nm,sqrt);b.free(nm)
        ar._phase_norm(b,y,old,K);b.free(old)
        cx(b,p[1],p[0],K)
        ar.linear_inplace(b,p[0],sqrt);ar.linear_inplace(b,p[1],sqrt)
        t=b.alloc_qubits(12)
        ar.mul_xor0(b,h,p[0],t);ar.mul_xor0(b,u,p[1],t)
        out=b.alloc_qubits(12);ar.mul_xor0(b,t,n,out)
        m=b.alloc_bits(12);b.hmr(t,m);b.swap(t,out);b.free(out)
        ar.phase_product(b,h,p[0],m);ar.phase_product(b,u,p[1],m);b.free(m)
        ar.linear_inplace(b,p[0],square);ar.linear_inplace(b,p[1],square)
        cx(b,p[1],p[0],K)
        ar.linear_inplace(b,t,square);b.cx(p[1],t)
        im=b.alloc_bits(12);b.hmr(n,im);b.free(n)
        trans=classical_transpose(b,im,sqrt);b.free(im)
        b.cx(trans,self.state['sqrt_norm_debt']);b.free(trans)
        b.cx(flag,u[0]);self.state['top']=t

    def _retire_top(self,b,h1,h2):
        super()._retire_top(b,h1,h2)
        f=self.state['flag'];y=combine(h1);b.cx(f,y[0])
        n=b.alloc_qubits(12);norm_xor_noscratch(b,y,n,K)
        m=self.state.pop('sqrt_norm_debt');phase_inverse36_pivot(b,n,m);b.free(m)
        ar._erase_norm(b,y,n,K);b.free(n);b.cx(f,y[0])


class LateSqrtTopOverlap(SqrtTopOverlap):
    retire_through=15


make_return=partial(_make_return,source_type=SqrtTopOverlap)
make_late_return=partial(_make_return,source_type=LateSqrtTopOverlap)
