"""Keep the six-bit inverse-norm source through each local jet reverse."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'exp/r-main/narrow240'))
import decode_combo as base
import exact_subs as xs
import inspect
from types import FunctionType, SimpleNamespace, ModuleType
from exp.jet24 import pro_jet as jet
from exp.jet24.pro_jet import *


def start_inverse_kept(b,N):
    """Return k=inv0(D), F=[N=0], D=Norm12(N), preserving all three."""
    to,frm,K=tower(12)
    linear_inplace(b,N,to)
    D=b.alloc_qubits(6)
    norm_xor_noscratch(b,N,D,K)
    k,F=inverse6_zero18(b,D)
    linear_inplace(b,N,frm)
    return k,F,D


def erase_inverse_kept(b,t,N,k,F,fz,D):
    """Erase N=inv0(t) using retained D=inv0(k); close all phases."""
    to,frm,K=tower(12)
    linear_inplace(b,t,to)
    linear_inplace(b,N,to)
    m=b.alloc_bits(12);b.hmr(N,m);b.free(N)
    L=b.alloc_qubits(6);f=field(6)
    def coeff():
        for j in range(6):
            for i in range(6):
                for r in bits(f.mul(1<<i,1<<j)):
                    b.ccx(m[r],t[i],L[j])
                    b.ccx(m[r],t[i+6],L[j])
                    b.ccx(m[r+6],t[i+6],L[j])
    coeff();b.cz(L,D);coeff();b.free(L);b.free(m)
    b.cz(F,fz[0]);b.free(fz)
    fm=b.alloc_bits(1);b.hmr(F,fm[0]);b.free(F)
    b.z(fm[0])
    mask=b.alloc_bits(6);b.bit_store(mask,False);b.cx(fm[0],mask[0])
    ar.phase_product(b,D,k,mask);b.free(mask);b.free(fm)
    dm=b.alloc_bits(6);b.hmr(D,dm);b.free(D)
    xs.phase_inverse6_quad4(b,k,dm);b.free(dm)
    ar._erase_norm(b,t,k,K);b.free(k)
    linear_inplace(b,t,frm)

_source=inspect.getsource(jet.reverse_canonical)
_source=_source.replace('k, F = start_inverse(b, N)','k, F, D = start_inverse_kept(b, N)')
_source=_source.replace('erase_inverse_cached(b, t, N, k, F, fz)','erase_inverse_kept(b, t, N, k, F, fz, D)')
_env=dict(jet.reverse_canonical.__globals__,start_inverse_kept=start_inverse_kept,erase_inverse_kept=erase_inverse_kept)
exec(compile(_source,__file__,'exec'),_env)
reverse_canonical_kept=_env['reverse_canonical']


def replacement_ids(entry, original, replacement):
    seen=set();matches={}
    def visit(v):
        if id(v) in seen:return
        seen.add(id(v))
        if isinstance(v,FunctionType):
            if v.__code__ is original.__code__:matches[id(v)]=replacement
            for name in v.__code__.co_names:
                if name in v.__globals__:visit(v.__globals__[name])
            if v.__closure__:
                for c in v.__closure__:visit(c.cell_contents)
            for c in v.__code__.co_consts:
                if hasattr(c,'co_names'):
                    for name in c.co_names:
                        if name in v.__globals__:visit(v.__globals__[name])
        elif isinstance(v,(ModuleType,SimpleNamespace)):
            path=getattr(v,'__file__',None)
            if path is None or str(ROOT) in str(path):
                for x in vars(v).values():visit(x)
        elif isinstance(v,dict):
            for x in v.values():visit(x)
        elif isinstance(v,(tuple,list)):
            for x in v:visit(x)
    visit(entry);return matches

replacements=replacement_ids(base.decode,jet.reverse_canonical,reverse_canonical_kept)
assert replacements
body=xs.private_rebind(base.decode,replacements)
def decode(b,S,E):
    return body(b,S,E)
