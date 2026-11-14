"""All16finite GF16 places and infinity, same degree-six field basis."""
from functools import lru_cache
from defect_tensor import ar,emul,transpose,dual
from eval_blocks import blocks as supplied,trace_mask
from exp.mul99.kernels import tensor4

@lru_cache(None)
def evaluations():
    base=supplied();f=ar.field(4);out=[]
    for p in range(16):
        if p<10:out.append(base[p][0]);continue
        weights=[]
        for i in range(6):
            top=bottom=1
            for j in range(6):
                if i==j:continue
                top=f.mul(top,p^j);bottom=f.mul(bottom,i^j)
            weights.append(f.mul(top,f.invert(bottom)))
        cols=[]
        for k in range(24):
            v=0
            for i,w in enumerate(weights):v^=f.mul(w,base[i][0][k])
            cols.append(v)
        out.append(tuple(cols))
    out.append(base[10][0])
    return tuple(out)

def dual_representatives():return [dual(transpose(trace_mask(),ev)) for ev in evaluations()]

@lru_cache(None)
def selected_blocks(indices):
    assert len(indices)==11 and len(set(indices))==11
    evs=[evaluations()[j] for j in indices];low=tensor4()
    masks=[transpose(m,ev) for ev in evs for m,v in low]
    equations=[]
    for i in range(24):
        for j in range(i,24):
            row=sum((((m>>i)&1)&((m>>j)&1))<<r for r,m in enumerate(masks))
            equations.append((row,emul(1<<i,1<<j)))
    vectors=ar._solve_output_vectors(equations,len(masks))
    assert all(vectors)
    out=[]
    for k,ev in enumerate(evs):
        values=vectors[9*k:9*k+9]
        cols=tuple(ar._solve_output_vectors([(v,w) for (m,v),w in zip(low,values)],4))
        for (m,v),w in zip(low,values):assert ar.apply(cols,v)==w
        out.append((ev,cols))
    return tuple(out),tuple(zip(masks,vectors))
