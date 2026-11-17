"""Balanced division and early sign retirement for the Q44 INV-74 circuit.

Syed Asad Ali is the original builder (NOTICE.txt). A triangular ripple
initializer computes (4094-3*v+P11+P12-2*P13) modulo 2**14. Twelve feed rows
consume P11..P0, then the first sign is retired through its root/sign code and
its owner feeds an exact zero bit in row 24. Eleven further rows rotate the
remainder, truncating at k=j-25 from row 27. Carry debts are retained for the
inverse; their input carries are retired early to maintain the 44-qubit cap.
"""
from dataclasses import dataclass
import coefficient as cf
import kickmix as km


@dataclass
class DividerToken:
    v: list
    flags: list
    initial_u: tuple
    u: list
    history: dict
    rows: list
    product: list
    coefficient_outcomes: list


def forward(cb,ar,v,P,flags,D):
    """Consume coefficient owners, compute the balanced quotient endpoint."""
    v,P,flags=list(v),list(P),list(flags)
    coefficient_outcomes=[cf.retire(cb,z) for z in D]
    u=list(cb.alloc_qubits(14));initial_u=tuple(u)
    for z in (v[0],P[11],P[12]):cb.cx(z,u[0])
    cb.x(u[1])
    for z in (v[1],P[12],P[13]):cb.cx(z,u[1])
    cb.cx(P[12],v[0]);cb.cx(P[12],P[11]);cb.ccx(v[0],P[11],u[1]);cb.cx(P[12],P[11]);cb.cx(P[12],v[0])
    for z in (v[0],v[2],P[13]):cb.cx(z,u[2])
    cb.cx(u[1],v[1]);cb.cx(u[1],P[13]);cb.ccx(v[1],P[13],u[2]);cb.cx(u[1],P[13]);cb.cx(u[1],v[1])
    for i in range(3,13):
     if i==12:cb.x(u[i]);linear=(v[i-3],v[i-2])
     else:linear=(v[i-3],v[i-2],v[i])
     for z in linear:cb.cx(z,u[i])
     cb.cx(u[i-1],v[i-3]);cb.cx(u[i-1],v[i-1]);cb.ccx(v[i-3],v[i-1],u[i]);cb.cx(u[i-1],v[i-1]);cb.cx(u[i-1],v[i-3])
    cb.cx(v[11],u[13]);cb.ccx(v[10],u[12],u[13])
    m=cf.retire(cb,P[12]);cb.push_condition(m)
    for z in (v[0],P[11],u[0]):cb.z(z)
    cb.pop_condition();cb.free(m)
    m=cf.retire(cb,P[13]);cb.cx(m,km.xbool(True));cb.push_condition(m)
    for z in (v[0],v[1],P[11],u[1]):cb.z(z)
    for a,b in ((v[0],P[11]),(v[0],u[0]),(P[11],u[0])):cb.cz(a,b)
    cb.pop_condition();cb.free(m);P[12]=P[13]=None
    history={};rows=[]
    def feed_carry(prev,cur,sign,known_zero=False):
     z=cb.alloc_qubits(1)[0]
     for t in (v[0],prev,cur):
      if t is not None:cb.cx(t,z)
     if cur is not None:cb.cx(cur,v[0])
     cb.cx(sign,v[0])
     if cur is not None:cb.cx(cur,prev)
     if not known_zero:cb.ccx(v[0],prev,z)
     if cur is not None:cb.cx(cur,prev)
     cb.cx(sign,v[0])
     if cur is not None:cb.cx(cur,v[0])
     return z
    
    def erase_feed(z,prev,cur,sign):
     m=cf.retire(cb,z);cb.push_condition(m);cb.z(v[0]);cb.z(prev)
     terms=[(v[0],prev)]
     if cur is not None:terms.extend([(v[0],cur),(prev,cur)])
     terms.append((prev,sign))
     if cur is not None:terms.append((cur,sign))
     for a,b in terms:cb.cz(a,b)
     cb.pop_condition();cb.free(m)
    
    def frame(sign,target):
     for z in target:cb.x(z);cb.cx(sign,z)
    for j in range(12,36):
     pass
     if j<=24:
      if j==24:
       old=history.pop(12);m=cf.retire(cb,old);cb.push_condition(m);cb.z(v[11]);cb.z(v[10]);cb.cz(v[10],history[13]);cb.pop_condition();cb.free(m);prev=cb.alloc_qubits(1)[0];cur=None
      else:prev=P[23-j];cur=P[22-j] if j<23 else None
      sign=u[-1];target=u[:-1];c=feed_carry(prev,cur,sign,known_zero=j==24);frame(sign,target)
      debt=cf.disposable(ar,cb,v[1:],target,c,lambda z:erase_feed(z,prev,cur,sign))
      cb.cx(target[-2],target[-1]);cb.x(target[-2]);frame(sign,target)
      cb.cx(v[0],prev);cb.cx(sign,prev)
      if cur is not None:cb.cx(cur,prev)
      u=[prev]+target;history[j]=sign
      if j<24:P[23-j]=None
      k=0
     else:
      k=j-25 if j>=27 else 0;u=[u[-1]]+u[:-1];sign=u[0];target=u[k+1:];frame(sign,target)
      debt=ar.forward_add(cb,v[k+1:],target,carry_in=v[k])
      cb.cx(target[-2],target[-1]);cb.x(target[-2]);frame(sign,target);cb.cx(v[0],u[0])
     rows.append((j,k,debt))
    return DividerToken(v,flags,initial_u,u,history,rows,P,coefficient_outcomes)
