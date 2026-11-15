"""Synthesize coefficient lookup circuits from quadratic and affine plans.

The certificate describes only the small six-input Boolean lookup problem.
It carries no angles, whole-circuit payload, KMB, KMX, or measurement IDs.
Callers supply wire owners and measurement outcomes; HMR debts remain theirs.
"""

def emit(builder, certificate, wires, outcomes):
    """Emit a factored GF(2) lookup, returning output wires in table order."""
    fixed = [wires[i] for i in certificate['fixed']]
    offset = 1+len(fixed)
    measurement = iter(outcomes)
    and_count = 0
    for step in certificate['steps']:
        kind = step['kind']
        if kind == 'quadratic_coordinate':
            variables = [wires[i] for i in step['variables']]
            target = wires[step['target']]
            left,right = [wires[i] for i in step['pivots']]
            if step['constant']: builder.x(target)
            for bit,q in enumerate(variables):
                if (step['linear']>>(1+bit))&1: builder.cx(q,target)
            frame = []
            for form,pivot in ((step['left'],left),(step['right'],right)):
                assert not form&1
                for bit,q in enumerate(variables):
                    if (form>>(1+bit))&1 and q != pivot: frame.append((q,pivot))
            for a,b in frame: builder.cx(a,b)
            builder.ccx(left,right,target)
            for a,b in reversed(frame): builder.cx(a,b)
            and_count += 1
        elif kind == 'affine_frame':
            work = [wires[i] for i in step['work']]
            rows = step['rows']
            matrix = [row>>offset for row in rows]
            operations = []
            for column in range(len(work)):
                pivot = next(r for r in range(column,len(work)) if (matrix[r]>>column)&1)
                if pivot != column:
                    matrix[pivot],matrix[column] = matrix[column],matrix[pivot]
                    operations.append(('swap',pivot,column))
                for r in range(len(work)):
                    if r != column and (matrix[r]>>column)&1:
                        matrix[r] ^= matrix[column]
                        operations.append(('cx',column,r))
            assert matrix == [1<<i for i in range(len(work))]
            for action,a,b in reversed(operations):
                builder.cx(work[a],work[b])
                if action == 'swap':
                    builder.cx(work[b],work[a])
                    builder.cx(work[a],work[b])
            for target,row in zip(work,rows):
                if row&1: builder.x(target)
                for bit,q in enumerate(fixed):
                    if (row>>(1+bit))&1: builder.cx(q,target)
        elif kind == 'erase_coordinate':
            builder.hmr(wires[step['target']],next(measurement))
        else:
            raise ValueError('Unknown mathematical lookup step: '+kind)
    assert and_count == certificate['AND_count']
    try:
        next(measurement)
    except StopIteration:
        pass
    else:
        raise ValueError('Unused measurement outcomes')
    return [wires[i] for i in certificate['outputs']]
