"""Complete experimental reverse root retirement with exact reconstruction."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(Path(__file__).resolve().parent),
                str(ROOT/'research/integrated'), str(ROOT/'research/agents/a08'),
                str(ROOT/'research/agents/a01')]
import decode_compact_integrated as reference
import scalar_compact_v3 as scalar
from rebind_graph import private_rebind
p = scalar.p


def look_root_cached(b, O, g, payloads, reverse, phase):
    m=len(O); keep=m in KEEP_CHILD; full=m in KEEP_FULL
    F=phase['held_gap'].pop(m) if reverse and full else old.fresh_zero_flag(b,g[-1])
    if reverse and not full:consume_flag(b,F,phase['gap_flags'].pop(m))
    pivot(b,g,F); a=g[-1]; ai,Z=old.inverse_zero(b,a); b.cx(Z,ai[0])
    if reverse:
        mask=phase.pop('_root_inverse_mask'); b.cz(ai,mask); b.free(mask)
    f=list(O)+[ai]
    if reverse:
        H=phase['held_gap'][m-1]
        mask=b.alloc_bits(1); b.hmr(Z,mask[0]); b.free(Z)
        b.ccz(F,H,mask[0]); b.free(mask)
        gap_zero_action(b,f,g,payloads,ai,F,H,post=True,undo=True)
    else:
        root_pre_partial(b,f,g,payloads,ai,Z,F)
        erase_product_zero(b,a,ai,Z)
    pivot(b,g,F); aligned(b,f,g,F)
    if reverse or keep:phase['given_gap'][m]=F
    else:phase['incoming_gap'][m]=hold_flag(b,F)
    parent=([v[-1] for v in payloads],f[-1],f[-2])
    if not reverse:
        phase['_root_block_payloads']=payloads
        root_mask=b.alloc_bits(12); b.hmr(ai,root_mask); b.free(ai)
        phase['_ephemeral_root']=(ai,root_mask)
    old.look_solve(b,g,f[:-2],[v[:-1] for v in payloads],None,parent,reverse,phase)
    if reverse and not keep:
        F=old.fresh_zero_flag(b,g[-1]); consume_flag(b,F,phase['return_mask'].pop(m))
    else:F=phase['returned_gap'].pop(m)
    aligned(b,f,g,F); pivot(b,g,F)
    if not reverse:
        H=phase['held_gap'][m-1]
        gap_zero_action(b,f,g,payloads,ai,F,H,post=True,undo=False)
    else:
        saved,mask=phase.pop('_a12_reverse_root')
        replacement,Z=old.inverse_zero(b,a)
        b.cx(Z,replacement[0]); saved[:]=replacement
        b.cz(ai,mask); b.free(mask)
        root_action(b,f,g,payloads,ai,Z,F,post=False,undo=True)
        erase_product_zero(b,a,ai,Z)
    mask=b.alloc_bits(12); b.hmr(ai,mask); b.free(ai)
    if reverse:phase_inverse34(b,a,mask,zero_mask=mask[0]); b.free(mask)
    else:phase['_root_inverse_mask']=mask
    pivot(b,g,F)
    if reverse:clear_flag(b,g[-1],F)
    elif full:phase['held_gap'][m]=F
    else:phase['gap_flags'][m]=hold_flag(b,F)


def install(cv):
    cells=dict(zip(cv.__code__.co_freevars,cv.__closure__))
    short=cells['core'].cell_contents.__globals__
    scope=scalar.scope_of(cv)
    original=scope['direct_post']

    def direct_post(b,f,g,payloads,F,H,parent,reverse=False,incoming=None,defer=False,phase=None):
        result=original(b,f,g,payloads,F,H,parent,reverse,incoming,defer,phase)
        if reverse and len(f)-1==16 and phase['_short_monic']:
            held=parent[1]
            mask=b.alloc_bits(12); b.hmr(held,mask); b.free(held)
            phase['_a12_reverse_root']=(held,mask)
        return result

    scope['direct_post']=direct_post
    short['look_root_cached']=p.clone(look_root_cached,short)
    return cv


def make_decoder():
    decoder=private_rebind(reference.decode,{},p.ROOT)
    install(scalar.converter_of(decoder))
    return decoder
