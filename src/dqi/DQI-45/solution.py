"""DQI-45: screen Schur syndrome borrowing and in-place Bezout phase maps.

Sources (Apache-2.0, src/LICENSE.txt): DQI-27 96a39559419067f98dc7cde47ed03ee615de075e,
DQI-19 c0cf9dfb45b62ba7eeb8588c87b0066409880046, DQI-21
2bfda079587dfdc4b85b1245417b7acca52362ff. Structured Bezoutian model functions
derive from DQI-32 10173eea73cf850e4290989c15e31de384f51af0; that PR is closed,
unmerged, and its coherent evaluator reference is not imported as a candidate.

The exact desired map is (f,w)->(f,R=w/f' mod f), with inverse multiplication
by f' on square-free locators. Structured swaps, scales and shears below are a
CLASSICAL reference with coefficients computed from each fixture. They are
not compiled as host-selected gates for a quantum locator. A separate quantum
component accepts already transformed R and verifies the 11-AND root predicate
sweep with runtime masks, restoring coefficients and workspace. This does not
implement coherent preprocessing. No field rounding, mask fitting, degree
cutoff, or claim of a complete H6 submission is made.

Full-width Schur forward/reverse components use the original Narrow Return
layout and a rank-42 override. Read their actual 70-word boundary on valid RS
basis fixtures to test the proposed clean-bank premise. This basis-state test
does not allow measuring coefficients in a submission. Check phase, inputs,
ancilla and forced degree jumps with three measurement seeds. Count inherited
core T and peak Q before assuming the 892-qubit/600k-T goal is attainable.

Commit source/config before running the reproducible screening command:
  python src/dqi/DQI-45/solution.py --config src/dqi/DQI-45/configs/inplace_probe.json --screen
The inferred artifact directory receives a diagnostic JSON report only. A
submission build is deliberately unavailable until a coherent, variable-degree
preprocessing/cleanup schedule and resource gates have been demonstrated.
No .kmb is emitted by screening and no official grader is invoked.
"""
from __future__ import annotations
import argparse
from collections import Counter
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import re
import sys
import subprocess
import time

import kickmix as km
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DEPENDENCIES={
 'schur':('DQI-27','e46d04fee3af4b05ffb1cc7001d5c0098c492a3cb2b64f3d1822d2a14bfa8a08'),
 'rank':('DQI-19','3798b608825c8ca741aaf4cf1d7913d87b650f2be55242a35dc769b8cd47c298'),
 'previous':('DQI-21','32ff5f4ffeade7b98c4470a179e3b57111eb13184125a5d37b693818ffe4aa02')}
