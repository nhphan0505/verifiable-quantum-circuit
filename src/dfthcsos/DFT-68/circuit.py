# Copyright 2026 Syed Asad Ali. Licensed under Apache-2.0.
"""Frozen algebraic loader compiler; adapted from author source without searches.

Explicit GF(2) product plans generate KMX, with Boolean corrections, HMR and CZ
phase repayment retained. No source archive or precompiled gate stream is read.
Unsupported search plans are rejected. emit_k0 receives its frozen event schedule.
"""
import itertools
import json
from pathlib import Path
import numpy as np
NOUT=35


def emit_k0_emit(s, words, out, events):
    words = apply_padding_completion(s, words)
    assert s['k'] == 0 and 'windows' in s
    if 'explicit_products' in s:
        spec = s['explicit_products']
        D = []
        for p in spec:
            D.append(outer(p['l1'], p['out']))
            if p['l2']:
                D.append(outer(p['l2'], p['out']))
        assert len(basis(D)) == len(D), 'Explicit product columns are dependent'
        cert = s['explicit_certificate']
    else:
        raise ValueError('Only frozen explicit product plans are supported')
    co = coordinate_basis(D)
    T = cross_tensor(words, 0)
    hs = [0] * len(D)
    for h in range(1, 77):
        for i in bitinds(coordinates(T[h], co)):
            hs[i] |= 1 << h
    ps = []
    position = 0
    for p in spec:
        h2 = hs[position]
        position += 1
        h1 = hs[position] if p['l2'] else 0
        if p['l2']:
            position += 1
        if h1 or h2:
            ps.append(dict(p, h1=h1, h2=h2))
    for p in ps:
        p['window'] = next((i for i, w in enumerate(s['windows']) if (p['l1'] | p['l2']) & ~w == 0))
    addr = np.arange(1232)
    low = addr % 16
    high = addr // 16
    cur = words[:, :5]
    corr = np.zeros(1232, dtype=np.uint64)
    for j in range(5):
        corr |= (cur[:, j].astype(np.uint64) & 127) << 7 * j
    for p in ps:
        a = np.zeros(1232, dtype=np.uint8)
        b = a.copy()
        for i in bitinds(p['l1']):
            a ^= low & i + 1 == i + 1
        for i in bitinds(p['l2']):
            b ^= low & i + 1 == i + 1
        for i in bitinds(p['h1']):
            a ^= high & i == i
        for i in bitinds(p['h2']):
            b ^= high & i == i
        corr ^= (a & b).astype(np.uint64) * np.uint64(p['out'])
    c = corr.reshape(77, 16)
    ch = c[:, 0]
    cl = c[0] ^ c[0, 0]
    assert np.array_equal(c, ch[:, None] ^ cl[None, :])
    ah = mobius(ch)
    al = mobius(cl)
    helper, high_helper = separate_helpers((cur >> 7 ^ cur >> 6) & 1)
    hm = mobius(helper)

    def targets(mask):
        return [11 + 8 * (i // 7) + i % 7 for i in bitinds(mask)]
    lines = []
    for q in range(11):
        lines.append(f'APPEND_TO_REGISTER q{q} r0')
    lines.append('REGISTER r0 "selection"')
    for j in range(5):
        for b in range(8):
            lines.append(f'APPEND_TO_REGISTER q{11 + 8 * j + b} r{j + 1}')
        lines.append(f'REGISTER r{j + 1} "word_{j}"')
    for j in range(5):
        lines.append(f'CX q{17 + 8 * j} q{18 + 8 * j}')
    hi = {1 << b: 4 + b for b in range(7)}
    lo = {1 << b: b for b in range(4)}
    nextq = 51
    hcomp = []
    for h in range(1, 77):
        if h in hi:
            continue
        bit = 1 << h.bit_length() - 1
        x, y, z = (hi[h ^ bit], hi[bit], nextq)
        hi[h] = z
        nextq += 1
        lines += [f'R q{z}', f'CCX q{x} q{y} q{z}']
        hcomp.append((x, y, z))
    assert nextq == 120
    for z in targets(int(ah[0])):
        lines.append(f'X q{z}')
    for j in range(5):
        if hm[0, j]:
            lines.append(f'X q{18 + 8 * j}')
    for h in range(1, 77):
        for z in targets(int(ah[h])):
            lines.append(f'CX q{hi[h]} q{z}')
    for h in range(1, len(high_helper)):
        for j in range(5):
            if high_helper[h, j]:
                lines.append(f'CX q{hi[h]} q{18 + 8 * j}')

    def low_correction(m):
        for z in targets(int(al[m])):
            lines.append(f'CX q{lo[m]} q{z}')
        for j in range(5):
            if hm[m, j]:
                lines.append(f'CX q{lo[m]} q{18 + 8 * j}')
    for m in [1, 2, 4, 8]:
        low_correction(m)

    def physical(l, h):
        a = 0
        for i in bitinds(l):
            a ^= 1 << lo[i + 1]
        for i in bitinds(h):
            a ^= 1 << hi[i]
        return a

    def product(p):
        a = physical(p['l1'], p['h1'])
        b = physical(p['l2'], p['h2'])
        ap = (a & -a).bit_length() - 1
        ops1 = [f'CX q{i} q{ap}' for i in bitinds(a ^ 1 << ap)]
        if b >> ap & 1:
            b ^= a ^ 1 << ap
        rest = b & ~(1 << ap)
        bp = (rest & -rest).bit_length() - 1
        assert bp >= 0
        ops2 = [f'CX q{i} q{bp}' for i in bitinds(b ^ 1 << bp)]
        zz = targets(p['out'])
        z = zz[0]
        fan = [f'CX q{z} q{i}' for i in zz[1:]]
        lines.extend(ops1 + ops2 + fan + [f'CCX q{ap} q{bp} q{z}'] + list(reversed(fan)) + list(reversed(ops2)) + list(reversed(ops1)))
    emitted = set()
    events = events
    for e in events:
        m, q = (e['m'], e['qubit'])
        if e['action'] == 'compute':
            x, y = e['controls']
            lines.extend([f'R q{q}', f'CCX q{x} q{y} q{q}'])
            lo[m] = q
            low_correction(m)
            active = sum((1 << mm - 1 for mm in lo))
            for wi, win in enumerate(s['windows']):
                if wi not in emitted and win & ~active == 0:
                    for p in ps:
                        if p['window'] == wi:
                            product(p)
                    emitted.add(wi)
        else:
            x, y = e['phase_controls']
            lines.extend([f'HMR q{q} b0', f'CZ q{x} q{y} if b0'])
            lo.pop(m)
    assert len(emitted) == len(s['windows'])
    for x, y, z in reversed(hcomp):
        lines.extend([f'HMR q{z} b0', f'CZ q{x} q{y} if b0'])
    for j in range(5):
        lines.append(f'CX q{17 + 8 * j} q{18 + 8 * j}')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines) + '\n')
    report = {'k': 0, 'product_count': len(ps), 'high_cache': 69, 'low_computes': 11, 'toffoli_count': len(ps) + 80, 'num_qubits': 128, 'low_cache_peak': 8, 'matching_certificate': cert, 'instructions': len(lines)}
    out.with_suffix('.plan.json').write_text(json.dumps({'report': report, 'products': ps}, indent=2) + '\n')
    return report


