"""One-word transpose dot: accumulate its constant output in the target."""


def selected_dot(b, g, v, target, F):
    """target ^= D0 + F*(D0+D1), retaining only D0+D1.

    At each rank t, direct accumulation into target contributes the old D0
    term; the sole temporary receives (1+t) times the same rank product.
    Its X measurement is repaid by that exact transposed bilinear character.
    """
    d = b.alloc_qubits(12)
    N = len(g)
    V, W = k.vandermonde(N)
    for t in range(N):
        rank_update(b, g, V[t], v, [W[i][t] for i in range(N)],
                    [target, d], [1, 1 ^ t])
    for j in range(12):
        b.ccx(F, d[j], target[j])
    r = b.alloc_bits(12)
    b.hmr(d, r)
    b.free(d)
    field = ar.field(12)
    for t in range(N):
        mask = b.alloc_bits(12)
        b.bit_store(mask, False)
        for j in range(12):
            value = field.mul(1 ^ t, 1 << j)
            for i in ar.bits(value):
                b.cx(r[i], mask[j])
        x, p = k.expose(b, g, V[t])
        weights = [W[i][t] for i in range(N)]
        y, q = k.expose(b, v, weights)
        ar.phase_product(b, x, y, mask)
        k.unexpose(b, v, weights, q)
        k.unexpose(b, g, V[t], p)
        b.free(mask)
    b.free(r)


def install(cv, scalar):
    from types import FunctionType
    scope = scalar.scope_of(cv)
    dk = scope['dk']
    dk.selected_dot = FunctionType(selected_dot.__code__,
                                   dict(vars(dk)), 'selected_dot')
    return cv
