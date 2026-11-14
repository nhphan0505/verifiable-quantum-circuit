"""Exact partitioned zero predicates chosen at the current live width."""
from functools import lru_cache
import frozen_chart as frozen

TRACE=[]

def partitions(n,lo=1):
    if not n:
        yield ()
    for a in range(lo,n+1):
        for rest in partitions(n-a,a):yield (a,)+rest

def metrics(parts,phase):
    groups=sorted((n for n in parts if n>1),reverse=True)
    k=len(groups);m=len(parts)
    if m<2:return None
    peak=0
    for i,n in enumerate(groups):peak=max(peak,i+n-1)
    peak=max(peak,k+m-(2 if phase else 1))
    # Aggregate ladder has gone. Erase small groups first, big groups last.
    for i,n in enumerate(reversed(groups)):
        if n>2:peak=max(peak,k-i-1+(0 if phase else 1)+n-2)
    mean=sum(n-1 for n in groups)+m-(2 if phase else 1)+sum(n-2 for n in groups)/2
    return mean,peak

@lru_cache(None)
def plan(n,space,phase):
    options=[]
    for p in partitions(n):
        z=metrics(p,phase)
        if z is not None and z[1]<=space:options.append((z[0],z[1],p))
    if not options:raise ValueError(('no zero partition',n,space,phase))
    return min(options)

def phase_and(b,x):
    if len(x)==2:b.cz(x[0],x[1]);return
    nodes=b.alloc_qubits(len(x)-2)
    b.init_and(x[0],x[1],nodes[0])
    for j in range(1,len(nodes)):b.init_and(nodes[j-1],x[j+1],nodes[j])
    b.cz(nodes[-1],x[-1])
    for j in reversed(range(len(nodes))):
        if j:b.del_and(nodes[j-1],x[j+1],nodes[j])
        else:b.del_and(x[0],x[1],nodes[0])
    b.free(nodes)

def predicate(b,x,phase):
    live=b.num_allocated_qubits
    mean,peak,parts=plan(len(x),889-live,phase)
    TRACE.append(dict(n=len(x),phase=phase,live=live,parts=parts,mean=mean,scratch=peak))
    b.x(x);groups=[];controls=[];offset=0
    for n in sorted(parts,reverse=True):
        group=x[offset:offset+n];offset+=n
        if n==1:controls.append(group[0])
        else:
            flag=frozen.and_flag(b,group)
            groups.append((group,flag));controls.append(flag)
    if phase:phase_and(b,controls);out=None
    else:out=frozen.and_flag(b,controls)
    for group,flag in reversed(groups):
        if len(group)==2:b.del_and(group[0],group[1],flag);b.free(flag)
        else:
            mask=b.alloc_bits(1);b.hmr(flag,mask[0]);b.free(flag)
            b.push_condition(mask[0]);phase_and(b,group);b.pop_condition();b.free(mask)
    b.x(x)
    return out

def zero_flag24(b,x):return predicate(b,x,False)
def clean_zero_phase24(b,x):predicate(b,x,True)
