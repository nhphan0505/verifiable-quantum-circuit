"""DQI survey: exact arithmetic and phase composition on the supplied decoder.

Keeps the original extraction threshold, every original chart flag, and the
original conversion gap schedule.  All replacements are exact on their
stated APIs, including zero inputs and every measurement outcome.  The
whole decoder therefore inherits the base's exceptional-input domain.

New components: a shared Frobenius-product tensor, exact terminal gauge
phase, 4-AND GF64 scalar phases, 32-T GF4096 scalar phase, and initialized
18-T GF64 inversion with quadratic zero-flag erasure.

Sources: Bartoli--Zini--Zullo arXiv:2201.08242; Calik--Sonmez Turan--Peralta
DOI10.1007/s12095-018-0297-2; Soeken arXiv:2005.01778. Finite-size schedules
and the SAT quadratic-output phase are derived and checked in this survey.
This file depends only on unchanged files supplied in decoderkit-2.
"""
from pathlib import Path
from functools import lru_cache
from contextlib import contextmanager
from types import CodeType, FunctionType, ModuleType, SimpleNamespace, CellType
import sys

ROOT = Path(__file__).resolve().parents[3] / "playbook/kit/decoder"
DECODER = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT.parent)]
from final_decoder import decode as core
from final_decoder.decode import *
from exp.mul99.kernels import tensor99_extension
from exp.arithmetic.field import (bits, field, tower, linear_inplace,
                                  inverse_columns, apply)
from exp.arithmetic.lowwidth import classical_transpose
from exp.phase24_tradeoff.phase6small import classical_equal
from exp.inverse_search.inverse20 import expose_pair
from exp.inverse_search import inverse20 as ref
from exp.inverse_search import inverse20_iso as iso
from exp.inverse19_joint import kernel as joint
from exp.inverse12_escape import zero1
from exp.jet24.pro_jet import (W14_JOINT18, TO6, FROM6,
                               inverse6_joint18_12extra)
from exp.mul99.phase36 import phase_classical_parity
from exp.noscratch.schedules import norm_xor_noscratch
from exp.noscratch.kernels import mul_xor_noscratch
from exp.fold_cached_norm.phase34 import phase_inverse34 as old12
from exp.phase24_tradeoff.phase6small import phase_inverse6_classical6 as old6
from exp.arithmetic.lowwidth import phase_inverse_generic6 as old_generic6

ar, emul, einv = core.ar, core.emul, core.einv


PAIR4 = ((1, 7, 140), (13, 1, 191), (12, 8, 45), (5, 6, 82),
         (4, 3, 17), (6, 14, 123), (11, 9, 55), (2, 4, 249),
         (7, 5, 234), (9, 2, 99), (8, 12, 182), (3, 11, 255))


EVAL = (1, 8, 7, 6, 7, 0, 9, 4, 0, 0, 8, 13,
        4, 11, 9, 4, 5, 8, 9, 2, 2, 6, 12, 14)


OUT = (5733313, 3867560, 5497562, 4112984)


def pull(mask, columns):
    return sum(((mask & col).bit_count() & 1) << i
               for i, col in enumerate(columns))


