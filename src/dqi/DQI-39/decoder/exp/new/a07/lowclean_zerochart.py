"""Use the completed zero scale to remove the subfield chart correction."""
from functools import lru_cache
from types import FunctionType
import lowclean_batched as old
from lowclean_batched import ar


@lru_cache(None)
def chart_columns(n,K):
    f=ar.field(n)
    # Raw qF=0; every scale clips this to its effective multiplier1.
    cols=tuple((f.square(1<<i)^(1<<i))|((i==0)<<n) for i in range(n))+(K,)
    return cols,tuple(ar.inverse_columns(cols))


def chart(b,r,F,K,reverse=False):
    cols,back=chart_columns(len(r),K)
    if reverse:b.gf2_iadd(K,target=r);ar.linear_inplace(b,list(r)+[F],back)
    else:ar.linear_inplace(b,list(r)+[F],cols);b.gf2_iadd(K,target=r)
    return 1 # Effective nonzero multiplier used in the F=1 correction.


scope=dict(old.__dict__,chart=chart)
scale_many=FunctionType(old.scale_many.__code__,scope,'scale_many')
scale=FunctionType(old.scale.__code__,scope,'scale')
iscope=dict(old.inverse.__globals__,chart=chart,scale=scale)
inverse=FunctionType(old.inverse.__code__,iscope,'inverse')
iscope['inverse']=inverse
scope.update(scale=scale,scale_many=scale_many,inverse=inverse)
stream=FunctionType(old.stream.__code__,scope,'stream')
scale_defer=FunctionType(old.scale_defer.__code__,scope,'scale_defer')
many_defer=FunctionType(old.many_defer.__code__,scope,'many_defer')
inverse_phase=FunctionType(old.inverse_phase.__code__,scope,'inverse_phase')
