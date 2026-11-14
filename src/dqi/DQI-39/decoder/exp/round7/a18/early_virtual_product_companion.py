"""Close both direct products using one preserved reciprocal norm.

Their classical masks are contracted into the99-term extension tensor.
The final inverse-norm erasure is explicitly paid against the true norm.
"""
from types import FunctionType
from early_product_companion import *
import early_product_companion as prior
from exp.mul99.kernels import tensor99_extension
from exp.mul99.phase36 import phase_classical_parity


def phase_three_factor(b,x,C,u,mask):
    """Phase <mask,x*C*u>, u in the scalar subfield; no fresh qubit."""
    f=ar.field(12)
    for sm,v in tensor99_extension(K):
        co=b.alloc_bits(12);b.bit_store(co,False)
        for j in range(12):
            lo=f.mul(v&4095,1<<j);hi=f.mul(v>>12,1<<j)
            for k in ar.bits(lo):b.cx(mask[k],co[j])
            for k in ar.bits(hi):b.cx(mask[k+12],co[j])
        ix=list(ar.bits(sm));p=ix[0]
        for j in ix[1:]:b.cx(x[j],x[p]);b.cx(C[j],C[p])
        phase_classical_parity(b,x[p],C[p],u,co)
        for j in reversed(ix[1:]):b.cx(C[j],C[p]);b.cx(x[j],x[p])
        b.free(co)


def multiply_pair_and_restore(b,targets,C,F,old_g):
    masks=[multiply_forward99(b,x,C,K)for x in targets]
    u=b.alloc_qubits(12);norm_xor_noscratch(b,C,u,K)
    nm=inverse_stream_noscratch(b,u);ar._phase_norm(b,C,nm,K);b.free(nm)
    # The selected raw high coordinate of1/C is a component ofC times u.
    b.cswap(F,C[:12],C[12:]);ar.phase_product(b,C[12:],u,old_g);b.cswap(F,C[:12],C[12:]);b.free(old_g)
    b.cx(C[12:],C[:12])
    for x,m in zip(targets,masks):phase_three_factor(b,x,C,u,m);b.free(m)
    b.cx(C[12:],C[:12])
    im=b.alloc_bits(12);b.hmr(u,im);b.free(u)
    norm=b.alloc_qubits(12);norm_xor_noscratch(b,C,norm,K)
    phase_inverse36_pivot(b,norm,im);b.free(im);ar._erase_norm(b,C,norm,K);b.free(norm)


finish_factory=FunctionType(prior.finish_factory.__code__,dict(prior.finish_factory.__globals__,
                                  multiply_pair_and_restore=multiply_pair_and_restore),
                            prior.finish_factory.__name__,prior.finish_factory.__defaults__,prior.finish_factory.__closure__)
install=FunctionType(prior.install.__code__,dict(prior.install.__globals__,finish_factory=finish_factory),
                    prior.install.__name__,prior.install.__defaults__,prior.install.__closure__)
