"""Early numerator retirement with an endpoint-paid direct multiplier.

C is held at both endpoints. The intermediate reciprocal pays both payload
characters and the actual first-half source character. The second consuming
inverse keeps its true norm long enough to pay its remaining inverse-C mask.
"""
from types import FunctionType
import early_shared_companion as prior
from early_shared_companion import *
from early_stream_shared_companion import invert24_deferred
from exp.mul99.schedules import multiply_forward99
from exp.arithmetic.division import phase_product24
from exp.noscratch.schedules import norm_xor_noscratch
from exp.decoder.common import K


def invert24_keep_norm(b,D):
    n=b.alloc_qubits(12);norm_xor_noscratch(b,D,n,K)
    nm=inverse_stream_noscratch(b,n);ar._phase_norm(b,D,nm,K);b.free(nm)
    b.cx(D[12:],D[:12]);mask=b.alloc_bits(24)
    for off in(0,12):
        half=D[off:off+12];out=b.alloc_qubits(12);ar.mul_xor0(b,half,n,out)
        b.hmr(half,mask[off:off+12]);b.swap(half,out);b.free(out)
    b.cx(mask[:12],mask[12:])
    return mask,n


def multiply_pair_and_restore(b,targets,C,F,old_g):
    masks=[multiply_forward99(b,x,C,K)for x in targets]
    direct=invert24_deferred(b,C)
    # Here C holds1/C_original; the original selected high component is
    # exactly the first-half source whose multiplication mask is old_g.
    b.cswap(F,C[:12],C[12:]);b.cz(C[12:],old_g);b.cswap(F,C[:12],C[12:]);b.free(old_g)
    for x,m in zip(targets,masks):phase_product24(b,x,C,m,K);b.free(m)
    reciprocal,norm=invert24_keep_norm(b,C)
    b.cz(C,direct);b.free(direct)
    # norm=Norm(C) and inverse(C)=conjugate(C)/norm.
    zero=b.alloc_bits(12);b.bit_store(zero,False);b.cx(C[12:],C[:12])
    linear_inverse_character(b,norm,zero,[(C[:12],reciprocal[:12]),(C[12:],reciprocal[12:])])
    b.cx(C[12:],C[:12]);b.free(zero);b.free(reciprocal)
    ar._erase_norm(b,C,norm,K);b.free(norm)


def finish_factory(reference,scope):
    cx=scope['cx']
    def finish(b,D,F,forward,reverse,N,L,R,head,ct):
        assert reverse=='a18_early_shared'
        r,g=D[:12],D[12:];a,h=head;original=b.alloc_bits(24)
        with b.mark('early_old_numerator'):
            cx(b,h,a,ct);b.cx(a,N[12:]);cx(b,h,a,ct)
            b.hmr(N[12:],original[:12]);b.swap(N[12:],R[:12]);b.free(R[:12])
            rgm=inverse_stream_noscratch(b,g);rrm=scale_defer(b,r,g);rim=inverse_stream_noscratch(b,g)
            b.cz(g,rgm);b.free(rgm);ar.phase_product(b,r,g,rrm);b.free(rrm)
            merged_chart(b,r,F);gm=scale_defer(b,g,r);merged_chart(b,r,F,True)
            hm=inverse_stream_noscratch(b,g);vm=scale_defer(b,N[:12],g)
            linear_inverse_character(b,g,hm,[(N[:12],vm)]);b.free(hm);b.free(vm)
            b.x(r[0]);b.cx(F,r[0]);ar.phase_product(b,r,N[:12],original[:12])
            b.cx(h,N[:12]);b.hmr(N[:12],original[12:]);b.swap(N[:12],R[12:]);b.free(R[12:]);b.swap(N[:12],N[12:])
            b.cx(F,r[0]);b.x(r[0])
        with b.mark('direct_gauge_source_closure'):
            merged_chart(b,r,F);ar.phase_product(b,g,r,rim);b.free(rim);merged_chart(b,r,F,True)
            b.x(r[0]);b.cx(F,r[0]);rm=scale_defer(b,r,g)
            zero=b.alloc_bits(12);b.bit_store(zero,False)
            linear_inverse_character(b,g,zero,[(r,rm)]);b.free(zero);b.free(rm)
            b.cswap(F,r,g)
        b.cz(D,forward['gauge']);b.free(forward['gauge'])
        with b.mark('two_payload_direct_product'):
            reference.external_square24(b,L,True)
            multiply_pair_and_restore(b,[N,L],D,F,gm)
            reference.external_square24(b,L)
        fm=b.alloc_bits(1);b.hmr(F,fm[0]);b.free(F);phase_zero(b,g,fm[0]);b.free(fm)
        b.cx(h,L[:12]);return original
    return finish


install=FunctionType(prior.install.__code__,dict(prior.install.__globals__,finish_factory=finish_factory),
                     prior.install.__name__,prior.install.__defaults__,prior.install.__closure__)
