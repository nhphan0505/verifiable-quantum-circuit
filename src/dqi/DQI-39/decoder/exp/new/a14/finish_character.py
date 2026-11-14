"""Close the first numerator character without replaying an inverse.

No stand-alone resource claim; installed in a whole decoder.
"""
def finish_partial_chart(b,D,F,forward,unused,N,L,R,head,ct):
    r,g=D[:12],D[12:]
    a,h=head;original=b.alloc_bits(24)
    b.cz(F,forward['f'][0]);b.free(forward['f'])
    cx(b,h,a,ct);b.cx(a,N[12:]);cx(b,h,a,ct)
    b.hmr(N[12:],original[:12]);b.swap(N[12:],R[:12]);b.free(R[:12])
    # g_raw -> g_raw*q -> inv(g_raw*q). Its masks are kept until their
    # arguments are either restored or included in a required character.
    merged_chart(b,r,F);gm=scale_defer(b,g,r);merged_chart(b,r,F,True)
    hm=inverse_stream_noscratch(b,g)
    vm=scale_defer(b,N[:12],g)
    # Pay the reciprocal-gq and old-P characters directly at t. This
    # replaces t -> 1/t -> t and leaves no artificial inversion transcript.
    linear_inverse_character(b,g,hm,[(N[:12],vm)])
    b.free(hm);b.free(vm)
    # The skipped shear repays the first original-N measurement.
    b.x(r[0]);b.cx(F,r[0])
    ar.phase_product(b,r,N[:12],original[:12])
    b.cx(h,N[:12]);b.hmr(N[:12],original[12:])
    b.swap(N[:12],R[12:]);b.free(R[12:]);b.swap(N[:12],N[12:])
    b.cx(F,r[0]);b.x(r[0])
    # R has retired completely. Hold inv(g_raw*q) while temporarily
    # producing inv(g_raw) to normalize the two high halves.
    # g already equals t=1/(g_raw*q).
    keep=b.alloc_qubits(12);b.cx(g,keep)
    merged_chart(b,r,F)
    sm=scale_defer(b,g,r);b.cz(keep,sm);b.free(sm)
    merged_chart(b,r,F,True)
    ref.external_square24(b,L,True)
    for x in (N,L):
        correct_subfield(b,x,F);ar.mul_xor0(b,r,x[12:],x[:12])
    high=[scale_defer(b,x[12:],g) for x in (N,L)]
    # Here g=1/g_raw. These two original forward characters are now
    # available without the old keep-and-recompute direct-chart stage.
    b.cz(g,forward['h']);b.free(forward['h'])
    high_constant=add_masks(b,gm,forward['t'])
    linear_inverse_character(b,g,high_constant,[(N[12:],high[0]),(L[12:],high[1])])
    b.free(high_constant)
    for m in high:b.free(m)
    # Restore inv(g_raw*q) from its copy and close the discarded value
    # inv(g_raw)=q*inv(g_raw*q) by a bilinear character.
    mm=b.alloc_bits(12);b.hmr(g,mm);b.swap(g,keep);b.free(keep)
    merged_chart(b,r,F);ar.phase_product(b,g,r,mm);merged_chart(b,r,F,True);b.free(mm)
    low=[scale_defer(b,x[:12],g) for x in (N,L)]
    inverse_mask=forward['i']
    b.x(r[0]);b.cx(F,r[0])
    b.cz(r,forward['r']);b.free(forward['r'])
    for x in (N,L):
        ar.mul_xor0(b,r,x[:12],x[12:]);b.swap(x[:12],x[12:])
    # Restore the direct denominator's raw first coordinate. Its old-r
    # mask joins the same inverse-g character as both low-half masks.
    rm=scale_defer(b,r,g)
    linear_inverse_character(b,g,inverse_mask,
        [(N[12:],low[0]),(L[12:],low[1]),(r,rm)])
    b.free(inverse_mask);b.free(rm)
    for m in low:b.free(m)
    ref.external_square24(b,L)
    b.cz(g,forward['g']);b.free(forward['g'])
    b.cswap(F,r,g)
    fm=b.alloc_bits(1);b.hmr(F,fm[0]);b.free(F)
    b.x(g);frozen.phase_and(b,g,fm[0]);b.x(g);b.free(fm)
    b.cx(h,L[:12])
    return original