@lru_cache(None)
def joint_tensor(c):
    sq = [emul(1 << i, 1 << i) for i in range(24)]
    hc = [emul(c, 1 << i) ^ ((1 << i) >> 12) for i in range(24)]
    m99 = tensor99_extension(2048)
    if c:
        # EVAL(lam*H)=EVAL(c*H+h), EVAL(mu*D)^2=EVAL(D^2).
        lam, mu = c ^ 10905896, 7455554
        lc = [emul(lam, 1 << i) for i in range(24)]
        mc = [emul(mu, 1 << i) for i in range(24)]
        xc = [ar.apply(EVAL, z) for z in hc]
        yc = [ar.apply(EVAL, z) for z in mc]
        assert [ar.apply(EVAL, z) for z in lc] == xc
        assert [ar.field(4).square(z) for z in yc] == [ar.apply(EVAL, z) for z in sq]
        scale = einv(emul(lam, mu))
        out1 = [emul(scale, z) for z in OUT]
        terms = [(pull(u, xc), pull(v, yc),
                  ar.apply(out1, w & 15) | (ar.apply(OUT, w >> 4) << 24))
                 for u, v, w in PAIR4]
        for mask, value in m99[9:]:
            terms.append((pull(mask, lc), pull(mask, mc), emul(scale, value)))
            terms.append((pull(mask, hc), pull(mask, sq), value << 24))
    else:
        # Align one product term with the GF12-by-GF24 scalar product.
        lam, mu = 6520244, 6404392
        lc = [emul(lam, 1 << i) for i in range(24)]
        mc = [emul(mu, 1 << i) for i in range(24)]
        scale = einv(emul(lam, mu))
        terms = [(pull(m, lc), pull(m, mc), emul(scale, w)) for m, w in m99]
        for off in (0, 12):
            ds = [(v >> off) & 4095 for v in sq]
            terms.extend((m << 12, pull(m, ds), w << (24 + off))
                         for m, w in ar.tensor(12))
    combined = {}
    for u, v, w in terms:
        combined[u, v] = combined.get((u, v), 0) ^ w
    result = tuple((u, v, w) for (u, v), w in combined.items() if w)
    assert len(result) == (192 if c else 182)
    return result


def accumulator(b, x, y, z, terms):
    """Accumulate a binary tensor with no scratch, restoring both inputs."""
    for u, v, w in terms:
        ix, iy, iz = [list(ar.bits(mask)) for mask in (u, v, w)]
        a, c, t = ix[0], iy[0], iz[0]
        for i in ix[1:]: b.cx(x[i], x[a])
        for i in iy[1:]: b.cx(y[i], y[c])
        for i in iz[1:]: b.cx(z[t], z[i])
        b.ccx(x[a], y[c], z[t])
        for i in reversed(iz[1:]): b.cx(z[t], z[i])
        for i in reversed(iy[1:]): b.cx(y[i], y[c])
        for i in reversed(ix[1:]): b.cx(x[i], x[a])


def chain_step(b, head, N, D, L, q, ct, c, reverse=False, first=False):
    if first:
        return core.external_chain_step(b, head, N, D, L, q, ct, c, reverse, first)
    if reverse:
        core.scalepair(b, N, core.inv(q))
        b.swap(N, D)
        core.scalepair(b, L, core.inv(q))
    a, h = head
    core.cx(b, h, a, ct)
    accumulator(b, core.combine(head), D, list(N) + list(L), joint_tensor(c))
    core.cx(b, h, a, ct)
    if not reverse:
        core.scalepair(b, L, q)
        b.swap(N, D)
        core.scalepair(b, N, q)

def clone(fn,scope):
    out=FunctionType(fn.__code__,scope,fn.__name__,fn.__defaults__,fn.__closure__)
    out.__kwdefaults__=fn.__kwdefaults__
    return out


def dirty_zero_phase(b, x, dirty):
    """Exact zero phase, one clean bit and len(x)-3 borrowed dirty bits."""
    work = list(b.alloc_qubits(1)) + list(dirty[:len(x)-3])
    b.x(x)
    for first in (True, False):
        if first: b.init_and(x[0], x[1], work[0])
        start = 1 if first else 2
        for j in range(start, len(work)):
            b.ccx(work[j-1], x[j+1], work[j])
        b.cz(work[-1], x[-1])
        for j in reversed(range(start, len(work))):
            b.ccx(work[j-1], x[j+1], work[j])
        if first: b.del_and(x[0], x[1], work[0])
    b.x(x)
    b.free(work[0])


