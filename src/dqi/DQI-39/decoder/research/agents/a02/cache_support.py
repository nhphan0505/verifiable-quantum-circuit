"""Exact retained three-bit inverse-tower caches in selected converter frames.

No decision depends on quantum values or checker samples. The cache is
inv0(Norm_GF64/GF8(Norm_GF4096/GF64(a))) in fixed tower coordinates.
"""
from contextlib import contextmanager
from pathlib import Path
import importlib.util
import inspect
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'research/agents/a01'))
import ported as p
from exp.inverse19_joint import kernel as joint
from exp.noscratch.schedules import norm_xor_noscratch
from exp.noscratch.kernels import mul_xor_noscratch
from exp.arithmetic.lowwidth import classical_transpose
from exp.decoder.common import ar
from exp.jet24 import pro_jet
import exact_subs as exact


def close_spilled_phase(b,x,mask,zero_mask,debt):
    """Close the ordinary inverse and a measured inner-cache character jointly."""
    source=inspect.getsource(exact.phase_inverse12_virtual_nonzero)
    source=source.replace('def phase_inverse12_virtual_nonzero(b, x, mask, zero_mask=None):',
                          'def joint_phase(b, x, mask, zero_mask=None, debt=None):')
    needle='    w = ref.inverse3_virtual(b, prefix, forms)\n'
    assert source.count(needle)==1
    source=source.replace(needle,needle+'    if debt is not None:b.cz(w,debt)\n')
    env=dict(exact.phase_inverse12_virtual_nonzero.__globals__)
    exec(compile(source,__file__,'exec'),env)
    active=b.alloc_bits(1)[0];b.bit_store(active,False)
    for bit in mask:b.bit_store(active,True,control=bit)
    if zero_mask is not None:b.bit_store(active,True,control=zero_mask)
    if debt is not None:
        for bit in debt:b.bit_store(active,True,control=bit)
    b.push_condition(active);env['joint_phase'](b,x,mask,zero_mask,debt)
    b.pop_condition();b.free(active)
    if debt is not None:b.free(debt)


def inverse6_keep_cache(b,x):
    """The supplied initialized inverse, retaining its existing inner inverse."""
    to,frm,K=ar.tower(6);ar.linear_inplace(b,x,to);g=b.alloc_qubits(6)
    for i,(l,r) in enumerate(joint.basic.raw_forms19()):
        with joint.ref.expose_pair(b,x,l,r) as (u,v):b.init_and(u,v,g[i])
    prefix=list(x)+list(g);forms=joint.ref.norm_forms(K)
    w=joint.ref.inverse3_virtual(b,prefix,forms)
    ar.linear_inplace(b,g,joint.LAY['raw_columns']);R,E=g[:4],g[4:]
    z=list(E)+list(b.alloc_qubits(4));source=list(x)+list(R)+list(w)
    for j,e in enumerate(joint.LAY['outputs']):joint.ref.form_xor(b,source,e&65535,z[j])
    for i,(l,r) in enumerate(joint.LAY['gates']):
        v=sum(((e>>(16+i))&1)<<j for j,e in enumerate(joint.LAY['outputs']))
        with joint.ref.expose_pair(b,source,l,r) as (u,vv):joint.rankone_xor(b,u,vv,z,v)
    rm=b.alloc_bits(4);b.hmr(R,rm);b.free(R)
    for i,(l,r) in enumerate(joint.basic.raw_forms19()):
        with joint.ref.expose_pair(b,x,l,r) as (u,v):
            for j,row in enumerate(joint.LAY['raw_rows'][:4]):
                if row>>i&1:b.ccz(u,v,rm[j])
    b.free(rm);ar.linear_inplace(b,z,joint.LAY['output_inverse_columns'])
    F=zero_from_cache(b,w)
    ar.linear_inplace(b,x,frm);ar.linear_inplace(b,z,frm)
    return z,F,w


def zero_from_cache(b,w):
    b.x(w);u=b.alloc_qubits(1)[0];F=b.alloc_qubits(1)[0]
    b.init_and(w[0],w[1],u);b.init_and(u,w[2],F)
    b.del_and(w[0],w[1],u);b.free(u);b.x(w)
    return F


