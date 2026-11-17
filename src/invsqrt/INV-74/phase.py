"""N27 reflected phase walk and reversible root metadata restoration.

Syed Asad Ali is the original builder (NOTICE.txt). Twenty-six sign features
and one constant form a 27-coordinate cyclic word. Five controlled reflections
have centres (2,6,25,0,26). The last two are streamed by holding differences;
two third-reflection pairs are retained only across their dependent visits.
Exact dyadic base/threshold angles are mathematical parameters, never floats.

Four root/remainder owners are temporarily retired, used as clean workspace,
then restored from a four-AND sign code. The supplied finishing outcome erases
the known AND at the constant-one restoration site. No reference circuit,
operation list or external data is read by this module.
"""
from fractions import Fraction
from contextlib import contextmanager
import kickmix as km
from coefficient import retire


def apply(cb,poly,cyclic,token,parameters,*,finishing_outcome):
    """Apply phase, return all borrowed owners and repay metadata measurements."""
    v,u,flags,history=token.v,token.u,token.flags,token.history
    # Reconstruct first saved sign and prepare the expanded N27 endpoint chart.
    h12=cb.alloc_qubits(1)[0]
    cb.cx(v[11],h12);cb.cx(v[10],h12);cb.ccx(v[10],history[13],h12)
    cb.cx(v[11],u[12]);cb.x(v[11]);cb.cx(u[11],u[13]);cb.x(u[13]);cb.ccx(u[13],v[11],u[12]);cb.x(u[13]);cb.cx(u[11],u[13]);cb.x(v[11])
    cb.cx(v[1],u[10]);cb.cx(v[0],u[9]);cb.cx(v[1],u[9])
    for z in u[:9]:cb.cx(v[0],z)
    cb.cx(v[1],u[9])
    m11=cb.alloc_bits(1)[0];cb.hmr(u[11],m11)
    m=cb.alloc_bits(1)[0];cb.hmr(v[11],m);cb.push_condition(m);cb.z(h12);cb.z(v[10]);cb.cz(v[10],history[13]);cb.pop_condition();cb.free(m)
    m10=cb.alloc_bits(1)[0];cb.hmr(v[10],m10)
    m9=cb.alloc_bits(1)[0];cb.hmr(v[9],m9)
    class Pool:
     def __init__(self):self.spare=[u[11],v[11],v[10],v[9]];self.lent=set(self.spare)
     def __getattr__(self,n):return getattr(cb,n)
     def alloc_qubits(self,n):
      if n==1 and self.spare:return [self.spare.pop()]
      return cb.alloc_qubits(n)
     def free(self,z):
      if z in self.lent:self.spare.append(z)
      else:cb.free(z)
    pool=Pool();signs={**history,12:h12,25:u[10],26:u[9],36:u[13],37:u[12]};signs.update({j:u[35-j] for j in range(27,36)})
    for z in signs.values():cb.x(z)
    one=pool.alloc_qubits(1)[0];cb.x(one);word=[signs[37-i] for i in range(26)]+[one]
    # Fixed dyadic parameters recovered separately from the artifact, not a gate tape.
    angles=parameters['base_half_turns'];betas=parameters['overflow_half_turns']+['0.25']
    centres=(2,6,25,0,26);controls=((0,4),(8,),(0,2,4,8),(0,1,2),(0,1))
    @contextmanager
    def ctl(stage):
     terms=controls[stage];bits=[i for i in range(4) if 1<<i in terms];a=flags[bits[0]]
     for i in bits[1:]:cb.cx(flags[i],a)
     if 0 in terms:cb.x(a)
     yield a
     if 0 in terms:cb.x(a)
     for i in reversed(bits[1:]):cb.cx(flags[i],a)
    def pairs(stage):return [(i,(centres[stage]-i)%27) for i in range(27) if i<(centres[stage]-i)%27]
    def cswap(stage,pr):
     with ctl(stage) as c:cb.cswap(c,word[pr[0]],word[pr[1]])
    def cswap_stage(stage,prs,undo_first=False):
     with ctl(stage) as c:
      for a,b in prs:
       if undo_first and (a,b)==(3,26):
        cb.cx(word[b],word[a]);cb.x(word[b]);cb.hmr(word[b],finishing_outcome);cb.ccz(finishing_outcome,c,word[a]);cb.x(word[b]);cb.cx(word[b],word[a])
       else:cb.cswap(c,word[a],word[b])
    def hold(stage,pr):
     a,b=[word[i] for i in pr];anc=pool.alloc_qubits(1)[0]
     with ctl(stage) as c:cb.cx(a,b);cb.ccx(c,b,anc);cb.cx(a,b)
     cb.cx(anc,a);cb.cx(anc,b);return anc
    def release(stage,pr,anc):
     a,b=[word[i] for i in pr];cb.cx(anc,a);cb.cx(anc,b);m=cb.alloc_bits(1)[0];cb.hmr(anc,m)
     with ctl(stage) as c:cb.push_condition(m);cb.cz(c,a);cb.cz(c,b);cb.pop_condition()
     cb.free(m);pool.free(anc)
    encfn={0:lambda f0,f1,f2,f3,p,s:(f1^f2^f3^p)&(s^f0)^f0,1:lambda f0,f1,f2,f3,p,s:(f1^f2^f3^p)&s,2:lambda f0,f1,f2,f3,p,s:f0&(f1^p)^(f2^f3)&s,3:lambda f0,f1,f2,f3,p,s:(f2^f3)&s,6:lambda f0,f1,f2,f3,p,s:f0&p^f3&s,7:lambda f0,f1,f2,f3,p,s:f3&s}
    def anf(fn):
     a=[fn(*[x>>i&1 for i in range(6)]) for x in range(64)]
     for i in range(6):
      for x in range(64):
       if x>>i&1:a[x]^=a[x^(1<<i)]
     return tuple(i for i in range(64) if a[i])
    enc={j:anf(f) for j,f in encfn.items()};p=None
    slots=[word[(j-5)%27] for j in range(27)]
    def feature(j):
     if j==8:return
     if j in enc:
      variables=flags+[p,slots[j]];terms=enc[j];h=pool.alloc_qubits(1)[0];poly.xor_polynomial(cb,variables,h,terms);cb.z_pow(h,Fraction(betas[j]));cyclic._erase_polynomial(pool,h,variables,terms)
     else:
      terms={4:(5,17,6,18,8,16),5:(6,8)}[j];h=pool.alloc_qubits(1)[0];poly.xor_polynomial(cb,flags+[p],h,terms)
      t=pool.alloc_qubits(1)[0];cb.ccx(h,slots[j],t);cb.z_pow(t,Fraction(betas[j]));cb.del_and(h,slots[j],t);pool.free(t);cyclic._erase_polynomial(pool,h,flags+[p],terms)
    def visit(pos):
     j=(pos+5)%27;cb.z_pow(word[pos],Fraction(angles[j]))
     if j<=8:feature(j)
    r2={(11,14):(0,2),(7,18):(3,6)};held2={};ehold=set(range(13))-{8,10,12};held={};e={k:(13-k,14+k) for k in range(13)};f={k:(12-k,14+k) for k in range(13)}
    def open2(k):
     for pr,(lo,hi) in r2.items():
      if lo==k:held2[pr]=hold(2,pr)
    def close2(k):
     for pr,(lo,hi) in r2.items():
      if hi==k:release(2,pr,held2.pop(pr))
    def ef(k):
     if k in ehold:held[k]=hold(3,e[k])
     else:cswap(3,e[k])
    def eu(k):
     if k in ehold:release(3,e[k],held.pop(k))
     else:cswap(3,e[k])
    late=[pr for pr in pairs(2) if pr not in r2]
    cswap_stage(0,pairs(0));cswap_stage(1,pairs(1));cswap_stage(2,late)
    open2(0);ef(0);visit(13)
    for k in range(13):
     if k==8:p=pool.alloc_qubits(1)[0];poly.xor_polynomial(cb,flags,p,(6,10))
     if k:open2(k)
     if k+1<=12:ef(k+1)
     a=hold(4,f[k]);visit(f[k][0]);visit(f[k][1]);release(4,f[k],a);eu(k);close2(k)
    cb.cz(flags[1],flags[3]);cswap_stage(2,late);cswap_stage(1,pairs(1));cswap_stage(0,pairs(0),undo_first=True)
    cyclic._erase_polynomial(pool,p,flags,(6,10));cb.x(one)
    for z in signs.values():cb.x(z)
    cb.cx(v[1],u[9])
    for z in u[:9]:cb.cx(v[0],z)
    
    # Decode v9 by a four-AND Boolean chart, borrowing the retired root owners.
    def pair_forms(SA,SB):
     SA=list(dict.fromkeys(SA));SB=list(dict.fromkeys(SB));a=SA[0];trace=[]
     for w in SA[1:]:cb.cx(w,a);trace.append((w,a))
     SBc=(set(SA)-{a})^(set(SB)-{a}) if a in SB else set(SB)
     if a in SB:SBc.add(a)
     choices=[w for w in SB if w in SBc and w!=a]+[w for w in SA if w in SBc and w!=a];b=choices[0]
     for w in [x for x in SB+SA+[a] if x in SBc and x!=b]:
      if (w,b) not in trace:cb.cx(w,b);trace.append((w,b))
     return a,b,trace
    
    def undo(trace):
     for a,b in reversed(trace):cb.cx(a,b)
    
    def product_form(SA,SB,target):
     a,b,trace=pair_forms(SA,SB);cb.ccx(a,b,target);undo(trace)
    def erase_form(target,SA,SB,free=False):
     m=cb.alloc_bits(1)[0];cb.hmr(target,m)
     if free:cb.free(target)
     a,b,trace=pair_forms(SA,SB);cb.push_condition(m);cb.cz(a,b);cb.pop_condition();undo(trace);cb.free(m)
    h13,h14,h15,h16=[history[j] for j in range(13,17)];v8=v[8];g0=v[11];g1=cb.alloc_qubits(1)[0];g2=v[10]
    forms=[([v8,h13,h14,h15,h16],[h12,v8,h13,h14,h16]),([h12,h14],[v8,h13,h15,g0]),([h12,h13,g1],[h14,h15,h16,g0]),([v8,h12,h14,h15,g1],[h16,v8,h14,h15,g1,g0,g2])]
    for z in (h12,h13,h15,h16):cb.cx(z,v[9])
    for i,target in enumerate((g0,g1,g2,v[9])):
     product_form(*forms[i],target)
     if i<3:cb.cx(target,v[9])
    erase_form(g2,*forms[2])
    cb.push_condition(m9);cb.z(v[9]);cb.pop_condition();cb.free(m9)
    cb.cx(v[9],v[10]);cb.cx(g1,v[10]);product_form([h13,g1],[v[9],h14],v[10])
    erase_form(g1,*forms[1],free=True);erase_form(g0,*forms[0])
    cb.push_condition(m10);cb.z(v[10]);cb.pop_condition();cb.free(m10)
    cb.cx(v[1],u[10]);cb.cx(v[0],u[9]);cb.cx(v[1],u[9])
    cb.cx(h12,v[11]);cb.cx(v[10],v[11]);cb.ccx(v[10],h13,v[11])
    for z in (history[24],v[11],v[0],v[1]):cb.cx(z,u[11])
    cb.cx(v[1],v[0]);cb.cx(u[9],u[10]);cb.ccx(v[0],u[10],u[11]);cb.cx(u[9],u[10]);cb.cx(v[1],v[0])
    cb.push_condition(m11);cb.z(u[11]);cb.pop_condition();cb.free(m11)
    cb.cx(v[11],u[12]);cb.x(v[11]);cb.cx(u[11],u[13]);cb.x(u[13]);cb.ccx(u[13],v[11],u[12]);cb.x(u[13]);cb.cx(u[11],u[13]);cb.x(v[11])
    m=retire(cb,h12);cb.push_condition(m);cb.z(v[11]);cb.z(v[10]);cb.cz(v[10],h13);cb.pop_condition();cb.free(m)
