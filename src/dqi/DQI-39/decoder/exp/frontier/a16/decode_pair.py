"""Use a jointly synthesized inverse-character pair at four-coordinate norm sites."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'root'),str(HERE.parent/'a04')]
import decode_local_norm_partial as partial
from nonzero_consume16 import functions
from phase_pair import phase_pair,MASKS,xs


def _layout():
    rows=list(MASKS)
    def rank(values):
        bs={}
        for v in values:
            while v:
                p=v.bit_length()-1
                if p in bs:v^=bs[p]
                else:bs[p]=v;break
        return len(bs)
    for i in range(6):
        if rank(rows+[1<<i])>len(rows):rows.append(1<<i)
    rows=rows[2:]+rows[:2]
    assert len(rows)==6
    columns=[sum(((r>>i)&1)<<j for j,r in enumerate(rows)) for i in range(6)]
    return tuple(rows),tuple(columns),tuple(xs.inverse_columns(columns))


ROWS,COLUMNS,INVERSE=_layout()


def transpose_mask(b,m):
    out=b.alloc_bits(6)
    b.bit_store(out,False)
    for j,row in enumerate(ROWS):
        for i in bits(row):b.cx(m[j],out[i])
    return out


def inverse12_keep_partial_norm(b,x,keep):
    if keep!=4:return original_produce(b,x,keep)
    to,frm,K=tower(12)
    linear_inplace(b,x,to)
    D=b.alloc_qubits(6)
    norm_xor_noscratch(b,x,D,K)
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
    if len(D)!=4:return original_erase(b,t,N,u,D)
    to,frm,K=tower(12)
    linear_inplace(b,t,to);linear_inplace(b,N,to)
    m=b.alloc_bits(12);b.hmr(N,m);b.free(N)
    L=b.alloc_qubits(2)
    f=field(6)
    def coefficient(j,target):
        k=INVERSE[j]
        for i in range(6):
            for r in bits(f.mul(1<<i,k)):
                b.ccx(m[r],t[i],target)
                b.ccx(m[r],t[i+6],target)
                b.ccx(m[r+6],t[i+6],target)
    for j in range(4):
        coefficient(j,L[0]);b.cz(L[0],D[j]);coefficient(j,L[0])
    coefficient(4,L[0]);coefficient(5,L[1])
    phase_pair(b,u,L)
    coefficient(5,L[1]);coefficient(4,L[0])
    b.free(L);b.free(m)
    dm=b.alloc_bits(6);b.bit_store(dm,False)
    b.hmr(D,dm[:4]);b.free(D)
    original_mask=transpose_mask(b,dm)
    xs.phase_inverse6_quad4(b,u,original_mask)
    b.free(original_mask);b.free(dm)
    ar._erase_norm(b,t,u,K);b.free(u)
    linear_inplace(b,t,frm)


def install(entry):
    replacements={}
    for fn in functions(entry):
        if fn.__code__ is partial.inverse12_keep_partial_norm.__code__:
            extra=dict(original_produce=fn,COLUMNS=COLUMNS,transpose_mask=transpose_mask)
            replacements[id(fn)]=xs.clone(inverse12_keep_partial_norm,dict(fn.__globals__,**extra))
        elif fn.__code__ is partial.erase_norm_with_partial.__code__:
            extra=dict(original_erase=fn,INVERSE=INVERSE,phase_pair=phase_pair,transpose_mask=transpose_mask)
            replacements[id(fn)]=xs.clone(erase_norm_with_partial,dict(fn.__globals__,**extra))
    assert len(replacements)>=2
    scope=dict(entry.__globals__)
    for name in ('extraction','synthesize'):
        scope[name]=xs.private_rebind(scope[name],replacements)
    result=xs.clone(entry,scope)
    for name in ('convert_safe','baseline'):
        assert result.__globals__[name] is entry.__globals__[name]
    return result


# This helper is called from both privately rebound runtime functions.
bits=xs.bits
import decode_combo_v11 as current
decode=install(current.decode)
