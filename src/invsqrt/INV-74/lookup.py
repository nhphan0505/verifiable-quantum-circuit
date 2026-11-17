"""Compile six-input coefficient codebooks from GF(2) coordinates.

Syed Asad Ali is the original builder (NOTICE.txt). The data contains invertible
linear matrices and factored quadratic coordinate formulas for the two small
64-row lookup problems. It contains no KMB/KMX, angle stream, measurement IDs
or whole-circuit program. Gaussian elimination reconstructs each linear frame;
quadratic control forms are conjugated in their declared mathematical basis.
Every measured coordinate retains its exact 64-codeword truth vector as debt.
"""
from pathlib import Path
import json

FULL=(1<<64)-1


def truth_bits():
    return [sum(((x>>i&1)<<x) for x in range(64)) for i in range(6)]


def parity(mask,functions):
    value=FULL if mask&1 else 0
    for i,f in enumerate(functions):
        if mask>>(1+i)&1:value^=f
    return value


def emit(cb,certificate,wires,functions):
    """Compile a Boolean code and return deferred (outcome, truth) pairs."""
    pending=[]
    for step in certificate['steps']:
        kind=step['kind']
        if kind=='quadratic_coordinate':
            indices=step['variables'];variables=[wires[i] for i in indices]
            target=wires[step['target']];left,right=[wires[i] for i in step['pivots']]
            vals=[functions[i] for i in indices]
            functions[step['target']]^=(FULL if step['constant'] else 0)^parity(step['linear'],vals)^parity(step['left'],vals)&parity(step['right'],vals)
            if step['constant']:cb.x(target)
            for bit,q in enumerate(variables):
                if step['linear']>>(1+bit)&1:cb.cx(q,target)
            frame=[]
            for form,pivot in ((step['left'],left),(step['right'],right)):
                if form&1:raise ValueError('Control form must have zero constant')
                for bit,q in enumerate(variables):
                    if form>>(1+bit)&1 and q!=pivot:frame.append((q,pivot))
            for a,b in frame:cb.cx(a,b)
            cb.ccx(left,right,target)
            for a,b in reversed(frame):cb.cx(a,b)
        elif kind=='affine_frame':
            wi,fi=step['work'],step['fixed'];work=[wires[i] for i in wi];fixed=[wires[i] for i in fi];rows=step['rows'];offset=1+len(fi)
            values=[functions[i] for i in fi+wi]
            for i,row in zip(wi,rows):functions[i]=parity(row,values)
            matrix=[row>>offset for row in rows];operations=[]
            for column in range(len(work)):
                pivot=next(r for r in range(column,len(work)) if matrix[r]>>column&1)
                if pivot!=column:
                    matrix[pivot],matrix[column]=matrix[column],matrix[pivot];operations.append(('swap',pivot,column))
                for r in range(len(work)):
                    if r!=column and matrix[r]>>column&1:matrix[r]^=matrix[column];operations.append(('cx',column,r))
            if matrix!=[1<<i for i in range(len(work))]:raise ValueError('Singular code frame')
            for action,a,b in reversed(operations):
                cb.cx(work[a],work[b])
                if action=='swap':cb.cx(work[b],work[a]);cb.cx(work[a],work[b])
            for target,row in zip(work,rows):
                if row&1:cb.x(target)
                for bit,q in enumerate(fixed):
                    if row>>(1+bit)&1:cb.cx(q,target)
        elif kind=='erase_coordinate':
            i=step['target'];outcome=cb.alloc_bits(1)[0];cb.hmr(wires[i],outcome);pending.append((outcome,functions[i]));functions[i]=0
        else:raise ValueError('Unknown coefficient code coordinate')
    return pending


def load(cb,address,which):
    """Allocate the coded lookup workspace and compile its 64 input functions."""
    path=Path(__file__).resolve().parent/'data/coefficient_codes.json'
    data=json.loads(path.read_text(encoding='utf8'))[which]
    fresh=list(cb.alloc_qubits(data['wire_count']-6));owners=list(address)+fresh
    functions=truth_bits()+[0]*len(fresh)
    pending=emit(cb,data,owners,functions)
    if functions[-1]:raise ValueError('Final lookup temporary was not erased')
    cb.free(owners[-1])
    if which=='first':
        D=[owners[i] for i in (5,6,7,8,9,10,11,12,13,14,4,16,17)]
        H=[owners[i] for i in range(18,23)]
        return D,H,owners[15],pending,functions
    low=[owners[i] for i in range(10)]
    H=[owners[i] for i in (13,14,15,16,17)]
    return low+[None,None,owners[12]],H,(owners[10],owners[11]),pending,functions
