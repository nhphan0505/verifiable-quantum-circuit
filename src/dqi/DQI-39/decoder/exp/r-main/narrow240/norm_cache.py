"""Retain the most profitable norm coordinates within the live width ceiling."""
from functools import lru_cache
from exp.decoder.common import ar
from exp.noscratch.kernels import rankone_xor

TRACE=[]
FORCE=None

@lru_cache(None)
def layout(k):
    # Enumerate subspaces, not ordered bases. This is only six dimensions.
    tensor=ar.tensor(6)
    spaces={frozenset({0}):()}
    for dim in range(k):
        nxt={}
        for span,basis in spaces.items():
            for w in range(1,64):
                if w in span:continue
                full=span|{a^w for a in span}
                if full not in nxt:nxt[full]=basis+(w,)
        spaces=nxt
    span,columns=max(spaces.items(),key=lambda item:(sum(v in item[0] for _,v in tensor),item[1]))
    columns=list(columns)
    for w in (1,2,4,8,16,32):
        if w not in span:
            columns.append(w);span=span|{a^w for a in span}
    return tuple(ar.inverse_columns(columns)),tuple(columns)

def keep(b,D):
    # D is already live; its streamed inverse needs six further wires.
    live=b.num_allocated_qubits
    k=min(6,max(0,889-live-6)) if FORCE is None else FORCE
    to,frm=layout(k)
    saved=b.alloc_qubits(k)
    ar.linear_xor(b,D,saved,[v&((1<<k)-1) for v in to])
    skipped=sum(ar.apply(to,v)>>k==0 for _,v in ar.tensor(6))
    TRACE.append(dict(live_with_D=live,kept=k,skipped=skipped,expected_peak=live+6+k))
    return saved

def rebuild(b,g,saved,K):
    k=len(saved);to,frm=layout(k)
    rest=b.alloc_qubits(6-k)
    square=ar.square_columns(6)
    ar.linear_xor(b,g[:6],rest,[ar.apply(to,v)>>k for v in square])
    ar.linear_xor(b,g[6:],rest,[ar.apply(to,ar.field(6).mul(K,v))>>k for v in square])
    for mask,vector in ar.tensor(6):
        vector=ar.apply(to,vector)>>k
        if not vector:continue
        ix=list(ar.bits(mask));p=ix[0]
        for j in ix[1:]:b.cx(g[j],g[p]);b.cx(g[j+6],g[p+6])
        rankone_xor(b,g[p],g[p+6],rest,vector)
        for j in reversed(ix[1:]):b.cx(g[j+6],g[p+6]);b.cx(g[j],g[p])
    D=list(saved)+list(rest)
    ar.linear_inplace(b,D,frm)
    return D
