"""Recovered 64-row invsqrt arithmetic generator for INV-66.

Normalize -> consumed root/residual -> rounded coefficient -> seed/product ->
balanced m37 divider phase -> inverse arithmetic -> Boolean table erasure ->
inverse root/normalization. Mathematical tables and small GF(2) certificates
are tracked. No downloaded KMB/KMX, gate tape or local bundle is read.
Shared arithmetic primitives are attributed to INV-51; finishing stays separate.
"""
from pathlib import Path
from types import SimpleNamespace
import importlib.util
import hashlib
import io
import json
from arithmetic_helpers import load_math
from lookup_certificate import emit
from recovery_model import INTERCEPT, SLOPE
from cleanup import cleanup
from finishing import finish
HERE = Path(__file__).resolve().parent
POSTPROCESSING_REPORT = {}

def bits(values, width):
    return [sum(((v >> i & 1) << a for a, v in enumerate(values))) for i in range(width)]

def root_frame(cb, v):
    """XOR a5 with a0+a1+a2+(a0+a2)*a4, over GF(2)."""
    for i in (6, 7, 8):
        cb.cx(v[i], v[11])
    cb.cx(v[8], v[6])
    cb.ccx(v[6], v[10], v[11])
    cb.cx(v[8], v[6])

def metadata(cb, v, D, H, inverse=False):
    """Borrow A11/A12 as slope H4/H5 and frame the slope parity in R.

    A10 is restored; no fresh high-slope owner is needed. The reverse is
    scheduled in native compiler order rather than reversing Clifford calls.
    """
    a, b, c = D[10:]
    h = H[3]
    r = v[11]
    if not inverse:
        cb.cx(c, r)
        cb.x(c)
        cb.cx(a, c)
        cb.cx(b, c)
        cb.ccx(a, b, c)
        cb.x(b)
        cb.cx(a, b)
        cb.cx(c, a)
        cb.cx(c, h)
        cb.ccx(a, h, b)
        cb.cx(c, h)
        cb.cx(c, a)
        cb.cx(c, r)
        cb.cx(b, r)
    else:
        cb.cx(b, r)
        cb.cx(c, r)
        cb.x(b)
        cb.cx(a, b)
        cb.cx(c, a)
        cb.cx(c, h)
        cb.ccx(a, h, b)
        cb.cx(c, h)
        cb.cx(c, a)
        cb.x(c)
        cb.cx(a, c)
        cb.cx(b, c)
        cb.ccx(a, b, c)
        cb.cx(c, r)

def disposable_add(ar, cb, source, target, carry, erase):
    """Forward ripple add with early erasure of its owned input carry."""
    a, b, preserve = ar._inputs(source, target, carry, False)
    width = len(b)
    debts = {}
    released = False
    assert preserve is None and width >= 3

    def measure(q, pos):
        if q is False:
            return
        m = cb.alloc_bits(1)[0]
        cb.hmr(q, m)
        cb.free(q)
        debts[pos] = m
    current = carry
    for index, (aa, bb) in enumerate(zip(a[:-2], b[:-2])):
        frame = ar._compute_carry(cb, aa, bb, current, preserve=None)
        ar._sum_keep_carry(cb, frame)
        if index == 0:
            erase(carry)
            released = True
        if index:
            measure(current, index)
        current = frame.outgoing
    ar._finish_top(cb, a, b, current, None)
    measure(current, width - 2)
    return (ar.CarryDebt(debts, width), released)

def overflow(bl, cb, v, D, token):
    sigma = v[token.plan.last - 1]
    saved = token.saved_bit
    top = D[token.window - 1]
    cb.cx(sigma, saved)
    cb.cx(sigma, top)
    cb.x(top)
    carry = cb.alloc_qubits(1)[0]
    cb.ccx(saved, top, carry)
    high = D[token.window:]
    for q in high:
        cb.cx(sigma, q)

    def erase(q):
        cb.del_and(saved, top, q)
        cb.free(q)
    token.overflow_debt, _ = disposable_add(bl.ar, cb, [], high, carry, erase)
    for q in high:
        cb.cx(sigma, q)
    cb.x(top)
    cb.cx(sigma, top)
    cb.cx(sigma, saved)

