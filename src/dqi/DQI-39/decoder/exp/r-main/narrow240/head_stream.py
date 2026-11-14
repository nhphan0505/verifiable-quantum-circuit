"""Exact low head restore, 12 rather than 24 simultaneous output wires."""
from exp.decoder.common import ar
from direct_kernels import conv,k

def full_restore12(b,f,g):
 m=len(g);lo=b.alloc_qubits(12)
 with b.mark('full_head_product_stream'):conv(b,g,f[-2:],f[:-2]+[lo],m)
 masks=[b.alloc_bits(12),b.alloc_bits(12)]
 b.hmr(f[-2],masks[0]);b.swap(f[-2],lo);b.free(lo)
 hi=b.alloc_qubits(12);ar.mul_xor0(b,g[-1],f[-1],hi)
 b.hmr(f[-1],masks[1]);b.swap(f[-1],hi);b.free(hi)
 V,W=k.vandermonde(m);field=ar.field(12)
 for j,word in enumerate(f[:-1]):
  correction=0
  for t in range(m):correction^=field.mul(W[j][t],field.pow(t,m))
  k.cx(b,f[-1],word,correction)
 return masks
