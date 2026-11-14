"""Closed scalar division through the real GF64 norm;12fresh wires."""
from exp.decoder.common import ar
from exp.noscratch.schedules import norm_xor_noscratch,inverse_stream_noscratch
from phase_quantum import phase_inverse6_9


def divide(b,x,y):
    to,back,K=ar.tower(12)
    # The rank42 product is in canonical coordinates, not tower coordinates.
    ar.linear_inplace(b,y,to);b.cx(y[6:],y[:6]);ar.linear_inplace(b,y,back)
    out=b.alloc_qubits(12);ar.mul_xor0(b,x,y,out)
    old=b.alloc_bits(12);b.hmr(x,old);b.swap(x,out);b.free(out)
    ar.linear_inplace(b,y,to);b.cx(y[6:],y[:6])
    u=b.alloc_qubits(6);norm_xor_noscratch(b,y,u,K)
    nm=inverse_stream_noscratch(b,u);ar._phase_norm(b,y,nm,K);b.free(nm)
    ar.linear_inplace(b,x,to);halves=[]
    for off in(0,6):
        half=x[off:off+6];out=b.alloc_qubits(6);ar.mul_xor0(b,half,u,out)
        m=b.alloc_bits(6);b.hmr(half,m);b.swap(half,out);b.free(out);halves.append(m)
    im=b.alloc_bits(6);b.hmr(u,im);b.free(u)
    n=b.alloc_qubits(6);norm_xor_noscratch(b,y,n,K)
    for off,m in zip((0,6),halves):ar.phase_product(b,x[off:off+6],n,m);b.free(m)
    phase_inverse6_9(b,n,im);b.free(im);ar._erase_norm(b,y,n,K);b.free(n)
    ar.linear_inplace(b,x,back);ar.linear_inplace(b,y,back)
    ar.phase_product(b,x,y,old);b.free(old)
