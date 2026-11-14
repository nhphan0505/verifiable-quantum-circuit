"""Predicate-controlled Frobenius in a normal basis using dirty borrowing.

Frob is a cyclic bit rotation; reversing that cycle conjugates it to its
inverse. Six predicate bits cost32T for the two dirty-flag toggles.
"""
from functools import lru_cache
from dirty_norm_control import ar,mcx_dirty


@lru_cache(None)
def normal_basis(n):
    f=ar.field(n)
    for a in range(2,1<<n):
        columns=[];v=a
        for _ in range(n):columns.append(v);v=f.square(v)
        try:frame=tuple(ar.inverse_columns(tuple(columns)))
        except (AssertionError,ValueError,StopIteration):continue
        assert tuple(ar.apply(frame,f.square(v))for v in columns)==tuple(1<<((j+1)%n)for j in range(n))
        return frame,tuple(columns)
    raise AssertionError(('No normal basis',n))


def controlled_frobenius(b,x,key,borrow,inverse=False):
    n=len(x);frame,back=normal_basis(n);ar.linear_inplace(b,x,frame)
    h=borrow[0];scratch=borrow[1:]
    def reflection():
        for j in range(1,(n+1)//2):b.cswap(h,x[j],x[n-j])
    def cycle(inv):
        for j in reversed(range(1,n))if inv else range(1,n):b.cswap(h,x[0],x[j])
    reflection();mcx_dirty(b,key,h,scratch);cycle(inverse)
    mcx_dirty(b,key,h,scratch);cycle(not inverse);reflection()
    ar.linear_inplace(b,x,back)
