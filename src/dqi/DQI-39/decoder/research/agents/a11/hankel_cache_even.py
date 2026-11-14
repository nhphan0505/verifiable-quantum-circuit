"""Exact one-word handoff from forward Hankel to its measured inverse.

The public plans impose an even root source count for cyclic top-dot sharing.  The only additional
live state through scan is one original GF4096 word from the final triple.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'research/agents/a09'),str(ROOT/'research/agents/a01')]
import hankel_compact as h
p,ar,k=h.p,h.ar,h.kernels

FORWARD={(34,True):18,(16,False):8,(8,False):4,(6,False):4,
         (16,True):9,(7,False):4,(7,True):5}
REVERSE_FIRST={34:18,18:10,10:6,6:3}


def install(cv):
    core=dict(zip(cv.__code__.co_freevars,cv.__closure__))['core'].cell_contents
    owner=core.__globals__['old']
    saved=[]

    def forward(b,q,x,first=True):
        n=len(x)
        if n in (2,3,4):
            if first:
                assert n==3 and not saved
                word=b.alloc_qubits(12);b.cx(x[-1],word);saved.append(word)
            if n==2:return ar.mul_xor0(b,q[0],x[0],x[1])
            return p.hankel_direct(b,q,x)
        sources=FORWARD[n,first];prefix=sources-2
        forward(b,q[:n-sources-1],x[sources:],False)
        copies=[b.alloc_qubits(12)for _ in range(2)]
        for source,target in zip(x[prefix:sources],copies):b.cx(source,target)
        old_sources=x[:prefix]+copies
        h.accumulate(b,h.flat(old_sources),h.flat(q[:n-1]),h.flat(x[prefix:]),
                     h.hybrid_tensor(n-1,sources,2))
        h.retire_descending(b,q,x,old_sources,copies,prefix)
        forward(b,q[:prefix-1],x[:prefix],first)

    def hankel(b,B,A,reverse=False):
        qfull=list(reversed(B[1:]))
        if not reverse:
            assert not saved
            forward(b,qfull,A)
            for i in range(len(A)//2):b.swap(A[i],A[-1-i])
            assert len(saved)==1
            return
        assert len(saved)==1
        cube=b.alloc_qubits(12);p.cube_xor(b,B[-1],cube)

        def solve(q,x,first=False):
            n=len(x)
            if n==1:return
            if first and n==3:
                solve(q[:1],x[:2])
                mask=b.alloc_bits(12);b.hmr(x[2],mask)
                word=saved.pop();b.swap(x[2],word);b.free(word)
                b.cz(x[2],mask)
                ar.phase_product(b,q[1],x[0],mask)
                ar.phase_product(b,q[0],x[1],mask)
                b.free(mask)
                return
            if first:
                left=REVERSE_FIRST[n]
            else:
                _,left=p.reverse_partition(n)
            if left is None:
                if n==4:b.cx(cube,q[2])
                ar.linear_xor(b,q[0],q[1],ar.square_columns(12))
                p.hankel_direct(b,q,x)
                ar.linear_xor(b,q[0],q[1],ar.square_columns(12))
                if n==4:b.cx(cube,q[2])
                return
            solve(q[:left-1],x[:left],first)
            for ac,bc,tc in reversed(k.cross_terms(left,n-left)):
                k.rank_update(b,x[:left],ac,q[:n-1],bc,x[left:],tc)
            solve(q[:n-left-1],x[left:])

        for i in range(len(A)//2):b.swap(A[i],A[-1-i])
        solve(qfull,A,True)
        assert not saved
        mask=b.alloc_bits(12);b.hmr(cube,mask);b.free(cube)
        p.cube_phase(b,B[-1],mask);b.free(mask)

    owner.hankel=hankel
    return cv
