"""Use the released pole-flag space for the completed source predicate.

The chosen plan depends only on the public live-wire count. All plans are
exact reversible zero predicates and retain the same completed chart.
"""
import inspect
from direct_owned_companion import clone
import owned_fused_companion as implementation
import early_shared_companion as original
from adaptive_zero import plan,phase_and
import frozen_chart as frozen


def selected_zero(b,x,borrow):
    try:_,_,parts=plan(len(x),892-b.num_allocated_qubits,False)
    except ValueError:
        F=b.alloc_qubits(1)[0];original.zero_toggle(b,x,F,borrow);return F
    b.x(x);groups=[];controls=[];offset=0
    for n in sorted(parts,reverse=True):
        group=x[offset:offset+n];offset+=n
        if n==1:controls.append(group[0])
        else:
            flag=frozen.and_flag(b,group);groups.append((group,flag));controls.append(flag)
    F=frozen.and_flag(b,controls)
    for group,flag in reversed(groups):
        if len(group)==2:b.del_and(group[0],group[1],flag);b.free(flag)
        else:
            m=b.alloc_bits(1);b.hmr(flag,m[0]);b.free(flag)
            b.push_condition(m[0]);phase_and(b,group);b.pop_condition();b.free(m)
    b.x(x);return F


source=inspect.getsource(original.normalize_first)
old='F=b.alloc_qubits(1)[0];zero_toggle(b,g,F,r);b.cswap(F,r,g)'
assert source.count(old)==1
source=source.replace(old,'F=selected_zero(b,g,r);b.cswap(F,r,g)')
scope=dict(original.normalize_first.__globals__,selected_zero=selected_zero)
exec(compile(source,__file__,'exec'),scope)
normalize_first=scope['normalize_first']
finish_factory=implementation.finish_factory
install=clone(implementation.install,dict(implementation.install.__globals__,normalize_first=normalize_first))
OWNER_LOG=implementation.OWNER_LOG
