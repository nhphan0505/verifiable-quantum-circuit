"""Carry three norm coordinates from the consumed denominator to its phase."""
from pathlib import Path
import inspect
import sys
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import decode_trailing_companion as companion
from exp.noscratch import schedules as ns
from exp.arithmetic.lowwidth import classical_transpose
import norm_cache


def inverse12_keep_norm(b,x,ceiling=889):
    to,frm,K=ns.tower(12)
    ns.linear_inplace(b,x,to)
    N=b.alloc_qubits(6)
    ns.norm_xor_noscratch(b,x,N,K)
    nm=ns.inverse_stream_noscratch(b,N)
    ns.ar._phase_norm(b,x,nm,K)
    b.free(nm)
    out=b.alloc_qubits(6)
    ns.mul_xor_noscratch(b,x[6:],N,out)
    raw=b.alloc_bits(12)
    b.hmr(x[6:],raw[6:])
    ns.mul_xor_noscratch(b,x[:6],N,x[6:])
    b.cx(out,x[6:])
    b.hmr(x[:6],raw[:6])
    b.swap(x[:6],x[6:])
    b.swap(x[6:],out)
    b.free(out)
    keep=min(6,max(0,ceiling-(b.num_allocated_qubits-6)-12))
    columns,back=norm_cache.layout(keep)
    ns.linear_inplace(b,N,columns)
    mask=b.alloc_bits(6)
    b.bit_store(mask,False)
    b.hmr(N[keep:],mask[keep:])
    b.free(N[keep:])
    original=classical_transpose(b,mask,columns)
    b.free(mask)
    ns.ar._phase_norm(b,x,original,K)
    b.free(original)
    ns.linear_inplace(b,x,frm)
    result=classical_transpose(b,raw,to)
    b.free(raw)
    return result,N[:keep]


def install(entry,ceiling=889):
    entry=companion.install(entry)
    extraction=entry.__globals__['extraction']
    scope=dict(extraction.__globals__)
    inverse=companion.combo.xsub.private_rebind(inverse12_keep_norm,
                                               companion.combo.synth.replacements)
    def consume(b,x):return inverse(b,x,ceiling)
    scope['inverse12_keep_norm']=consume
    original_character=scope['linear_inverse_character']
    source=inspect.getsource(companion.retained.linear_inverse_character)
    source=source.replace('def linear_inverse_character(b,g,constant,terms):',
                          'def linear_inverse_character(b,g,constant,terms,saved_norm):')
    before='D=b.alloc_qubits(6);core.norm_xor_noscratch(b,g,D,kval)'
    assert before in source
    source=source.replace(before,'D=core.norm_cache.rebuild(b,g,saved_norm,kval)')
    character_scope=dict(original_character.__globals__)
    def keep_for_ceiling(b,D):
        count=min(6,max(0,ceiling-b.num_allocated_qubits-6))
        columns,back=norm_cache.layout(count)
        saved=b.alloc_qubits(count)
        ns.ar.linear_xor(b,D,saved,[v&((1<<count)-1)for v in columns])
        return saved
    original_core=character_scope['core']
    cache=SimpleNamespace(**dict(vars(original_core.norm_cache),keep=keep_for_ceiling))
    character_scope['core']=SimpleNamespace(**dict(vars(original_core),norm_cache=cache))
    exec(compile(source,__file__,'exec'),character_scope)
    scope['linear_inverse_character']=character_scope['linear_inverse_character']
    source=inspect.getsource(companion.extraction_companion)
    source=source.replace('im = inverse_stream_noscratch(b, D)',
                          'im, saved_norm = inverse12_keep_norm(b, D)')
    source=source.replace('[(N, nm), (ratio, rm), (L, sm)])',
                          '[(N, nm), (ratio, rm), (L, sm)], saved_norm)')
    exec(compile(source,__file__,'exec'),scope)
    return companion.combo.xsub.clone(entry,dict(entry.__globals__,extraction=scope['extraction_companion']))


decode=install(companion.combo.decode)