def coefficient(bl, cb, v, D, H):
    S = [v[11]] + list(H) + list(D[11:])
    saved = cb.alloc_qubits(1)[0]
    cb.cx(D[7], saved)
    token = bl.ar.DeferredBoundedToken(SimpleNamespace(last=6, signed_source=False), saved, 8, [])
    for i in range(6):
        k = 5 - i
        carry = bl._coefficient_carry(cb, S, v[i], k)
        for q in D[:8]:
            cb.cx(v[i], q)

        def erase(q, i=i, k=k):
            bl._clear_coefficient_carry(cb, S, v[i], k, q)
        debt, _ = disposable_add(bl.ar, cb, S[k + 1:], D[:8], carry, erase)
        token.row_debts.append(debt)
        for q in D[:8]:
            cb.cx(v[i], q)
    metadata(cb, v, D, H, inverse=True)
    overflow(bl, cb, v, D, token)
    return token

def lookup(ctx, cb, address, which, debts):
    data = json.loads((HERE / 'data/lookup64_certificates.json').read_text(encoding='utf-8'))['loaders'][which]
    fresh = list(cb.alloc_qubits(20 if which == 'first' else 15))
    owners = list(address) + fresh
    truths = bits(range(64), 6)
    if which == 'second':
        truths[5] ^= truths[0] ^ truths[1] ^ truths[2] ^ (truths[0] ^ truths[2]) & truths[4]
    values = {q: t for q, t in zip(owners, truths + [0] * len(fresh))}

    class Dual:

        def x(self, q):
            values[q] ^= (1 << 64) - 1
            cb.x(q)

        def cx(self, a, b):
            values[b] ^= values[a]
            cb.cx(a, b)

        def ccx(self, a, b, t):
            values[t] ^= values[a] & values[b]
            cb.ccx(a, b, t)

        def hmr(self, q, m):
            debts.append((m, values[q]))
            values[q] = 0
            cb.hmr(q, m)
    outcomes = (cb.alloc_bits(1)[0] for _ in range(sum((s['kind'] == 'erase_coordinate' for s in data['steps']))))
    output = emit(Dual(), data, owners, outcomes)
    for q in owners:
        if q not in output and q not in [owners[i] for i in data['fixed']]:
            assert values[q] == 0
            cb.free(q)
    assert [values[q] for q in output[:13]] == bits(INTERCEPT, 13)
    assert [values[q] for q in output[13:]] == bits([s >> 1 for s in SLOPE], 6)[:4]
    return (list(output[:13]), list(output[13:]))