def direct_gauge_narrow(b, D, norm_pair, gauge_mask):
    """Recover the gauge and close both norm histories with 48 private bits."""
    reciprocal, direct = norm_pair
    ar._erase_norm(b, D, reciprocal, K)
    b.free(reciprocal)
    b.cx(D[12:], D[:12])
    oldmask = b.alloc_bits(24)
    for off in (0, 12):
        half = D[off:off+12]
        out = b.alloc_qubits(12)
        mul_xor_noscratch(b, half, direct, out)
        b.hmr(half, oldmask[off:off+12])
        b.swap(half, out)
        b.free(out)
    b.cz(D, gauge_mask)
    b.free(gauge_mask)
    inverse_mask = inverse_stream_noscratch(b, direct)
    ar._phase_norm(b, D, inverse_mask, K)
    b.free(inverse_mask)
    ar.phase_product(b, D[:12], direct, oldmask[:12])
    ar.phase_product(b, D[12:], direct, oldmask[12:])
    b.free(oldmask)
    norm = b.alloc_qubits(12)
    norm_xor_noscratch(b, D, norm, K)
    m = b.alloc_bits(12)
    b.hmr(direct, m)
    b.free(direct)
    phase_inverse36_pivot(b, norm, m)
    b.free(m)
    ar._erase_norm(b, D, norm, K)
    b.free(norm)
    mask = b.alloc_bits(24)
    b.hmr(D, mask)
    b.free(D)
    return mask


def head_phase(b, head, factor, mask, ct):
    a, h = head
    cx(b, h, a, ct)
    phase_product24(b, combine(head), factor, mask, K)
    cx(b, h, a, ct)


def terminal_two_phase(b, N, heads, params, ct, mask, pole, dirty):
    """Close the last two scalar replay steps and the pole flag exactly."""
    stop = len(heads)-2
    D = b.alloc_qubits(24)
    b.x(D[0])
    for i in range(stop):
        external_scalar_step(b, heads[i], N, D, params[i][0], ct, first=i == 0)
    W = b.alloc_qubits(24)
    b.cx(N, W)
    external_mul_head(b, heads[-2], D, W, ct)
    scalepair(b, D, params[-2][0])
    b.cz(D, mask)
    scalepair(b, D, inv(params[-2][0]))
    head_phase(b, heads[-1], W, mask, ct)
    scalepair(b, W, params[-1][0])
    b.ccz(pole, W, mask)
    scalepair(b, W, inv(params[-1][0]))
    fm = b.alloc_bits(1)
    b.hmr(pole, fm[0])
    b.free(pole)
    b.push_condition(fm[0])
    scalepair(b, D, params[-2][0])
    external_mul_head(b, heads[-1], W, D, ct)
    dirty_zero_phase(b, D, dirty)
    external_mul_head(b, heads[-1], W, D, ct)
    scalepair(b, D, inv(params[-2][0]))
    b.pop_condition()
    b.free(fm)
    wm = b.alloc_bits(24)
    b.hmr(W, wm)
    b.free(W)
    b.cz(N, wm)
    head_phase(b, heads[-2], D, wm, ct)
    b.free(wm)
    b.free(mask)
    for i in reversed(range(stop)):
        external_scalar_step(b, heads[i], N, D, params[i][0], ct, True, first=i == 0)
    b.x(D[0])
    b.free(D)


def external_node_chain(b,words,gi,reverse=False,token=None,normalizer=None):
    g=groups[gi];N=combine(words[g['word']:g['word']+2]);L=combine(words[g['word']+2:g['word']+4])
    heads=[words[2*i:2*i+2]for i in range(2*gi)]
    params=[];c=0
    for i in range(2*gi):
        q=ks[i]^g['kap'];assert q
        params.append((q,c));c^=inv(q)
    assert c==0
    if not reverse:
        D=b.alloc_qubits(24);b.x(D[0])
        for i,(head,(q,c))in enumerate(zip(heads,params)):
            external_chain_step(b,head,N,D,L,q,g['c'],c,first=i==0)
        pole=zero_flag(b,D);b.cswap(pole,N,D)
        norm=external_normalize_paired(b,N,D,L)
        gauge=b.alloc_bits(24);b.hmr(D,gauge);b.free(D)
        return dict(pole=pole,gauge=gauge,norm=norm)
    pole=token['pole'];D=b.alloc_qubits(24);b.x(D[0]);b.cx(pole,N[0]);b.cx(pole,D[0])
    for head,(q,c)in reversed(list(zip(heads,params))[1:]):external_chain_step(b,head,N,D,L,q,g['c'],c,True)
    q0=params[0][0];scalepair(b,N,inv(q0));b.swap(N,D);scalepair(b,L,inv(q0))
    norm=external_normalize_paired(b,N,D,L,True,token['norm'])
    a,h=heads[0];cx(b,h,a,g['c']);b.cx(combine(heads[0]),N);cx(b,h,a,g['c']);b.cx(h,L[:12])
    mask=direct_gauge_narrow(b,D,norm,token['gauge'])
    terminal_two_phase(b,N,heads,params,g['c'],mask,pole,L)


