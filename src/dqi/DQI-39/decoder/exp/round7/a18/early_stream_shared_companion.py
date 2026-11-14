"""Close the early gauge conversion at its real restored endpoint.

The complete width-cut source is unchanged. The conversion C->1/C now
returns one actual C-character, paid when the two-target shared divider
restores C. This replaces the earlier fully coherent inversion.
"""
from types import FunctionType
import inspect
import early_shared_companion as prior
from exp.decoder.common import ar,K
from exp.noscratch.schedules import norm_xor_noscratch,inverse_stream_noscratch


def invert24_deferred(b,D):
    n=b.alloc_qubits(12);norm_xor_noscratch(b,D,n,K)
    nm=inverse_stream_noscratch(b,n);ar._phase_norm(b,D,nm,K);b.free(nm)
    b.cx(D[12:],D[:12]);mask=b.alloc_bits(24)
    for off in(0,12):
        half=D[off:off+12];out=b.alloc_qubits(12);ar.mul_xor0(b,half,n,out)
        b.hmr(half,mask[off:off+12]);b.swap(half,out);b.free(out)
    ar._erase_norm(b,D,n,K);b.free(n)
    # The measured old halves were conjugate(C).
    b.cx(mask[:12],mask[12:])
    return mask


source=inspect.getsource(prior.finish_factory)
assert source.count('invert24(b,D)')==1
source=source.replace('invert24(b,D)','dm=invert24_deferred(b,D)')
source=source.replace('divide_pair_and_invert(b,[N,L],D)','divide_pair_and_invert(b,[N,L],D)\n            b.cz(D,dm);b.free(dm)')
scope=dict(prior.finish_factory.__globals__,invert24_deferred=invert24_deferred)
exec(compile(source,__file__,'exec'),scope)
finish_factory=scope['finish_factory']
install=FunctionType(prior.install.__code__,dict(prior.install.__globals__,finish_factory=finish_factory),
                     prior.install.__name__,prior.install.__defaults__,prior.install.__closure__)
normalize_first=prior.normalize_first
