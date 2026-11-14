"""One controlled Toffoli per transvection of a fixed binary linear map."""
from functools import lru_cache


@lru_cache(None)
def factor(columns):
    """Return at most n constructive transvections.

    Every iteration fixes a new coordinate vector while preserving the
    already fixed coordinate vectors.  All arithmetic here is classical.
    """
    cols=list(columns);n=len(cols);ops=[]
    while any(x!=(1<<i) for i,x in enumerate(cols)):
        fixed={i for i,x in enumerate(cols) if x==(1<<i)}
        i=next(i for i in range(n) if i not in fixed)
        w=cols[i]^(1<<i)
        f=1<<i
        if w>>i&1:
            j=next(j for j in range(n) if j!=i and j not in fixed and w>>j&1)
            f^=1<<j
        assert (w&f).bit_count()%2==0 and f>>i&1
        cols=[z^(w if (z&f).bit_count()%2 else 0) for z in cols]
        ops.append((w,f))
        assert all(cols[j]==1<<j for j in fixed|{i})
    assert len(ops)<=n
    return tuple(reversed(ops))


def controlled(b,x,columns,flag):
    """x <- columns*x when flag is one; all bases and flag are preserved."""
    for w,f in factor(tuple(columns)):
        p=next(i for i in range(len(x)) if f>>i&1)
        others=[i for i in range(len(x)) if i!=p and f>>i&1]
        for i in others:b.cx(x[i],x[p])
        # In this parity frame, the direction has zero p coordinate.
        assert (w&f).bit_count()%2==0
        q=next(i for i in range(len(x)) if i!=p and w>>i&1)
        directions=[i for i in range(len(x)) if i!=p and i!=q and w>>i&1]
        for i in directions:b.cx(x[q],x[i])
        b.ccx(flag,x[p],x[q])
        for i in reversed(directions):b.cx(x[q],x[i])
        for i in reversed(others):b.cx(x[i],x[p])


def extension_scalar(b,x,value,flag):
    from exp.decoder.common import mul
    cols=tuple(mul(value,1<<i) for i in range(12))
    controlled(b,x[:12],cols,flag);controlled(b,x[12:],cols,flag)
