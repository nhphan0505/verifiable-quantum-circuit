"""Exact middle fusion of the root pre and its first two child pres."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(Path(__file__).resolve().parent),str(ROOT/'research/agents/a01'),
              str(ROOT/'research/agents/a03'),str(ROOT/'research/agents/a09')]
import blocked_three_noscratch as base
p=base.p
from rebind_graph import private_rebind


def look_solve(b,f,g,payloads,H=None,parent=None,reverse=False,phase=None):
    if reverse or '_root_block_payloads' not in phase:
        return ordinary_solve(b,f,g,payloads,H,parent,reverse,phase)
    m=len(f)-1;assert m==16
    root_payloads=phase.pop('_root_block_payloads')
    cutoff=m-2;frames=[]
    for i in range(2):
        n=len(f)-1;F=fresh_zero_flag(b,g[-1])
        carry=pre_partial(b,f,g,payloads,F,cutoff,i==1)
        frames.append((n,f,g,payloads,H,parent,F,carry))
        if i==1:break
        aligned(b,f,g,F)
        phase['incoming_gap'][n]=hold_flag(b,F)
        childparent=([v[-1]for v in payloads],f[-1],f[-2])
        f,g,payloads,H,parent=g,f[:-2],[v[:-1]for v in payloads],None,childparent
    F0=fresh_zero_flag(b,frames[0][1][-1])
    F1=fresh_zero_flag(b,frames[1][1][-1])
    F2=frames[1][6]
    for j in range(len(payloads)):
        heads=[root_payloads[j][-1]]+[frame[3][j][-1] for frame in frames]
        payload_middle(b,f[:cutoff],g[:cutoff],heads,payloads[j][:cutoff],
                       frames[0][1][-2:],F0,F1,F2)
    for flag,n in ((F0,m+1),(F1,m)):
        mask=hold_flag(b,flag)
        b.cx(mask,phase['incoming_gap'][n]);b.free(mask)
    pivot(b,g,F2);dk.shifted_conv(b,g[:-1],f[-2:],f[:-2],F2);pivot(b,g,F2)
    aligned(b,f,g,F2);phase['incoming_gap'][m-1]=hold_flag(b,F2)
    childparent=([v[-1]for v in payloads],f[-1],f[-2])
    look_solve(b,g,f[:-2],[v[:-1]for v in payloads],None,childparent,False,phase)
    for n,f,g,payloads,H,parent,unused,carry in reversed(frames):
        F=phase['returned_gap'].pop(n);aligned(b,f,g,F)
        phase['a'][n]=direct_post(b,f,g,payloads,F,H,parent,
                                 incoming=carry,defer=True,phase=phase)
        if n in KEEP_FULL:phase['held_gap'][n]=F
        else:phase['gap_flags'][n]=hold_flag(b,F)


def make_decoder(hankel=False):
    cv=p.install_dot_cache(p.install_base_zero(p.install_undo_zeros(
        p.install_child_inverse(p.install_retained_gaps(p.make_converter())))))
    cells=dict(zip(cv.__code__.co_freevars,cv.__closure__))
    short=cells['core'].cell_contents.__globals__
    scope=short['old'].direct_post.__globals__
    scope.update(ordinary_solve=scope['look_solve'],
                 convolution=lambda b,x,y,out: scope['dk'].conv(b,x,y,out,len(x)+len(y)-1),
                 phase_classical_parity=base.phase_classical_parity)
    for fun in (base.mask_word,base.erase_mask,base.copy_flag,base.phase_flag,
                base.payload_middle,base.pre_partial,look_solve):
        scope[fun.__name__]=p.clone(fun,scope)
    short['old'].look_solve=scope['look_solve']
    from ephemeral_root_block import install
    install(cv,p)
    if hankel:
        from descending_overlap import install as install_hankel
        install_hankel(cv,maximum=18,max_sources=8)
    cv=private_rebind(cv,p.base.replacements,p.ROOT)
    import local_norm
    return local_norm.make_decoder(count=1,plain_count=1,plain_levels=(3,4,5),
                                   converter=cv,reference_decode=p.decode,factorized=True)


decode=make_decoder()
