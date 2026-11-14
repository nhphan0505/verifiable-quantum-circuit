"""Borrow a clean bit from complementary gap-supported words.

Only public frame dimensions and builder wire identities select the source.
No quantum values or simulator state are read by this installer.
"""
from pathlib import Path
import sys
from types import FunctionType
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'research/agents/a08'),str(ROOT/'research/agents/a01')]
import scalar_compact_v3 as scalar
p=scalar.p

def payload_middle(b,lo_f,lo_g,heads,out,q,F0,F1,F2,zero_word):
    s0,s1,s2=heads; q0,q1=q
    # F0=[q1=0] is an exact completed-frame identity.
    M=mask_word(b,s0,F0,F1,True,True)
    P0=b.alloc_qubits(12); ar.mul_xor0(b,q0,M,P0)
    b.cx(M,P0)
    copy_flag(b,F0,s0,P0,True); copy_flag(b,F1,s1,P0,True)
    P1=b.alloc_qubits(12); ar.mul_xor0(b,q1,s0,P1)
    b.cx(M,P1); copy_flag(b,F1,s0,P1,True)
    erase_mask(b,s0,M,F0,F1,True,True)
    Q2=b.alloc_qubits(12); b.cswap(F1,P1,Q2)
    convolution(b,lo_f,[P0,P1],out)
    r1=b.alloc_bits(12)
    b.hmr(P1,r1); b.free(P1)
    ar.phase_product(b,q1,s0,r1); b.cz(Q2,r1)
    b.x(F1); phase_classical_parity(b,F0,F1,s0,r1); b.x(F1)
    b.free(r1)
    # P0 becomes Q1; M_P+M_Q=(1+F0)*s0.
    M=b.alloc_qubits(12); b.x(F0)
    for bit,target in zip(s0,M):b.init_and(F0,bit,target)
    b.x(F0)
    ar.mul_xor0(b,q0,M,P0)
    mask=b.alloc_bits(12); b.hmr(M,mask); b.free(M)
    phase_flag(b,F0,s0,mask,True); b.free(mask)
    Q1=P0
    b.cx(s1,Q1); copy_flag(b,F1,s0,Q1)
    # F1*zero_word=0 and (1+F1)*Q2=0. The swap exposes clean Q2[0].
    M=b.alloc_qubits(12)
    b.cswap(F1,zero_word[0],Q2[0])
    b.x(F0);b.x(F1);b.init_and(F0,F1,Q2[0])
    for bit,target in zip(s0,M):b.ccx(Q2[0],bit,target)
    b.del_and(F0,F1,Q2[0]);b.x(F1);b.x(F0)
    b.cswap(F1,zero_word[0],Q2[0])
    b.cx(s2,M)
    b.cx(M,Q1); copy_flag(b,F2,s2,M); b.cx(M,Q1)
    convolution(b,lo_g,[M,Q1,Q2],out)
    r0=b.alloc_bits(12); r1=b.alloc_bits(12); r2=b.alloc_bits(12)
    b.hmr(M,r0); b.hmr(Q1,r1); b.hmr(Q2,r2)
    b.free(M); b.free(Q1); b.free(Q2)
    M=mask_word(b,s0,F0,F1,True,False)
    b.cz(M,r0); phase_flag(b,F0,s0,r0,True); phase_flag(b,F2,s2,r0,True)
    ar.phase_product(b,q0,M,r1); ar.phase_product(b,q1,M,r2); b.cz(M,r1)
    phase_flag(b,F1,s0,r1); phase_flag(b,F1,s1,r1); phase_flag(b,F2,s2,r1)
    b.free(r0); b.free(r1); b.free(r2)
    erase_mask(b,s0,M,F0,F1,True,False)

def install(cv):
    scope=scalar.scope_of(cv)
    short=dict(zip(cv.__code__.co_freevars,cv.__closure__))['core'].cell_contents.__globals__
    original=scope['look_solve'];frames=[]
    arithmetic=p.clone(payload_middle,scope)

    def solve(b,f,g,payloads,H=None,parent=None,reverse=False,phase=None):
        frames.append((f,g))
        try:return original(b,f,g,payloads,H,parent,reverse,phase)
        finally:frames.pop()

    def middle(b,lo_f,lo_g,heads,out,q,F0,F1,F2):
        # In both completed three-frame traversals lo_f is bottom f[:-2].
        # Enclosing frames retain the same physical coefficient bank prefix.
        candidates=[]
        for pair in frames:
            for bank in pair:
                if len(bank)>=len(lo_f)+2 and bank[:len(lo_f)]==lo_f:
                    candidates.append(bank[len(lo_f)+1])
        assert candidates and all(word==candidates[0] for word in candidates)
        return arithmetic(b,lo_f,lo_g,heads,out,q,F0,F1,F2,candidates[0])

    scope['look_solve']=solve;short['old'].look_solve=solve
    owners={};seen=set()
    def visit(value):
        if id(value) in seen:return
        seen.add(id(value))
        if isinstance(value,dict):
            if 'payload_middle' in value:owners[id(value)]=value
            for name in ('look_solve','direct_pre','direct_post','handed_aligned_pre','look_root_cached'):
                if name in value:visit(value[name])
        elif isinstance(value,FunctionType):
            visit(value.__globals__)
            for cell in value.__closure__ or ():
                try:child=cell.cell_contents
                except ValueError:continue
                if isinstance(child,(dict,FunctionType)):visit(child)
    visit(scope);visit(original);visit(short['look_root_cached'])
    for owner in owners.values():owner['payload_middle']=middle
    return cv
