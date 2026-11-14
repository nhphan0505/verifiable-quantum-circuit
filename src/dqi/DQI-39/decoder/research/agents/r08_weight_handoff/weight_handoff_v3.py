"""Share q1*s0 and retain P0 as the second-pass Q1 weight."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'research/agents/a01'), str(ROOT/'research/agents/a08')]
import ported as p
import scalar_compact_v3 as scalar


def payload_middle(b,lo_f,lo_g,heads,out,q,F0,F1,F2):
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
    # Twelve output wires also hold the conjunction while eleven bits form.
    # The last masked bit uses Q1[0] as restored arbitrary dirty workspace.
    M=b.alloc_qubits(12); b.x(F0); b.x(F1)
    b.init_and(F0,F1,M[0])
    for j in range(1,12):b.ccx(M[0],s0[j],M[j])
    b.del_and(F0,F1,M[0])
    b.ccx(F0,F1,Q1[0]); b.ccx(Q1[0],s0[0],M[0])
    b.ccx(F0,F1,Q1[0]); b.ccx(Q1[0],s0[0],M[0])
    b.x(F1); b.x(F0)
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


def install(decoder):
    cv=scalar.converter_of(decoder)
    core=dict(zip(cv.__code__.co_freevars,cv.__closure__))['core'].cell_contents
    scope=core.__globals__['old'].look_solve.__globals__
    assert 'payload_middle' in scope
    scope['payload_middle']=p.clone(payload_middle,scope)
    return decoder