def extraction(b,words,reverse=False,token=None):
    heads=[words[2*i:2*i+2]for i in range(34)];N,L=words[-2:]
    if not reverse:
        ext=external_extraction(b,words);D=b.alloc_qubits(12);b.x(D[0])
        first_step(b,heads[0],N,D,L,ks[0])
        for head,kap,c in zip(heads[1:],ks[1:],corrections[1:]):step(b,head,N,D,L,kap,c)
        pole=b.alloc_qubits(1)[0];guarded.zero_toggle(b,D,pole);b.cswap(pole,N,D)
        norm=normal_form(b,N,D,L);ci=controlled_inverse(b,L,pole)
        gauge=b.alloc_bits(12);b.hmr(D,gauge);b.free(D)
        return dict(external=ext,pole=pole,normalization=norm,gauge_mask=gauge,chart_inverse=ci)
    pole=token['pole'];controlled_inverse(b,L,pole,True,token['chart_inverse'])
    D=b.alloc_qubits(12);b.x(D[0]);b.cx(pole,N[0]);b.cx(pole,D[0])
    for head,kap,c in reversed(list(zip(heads,ks,corrections))[1:]):step(b,head,N,D,L,kap,c,True)
    scale(b,N,inv(ks[0]));b.swap(N,D);scale(b,L,inv(ks[0]))
    extra_z_mask=normal_form(b,N,D,L)
    b.cx(heads[0][0],N);b.cx(heads[0][1],L)
    b.cz(D,token['normalization']);b.free(token['normalization'])
    inverse_mask=b.alloc_bits(12);b.hmr(D,inverse_mask);b.free(D)
    z_mask=token['gauge_mask'];b.cx(extra_z_mask,z_mask);b.free(extra_z_mask)
    D=b.alloc_qubits(12);b.x(D[0]);scalar_step(b,heads[0],N,D,ks[0],first=True)
    for head,kap in zip(heads[1:],ks[1:]):scalar_step(b,head,N,D,kap)
    b.cswap(pole,N,D);b.cz(D,z_mask);b.free(z_mask)
    phase_inverse34(b,D,inverse_mask);b.free(inverse_mask);b.cswap(pole,N,D)
    guarded.zero_toggle(b,D,pole)
    for head,kap in reversed(list(zip(heads[1:],ks[1:]))):scalar_step(b,head,N,D,kap,True)
    scalar_step(b,heads[0],N,D,ks[0],True,first=True)
    b.x(D[0]);b.free(D);b.free(pole);external_extraction(b,words,True,token['external'])

def _mask_scalars():
    out = {}
    f = field(6)
    for s in range(1, 64):
        si = f.invert(s)
        mask = sum((f.mul(si, 1 << i) & 1) << i for i in range(6))
        assert mask and mask not in out
        out[mask] = s
    return out