def inverse6_keep18(b,x):
    """Keep a copy of the existing 18-AND producer's inner inverse prefix."""
    ar.linear_inplace(b,x,pro_jet.TO6)
    raw=b.alloc_qubits(6)
    for j,(l,r) in enumerate(pro_jet.RAW):
        with joint.ref.expose_pair(b,x,l,r) as (u,v):b.init_and(u,v,raw[j])
    w=joint.ref.inverse3_virtual(b,list(x)+list(raw),joint.ref.norm_forms(1))
    cache=b.alloc_qubits(3);b.cx(w,cache)
    raw=list(raw)+list(w);out=[]
    for kind,a,c,d in pro_jet.PLAN:
        if kind=='r':
            ar.linear_inplace(b,raw,a)
            for j,action in enumerate(d,c):
                if action is None:
                    out.append(raw[j]);continue
                coeff,phase=action
                for k in ar.bits(coeff):b.cx(raw[j],out[k])
                m=b.alloc_bits(1)[0];b.hmr(raw[j],m)
                live=list(x)+raw[:c]+raw[j+1:]+out
                for i,k in phase:
                    if i==0:b.z(m)
                    elif k==0 or i==k:b.cz(live[i-1],m)
                    else:b.ccz(live[i-1],live[k-1],m)
                b.free(m);b.free(raw[j])
            raw=list(raw[:c])
        elif kind=='g':out.extend(b.alloc_qubits(a))
        else:
            with joint.ref.expose_pair(b,list(x)+raw,a,c) as (u,v):
                joint.rankone_xor(b,u,v,out,d)
    ar.linear_inplace(b,out,pro_jet.OUTPUT)
    for j,form in enumerate(pro_jet.LINEAR):joint.ref.form_xor(b,x,form,out[j])
    ar.linear_inplace(b,x,pro_jet.FROM6);ar.linear_inplace(b,out[:6],pro_jet.FROM6)
    return out[:6],out[6],cache


def inverse_zero_cached(b,x,w=None,producer18=False):
    """Return inv0(x), [x=0], and the unchanged three-bit inverse cache."""
    to,frm,K=ar.tower(12);ar.linear_inplace(b,x,to)
    N=b.alloc_qubits(6);norm_xor_noscratch(b,x,N,K)
    if w is None:
        t,F,w=(inverse6_keep18 if producer18 else inverse6_keep_cache)(b,N)
    else:
        to6,frm6,_=ar.tower(6);ar.linear_inplace(b,N,to6)
        t=b.alloc_qubits(6)
        b.cx(N[3:],N[:3]);mul_xor_noscratch(b,N[:3],w,t[:3])
        mul_xor_noscratch(b,N[3:],w,t[3:]);b.cx(N[3:],N[:3])
        ar.linear_inplace(b,N,frm6);ar.linear_inplace(b,t,frm6)
        F=zero_from_cache(b,w)
    ar._erase_norm(b,x,N,K);b.free(N)
    out=b.alloc_qubits(12);b.cx(x[6:],x[:6])
    mul_xor_noscratch(b,x[:6],t,out[:6]);mul_xor_noscratch(b,x[6:],t,out[6:])
    b.cx(x[6:],x[:6]);ar._erase_norm(b,out,t,K);b.free(t)
    ar.linear_inplace(b,x,frm);ar.linear_inplace(b,out,frm)
    return out,F,w


def close_cached_phase(b,x,mask,zero_mask,w):
    """Repay inverse/zero characters and retire the cache with its own character."""
    to12,frm12,K12=ar.tower(12);ar.linear_inplace(b,x,to12)
    mt=classical_transpose(b,mask,frm12)
    D=b.alloc_qubits(6);norm_xor_noscratch(b,x,D,K12)
    to6,frm6,K6=ar.tower(6);ar.linear_inplace(b,D,to6)
    anc=b.alloc_qubits(1)[0];f6=ar.field(6)
    def coefficient(h):
        for j in range(6):
            for r in ar.bits(f6.mul(h,1<<j)):
                b.ccx(mt[r],x[j],anc);b.ccx(mt[r],x[j+6],anc)
                b.ccx(mt[r+6],x[j+6],anc)
    for segment in (0,1):
        if segment==0:b.cx(D[3:],D[:3])
        controls=D[:3] if segment==0 else D[3:]
        for m,v in ar.tensor(3):
            h=ar.apply(frm6,v<<(3*segment));ix=list(ar.bits(m));q=ix[0]
            coefficient(h)
            for j in ix[1:]:b.cx(controls[j],controls[q]);b.cx(w[j],w[q])
            b.ccz(controls[q],w[q],anc)
            for j in reversed(ix[1:]):b.cx(w[j],w[q]);b.cx(controls[j],controls[q])
            coefficient(h)
        if segment==0:b.cx(D[3:],D[:3])
    b.free(anc)
    if zero_mask is not None:
        b.x(w);b.push_condition(zero_mask);b.ccz(w[0],w[1],w[2]);b.pop_condition();b.x(w)
    E=b.alloc_qubits(3);norm_xor_noscratch(b,D,E,K6)
    ar.erase_inverse(b,E,w);b.free(w)
    ar._erase_norm(b,D,E,K6);b.free(E)
    ar.linear_inplace(b,D,frm6);ar._erase_norm(b,x,D,K12);b.free(D)
    ar.linear_inplace(b,x,frm12);b.free(mt)


