"""Keep two norm coordinates through streamed inversion.

Only terms with output outside their span are recomputed.  The old M6
measurement debt is still paid in its original polynomial coordinates.
"""
from functools import lru_cache
from exp.decoder.common import ar
from exp.noscratch.kernels import rankone_xor

@lru_cache(None)
def layout():
    tensor=ar.tensor(6)
    _,u,v=max((sum(w in (u,v,u^v) for _,w in tensor),u,v)
              for u in range(1,64) for v in range(u+1,64))
    columns=[u,v]
    span={0,u,v,u^v}
    for w in (1,2,4,8,16,32):
        if w not in span:
            columns.append(w);span|={a^w for a in tuple(span)}
    return tuple(ar.inverse_columns(columns)),tuple(columns)

def keep(b,M):
    to,_=layout()
    kept=b.alloc_qubits(2)
    ar.linear_xor(b,M,kept,[v&3 for v in to])
    return kept

def rebuild(b,N,kept,K):
    to,frm=layout()
    rest=b.alloc_qubits(4)
    square=ar.square_columns(6)
    ar.linear_xor(b,N[:6],rest,[ar.apply(to,v)>>2 for v in square])
    ar.linear_xor(b,N[6:],rest,[ar.apply(to,ar.field(6).mul(K,v))>>2 for v in square])
    for mask,vector in ar.tensor(6):
        vector=ar.apply(to,vector)>>2
        if not vector:continue
        ix=list(ar.bits(mask));p=ix[0]
        for j in ix[1:]:b.cx(N[j],N[p]);b.cx(N[j+6],N[p+6])
        rankone_xor(b,N[p],N[p+6],rest,vector)
        for j in reversed(ix[1:]):b.cx(N[j+6],N[p+6]);b.cx(N[j],N[p])
    M=list(kept)+list(rest)
    ar.linear_inplace(b,M,frm)
    return M
