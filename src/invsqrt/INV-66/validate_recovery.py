"""Analysis-only, bit-sliced computational-basis interpreter; no grading.

HMR outcome is fixed to zero. This checks classical register values only,
not amplitudes, measurement phases, or the verifier contract.
"""
from pathlib import Path
import json, re

META = {'REGISTER', 'APPEND_TO_REGISTER', 'INFO_TAG', 'DEBUG_PRINT'}

def operations(path):
    return [line.split() for line in path.read_text(encoding='utf-8').splitlines()
            if line.strip() and line.split()[0] not in META]

class Basis:
    def __init__(self, samples):
        self.samples = list(samples)
        self.full = (1 << len(self.samples)) - 1
        self.q = [0] * 46
        self.b = [0] * 1000
        self.stack = []
        self.measurements = None
        self.phase_sign = 0
        self.rotations = []

    def load(self, values, wires):
        for bit, wire in enumerate(wires):
            self.q[wire] = sum(((v >> bit) & 1) << j for j,v in enumerate(values))

    def read(self, wires):
        return [sum(((self.q[q] >> j) & 1) << k for k,q in enumerate(wires))
                for j in range(len(self.samples))]

    def execute(self, ops, start=0, stop=None, checkpoints=()):
        snapshots = {}
        for i in range(start, len(ops) if stop is None else stop):
            if i in checkpoints:
                snapshots[i] = self.q.copy()
            words = ops[i]
            gate = words[0]
            mask = self.full
            for condition in self.stack:
                mask &= condition
            if 'if' in words:
                p = words.index('if')
                mask &= self.b[int(words[p+1][1:])]
                words = words[:p]
            qs = [int(w[1:]) for w in words[1:] if re.fullmatch(r'q\d+',w)]
            if gate == 'X': self.q[qs[0]] ^= mask
            elif gate == 'CX': self.q[qs[1]] ^= mask & self.q[qs[0]]
            elif gate == 'CCX': self.q[qs[2]] ^= mask & self.q[qs[0]] & self.q[qs[1]]
            elif gate in ('SWAP', 'CSWAP'):
                if gate == 'CSWAP':
                    mask &= self.q[qs.pop(0)]
                delta = mask & (self.q[qs[0]] ^ self.q[qs[1]])
                self.q[qs[0]] ^= delta
                self.q[qs[1]] ^= delta
            elif gate == 'HMR':
                outcome = 0 if self.measurements is None else self.measurements(i, len(self.samples)) & mask
                self.phase_sign ^= self.q[qs[0]] & outcome
                self.q[qs[0]] &= self.full ^ mask
                bit = int(words[-1][1:])
                self.b[bit] = (self.b[bit] & (self.full ^ mask)) | outcome
            elif gate == 'PUSH_CONDITION': self.stack.append(mask)
            elif gate == 'POP_CONDITION': self.stack.pop()
            elif gate == 'BIT_INVERT': self.b[int(words[1][1:])] ^= mask
            elif gate == 'BIT_STORE0': self.b[int(words[1][1:])] &= self.full ^ mask
            elif gate in ('Z','CZ','CCZ','Z_POW','CZ_POW','CCZ_POW','NEG'):
                for q in qs: mask &= self.q[q]
                if gate.endswith('_POW'):
                    self.rotations.append((i,words[-1],mask))
                else:
                    self.phase_sign ^= mask
            else: raise ValueError((i,words))
        return snapshots

