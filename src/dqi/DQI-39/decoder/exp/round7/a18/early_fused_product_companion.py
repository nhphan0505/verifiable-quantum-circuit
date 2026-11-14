"""Fuse both old-N and restored-gauge ratio characters before retirement.

The same exact inverse-g character closes the measured low numerator and
measured projective coordinate. Its source is held at that point and the
remaining high-source mask is repaid by the direct product's reciprocal norm.
"""
from types import FunctionType
from early_virtual_product_companion import *
import early_virtual_product_companion as prior


def finish_factory(reference,scope):
    cx=scope['cx']
    def finish(b,D,F,forward,reverse,N,L,R,head,ct):
        assert reverse=='a18_early_shared'
        r,g=D[:12],D[12:];a,h=head;original=b.alloc_bits(24)
        with b.mark('fused_old_numerator_gauge'):
            cx(b,h,a,ct);b.cx(a,N[12:]);cx(b,h,a,ct)
            b.hmr(N[12:],original[:12]);b.swap(N[12:],R[:12]);b.free(R[:12])
            rgm=inverse_stream_noscratch(b,g);rrm=scale_defer(b,r,g);rim=inverse_stream_noscratch(b,g)
            b.cz(g,rgm);b.free(rgm);ar.phase_product(b,r,g,rrm);b.free(rrm)
            merged_chart(b,r,F);gm=scale_defer(b,g,r);merged_chart(b,r,F,True)
            hm=inverse_stream_noscratch(b,g);vm=scale_defer(b,N[:12],g)
            # g=t=1/(g_raw*q). The first inverse-g mask is now t*q.
            merged_chart(b,r,F);ar.phase_product(b,g,r,rim);b.free(rim);merged_chart(b,r,F,True)
            b.x(r[0]);b.cx(F,r[0]);ar.phase_product(b,r,N[:12],original[:12])
            rm=scale_defer(b,r,g)
            # Both overwritten coordinates are divided by the same heldt.
            linear_inverse_character(b,g,hm,[(N[:12],vm),(r,rm)])
            b.free(hm);b.free(vm);b.free(rm)
            b.cx(h,N[:12]);b.hmr(N[:12],original[12:]);b.swap(N[:12],R[12:]);b.free(R[12:]);b.swap(N[:12],N[12:])
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