def mobius(a):
    a = a.copy()
    for b in range((len(a) - 1).bit_length()):
        for m in range(len(a)):
            if m & 1 << b:
                a[m] ^= a[m ^ 1 << b]
    return a


def emit_plan_emit(s, words, out_path):
    if 'high_cache_plan' in s:
        return high_subspace_emitter_emit(s, words, s['high_cache_plan'], out_path)
    words = apply_padding_completion(s, words)
    k = s['k']
    assert k >= 1, 'ANGLE_0 needs a separately scheduled low-cache window'
    if 'explicit_products' in s:
        spec = s['explicit_products']
        D = []
        for p in spec:
            D.append(outer(p['l1'], p['out']))
            if p['l2']:
                D.append(outer(p['l2'], p['out']))
        assert len(basis(D)) == len(D), 'Explicit product columns are dependent'
        cert = s['explicit_certificate']
    else:
        raise ValueError('Only frozen explicit product plans are supported')
    co = coordinate_basis(D)
    target = cross_tensor(words, k)
    hs = [0] * len(D)
    for h in range(1, 77):
        x = coordinates(target[h], co)
        for i in bitinds(x):
            hs[i] |= 1 << h
    ps = []
    position = 0
    for p in spec:
        h2 = hs[position]
        position += 1
        h1 = hs[position] if p['l2'] else 0
        if p['l2']:
            position += 1
        if h1 or h2:
            ps.append(dict(p, h1=h1, h2=h2))
    helper_table = (words[:, :5] >> 7 ^ words[:, :5] >> 6) & 1
    helper, high_helper = separate_helpers(helper_table)
    prev = words[:, 5 * k - 5:5 * k]
    cur = words[:, 5 * k:5 * k + 5]
    for j in range(5):
        assert np.array_equal((prev[:, j] >> 7 ^ prev[:, j] >> 6) & 1, helper_table[:, j])
        assert np.array_equal((cur[:, j] >> 7 ^ cur[:, j] >> 6) & 1, helper_table[:, j])
    lines = []
    for q in range(11):
        lines.append(f'APPEND_TO_REGISTER q{q} r0')
    lines.append('REGISTER r0 "selection"')
    for j in range(5):
        for b in range(8):
            lines.append(f'APPEND_TO_REGISTER q{11 + 8 * j + b} r{j + 1}')
        lines.append(f'REGISTER r{j + 1} "word_{j}"')
    for j in range(5):
        lines.append(f'CX q{17 + 8 * j} q{18 + 8 * j}')
    hi = {1 << b: 4 + b for b in range(7)}
    lo = {1 << b: b for b in range(4)}
    pure_helpers = True
    for j in range(5):
        ms = [m for m in range(1, 16) if np.array_equal(helper[:, j], (np.arange(16) & m == m).astype(int))]
        if len(ms) != 1:
            pure_helpers = False
        else:
            lo[ms[0]] = 18 + 8 * j
    nextq = 51
    computes = []
    for h in range(1, 77):
        if h in hi:
            continue
        bit = 1 << h.bit_length() - 1
        x = hi[h ^ bit]
        y = hi[bit]
        z = nextq
        nextq += 1
        hi[h] = z
        lines += [f'R q{z}', f'CCX q{x} q{y} q{z}']
        computes.append((x, y, z))
    high_helper_ops = [f'CX q{hi[h]} q{18 + 8 * j}' for h in range(1, len(high_helper)) for j in range(5) if high_helper[h, j]]
    lines += high_helper_ops
    if pure_helpers:
        for l in range(1, 16):
            if l in lo:
                continue
            bit = 1 << l.bit_length() - 1
            x = lo[l ^ bit]
            y = lo[bit]
            z = nextq
            nextq += 1
            lo[l] = z
            lines += [f'R q{z}', f'CCX q{x} q{y} q{z}']
            computes.append((x, y, z))
        low_representations = {m: (1 << q, 0) for m, q in lo.items()}
    else:
        low_computes, low_representations, nextq = synthesize_low_cache(helper, nextq)
        for x, y, z in low_computes:
            lines += [f'R q{z}', f'CCX q{x} q{y} q{z}']
            computes.append((x, y, z))
    assert nextq <= 128

    def fanout(mask):
        return [11 + 8 * (i // 7) + i % 7 for i in bitinds(mask)]

    def physical(l, h):
        mask = 0
        constant = 0
        for i in bitinds(l):
            low_mask, low_constant = low_representations[i + 1]
            mask ^= low_mask
            constant ^= low_constant
        for i in bitinds(h):
            mask ^= 1 << hi[i]
        return (mask, constant)
    for p in ps:
        a, ac = physical(p['l1'], p['h1'])
        b, bc = physical(p['l2'], p['h2'])
        ap = (a & -a).bit_length() - 1
        ops1 = [f'CX q{i} q{ap}' for i in bitinds(a ^ 1 << ap)]
        if ac:
            ops1.append(f'X q{ap}')
        if b >> ap & 1:
            b ^= a ^ 1 << ap
            bc ^= ac
        bp = (b & ~(1 << ap) & -(b & ~(1 << ap))).bit_length() - 1
        assert bp >= 0
        ops2 = [f'CX q{i} q{bp}' for i in bitinds(b ^ 1 << bp)]
        if bc:
            ops2.append(f'X q{bp}')
        outputs = fanout(p['out'])
        z = outputs[0]
        fan = [f'CX q{z} q{i}' for i in outputs[1:]]
        lines += ops1 + ops2 + fan + [f'CCX q{ap} q{bp} q{z}'] + list(reversed(fan)) + list(reversed(ops2)) + list(reversed(ops1))
    addr = np.arange(1232)
    low = addr % 16
    high = addr // 16
    delta = prev ^ cur
    corr = np.zeros(1232, dtype=np.uint64)
    for j in range(5):
        corr |= (delta[:, j].astype(np.uint64) & 127) << 7 * j
    for p in ps:
        a = np.zeros(1232, dtype=np.uint8)
        b = a.copy()
        for i in bitinds(p['l1']):
            a ^= low & i + 1 == i + 1
        for i in bitinds(p['l2']):
            b ^= low & i + 1 == i + 1
        for i in bitinds(p['h1']):
            a ^= high & i == i
        for i in bitinds(p['h2']):
            b ^= high & i == i
        corr ^= (a & b).astype(np.uint64) * np.uint64(p['out'])
    c = corr.reshape(77, 16)
    ch = c[:, 0]
    cl = c[0] ^ c[0, 0]
    assert np.array_equal(c, ch[:, None] ^ cl[None, :]), 'Product tensor mismatch'
    ah = mobius(ch)
    al = mobius(cl)
    for z in fanout(int(ah[0])):
        lines.append(f'X q{z}')
    for h in range(1, 77):
        for z in fanout(int(ah[h])):
            lines.append(f'CX q{hi[h]} q{z}')
    for l in range(1, 16):
        mask, constant = low_representations[l]
        for z in fanout(int(al[l])):
            if constant:
                lines.append(f'X q{z}')
            for q in bitinds(mask):
                lines.append(f'CX q{q} q{z}')
    for x, y, z in reversed(computes[69:]):
        lines += [f'HMR q{z} b0', f'CZ q{x} q{y} if b0']
    lines += list(reversed(high_helper_ops))
    for x, y, z in reversed(computes[:69]):
        lines += [f'HMR q{z} b0', f'CZ q{x} q{y} if b0']
    for j in range(5):
        lines.append(f'CX q{17 + 8 * j} q{18 + 8 * j}')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text('\n'.join(lines) + '\n')
    report = {'k': k, 'product_count': len(ps), 'high_cache': 69, 'low_computes': len(computes) - 69, 'toffoli_count': len(ps) + len(computes), 'num_qubits': nextq, 'instructions': len(lines), 'matching_certificate': cert, 'status': 'Algebraic table check passed; simulator pending.'}
    out_path.with_suffix('.plan.json').write_text(json.dumps({'report': report, 'products': ps}, indent=2) + '\n')
    return report


def bitinds(x):
    out = []
    while x:
        b = x & -x
        x ^= b
        out.append(b.bit_length() - 1)
    return out


def cross_tensor(words, k):
    delta = words[:, 5 * k:5 * k + 5].copy()
    if k:
        delta ^= words[:, 5 * k - 5:5 * k]
    packed = np.zeros(1232, dtype=np.uint64)
    for j in range(5):
        packed[:len(delta)] |= (delta[:, j].astype(np.uint64) & 127) << 7 * j
    f = packed.reshape(77, 16).copy()
    for b in range(4):
        for lo in range(16):
            if lo & 1 << b:
                f[:, lo] ^= f[:, lo ^ 1 << b]
    for b in range(7):
        for hi in range(77):
            if hi & 1 << b:
                f[hi] ^= f[hi ^ 1 << b]
    return [sum((int(f[h, l]) << (l - 1) * NOUT for l in range(1, 16))) for h in range(77)]


def xor_values(mask, values):
    out = 0
    for i in bitinds(mask):
        out ^= values[i]
    return out


def form_truth(anf):
    return sum((sum((int(h & m == m) for m in bitinds(anf))) % 2 << h for h in range(77)))


def joint_controls(a, b):
    """Return a reversible CNOT preparation of two independent XOR forms."""
    assert a and b and (a != b)
    pivot = (a & -a).bit_length() - 1
    op1 = [f'CX q{i} q{pivot}' for i in bitinds(a ^ 1 << pivot)]
    if b >> pivot & 1:
        b ^= a ^ 1 << pivot
    avail = b & ~(1 << pivot)
    second = (avail & -avail).bit_length() - 1
    assert second >= 0
    op2 = [f'CX q{i} q{second}' for i in bitinds(b ^ 1 << second)]
    return (pivot, second, op1 + op2)


def high_subspace_emitter_emit(state, words, cache, out_path):
    words = apply_padding_completion(state, words)
    k = state['k']
    assert k >= 1
    if 'explicit_products' in state:
        specs = state['explicit_products']
        cert = state['explicit_certificate']
        columns = []
        for p in specs:
            columns.append(outer(p['l1'], p['out']))
            if p['l2']:
                columns.append(outer(p['l2'], p['out']))
    else:
        raise ValueError('Only frozen explicit product plans are supported')
    column_rank = len(basis(columns))
    target = cross_tensor(words, k)
    if 'explicit_high_coefficients' in state:
        high_coefficients = list(map(int, state['explicit_high_coefficients']))
        assert len(high_coefficients) == len(columns)
        assert all((0 <= h < 1 << 77 for h in high_coefficients))
        for h in range(1, 77):
            reconstructed = 0
            for c, f in zip(columns, high_coefficients):
                if f >> h & 1:
                    reconstructed ^= c
            assert reconstructed == target[h], ('Explicit dependent cross coefficients mismatch', h)
    else:
        assert column_rank == len(columns)
        co = coordinate_basis(columns)
        high_coefficients = [0] * len(columns)
        for h in range(1, 77):
            for ci in bitinds(coordinates(target[h], co)):
                high_coefficients[ci] |= 1 << h
    products = []
    position = 0
    for p in specs:
        h2 = high_coefficients[position]
        position += 1
        h1 = high_coefficients[position] if p['l2'] else 0
        if p['l2']:
            position += 1
        if h1 or h2:
            products.append(dict(p, h1=h1, h2=h2))
    constant = (1 << 77) - 1
    functions = [sum(((h >> j & 1) << h for h in range(77))) for j in range(7)]
    high_qubits = list(range(4, 11))
    nextq = 51
    high_operations = []
    for operation in cache['operations']:
        left, right = (operation['left_form'], operation['right_form'])
        assert left < 1 << len(functions) and right < 1 << len(functions)
        truth = xor_values(left, functions) & xor_values(right, functions)
        assert truth == operation['truth']
        assert len(basis([constant, *functions, truth])) == len(functions) + 2
        a = sum((1 << high_qubits[i] for i in bitinds(left)))
        b = sum((1 << high_qubits[i] for i in bitinds(right)))
        x, y, ops = joint_controls(a, b)
        high_operations.append((x, y, nextq, ops))
        high_qubits.append(nextq)
        functions.append(truth)
        nextq += 1
    assert len(high_operations) == cache['AND_count']
    high_co = coordinate_basis([constant, *functions])
    assert len(high_co) == cache['rank']

    def high_physical_truth(truth):
        try:
            coord = coordinates(int(truth), high_co)
        except ValueError:
            raise ValueError('Required high function lies outside the explicitly synthesized cache.')
        return (sum((1 << high_qubits[i - 1] for i in bitinds(coord) if i)), coord & 1)

    def high_physical(anf):
        return high_physical_truth(form_truth(anf))
    helper_table = (words[:, :5] >> 7 ^ words[:, :5] >> 6) & 1
    helper, high_helper = separate_helpers(helper_table)
    prev = words[:, 5 * k - 5:5 * k]
    cur = words[:, 5 * k:5 * k + 5]
    for j in range(5):
        assert np.array_equal((prev[:, j] >> 7 ^ prev[:, j] >> 6) & 1, helper_table[:, j])
        assert np.array_equal((cur[:, j] >> 7 ^ cur[:, j] >> 6) & 1, helper_table[:, j])
    lines = [f'APPEND_TO_REGISTER q{q} r0' for q in range(11)] + ['REGISTER r0 "selection"']
    for j in range(5):
        lines += [f'APPEND_TO_REGISTER q{11 + 8 * j + b} r{j + 1}' for b in range(8)]
        lines.append(f'REGISTER r{j + 1} "word_{j}"')
    lines += [f'CX q{17 + 8 * j} q{18 + 8 * j}' for j in range(5)]
    for x, y, z, ops in high_operations:
        lines += ops + [f'R q{z}', f'CCX q{x} q{y} q{z}'] + list(reversed(ops))
    high_helper_ops = []
    for j in range(5):
        mask, offset = high_physical(sum((int(high_helper[h, j]) << h for h in range(len(high_helper)))))
        if offset:
            high_helper_ops.append(f'X q{18 + 8 * j}')
        high_helper_ops.extend((f'CX q{q} q{18 + 8 * j}' for q in bitinds(mask)))
    lines += high_helper_ops
    low_computes, low_representations, nextq = synthesize_low_cache(helper, nextq)
    for x, y, z in low_computes:
        lines += [f'R q{z}', f'CCX q{x} q{y} q{z}']
    assert nextq <= 128

    def fanout(mask):
        return [11 + 8 * (i // 7) + i % 7 for i in bitinds(mask)]

    def physical(low, high):
        mask, offset = high_physical(high)
        for i in bitinds(low):
            m, c = low_representations[i + 1]
            mask ^= m
            offset ^= c
        return (mask, offset)
    for p in products:
        a, ac = physical(p['l1'], p['h1'])
        b, bc = physical(p['l2'], p['h2'])
        ap = (a & -a).bit_length() - 1
        op1 = [f'CX q{i} q{ap}' for i in bitinds(a ^ 1 << ap)]
        if ac:
            op1.append(f'X q{ap}')
        if b >> ap & 1:
            b ^= a ^ 1 << ap
            bc ^= ac
        avail = b & ~(1 << ap)
        bp = (avail & -avail).bit_length() - 1
        assert bp >= 0
        op2 = [f'CX q{i} q{bp}' for i in bitinds(b ^ 1 << bp)]
        if bc:
            op2.append(f'X q{bp}')
        outputs = fanout(p['out'])
        z = outputs[0]
        fan = [f'CX q{z} q{i}' for i in outputs[1:]]
        lines += op1 + op2 + fan + [f'CCX q{ap} q{bp} q{z}'] + list(reversed(fan)) + list(reversed(op2)) + list(reversed(op1))
    address = np.arange(1232)
    low = address % 16
    high = address // 16
    delta = prev ^ cur
    corr = sum(((delta[:, j].astype(np.uint64) & 127) << 7 * j for j in range(5)))
    for p in products:
        a = np.zeros(1232, dtype=np.uint8)
        b = a.copy()
        for i in bitinds(p['l1']):
            a ^= low & i + 1 == i + 1
        for i in bitinds(p['l2']):
            b ^= low & i + 1 == i + 1
        for i in bitinds(p['h1']):
            a ^= high & i == i
        for i in bitinds(p['h2']):
            b ^= high & i == i
        corr ^= (a & b).astype(np.uint64) * np.uint64(p['out'])
    c = corr.reshape(77, 16)
    ch = c[:, 0]
    cl = c[0] ^ c[0, 0]
    assert np.array_equal(c, ch[:, None] ^ cl[None, :]), 'Cross product mismatch'
    obstruction = []
    for bit in range(35):
        truth = sum((int(ch[h] >> np.uint64(bit) & np.uint64(1)) << h for h in range(77)))
        try:
            mask, offset = high_physical_truth(truth)
        except ValueError:
            obstruction.append(bit)
            continue
        z = 11 + 8 * (bit // 7) + bit % 7
        if offset:
            lines.append(f'X q{z}')
        lines.extend((f'CX q{q} q{z}' for q in bitinds(mask)))
    if obstruction:
        raise ValueError('Combined pure-high polarization correction lies outside H at payload bits ' + str(obstruction))
    al = mobius(cl)
    for lowmon in range(1, 16):
        mask, offset = low_representations[lowmon]
        for z in fanout(int(al[lowmon])):
            if offset:
                lines.append(f'X q{z}')
            lines.extend((f'CX q{q} q{z}' for q in bitinds(mask)))
    for x, y, z in reversed(low_computes):
        lines += [f'HMR q{z} b0', f'CZ q{x} q{y} if b0']
    lines += list(reversed(high_helper_ops))
    for x, y, z, ops in reversed(high_operations):
        lines += ops + [f'HMR q{z} b0', f'CZ q{x} q{y} if b0'] + list(reversed(ops))
    lines += [f'CX q{17 + 8 * j} q{18 + 8 * j}' for j in range(5)]
    report = {'k': k, 'product_count': len(products), 'high_cache': len(high_operations), 'low_computes': len(low_computes), 'toffoli_count': len(products) + len(high_operations) + len(low_computes), 'num_qubits': nextq, 'instructions': len(lines), 'all_high_functions_and_combined_correction_in_cache': True, 'cache_rank': len(high_co), 'product_columns': len(columns), 'product_column_rank': column_rank, 'literal_cross_coefficients_verified': True, 'matching_certificate': cert, 'status': 'Exact algebraic check; endpoint simulation pending.'}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text('\n'.join(lines) + '\n')
    out_path.with_suffix('.plan.json').write_text(json.dumps({'report': report, 'products': products}, indent=2) + '\n')
    return report


def monomial(m):
    return sum((1 << a for a in range(16) if a & m == m))


def apply_padding_completion(state, words):
    if 'tail_projection' in state:
        raise ValueError('Materialize the relaxed-tail search state before emission.')
    completion = state.get('padding_completion')
    if completion is None:
        return words
    if completion.get('version') != 1:
        raise ValueError('Unsupported padding-completion version.')
    if completion.get('first_unused_address') != 1220 or completion.get('word_width') != 75:
        raise ValueError('Padding completion must replace exactly addresses 1220 through 1231.')
    source = np.asarray(words)
    if source.shape != (1232, 75) or source.dtype.kind not in 'iu':
        raise ValueError('Expected a 1232 by 75 integer source word table.')
    if np.any(source < 0) or np.any(source > 255):
        raise ValueError('Source words must be bytes.')
    source = np.ascontiguousarray(source, dtype=np.uint8)
    prefix_hash = hashlib.sha256(source[:1220].tobytes()).hexdigest()
    if prefix_hash != completion.get('real_word_prefix_sha256'):
        raise ValueError('Padding completion belongs to a different real word table.')
    suffix = np.asarray(completion.get('words'))
    if suffix.shape != (12, 75) or suffix.dtype.kind not in 'iu':
        raise ValueError('Expected exactly twelve rows of 75 literal integer bytes.')
    if np.any(suffix < 0) or np.any(suffix > 255):
        raise ValueError('Padding completion contains a value outside the byte range.')
    completed = source.copy()
    completed[1220:] = suffix.astype(np.uint8)
    if not np.array_equal(completed[:1220], source[:1220]):
        raise AssertionError('Real-address prefix changed while applying padding.')
    return completed


def basis(xs):
    d = {}
    for x in xs:
        while x:
            j = x.bit_length() - 1
            if j in d:
                x ^= d[j]
            else:
                d[j] = x
                break
    return d


def reduce(x, d):
    for p in sorted(d, reverse=True):
        if x & 1 << p:
            x ^= d[p]
    return x


def outer(l, v):
    out = 0
    while l:
        b = l & -l
        l ^= b
        out ^= v << NOUT * (b.bit_length() - 1)
    return out


def coordinate_basis(xs):
    d = {}
    for i, x in enumerate(xs):
        co = 1 << i
        while x:
            p = x.bit_length() - 1
            if p in d:
                x ^= d[p][0]
                co ^= d[p][1]
            else:
                d[p] = (x, co)
                break
    return d


def coordinates(x, d):
    co = 0
    while x:
        p = x.bit_length() - 1
        if p not in d:
            raise ValueError('outside basis')
        x ^= d[p][0]
        co ^= d[p][1]
    return co


def separate_helpers(table):
    table = np.asarray(table, dtype=np.uint8)
    assert table.ndim == 2 and table.shape[1] == 5 and (len(table) % 16 == 0)
    low = table[:16].copy()
    high = table[::16].copy() ^ low[0]
    addresses = np.arange(len(table))
    assert np.array_equal(table, low[addresses % 16] ^ high[addresses // 16]), 'Helper is not a sum of a low-only and a high-only function'
    anf = high.copy()
    for bit in range((len(high) - 1).bit_length()):
        for h in range(len(high)):
            if h >> bit & 1:
                anf[h] ^= anf[h ^ 1 << bit]
    assert not np.any(anf[0])
    return (low, anf)


def synthesize_low_cache(helper_patterns, next_qubit=120):
    helpers = [18 + 8 * j for j in range(5)]
    functions = {b: monomial(1 << b) for b in range(4)}
    for j, q in enumerate(helpers):
        functions[q] = sum((int(helper_patterns[a, j]) << a for a in range(16)))
    constant = (1 << 16) - 1
    span = basis([constant, *functions.values()])
    assert len(span) == 10, 'Five helpers must be independent modulo affine functions for six ANDs'
    computes = []
    while len(span) < 16:
        choice = None
        for x, y in itertools.combinations(sorted(functions), 2):
            value = functions[x] & functions[y]
            if reduce(value, span):
                choice = (x, y, value)
                break
        assert choice is not None, 'Address bits must generate the full Boolean algebra'
        x, y, value = choice
        z = next_qubit
        next_qubit += 1
        computes.append((x, y, z))
        functions[z] = value
        span = basis([constant, *functions.values()])
    assert len(computes) == 6
    qubits = sorted(functions)
    cb = coordinate_basis([constant] + [functions[q] for q in qubits])
    representations = {}
    for m in range(1, 16):
        coefficients = coordinates(monomial(m), cb)
        affine = coefficients & 1
        mask = sum((1 << q for j, q in enumerate(qubits) if coefficients >> j + 1 & 1))
        rebuilt = constant if affine else 0
        for q in qubits:
            if mask >> q & 1:
                rebuilt ^= functions[q]
        assert rebuilt == monomial(m)
        representations[m] = (mask, affine)
    return (computes, representations, next_qubit)
