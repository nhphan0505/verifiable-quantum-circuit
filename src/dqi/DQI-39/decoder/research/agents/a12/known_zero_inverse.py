"""Use a supplied exact zero flag in the initialized GF64 inverse plan."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'research/agents/a08'),str(ROOT/'research/agents/a01')]
import scalar_compact_v3 as scalar
from exp.jet24 import pro_jet as jet
ar=scalar.ar


def inverse6_known_zero(b,x,Z):
    """Return inv0(x), preserving x and supplied Z=[x=0]."""
    ar.linear_inplace(b,x,jet.TO6)
    raw=b.alloc_qubits(6)
    for j,(l,r) in enumerate(jet.RAW):
        with jet.ref.expose_pair(b,x,l,r) as (p,q):b.init_and(p,q,raw[j])
    w=jet.ref.inverse3_virtual(b,list(x)+list(raw),jet.ref.norm_forms(1))
    raw=list(raw)+list(w);out=[]
    for step,(kind,a,c,d) in enumerate(jet.PLAN):
        if kind=='r':
            ar.linear_inplace(b,raw,a)
            for j,action in enumerate(d,c):
                if action is None:out.append(raw[j]);continue
                coeff,phase=action
                for k in ar.bits(coeff):b.cx(raw[j],out[k])
                mask=b.alloc_bits(1)[0];b.hmr(raw[j],mask)
                live=list(x)+raw[:c]+raw[j+1:]+out
                for i,k in phase:
                    if i==0:b.z(mask)
                    elif k==0 or i==k:b.cz(live[i-1],mask)
                    else:b.ccz(live[i-1],live[k-1],mask)
                b.free(mask);b.free(raw[j])
            raw=list(raw[:c])
        elif kind=='g':out.extend(b.alloc_qubits(a))
        elif step==17:
            assert (a,c,d,len(raw),len(out))==(200,474,64,5,7)
            # Exact all-field identity in this live prefix's coordinates.
            b.x(out[6]);b.cx(x[0],out[6]);b.cx(x[3],out[6])
            b.cx(raw[1],out[6]);b.cx(Z,out[6])
        else:
            with jet.ref.expose_pair(b,list(x)+raw,a,c) as (p,q):
                jet.rankone_xor(b,p,q,out,d)
    ar.linear_inplace(b,out,jet.OUTPUT)
    for j,form in enumerate(jet.LINEAR):jet.ref.form_xor(b,x,form,out[j])
    ar.linear_inplace(b,x,jet.FROM6)
    ar.linear_inplace(b,out[:6],jet.FROM6)
    b.cx(Z,out[6]);b.free(out[6])
    return out[:6]


def inverse_normpair_known_zero(b,a,Z):
    to,frm,K=ar.tower(12);ar.linear_inplace(b,a,to)
    N=b.alloc_qubits(6);scalar.norm_xor_noscratch(b,a,N,K)
    t=inverse6_known_zero(b,N,Z)
    ar.linear_inplace(b,a,frm)
    ai=scalar.finish(b,a,(N,t))
    return ai,Z,(N,t)


def install(cv):
    scope=scalar.scope_of(cv)
    dcells=dict(zip(scope['direct_pre'].__code__.co_freevars,scope['direct_pre'].__closure__))
    pcells=dict(zip(scope['pre'].__code__.co_freevars,scope['pre'].__closure__))
    aligned_original=dcells['handed'].cell_contents
    plain_original=pcells['plain_handed'].cell_contents
    acells=dict(zip(aligned_original.__code__.co_freevars,aligned_original.__closure__))
    close_heads=acells['close_heads'].cell_contents
    aligned_levels=frozenset(range(6,17));plain_levels=frozenset((2,3,4,5))

    def handed(b,f,g,payloads,F,incoming,defer,Z0):
        if len(f)-1 not in aligned_levels:return aligned_original(b,f,g,payloads,F,incoming,defer,Z0)
        assert not defer
        b.cx(Z0,g[-2][0]);masks=scope['high_full_restore'](b,f,g,F);b.cx(Z0,g[-2][0])
        scope['pivot'](b,g,F);a=g[-1]
        for v in payloads:scope['dk'].shifted_product(b,g[:-1],v[-1],v[:-1],F)
        b.cx(Z0,a[0]);debts=[scalar.scale_before_inverse(b,v[-1],a)for v in payloads];b.cx(Z0,a[0])
        ai,Z,saved=inverse_normpair_known_zero(b,a,Z0);scope['consume'](b,ai,Z,incoming)
        b.cx(Z,a[0]);b.cx(Z,ai[0])
        for v,mask in zip(payloads,debts):ar.phase_product(b,ai,v[-1],mask);b.free(mask)
        close_heads(b,f,g,ai,F,masks)
        b.cx(Z,ai[0]);b.cx(Z,a[0]);scalar.erase_normpair(b,a,ai,Z,saved)
        scope['pivot'](b,g,F)

    def plain(b,f,g,payloads,incoming,defer,Z0):
        if len(f)-1 not in plain_levels:return plain_original(b,f,g,payloads,incoming,defer,Z0)
        assert not defer
        a=g[-1];b.cx(Z0,a[0]);masks=scope['full_restore'](b,f,g);b.cx(Z0,a[0])
        for v in payloads:
            for i in range(len(g)-1):ar.mul_xor0(b,g[i],v[-1],v[i])
        b.cx(Z0,a[0]);debts=[scalar.scale_before_inverse(b,v[-1],a)for v in payloads];b.cx(Z0,a[0])
        ai,Z,saved=inverse_normpair_known_zero(b,a,Z0);scope['consume'](b,ai,Z,incoming)
        b.cx(Z,a[0]);b.cx(Z,ai[0])
        for v,mask in zip(payloads,debts):ar.phase_product(b,ai,v[-1],mask);b.free(mask)
        scope['close_heads'](b,f,g,ai,masks)
        b.cx(Z,ai[0]);b.cx(Z,a[0]);scalar.erase_normpair(b,a,ai,Z,saved)

    dcells['handed'].cell_contents=handed;scope['handed_aligned_pre']=handed
    pcells['plain_handed'].cell_contents=plain;scope['handed_plain_pre']=plain
    return cv