def install(cv,levels=(14,),trace=False,split=False,producer18=False,spill=False):
    """Retain one cache per listed degree between first pre and final undo pre."""
    cells=dict(zip(cv.__code__.co_freevars,cv.__closure__))
    short=cells['core'].cell_contents.__globals__
    scope=short['old'].direct_post.__globals__
    levels=frozenset(levels)
    frames=[]
    old_inverse=scope['inverse_zero'];old_erase=scope['erase']
    old_gap_phase=scope['phase_inverse_for_gap']
    old_solve=scope['look_solve']
    def selected(x):
        if not frames:return None
        frame=frames[-1]
        return frame if frame[0] in levels and list(x)==list(frame[2][-1]) else None
    def inverse_zero(b,x):
        frame=selected(x)
        if frame is None:return old_inverse(b,x)
        m,phase,g,reverse=frame
        cache=phase.setdefault('_inverse3_cache',{})
        if trace:print('CACHE-INVERSE',m,len(cache),b.num_allocated_qubits,file=sys.stderr)
        ai,F,w=inverse_zero_cached(b,x,cache.get(m),producer18)
        cache[m]=w
        if (spill or split and reverse) and m in phase.get('_inverse3_debt',{}):
            debt=phase['_inverse3_debt'].pop(m);b.cz(w,debt);b.free(debt)
        return ai,F
    def erase(b,a,ai,F,defer):
        frame=selected(a)
        if frame is None:return old_erase(b,a,ai,F,defer)
        m,phase,g,reverse=frame
        mask=b.alloc_bits(12);zm=b.alloc_bits(1)
        b.hmr(ai,mask);b.hmr(F,zm[0]);b.free(ai);b.free(F)
        if defer:return mask,zm
        w=phase['_inverse3_cache'].pop(m,None)
        if w is not None:close_cached_phase(b,a,mask,zm[0],w)
        else:close_spilled_phase(b,a,mask,zm[0],phase['_inverse3_debt'].pop(m,None))
        b.free(mask);b.free(zm)
    def inverse_apply_safe(b,a,action,incoming=None,defer=False):
        ai,F=inverse_zero(b,a);scope['consume'](b,ai,F,incoming)
        b.cx(F,a[0]);b.cx(F,ai[0]);action(ai)
        b.cx(F,ai[0]);b.cx(F,a[0])
        return erase(b,a,ai,F,defer)
    def gap_phase(b,a,mask,zero_mask=None):
        frame=selected(a)
        if frame is None:return old_gap_phase(b,a,mask,zero_mask)
        m,phase,g,reverse=frame
        w=phase['_inverse3_cache'].pop(m,None)
        if w is not None:close_cached_phase(b,a,mask,zero_mask,w)
        else:close_spilled_phase(b,a,mask,zero_mask,phase['_inverse3_debt'].pop(m,None))
    def retire_for_workspace(b):
        if not frames:return
        m,phase,g,reverse=frames[-1]
        w=phase.get('_inverse3_cache',{}).pop(m,None)
        if w is None:return
        debt=b.alloc_bits(3);b.hmr(w,debt);b.free(w)
        assert m not in phase.setdefault('_inverse3_debt',{})
        phase['_inverse3_debt'][m]=debt
    def solve(b,f,g,payloads,H=None,parent=None,reverse=False,phase=None):
        m=len(f)-1
        frames.append((m,phase,g,reverse))
        try:
            answer=old_solve(b,f,g,payloads,H,parent,reverse,phase)
            if split and not reverse and m in levels and m in phase.get('_inverse3_cache',{}):
                cache=phase['_inverse3_cache'].pop(m)
                debt=b.alloc_bits(3);b.hmr(cache,debt);b.free(cache)
                phase.setdefault('_inverse3_debt',{})[m]=debt
            return answer
        finally:frames.pop()
    scope.update(inverse_zero=inverse_zero,erase=erase,inverse_apply_safe=inverse_apply_safe,
                 look_solve=solve,phase_inverse_for_gap=gap_phase)
    if spill:
        for name in ['scale','high_close_heads','close_heads']:
            old=scope[name]
            def call(b,*args,_old=old,**kw):
                retire_for_workspace(b)
                return _old(b,*args,**kw)
            scope[name]=call
        short['old'].scale=scope['scale']
    short['old'].look_solve=solve
    return cv


def decoder(levels,trace=False,split=False,exact=False,producer18=False,spill=False):
    cv=install(p.convert_safe,levels,trace,split,producer18,spill)
    if exact:
        from rebind_graph import private_rebind
        cv=private_rebind(cv,p.base.replacements,p.ROOT)
    return p.clone(p.decode,dict(p.decode.__globals__,convert_safe=cv))
