"""Retain the reverse chart, close its ledger, HMR a linear direct gauge."""
import frozen_chart as frozen
from frozen_chart import *
from core90 import affine_inverse_g_character
from exact_subs import terminal_two_phase
import core90 as core
import exact_subs as xsub
import inspect

_source=inspect.getsource(frozen.normalize)
_source=_source.replace('def normalize(b,N,D,L):','def normalize_retained(b,N,D,L):')
_start=_source.index(' rm=b.alloc_bits(12);gg=')
_source=_source[:_start]+''' return dict(g=gm,i=im,h=hm,t=tm),F
'''
exec(compile(_source,__file__,'exec'))

_source2=_source.replace('def normalize_retained','def normalize_early')
_lo=_source2.index(' tm=inverse_stream_noscratch')
_hi=_source2.index(' b.x(r[0]);b.cx(F,r[0])',_lo)
_source2=_source2[:_lo]+_source2[_hi:]
_source2=_source2.replace('return dict(g=gm,i=im,h=hm,t=tm),F','return dict(g=gm,i=im,h=hm,half=half_masks),F')
exec(compile(_source2,__file__,'exec'))

def linear_inverse_character(b,g,constant,terms):
 to,frm,kval=ar.tower(12);ar.linear_inplace(b,g,to)
 D=b.alloc_qubits(6);core.norm_xor_noscratch(b,g,D,kval)
 saved=core.norm_cache.keep(b,D)
 dm=inverse_stream_noscratch(b,D);ar._phase_norm(b,g,dm,kval);b.free(dm)
 f=ar.field(12);b.cx(g[6:],g[:6])
 source=[q for x,m in terms for q in x]
 for seg in (0,1):
  x=g[:6]if seg==0 else g[6:]
  for sm,vv in ar.tensor(6):
   h=ar.apply(frm,vv<<(6*seg));co=b.alloc_bits(len(source));offset=b.alloc_bits(1)[0]
   b.bit_store(co,False);b.bit_store(offset,False)
   for j in ar.bits(h):b.cx(constant[j],offset)
   for off,(xx,mm)in enumerate(terms):
    for i in range(12):
     for j in ar.bits(f.mul(1<<i,h)):b.cx(mm[j],co[off*12+i])
   ix=list(ar.bits(sm));p=ix[0]
   for i in ix[1:]:b.cx(x[i],x[p]);b.cx(D[i],D[p])
   b.ccz(x[p],D[p],offset);core.phase_classical_parity(b,x[p],D[p],source,co)
   for i in reversed(ix[1:]):b.cx(D[i],D[p]);b.cx(x[i],x[p])
   b.free(offset);b.free(co)
 b.cx(g[6:],g[:6]);im=b.alloc_bits(6);b.hmr(D,im);b.free(D)
 D=core.norm_cache.rebuild(b,g,saved,kval)
 core.phase_inverse6_9(b,D,im);b.free(im);ar._erase_norm(b,g,D,kval);b.free(D);ar.linear_inplace(b,g,frm)

@lru_cache(None)
def merged_chart_columns():
 f=ar.field(12)
 cols=[(f.square(1<<i)^(1<<i))|((1 if i==0 else 0)<<12)for i in range(12)]+[K^1]
 return tuple(cols),tuple(ar.inverse_columns(cols))

def merged_chart(b,r,F,reverse=False):
 cols,back=merged_chart_columns();w=list(r)+[F]
 if not reverse:
  ar.linear_inplace(b,w,cols)
  for i in ar.bits(K):b.x(r[i])
 else:
  for i in ar.bits(K):b.x(r[i])
  ar.linear_inplace(b,w,back)

