"""Completed GF64 inverse with eight arbitrary dirty wires, no clean wire.

Use the regular projective inverse, then repair its zero-high row with a
controlled GF8 inversion. The latter is an involution, so a dirty flag
can control it twice and cancel its unknown initial value.
"""
from virtual_norm import ar,encoded_norm3
from lowclean import permutation3,PERMS,mcx_dirty
import logscale7

def scale3(b,x,g,inverse=False):
    permutation3(b,g,'log');logscale7.scale_many(b,[x],g,inverse);permutation3(b,g,'log',True)

def inverse6_dirty(b,x,borrow):
    to,back,K=ar.tower(6);ar.linear_inplace(b,x,to)
    r,g=x[:3],x[3:]
    scale3(b,r,g,True)
    permutation3(b,g,'inverse')
    with encoded_norm3(b,r,K) as apply:apply([g],True)
    b.x(r[0]);scale3(b,r,g)
    # If g=0, the regular circuit yielded r=a+1. Correct to inv0(a).
    b.x(g);mcx_dirty(b,g,r[0],borrow)
    h=borrow[0];scratch=borrow[1:]
    def controlled_inverse():
        for op,*args in PERMS['inverse']['gates']:
            wires=[r[i] for i in args]
            if op=='ccx':mcx_dirty(b,[h]+wires[:2],wires[2],scratch)
            elif op=='cx':b.ccx(h,wires[0],wires[1])
            elif op=='x':b.cx(h,wires[0])
            else:raise AssertionError(op)
    mcx_dirty(b,g,h,scratch);controlled_inverse()
    mcx_dirty(b,g,h,scratch);controlled_inverse()
    b.x(g);ar.linear_inplace(b,x,back)
