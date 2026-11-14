"""Exact back-half improvements to the uploaded narrow240 decoder.

This file imports only unchanged files from the uploaded kit. All new
arithmetic, scan and measurement-phase helpers are defined here.
"""
from functools import lru_cache
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
import importlib.util
import inspect
import sys

ROOT = Path(__file__).resolve().parent
BASE_DIR = ROOT / 'exp/r-main/narrow240'
sys.path[:0] = [str(BASE_DIR), str(ROOT/'playbook/kit/decoder'),
               str(ROOT/'playbook/kit'),
               str(ROOT/'playbook/kit/decoder/exp/convert')]
spec = importlib.util.spec_from_file_location('uploaded_default',
                                             BASE_DIR/'decode_retimed.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
import high_stream
import direct_converter
import direct_kernels as dk
import truncated_small as small
from converter import clone
from exp.convert import kernels as k
from exp.decoder.common import ar, zero_hold, zero_free
from exp.safe_scalar.phase import phase_classical_parity
from exp.inverse19_joint.kernel import inverse_initialized
from exp.scan.scan import constants, gf, power, mul, inv, scale

def masked_products(b, F, payloads, c, targets):
    """Add F*c*v[-1] to each target, with one shared AND bank.

    HMR of u_i=F*c_i adds r_i*F*c_i to the phase. CCZ(F,c_i,r_i)
    repays it exactly, for every outcome and also when F or c is zero.
    """
    u = b.alloc_qubits(12)
    for i in range(12):
        b.init_and(F, c[i], u[i])
    for v, t in zip(payloads, targets):
        ar.mul_xor0(b, u, v[-1], t)
    mask = b.alloc_bits(12)
    b.hmr(u, mask)
    b.free(u)
    for i in range(12):
        b.ccz(F, c[i], mask[i])
    b.free(mask)


def q_post(b, q, payloads, H, m, parent, reverse=False, phase=None):
    if parent is None:
        with q_inverse(b, q, m, reverse, phase) as qi:
            for v in payloads:
                scale(b, v[-1], q, qi, not reverse)
        return
    tops, p, c = parent
    if reverse or m + 1 in KEEP_CHILD:
        F = phase['given_gap'].pop(m + 1)
    else:
        F = fresh_zero_flag(b, q)
        consume_flag(b, F, phase['incoming_gap'].pop(m + 1))
    b.cswap(F, q, p)
    if not reverse:
        for v, t in zip(payloads, tops):
            b.cswap(F, v[-1], t)
    with q_inverse(b, q, m, reverse, phase) as qi:
        if not reverse:
            for v in payloads:
                scale(b, v[-1], q, qi, True)
            masked_products(b, F, payloads, c, tops)
        else:
            masked_products(b, F, payloads, c, tops)
            for v in payloads:
                scale(b, v[-1], q, qi, False)
    if reverse:
        for v, t in zip(payloads, tops):
            b.cswap(F, v[-1], t)
    b.cswap(F, q, p)
    if reverse and m + 1 not in KEEP_CHILD:
        phase['return_mask'][m + 1] = hold_flag(b, F)
    else:
        phase['returned_gap'][m + 1] = F


def selected_pre(b,f,g,payloads,F,undo=False,incoming=None,defer=False):
    if not undo:return ordinary_pre(b,f,g,payloads,F,False,incoming,defer)
    # F=[g[-1]=0] is already live. Thus the old 24-bit zero test equals
    # F AND [g[-2]=0]. The temporary zero ladder is erased exactly.
    ladder=zero_hold(b,g[-2]);Z0=b.alloc_qubits(1)[0]
    b.init_and(F,ladder[-1],Z0);zero_free(b,g[-2],ladder)
    b.cx(Z0,g[-2][0])
    masks=high_full_restore(b,f,g,F)
    b.cx(Z0,g[-2][0]);pivot(b,g,F);a=g[-1]
    ai,Z=inverse_zero(b,a);b.cx(Z,Z0);b.free(Z0);consume(b,ai,Z,incoming)
    b.cx(Z,a[0]);b.cx(Z,ai[0]);high_close_heads(b,f,g,ai,F,masks)
    for v in payloads:dk.shifted_product(b,g[:-1],v[-1],v[:-1],F)
    for v in payloads:scale(b,v[-1],a,ai,False)
    b.cx(Z,ai[0]);b.cx(Z,a[0]);out=erase(b,a,ai,Z,defer)
    pivot(b,g,F);return out


def triple_square_phase(b,x,y,z,mask):
    """Apply (-1)**dot(mask, x*y*z**2), with no fresh quantum wire."""
    assert len(x)==len(y)==len(z)==len(mask)==12
    f=ar.field(12)
    for linear,vector in ar.tensor(12):
        co=b.alloc_bits(12)
        b.bit_store(co,False)
        for j in range(12):
            for k in ar.bits(f.mul(vector,f.square(1<<j))):
                b.cx(mask[k],co[j])
        ix=list(ar.bits(linear));p=ix[0]
        for j in ix[1:]:
            b.cx(x[j],x[p]);b.cx(y[j],y[p])
        phase_classical_parity(b,x[p],y[p],z,co)
        for j in reversed(ix[1:]):
            b.cx(y[j],y[p]);b.cx(x[j],x[p])
        b.free(co)


def high_close_heads(b,f,g,ai,F,masks):
    lo,hi=f[-2:]
    ar.phase_product(b,hi,ai,masks[1])
    ar.phase_product(b,lo,ai,masks[0])
    with dk.selected(b,g[-2],g[-3],F) as c:
        triple_square_phase(b,hi,c,ai,masks[0])
    for mask in masks:b.free(mask)


def close_heads(b,f,g,ai,masks):
    lo,hi=f[-2:]
    ar.phase_product(b,hi,ai,masks[1])
    ar.phase_product(b,lo,ai,masks[0])
    triple_square_phase(b,hi,g[-2],ai,masks[0])
    for mask in masks:b.free(mask)


CUBE_TERMS = ((1211, 2209, 1392), (1841, 3016, 2582), (179, 3076, 80), (41, 3038, 2255), (8, 774, 1831), (1875, 2483, 3690), (1651, 2511, 2931), (280, 3214, 3979), (26, 3467, 589), (929, 3190, 2015), (303, 631, 540), (1973, 2217, 1107), (595, 3124, 703), (127, 2465, 2410), (440, 756, 735), (688, 3342, 3259), (894, 2259, 2441), (453, 3665, 525), (1504, 2527, 499), (212, 3164, 1395), (728, 3409, 2134), (497, 2243, 2285), (211, 3422, 1259), (1315, 3054, 1230))
CUBE_LINEAR = (1453, 3308, 1839, 1801, 3614, 2307, 1204, 3804, 23, 166, 1183, 1118)


def quadratic_accumulate(b, x, z, terms, linear):
    assert len(set(map(str, list(x)+list(z)))) == len(x)+len(z)
    for i, value in enumerate(linear):
        for j in ar.bits(value):
            b.cx(x[i], z[j])
    for A, C, value in terms:
        assert A and C and A != C and value
        left = list(ar.bits(A))
        p = left[0]
        for i in left[1:]:
            b.cx(x[i], x[p])
        transformed_C = C ^ ((A ^ (1 << p)) if (C >> p) & 1 else 0)
        q = next(i for i in ar.bits(transformed_C) if i != p)
        right = [i for i in ar.bits(transformed_C) if i != q]
        for i in right:
            b.cx(x[i], x[q])
        output = list(ar.bits(value))
        t = output[0]
        for j in output[1:]:
            b.cx(z[t], z[j])
        b.ccx(x[p], x[q], z[t])
        for j in reversed(output[1:]):
            b.cx(z[t], z[j])
        for i in reversed(right):
            b.cx(x[i], x[q])
        for i in reversed(left[1:]):
            b.cx(x[i], x[p])


def cube_xor(b, x, z):
    quadratic_accumulate(b, x, z, CUBE_TERMS, CUBE_LINEAR)


def cube_phase(b, x, mask):
    field = ar.field(12)
    linear = [field.pow(1 << i, 3) for i in range(12)]
    for i, value in enumerate(linear):
        for bit in ar.bits(value):
            b.cz(x[i], mask[bit])
    for i in range(12):
        for j in range(i):
            value = field.pow((1 << i) ^ (1 << j), 3) ^ linear[i] ^ linear[j]
            for bit in ar.bits(value):
                b.ccz(x[i], x[j], mask[bit])


def hankel_direct(b, q, x):
    """Apply T(q) to len(x)=3 or 4 words, q[0] is coefficient of z."""
    n = len(x)
    assert n in (3, 4)
    copies = [b.alloc_qubits(12) for _ in range(n-2)]
    for source, target in zip(x[1:-1], copies):
        b.cx(source, target)
    small.accumulate(b, [v for w in [x[0]]+copies for v in w],
                     [v for w in q[:n-1] for v in w],
                     [v for w in x[1:] for v in w], n-1)
    masks = [b.alloc_bits(12) for _ in copies]
    for source, mask in zip(copies, masks):
        b.hmr(source, mask)
        b.free(source)
    # old x1 = new x1 + q1*x0.
    b.cz(x[1], masks[0])
    ar.phase_product(b, q[0], x[0], masks[0])
    if n == 4:
        # old x2 = new x2 + q1*new x1 + (q1^2+q2)*x0.
        b.cz(x[2], masks[1])
        ar.phase_product(b, q[0], x[1], masks[1])
        ar.phase_product(b, q[1], x[0], masks[1])
        ar.linear_inplace(b, q[0], ar.square_columns(12))
        ar.phase_product(b, q[0], x[0], masks[1])
        ar.linear_inplace(b, q[0], [ar.field(12).pow(1 << i, 2048) for i in range(12)])
    for mask in masks:
        b.free(mask)


@lru_cache(None)
def reverse_partition(n):
    if n == 1:
        return 0, None
    choices = []
    if n == 3:
        choices.append((99, None))
    if n == 4:
        choices.append((153, None))
    for left in range(1, n):
        choices.append((reverse_partition(left)[0]
                        + reverse_partition(n-left)[0] + 42*(n-1), left))
    return min(choices, key=lambda pair: pair[0])


def hankel(b, B, A, reverse=False):
    if not reverse:
        return k.hankel(b, B, A)
    cube = b.alloc_qubits(12)
    cube_xor(b, B[-1], cube)

    def reverse_tri(b, q, x, reverse=False):
        assert reverse
        n = len(x)
        if n == 1:
            return
        _, left = reverse_partition(n)
        if left is None:
            if n == 4:
                b.cx(cube, q[2])
            ar.linear_xor(b, q[0], q[1], ar.square_columns(12))
            hankel_direct(b, q, x)
            ar.linear_xor(b, q[0], q[1], ar.square_columns(12))
            if n == 4:
                b.cx(cube, q[2])
            return
        right = n-left
        reverse_tri(b, q[:left-1], x[:left], True)
        for ac, bc, tc in reversed(k.cross_terms(left, right)):
            k.rank_update(b, x[:left], ac, q[:n-1], bc, x[left:], tc)
        reverse_tri(b, q[:right-1], x[left:], True)

    clone(k.hankel, dict(vars(k), tri=reverse_tri))(b, B, A, True)
    mask = b.alloc_bits(12)
    b.hmr(cube, mask)
    b.free(cube)
    cube_phase(b, B[-1], mask)
    b.free(mask)


def scan(b, A, B, E, *, points=4095, skip_points=(), node_polynomial=None):
    if len(A) != 35 or len(B) != 35 or len(E) < points:
        raise ValueError("need 35+35 words and one mask per point")
    if points != 4095:
        raise ValueError("full cycle required for restoration")
    alpha = gf.primitive_element
    P = constants()[2] if node_polynomial is None else node_polynomial
    powers = [power(alpha, k) for k in range(35)]
    skip_points = frozenset(skip_points)
    assert all(0 <= j < 4095 for j in skip_points)
    beta = lead = 1
    leadstep = power(alpha, 35)
    m = b.alloc_bits(12)
    nonzero = b.alloc_bits(1)
    for j in range(4095):
        if j not in skip_points:
            # OR is implemented entirely on classical wires, using the
            # builder's conditional store.  No quantum input is observed.
            b.bit_store(nonzero, False)
            for bit in E[j]:
                b.bit_store(nonzero, True, control=bit)
            b.push_condition(nonzero[0])
            for k in range(1, 35):
                b.cx(A[k], A[0])
                b.cx(B[k], B[0])
            b.gf2_iadd(lead, target=B[0])
            ladder = zero_hold(b, B[0])
            pv = 0
            for v in reversed(P):
                pv = mul(pv, beta) ^ v
            c = inv(mul(beta, pv))
            assert c
            b.bit_store(m, False)
            for t in range(12):
                for i in ar.bits(mul(c, 1 << t)):
                    b.cx(E[j][i], m[t])
            b.ccz(ladder[-1], A[0], m)
            zero_free(b, B[0], ladder)
            b.gf2_iadd(lead, target=B[0])
            for k in range(1, 35):
                b.cx(A[k], A[0])
                b.cx(B[k], B[0])
            b.pop_condition()
        for k in range(1, 35):
            scale(b, A[k], powers[k])
            scale(b, B[k], powers[k])
        beta = mul(beta, alpha)
        lead = mul(lead, leadstep)
    assert beta == lead == 1
    b.free(nonzero)
    b.free(m)


def make_converter():
    original = direct_converter.mh.make_converter

    def factory(return_scope=False):
        cv, scope, short = original(True)
        scope['masked_products'] = clone(masked_products, scope)
        scope['q_post'] = clone(q_post, scope)
        short['old'] = SimpleNamespace(**scope)
        return (cv, scope, short) if return_scope else cv

    direct = SimpleNamespace(**dict(vars(direct_converter),
                                   mh=SimpleNamespace(make_converter=factory)))
    cv = clone(high_stream.make_converter,
               dict(vars(high_stream), direct=direct))()
    cells = dict(zip(cv.__code__.co_freevars, cv.__closure__))
    short = cells['core'].cell_contents.__globals__
    scope = short['old'].direct_post.__globals__
    scope.update(zero_hold=zero_hold, zero_free=zero_free,
                 KEEP_FULL=frozenset({16}), THRESHOLD=6)
    short['KEEP_FULL'] = scope['KEEP_FULL']
    scope['direct_pre'] = clone(selected_pre, scope)
    scope['high_close_heads'] = high_close_heads
    scope['close_heads'] = close_heads
    short['old'].hankel = hankel
    return cv


def gap_zero_action(b,f,g,payloads,ai,F,H,post,undo):
    a=g[-1]
    b.ccx(F,H,a[0])
    root_action(b,f,g,payloads,ai,False,F,post,undo)
    b.ccx(F,H,a[0])


def look_root_cached(b,O,g,payloads,reverse,phase):
    m=len(O);keep=m in KEEP_CHILD;full=m in KEEP_FULL
    F=phase['held_gap'].pop(m) if reverse and full else old.fresh_zero_flag(b,g[-1])
    if reverse and not full:consume_flag(b,F,phase['gap_flags'].pop(m))
    pivot(b,g,F);a=g[-1];ai,Z=old.inverse_zero(b,a);b.cx(Z,ai[0])
    if reverse:
        mask=phase.pop('_root_inverse_mask');b.cz(ai,mask);b.free(mask)
    f=list(O)+[ai]
    if reverse:
        H=phase['held_gap'][m-1]
        mask=b.alloc_bits(1);b.hmr(Z,mask[0]);b.free(Z)
        b.ccz(F,H,mask[0]);b.free(mask)
        gap_zero_action(b,f,g,payloads,ai,F,H,post=True,undo=True)
    else:
        root_action(b,f,g,payloads,ai,Z,F,post=False,undo=False)
        erase_product_zero(b,a,ai,Z)
    pivot(b,g,F);aligned(b,f,g,F)
    if reverse or keep:phase['given_gap'][m]=F
    else:phase['incoming_gap'][m]=hold_flag(b,F)
    parent=([v[-1]for v in payloads],f[-1],f[-2])
    old.look_solve(b,g,f[:-2],[v[:-1]for v in payloads],None,parent,reverse,phase)
    if reverse and not keep:
        F=old.fresh_zero_flag(b,g[-1]);consume_flag(b,F,phase['return_mask'].pop(m))
    else:F=phase['returned_gap'].pop(m)
    aligned(b,f,g,F);pivot(b,g,F)
    if not reverse:
        H=phase['held_gap'][m-1]
        gap_zero_action(b,f,g,payloads,ai,F,H,post=True,undo=False)
    else:
        Z=old.fresh_zero_flag(b,a)
        root_action(b,f,g,payloads,ai,Z,F,post=False,undo=True)
        erase_product_zero(b,a,ai,Z)
    mask=b.alloc_bits(12);b.hmr(ai,mask);b.free(ai)
    if reverse:phase_inverse34(b,a,mask,zero_mask=mask[0]);b.free(mask)
    else:phase['_root_inverse_mask']=mask
    pivot(b,g,F)
    if reverse:clear_flag(b,g[-1],F)
    elif full:phase['held_gap'][m]=F
    else:phase['gap_flags'][m]=hold_flag(b,F)


def consume_clipped(b,ai,F,H,token):
    if token is None:return
    mask,zm=token
    b.cz(ai,mask)
    b.ccz(F,H,mask[0]);b.ccz(F,H,zm[0])
    b.free(mask);b.free(zm)


def retire_clipped(b,ai):
    mask=b.alloc_bits(12);b.hmr(ai,mask);b.free(ai)
    zm=b.alloc_bits(1);b.bit_store(zm,False);b.cx(mask[0],zm[0])
    return mask,zm


def post(b,f,g,payloads,F,H,parent,reverse=False,incoming=None,defer=False,phase=None):
    m=len(f)-1;G=phase['held_gap'][m-1];q0,q1=f[-2:]
    assert defer
    if not reverse:
        q_post(b,q1,payloads,H,m,parent,phase=phase)
        pivot(b,g,F);a=g[-1]
        for v in payloads:dk.selected_dot(b,g[:-1],v[:-1],v[-1],F)
        b.ccx(F,G,a[0]);ai=inverse_initialized(b,a)
        consume_clipped(b,ai,F,G,incoming)
        for v in payloads:scale(b,v[-1],a,ai,True)
        out=retire_clipped(b,ai)
        pivot(b,g,F);phase['heads'][m]=high_full_restore(b,f,g,F)
        # The product flag implies F=1, so the selected scalar is here.
        b.ccx(F,G,g[-2][0])
        return out
    pivot(b,g,F);a=g[-1]
    b.ccx(F,G,a[0]);ai=inverse_initialized(b,a)
    consume_clipped(b,ai,F,G,incoming)
    scale(b,q1,a,ai,True);cross(b,g,q1,q0,F);scale(b,q0,a,ai,True)
    for word,mask in zip([q0,q1],phase['heads'].pop(m)):
        b.cz(word,mask);b.free(mask)
    dk.shifted_conv(b,g[:-1],[q0,q1],f[:-2],F,True)
    for v in payloads:scale(b,v[-1],a,ai,False)
    b.ccx(F,G,a[0]);out=retire_clipped(b,ai)
    for v in payloads:dk.selected_dot(b,g[:-1],v[:-1],v[-1],F)
    pivot(b,g,F);q_post(b,q1,payloads,H,m,parent,True,phase)
    return out


def install_retained_gaps(cv):
    cells=dict(zip(cv.__code__.co_freevars,cv.__closure__))
    short=cells['core'].cell_contents.__globals__
    scope=short['old'].direct_post.__globals__
    scope['KEEP_FULL']=frozenset({15,16,17})
    short['KEEP_FULL']=scope['KEEP_FULL']
    old_inverse=scope['q_inverse']
    @contextmanager
    def q_inverse(b,a,m,reverse,phase):
        if m!=16 or not phase['_short_monic']:
            with old_inverse(b,a,m,reverse,phase) as ai:
                yield ai
            return
        ai=inverse_initialized(b,a)
        if reverse:
            mask=phase['q'].pop(m);b.cz(ai,mask);b.free(mask)
        yield ai
        mask=b.alloc_bits(12);b.hmr(ai,mask);b.free(ai)
        if reverse:
            short['phase_inverse34'](b,a,mask);b.free(mask)
        else:phase['q'][m]=mask
    scope['q_inverse']=q_inverse
    short['gap_zero_action']=clone(gap_zero_action,short)
    short['look_root_cached']=clone(look_root_cached,short)
    original=scope['direct_post']
    scope.update(consume_clipped=consume_clipped,retire_clipped=retire_clipped,
                 inverse_initialized=inverse_initialized)
    selected=clone(post,scope)
    def direct_post(b,f,g,payloads,*args,**kwargs):
        return (selected if len(f)-1==16 else original)(b,f,g,payloads,*args,**kwargs)
    scope['direct_post']=direct_post
    return cv


def make_gate(b, F, H):
    """G=H(1+F)."""
    G = b.alloc_qubits(1)[0]
    b.x(F); b.init_and(F, H, G); b.x(F)
    return G


def erase_gate(b, F, H, G):
    mask = b.alloc_bits(1)
    b.hmr(G, mask[0]); b.free(G)
    b.cz(H, mask[0]); b.ccz(F, H, mask[0])
    b.free(mask)


def quotient_inverse(b, p, g, F, H, K):
    # FH+GK = H+G(1+K), since G=H(1+F).
    t, s = g[-1], g[-2]
    G = make_gate(b, F, H)
    r = b.alloc_qubits(12)
    b.cx(t, r); b.cx(H, r[0])
    b.cx(s, t); b.cx(K, t[0]); b.x(t[0])
    b.ccx(G, t, r)
    b.x(t[0]); b.cx(K, t[0]); b.cx(s, t)
    erase_gate(b, F, H, G)
    qi = b.alloc_qubits(12)
    b.cx(F, p[0]); ar.mul_xor0(b, p, r, qi); b.cx(F, p[0])
    mask = b.alloc_bits(12)
    b.hmr(r, mask); b.free(r)
    b.cz(t, mask); b.cz(H, mask[0])
    G = make_gate(b, F, H)
    b.ccz(G, t, mask); b.ccz(G, s, mask)
    b.ccz(G, K, mask[0]); b.cz(G, mask[0])
    erase_gate(b, F, H, G); b.free(mask)
    return qi


def close_quotient_phase(b, p, g, F, H, K, mask):
    # p*F=0 after the parent swap, and H*t=0 for t=g[-1].
    # Therefore qi=(p+F)*t + H*p*(s+K) + F*H.
    t, s = g[-1], g[-2]
    b.cx(F, p[0]); ar.phase_product(b, p, t, mask); b.cx(F, p[0])
    b.ccz(F, H, mask[0])
    b.cx(K, s[0])
    field = ar.field(12)
    for j in range(12):
        coefficients = b.alloc_bits(12); b.bit_store(coefficients, False)
        for i in range(12):
            for bit in ar.bits(field.mul(1 << i, 1 << j)):
                b.cx(mask[bit], coefficients[i])
        phase_classical_parity(b, H, s[j], p, coefficients)
        b.free(coefficients)
    b.cx(K, s[0])


def root_child_post(b, q, payloads, H, m, parent, reverse=False, phase=None):
    if m != 16 or not phase['_short_monic']:
        return prior_q_post(b, q, payloads, H, m, parent, reverse, phase)
    assert parent is not None
    tops, p, c = parent
    g, current, child = phase['_child_scalar_context']
    if reverse or m+1 in KEEP_CHILD:
        F = phase['given_gap'].pop(m+1)
    else:
        F = fresh_zero_flag(b, q)
        consume_flag(b, F, phase['incoming_gap'].pop(m+1))
    b.cswap(F, q, p)
    if not reverse:
        for v, top in zip(payloads, tops):
            b.cswap(F, v[-1], top)
    qi = quotient_inverse(b, p, g, F, current, child)
    if reverse:
        mask = phase['q'].pop(m); b.cz(qi, mask); b.free(mask)
    if not reverse:
        for v in payloads:
            scale(b, v[-1], q, qi, True)
        masked_products(b, F, payloads, c, tops)
    else:
        masked_products(b, F, payloads, c, tops)
        for v in payloads:
            scale(b, v[-1], q, qi, False)
    mask = b.alloc_bits(12)
    b.hmr(qi, mask); b.free(qi)
    if reverse:
        close_quotient_phase(b, p, g, F, current, child, mask); b.free(mask)
    else:
        phase['q'][m] = mask
    if reverse:
        for v, top in zip(payloads, tops):
            b.cswap(F, v[-1], top)
    b.cswap(F, q, p)
    if reverse and m+1 not in KEEP_CHILD:
        phase['return_mask'][m+1] = hold_flag(b, F)
    else:
        phase['returned_gap'][m+1] = F


def install_child_inverse(cv):
    cells = dict(zip(cv.__code__.co_freevars, cv.__closure__))
    short = cells['core'].cell_contents.__globals__
    scope = short['old'].direct_post.__globals__
    # The selected post dispatcher is a closure; its selected implementation
    # still reads the original private converter globals.
    if 'old_look_solve' not in scope:
        candidates = dict(zip(short['old'].direct_post.__code__.co_freevars,
                              short['old'].direct_post.__closure__))
        scope = candidates['selected'].cell_contents.__globals__
    prior_post = scope['direct_post']
    scope.update(prior_q_post=scope['q_post'], quotient_inverse=quotient_inverse,
                 close_quotient_phase=close_quotient_phase)
    scope['q_post'] = clone(root_child_post, scope)
    def post(b, f, g, payloads, F, H, parent, reverse=False,
             incoming=None, defer=False, phase=None):
        selected = len(f)-1 == 16 and phase['_short_monic']
        if selected:
            phase['_child_scalar_context'] = (g, F, phase['held_gap'][15])
        try:
            return prior_post(b, f, g, payloads, F, H, parent,
                              reverse, incoming, defer, phase)
        finally:
            if selected:
                del phase['_child_scalar_context']
    scope['direct_post'] = post
    return cv


def finish_reverse_gap(b, m, g, F, phase):
    if m+1 in ZERO_HANDOFF_LEVELS:
        phase.setdefault('_undo_child_flags', {})[m] = F
    else:
        clear_flag(b, g[-1], F)


def receive_reverse_gap(b, m, f, F, phase):
    if m not in ZERO_HANDOFF_LEVELS:
        return
    H = phase['_undo_child_flags'].pop(m-1)
    Z0 = b.alloc_qubits(1)[0]; b.init_and(F, H, Z0)
    clear_flag(b, f[-3], H)
    phase.setdefault('_undo_parent_zeros', {})[m] = Z0


def handed_aligned_pre(b, f, g, payloads, F, incoming, defer, Z0):
    b.cx(Z0, g[-2][0]); masks = high_full_restore(b, f, g, F)
    b.cx(Z0, g[-2][0]); pivot(b, g, F); a = g[-1]
    ai, Z = inverse_zero(b, a); b.cx(Z, Z0); b.free(Z0)
    consume(b, ai, Z, incoming)
    b.cx(Z, a[0]); b.cx(Z, ai[0])
    high_close_heads(b, f, g, ai, F, masks)
    for v in payloads: dk.shifted_product(b, g[:-1], v[-1], v[:-1], F)
    for v in payloads: scale(b, v[-1], a, ai, False)
    b.cx(Z, ai[0]); b.cx(Z, a[0]); out = erase(b, a, ai, Z, defer)
    pivot(b, g, F)
    return out


def handed_plain_pre(b, f, g, payloads, incoming, defer, Z0):
    a = g[-1]
    b.cx(Z0, a[0]); masks = full_restore(b, f, g); b.cx(Z0, a[0])
    ai, Z = inverse_zero(b, a); b.cx(Z, Z0); b.free(Z0)
    consume(b, ai, Z, incoming)
    b.cx(Z, a[0]); b.cx(Z, ai[0]); close_heads(b, f, g, ai, masks)
    for v in payloads:
        for i in range(len(g)-1): ar.mul_xor0(b, g[i], v[-1], v[i])
    for v in payloads: scale(b, v[-1], a, ai, False)
    b.cx(Z, ai[0]); b.cx(Z, a[0])
    return erase(b, a, ai, Z, defer)


def base_with_returned_zero(b, f, g, payloads, H, parent, reverse=False, phase=None):
    a = g[0]; q = f[-1]
    def first(undo, inc=None, delay=False):
        def action(ai):
            runops(b, [('s', v[0], True) for v in payloads]+[('s', q, True)], a, ai, undo)
        if not undo or 2 not in ZERO_HANDOFF_LEVELS:
            return inverse_apply(b, a, action, inc, delay)
        ai, Z = inverse_zero(b, a); consume(b, ai, Z, inc)
        b.cx(Z, a[0]); b.cx(Z, ai[0]); action(ai)
        b.cx(Z, ai[0]); b.cx(Z, a[0])
        mask = b.alloc_bits(12); b.hmr(ai, mask); b.free(ai)
        phase_inverse_for_gap(b, a, mask); b.free(mask)
        phase.setdefault('_undo_child_flags', {})[1] = Z
    def last(undo, inc=None, delay=False):
        def action(ai):
            runops(b, [('s', v[0], True) for v in payloads]+[('s', q, False)], a, ai, undo)
        return inverse_apply(b, a, action, inc, delay)
    if not reverse:
        carry = first(False, delay=True)
        q_post(b, q, payloads, H, 1, parent, phase=phase)
        phase['a'][1] = last(False, carry, True)
    else:
        carry = last(True, phase['a'].pop(1), True)
        q_post(b, q, payloads, H, 1, parent, True, phase)
        first(True, carry)


def install_undo_zeros(cv, levels=range(2,17)):
    cells = dict(zip(cv.__code__.co_freevars, cv.__closure__))
    short = cells['core'].cell_contents.__globals__
    scope = short['old'].direct_post.__globals__
    scope['ZERO_HANDOFF_LEVELS'] = frozenset(levels)
    scope['phase_inverse_for_gap'] = short['phase_inverse34']
    for function in (finish_reverse_gap, receive_reverse_gap,
                     handed_aligned_pre, handed_plain_pre, base_with_returned_zero):
        scope[function.__name__] = clone(function, scope)
    for name, newname in [('look_solve', 'handoff_direct_solve'),
                          ('old_look_solve', 'handoff_generic_solve')]:
        source = inspect.getsource(scope[name])
        needle = 'if reverse:clear_flag(b,g[-1],F)'
        assert source.count(needle) == 1
        source = source.replace(needle, 'if reverse:finish_reverse_gap(b,m,g,F,phase)')
        if name == 'look_solve':
            needle = " else:F=phase['returned_gap'].pop(m)\n aligned(b,f,g,F)"
            replacement = " else:F=phase['returned_gap'].pop(m)\n if reverse:receive_reverse_gap(b,m,f,F,phase)\n aligned(b,f,g,F)"
            call = 'direct_pre(b,f,g,payloads,F,True,incoming=carry)'
            newcall = "direct_pre(b,f,g,payloads,F,True,incoming=carry,handoff_zero=phase.get('_undo_parent_zeros',{}).pop(m,None))"
        else:
            needle = "    else:F=phase['returned_gap'].pop(m)\n    canonical_permute(b,f,g,F,True)"
            replacement = "    else:F=phase['returned_gap'].pop(m)\n    if reverse:receive_reverse_gap(b,m,f,F,phase)\n    canonical_permute(b,f,g,F,True)"
            call = 'pre(b,f,g,payloads,True,incoming=carry)'
            newcall = "pre(b,f,g,payloads,True,incoming=carry,handoff_zero=phase.get('_undo_parent_zeros',{}).pop(m,None))"
        assert source.count(needle) == source.count(call) == 1
        source = source.replace(needle, replacement).replace(call, newcall)
        source = source.replace('def look_solve(', 'def '+newname+'(', 1)
        exec(compile(source, __file__, 'exec'), scope)
        scope[name] = scope[newname]
    original, plain_original = scope['direct_pre'], scope['pre']
    handed, plain_handed = scope['handed_aligned_pre'], scope['handed_plain_pre']
    def direct_pre(b, f, g, payloads, F, undo=False, incoming=None,
                   defer=False, handoff_zero=None):
        if handoff_zero is None:
            return original(b, f, g, payloads, F, undo, incoming, defer)
        assert undo
        return handed(b, f, g, payloads, F, incoming, defer, handoff_zero)
    def pre(b, f, g, payloads, undo=False, incoming=None, defer=False, handoff_zero=None):
        if handoff_zero is None:
            return plain_original(b, f, g, payloads, undo, incoming, defer)
        assert undo
        return plain_handed(b, f, g, payloads, incoming, defer, handoff_zero)
    scope['direct_pre'] = direct_pre; scope['pre'] = pre
    scope['base_case'] = scope['base_with_returned_zero']
    short['old'].look_solve = scope['look_solve']
    return cv


def base_with_fused_zero(b, f, g, payloads, H, parent, reverse=False, phase=None):
    a = g[0]; q = f[-1]
    def first(undo, inc=None, delay=False):
        def action(ai):
            runops(b, [('s', v[0], True) for v in payloads]+[('s', q, True)], a, ai, undo)
        if not undo:
            return inverse_apply(b, a, action, inc, delay)
        ai, Z = inverse_zero(b, a); consume(b, ai, Z, inc)
        b.cx(Z, a[0]); b.cx(Z, ai[0]); action(ai)
        b.cx(Z, ai[0]); b.cx(Z, a[0])
        F = phase['returned_gap'][2]
        Z0 = b.alloc_qubits(1)[0]; b.init_and(F, Z, Z0)
        erase_product_zero(b, a, ai, Z)
        phase.setdefault('_undo_parent_zeros', {})[2] = Z0
        mask = b.alloc_bits(12); b.hmr(ai, mask); b.free(ai)
        phase_inverse_for_gap(b, a, mask); b.free(mask)
    def last(undo, inc=None, delay=False):
        def action(ai):
            runops(b, [('s', v[0], True) for v in payloads]+[('s', q, False)], a, ai, undo)
        return inverse_apply(b, a, action, inc, delay)
    if not reverse:
        carry = first(False, delay=True)
        q_post(b, q, payloads, H, 1, parent, phase=phase)
        phase['a'][1] = last(False, carry, True)
    else:
        carry = last(True, phase['a'].pop(1), True)
        q_post(b, q, payloads, H, 1, parent, True, phase)
        first(True, carry)


def install_base_zero(cv, keep=(2, 3)):
    cells = dict(zip(cv.__code__.co_freevars, cv.__closure__))
    short = cells['core'].cell_contents.__globals__
    scope = short['old'].direct_post.__globals__
    assert 2 in keep and 2 in scope['ZERO_HANDOFF_LEVELS']
    scope['KEEP_CHILD'] = short['KEEP_CHILD'] = frozenset(keep)
    scope['erase_product_zero'] = short['erase_product_zero']
    scope['base_case'] = clone(base_with_fused_zero, scope)
    original_receive = scope['receive_reverse_gap']
    def receive(b, m, f, F, phase):
        if m == 2:
            assert 2 in phase['_undo_parent_zeros']
            return
        original_receive(b, m, f, F, phase)
    scope['receive_reverse_gap'] = receive
    return cv


def dot_cache_core(b,A,B,reverse=False,history_scratch12=None,phase_token=None,*,monic_root=False):
    assert len(A)==len(B)==35
    phase={'a':{},'q':{},'_short_monic':bool(monic_root)} if phase_token is None else phase_token
    assert not reverse or phase_token is not None
    old.frob(b,B,2048);old.frob(b,A,2048)
    E=B[::2];O=B[1::2];u=A[1::2];w=A[:34:2];top=A[-1]
    def bez(rev):
        if phase['_short_monic']:_bez_monic(b,O,E,[u,w],rev,history_scratch12,phase)
        else:old.bez_lookahead(b,O,E,[u,w],rev,history_scratch12,phase)
    if not reverse:
        for i in range(17):old.ar.mul_xor0(b,top,O[i],w[i])
        bez(False)
        delta=b.alloc_qubits(12)
        for i in range(17):old.ar.mul_xor0(b,E[i+1],w[i],delta)
        b.cx(delta,top);phase['_top_dot']=delta
        for i in range(17):b.swap(A[2*i],A[2*i+1])
        old.hankel(b,B[1:],A[:34])
        for i in reversed(range(34)):b.swap(A[i],A[i+1])
    else:
        for i in range(34):b.swap(A[i],A[i+1])
        # Top is outside the 34-word Hankel. Free delta before that map.
        delta=phase.pop('_top_dot');b.cx(delta,top)
        mask=b.alloc_bits(12);b.hmr(delta,mask);b.free(delta)
        old.hankel(b,B[1:],A[:34],True)
        for i in range(17):b.swap(A[2*i],A[2*i+1])
        for i in range(17):old.ar.phase_product(b,E[i+1],w[i],mask)
        b.free(mask)
        bez(True)
        for i in range(17):old.ar.mul_xor0(b,top,O[i],w[i])
    old.frob(b,A,2);old.frob(b,B,2)
    if reverse:assert not phase['a'] and not phase['q']
    return phase if not reverse else None


@lru_cache(None)
def restricted_tensor16(ar):
    k,nx,width,extension=3,2,4,3
    f,sub=ar.field(12),ar.field(width)
    def product(a,b):
        out=[0]*(len(a)+len(b)-1)
        for i,x in enumerate(a):
            for j,y in enumerate(b):out[i+j]^=sub.mul(x,y)
        return out
    def remainder(a,p):
        out=list(a)
        for i in range(len(out)-len(p),-1,-1):
            c=out[i+len(p)-1]
            for j,v in enumerate(p):out[i+j]^=sub.mul(c,v)
        return (out+[0]*(len(p)-1))[:len(p)-1]
    def evaluate(a,x):
        out=0
        for c in reversed(a):out=sub.mul(out,x)^c
        return out
    def pack(a):return sum(c<<(width*i) for i,c in enumerate(a))
    def unpack(value,n):return [(value>>(width*i))&15 for i in range(n)]
    generator=f.pow(f.primitive_element,273)
    def binary_eval(p,x):
        out=0
        for i in reversed(range(width+1)):out=f.mul(out,x)^((p>>i)&1)
        return out
    root=next(f.pow(generator,i) for i in range(1,16)
              if binary_eval(sub.modulus,f.pow(generator,i))==0)
    embed=[f.pow(root,i) for i in range(width)]
    alpha=f.primitive_element
    to=ar.inverse_columns([f.mul(value,f.pow(alpha,j)) for j in range(extension) for value in embed])
    p=unpack(ar.apply(to,f.pow(alpha,extension)),extension)+[1]
    modulus=[1]
    for _ in range(k):modulus=product(modulus,p)
    theta=[0,1]
    for _ in range(12):theta=remainder(product(theta,theta),modulus)
    powers=[[1],theta,remainder(product(theta,theta),modulus)]
    test=[0]*(extension*k)
    power=[1]
    for c in p:
        for i,value in enumerate(power):test[i]^=sub.mul(c,value)
        power=remainder(product(power,theta),modulus)
    assert not any(test)
    epsilon=list(theta);epsilon[1]^=1
    epowers=[[1]]
    for _ in range(k):epowers.append(remainder(product(epowers[-1],epsilon),modulus))
    assert not any(epowers[k])
    # Frozen exact unit from the constant nullspace over this field basis.
    assert p==[2,13,7,1]
    bound=2*k;u=[0,8,1]
    assert any(remainder(u,p))
    for value in powers:assert not any(remainder(product(u,value),modulus)[bound+1:])
    columns=[]
    for degree in range(k):
        for bit in range(12):
            value=[0]*(extension*k)
            for c,theta_power in zip(unpack(to[bit],extension),powers):
                for i,a in enumerate(theta_power):value[i]^=sub.mul(c,a)
            columns.append(pack(remainder(product(value,epowers[degree]),modulus)))
    weighted=[pack(remainder(product(unpack(value,extension*k),u),modulus)) for value in columns]
    inverse=ar.inverse_columns(weighted)
    assert all(not (value>>(width*(bound+nx))) for value in weighted[:12*nx])
    left_degree=max((value.bit_length()-1)//width for value in weighted[:12*nx] if value)
    right_degree=max((value.bit_length()-1)//width for value in columns if value)
    points=list(range(left_degree+right_degree+1))
    assert len(points)<=16
    local=((1,9),(12,3),(13,10),(15,14),(4,2),(11,12),(14,1),(8,6),(6,7))
    for i in range(4):
        for j in range(4):
            check=0
            for mask,vector in local:
                if (mask>>i)&(mask>>j)&1:check^=vector
            assert check==sub.mul(1<<i,1<<j)
    terms=[]
    for point in points:
        lag,denominator=[1],1
        for other in points:
            if other==point:continue
            lag=product(lag,[other,1]);denominator=sub.mul(denominator,point^other)
        lag=[sub.mul(a,sub.invert(denominator)) for a in lag]
        left=[evaluate(unpack(value,extension*k),point) for value in weighted[:12*nx]]
        right=[evaluate(unpack(value,extension*k),point) for value in columns]
        for mask,vector in local:
            am=sum(((a&mask).bit_count()&1)<<i for i,a in enumerate(left))
            bm=sum(((a&mask).bit_count()&1)<<i for i,a in enumerate(right))
            output=ar.apply(inverse,pack(remainder([sub.mul(a,vector) for a in lag],modulus)))
            if am and bm and output:terms.append((am,bm,output))
    merged={}
    for a,b,value in terms:merged[a,b]=merged.get((a,b),0)^value
    return tuple((a,b,value) for (a,b),value in merged.items() if value)


@lru_cache(None)
def weighted_tensor64(ar, k, nx):
    if (k, nx) == (3, 2):
        return restricted_tensor16(ar)
    def product(a, b, f):
        out = [0]*(len(a)+len(b)-1)
        for i, x in enumerate(a):
            for j, y in enumerate(b): out[i+j] ^= f.mul(x, y)
        return out


    def remainder(a, p, f):
        out = list(a)
        for i in range(len(out)-len(p), -1, -1):
            c = out[i+len(p)-1]
            for j, v in enumerate(p): out[i+j] ^= f.mul(c, v)
        return (out+[0]*(len(p)-1))[:len(p)-1]


    def evaluate(a, x, f):
        out = 0
        for c in reversed(a): out = f.mul(out, x) ^ c
        return out


    def pack(a): return sum(c << (6*i) for i, c in enumerate(a))
    def unpack(x, n): return [(x >> (6*i)) & 63 for i in range(n)]
    assert 2<=k<=9 and 1<=nx<=k
    f,sub=ar.field(12),ar.field(6)
    generator=f.pow(f.primitive_element,65)
    def binary_eval(p,x):
        out=0
        for i in reversed(range(7)):out=f.mul(out,x)^((p>>i)&1)
        return out
    root=next(f.pow(generator,i) for i in range(1,64)
              if binary_eval(sub.modulus,f.pow(generator,i))==0)
    embed=[f.pow(root,i) for i in range(6)];alpha=f.primitive_element
    to=ar.inverse_columns(embed+[f.mul(v,alpha) for v in embed])
    p=unpack(ar.apply(to,f.square(alpha)),2)+[1]
    modulus=[1]
    for _ in range(k):modulus=product(modulus,p,sub)
    theta=[0,1]
    for _ in range(12):theta=remainder(product(theta,theta,sub),modulus,sub)
    epsilon=list(theta);epsilon[1]^=1
    epowers=[[1]]
    for _ in range(k):epowers.append(remainder(product(epowers[-1],epsilon,sub),modulus,sub))
    assert not any(epowers[k])
    # (Y+alpha)^k=v(Y)+alpha*u(Y), and theta*u=v modulo P^k.
    u=[0]*(k+1);v=[0]*(k+1)
    for j in range(k+1):
        if (j&k)==j:v[j],u[j]=unpack(ar.apply(to,f.pow(alpha,k-j)),2)
    assert any(remainder(u,p,sub))
    assert remainder(product(theta,u,sub),modulus,sub)==remainder(v,modulus,sub)
    columns=[]
    for degree in range(k):
        for bit in range(12):
            c0,c1=unpack(to[bit],2)
            value=[sub.mul(c1,a) for a in theta];value[0]^=c0
            columns.append(pack(remainder(product(value,epowers[degree],sub),modulus,sub)))
    weighted=[pack(remainder(product(unpack(value,2*k),u,sub),modulus,sub)) for value in columns]
    inverse=ar.inverse_columns(weighted)
    assert all(not (value>>(6*(k+nx))) for value in weighted[:12*nx])
    left_degree=max((value.bit_length()-1)//6 for value in weighted[:12*nx] if value)
    right_degree=max((value.bit_length()-1)//6 for value in columns if value)
    points=list(range(left_degree+right_degree+1));terms=[]
    assert len(points)<=64
    for point in points:
        lag,denominator=[1],1
        for other in points:
            if other==point:continue
            lag=product(lag,[other,1],sub);denominator=sub.mul(denominator,point^other)
        lag=[sub.mul(a,sub.invert(denominator)) for a in lag]
        left=[evaluate(unpack(value,2*k),point,sub) for value in weighted[:12*nx]]
        right=[evaluate(unpack(value,2*k),point,sub) for value in columns]
        for mask,vector in ar.tensor(6):
            am=sum(((a&mask).bit_count()&1)<<i for i,a in enumerate(left))
            bm=sum(((a&mask).bit_count()&1)<<i for i,a in enumerate(right))
            poly=[sub.mul(a,vector) for a in lag]
            output=ar.apply(inverse,pack(remainder(poly,modulus,sub)))
            if am and bm and output:terms.append((am,bm,output))
    merged={}
    for a,b,value in terms:merged[a,b]=merged.get((a,b),0)^value
    return tuple((a,b,value) for (a,b),value in merged.items() if value)


def install_weighted_hankel(reference, cv, maximum=8, low_lengths=(3, 4)):
    ar, k = reference.ar, reference.k
    flat = lambda words: [bit for word in words for bit in word]
    tensor = lambda degree, sources: weighted_tensor64(ar, degree, sources)

    def accumulate(b, x, q, out, terms):
        assert len(set(map(str, x+q+out))) == len(x)+len(q)+len(out)
        for am, bm, vector in terms:
            ix, iy, iz = [list(ar.bits(v)) for v in (am, bm, vector)]
            p, r, t = ix[0], iy[0], iz[0]
            for i in ix[1:]: b.cx(x[i], x[p])
            for i in iy[1:]: b.cx(q[i], q[r])
            for i in iz[1:]: b.cx(out[t], out[i])
            b.ccx(x[p], q[r], out[t])
            for i in reversed(iz[1:]): b.cx(out[t], out[i])
            for i in reversed(iy[1:]): b.cx(q[i], q[r])
            for i in reversed(ix[1:]): b.cx(x[i], x[p])

    def erase_copies(b, q, x, copies):
        masks = [b.alloc_bits(12) for _ in copies]
        for source, mask in zip(copies, masks):
            b.hmr(source, mask)
            b.free(source)
        b.cz(x[1], masks[0])
        ar.phase_product(b, q[0], x[0], masks[0])
        b.cz(x[2], masks[1])
        ar.phase_product(b, q[0], x[1], masks[1])
        ar.phase_product(b, q[1], x[0], masks[1])
        ar.linear_inplace(b, q[0], ar.square_columns(12))
        ar.phase_product(b, q[0], x[0], masks[1])
        ar.linear_inplace(b, q[0], [ar.field(12).pow(1 << i, 2048) for i in range(12)])
        for mask in masks: b.free(mask)

    cells = dict(zip(cv.__code__.co_freevars, cv.__closure__))
    scope = cells['core'].cell_contents.__globals__
    def original_tri(b, q, x, reverse=False):
        assert not reverse and 2 <= len(x) <= 4
        if len(x) == 2:
            return ar.mul_xor0(b, q[0], x[0], x[1])
        return hankel_direct(b, q, x)

    @lru_cache(None)
    def partition(n):
        if n == 1: return 0, None
        leaves = {2: 42, 3: 99, 4: 153, 5: 42+len(tensor(4, 3))}
        if 6 <= n <= maximum:
            leaves[n] = partition(n-3)[0]+len(tensor(n-1, 3))
        choices = [(leaves[n], None)] if n in leaves else []
        for left in range(1, n):
            choices.append((partition(left)[0]+partition(n-left)[0]+42*(n-1), left))
        return min(choices, key=lambda pair: pair[0])

    def direct(b, q, x):
        n = len(x)
        if n == 5:
            ar.mul_xor0(b, q[0], x[3], x[4])
        else:
            tri(b, q[:n-4], x[3:])
        copies = [b.alloc_qubits(12) for _ in range(2)]
        for source, target in zip(x[1:3], copies): b.cx(source, target)
        accumulate(b, flat([x[0]]+copies), flat(q[:n-1]), flat(x[1:]), tensor(n-1, 3))
        erase_copies(b, q, x, copies)

    def tri(b, q, x, reverse=False):
        assert not reverse
        n = len(x)
        if n == 1: return
        _, left = partition(n)
        if left is None:
            if n >= 5: return direct(b, q, x)
            return original_tri(b, q, x)
        right = n-left
        tri(b, q[:right-1], x[left:])
        for ac, bc, tc in k.cross_terms(left, right):
            k.rank_update(b, x[:left], ac, q[:n-1], bc, x[left:], tc)
        tri(b, q[:left-1], x[:left])

    def hankel(b, B, A, reverse=False):
        if reverse: return reference.hankel(b, B, A, True)
        return reference.clone(k.hankel, dict(vars(k), tri=tri))(b, B, A)
    scope['old'].hankel = hankel
    direct_scope = scope['old'].direct_post.__globals__
    prior = direct_scope['convolution_xor']

    def convolution(b, x, y, out, reverse=False):
        degree = len(out)
        if degree in low_lengths and len(x) == degree and len(y) == 2:
            return accumulate(b, flat(y), flat(x), flat(out), tensor(degree, 2))
        return prior(b, x, y, out, reverse)
    direct_scope['convolution_xor'] = convolution
    return cv


def install_dot_cache(cv):
    cells = dict(zip(cv.__code__.co_freevars, cv.__closure__))
    short = cells['core'].cell_contents.__globals__
    cells['core'].cell_contents = clone(dot_cache_core, short)
    reference = SimpleNamespace(ar=ar, k=k, hankel=hankel, clone=clone)
    return install_weighted_hankel(reference, cv)


convert_safe = install_dot_cache(install_base_zero(install_undo_zeros(install_child_inverse(install_retained_gaps(make_converter())))))
baseline = SimpleNamespace(**dict(vars(base.ref.baseline), scan=scan))
decode = clone(base.decode, dict(base.decode.__globals__,
                               convert_safe=convert_safe, baseline=baseline))


def make_prefix_boundary(original):
    env=original.__globals__
    folds=env['folds'];sg=folds.sg['absorb'].__globals__
    old,dv=sg['old'],sg['dv']
    c,kap=env['cs'][1],env['ks'][1]
    def synthesis():
        source=inspect.getsource(original)
        needle='    for i in reversed(range(1,34)):\n        aa,bb=A,B\n'
        assert source.count(needle)==1
        source=source.replace(needle,'    for i in reversed(range(2,34)):\n        aa,bb=A,B\n')
        needle='    b.x(border[0]);b.free(border);C=B+[r]\n'
        assert source.count(needle)==1
        source=source.replace(needle,'    C=A+[r];D=B+heads[1]\n')
        needle="        folds.ug['reclaim'](b,[border]);b.x(border[0])\n"
        assert source.count(needle)==1
        source=source.replace(needle,needle+'        ar.mul_xor0(b,heads[1][1],r,border)\n')
        needle='    return C,A,undo\n'
        assert source.count(needle)==1
        source=source.replace(needle,'    return C,D,border,undo\n')
        scope=dict(original.__globals__)
        exec(compile(source,__file__,'exec'),scope)
        return scope['synthesize']


    def materialize(b,A,D,prefix):
        low=A[:-1];Q=A[-1];B=D[:-2];head=D[-2:]
        value=old.eval_implicit(b,low,Q,c)
        F=dv.zero_flag(b,value)
        old.eval_implicit(b,low,Q,c,True)
        spare=[b.alloc_qubits(12),b.alloc_qubits(12)]
        b.cx(B[-2],spare[0]);b.cx(B[-1],spare[0]);b.cx(B[-1],spare[1])
        b.gf2_iadd(kap,target=spare[0]);b.x(spare[1][0])
        sg['q_times_low'](b,B,kap)
        b.cx(F,low[0][0])
        # Full product degree is at most 35. Its leading coefficient is
        # head[1]*Q = prefix+1, so only 35 finite evaluations are needed.
        targets=B+spare;n=len(targets)
        V,W=k.vandermonde(n);field=ar.field(12)
        for t in range(n):
            old.rank_affine(b,head,[1,t],A,V[t][:len(A)],
                                 targets,[W[j][t] for j in range(n)])
        for j in range(n):
            co=0
            for t in range(n):co^=field.mul(W[j][t],field.pow(t,n))
            if j==n-2:co^=kap
            if j==n-1:co^=1
            if co:
                k.cx(b,prefix,targets[j],co)
                b.gf2_iadd(co,target=targets[j])
        b.cx(F,low[0][0])
        for bit in ar.bits(kap):b.cx(F,spare[0][bit])
        b.cx(F,spare[1][0])
        pm=b.alloc_bits(12);b.hmr(prefix,pm);b.free(prefix)
        b.z(pm[0]);ar.phase_product(b,head[1],Q,pm);b.free(pm)
        hm=b.alloc_bits(24);b.hmr(head[0]+head[1],hm)
        for source,new in zip(head,spare):b.swap(source,new);b.free(new)
        fm=b.alloc_bits(1);b.hmr(F,fm[0]);b.free(F)
        return hm,fm

    return synthesis(),materialize


def install_factorized_boundary(reference_decode):
    from exp.decoder.common import ar
    from exp.convert import kernels as k
    from exp.noscratch.schedules import norm_xor_noscratch
    from exp.mul99.schedules import multiply_forward99
    from exp.arithmetic.division import phase_product24,zero_flag
    from exp.inverse19_joint.kernel import inverse_initialized
    from exp.fold_cached_norm.phase34 import phase_inverse34

    original=reference_decode.__globals__['synthesize']
    env=original.__globals__
    folds=env['folds']
    sg=folds.sg['absorb'].__globals__
    old,dv=sg['old'],sg['dv']
    c,kap=env['cs'][1],env['ks'][1]
    K=sg['K']


    synthesize, materialize = make_prefix_boundary(original)

    def divide_cached(b,x,y,N,F,fm,after):
        'Divide by clipped y with its raw norm already held; close all signs.'
        b.cx(F,y[0]);b.cx(F,N[0])
        b.cx(y[12:],y[:12])
        oldmask=multiply_forward99(b,x,y,K)
        b.cx(y[12:],y[:12])
        ai=inverse_initialized(b,N)
        for offset in (0,12):
            part=x[offset:offset+12];out=b.alloc_qubits(12)
            ar.mul_xor0(b,part,ai,out)
            ar.erase_product(b,out,N,part)
            b.swap(part,out);b.free(out)
        phase_product24(b,x,y,oldmask,K);b.free(oldmask)
        b.cx(F,y[0]);b.cx(F,N[0])
        after()
        mask=b.alloc_bits(1);b.hmr(F,mask[0]);b.free(F)
        b.cx(fm[0],mask[0]);b.free(fm);b.z(mask[0])
        pm=b.alloc_bits(12);b.bit_store(pm,False);b.cx(mask[0],pm[0])
        ar.phase_product(b,N,ai,pm);b.free(pm);b.free(mask)
        im=b.alloc_bits(12);b.hmr(ai,im);b.free(ai)
        phase_inverse34(b,N,im,zero_mask=im[0]);b.free(im)
        ar._erase_norm(b,y,N,K);b.free(N)


    def dematerialize_cached(b,A,D,token):
        head=D[-2:];B=D[:-2];low=A[:-1];Q=A[-1]
        g=folds.ug['absorb'].__globals__
        g['R_to_tops'](b,head,B,c,True)
        v=g['epow'](c,len(B)+2);co=[v&4095,v>>12]
        one=[True]+[False]*11
        old.add_alias(b,one,head,co)
        value=old.eval_implicit(b,low,Q,c)
        N=b.alloc_qubits(12);norm_xor_noscratch(b,value,N,K)
        F=zero_flag(b,N)
        hm,fm=token
        old.controlled_linear_xor(b,F,one,head,co)
        def after():
            k.cx(b,head[1],head[0],c)
            old.eval_implicit(b,low,Q,c,True)
            b.cx(F,low[0][0]);g['low_product'](b,head,low,B);b.cx(F,low[0][0])
            g['q_times_low'](b,B,kap,True)
            old.eval_implicit(b,low,Q,c)
        divide_cached(b,head[0]+head[1],value,N,F,fm,after)
        b.cz(head[0]+head[1],hm);b.free(hm)
        old.eval_implicit(b,low,Q,c,True)


    def make_decoder():
        g=reference_decode.__globals__
        undo_materialize=dematerialize_cached
        def decode(b,S,E):
            with b.mark('mask_projection'):mt=g['baseline'].project(b,S,E)
            with b.mark('initial'):g['linear_words'](b,S,g['matrix'])
            with b.mark('extract'):et=g['extraction'](b,S)
            with b.mark('synthesis'):A,B,prefix,undo=synthesize(b,S,et['pole'])
            with b.mark('materialize_boundary'):ft=materialize(b,A,B,prefix)
            with b.mark('convert'):ct=g['convert_safe'](b,A,B,monic_root=True)
            with b.mark('scan'):g['baseline'].scan(b,A,B,E,skip_points=g['baseline'].SELECTED,node_polynomial=g['Pscan'])
            with b.mark('unconvert'):g['convert_safe'](b,A,B,True,phase_token=ct)
            with b.mark('dematerialize_boundary'):undo_materialize(b,A,B,ft)
            with b.mark('unsynthesis'):undo()
            with b.mark('unextract'):g['extraction'](b,S,True,et)
            with b.mark('uninitial'):g['linear_words'](b,S,g['matrix'],True)
            with b.mark('restore_masks'):g['baseline'].restore(b,E,mt)
        return decode


    return make_decoder()


decode = install_factorized_boundary(decode)