def direct_chart(b,D,F,forward,reverse,N=None,L=None):
 r,g=D[:12],D[12:]
 b.cz(F,forward['f'][0]);b.free(forward['f'])
 # r_reverse=r_forward+1-F, g_reverse*q_reverse=1/g_forward.
 b.x(r[0]);b.cx(F,r[0])
 masks=dict(g=forward['g'] if N is not None else add_masks(b,forward['g'],reverse['t']),
            i=add_masks(b,forward['i'],reverse['h']),
            h=add_masks(b,forward['h'],reverse['i']),
            t=add_masks(b,forward['t'],reverse['g']),r=forward['r'])
 if N is None:
  b.cz(g,masks['i']);b.free(masks['i'])
  im=inverse_stream_noscratch(b,g)
  phase_inverse36_pivot(b,g,im);b.free(im)
 else:
  ref.external_square24(b,L,True)
  linear_inverse_character(b,g,masks['i'],[(N[12:],reverse['half'][0]),(L[12:],reverse['half'][1])])
  ref.external_square24(b,L)
  b.free(masks['i'])
  for m in reverse['half']:b.free(m)
 b.cz(g,masks['g']);b.free(masks['g'])
 b.cz(r,masks['r']);b.free(masks['r'])
 # Include F in the invertible rank13 chart: no extra kernel bit.
 merged_chart(b,r,F)
 gm=scale_defer(b,g,r)
 b.cz(g,masks['h']);b.free(masks['h'])
 phase_inverse36_pivot(b,g,masks['t']);b.free(masks['t'])
 merged_chart(b,r,F,True)
 rm=b.alloc_bits(12);hm=b.alloc_bits(12);fm=b.alloc_bits(1)
 b.hmr(r,rm);b.hmr(g,hm);b.hmr(F,fm[0]);b.free(D);b.free(F)
 return dict(g=gm,r=rm,h=hm,f=fm)

def zero_affine_character(b,g,A,gm,fm):
 # [g=0] * (fm XOR dot(A,gm)), 11T/12fresh, exact at g=0.
 C=b.alloc_qubits(1)[0];b.cx(fm,C)
 for a,m in zip(A,gm):b.ccx(a,m,C)
 b.x(g);ladder=b.alloc_qubits(len(g)-1)
 b.init_and(g[0],g[1],ladder[0])
 for j in range(1,len(ladder)):b.init_and(ladder[j-1],g[j+1],ladder[j])
 b.cz(ladder[-1],C)
 for j in reversed(range(len(ladder))):
  if j:b.del_and(ladder[j-1],g[j+1],ladder[j])
  else:b.del_and(g[0],g[1],ladder[0])
 b.free(ladder);b.x(g)
 for a,m in zip(A,gm):b.ccx(a,m,C)
 b.cx(fm,C);b.free(C)

def full_core_phase(b,N,heads,params,ct,masks,pole,dirty):
 D=b.alloc_qubits(24);b.x(D[0])
 for i,(head,(q,c))in enumerate(zip(heads,params)):
  ref.external_scalar_step(b,head,N,D,q,ct,first=i==0)
 b.cswap(pole,N,D)
 A,g=D[:12],D[12:]
 zero_affine_character(b,g,A,masks['g'],masks['f'][0])
 zero=b.alloc_bits(12);b.bit_store(zero,False)
 masks['i']=zero
 # Unswapped chart: inv(0)=0 and F implies g=0.
 b.cz(g,masks['g']);b.cz(A,masks['h'])
 f=ar.field(12)
 for j in range(12):
  for k in ar.bits(f.mul(K,1<<j)):b.cz(g[j],masks['h'][k])
 core.affine_inverse_g_character(b,A,g,masks)
 for m in masks.values():b.free(m)
 b.cswap(pole,N,D)
 fm=b.alloc_bits(1);b.hmr(pole,fm[0]);b.free(pole)
 b.push_condition(fm[0]);clean_zero_phase24(b,D);b.pop_condition();b.free(fm)
 from replay_erase import scalar_erase_second24
 for i in reversed(range(len(heads))):
  if i==1:scalar_erase_second24(b,heads[i],N,D,params[i][0],ct,params[0][0])
  else:ref.external_scalar_step(b,heads[i],N,D,params[i][0],ct,True,first=i==0)
 b.x(D[0]);b.free(D)

def terminal_one_phase(b,N,heads,params,ct,mask,pole,dirty):
 stop=len(heads)-1;D=b.alloc_qubits(24);b.x(D[0])
 for i in range(stop):ref.external_scalar_step(b,heads[i],N,D,params[i][0],ct,first=i==0)
 b.cz(N,mask);xsub.head_phase(b,heads[-1],D,mask,ct)
 scalepair(b,D,params[-1][0]);b.ccz(pole,D,mask);scalepair(b,D,inv(params[-1][0]))
 fm=b.alloc_bits(1);b.hmr(pole,fm[0]);b.free(pole)
 b.push_condition(fm[0])
 ref.external_scalar_step(b,heads[-1],N,D,params[-1][0],ct)
 clean_zero_phase24(b,D)
 ref.external_scalar_step(b,heads[-1],N,D,params[-1][0],ct,True)
 b.pop_condition();b.free(fm);b.free(mask)
 from replay_erase import scalar_erase_second24
 for i in reversed(range(stop)):
  if i==1:scalar_erase_second24(b,heads[i],N,D,params[i][0],ct,params[0][0])
  else:ref.external_scalar_step(b,heads[i],N,D,params[i][0],ct,True,first=i==0)
 b.x(D[0]);b.free(D)