def validate(path):
    """Read an explicit analysis reference; never used by solution.py."""
    import hashlib, random, time
    from fractions import Fraction
    import numpy as np
    import recovery_model as model

    started = time.monotonic()
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != '69872bf5557a94e4a7425c9470b7a0451958e18276f2be178b5b0ee27dddb1b1':
        raise ValueError('KMX differs from the frozen analysis reference')
    ops = operations(path)
    assert len(ops) == 23877
    import lookup_certificate
    certificate_path = Path(__file__).resolve().parent/'data/lookup64_certificates.json'
    certificates = json.loads(certificate_path.read_text(encoding='utf-8'))['loaders']
    class Recorder:
        def __init__(self): self.operations=[]
        def x(self,q): self.operations.append(['X',f'q{q}'])
        def cx(self,a,b): self.operations.append(['CX',f'q{a}',f'q{b}'])
        def ccx(self,a,b,t): self.operations.append(['CCX',f'q{a}',f'q{b}',f'q{t}'])
        def hmr(self,q,b): self.operations.append(['HMR',f'q{q}',b])
    for name,start,stop,ports in (
        ('first',1638,2866,[16,17,18,19,20,21,34,36,30,32,28,35,33,31,29,26,27,37,38,39,40,41,42,43,44,45]),
        ('second',15012,16761,[16,17,18,19,20,44,38,37,27,26,29,31,33,35,28,32,9,7,34,8,21]),
    ):
        recorder=Recorder()
        reference=ops[start:stop]
        outcomes=[row[2] for row in reference if row[0]=='HMR']
        lookup_certificate.emit(recorder,certificates[name],ports,outcomes)
        assert recorder.operations == reference, ('certificate synthesis',name)
    xs = np.arange(1,3133453,dtype=np.uint64)
    k = ((22-np.frexp(xs)[1])//2).astype(np.uint64)
    n = xs<<(2*k)
    r = np.sqrt(n*16).astype(np.uint64)
    assert np.all(r*r <= n*16) and np.all((r+1)*(r+1) > n*16)
    v = r-4096
    h = (n-(r*(r+1)//16)-1)&1023
    for j in range(0,len(xs),251):
        assert model.normalize_root(int(xs[j])) == (int(k[j]),int(n[j]),int(v[j]),int(h[j]))
    c = np.asarray([model.coefficient(i) for i in range(4096)],dtype=np.uint64)[v]
    seed = model.seed_word(v,c)
    product = model.signed_product(h,c,seed)

    def truth(values, bit):
        bits = ((values>>bit)&1).astype(np.uint8)
        return int.from_bytes(np.packbits(bits,bitorder='little').tobytes(),'little')

    sim = Basis([])
    sim.samples = None
    sim.full = (1<<len(xs))-1
    for bit in range(22): sim.q[bit] = truth(xs,bit)
    checked = []
    previous = 0
    for boundary,groups in (
        (609,((n,range(22)),(k,range(22,26)))),
        (1638,((v,range(10,22)),(h,range(10)))),
        (3283,((c,model.COEFFICIENT_PORTS),)),
        (3404,((seed,model.SEED_PORTS),)),
        (4407,((product,model.PRODUCT_PORTS),)),
        (15006,((product,model.RETURNED_PRODUCT_PORTS),)),
        (len(ops),((xs,range(22)),)),
    ):
        sim.execute(ops,start=previous,stop=boundary)
        for values,ports in groups:
            for bit,wire in enumerate(ports):
                assert sim.q[wire] == truth(values,bit), (boundary,bit,wire)
        checked.append(boundary)
        previous = boundary
    assert all(q == 0 for q in sim.q[22:])

    # Check every address for both different loader lifecycles.
    d1 = list(model.COEFFICIENT_PORTS)
    d2 = [16,17,18,19,20,38,37,27,26,29,31,33,35]
    loader_counts = []
    for start,stop,inputs,dports,hports in (
        (1638,2866,range(16,22),d1,[39,40,41,42]),
        (15006,16761,[16,17,18,19,20,44],d2,[28,32,9,7]),
    ):
        loader = Basis(range(64))
        loader.load(range(64),inputs)
        loader.execute(ops,start=start,stop=stop)
        assert loader.read(dports) == list(model.INTERCEPT)
        assert loader.read(hports) == [(s>>1)&15 for s in model.SLOPE]
        count_start = start if start == 1638 else 15012
        loader_counts.append(sum(row[0]=='CCX' for row in ops[count_start:stop]))
    assert loader_counts == [27,29]

    # All 4096 possible root values, including coefficient bin boundaries.
    root = Basis(range(4096))
    root.load(range(4096),range(10,22))
    root.execute(ops,start=1638,stop=3283)
    assert root.read(model.COEFFICIENT_PORTS) == [model.coefficient(i) for i in range(4096)]
    root.execute(ops,start=3283,stop=3404)
    assert root.read(model.SEED_PORTS) == [model.seed_word(i,model.coefficient(i)) for i in range(4096)]

    rng = random.Random(660067)
    samples = [1,2,3,4,159,3133452,1048575,1048576,2097151,2097152]
    samples += [rng.randrange(1,3133453) for _ in range(502)]

    def phases(random_outcomes):
        branch = Basis(samples)
        branch.load(samples,range(22))
        if random_outcomes:
            branch.measurements = lambda i,count:rng.getrandbits(count)
        branch.execute(ops)
        assert branch.read(range(22)) == samples
        assert all(q == 0 for q in branch.q[22:])
        result = [Fraction((branch.phase_sign>>j)&1) for j in range(len(samples))]
        for _,angle,mask in branch.rotations:
            for j in range(len(samples)):
                if (mask>>j)&1: result[j] += Fraction(angle)
        return [value%2 for value in result]

    baseline = phases(False)
    for trial in range(8): assert phases(True) == baseline, ('phase branch',trial)
    return dict(
        kind='INDEPENDENT_ARITHMETIC_ANALYSIS_NOT_GRADING',
        reference_kmx_sha256=digest,reference_operations=len(ops),
        model_sha256=hashlib.sha256(Path(model.__file__).read_bytes()).hexdigest(),
        validator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        lookup_emitter_sha256=hashlib.sha256(Path(lookup_certificate.__file__).read_bytes()).hexdigest(),
        lookup_certificate_sha256=hashlib.sha256(certificate_path.read_bytes()).hexdigest(),
        exact_synthesized_lookup_operations=2977,
        exhaustive_input_count=len(xs),checked_boundaries=checked,
        exhaustive_root_values=4096,loader_addresses_per_loader=64,
        loader_AND_counts=loader_counts,
        random_measurement_input_branches=len(samples)*8,measurement_seed=660067,
        arithmetic_mismatches=0,phase_branch_mismatches=0,
        input_restored=True,scratch_zero=True,
        elapsed_seconds=round(time.monotonic()-started,3),
        limitations=[
            'Exhaustive arithmetic/register checks use zero HMR outcomes.',
            'Random measurement checks compare exact phase modulo two half-turns; they do not exhaust all outcomes.',
            'Balanced divider forward quotient/phase model and high-level inverse lifecycle remain unrecovered.',
            'Lookup certificates/emitter recovered; no complete high-level circuit builder, verifier run, or score is asserted.',
        ],
    )

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-kmx',required=True,type=Path)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    report = json.dumps(validate(args.reference_kmx),indent=2)+'\n'
    if args.output: args.output.write_text(report,encoding='utf-8')
    print(report)

