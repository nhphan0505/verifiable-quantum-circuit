"""One fixed inverse-field character with a quantum coefficient."""
from pathlib import Path
import json
import sys
HERE = Path(__file__).resolve().parent
KIT_ROOT = HERE.parents[2]
sys.path.insert(0, str(KIT_ROOT / 'exp/r-main/narrow240'))
import exact_subs as xs


def quadratic_decomposition(terms):
    rows = [0] * 10
    linear = 0
    constant = 0
    for term in terms:
        if term[0] == 'constant':
            constant ^= 1
        elif term[0] == 'linear':
            linear ^= 1 << term[1]
        else:
            a, c = term[1:]
            rows[a] ^= 1 << c
            rows[c] ^= 1 << a
    pairs = []
    while any(rows):
        a = next(i for i, row in enumerate(rows) if row)
        c = next(xs.bits(rows[a]))
        left, right = rows[a], rows[c]
        pairs.append((left, right))
        linear ^= left & right
        for i in range(10):
            if left >> i & 1:
                rows[i] ^= right
            if right >> i & 1:
                rows[i] ^= left
    return constant, linear, tuple(pairs)


_record = json.loads((HERE / 'search_quantum_phase6.json').read_text())
CONSTANT, LINEAR, PAIRS = quadratic_decomposition(_record['terms'])
assert len(PAIRS) == 2


def phase_quantum_character(b, x, coefficient, mask):
    """Pay coefficient * dot(mask, inverse0(x)); preserve both inputs."""
    if not mask:
        return
    xs.linear_inplace(b, x, xs.SCALES[mask])
    raw = b.alloc_qubits(4)
    source = list(x) + list(raw)
    for i, (left, right) in enumerate(xs.FORMS):
        with xs.expose_pair(b, source[:6+i], left, right) as (a, c):
            b.init_and(a, c, raw[i])
    if CONSTANT:
        b.z(coefficient)
    for i in xs.bits(LINEAR):
        b.cz(source[i], coefficient)
    for left, right in PAIRS:
        with xs.expose_pair(b, source, left << 1, right << 1) as (a, c):
            b.ccz(a, c, coefficient)
    for i in reversed(range(4)):
        with xs.expose_pair(b, source[:6+i], *xs.FORMS[i]) as (a, c):
            b.del_and(a, c, raw[i])
    b.free(raw)
    xs.linear_inplace(b, x, xs.UNSCALES[mask])
