"""Seven-Toffoli multiplication by 2**key in the supplied GF8 basis.

Every three-bit key is supported. Keys 0 and 7 both select identity.
The source key and all target bases are restored, without extra qubits.
"""
from lowclean_norm5 import ar, transvection_data

GATES=((1,4,2),(1,2,5),(5,7,3),(4,2,4),(6,1,6),(2,4,2),(2,6,1))
COMPILED=tuple((c,*transvection_data(a,v)) for c,a,v in GATES)


def scale_many(b,targets,key,inverse=False):
    for c,cols,back in reversed(COMPILED) if inverse else COMPILED:
        bits=[j for j in range(3) if c>>j&1]
        control=key[bits[0]]
        for j in bits[1:]:b.cx(key[j],control)
        for x in targets:
            ar.linear_inplace(b,x,cols)
            b.ccx(control,x[0],x[1])
            ar.linear_inplace(b,x,back)
        for j in reversed(bits[1:]):b.cx(key[j],control)


def scale(b,x,key,inverse=False):
    scale_many(b,[x],key,inverse)
