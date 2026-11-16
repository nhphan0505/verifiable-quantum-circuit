"""Six-bit address decoding and exact repayment of all table HMR debts.

The 8-AND decoder is a small Boolean code certificate. Each phase correction is
synthesized from its truth vector over all 64 addresses in a retained quadratic
chart. Every emitted polynomial is checked before its measurement bit is freed.
The eight temporary banks preserve enough quadratic rank during table erasure.
"""
from pathlib import Path
import json
from lookup_certificate import emit
from recovery_model import INTERCEPT, SLOPE

def bits(values, width):
    return [sum(((v >> i & 1) << a for a, v in enumerate(values))) for i in range(width)]

def cleanup(ctx, cb, D, H, R, pending):
    data = json.loads((Path(__file__).resolve().parent / 'data/cleanup64.json').read_text())
    full = (1 << 64) - 1
    address_truths = bits(range(64), 6)
    rtruth = address_truths[5] ^ address_truths[0] ^ address_truths[1] ^ address_truths[2] ^ (address_truths[0] ^ address_truths[2]) & address_truths[4]
    original = D + H + [R]
    truths = bits(INTERCEPT, 13) + bits([s >> 1 for s in SLOPE], 6)[:4] + [rtruth]
    fresh = list(cb.alloc_qubits(6))
    owners = original + fresh
    values = {q: t for q, t in zip(owners, truths + [0] * 6)}

    class Dual:

        def x(self, q):
            values[q] ^= full
            cb.x(q)

        def cx(self, a, b):
            values[b] ^= values[a]
            cb.cx(a, b)

        def ccx(self, a, b, t):
            values[t] ^= values[a] & values[b]
            cb.ccx(a, b, t)
    raw = emit(Dual(), data['decoder'], owners, [])
    assert [values[q] for q in raw] == address_truths
    assert [values[q] for q in original] == truths
    for i in (0, 1, 2, 5):
        cb.cx(raw[i], R)
    cb.cx(raw[2], raw[0])
    cb.ccx(raw[0], raw[4], R)
    cb.cx(raw[2], raw[0])
    cb.free(R)
    assert rtruth ^ address_truths[0] ^ address_truths[1] ^ address_truths[2] ^ address_truths[5] ^ (address_truths[0] ^ address_truths[2]) & address_truths[4] == 0
    remaining = list(D + H)
    banks = []
    bank_truths = []
    books = {}

    def pay(outcome, truth, columns):
        functions = tuple((values[q] for q in columns))
        if functions not in books:
            books[functions] = ctx.tables.cb.Codebook(functions, 64)
        book = books[functions]
        expression = book.span.solve(truth)
        assert expression is not None, 'Retained quadratic chart cannot repay a phase'
        plan = book.decode_expression(expression)
        assert plan.evaluate_functions(functions, full) == truth
        ctx.tables.cb.emit_phase(cb, columns, outcome, plan)
        cb.free(outcome)
    chart = raw + remaining
    book = ctx.tables.cb.Codebook([values[q] for q in chart], 64)
    assert len(book.span.pivots) == 64
    for outcome, truth in pending:
        pay(outcome, truth, chart)
    pending.clear()
    for pos, signal in enumerate(data['retirement_order']):
        for bank in data['banks_before_retirement'].get(str(pos), []):
            assert bank == len(banks)
            features = raw + banks
            a, b = (features[i] for i in data['bank_factors'][bank])
            target = cb.alloc_qubits(1)[0]
            cb.ccx(a, b, target)
            banks.append(target)
            values[target] = values[a] & values[b]
        target = (D + H)[signal]
        m = cb.alloc_bits(1)[0]
        cb.hmr(target, m)
        remaining.remove(target)
        pay(m, values[target], raw + banks + remaining)
        cb.free(target)
    for bank in data['bank_erasure_order']:
        target = banks[bank]
        m = cb.alloc_bits(1)[0]
        cb.hmr(target, m)
        pay(m, values[target], raw + banks[:bank])
        cb.free(target)
    return raw
