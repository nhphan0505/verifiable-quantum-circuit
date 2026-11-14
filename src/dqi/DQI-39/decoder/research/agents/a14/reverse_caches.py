"""Exact mixed-size reverse inverse-norm caches in the retired-root lifetime."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'research/agents/a12'),str(ROOT/'research/agents/a08')]
import forward_norm_cache as cache
import scalar_compact_v3 as scalar
ar=scalar.ar
sys.path.insert(0,str(ROOT/'research/agents/a02'))
import cache_support as small_cache


def cached_pair_from_w(b,x,w,Z):
    to,frm,K=ar.tower(12);ar.linear_inplace(b,x,to)
    N=b.alloc_qubits(6);scalar.norm_xor_noscratch(b,x,N,K)
    to6,frm6,K6=ar.tower(6);ar.linear_inplace(b,N,to6)
    t=b.alloc_qubits(6);b.cx(N[3:],N[:3])
    scalar.mul_xor_noscratch(b,N[:3],w,t[:3])
    scalar.mul_xor_noscratch(b,N[3:],w,t[3:])
    b.cx(N[3:],N[:3]);ar.linear_inplace(b,N,frm6)
    # In tower coordinates w = Norm(t), including t=0.
    ar._erase_norm(b,t,w,K6);b.free(w);ar.linear_inplace(b,t,frm6)
    ar.linear_inplace(b,x,frm)
    return scalar.finish(b,x,(N,t)),Z,(N,t)



def install(cv):
    kinds={11:'t6',5:'w3'}
    levels=tuple(kinds)
    cells=dict(zip(cv.__code__.co_freevars,cv.__closure__))
    short=cells['core'].cell_contents.__globals__
    scope=scalar.scope_of(cv)
    inverse_original=scope['inverse_zero']
    solve_original=scope['look_solve']
    frames=[]
    levels=frozenset(levels)

    def selected(x):
        if not frames:return None
        m,phase,g,reverse=frames[-1]
        if reverse and m in levels and list(x)==list(g[-1]):return m,phase
        return None

    def inverse_zero(b,x):
        match=selected(x)
        if match is None:return inverse_original(b,x)
        m,phase=match
        caches=phase.setdefault('_a12_reverse_norm',{})
        assert m not in caches
        if kinds[m]=='w3':
            ai,Z,caches[m]=small_cache.inverse_zero_cached(b,x,producer18=True)
        else:
            assert kinds[m]=='t6'
            ai,Z,caches[m]=cache.first_inverse_with_t(b,x)
        return ai,Z

    def inverse_apply_safe(b,a,action,incoming=None,defer=False):
        ai,Z=inverse_zero(b,a)
        scope['consume'](b,ai,Z,incoming)
        b.cx(Z,a[0]);b.cx(Z,ai[0]);action(ai)
        b.cx(Z,ai[0]);b.cx(Z,a[0])
        return scope['erase'](b,a,ai,Z,defer)

    def solve(b,f,g,payloads,H=None,parent=None,reverse=False,phase=None):
        m=len(f)-1
        frames.append((m,phase,g,reverse))
        try:
            out=solve_original(b,f,g,payloads,H,parent,reverse,phase)
            if reverse and m in levels:
                assert m not in phase.get('_a12_reverse_norm',{})
            return out
        finally:frames.pop()

    def producer(original):
        def inverse_zero_normpair(b,x,Z):
            match=selected(x)
            if match is None:return original(b,x,Z)
            m,phase=match
            t=phase['_a12_reverse_norm'].pop(m)
            if kinds[m]=='w3':return cached_pair_from_w(b,x,t,Z)
            to,frm,K=ar.tower(12);ar.linear_inplace(b,x,to)
            N=b.alloc_qubits(6);scalar.norm_xor_noscratch(b,x,N,K)
            ar.linear_inplace(b,x,frm)
            ai=scalar.finish(b,x,(N,t))
            return ai,Z,(N,t)
        return inverse_zero_normpair

    dcells=dict(zip(scope['direct_pre'].__code__.co_freevars,
                    scope['direct_pre'].__closure__))
    pcells=dict(zip(scope['pre'].__code__.co_freevars,scope['pre'].__closure__))
    seen=set()
    for function in (dcells['handed'].cell_contents,pcells['plain_handed'].cell_contents):
        namespace=function.__globals__
        if id(namespace) not in seen:
            seen.add(id(namespace))
            namespace['inverse_normpair_known_zero']=producer(namespace['inverse_normpair_known_zero'])
    scope.update(inverse_zero=inverse_zero,inverse_apply_safe=inverse_apply_safe,look_solve=solve)
    short['old'].look_solve=solve
    return cv
