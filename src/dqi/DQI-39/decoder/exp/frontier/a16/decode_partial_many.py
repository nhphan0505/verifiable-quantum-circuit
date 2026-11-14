"""Use two through five retained norm coordinates, with all inverse phases fused."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import decode_pair as pair
from phase_many_fused import phase_many_fused


def inverse12_keep_partial_norm(b,x,keep):
    if keep==6:return original_produce(b,x,keep)
    to,frm,K=tower(12)
    linear_inplace(b,x,to)
    D=b.alloc_qubits(6);norm_xor_noscratch(b,x,D,K)
    u=inverse6_init19(b,D)
    linear_inplace(b,D,COLUMNS)
    dm=b.alloc_bits(6);b.bit_store(dm,False)
    b.hmr(D[keep:],dm[keep:]);b.free(D[keep:])
    original_mask=transpose_mask(b,dm)
    ar._phase_norm(b,x,original_mask,K)
    b.free(original_mask);b.free(dm)
    t=b.alloc_qubits(12)
    b.cx(x[6:],x[:6])
    mul_xor_noscratch(b,x[:6],u,t[:6])
    mul_xor_noscratch(b,x[6:],u,t[6:])
    b.cx(x[6:],x[:6])
    linear_inplace(b,x,frm);linear_inplace(b,t,frm)
    return t,u,D[:keep]


def erase_norm_with_partial(b,t,N,u,D):
    keep=len(D)
    if keep==6:return original_erase(b,t,N,u,D)
    to,frm,K=tower(12)
    linear_inplace(b,t,to);linear_inplace(b,N,to)
    m=b.alloc_bits(12);b.hmr(N,m);b.free(N)
    L=b.alloc_qubits(6-keep)
    f=field(6)
    def coefficient(j,target):
        k=INVERSE[j]
        for i in range(6):
            for r in bits(f.mul(1<<i,k)):
                b.ccx(m[r],t[i],target)
                b.ccx(m[r],t[i+6],target)
                b.ccx(m[r+6],t[i+6],target)
    for j in range(keep):
        coefficient(j,L[0]);b.cz(L[0],D[j]);coefficient(j,L[0])
    dm=b.alloc_bits(6);b.bit_store(dm,False)
    b.hmr(D,dm[:keep]);b.free(D)
    original_mask=transpose_mask(b,dm)
    for j in range(keep,6):coefficient(j,L[j-keep])
    phase_many_fused(b,u,{ROWS[j]:L[j-keep] for j in range(keep,6)},original_mask)
    for j in reversed(range(keep,6)):coefficient(j,L[j-keep])
    b.free(L);b.free(m);b.free(original_mask);b.free(dm)
    ar._erase_norm(b,t,u,K);b.free(u)
    linear_inplace(b,t,frm)


def inverse24_reverse_partial(b,x,mask,K=None):
    keep=min(6,889-b.num_allocated_qubits-42)
    if keep<2:return fallback(b,x,mask,K)
    cols,back,_=extension_columns(K)
    linear_inplace(b,x,cols)
    to,frm,K24=tower(24);linear_inplace(b,x,to)
    N=b.alloc_qubits(12);norm_xor_noscratch(b,x,N,K24)
    t,u,D=inverse12_keep_partial_norm(b,N,keep)
    out=b.alloc_qubits(12)
    mul_xor_noscratch(b,x[12:],t,out)
    erase_product(b,out,N,x[12:])
    mul_xor_noscratch(b,x[:12],t,x[12:])
    erase_product(b,x[12:],N,x[:12])
    b.cx(out,x[12:]);b.swap(x[:12],x[12:]);b.swap(x[12:],out);b.free(out)
    erase_norm_with_partial(b,t,N,u,D)
    ar._erase_norm(b,x,t,K24);b.free(t)
    linear_inplace(b,x,frm);b.cz(x,mask);b.free(mask);linear_inplace(b,x,back)


def install(entry):
    replacements={}
    for fn in pair.functions(entry.__globals__['extraction']):
        if fn.__code__ is pair.partial.inverse24_reverse_partial.__code__:
            scope=dict(fn.__globals__)
            produce=scope['inverse12_keep_partial_norm'];erase=scope['erase_norm_with_partial']
            pscope=dict(produce.__globals__,original_produce=produce,COLUMNS=pair.COLUMNS,transpose_mask=pair.transpose_mask)
            escope=dict(erase.__globals__,original_erase=erase,ROWS=pair.ROWS,INVERSE=pair.INVERSE,transpose_mask=pair.transpose_mask,phase_many_fused=phase_many_fused)
            scope['inverse12_keep_partial_norm']=pair.xs.clone(inverse12_keep_partial_norm,pscope)
            scope['erase_norm_with_partial']=pair.xs.clone(erase_norm_with_partial,escope)
            replacements[id(fn)]=pair.xs.clone(inverse24_reverse_partial,scope)
    assert replacements
    scope=dict(entry.__globals__)
    scope['extraction']=pair.xs.private_rebind(scope['extraction'],replacements)
    result=pair.xs.clone(entry,scope)
    for name in ('convert_safe','baseline'):
        assert result.__globals__[name] is entry.__globals__[name]
    return result


decode=install(pair.current.decode)
