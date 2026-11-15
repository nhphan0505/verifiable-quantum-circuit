"""Arithmetic inversion and symbolic HMR-debt checks; never invokes grading."""
from pathlib import Path
from types import SimpleNamespace
import json
import random
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from arithmetic_helpers import load_math
from cleanup import cleanup,bits
from finishing import remap_pending
from lookup_certificate import emit
from recovery_model import INTERCEPT,SLOPE,divider_forward,divider_inverse

FULL = (1<<64)-1

class SymbolicBasis:
    """All 64 codewords and independent symbolic phases for every outcome.

    Data gates never depend on outcomes in the Boolean cleanup. Thus each
    outcome's phase coefficient can be checked separately, proving all
    combinations of those outcomes without enumerating 2**55 branches.
    """
    def __init__(self):
        self.values={}
        self.phases={}
        self.live=set()
        self.stack=[]
        self.qnext=self.bnext=0

    def alloc_qubits(self,n):
        output=[]
        for _ in range(n):
            q=('q',self.qnext);self.qnext+=1
            self.values[q]=0;self.live.add(q);output.append(q)
        return output

    def alloc_bits(self,n):
        output=[]
        for _ in range(n):
            b=('b',self.bnext);self.bnext+=1
            self.phases[b]=0;self.live.add(b);output.append(b)
        return output

    def free(self,wire):
        if wire[0]=='q':
            assert self.values[wire]==0,('dirty quantum release',wire)
        else:
            assert self.phases[wire]==0,('unpaid independent outcome',wire,hex(self.phases[wire]))
        self.live.remove(wire)

    def x(self,q): self.values[q]^=FULL
    def cx(self,a,b): self.values[b]^=self.values[a]
    def ccx(self,a,b,t): self.values[t]^=self.values[a]&self.values[b]

    def hmr(self,q,m):
        self.phases[m]^=self.values[q]
        self.values[q]=0

    def push_condition(self,m):
        assert not self.stack
        self.stack.append(m)

    def pop_condition(self): self.stack.pop()

    def z(self,q):
        if q[0]=='b':
            assert not self.stack
            self.phases[q]^=FULL
        else:
            assert len(self.stack)==1
            self.phases[self.stack[-1]]^=self.values[q]

    def cz(self,a,b):
        assert len(self.stack)==1
        self.phases[self.stack[-1]]^=self.values[a]&self.values[b]

def lookup_debt_truths():
    certificates=json.loads((HERE/'data/lookup64_certificates.json').read_text())['loaders']
    raw=bits(range(64),6)
    result=[]
    class Lookup:
        def __init__(self,which):
            address=raw.copy()
            if which=='second':address[5]^=address[0]^address[1]^address[2]^((address[0]^address[2])&address[4])
            self.values=address+[0]*(20 if which=='first' else 15)
        def x(self,q):self.values[q]^=FULL
        def cx(self,a,b):self.values[b]^=self.values[a]
        def ccx(self,a,b,t):self.values[t]^=self.values[a]&self.values[b]
        def hmr(self,q,m):result.append(self.values[q]);self.values[q]=0
    for which in ('first','second'):
        certificate=certificates[which];builder=Lookup(which)
        outcomes=range(sum(s['kind']=='erase_coordinate' for s in certificate['steps']))
        emit(builder,certificate,list(range(certificate['wire_count'])),outcomes)
        if which=='first':result.extend(bits([s>>1 for s in SLOPE],6)[:4])
    result.append(bits([s>>1 for s in SLOPE],6)[3])
    assert len(result)==30
    return result

class RecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source,ctx=load_math()
        cls.context=SimpleNamespace(tables=SimpleNamespace(cb=ctx.codebook))

    def test_cleanup_all_codewords_all_independent_outcomes(self):
        builder=SymbolicBasis()
        owners=builder.alloc_qubits(18)
        address=bits(range(64),6)
        r=address[5]^address[0]^address[1]^address[2]^((address[0]^address[2])&address[4])
        initial=bits(INTERCEPT,13)+bits([s>>1 for s in SLOPE],6)[:4]+[r]
        for q,t in zip(owners,initial):builder.values[q]=t
        pending=[]
        for truth in lookup_debt_truths():
            outcome=builder.alloc_bits(1)[0];builder.phases[outcome]=truth
            pending.append((outcome,truth))
        output=cleanup(self.context,builder,owners[:13],owners[13:17],owners[17],pending)
        self.assertEqual([builder.values[q] for q in output],address)
        self.assertEqual(builder.live,set(output))
        self.assertFalse(pending)
        self.assertTrue(all(value==0 for value in builder.phases.values()))
        self.assertEqual(builder.bnext,55)

    def test_balanced_divider_inverse_at_bit_boundaries(self):
        for v in (0,1,2,63,64,2047,2048,4094,4095):
            for p in (0,1,4095,4096,8191,8192,16383,16384,32766,32767):
                u,history=divider_forward(v,p)
                self.assertEqual(divider_inverse(v,u,history),p,(v,p))

    def test_balanced_divider_inverse_random_operands(self):
        rng=random.Random(660067)
        for _ in range(2048):
            v,p=rng.randrange(4096),rng.randrange(32768)
            u,history=divider_forward(v,p)
            self.assertEqual(divider_inverse(v,u,history),p)

    def test_interleaved_hold_coordinates(self):
        # A rewrite on [5,12] crosses a pending chain [1,9]. The hop is
        # inserted before pending gate 9 and must move that gate as well.
        self.assertEqual(remap_pending([[1,9],[13]],[5,12],[(9,'old','new')]),[[1,12],[18]])

    def test_disjoint_hold_coordinates(self):
        self.assertEqual(remap_pending([[1,3],[15,18]],[6,10],[]),[[1,3],[18,21]])

    def test_replacement_and_insertion_boundaries(self):
        self.assertEqual(remap_pending([[4,7,8,11]],[5,10],[(8,'old','new')]),[[4,8,11,16]])

if __name__=='__main__':unittest.main()
