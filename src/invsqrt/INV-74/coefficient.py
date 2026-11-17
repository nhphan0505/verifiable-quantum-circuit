"""Rounded six-row interpolation and deferred overflow for INV-74.

Syed Asad Ali is the original builder of this circuit lineage (see NOTICE.txt).
The independently recovered tables below are mathematical coefficients, not a
serialized gate stream. Each row adds/subtracts one truncated slope word with
an adjacent rounding bit. Carries are X-measured and retained as typed debts.

The lookup supplies a coded high coefficient bit and a bridge coordinate;
these are measured before interpolation and reconstructed from the retained
quadratic chart. The sign of the last row and saved low-byte bit control the
single deferred overflow into the high five coefficient bits. All 4096 root
values match the observed 13-bit coefficient at operation boundary 3335.
"""
from dataclasses import dataclass
from types import SimpleNamespace
import sys
import kickmix as km

INTERCEPT = (8065, 7821, 7587, 7364, 7151, 6947, 6751, 6564, 6384, 6212, 6046, 5887, 5734, 5587, 5445, 5309, 5178, 5051, 4930, 4812, 4699, 4590, 4484, 4382, 4284, 4189, 4097, 4008, 3921, 3838, 3757, 3679, 3603, 3529, 3458, 3389, 3322, 3257, 3194, 3132, 3073, 3015, 2958, 2904, 2850, 2799, 2748, 2699, 2651, 2605, 2559, 2515, 2472, 2430, 2390, 2350, 2311, 2273, 2236, 2200, 2165, 2130, 2097, 2064)
SLOPE = (124, 120, 113, 109, 104, 100, 96, 92, 88, 84, 80, 77, 75, 72, 70, 67, 64, 62, 60, 58, 56, 54, 52, 50, 48, 47, 45, 44, 42, 41, 40, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 29, 28, 27, 26, 26, 25, 24, 23, 23, 22, 22, 21, 21, 20, 20, 19, 18, 18, 18, 18, 17, 16, 16)


def coefficient(v):
    """Return the exact modular coefficient, including each row's rounding."""
    if not 0 <= v < 4096:
        raise ValueError('Root fraction must be a twelve-bit integer')
    a, t = divmod(v, 64)
    value, slope = INTERCEPT[a], SLOPE[a]
    for i in range(6):
        k = 5-i
        upper = slope >> (k+1)
        if t >> i & 1:
            value -= upper + ((slope >> (k-1) & 1) if k else 0)
        else:
            value += upper + (slope >> k & 1)
    return value & 8191


def prove_first_row_top():
    """The first ripple carry implies its next target bit on all 64 codewords.

    Thus carry*bit6=carry permits the top CCX to become CX in that row.
    This is a checked table-domain identity, not an unconditional gate identity.
    """
    for a, slope in zip(INTERCEPT, SLOPE):
        for sign in (0, 1):
            cin = (slope >> 5 & 1) ^ (sign & ((slope >> 4 ^ slope >> 5) & 1))
            carry6 = ((((a & 63) ^ (63*sign)) + (slope >> 6) + cin) >> 6) & 1
            if carry6 and not ((a >> 6 & 1) ^ sign):
                raise ValueError('Coefficient table violates first-row carry identity')


def carry(cb,S,sign,k):
 q=cb.alloc_qubits(1)[0]
 if k:
  cb.cx(S[k],S[k-1]);cb.ccx(sign,S[k-1],q);cb.cx(S[k],S[k-1]);cb.cx(S[k],q)
 else:
  cb.x(sign);cb.ccx(sign,S[0],q);cb.x(sign)
 return q

def clear(cb,S,sign,k,q):
 if k:
  cb.cx(S[k],q);cb.cx(S[k],S[k-1]);cb.del_and(sign,S[k-1],q);cb.cx(S[k],S[k-1])
 else:
  cb.x(sign);cb.del_and(sign,S[0],q);cb.x(sign)
 cb.free(q)

def disposable(ar,cb,source,target,c,erase):
 a,b,preserve=ar._inputs(source,target,c,False);assert preserve is None
 debts={};current=c
 def measure(q,i):
  if q is False:return
  m=cb.alloc_bits(1)[0];cb.hmr(q,m);cb.free(q);debts[i]=m
 for i,(aa,bb) in enumerate(zip(a[:-2],b[:-2])):
  frame=ar._compute_carry(cb,aa,bb,current,preserve=None);ar._sum_keep_carry(cb,frame)
  if i==0:erase(c)
  if i:measure(current,i)
  current=frame.outgoing
 
 if len(b)==8 and len(source)==1:
  # First interpolation row: carry implies pre-top bit6 on this table domain.
  cb.cx(current,b[-1]);cb.cx(current,b[-2])
 else:ar._finish_top(cb,a,b,current,None)
 measure(current,len(b)-2)
 return ar.CarryDebt(debts,len(b))


@dataclass
class CoefficientToken:
    """Measured words and ripple debts that inverse/cleanup must repay."""
    rows: list
    overflow: object
    coded_high_outcome: object
    slope_outcomes: list
    saved_outcome: object


