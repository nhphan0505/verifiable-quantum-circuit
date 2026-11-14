"""Recover the11 GF16 evaluation/output blocks of the supplied tensor."""
from functools import lru_cache
from defect_tensor import ar,K,tensor99_extension,transpose,dual
from exp.mul99.kernels import tensor4

PAIR4=((1,7,140),(13,1,191),(12,8,45),(5,6,82),
       (4,3,17),(6,14,123),(11,9,55),(2,4,249),
       (7,5,234),(9,2,99),(8,12,182),(3,11,255))

@lru_cache(None)
def blocks():
    low=tensor4();top=tensor99_extension(K);out=[]
    for index in range(11):
        t=top[index*9:index*9+9]
        rows=ar._solve_output_vectors([(m,a) for (m,v),(a,w) in zip(low,t)],4)
        ev=tuple(sum(((row>>j)&1)<<k for k,row in enumerate(rows)) for j in range(24))
        cols=tuple(ar._solve_output_vectors([(v,w) for (m,v),(a,w) in zip(low,t)],4))
        for (m,v),(a,w) in zip(low,t):
            assert transpose(m,ev)==a and ar.apply(cols,v)==w
        out.append((ev,cols))
    return tuple(out)

@lru_cache(None)
def trace_mask():
    f=ar.field(4);mask=0
    for j in range(4):
        x=1<<j;t=x
        for _ in range(3):x=f.square(x);t^=x
        assert t in (0,1);mask|=t<<j
    return mask

def dual_representatives():return [dual(transpose(trace_mask(),ev)) for ev,out in blocks()]
