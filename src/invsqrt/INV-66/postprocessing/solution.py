"""PP-005: replace a dead-target CCX followed by HMR with early HMR/CZ.

Attribution: the asteriospanoras dead-write correction described by the supplied
mizeroluckygall walkthrough; this is a new conservative reusable implementation.
rewrite(circuit, operation_index=None) returns (new_circuit, count), changing at
most one site. The caller owns all file I/O; no config, cache or results are used.

Both endpoints must be unconditional and outside a condition stack. The target
cannot be touched between them; the measurement bit cannot be read or written.
Control-flow and metadata/debug barriers are rejected. Controls may change after
the CCX because its conditional CZ is emitted at the original CCX position.
No initial-zero assumption is needed: <m_X|X = (-1)^m <m_X| proves equality of
the branch Kraus operators for arbitrary, including entangled, target states.
This exact rule does not approximate phases or prove verifier PASS on its own.
"""
import io
import re

import kickmix as km

_META = {'REGISTER', 'APPEND_TO_REGISTER', 'INFO_TAG', 'DEBUG_PRINT'}
_KNOWN = {'X', 'Z', 'CX', 'CZ', 'CCX', 'CCZ', 'CSWAP', 'SWAP', 'HMR',
          'Z_POW', 'BIT_INVERT', 'BIT_STORE0', 'BIT_STORE1', 'NEG', 'R'}


def rewrite(circuit, *, operation_index=None):
    """Return a rewritten copy and 1, or the unchanged circuit and 0.

operation_index is zero-based excluding metadata. None searches for the first
safe candidate. A selected noncandidate returns 0; invalid indices raise.
Only this local pass is executed; no other PP is called.
"""
    if operation_index is not None and (type(operation_index) is not int or operation_index < 0):
        raise ValueError('operation_index must be None or a nonnegative integer')
    text = io.StringIO()
    circuit.to_file(text, format='kmx')
    lines = text.getvalue().splitlines()
    ops, depths, depth = [], [], 0
    for line_index, line in enumerate(lines):
        tokens = line.split()
        if not tokens or tokens[0] in _META:
            continue
        ops.append((line_index, tokens))
        depths.append(depth)
        if tokens[0] == 'PUSH_CONDITION':
            depth += 1
        elif tokens[0] == 'POP_CONDITION':
            depth -= 1
            if depth < 0:
                raise ValueError('Unbalanced condition stack')
    if depth:
        raise ValueError('Unbalanced condition stack')
    if operation_index is not None and operation_index >= len(ops):
        raise ValueError('operation_index is outside the circuit')
    indices = range(len(ops)) if operation_index is None else [operation_index]
    for index in indices:
        first, gate = ops[index]
        if depths[index] or len(gate) != 4 or gate[0] != 'CCX':
            continue
        a, b, target = gate[1:]
        if len({a, b, target}) != 3 or not all(re.fullmatch(r'q[0-9]+', q) for q in gate[1:]):
            continue
        last = None
        for j in range(first + 1, len(lines)):
            tokens = lines[j].split()
            if not tokens:
                continue
            if tokens[0] not in _KNOWN:
                break
            if target in tokens:
                if len(tokens) == 3 and tokens[:2] == ['HMR', target] and re.fullmatch(r'b[0-9]+', tokens[2]):
                    last = j
                break
        if last is None:
            continue
        bit = lines[last].split()[2]
        if any(bit in line.split() for line in lines[first + 1:last]):
            continue
        result = lines[:first] + [f'HMR {target} {bit}', f'CZ {a} {b} if {bit}']
        result += lines[first + 1:last] + lines[last + 1:]
        return km.Circuit('\n'.join(result) + '\n'), 1
    return circuit, 0