def load(name):
    experiment,sha=DEPENDENCIES[name];path=HERE.parent/experiment/'solution.py'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=sha:raise ValueError('Dependency snapshot changed: '+experiment)
    spec=importlib.util.spec_from_file_location('dqi45_'+name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
SCHUR=load('schur');RANK=load('rank');P=load('previous');FIELD=km.GF2Field(12)


def division_ops(divisor,size):
    degree=len(divisor)-1;inverse=FIELD.invert(divisor[-1])
    for high in range(size-1,degree-1,-1):
        yield ('scale',high,high,inverse)
        for j,coefficient in enumerate(divisor[:-1]):yield ('shear',high-degree+j,high,coefficient)

def solve_b1_ops(polynomial,start):
    size=len(polynomial)-1;inverse=FIELD.invert(polynomial[-1])
    for i in range(size//2):yield ('swap',start+i,start+size-i-1,0)
    for i in range(size):
        for j in range(i):yield ('shear',start+i,start+j,polynomial[size-i+j])
        yield ('scale',start+i,start+i,inverse)

def multiply_b1_ops(polynomial):
    size=len(polynomial)-1
    for i in range(size//2):yield ('swap',i,size-i-1,0)
    for i in range(size):
        yield ('scale',i,i,polynomial[-1])
        for j in range(i+1,size):yield ('shear',i,j,polynomial[size+i-j])

def apply_ops(words,ops,inverse=False):
    for kind,dst,src,coefficient in reversed(ops) if inverse else ops:
        if kind=='swap':words[dst],words[src]=words[src],words[dst]
        elif kind=='scale':words[dst]=FIELD.mul(words[dst],FIELD.invert(coefficient) if inverse else coefficient)
        else:words[dst]^=FIELD.mul(coefficient,words[src])

def evaluator_ops(locator):
    """DQI-32 structured reference; host coefficients, never quantum gates."""
    if len(locator)==1:return []
    even=P.trim(FIELD.pow(x,1<<11) for x in locator[::2])
    odd=P.trim(FIELD.pow(x,1<<11) for x in locator[1::2])
    banks=[even+[0]*(18-len(even)),odd+[0]*(18-len(odd))]
    lengths=[len(even),len(odd)];factors=[];history=[];target=0
    while lengths[1-target]:
        divisor=banks[1-target][:lengths[1-target]];size=lengths[target];split=len(divisor)-1
        apply_ops(banks[target],list(division_ops(divisor,size)))
        remainder=P.trim(banks[target][:min(size,split)]);quotient=banks[target][split:size]
        if not history:
            q=P.add(P.square(quotient),[0,1]);d=P.square(divisor)
            assert P.add(P.mul(q,d),P.square(remainder))==locator
            factors.append((len(locator)-1,d,q))
        else:factors.append((2*(size-1),P.square(divisor),P.square(quotient)))
        history.append((target,size,len(divisor)));lengths[target]=len(remainder);target=1-target
    if lengths[target]!=1:raise ValueError('Locator must be square-free')
    for target,size,divisor_size in reversed(history):
        apply_ops(banks[target],list(division_ops(banks[1-target][:divisor_size],size)),inverse=True)
    assert P.trim(banks[0])==even and P.trim(banks[1])==odd
    ops=[];divisions=[]
    for size,divisor,quotient in factors:
        division=list(division_ops(divisor,size));divisions.append(division)
        ops.extend(division);ops.extend(solve_b1_ops(quotient,len(divisor)-1))
    for division in reversed(divisions):
        for kind,dst,src,coefficient in reversed(division):ops.append((kind,src,dst,coefficient))
    ops.extend(multiply_b1_ops(locator));return ops


class RankNarrow(SCHUR.SchurDecoder):
    def multiply_add(self,lhs,rhs,target,control):
        words=[set(x) for x in (lhs,rhs,target)]
        if any(words[i]&words[j] for i in range(3) for j in range(i)):raise ValueError('Aliased field words')
        if control is not True:
            if any(control in word for word in words):raise ValueError('Aliased control')
            masked=self.b.alloc_qubits(12);self.b.init_and(control,lhs,masked)
            self.rank42_unitary(masked,rhs,target)
            self.b.del_and(control,lhs,masked);self.b.free(masked)
        else:self.rank42_unitary(lhs,rhs,target)

    def rank42_unitary(self,lhs,rhs,target):
        """42 CCX, no scratch: conjugate a target pivot by binary basis maps.

        Input parity is computed in a selected input bit and restored. For a
        nonzero output mask p, target fanout L satisfies L(e_pivot)=p. Thus
        L CCX L implements target ^= p*(left_parity AND right_parity) for an
        arbitrary target. The circuit is a classical reversible permutation,
        with no measurements or relative phase. Masked-input HMR follows only
        after all input basis maps are undone; its original factors survive.
        """
        for left,right,output in RANK.rank42_tensor():
            i=(left&-left).bit_length()-1;j=(right&-right).bit_length()-1;k=(output&-output).bit_length()-1
            ls=km.array([lhs[a] for a in range(12) if a!=i and left>>a&1])
            rs=km.array([rhs[a] for a in range(12) if a!=j and right>>a&1])
            ts=km.array([target[a] for a in range(12) if a!=k and output>>a&1])
            if len(ls):self.b.cx(ls,lhs[i])
            if len(rs):self.b.cx(rs,rhs[j])
            if len(ts):self.b.cx(target[k],ts)
            self.b.ccx(lhs[i],rhs[j],target[k])
            if len(ts):self.b.cx(target[k],ts)
            if len(rs):self.b.cx(rs,rhs[j])
            if len(ls):self.b.cx(ls,lhs[i])

def validate_kernel(config):
    reports=[]
    for controlled in (False,True):
        b=km.CircuitBuilder();regs=[b.create_quantum_register(12,k) for k in ('x','y','t')]
        control=b.create_quantum_register(1,'c')[0] if controlled else True
        RankNarrow(b,FIELD,[],masked_cleanup='hmr').multiply_add(*regs,control)
        circuit=b.finish_circuit();assert circuit.operation_statistics().num_toffoli_like==(54 if controlled else 42)
        cases=0
        for seed in config['measurement_seeds']:
            rng=np.random.default_rng(seed);count=65536
            x=rng.integers(0,4096,count,dtype=np.uint32);y=rng.integers(0,4096,count,dtype=np.uint32)
            x[:4096]=np.arange(4096);y[:4096]=0;x[4096:8192]=0;y[4096:8192]=np.arange(4096)
            x[8192:12288]=np.arange(4096);y[8192:12288]=np.arange(4096)
            t=rng.integers(0,4096,count,dtype=np.uint32)
            a=x.copy();product=np.zeros_like(a)
            for i in range(12):
                product^=np.where(y>>i&1,a,0).astype(a.dtype);a<<=1
                a^=np.where(a&4096,FIELD.modulus,0).astype(a.dtype)
            for value in ((False,True) if controlled else (True,)):
                sim=km.Simulator(count,seed=seed,debug_print=False);sim.use_same_registers_as(circuit)
                for reg,data in zip(regs,(x,y,t)):sim.write_across_shots(reg,bits(data))
                if controlled:sim.write_across_shots(control,np.full(count,value,dtype=bool))
                sim.do(circuit)
                for reg,data in zip(regs,(x,y,t^product if value else t)):
                    assert np.array_equal(sim.read_across_shots(reg),bits(data))
                if controlled:assert np.all(sim.read_across_shots(control)==value)
                anc=km.array([km.q(i) for i in range(37 if controlled else 36,circuit.num_qubits)])
                if len(anc):assert not sim.read_across_shots(anc).any()
                assert not sim.read_phase_flipped_across_shots().any();cases+=count
        reports.append({'controlled':controlled,'cases':cases,'qubits':circuit.num_qubits,
                        'static_toffoli_like':circuit.operation_statistics().num_toffoli_like,
                        'value_errors':0,'phase_errors':0,'workspace_errors':0})
    return reports

def bits(values):return np.array([(values>>i)&1 for i in range(12)],dtype=bool)
def read_words(sim,words):
    return np.array([sum(sim.read_across_shots(word)[i].astype(np.uint32)<<i for i in range(12)) for word in words])

def fixtures(config):
    rng=random.Random(config['seed']);cases=[]
    def add(positions,values,label):
        f=[1]
        for j in positions:f=P.mul(f,[1,FIELD.pow(FIELD.primitive_element,j)])
        syndrome=[0]*70
        for j,value in zip(positions,values):
            a=FIELD.pow(FIELD.primitive_element,j)
            for i in range(70):syndrome[i]^=FIELD.mul(value,FIELD.pow(a,i+1))
        omega=[]
        for i in range(70):
            word=syndrome[i]
            for k in range(1,min(i,len(f)-1)+1):word^=FIELD.mul(f[k],syndrome[i-k])
            omega.append(word)
        assert not any(omega[len(positions):])
        cases.append({'weight':len(positions),'positions':positions,'values':values,'label':label,
                      'syndrome':syndrome,'locator':f,'omega':omega[:35]})
    for weight in range(36):
        for _ in range(config['cases_per_weight']):
            add(rng.sample(range(4095),weight),[rng.randrange(1,4096) for _ in range(weight)],'random')
    add([0],[1],'first_position');add([4094],[4095],'last_position')
    for weight in range(1,36):
        positions=list(range(weight));roots=[FIELD.pow(FIELD.primitive_element,j) for j in positions];values=[]
        for i,a in enumerate(roots):
            den=a
            for j,other in enumerate(roots):
                if i!=j:den=FIELD.mul(den,a^other)
            values.append(FIELD.invert(den))
        add(positions,values,'forced_jump')
        assert not any(cases[-1]['syndrome'][:weight-1]) and cases[-1]['syndrome'][weight-1]==1
    return cases

def model(cases):
    maximum=Counter();root_checks=0
    for case in cases:
        f=case['locator'];w=case['omega'];ops=evaluator_ops(f);r=w.copy();apply_ops(r,ops)
        if len(f)>1:
            psi,_=P.reciprocal_reference(f);_,expected=P.divide(P.mul(w,psi),f)
            assert P.trim(r)==expected
            _,restored=P.divide(P.mul(r,P.derivative(f)),f);assert restored==P.trim(w)
        restored=r.copy();apply_ops(restored,ops,inverse=True);assert restored==w
        for j,value in zip(case['positions'],case['values']):
            beta=FIELD.pow(FIELD.primitive_element,(-j)%4095)
            assert P.evaluate(f,beta)==0 and P.evaluate(r,beta)==value
            root_checks+=1
        maximum|=Counter(kind for kind,_,_,_ in ops);case['transformed']=r
    return {'cases':len(cases),'weights':list(range(36)),'root_value_checks':root_checks,
            'max_model_operations_by_kind':dict(maximum),'inverse_checks':len(cases),
            'scope':'classical structured transform only; not coherent preprocessing'}

def boundary_circuit(reverse=False):
    b=km.CircuitBuilder();words=[b.create_quantum_register(12,f'S{i}') for i in range(70)]
    decoder=RankNarrow(b,FIELD,words,masked_cleanup='hmr',use_extra_converter_qubit=True)
    stages={};previous_t=0
    def record(name):
        nonlocal previous_t
        c=b.finish_circuit();t=c.operation_statistics().num_toffoli_like
        stages[name]={'static_toffoli_like':t-previous_t,'qubits_allocated_so_far':c.num_qubits};previous_t=t
        print(json.dumps({'stage':name,**stages[name]}),file=sys.stderr,flush=True)
    if not reverse:
        cursor=b.alloc_qubits(6);decoder.extraction(cursor);decoder.cursor_from_quotients(cursor,reverse=True);b.free(cursor)
        record('forward_extraction');decoder.conversion();record('forward_conversion')
    else:
        decoder.conversion(reverse=True);record('reverse_conversion')
        cursor=b.alloc_qubits(6);decoder.cursor_from_quotients(cursor,reverse=False);decoder.extraction(cursor,reverse=True);b.free(cursor)
        record('reverse_extraction')
    return b.finish_circuit(),words,stages

def boundary(cases,config):
    forward,words,fs=boundary_circuit();reverse,_,rs=boundary_circuit(True)
    q=max(forward.num_qubits,reverse.num_qubits)
    reserve=km.CircuitBuilder();reserve_words=[reserve.create_quantum_register(12,f'S{i}') for i in range(70)]
    scratch=reserve.alloc_qubits(q-840);reserve.free(scratch);reservation=reserve.finish_circuit()
    original=np.array([x['syndrome'] for x in cases],dtype=np.uint32).T
    expected=np.array([[*(v for pair in zip(x['locator'][1:]+[0]*(36-len(x['locator'])),x['omega']) for v in pair)] for x in cases],dtype=np.uint32).T
    witness=None;min_zero=70;universal=np.ones(70,dtype=bool)
    for seed in config['measurement_seeds']:
        sim=km.Simulator(len(cases),seed=seed,debug_print=False);sim.use_same_registers_as(reservation)
        for word,value in zip(reserve_words,original):sim.write_across_shots(word,bits(value))
        sim.do(forward);actual=read_words(sim,words)
        assert np.array_equal(actual,expected),'Schur locator/evaluator boundary convention mismatch'
        assert not sim.read_phase_flipped_across_shots().any(),'Forward arithmetic phase'
        anc=km.array([km.q(i) for i in range(840,q)])
        assert not sim.read_across_shots(anc).any(),'Forward dirty scratch'
        universal&=np.all(actual==0,axis=1)
        zero=np.sum(actual==0,axis=0);min_zero=min(min_zero,int(zero.min()))
        for i,count in enumerate(zero):
            if count==0 and witness is None:
                witness={'seed':seed,'weight':cases[i]['weight'],'positions':cases[i]['positions'],'values':cases[i]['values'],
                         'packed_words':actual[:,i].tolist(),'clean_words':0}
        sim.do(reverse)
        assert np.array_equal(read_words(sim,words),original),'Reverse did not restore syndrome'
        assert not sim.read_across_shots(anc).any() and not sim.read_phase_flipped_across_shots().any(),'Reverse workspace/phase'
    stages={**fs,**rs};total=sum(x['static_toffoli_like'] for x in stages.values())
    return {'cases_per_seed':len(cases),'measurement_seeds':config['measurement_seeds'],'stages':stages,
            'inherited_core_static_toffoli_like':total,'inherited_core_qubits':q,
            'minimum_zero_coefficient_words_observed':min_zero,'always_zero_slots_in_fixtures':np.flatnonzero(universal).tolist(),
            'no_free_bank_witness':witness,'value_errors':0,'phase_errors':0,'workspace_errors':0}

def phase_component(cases,config):
    """Scan precomputed R directly with Schur's beta convention, not R/z."""
    selected=[next(x for x in cases if x['weight']==w) for w in (0,1,7,17,35)]
    b=km.CircuitBuilder();den=[b.create_quantum_register(12,f'f{i+1}') for i in range(35)]
    r=[b.create_quantum_register(12,f'R{i}') for i in range(35)]
    masks=[b.create_classical_register(12,f'E{i}') for i in range(4095)]
    fvalue=b.alloc_qubits(12);rvalue=b.alloc_qubits(12);b.x(fvalue[0])
    sources=lambda rows:km.array([bit for word in rows for bit in word])
    targets=lambda value:km.array([bit for _ in range(35) for bit in value])
    steps=[(word,FIELD.pow(FIELD.primitive_element,-(i+1)%4095)) for i,word in enumerate(den)]
    steps += [(word,FIELD.pow(FIELD.primitive_element,-i%4095)) for i,word in enumerate(r) if i]
    for j,mask in enumerate(masks):
        b.cx(sources(den),targets(fvalue));b.cx(sources(r),targets(rvalue))
        P.phase_point(b,fvalue,rvalue,mask)
        b.cx(sources(r),targets(rvalue));b.cx(sources(den),targets(fvalue))
        if j<4094:
            for word,factor in steps:b.gf2_imul(factor,target=word,field=FIELD)
    for word,factor in steps:b.gf2_idiv(FIELD.pow(factor,4094),target=word,field=FIELD)
    b.x(fvalue[0]);b.free(fvalue+rvalue);c=b.finish_circuit()
    assert c.operation_statistics().num_toffoli_like==45045
    inputs=[x['locator'][1:]+[0]*(36-len(x['locator']))+x['transformed'] for x in selected]
    inputs=np.array(inputs,dtype=np.uint32).T
    for seed in config['measurement_seeds']:
        sim=km.Simulator(len(selected),seed=seed,debug_print=False);sim.use_same_registers_as(c)
        for word,value in zip(den+r,inputs):sim.write_across_shots(word,bits(value))
        rng=np.random.default_rng(seed);expected=np.zeros(len(selected),dtype=bool)
        for j,mask in enumerate(masks):
            value=rng.integers(0,4096,len(selected),dtype=np.uint32);sim.write_across_shots(mask,bits(value))
            for i,x in enumerate(selected):
                if j in x['positions']:expected[i]^=bool((x['values'][x['positions'].index(j)]&int(value[i])).bit_count()&1)
        sim.do(c);assert np.array_equal(read_words(sim,den+r),inputs)
        assert np.array_equal(sim.read_phase_flipped_across_shots(),expected),'Sweep phase convention'
        assert not sim.read_across_shots(km.array([km.q(i) for i in range(840,c.num_qubits)])).any()
    return {'static_toffoli_like':45045,'qubits':c.num_qubits,'points':4095,'cases_per_seed':len(selected),
            'weights':[x['weight'] for x in selected],'measurement_seeds':config['measurement_seeds'],
            'value_errors':0,'phase_errors':0,'workspace_errors':0,'preprocessing':'R supplied by classical model, not computed coherently'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=HERE/'configs/inplace_probe.json');parser.add_argument('--screen',action='store_true')
    args=parser.parse_args();path=args.config.resolve()
    if path.parent!=(HERE/'configs').resolve() or path.suffix!='.json' or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',path.stem):raise ValueError('Config must be directly inside this ID configs/')
    config=json.loads(path.read_text(encoding='utf-8'))
    expected={'m':4095,'n':70,'degree':12,'mode':'screening_only','seed':20261110,'cases_per_weight':2,'measurement_seeds':[4501,4502,4503],'target_qubits':892,'target_total_t':600000}
    if config!=expected:raise ValueError('Only the predeclared screening config is supported')
    if not args.screen:raise RuntimeError('No submission compiler: coherent in-place preprocessing and resource gates are not demonstrated; run --screen')
    started=time.monotonic();kernels=validate_kernel(config);cases=fixtures(config);models=model(cases)
    print('Structured model complete',file=sys.stderr,flush=True)
    bound=boundary(cases,config);phase=phase_component(cases,config)
    optimistic=bound['inherited_core_static_toffoli_like']+phase['static_toffoli_like']
    report={'status':'SCREENED_NOT_BUILT','verification_level':'model and quantum component screening; no submission grading',
            'kernel':kernels,'model':models,'boundary':bound,'phase_component':phase,'optimistic_total_static_t_excluding_preprocessing':optimistic,
            'gates':{'existing_clean_bank_demonstrated':bool(bound['minimum_zero_coefficient_words_observed']>=35),
                     'coherent_variable_degree_preprocessing_implemented':False,'inherited_core_meets_t_budget':optimistic<=config['target_total_t'],
                     'inherited_core_meets_q_budget':bound['inherited_core_qubits']<=config['target_qubits']},
            'submission_artifact':None,'elapsed_seconds':time.monotonic()-started,
            'limitations':['No coherent evaluator transform/cleanup has been synthesized.',
                          'A nonzero-bank witness rejects borrowing existing zeros, not every possible overwrite algorithm.',
                          'The inherited Schur core is kept fixed in the cost bound; a new decoder could change that bound.',
                          'No .kmb or verifier score is produced.']}
    source=Path(__file__).resolve();sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for item in (source,path):
        relative=item.relative_to(ROOT).as_posix()
        assert item.read_bytes()==subprocess.check_output(['git','show',sha+':'+relative],cwd=ROOT),'Uncommitted screening source/config'
    report['provenance']={'source_commit':sha,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                          'build_config_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                          'command':subprocess.list2cmdline([sys.executable,*sys.argv]),
                          'dependency_sha256':{name:value[1] for name,value in DEPENDENCIES.items()}}
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out=ROOT/'artifacts/dqi'/HERE.name/(path.stem+'.'+stamp+'.screening.json');out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
