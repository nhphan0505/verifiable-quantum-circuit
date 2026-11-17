"""Return interpolation/product arithmetic and repay all lookup phases.

Original circuit builder: Syed Asad Ali (NOTICE.txt). Forward and return
interpolation have separate carry measurements, merged by their mathematical
carry positions. The measured high coefficient bit acts as a phase target,
so low-byte inverse arithmetic preserves its reconstructed original owner.
The final 64-codeword quadratic charts check every phase before debt release.
"""
from pathlib import Path
import json
from functools import reduce
from types import SimpleNamespace
import kickmix as km
import coefficient as cf
from lookup import load,emit,truth_bits
HERE=Path(__file__).resolve().parent


def inverse(cb,ar,book,token,product,first,first_pending):
    from divider_inverse import inverse as inverse_divider
    v,P=inverse_divider(cb,ar,book,token)
    flags=token.flags
    D,H,codes,pending,_=load(cb,v[6:],'second')
    cleanup_data=json.loads((HERE/'data/cleanup_codes.json').read_text())
    def erase_poly(target,linear,edges,constant=False):
        m=cf.retire(cb,target)
        if constant:cb.cx(m,km.xbool(True))
        cb.push_condition(m)
        for z in linear:cb.z(z)
        for a,b in edges:cb.cz(a,b)
        cb.pop_condition();cb.free(m)
    cb.push_condition(first.saved_outcome);cb.z(D[7]);cb.pop_condition();cb.free(first.saved_outcome)
    high=cb.alloc_qubits(1)[0];bridge,old_a11=codes
    for z in (D[7],D[8],D[9],H[2],H[4]):cb.cx(z,high)
    fr=(D[8],D[9],old_a11,H[2])
    for z in fr:cb.cx(z,D[7])
    cb.cx(H[4],bridge);cb.ccx(D[7],bridge,high);cb.cx(H[4],bridge)
    for z in reversed(fr):cb.cx(z,D[7])
    cb.cx(high,D[12]);cb.ccx(old_a11,high,D[12]);m_a10=cf.retire(cb,bridge);m_a11=cf.retire(cb,old_a11);saved=cb.alloc_qubits(1)[0];cb.cx(D[7],saved);Sbits=H+[high,D[12]];second_rows=[]
    for i in range(6):
     k=5-i;c=cf.carry(cb,Sbits,v[i],k)
     for z in D[:8]:cb.cx(v[i],z)
     second_rows.append(cf.disposable(ar,cb,Sbits[k+1:],D[:8],c,lambda z,i=i,k=k:cf.clear(cb,Sbits,v[i],k,z)))
     for z in D[:8]:cb.cx(v[i],z)
    D[10]=cb.alloc_qubits(1)[0]
    for z in (D[8],D[9],H[2],H[3],H[4],D[12],saved):cb.cx(z,D[10])
    left=(D[9],H[2],H[4],high,D[12],saved);right=(H[4],high)
    for z in left:cb.cx(z,D[8])
    for z in right:cb.cx(z,H[3])
    cb.ccx(D[8],H[3],D[10])
    for z in reversed(right):cb.cx(z,H[3])
    for z in reversed(left):cb.cx(z,D[8])
    cb.cx(H[0],D[9]);cb.ccx(D[9],D[12],D[10]);cb.cx(H[0],D[9])
    D[11]=cb.alloc_qubits(1)[0];cb.x(D[11]);cb.cx(high,D[11]);cb.cx(D[12],D[11]);cb.cx(D[12],D[10]);cb.cx(D[12],high);cb.ccx(D[10],high,D[11]);cb.cx(D[12],high);cb.cx(D[12],D[10])
    for m,z in ((m_a10,D[10]),(m_a11,D[11])):cb.push_condition(m);cb.z(z);cb.pop_condition();cb.free(m)
    cb.cx(high,D[12]);cb.ccx(D[11],high,D[12]);m_s5=cf.retire(cb,high);m_s4=cf.retire(cb,H[4]);sign=v[5];cb.cx(sign,saved);cb.cx(sign,D[7]);cb.x(D[7]);c=cb.alloc_qubits(1)[0];cb.ccx(saved,D[7],c)
    for z in D[8:]:cb.cx(sign,z)
    def erase(c):cb.del_and(saved,D[7],c);cb.free(c)
    second_overflow=cf.disposable(ar,cb,[],D[8:],c,erase)
    for z in D[8:]:cb.cx(sign,z)
    cb.x(D[7]);cb.cx(sign,D[7]);cb.cx(sign,saved)
    for m,z in zip(token.coefficient_outcomes,D):cb.push_condition(m);cb.z(z);cb.pop_condition();cb.free(m)
    for old,new in zip(first.rows+[first.overflow],second_rows+[second_overflow]):
     for position,m in list(old.measurements.items()):
      if position in new.measurements:cb.cx(m,new.measurements[position]);cb.free(m)
      else:new.measurements[position]=m
     old.measurements.clear();old.consumed=True

    highword=cb.alloc_qubits(1)[0];cb.cx(P[13],highword);cb.x(highword);word=P+[highword];m_s3=cf.retire(cb,H[3]);root_outcomes={}
    for i in (0,1,3):root_outcomes[i]=cf.retire(cb,v[i]);v[i]=None
    C=[False]+D;dirty=[z for z in v[:6] if z is not None]+flags+H[:3]+[saved];cb.x(word[14])
    def product_carry(sign,i):
     shift=9-i;parity=C[9]
     if shift<0:
      cb.cx(parity,sign);cb.x(sign);return sign
     if not shift:return False
     upper,lower=C[shift],C[shift-1];z=cb.alloc_qubits(1)[0]
     if lower is False:
      cb.cx(parity,sign);cb.ccx(upper,sign,z);cb.cx(parity,sign)
     else:
      cb.cx(upper,lower);cb.cx(parity,sign);cb.x(sign);cb.ccx(lower,sign,z);cb.x(sign);cb.cx(parity,sign);cb.cx(upper,lower);cb.cx(upper,z)
     return z

    def clear_product(sign,i,z):
     shift=9-i;parity=C[9]
     if shift<0:
      cb.x(sign);cb.cx(parity,sign);return
     if not shift:return
     upper,lower=C[shift],C[shift-1]
     if lower is False:
      cb.cx(parity,sign);cb.del_and(upper,sign,z);cb.cx(parity,sign)
     else:
      cb.cx(upper,z);cb.cx(upper,lower);cb.cx(parity,sign);cb.x(sign);cb.del_and(lower,sign,z);cb.x(sign);cb.cx(parity,sign);cb.cx(upper,lower)
     cb.free(z)

    for i in reversed(range(10)):
     sign=word[5+i];target=word[:5+i];source=C[10-i:]
     for z in target:cb.cx(sign,z)
     c=product_carry(sign,i)
     erase=lambda value,i=i,sign=sign:clear_product(sign,i,value)
     regenerate=lambda i=i,sign=sign:product_carry(sign,i)
     debt=product.product_rows[i]
     released=ar.inverse_add(cb,source,target,debt,carry_in=c,dirty_wires=dirty+word[5:],carry_lifecycle=(erase,regenerate) if i<9 else None)
     if not released:clear_product(sign,i,c)
     for z in target:cb.cx(sign,z)
    cb.x(word[14])

    seed0=cb.alloc_qubits(1)[0];cb.x(seed0);cb.cx(D[11],seed0);cb.cx(D[8],seed0);seed=[seed0]+word[:5]
    native_ccx=cb.ccx
    def seed_ccx(a,b,target):
     if cb.erase_seed_top and {a,b}=={D[11],seed[0]}:
      for z in (D[11],seed[0],D[12],seed[1]):cb.cx(z,target)
     elif cb.erase_seed_top and target==seed[2] and {a,b}=={D[12],seed[1]}:
      for z in (D[11],seed[0],D[10]):cb.cx(z,target)
      cb.hmr(target,km.b(366));cb.ccz(km.b(366),a,b)
      for z in (D[11],seed[0],D[10]):cb.cx(z,target)
     else:native_ccx(a,b,target)
    cb.ccx=seed_ccx
    for j in reversed(range(3)):
     cb.erase_seed_top=(j==0);ar.inverse_signed_row(cb,D,seed[:3+j],product.seed_rows[j],shift=-(11-j),sign=seed[3+j])
    cb.ccx=native_ccx
    cb.x(km.array(seed[:3]));cb.free(km.array(seed[:3]))
    for j,i in enumerate((0,1,3)):cb.x(seed[3+j]);v[i]=seed[3+j]
    cb.cx(v[1],v[0]);cb.ccx(v[0],v[1],v[3]);cb.cx(v[2],v[3]);cb.cx(v[2],v[1]);cb.cx(v[2],v[0])
    for i in (0,1,3):m=root_outcomes[i];cb.push_condition(m);cb.z(v[i]);cb.pop_condition();cb.free(m)

    a,b,c,d,e,f,g=D[8],D[9],D[10],D[11],D[12],H[0],H[1]
    def fact(target,left,right):
     a,ls=left;b,rs=right
     for z in ls:cb.cx(z,a)
     for z in rs:cb.cx(z,b)
     cb.ccx(a,b,target)
     for z in reversed(rs):cb.cx(z,b)
     for z in reversed(ls):cb.cx(z,a)
    def xor(target,terms,constant=False):
     if constant:cb.x(target)
     for z in terms:cb.cx(z,target)
    h0,h1,h2,h3=list(cb.alloc_qubits(4))
    fact(h0,(a,(d,e,f,g)),(c,(d,e)))
    fact(h1,(a,(g,)),(c,(e,g)))
    fact(h2,(a,(c,e,g)),(d,(e,f)))
    fact(h3,(b,(e,)),(d,(e,)))
    s3=cb.alloc_qubits(1)[0];xor(s3,(a,b,c,g,h0,h1),True)
    xor(h2,(a,b,g,h0,h3),True)
    # Constant follows the linear terms.
    for z in (c,d,f,g,H[2]):cb.cx(z,a)
    cb.x(a);cb.ccx(a,h2,s3);cb.x(a)
    for z in reversed((c,d,f,g,H[2])):cb.cx(z,a)
    xor(h2,(a,b,g,h0,h3),True)
    erase_poly(h0,[d,e],[(a,c),(a,d),(a,e),(c,d),(c,e),(c,f),(c,g),(d,f),(d,g),(e,f),(e,g)])
    erase_poly(h2,[e],[(a,d),(a,e),(a,f),(c,d),(c,e),(c,f),(d,e),(d,g),(e,f),(e,g),(f,g)])
    s4=cb.alloc_qubits(1)[0];xor(s4,(h1,h3),True);fact(s4,(b,(d,e,s3)),(c,(e,h1,s3)))
    erase_poly(h1,[g],[(a,c),(a,e),(a,g),(c,g),(e,g)])
    s5=h3;xor(s5,(d,e),True);fact(s5,(b,(d,e,s4)),(c,(s4,)))
    for m,z in ((m_s3,s3),(m_s4,s4)):cb.push_condition(m);cb.z(z);cb.pop_condition();cb.free(m)
    H=H[:3]+[s3,s4,s5]
    # Undo the bounded high carry while its saved low boundary is still live.
    sign=v[5];cb.cx(sign,saved);cb.cx(sign,D[7]);cb.x(D[7]);carry=cb.alloc_qubits(1)[0];cb.ccx(saved,D[7],carry)
    for z in D[8:]:cb.cx(sign,z)
    ar.inverse_add(cb,[],D[8:],second_overflow,carry_in=carry)
    for z in D[8:]:cb.cx(sign,z)
    cb.del_and(saved,D[7],carry);cb.free(carry);cb.x(D[7]);cb.cx(sign,D[7]);cb.cx(sign,saved)
    cb.cx(s5,D[12]);cb.ccx(D[11],s5,D[12]);erase_poly(D[11],[s5],[(D[10],s5),(D[10],D[12]),(s5,D[12])],True);D[11]=None
    saved_m=cf.retire(cb,D[7]);D[7]=cb.alloc_qubits(1)[0];cb.cx(saved,D[7]);cb.cx(D[7],saved);cb.free(saved)
    Sbits=H+[D[12]]
    original_x,original_cx,original_ccx=cb.x,cb.cx,cb.ccx
    high_target=D[7]
    def phase_x(q):
     if q==high_target:return
     if not isinstance(q,km.q):return original_x(km.array([q[i] for i in range(len(q)) if q[i]!=high_target]))
     return original_x(q)
    def phase_cx(a,b):
     if b==high_target:return
     return original_cx(a,b)
    def phase_ccx(a,b,t):
     if t==high_target:
      cb.push_condition(saved_m);cb.cz(b,a);cb.pop_condition();return
     return original_ccx(a,b,t)
    slope_retired=[]
    cb.x,cb.cx,cb.ccx=phase_x,phase_cx,phase_ccx
    def coefficient_inverse(source,target,debt,incoming,clean):
     a,b,preserve=ar._inputs(source,target,incoming,False)
     sizes,_=ar._terminal_partition(a,b,incoming,clean,(),ordinary_final=True,allow_dirty_terminal=False)
     cb.x(km.array(b));boundaries=[];start=0;carry=incoming
     for number,length in enumerate(sizes):
      aa,bb=a[start:start+length],b[start:start+length];retain=number+1<len(sizes)
      outgoing=ar._segment_repay(cb,aa,bb,carry,retain_outgoing=retain,preserve=None,start=start,debt=debt)
      if retain:boundaries.append((aa,bb,carry,outgoing))
      carry=outgoing;start+=length
     for aa,bb,inc,outgoing in reversed(boundaries):
      m=cf.retire(cb,outgoing);cb.push_condition(m);ar._phase_borrow(cb,aa,bb,inc,preserve=None);cb.pop_condition();cb.free(m)
     cb.x(km.array(b));assert not debt.measurements;debt.consumed=True
    for i in reversed(range(6)):
     k=5-i;c=cf.carry(cb,Sbits,v[i],k)
     for z in D[:8]:cb.cx(v[i],z)
     coefficient_inverse(Sbits[k+1:],D[:8],second_rows[i],c,5 if i>=4 else 6)
     for z in D[:8]:cb.cx(v[i],z)
     cf.clear(cb,Sbits,v[i],k,c)
     if i in (4,3):
      slope_retired.append(cf.retire(cb,H[4-i]))
    cb.x,cb.cx,cb.ccx=original_x,original_cx,original_ccx
    cb.push_condition(saved_m);cb.z(D[7]);cb.pop_condition();cb.free(saved_m)


    D[11]=cb.alloc_qubits(1)[0];xor(D[11],(H[5],D[12]),True);fact(D[11],(D[10],(D[12],)),(H[5],(D[12],)))
    cb.cx(H[5],D[12]);cb.ccx(D[11],H[5],D[12]);last_s5=cf.retire(cb,H[5]);
    fresh=list(cb.alloc_qubits(7));owners=D+H[2:5]+fresh
    bits=lambda xs,n:[sum((x>>i&1)<<a for a,x in enumerate(xs)) for i in range(n)]
    functions=bits(cf.INTERCEPT,13)+bits(cf.SLOPE,7)[2:5]+[0]*7
    emit(cb,cleanup_data['decoder'],owners,functions)
    raw=[owners[i] for i in (19,18,20,22,21,16)]
    assert [functions[owners.index(z)] for z in raw]==truth_bits()
    chart=raw+D+H[2:5];values=dict(zip(owners,functions));pending_second=pending[:]
    slope_truth=bits(cf.SLOPE,7)
    debts=first_pending+[(first.coded_high_outcome,truth_bits()[4])]+list(zip(first.slope_outcomes,[slope_truth[5]]+slope_truth[:5]))+pending_second+[(m_s5,slope_truth[5]),(slope_retired[0],slope_truth[0]),(slope_retired[1],slope_truth[1]),(last_s5,slope_truth[5])]
    books={}
    def pay(m,truth,cols):
     fs=tuple(values[z] for z in cols)
     if fs not in books:books[fs]=book.Codebook(fs,64)
     bk=books[fs];ex=bk.span.solve(truth);assert ex is not None
     plan=bk.decode_expression(ex);assert plan.evaluate_functions(fs,(1<<64)-1)==truth
     book.emit_phase(cb,cols,m,plan);cb.free(m)
    for m,t in debts:pay(m,t,chart)
    emit(cb,cleanup_data['basis'],owners,functions);values=dict(zip(owners,functions))
    order=[17,12,14,13,15,4,11,8,9,7,6,5,10,1,2,3,0];remaining=[owners[i] for i in reversed(order)]
    for index in order[:-2]:
     z=owners[index];remaining.remove(z);m=cf.retire(cb,z);pay(m,values[z],raw+remaining)

    zA,zB=owners[0],owners[3];mA=cb.alloc_bits(1)[0];cb.hmr(zA,mA);mB=cb.alloc_bits(1)[0];cb.hmr(zB,mB)
    # The measured owners are re-used by the conditioned helper charts.
    workers=[zB,zA]+list(cb.alloc_qubits(2));tailw=raw+workers;rawtruth=[values[z] for z in raw]
    def enter(ca,cbv):
     if not ca:cb.x(mA)
     cb.push_condition(mA)
     if not cbv:cb.x(mB)
     cb.push_condition(mB)
    def leave():
     cb.pop_condition()
     if not cbv:cb.x(mB)
     cb.pop_condition()
     if not ca:cb.x(mA)
    for ca,cbv in ((1,0),(0,1),(1,1)):
     key=f'{ca}{cbv}';cert=cleanup_data[key];fs=rawtruth+[0]*4
     enter(ca,cbv);emit(cb,cert,tailw,fs)
     helper_count=4 if key=='01' else 3
     functions_chart=fs[:6+helper_count];bk=book.Codebook(functions_chart,64);truth=(values[zA] if ca else 0)^(values[zB] if cbv else 0);ex=bk.span.solve(truth);assert ex is not None
     plan=SimpleNamespace(**cert["phase"])
     assert plan.constant*((1<<64)-1)^reduce(int.__xor__,[functions_chart[i] for i in range(plan.width) if plan.linear>>i&1]+[functions_chart[i]&functions_chart[j] for i,j in plan.edges],0)==truth
     if plan.constant:cb.z(True)
     for bit in range(plan.width):
      if plan.linear>>bit&1:cb.z(tailw[bit])
     for i,j in plan.edges:cb.cz(tailw[i],tailw[j])
     leave()
     for i in reversed(range(helper_count)):
      m=cb.alloc_bits(1)[0];cb.hmr(workers[i],m);enter(ca,cbv)
      bk=book.Codebook(rawtruth,64);ex=bk.span.solve(fs[6+i]);assert ex is not None
      book.emit_phase(cb,raw,m,bk.decode_expression(ex));leave();cb.free(m)
    cb.free(mA);cb.free(mB)
    for z in reversed(workers):cb.free(z)

    return word[5:]+v[:6]+raw
