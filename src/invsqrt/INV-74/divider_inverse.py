"""Inverse balanced division, history restoration and triangular cleanup.

Original circuit builder: Syed Asad Ali (NOTICE.txt). Each forward carry debt
is consumed once. The seven-input sign decoder is a small Boolean polynomial
certificate; it contains neither physical gate operands nor a circuit tape.
"""
from pathlib import Path
import json
import kickmix as km
import coefficient as cf
HERE=Path(__file__).resolve().parent


def inverse(cb,ar,book,token):
    v,u,flags,history,rows,P=(token.v,token.u,token.flags,token.history,token.rows,token.product)
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
    outcomes={}
    for j in (13,14,15,24):outcomes[j]=cf.retire(cb,history.pop(j))
    for j,k,debt in reversed(rows):
     if j<=24:break
     cb.cx(v[0],u[0]);sign=u[0];target=u[k+1:]
     frame(sign,target);cb.x(target[-2]);cb.cx(target[-2],target[-1])
     dirty=flags+[x for x in P if x is not None]+list(history.values())
     ar.inverse_add(cb,v[k+1:],target,debt,carry_in=v[k],dirty_wires=dirty)
     frame(sign,target);u=u[1:]+u[:1]

    # The final feed consumed an exact zero; its saved sign is low xor v0.
    j,k,debt=next(row for row in rows if row[0]==24);cb.cx(v[0],u[0]);sign=u[0];m=outcomes.pop(24);cb.push_condition(m);cb.z(sign);cb.pop_condition();cb.free(m);target=u[1:]
    frame(sign,target);cb.x(target[-2]);cb.cx(target[-2],target[-1]);dirty=flags+list(history.values());ar.inverse_add(cb,v[1:],target,debt,carry_in=v[0],dirty_wires=dirty);frame(sign,target);u=target+[sign]
    for j,k,debt in reversed(rows):
     if j>23:continue
     if j<=15:break
     low=u[0];target=u[1:];sign=history[j];cur=P[22-j] if j<23 else None
     carry=feed_carry(low,cur,sign);frame(sign,target);cb.x(target[-2]);cb.cx(target[-2],target[-1])
     dirty=flags+[x for x in P if x is not None]+list(history.values())
     released=ar.inverse_add(cb,v[1:],target,debt,carry_in=carry,dirty_wires=dirty,carry_lifecycle=(lambda c:erase_feed(c,low,cur,sign),lambda:feed_carry(low,cur,sign)))
     frame(sign,target)
     if not released:erase_feed(carry,low,cur,sign)
     if cur is not None:cb.cx(cur,low)
     cb.cx(sign,low);cb.cx(v[0],low);P[23-j]=low;u=target+[sign];del history[j]

    form=json.loads((HERE/'data/history_code.json').read_text())
    def form_frame(f,vals):
     a,b=[vals[i] for i in f['pivots']];trace=[]
     for order,target in ((f['left_order'],a),(f['right_order'],b)):
      for i in order:cb.cx(vals[i],target);trace.append((vals[i],target))
     return a,b,trace
    def undo(trace):
     for a,b in reversed(trace):cb.cx(a,b)
    def restore_form(form,outcome):
     vals=[v[item[1]] if item[0]=='v' else u[-1] for item in form['inputs']];n=len(vals);target=cb.alloc_qubits(1)[0];helpers=[]
     for i in form['output_linear_order']:
      if i<n:cb.cx(vals[i],target)
     for hi,plan in enumerate(form['helpers']):
      z=cb.alloc_qubits(1)[0]
      for f in plan['factors']:
       a,b,trace=form_frame(f,vals);cb.ccx(a,b,z);undo(trace)
      vals.append(z);helpers.append(z)
      if n+hi in form['output_linear_order']:cb.cx(z,target)
     for f in form['output_factors']:
      a,b,trace=form_frame(f,vals);cb.ccx(a,b,target);undo(trace)
     for z,plan in reversed(list(zip(helpers,form['helpers']))):
      m=cf.retire(cb,z);cb.push_condition(m)
      for i in plan.get('phase_linear_order',[]):cb.z(vals[i])
      for f in plan['phase_factors']:
       a,b,trace=form_frame(f,vals);cb.cz(a,b);undo(trace)
      cb.pop_condition();cb.free(m)
     cb.push_condition(outcome);cb.z(target);cb.pop_condition();cb.free(outcome)
     return target
    sign=restore_form(form,outcomes.pop(15));history[15]=sign
    j,k,debt=next(row for row in rows if row[0]==15);low=u[0];target=u[1:];cur=P[22-j];carry=feed_carry(low,cur,sign);frame(sign,target);cb.x(target[-2]);cb.cx(target[-2],target[-1]);dirty=flags+[x for x in P if x is not None]+list(history.values())
    released=ar.inverse_add(cb,v[1:],target,debt,carry_in=carry,dirty_wires=dirty,carry_lifecycle=(lambda c:erase_feed(c,low,cur,sign),lambda:feed_carry(low,cur,sign)))
    frame(sign,target)
    if not released:erase_feed(carry,low,cur,sign)
    cb.cx(cur,low);cb.cx(sign,low);cb.cx(v[0],low);P[23-j]=low;u=target+[sign];del history[j]

    formulas={
    14:dict(parents=[7,8,9,10,11,'next'],helpers=[dict(width=6,constant=0,linear=0,edges=[(1,3)]),dict(width=6,constant=0,linear=16,edges=[(0,1),(0,2),(0,4),(1,4),(1,5),(2,4),(2,5),(4,5)])],decoder=dict(width=8,constant=0,linear=186,edges=[(0,2),(0,3),(0,4),(0,5),(0,7),(1,2),(1,4),(1,6),(2,3),(2,4),(2,5),(2,6),(2,7),(3,4),(3,5),(3,6),(4,5),(4,7),(5,7),(6,7)])),
    13:dict(parents=[8,9,10,11,'next'],helpers=[dict(width=5,constant=0,linear=2,edges=[(0,1),(0,2),(1,2),(1,3),(2,3)])],decoder=dict(width=6,constant=0,linear=46,edges=[(1,3),(1,5),(3,4),(4,5)]))}
    def plan(spec):return book.factor_polynomial(spec['width'],spec['constant'],spec['linear'],set(map(tuple,spec['edges'])))
    def restore_formula(j,outcome):
     f=formulas[j];base=[u[-1] if x=='next' else v[x] for x in f['parents']];helpers=[];plans=[];inputs=[]
     for spec in f['helpers']:
      variables=base+helpers[:spec['width']-len(base)];pp=plan(spec);z=cb.alloc_qubits(1)[0];book.emit_xor(cb,variables,z,pp);helpers.append(z);plans.append(pp);inputs.append(variables)
     target=cb.alloc_qubits(1)[0];book.emit_xor(cb,base+helpers,target,plan(f['decoder']));cb.push_condition(outcome);cb.z(target);cb.pop_condition();cb.free(outcome)
     for z,pp,variables in reversed(list(zip(helpers,plans,inputs))):
      m=cf.retire(cb,z);book.emit_phase(cb,variables,m,pp);cb.free(m)
     return target
    for j in (14,13,12):
     if j in outcomes:sign=restore_formula(j,outcomes.pop(j))
     else:
      sign=cb.alloc_qubits(1)[0];cb.cx(v[11],sign);cb.cx(v[10],sign);cb.ccx(v[10],u[-1],sign)
     history[j]=sign
     k,debt=next((k,debt) for jj,k,debt in rows if jj==j);low=u[0];target=u[1:];cur=P[22-j];carry=feed_carry(low,cur,sign);frame(sign,target);cb.x(target[-2]);cb.cx(target[-2],target[-1]);dirty=flags+[x for x in P if x is not None]+list(history.values())
     released=ar.inverse_add(cb,v[1:],target,debt,carry_in=carry,dirty_wires=dirty,carry_lifecycle=(lambda c:erase_feed(c,low,cur,sign),lambda:feed_carry(low,cur,sign)))
     frame(sign,target)
     if not released:erase_feed(carry,low,cur,sign)
     cb.cx(cur,low);cb.cx(sign,low);cb.cx(v[0],low);P[23-j]=low;u=target+[sign];del history[j]

    P[12],P[13]=list(cb.alloc_qubits(2))
    for z in (v[0],P[11],u[0]):cb.cx(z,P[12])
    cb.x(P[13])
    for z in (v[0],v[1],P[11],u[0],u[1]):cb.cx(z,P[13])
    cb.cx(u[0],v[0]);cb.cx(u[0],P[11]);cb.ccx(v[0],P[11],P[13]);cb.cx(u[0],P[11]);cb.cx(u[0],v[0])
    def erase_poly(target,linear,edges,constant=False):
     m=cf.retire(cb,target)
     if constant:cb.cx(m,km.xbool(True))
     cb.push_condition(m)
     for z in linear:cb.z(z)
     for a,b in edges:cb.cz(a,b)
     cb.pop_condition();cb.free(m)
    erase_poly(u[13],[v[11]],[(v[10],u[12])])
    erase_poly(u[12],[v[9],v[10],u[11]],[(v[9],v[11]),(v[9],u[11]),(v[11],u[11])],True)
    for i in reversed(range(3,12)):
     erase_poly(u[i],[v[i-3],v[i-2],v[i],u[i-1]],[(v[i-3],v[i-1]),(v[i-3],u[i-1]),(v[i-1],u[i-1])])
    erase_poly(u[2],[v[0],v[2],P[13],u[1]],[(v[1],P[13]),(v[1],u[1]),(P[13],u[1])])
    erase_poly(u[1],[v[1],P[13]],[(v[0],P[11]),(v[0],P[12]),(P[11],P[12])],True)
    erase_poly(u[0],[v[0],P[11],P[12]],[])


    return v,P
