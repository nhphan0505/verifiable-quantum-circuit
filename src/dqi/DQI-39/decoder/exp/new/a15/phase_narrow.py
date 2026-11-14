"""Exact quantum-coefficient inverse12 phase, with ten private qubits.

Combines the supplied 29T/3-fresh exact GF64 inverse with the supplied
four-scratch GF64 inverse character. Resource claims belong to the whole
checker; the explicit source count is at most93T, depending on mask zero.
"""
from phase_quantum import ar, norm_xor_noscratch, phase_product_quantum
from streamed import inverse6_unitary29
from exact_subs import phase_inverse6_quad4


def phase_inverse12_quantum10(b,x,co):
    to,back,K=ar.tower(12);ar.linear_inplace(b,x,to)
    trans=[sum(((back[j]>>i)&1)<<j for j in range(12)) for i in range(12)]
    ar.linear_inplace(b,co,trans)
    N=b.alloc_qubits(6);norm_xor_noscratch(b,x,N,K)
    inverse6_unitary29(b,N)
    b.cx(x[6:],x[:6])
    phase_product_quantum(b,x[:6],N,co[:6])
    phase_product_quantum(b,x[6:],N,co[6:])
    b.cx(x[6:],x[:6])
    mask=b.alloc_bits(6);b.hmr(N,mask);b.free(N)
    N=b.alloc_qubits(6);norm_xor_noscratch(b,x,N,K)
    phase_inverse6_quad4(b,N,mask);b.free(mask)
    ar._erase_norm(b,x,N,K);b.free(N)
    ar.linear_inplace(b,co,ar.inverse_columns(trans));ar.linear_inplace(b,x,back)