def _fixed_phase(b, x, gates, output):
    """Phase one affine-XOR-AND circuit; final AND is a free CZ."""
    count = len(gates) - 1
    a = b.alloc_qubits(count)
    source = list(x) + list(a)
    for i, (left, right) in enumerate(gates[:-1]):
        with expose_pair(b, source[:6+i], left, right) as (p, q):
            b.init_and(p, q, a[i])
    assert output >> (7 + count) == 1
    if output & 1:
        b.z(True)
    for i in bits((output >> 1) & ((1 << (6 + count))-1)):
        b.z(source[i])
    with expose_pair(b, source, *gates[-1]) as (p, q):
        b.cz(p, q)
    for i in reversed(range(count)):
        with expose_pair(b, source[:6+i], *gates[i]) as (p, q):
            b.del_and(p, q, a[i])
    b.free(a)


def _zero_phase(b, x):
    """Phase [x=0], exactly 4 T / 4 scratch for six input bits."""
    b.x(x)
    a = b.alloc_qubits(4)
    b.init_and(x[0], x[1], a[0])
    for i in range(1, 4):
        b.init_and(a[i-1], x[i+1], a[i])
    b.cz(a[3], x[5])
    for i in reversed(range(1, 4)):
        b.del_and(a[i-1], x[i+1], a[i])
    b.del_and(x[0], x[1], a[0])
    b.free(a)
    b.x(x)

SCALARS = _mask_scalars()
GATES = {1: ((23, 78), (60, 234), (15, 182), (236, 310), (552, 1137))}
OUTPUT = {1: 3373}


FORMS = ((8, 20), (38, 92), (32, 280), (414, 538))


TERMS = ((0,), (2,), (3,), (4,), (5,), (9,), (0, 1), (0, 2),
         (0, 8), (0, 9), (1, 2), (1, 3), (1, 6), (1, 7),
         (2, 5), (2, 9), (3, 7), (3, 8), (3, 9), (5, 6),
         (5, 9), (6, 7))


SCALES = {m: [field(6).mul(s, 1 << i) for i in range(6)]
          for m, s in SCALARS.items()}


UNSCALES = {m: inverse_columns(c) for m, c in SCALES.items()}


def _ordinary(b, x):
    g = b.alloc_qubits(4)
    source = list(x) + list(g)
    for i, (left, right) in enumerate(FORMS):
        with expose_pair(b, source[:6+i], left, right) as (p, q):
            b.init_and(p, q, g[i])
    for term in TERMS:
        if len(term) == 1:
            b.z(source[term[0]])
        else:
            b.cz(source[term[0]], source[term[1]])
    for i in reversed(range(4)):
        with expose_pair(b, source[:6+i], *FORMS[i]) as (p, q):
            b.del_and(p, q, g[i])
    b.free(g)


def phase_inverse6_quad4(b, x, mask, zero_mask=None):
    """Phase dot(mask,inv0(x)) + zero_mask*[x=0], <=4 T /4 scratch.

    All controls are classical.  No input is exceptional; masks and x are
    restored exactly, with del_and closing every measurement phase.
    """
    assert len(x) == len(mask) == 6
    for m in range(1, 64):
        eq = classical_equal(b, mask, m)
        b.push_condition(eq)
        linear_inplace(b, x, SCALES[m])
        if zero_mask is None:
            _ordinary(b, x)
        else:
            b.push_condition(zero_mask)
            _fixed_phase(b, x, GATES[1], OUTPUT[1])
            b.pop_condition()
            b.x(zero_mask)
            b.push_condition(zero_mask)
            _ordinary(b, x)
            b.pop_condition()
            b.x(zero_mask)
        linear_inplace(b, x, UNSCALES[m])
        b.pop_condition()
        b.free(eq)
    if zero_mask is not None:
        eq = classical_equal(b, mask, 0)
        b.push_condition(eq)
        b.push_condition(zero_mask)
        _zero_phase(b, x)
        b.pop_condition()
        b.pop_condition()
        b.free(eq)

def phase_inverse12_virtual(b, x, mask, zero_mask=None):
    # Handle types are build-time metadata, not measured quantum values.
    # Preserve the unguarded API for a quantum zero-phase coefficient.
    if zero_mask is not None and type(zero_mask) is type(x[0]):
        return phase_inverse12_virtual_nonzero(b, x, mask, zero_mask)
    active = b.alloc_bits(1)[0]
    b.bit_store(active, False)
    for bit in mask:
        b.bit_store(active, True, control=bit)
    if zero_mask is not None:
        b.bit_store(active, True, control=zero_mask)
    b.push_condition(active)
    phase_inverse12_virtual_nonzero(b, x, mask, zero_mask)
    b.pop_condition()
    b.free(active)

