"""Retire the root inverse during forward descent; rebuild it at child return.

The returned child still holds its quotient head q and raw divisor g.
With F=[q=0], H=[g[-1]=0], K the next held gap, and clipped selected
child pivot a_c, the clipped original root pivot is
    R=q*a_c + F*g[-1] + F*H.
It is nonzero on every completed coefficient bank. The original root
inverse is therefore inv(R), and its measured character is consumed there.
"""
import inspect


def restore_root(b,f,g,Fchild,phase):
    held,mask=phase.pop('_ephemeral_root')
    q=f[-1]
    Froot=fresh_zero_flag(b,q)
    K=phase['held_gap'][15]
    R=b.alloc_qubits(12)
    pivot(b,g,Fchild)
    b.ccx(Fchild,K,g[-1][0])
    ar.mul_xor0(b,q,g[-1],R)
    b.ccx(Fchild,K,g[-1][0])
    pivot(b,g,Fchild)
    for x,y in zip(g[-1],R):b.ccx(Froot,x,y)
    b.ccx(Froot,Fchild,R[0])
    phase['_root_early_flag']=Froot
    replacement=inverse_initialized(b,R)
    rm=b.alloc_bits(12);b.hmr(R,rm);b.free(R)
    phase['_root_pivot_debt']=rm
    held[:]=replacement
    b.cz(held,mask);b.free(mask)



def root_pre_partial(b,f,g,payloads,ai,Z,F):
    a=g[-1];q0,q1=f[-2:];b.cx(Z,a[0])
    for v in payloads:old.scale(b,v[-1],a,ai,True)
    cutoff=len(g)-3
    for i in range(cutoff,len(g)-1):
        with dk.selected(b,g[i],g[i-1],F) as coefficient:
            for v in payloads:ar.mul_xor0(b,coefficient,v[-1],v[i])
    with dk.selected(b,g[-2],g[-3],F) as c:ar.mul_xor0(b,q1,c,q0)
    old.scale(b,q0,a,ai,True)
    dk.shifted_conv(b,g[:-1],[q0,q1],f[:-2],F)
    b.cx(Z,a[0])

def install(cv,p):
    cells=dict(zip(cv.__code__.co_freevars,cv.__closure__))
    short=cells['core'].cell_contents.__globals__
    scope=short['old'].direct_post.__globals__
    scope['phase_inverse_for_root']=short['phase_inverse34']
    scope['restore_root']=p.clone(restore_root,scope)
    original=scope['direct_post']
    def direct_post(b,f,g,payloads,F,H,parent,reverse=False,incoming=None,defer=False,phase=None):
        if not reverse and len(f)-1==16 and '_ephemeral_root' in phase:
            scope['restore_root'](b,f,g,F,phase)
        result=original(b,f,g,payloads,F,H,parent,reverse,incoming,defer,phase)
        if not reverse and len(f)-1==16 and '_root_pivot_debt' in phase:
            debt=phase.pop('_root_pivot_debt');Froot=phase['returned_gap'][17]
            b.cz(f[-1],debt)
            for x,y in zip(g[-1],debt):b.ccz(Froot,x,y)
            b.ccz(Froot,F,debt[0]);b.free(debt)
        return result
    scope['direct_post']=direct_post
    qsource=inspect.getsource(scope['q_post'])
    needle='        F = fresh_zero_flag(b, q)'
    assert qsource.count(needle)==1
    qsource=qsource.replace(needle,"        F = phase.pop('_root_early_flag') if '_root_early_flag' in phase else fresh_zero_flag(b, q)")
    exec(compile(qsource,__file__,'exec'),scope)
    scope['q_post']=scope['root_child_post']
    short['root_pre_partial']=p.clone(root_pre_partial,short)
    source=inspect.getsource(short['look_root_cached'])
    needle='    old.look_solve(b,g,f[:-2],[v[:-1]for v in payloads],None,parent,reverse,phase)'
    assert source.count(needle)==1
    replacement="""    if not reverse:
        root_mask=b.alloc_bits(12);b.hmr(ai,root_mask);b.free(ai)
        phase['_ephemeral_root']=(ai,root_mask)
"""+needle
    source=source.replace(needle,replacement)
    needle='        root_action(b,f,g,payloads,ai,Z,F,post=False,undo=False)'
    assert source.count(needle)==1
    source=source.replace(needle,'        root_pre_partial(b,f,g,payloads,ai,Z,F)')
    needle='    parent=([v[-1]for v in payloads],f[-1],f[-2])'
    assert source.count(needle)==1
    source=source.replace(needle,needle+"\n    if not reverse:phase['_root_block_payloads']=payloads")
    exec(compile(source,__file__,'exec'),short)
    return cv