def retire(cb, q):
    outcome = cb.alloc_bits(1)[0]
    cb.hmr(q, outcome)
    cb.free(q)
    return outcome


def forward(cb, ar, v, D, slope_low, bridge):
    """Interpolate D in place; return its complete deferred-measurement token.

    v contains the six low root bits. D has thirteen coefficient owners; D10
    initially holds a disposable lookup coordinate. slope_low contains S0..S4;
    S5 is rebuilt on a fresh owner and framed D12 provides S6 during the rows.
    """
    prove_first_row_top()
    D, v, H = list(D), list(v), list(slope_low)
    high = cb.alloc_qubits(1)[0]
    for q in (D[7],D[8],D[9],H[2],H[4]): cb.cx(q,high)
    frame = (D[8],D[9],D[11],H[2])
    for q in frame: cb.cx(q,D[7])
    cb.cx(H[4],bridge)
    cb.ccx(D[7],bridge,high)
    cb.cx(H[4],bridge)
    for q in reversed(frame): cb.cx(q,D[7])
    cb.cx(high,D[12])
    cb.ccx(D[11],high,D[12])
    coded = retire(cb,D[10])
    bridge_outcome = retire(cb,bridge)
    saved = cb.alloc_qubits(1)[0]
    cb.cx(D[7],saved)
    S = H + [high,D[12]]
    rows = []
    for i in range(6):
        k=5-i
        c=carry(cb,S,v[i],k)
        for q in D[:8]: cb.cx(v[i],q)
        rows.append(disposable(ar,cb,S[k+1:],D[:8],c,
            lambda q,i=i,k=k:clear(cb,S,v[i],k,q)))
        for q in D[:8]: cb.cx(v[i],q)
    D[10] = cb.alloc_qubits(1)[0]
    cb.x(D[10])
    for q in (H[2],H[3],high,D[12]): cb.cx(q,D[10])
    cb.cx(D[12],D[8]); cb.cx(D[12],H[2])
    cb.ccx(D[8],H[2],D[10])
    cb.cx(D[12],H[2]); cb.cx(D[12],D[8])
    cb.cx(D[11],D[9]); cb.cx(H[4],H[3]); cb.cx(high,H[3])
    cb.ccx(D[9],H[3],D[10])
    cb.cx(high,H[3]); cb.cx(H[4],H[3]); cb.cx(D[11],D[9])
    cb.push_condition(bridge_outcome); cb.z(D[10]); cb.pop_condition()
    cb.free(bridge_outcome)
    cb.cx(high,D[12]); cb.ccx(D[11],high,D[12])
    slope_outcomes = [retire(cb,high)] + [retire(cb,q) for q in H]
    sign = v[5]
    cb.cx(sign,saved); cb.cx(sign,D[7]); cb.x(D[7])
    c = cb.alloc_qubits(1)[0]
    cb.ccx(saved,D[7],c)
    for q in D[8:]: cb.cx(sign,q)
    def erase(q):
        cb.del_and(saved,D[7],q)
        cb.free(q)
    overflow = disposable(ar,cb,[],D[8:],c,erase)
    for q in D[8:]: cb.cx(sign,q)
    cb.x(D[7]); cb.cx(sign,D[7]); cb.cx(sign,saved)
    saved_outcome = retire(cb,saved)
    return D,CoefficientToken(rows,overflow,coded,slope_outcomes,saved_outcome)


class _SegmentBuilder:
    """Temporary physical-owner adapter while the remaining stages are lifted.

    The public forward API above accepts the live builder of the full generator.
    This adapter only reconstructs the entry allocator of the existing stage;
    it reads no reference input and carries no operation tape.
    """
    def __init__(self):
        self.cb=km.CircuitBuilder()
        self.cb.set_max_qubits(44)
        self.cb.alloc_qubits(44)
        self.cb.free(km.array([km.q(43),km.q(42)]))
        self.cb.alloc_bits(8)
    def __getattr__(self,name):
        return getattr(self.cb,name)
    def del_and(self,a,b,target):
        self.cb.hmr(target,km.b(1))
        self.cb.ccz(km.b(1),a,b)


def build_coefficient_segment():
    """Compile the recovered metadata/interpolation/overflow stage in isolation."""
    from arithmetic_prefix import arithmetic_modules
    arithmetic_modules()
    shared=sys.modules['_inv74_shared_arithmetic']
    spec=shared._Spec('_inv74_paired_arithmetic',shared._VROOT/'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py')
    ar=shared._new_module(spec)
    sys.modules[spec.name]=ar
    spec.loader.exec_module(ar)
    cb=_SegmentBuilder()
    D=[km.q(i) for i in (21,34,36,0,30,32,28,35,33,31,20,26,27)]
    forward(cb,ar,[km.q(i) for i in range(10,16)],D,[km.q(i) for i in range(37,42)],km.q(29))
    return str(cb.finish_circuit()).splitlines()