def clean_zero_phase24_direct(b,x):
 # 22T/22scratch, only used after pole qubit is freed: peak <=886.
 b.x(x);nodes=b.alloc_qubits(len(x)-2)
 b.init_and(x[0],x[1],nodes[0])
 for j in range(1,len(nodes)):b.init_and(nodes[j-1],x[j+1],nodes[j])
 b.cz(nodes[-1],x[-1])
 for j in reversed(range(len(nodes))):
  if j:b.del_and(nodes[j-1],x[j+1],nodes[j])
  else:b.del_and(x[0],x[1],nodes[0])
 b.free(nodes);b.x(x)

def clean_zero_phase24_mixed(b,x):
 # Six AND3 + three AND2 flags. Produce15T, phase AND9 costs7T,
 # repair six AND3 flags at mean0.5T each; AND2 flags del_and freely.
 # Total25T; flag bank9 + phase ladder7 =16 clean scratch.
 b.x(x)
 groups=[x[j:j+3]for j in range(0,18,3)]+[x[j:j+2]for j in range(18,24,2)]
 flags=[frozen.and_flag(b,group)for group in groups]
 nodes=b.alloc_qubits(7);b.init_and(flags[0],flags[1],nodes[0])
 for j in range(1,7):b.init_and(nodes[j-1],flags[j+1],nodes[j])
 b.cz(nodes[-1],flags[-1])
 for j in reversed(range(1,7)):b.del_and(nodes[j-1],flags[j+1],nodes[j])
 b.del_and(flags[0],flags[1],nodes[0]);b.free(nodes)
 for group,F in zip(groups,flags):
  if len(group)==2:b.del_and(group[0],group[1],F);b.free(F)
  else:frozen.erase_and(b,group,F)
 b.x(x)

clean_zero_phase24=clean_zero_phase24_mixed

def zero_flag24_grouped(b,x):
 # Eight AND3 flags (16T), AND8 (7T), eight repairs (mean4T).
 # Peak15 scratch, no chart value changes.
 b.x(x);groups=[x[j:j+3]for j in range(0,24,3)]
 flags=[frozen.and_flag(b,group)for group in groups]
 F=frozen.and_flag(b,flags)
 for group,flag in zip(groups,flags):frozen.erase_and(b,group,flag)
 b.x(x);return F

from adaptive_zero import zero_flag24 as zero_flag24_grouped,clean_zero_phase24
forward_chain=frozen.clone(frozen.external_node_chain,dict(frozen.external_node_chain.__globals__,zero_flag24=zero_flag24_grouped))

def external_node_chain(b,words,gi,reverse=False,token=None,normalizer=None):
 if not reverse:return forward_chain(b,words,gi,False,token,normalizer)
 gn=ref.groups[gi];N=combine(words[gn['word']:gn['word']+2]);L=combine(words[gn['word']+2:gn['word']+4])
 heads=[words[2*i:2*i+2]for i in range(2*gi)]
 params=[];c=0
 for i in range(2*gi):
  q=ref.ks[i]^gn['kap'];params.append((q,c));c^=inv(q)
 assert c==0
 pole=token['pole'];D=b.alloc_qubits(24);b.x(D[0]);b.cswap(pole,N,D)
 for head,(q,c)in reversed(list(zip(heads,params))[1:]):ref.external_chain_step(b,head,N,D,L,q,gn['c'],c,True)
 q0=params[0][0];scalepair(b,N,inv(q0));b.swap(N,D);scalepair(b,L,inv(q0))
 with b.mark('retained_normalize'):norm,F=normalize_early(b,N,D,L)
 with b.mark('retained_direct'):mask=direct_chart(b,D,F,token['norm'],norm,N,L)
 a,h=heads[0];cx(b,h,a,gn['c']);b.cx(combine(heads[0]),N);cx(b,h,a,gn['c']);b.cx(h,L[:12])
 with b.mark('retained_terminal'):terminal_two_phase(b,N,heads,params,gn['c'],mask,pole,L)
