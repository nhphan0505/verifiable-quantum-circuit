"""Eight-Toffoli dirty-controlled inv0 in GF8;54T dirty GF64 inv0.

GF8 inversion is conjugate, by two transpositions, to an OR-controlled
bit flip. Each transposition is one Toffoli in a free affine frame.
"""
from dirty_norm_control import ar,mcx_dirty
from lowclean import permutation3
from virtual_norm import encoded_norm3
from dirty_inverse6 import scale3
from functools import lru_cache


@lru_cache(None)
def transpose_frame(a,c):
    v=a^c
    for u in range(1,8):
        for w in range(1,8):
            try:frame=tuple(ar.inverse_columns((v,u,w)))
            except (AssertionError,ValueError,StopIteration):continue
            return frame,(v,u,w),ar.apply(frame,a)
    raise AssertionError((a,c))


def transpose3(b,x,a,c):
    frame,back,aa=transpose_frame(a,c)
    ar.linear_inplace(b,x,frame)
    flip=[x[j]for j in(1,2)if not(aa>>j&1)]
    b.x(flip);b.ccx(x[1],x[2],x[0]);b.x(flip)
    ar.linear_inplace(b,x,back)


def controlled_inverse3(b,x,h,borrow):
    transpose3(b,x,3,5);transpose3(b,x,4,6)
    b.x(x[1:]);mcx_dirty(b,[h,x[1],x[2]],x[0],borrow);b.x(x[1:])
    b.cx(h,x[0])
    transpose3(b,x,4,6);transpose3(b,x,3,5)


def inverse6_dirty(b,x,borrow):
    to,back,K=ar.tower(6);ar.linear_inplace(b,x,to)
    r,g=x[:3],x[3:]
    scale3(b,r,g,True);permutation3(b,g,'inverse')
    with encoded_norm3(b,r,K)as apply:apply([g],True)
    b.x(r[0]);scale3(b,r,g)
    # On g=0 the regular formula gives r=a+1. Correct by P=inv0 o X.
    # X P X=P^-1 supplies the dirty-control conjugation with free CNOTs.
    b.x(g);h=borrow[0];scratch=borrow[1:]
    b.cx(h,r[0])
    mcx_dirty(b,g,h,scratch)
    b.cx(h,r[0]);controlled_inverse3(b,r,h,scratch)
    mcx_dirty(b,g,h,scratch)
    controlled_inverse3(b,r,h,scratch);b.cx(h,r[0])
    b.cx(h,r[0]);b.x(g)
    ar.linear_inplace(b,x,back)
