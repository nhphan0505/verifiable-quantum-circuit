"""Defer the known-one implicit leader during the first reverse fold.

The released twelve wires permit a retained twelve-bit inverse in that one
fold. The leader is allocated only after divider scratch is completely gone.
"""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import inspect,sys
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'root')]
import decode_outer_alias_constant as outer
from decode_low_crt import combo,crt_matrix

@lru_cache(None)
def virtual_matrix(k,c,kap):
    return tuple(tuple(row[:-1])for row in crt_matrix(k,c,kap)[:-1])


def divide_retained_u(b,x,y,F,fm,after,K=None):
    b.cx(F,y[0]);b.cx(y[12:],y[:12])
    oldmask=multiply_forward99(b,x,y,K)
    b.cx(y[12:],y[:12])
    N=b.alloc_qubits(12);norm_xor_noscratch(b,y,N,K)
    u=inverse_initialized(b,N)
    for off in(0,12):
        half=x[off:off+12];out=b.alloc_qubits(12)
        ar.mul_xor0(b,half,u,out)
        ar.erase_product(b,out,N,half)
        b.swap(half,out);b.free(out)
    phase_product24(b,x,y,oldmask,K);b.free(oldmask)
    b.cx(F,y[0]);b.cx(F,N[0])
    after()
    mask=b.alloc_bits(1);b.hmr(F,mask[0]);b.free(F)
    b.cx(fm[0],mask[0]);b.free(fm)
    b.z(mask[0]);pm=b.alloc_bits(12);b.bit_store(pm,False)
    b.cx(mask[0],pm[0]);ar.phase_product(b,N,u,pm)
    b.free(pm);b.free(mask)
    um=b.alloc_bits(12);b.hmr(u,um);b.free(u)
    phase_inverse34(b,N,um,zero_mask=um[0]);b.free(um)
    ar._erase_norm(b,y,N,K);b.free(N)


def absorb_virtual_one(b,head,A,B,Q,r,c,kap,reverse=False,transcript=None):
    assert reverse and len(B)==33 and c==0
    k=len(B);out=head+B
    value=old.eval_implicit(b,A,Q,c);F=dv.zero_flag(b,value)
    old.eval_implicit(b,A,Q,c,True)
    linear_words(b,out,virtual_matrix(k,c,kap))
    v=epow(c,k+2);co=[(v&4095)^mul(c,v>>12),v>>12]
    for word,a in zip(head,co):
        for j in ar.bits(a):b.x(word[j])
    constant_alias(b,F,head,co)
    value=old.eval_implicit(b,A,Q,c);cx(b,head[1],head[0],c)
    hm,fm=transcript
    def after():
        cx(b,head[1],head[0],c);old.eval_implicit(b,A,Q,c,True)
        b.cx(F,A[0][0]);low_product(b,head,A,B);b.cx(F,A[0][0])
        q_times_low(b,B,kap,True)
        old.eval_implicit(b,A,Q,c)
    divide_retained_u(b,combine(head),value,F,fm,after,K)
    b.cz(combine(head),hm);b.free(hm)
    old.eval_implicit(b,A,Q,c,True)
    reclaim(b,[r]);b.x(r[0]);ar.mul_xor0(b,head[1],Q,r)
    return out,A,transcript


def install(entry):
    synth=entry.__globals__['synthesize'];folds=synth.__globals__['folds'];ug=dict(folds.ug)
    original=ug['absorb_even'];div=original.__globals__['divide_fused']
    divscope=dict(div.__globals__,inverse_initialized=synth.__globals__['inverse_initialized'],
                  phase_inverse34=combo.xsub.phase_inverse12_virtual)
    newdiv=combo.xsub.clone(divide_retained_u,divscope)
    scope=dict(original.__globals__,virtual_matrix=virtual_matrix,constant_alias=outer.constant_alias,
               divide_retained_u=newdiv)
    special=combo.xsub.clone(absorb_virtual_one,scope)
    def choose(b,head,A,B,Q,r,c,kap,reverse=False,transcript=None):
        fn=special if len(B)==33 and c==0 else original
        return fn(b,head,A,B,Q,r,c,kap,reverse,transcript)
    ug['absorb_even']=choose
    fs=SimpleNamespace(**dict(vars(folds),ug=ug))
    # Build from the supplied canonical driver because the current driver
    # was compiled dynamically by the full-fold source transform.
    source=inspect.getsource(combo.decode.__globals__['synthesize'])
    old='''        if i%2:
            ar.mul_xor0(b,heads[i][1],r,border);qi,p=r,border
            A,B,t=folds.sg['absorb'](b,heads[i],A,B,qi,p,None,0,cs[i],ks[i],wide=False)
        else:
            qi,p=border,r
            A,B,t=folds.sg['absorb_even'](b,heads[i],A,B,qi,r,cs[i],ks[i])'''
    new='''        qi,p=(r,border) if i%2 else (border,r)
        A,B,t=folds.sg['absorb_even'](b,heads[i],A,B,qi,p,cs[i],ks[i])'''
    assert old in source;source=source.replace(old,new)
    old='''            if i%2:
                folds.ug['absorb'](b,heads[i],aa,bb,qi,p,None,0,cs[i],ks[i],True,t,False)
                ar.mul_xor0(b,heads[i][1],r,border)
            else:folds.ug['absorb_even'](b,heads[i],aa,bb,qi,r,cs[i],ks[i],True,t)'''
    new="            folds.ug['absorb_even'](b,heads[i],aa,bb,qi,p,cs[i],ks[i],True,t)"
    assert old in source;source=source.replace(old,new)
    edits=(
        ('b.cx(border,r);b.cx(border,d);b.cx(r,border);b.x(border[0])','b.cx(border,r);b.cx(r,border);b.x(border[0])'),
        ('folds.add_tail(b,heads[i],qi,d,bool(i%2))','folds.add_tail(b,heads[i],qi,d,not bool(i%2))'),
        ('ar.mul_xor0(b,r,border,d);tt=tail_inplace','tt=tail_inplace'),
        ('tail_inplace(b,r,border,d,u,v,pole,True,tt);ar.mul_xor0(b,r,border,d)','tail_inplace(b,r,border,d,u,v,pole,True,tt)'),
        ('b.cx(r,d);b.x(border[0]);b.cx(r,border);b.cx(border,r);b.free(r)','b.x(border[0]);b.cx(r,border);b.cx(border,r);b.free(r)'),
        ("        folds.ug['reclaim'](b,[border]);b.x(border[0])\n",''),
    )
    for before,after in edits:
        assert before in source;source=source.replace(before,after)
    env=dict(synth.__globals__,folds=fs)
    exec(compile(source,__file__,'exec'),env)
    result=combo.xsub.clone(entry,dict(entry.__globals__,synthesize=env['synthesize']))
    assert result.__globals__['convert_safe'] is entry.__globals__['convert_safe']
    assert result.__globals__['baseline'] is entry.__globals__['baseline']
    return result


decode=install(outer.decode)