def phase_inverse12_virtual_nonzero(b, x, mask, zero_mask=None):
    """Same exact phase, <=32 executed T / 15 scratch.

    The quantum coefficient is exposed as a parity of the original x,
    chosen solely by classical mask bits.  No quantum mask is treated as
    classical, and no six-qubit coefficient register is allocated.
    """
    assert len(x) == len(mask) == 12
    to, frm, K = tower(12)
    linear_inplace(b, x, to)
    mt = classical_transpose(b, mask, frm)
    D = b.alloc_qubits(6)
    norm_xor_noscratch(b, x, D, K)
    linear_inplace(b, D, TO6)
    dag = W14_JOINT18
    g = b.alloc_qubits(6)
    for i, (left, right) in enumerate(dag['raw_gates']):
        with ref.expose_pair(b, D, left, right) as (p, q):
            b.init_and(p, q, g[i])
    prefix = list(D) + list(g)
    forms = ref.norm_forms(1)
    w = ref.inverse3_virtual(b, prefix, forms)
    source = prefix + list(w)
    def coefficient(vector):
        h = apply(FROM6, vector)
        co = b.alloc_bits(12)
        b.bit_store(co, False)
        for j in range(6):
            for r in bits(field(6).mul(h, 1 << j)):
                b.cx(mt[r], co[j])
                b.cx(mt[r], co[j+6])
                b.cx(mt[r+6], co[j+6])
        return co
    linear = [(e & 65535) ^ (1555 if e >> 16 & 1 else 0)
              for e in dag['outputs'][:6]]
    # Linear and constant source terms are bilinear in x and classical mask.
    for r in range(16):
        vector = sum(((e >> r) & 1) << j for j, e in enumerate(linear))
        if not vector:
            continue
        co = coefficient(vector)
        for j in range(12):
            if r == 0:
                b.cz(x[j], co[j])
            else:
                b.ccz(source[r-1], x[j], co[j])
        b.free(co)
    for i, (left, right) in enumerate(dag['gates'][1:], 1):
        vector = sum(((e >> (16+i)) & 1) << j for j, e in enumerate(dag['outputs'][:6]))
        if not vector:
            continue
        co = coefficient(vector)
        with ref.expose_pair(b, source, left, right) as (p, q):
            phase_classical_parity(b, p, q, x, co)
        b.free(co)
    if zero_mask is not None:
        b.z(zero_mask)
        for r in bits(1555 >> 1):
            b.cz(source[r], zero_mask)
        with ref.expose_pair(b, source, *dag['gates'][0]) as (p, q):
            b.ccz(p, q, zero_mask)
    wm = b.alloc_bits(3)
    b.hmr(w, wm)
    b.free(w)
    ref.phase_inverse3_virtual(b, prefix, forms, wm)
    b.free(wm)
    for i in reversed(range(6)):
        with ref.expose_pair(b, D, *dag['raw_gates'][i]) as (p, q):
            b.del_and(p, q, g[i])
    b.free(g)
    linear_inplace(b, D, FROM6)
    ar._erase_norm(b, x, D, K)
    b.free(D)
    b.free(mt)
    linear_inplace(b, x, frm)

def inverse6_init18(b,x):
    """Initialized inverse0; the zero output is erased quadratically."""
    t,F=inverse6_joint18_12extra(b,x)
    m=b.alloc_bits(1)
    b.hmr(F,m[0]);b.free(F)
    b.z(m[0])
    mask=b.alloc_bits(6);b.bit_store(mask,False)
    b.cx(m[0],mask[0])
    ar.phase_product(b,x,t,mask)
    b.free(mask);b.free(m)
    return t