def build_raw_circuit():
    """Construct all arithmetic and inverse blocks with explicit owner/debt tokens.

    The coefficient code is decoded only after its rounded rows are inverted.
    Exactly 26 live owners (root12/residual10/flags4) remain before inverse root.
    """
    source, ctx = load_math()
    bl = ctx.baseline
    km = ctx.km
    cb = km.CircuitBuilder()
    cb.set_max_qubits(46)
    x = list(cb.alloc_qubits(22))
    flags = list(cb.alloc_qubits(4))
    cuts = {}

    def mark(name):
        cuts[name] = dict(cut=len(str(cb.finish_circuit()).splitlines()), live=cb.num_allocated_qubits)
    ctx.normalization.forward(cb, x, flags)
    mark('normalized')
    root = ctx.root.forward(cb, x)
    v = list(root['root'])
    h = list(root['residual'])
    mark('root')
    debts = []
    D, H = lookup(ctx, cb, v[6:], 'first', debts)
    mark('first_lookup')
    root_frame(cb, v)
    metadata(cb, v, D, H)
    first = coefficient(bl, cb, v, D, H)
    mark('first_coefficient')
    for q, truth in zip(H, bits([s >> 1 for s in SLOPE], 6)[:4]):
        m = cb.alloc_bits(1)[0]
        cb.hmr(q, m)
        debts.append((m, truth))
        cb.free(q)
    saved = bl.ar.release_saved_bit(cb, first.saved_bit)
    first.saved_bit = None
    root_frame(cb, v)
    mark('coefficient_metadata_retired')
    seed, seed_token = bl.seed_forward(cb, v, D)
    mark('seed')
    mtop = cb.alloc_bits(1)[0]
    cb.hmr(v[11], mtop)
    cb.free(v[11])
    v[11] = None
    word, product_token = bl.product_forward(cb, D, seed, h)
    top = cb.alloc_qubits(1)[0]
    for q in D[10:]:
        cb.cx(q, top)
    cb.cx(v[10], D[10])
    cb.cx(v[10], D[11])
    cb.ccx(D[10], D[11], top)
    cb.cx(v[10], D[11])
    cb.cx(v[10], D[10])
    cb.push_condition(mtop)
    cb.z(top)
    cb.pop_condition()
    cb.free(mtop)
    v[11] = top
    cb.x(word[15])
    cb.cx(word[14], word[15])
    cb.free(word[15])
    P = word[:15]
    mark('product')
    coefficient_outcomes = []
    for q in D:
        m = cb.alloc_bits(1)[0]
        cb.hmr(q, m)
        cb.free(q)
        coefficient_outcomes.append(m)
    mark('divider_entry')
    params = json.loads((HERE / 'data/phase_parameters.json').read_text(encoding='utf-8'))
    from fractions import Fraction
    ctx.phase.BINDING.angles = tuple([Fraction(a) * (1 << 49) for a in params['base_half_turns'] + params['overflow_half_turns']] + [0])
    token = ctx.divider.compute_divider(cb, v, P, flags)
    mark('divider_forward')
    ctx.divider.phase_endpoint(cb, token)
    mark('phase')
    P = list(ctx.divider.cleanup_divider(cb, token))
    mark('divider_return')
    root_frame(cb, v)
    D, H = lookup(ctx, cb, v[6:], 'second', debts)
    for i in range(6, 11):
        v[i] = None
    mark('second_lookup')
    bl.ar.repay_saved_bit(cb, D[7], saved)
    metadata(cb, v, D, H)
    second = coefficient(bl, cb, v, D, H)
    mark('second_coefficient')
    for q, m in zip(D, coefficient_outcomes):
        cb.push_condition(m)
        cb.z(q)
        cb.pop_condition()
        cb.free(m)
    for a, b in zip(first.row_debts, second.row_debts):
        bl._merge_debts(cb, a, b)
    bl._merge_debts(cb, first.overflow_debt, second.overflow_debt)
    mark('coefficient_transcripts_paid')
    slope_outcome = cb.alloc_bits(1)[0]
    cb.hmr(H[3], slope_outcome)
    cb.free(H[3])
    H[3] = None
    high = cb.alloc_qubits(1)[0]
    cb.cx(P[14], high)
    cb.x(high)
    word = P + [high]
    dirty = [q for q in v if q is not None] + flags + H[:3] + [second.saved_bit]
    seed, h = ctx.inverse_product(cb, v, D, word, product_token, dirty)
    mark('inverse_product')
    ctx.inverse_seed(cb, v, D, seed, seed_token)
    mark('seed_cleared')
    bl.ar._deferred_overflow(cb, v[:6], [], D, second, inverse=True)
    mark('coefficient_overflow_undone')
    saved = bl.ar.release_saved_bit(cb, second.saved_bit)
    second.saved_bit = None
    H5 = cb.alloc_qubits(1)[0]
    cb.x(H5)
    for q in D[10:]:
        cb.cx(q, H5)
    cb.ccx(D[10], D[11], H5)
    H3 = cb.alloc_qubits(1)[0]
    for q in [D[8], D[10], D[11], D[12], H[1]]:
        cb.cx(q, H3)
    cb.cx(H[1], D[8])
    cb.cx(D[12], D[11])
    cb.cx(H[1], D[11])
    cb.cx(H5, D[11])
    cb.ccx(D[8], D[11], H3)
    cb.cx(H5, D[11])
    cb.cx(H[1], D[11])
    cb.cx(D[12], D[11])
    cb.cx(H[1], D[8])
    cb.cx(H[2], D[9])
    cb.cx(H[2], H[1])
    cb.ccx(D[9], H[1], H3)
    cb.cx(H[2], H[1])
    cb.cx(H[2], D[9])
    H[3] = H3
    H4 = cb.alloc_qubits(1)[0]
    cb.x(H4)
    cb.cx(D[10], H4)
    cb.cx(D[11], H4)
    cb.cx(H5, D[10])
    cb.cx(H5, H3)
    cb.ccx(D[10], H3, H4)
    cb.cx(H5, H3)
    cb.cx(H5, D[10])
    for q in (D[12], H5, H4):
        cb.cx(q, v[11])
    S = [v[11]] + H + [H4, H5]
    mark('coefficient_sources_restored')
    dirty = [q for q in v if q is not None] + flags + h
    for i in reversed(range(6)):
        k = 5 - i
        carry = bl._coefficient_carry(cb, S, v[i], k)
        for q in D[:8]:
            cb.cx(v[i], q)
        bl.ar.inverse_add(cb, S[k + 1:], D[:8], second.row_debts[i], carry_in=carry, dirty_wires=dirty)
        for q in D[:8]:
            cb.cx(v[i], q)
        bl._clear_coefficient_carry(cb, S, v[i], k, carry)
    for q in (H4, H5, D[12]):
        cb.cx(q, v[11])
    plan = ctx.tables.cb.factor_polynomial(4, True, 11, {(0, 2), (0, 3), (2, 3)})
    bl._erase(cb, H4, [D[10], D[11], H3, H5], plan)
    plan = ctx.tables.cb.factor_polynomial(3, True, 7, {(0, 1)})
    bl._erase(cb, H5, D[10:], plan)
    bl.ar.repay_saved_bit(cb, D[7], saved)
    mark('coefficient_restored')
    pending = debts + [(slope_outcome, bits([s >> 1 for s in SLOPE], 6)[3])]
    raw = cleanup(ctx, cb, D, H, v[11], pending)
    v = v[:6] + raw
    assert cb.num_allocated_qubits == 26 and len(set(v + h + flags)) == 26
    mark('table_debts_cleared')
    norm = h + v
    ctx.root.inverse(cb, norm)
    mark('root_restored')
    ctx.normalization.inverse(cb, norm, flags)
    cb.free(km.array(flags))
    mark('logical_input_restored')
    layout = ctx.base.restore_input_layout(cb, norm, x, 46)
    circuit = ctx.common.with_registers(cb.finish_circuit(), dict(x=x))
    return (circuit, dict(cuts=cuts, layout=layout))

def build_circuit(work):
    """Build arithmetic, run declared finishing, then the experiment-local HMR/CZ rule."""
    import kickmix as km
    circuit, construction = build_raw_circuit()
    text, finishing = finish(circuit, work)
    precursor = km.Circuit.from_file(io.BytesIO(text.encode('utf-8')), format='kmx')
    buffer = io.BytesIO()
    precursor.to_file(buffer, format='kmb')
    before = hashlib.sha256(buffer.getvalue()).hexdigest()
    expected = 'dcde70780434501912c5cc032c6dfad25ac694d50da4e8e45cdb65115baa81b2'
    if before != expected:
        raise RuntimeError('Arithmetic precursor mismatch: ' + before)
    path = HERE / 'postprocessing/solution.py'
    spec = importlib.util.spec_from_file_location('inv66_pp005', path)
    pp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pp)
    result, count = pp.rewrite(precursor, operation_index=3292)
    if count != 1:
        raise RuntimeError('Expected one PP-005 rewrite')
    POSTPROCESSING_REPORT.update(method='PP-005', operation_index=3292, rewrites=count, precursor_sha256=before, finishing=finishing, construction=construction)
    return result
