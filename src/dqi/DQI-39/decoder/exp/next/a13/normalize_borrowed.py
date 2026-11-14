"""First half for a high-pressure return; no new source-chart qubit."""
def normalize_first_half(b,N,D,L,R):
    r,g=D[:12],D[12:]
    F=b.alloc_qubits(1)[0]
    lowclean.zero_toggle(b,g,F,r)
    b.cswap(F,r,g)
    correct_subfield(b,N,F)
    with borrowed_source.source(b,g,L[:8],True) as apply:
        apply([N[12:]])
    ar.mul_xor0(b,r,N[12:],N[:12])
    return 'a13_defer',F