def inverse_zero(b,x):
    to,frm,K=tower(12)
    linear_inplace(b,x,to)
    N=b.alloc_qubits(6)
    norm_xor_noscratch(b,x,N,K)
    t,F=inverse6_joint18_12extra(b,N)
    ar._erase_norm(b,x,N,K)
    b.free(N)
    out=b.alloc_qubits(12)
    b.cx(x[6:],x[:6])
    mul_xor_noscratch(b,x[:6],t,out[:6])
    mul_xor_noscratch(b,x[6:],t,out[6:])
    b.cx(x[6:],x[:6])
    ar._erase_norm(b,out,t,K)
    b.free(t)
    linear_inplace(b,x,frm)
    linear_inplace(b,out,frm)
    return out,F

def private_rebind(entry, replacements):
    memo = {}
    scopes = {}
    processed = set()
    def owned(filename):
        try:
            return Path(filename).resolve().is_relative_to(DECODER)
        except (TypeError, ValueError):
            return False
    def names(code):
        result = set(code.co_names)
        for value in code.co_consts:
            if isinstance(value, CodeType):
                result.update(names(value))
        return result
    def copy(value):
        key = id(value)
        if key in replacements:
            return replacements[key]
        if key in memo:
            return memo[key]
        if isinstance(value, FunctionType) and owned(value.__code__.co_filename):
            old = value.__globals__
            scope = scopes.setdefault(id(old), dict(old))
            closure = value.__closure__
            if closure:
                closure = tuple(CellType(copy(c.cell_contents)) for c in closure)
            out = FunctionType(value.__code__, scope, value.__name__, value.__defaults__, closure)
            memo[key] = out
            out.__kwdefaults__ = value.__kwdefaults__
            for name in names(value.__code__):
                token = (id(old), name)
                if token not in processed and name in old:
                    processed.add(token)
                    scope[name] = copy(old[name])
            return out
        # contextmanager decorators store the original generator in a cell.
        if isinstance(value, FunctionType) and getattr(value, '__wrapped__', None) is not None:
            wrapped = value.__wrapped__
            if isinstance(wrapped, FunctionType) and owned(wrapped.__code__.co_filename):
                out = contextmanager(copy(wrapped))
                memo[key] = out
                return out
        if isinstance(value, SimpleNamespace) or (isinstance(value, ModuleType) and owned(getattr(value, '__file__', None))):
            out = SimpleNamespace()
            memo[key] = out
            for name, item in vars(value).items():
                if name != '__builtins__':
                    setattr(out, name, copy(item))
            return out
        if isinstance(value, dict):
            out = {}
            memo[key] = out
            out.update((k, copy(v)) for k, v in value.items())
            return out
        if isinstance(value, (list, tuple)) and any(isinstance(v, (FunctionType, SimpleNamespace, dict)) for v in value):
            out = [copy(v) for v in value]
            out = tuple(out) if isinstance(value, tuple) else out
            memo[key] = out
            return out
        return value
    return copy(entry)


def initialized19(b, x, with_zero=False):
    if with_zero:
        return inverse6_joint18_12extra(b, x)
    return inverse6_init18(b, x)


def initialized_only(old):
    def wrapped(b, x, z=None, keep_norm=False):
        if z is None and not keep_norm:
            return inverse6_init18(b, x)
        return old(b, x, z, keep_norm)
    return wrapped


external_chain_step = chain_step
external_extraction = clone(core.external_extraction, globals())
_base_body = clone(core.decode, globals())
_body = private_rebind(_base_body, {
    id(old6): phase_inverse6_quad4,
    id(old_generic6): phase_inverse6_quad4,
    id(old12): phase_inverse12_virtual,
    id(zero1.inverse_zero): inverse_zero,
    id(joint.inverse_zero): inverse_zero,
    id(joint.inverse6_init19): initialized19,
    id(iso.inverse6_xor20): initialized_only(iso.inverse6_xor20),
    id(ref.inverse6_xor20): initialized_only(ref.inverse6_xor20),
})


def decode(b, S, E):
    _body(b, S, E)
