"""Readable Fusion arithmetic/compiler, consolidated from the accepted INV-51 source.

Copyright 2026 Syed Asad Ali. Apache-2.0; see LICENSE.txt and NOTICE.txt.
Definitions use component prefixes to preserve mutable arithmetic bindings and
independent carry contexts. No source strings, archive, exec, precompiled circuit
or instruction payload is embedded. tables.json holds mathematical/config data.
"""
from __future__ import annotations
from pathlib import Path
import copy, hashlib, importlib, inspect, json, sys, types
_HERE = Path(__file__).resolve().parent
_VROOT = _HERE / '_components'
_TABLES = json.loads((_HERE / 'tables.json').read_text(encoding='utf-8'))
_CACHE = {}
_INITIALIZED = set()
_PROFILE = {'calls': set(), 'modules': set()}

class _Component:
    __slots__ = ('key', 'group', 'prefix', 'name')

    def __init__(self, key, group, name):
        object.__setattr__(self, 'key', key)
        object.__setattr__(self, 'group', group)
        object.__setattr__(self, 'prefix', _PREFIXES[key, group])
        object.__setattr__(self, 'name', name)

    def __getattr__(self, name):
        if name == '__file__':
            return str(_VROOT / self.key)
        if name == '__name__':
            return self.name
        if name == '__dict__':
            return {k[len(self.prefix):]: v for k, v in globals().items() if k.startswith(self.prefix)}
        try:
            return globals()[self.prefix + name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name, value):
        globals()[self.prefix + name] = value

    def __dir__(self):
        return ['__file__', '__name__', *self.__dict__]

class _Spec:

    def __init__(self, name, path):
        self.name = name
        self.key = _key(path)
        self.group = _GROUPS.get((self.key, name), 0)
        self.loader = self
        if (self.key, self.group) not in _FACTORIES:
            raise ImportError(str(path))

    def exec_module(self, module):
        pair = (self.key, self.group)
        if pair in _INITIALIZED:
            return
        _PROFILE['modules'].add(pair)
        prefix = module.prefix
        globals()[prefix + '__file__'] = str(_VROOT / self.key)
        globals()[prefix + '__name__'] = self.name
        _FACTORIES[pair]()
        _INITIALIZED.add(pair)

def _key(path):
    try:
        return Path(path).resolve().relative_to(_VROOT).as_posix()
    except ValueError:
        return None

def _spec(name, path):
    return _Spec(name, path)

def _new_module(spec):
    pair = (spec.key, spec.group)
    if pair not in _CACHE:
        _CACHE[pair] = _Component(spec.key, spec.group, spec.name)
    return _CACHE[pair]

def _import_component(name, current, top=False):
    if name in sys.modules:
        return sys.modules[name.split('.')[0] if top else name]
    paths = [str(_VROOT / Path(current).parent), *sys.path]
    for directory in paths:
        key = _key(Path(directory) / (name.replace('.', '/') + '.py'))
        if (key, 0) in _FACTORIES:
            spec = _Spec(name, _VROOT / key)
            module = _new_module(spec)
            sys.modules[name] = module
            spec.exec_module(module)
            return module
    matches = [k for k, g in _FACTORIES if g == 0 and k.endswith('/' + name.replace('.', '/') + '.py')]
    if len(matches) == 1:
        spec = _Spec(name, _VROOT / matches[0])
        module = _new_module(spec)
        sys.modules[name] = module
        spec.exec_module(module)
        return module
    return importlib.import_module(name.split('.')[0] if top else name)

def _import_star(prefix, module):
    for name in dir(module):
        if not name.startswith('_'):
            globals()[prefix + name] = getattr(module, name)

class _DataText(str):

    def __new__(cls, value, key):
        obj = str.__new__(cls, value)
        obj.key = key
        return obj

class _DataBytes(bytes):

    def __new__(cls, value, key):
        obj = bytes.__new__(cls, value)
        obj.key = key
        return obj

def _read_text(path, *args, **kwargs):
    key = _key(path)
    if key in _TABLES:
        return _DataText(json.dumps(_TABLES[key]), key)
    if key == 'patches/PATCH_ORDER.txt':
        return _PATCH_ORDER
    return Path(path).read_text(*args, **kwargs)

def _read_bytes(path, *args, **kwargs):
    key = _key(path)
    if key in _TABLES:
        return _DataBytes(json.dumps(_TABLES[key]).encode(), key)
    if (key, 0) in _FACTORIES:
        return inspect.getsource(_FACTORIES[key, 0]).encode()
    return Path(path).read_bytes(*args, **kwargs)

def _exists(path):
    key = _key(path)
    return key in _TABLES or (key, 0) in _FACTORIES or Path(path).exists()

def _json_loads(value, *args, **kwargs):
    if isinstance(value, (_DataText, _DataBytes)):
        return copy.deepcopy(_TABLES[value.key])
    return json.loads(value, *args, **kwargs)

def run_stage(key, args):
    sys.argv = [str(_VROOT / key), *args]
    sys.path.insert(0, str(_VROOT / Path(key).parent))
    module = _new_module(_Spec('__main__', _VROOT / key))
    _Spec('__main__', _VROOT / key).exec_module(module)

def _initialize_w2core_e2():
    global _w2core_e2_CENTRES, _w2core_e2_CONTROLS, _w2core_e2_ENC, _w2core_e2_ENC_FN, _w2core_e2_E_HOLD, _w2core_e2_F_HOLD, _w2core_e2_Fraction, _w2core_e2_INTEGRATED_ROOT, _w2core_e2_MAX_EXTRA, _w2core_e2_MODULUS, _w2core_e2_P_RETIRED_STEPS, _w2core_e2_QMAX, _w2core_e2_R2_HOLDS, _w2core_e2_RESULT, _w2core_e2_RETIRE_V9, _w2core_e2_SpareProxy, _w2core_e2_THR, _w2core_e2_V10_FROM_G1, _w2core_e2__IntegratedPath, _w2core_e2___file__, _w2core_e2___name__, _w2core_e2__anf, _w2core_e2__check_domain, _w2core_e2__emit_form, _w2core_e2__erase_helpers, _w2core_e2__pair_forms, _w2core_e2__quadratic, _w2core_e2__undo, _w2core_e2_apply, _w2core_e2_fn, _w2core_e2_j, _w2core_e2_make_endpoint, _w2core_e2_pairs
    _w2core_e2_Fraction = _import_component('fractions', 'agents/composer/p/w2core_e2.py', False).Fraction
    _w2core_e2_MODULUS = 1 << 50
    _w2core_e2_CENTRES = (2, 6, 24, 0, 25)
    _w2core_e2_CONTROLS = ((0, 4), (8,), (0, 2, 4, 8), (0, 1, 2), (0, 1))
    _w2core_e2_THR = {1: (1, 2, 4, 8, 16, 3, 5, 9, 17), 2: (2, 4, 8, 16), 3: (4, 8, 3, 17), 4: (4, 8), 5: (5, 17, 6, 18, 8, 16), 6: (6, 8), 7: (8, 17), 8: (8,), 9: (9, 10)}
    _w2core_e2_E_HOLD = set(range(1, 13))
    _w2core_e2_F_HOLD = set(range(13))
    _w2core_e2_R2_HOLDS = {(11, 13): (0, 2), (10, 14): (0, 3), (9, 15): (1, 4), (7, 17): (3, 6), (6, 18): (4, 7), (5, 19): (5, 8), (1, 23): (9, 12)}
    _w2core_e2_P_RETIRED_STEPS = (0, 7)
    _w2core_e2_MAX_EXTRA = 7
    _w2core_e2_QMAX = 48

    def _w2core_e2__anf(fn):
        """ANF monomials (bitmasks over [f0,f1,f2,f3,p,s]) of a Boolean function of 6 bits."""
        table = [fn(*[x >> i & 1 for i in range(6)]) & 1 for x in range(64)]
        coeff = list(table)
        for i in range(6):
            for x in range(64):
                if x >> i & 1:
                    coeff[x] ^= coeff[x ^ 1 << i]
        terms = tuple((x for x in range(64) if coeff[x]))
        assert all((bin(t).count('1') <= 2 for t in terms))
        return terms
    _w2core_e2_ENC_FN = {0: lambda f0, f1, f2, f3, p, s: (f1 ^ f2 ^ f3 ^ p) & (s ^ f0) ^ f0, 1: lambda f0, f1, f2, f3, p, s: (f1 ^ f2 ^ f3 ^ p) & s, 2: lambda f0, f1, f2, f3, p, s: f0 & (f1 ^ p) ^ (f2 ^ f3) & s, 3: lambda f0, f1, f2, f3, p, s: (f2 ^ f3) & s, 6: lambda f0, f1, f2, f3, p, s: f0 & p ^ f3 & s, 7: lambda f0, f1, f2, f3, p, s: f3 & s}
    _w2core_e2_ENC = {j: _w2core_e2__anf(fn) for j, fn in _w2core_e2_ENC_FN.items()}

    def _w2core_e2__check_domain():
        flags = {k: k for k in range(11)}
        flags[10] = 10
        for j, fn in _w2core_e2_ENC_FN.items():
            for k in range(11):
                f = [flags[k] >> i & 1 for i in range(4)]
                p = f[1] & (f[2] ^ f[3])
                for s in (1,) if k == j + 1 else (0, 1):
                    assert fn(*f, p, s) == int(k >= j + 1) & s, (j, k, s)
    _w2core_e2__check_domain()

    def _w2core_e2_pairs(stage):
        centre = _w2core_e2_CENTRES[stage]
        return [(i, (centre - i) % 26) for i in range(26) if i < (centre - i) % 26]

    class _w2core_e2_SpareProxy:
        """Delegate to the builder; single-qubit allocations take the spare wires first."""

        def __init__(self, builder, base_count):
            self._b = builder
            self.spare = []
            self.lent = set()
            self.base = base_count
            self.extra = 0
            self.max_extra = 0

        def __getattr__(self, name):
            return getattr(self._b, name)

        def alloc_qubits(self, count):
            if count == 1 and self.spare:
                q = self.spare.pop()
                out = [q]
            else:
                out = list(self._b.alloc_qubits(count))
            self.extra += count
            self.max_extra = max(self.max_extra, self.extra)
            assert self.extra <= self.limit, ('too many extra wires', self.extra)
            assert self._b.num_allocated_qubits <= _w2core_e2_QMAX, ('endpoint width', self._b.num_allocated_qubits)
            return out

        def free(self, target):
            if self._is_qubit(target) and any((target == s for s in self.lent)):
                self.spare.append(target)
                self.extra -= 1
                return
            self._b.free(target)
            if self._is_qubit(target):
                self.extra -= 1

        def _is_qubit(self, target):
            return type(target).__name__ == 'q'
    _w2core_e2_V10_FROM_G1 = False
    _w2core_e2_RETIRE_V9 = None

    def _w2core_e2__pair_forms(b, SA, SB):
        """Make two distinct wires hold the XORs of the wire sets SA and SB, in place (CX conjugation, no new wire).
    Returns (wa, wb, ops); undo with _undo(b, ops)."""
        SA = list(dict.fromkeys(SA))
        SB = list(dict.fromkeys(SB))
        ops = []
        a = SA[0]
        for w in SA[1:]:
            b.cx(w, a)
            ops.append((w, a))
        if a in SB:
            SBc = set(SA) - {a} ^ set(SB) - {a}
            SBc.add(a)
        else:
            SBc = set(SB)
        cands = [w for w in SB if w in SBc and w != a] + [w for w in SA if w in SBc and w != a] + [w for w in SBc if w != a]
        assert cands, 'degenerate AND: both factors equal'
        bp = cands[0]
        for w in [x for x in SB + SA + [a] if x in SBc and x != bp]:
            if (w, bp) in ops:
                continue
            b.cx(w, bp)
            ops.append((w, bp))
        return (a, bp, ops)

    def _w2core_e2__undo(b, ops):
        for c, t in reversed(ops):
            b.cx(c, t)

    def _w2core_e2__erase_helpers(b, helpers):
        for h, lw, rw in reversed(helpers):
            m = b.alloc_bits(1)[0]
            b.hmr(h, m)
            b.free(h)
            wa, wb, ops = _w2core_e2__pair_forms(b, lw, rw)
            b.push_condition(m)
            b.cz(wa, wb)
            b.pop_condition()
            _w2core_e2__undo(b, ops)
            b.free(m)

    def _w2core_e2__emit_form(b, form, named, target, keep=False):
        """XOR the straight-line AND program `form` (tools/minand_sat.py schema) into the zero wire `target`.
    Factors are formed in place (CX conjugation); gates read by later gates get their own helper wire (erased at
    the end by X-measurement + CZ on the factors); gates read only by the output are computed into the target."""
        names = list(form['inputs'])
        n = len(names)
        gates = form['gates']
        vals = [named[x] for x in names]
        used_later = [any((n + i in g2['left'] or n + i in g2['right'] for g2 in gates[i + 1:])) for i in range(len(gates))]
        out_terms = set(form['output']['terms'])
        helpers = []
        for j in out_terms:
            if j < n:
                b.cx(vals[j], target)
        if form['output']['constant']:
            b.x(target)
        for i, g in enumerate(gates):
            lw = [vals[j] for j in g['left']]
            rw = [vals[j] for j in g['right']]
            h = b.alloc_qubits(1)[0] if used_later[i] else target
            wa, wb, ops = _w2core_e2__pair_forms(b, lw, rw)
            b.ccx(wa, wb, h)
            _w2core_e2__undo(b, ops)
            if used_later[i]:
                vals.append(h)
                helpers.append((h, lw, rw))
                if n + i in out_terms:
                    b.cx(h, target)
            else:
                assert n + i in out_terms
                vals.append(None)
        if keep:
            return (vals, helpers)
        _w2core_e2__erase_helpers(b, helpers)
        return (vals, [])

    def _w2core_e2_make_endpoint(phase07, e_hold=_w2core_e2_E_HOLD, f_hold=_w2core_e2_F_HOLD, r2_holds=_w2core_e2_R2_HOLDS, retire_v11=True, retire_v10=True):

        def raw_endpoint(real, token):
            B = phase07.BINDING
            d = B.divider
            v, u, flags = (token.v, token.u, token.flags)
            assert (len(v), len(u), len(flags)) == (12, 14, 4) and real.num_allocated_qubits == 43
            h12, h13, v10, v11 = (token.history[12], token.history[13], v[10], v[11])
            h14, h15, v8, v9 = (token.history[14], token.history[15], v[8], v[9])
            builder = _w2core_e2_SpareProxy(real, 43)
            builder.limit = _w2core_e2_MAX_EXTRA if retire_v11 else _w2core_e2_MAX_EXTRA - 1
            if retire_v11:
                m = real.alloc_bits(1)[0]
                real.hmr(v11, m)
                real.push_condition(m)
                real.z(h12)
                real.z(v10)
                real.cz(v10, h13)
                real.pop_condition()
                real.free(m)
                builder.spare.append(v11)
                builder.lent.add(v11)
            d._sigma25_frame(real, v, u)
            for q in u[:9]:
                real.cx(v[0], q)
            real.cx(v[1], u[9])
            if retire_v10:
                assert retire_v11
                m10 = real.alloc_bits(1)[0]
                real.hmr(v10, m10)
                builder.spare.append(v10)
                builder.lent.add(v10)
            if _w2core_e2_RETIRE_V9 is not None:
                v9w = v[9]
                m9 = real.alloc_bits(1)[0]
                real.hmr(v9w, m9)
                builder.spare.append(v9w)
                builder.lent.add(v9w)
            signs = {**token.history, 25: u[10], 26: u[9], 36: u[13]}
            signs.update({j: u[35 - j] for j in range(27, 36)})
            assert sorted(signs) == list(range(12, 37))
            for q in signs.values():
                real.x(q)
            one = real.alloc_qubits(1)[0]
            real.x(one)
            word = [signs[36 - i] for i in range(25)] + [one]
            assert len(set(word)) == 26 and u[11] not in word and (u[12] not in word)
            variables = flags + [None]
            assert real.num_allocated_qubits == 44
            slots = [word[i] for i in B.slots]
            pos_slot = {B.slots[k]: k for k in range(26)}
            rotated, featured = (set(), set())

            def rotate(pos):
                assert pos not in rotated
                real.z_pow(word[pos], _w2core_e2_Fraction(2 * B.angles[pos_slot[pos]], _w2core_e2_MODULUS))
                rotated.add(pos)

            def cswap(stage, i, j):
                with d._affine_control(real, variables, _w2core_e2_CONTROLS[stage]) as ctl:
                    real.cswap(ctl, word[i], word[j])

            def cswap_stage(stage, plist):
                with d._affine_control(real, variables, _w2core_e2_CONTROLS[stage]) as ctl:
                    for i, j in plist:
                        real.cswap(ctl, word[i], word[j])

            def hold(stage, i, j):
                a, b = (word[i], word[j])
                anc = builder.alloc_qubits(1)[0]
                with d._affine_control(real, variables, _w2core_e2_CONTROLS[stage]) as ctl:
                    real.cx(a, b)
                    real.ccx(ctl, b, anc)
                    real.cx(a, b)
                real.cx(anc, a)
                real.cx(anc, b)
                return anc

            def release(stage, i, j, anc):
                a, b = (word[i], word[j])
                real.cx(anc, a)
                real.cx(anc, b)
                m = real.alloc_bits(1)[0]
                real.hmr(anc, m)
                with d._affine_control(real, variables, _w2core_e2_CONTROLS[stage]) as ctl:
                    real.push_condition(m)
                    real.cz(ctl, a)
                    real.cz(ctl, b)
                    real.pop_condition()
                real.free(m)
                builder.free(anc)

            def threshold(t):
                terms = _w2core_e2_THR[t]
                if max((x.bit_count() for x in terms)) <= 1:
                    return d._affine_control(real, variables, terms)
                return _w2core_e2__quadratic(builder, real, d, variables, terms)

            def feature(j):
                assert j not in featured and 0 <= j <= 8
                featured.add(j)
                if j in _w2core_e2_ENC:
                    terms = _w2core_e2_ENC[j]
                    vars6 = variables + [slots[j]]
                    h = builder.alloc_qubits(1)[0]
                    d.xor_polynomial(real, vars6, h, terms)
                    turns = _w2core_e2_Fraction(B.angles[26 + j], _w2core_e2_MODULUS) if j <= 6 else _w2core_e2_Fraction(1, 8)
                    real.z_pow(h, 2 * turns)
                    d._erase_polynomial(builder, h, vars6, terms)
                    return
                with threshold(j + 1) as control:
                    if j <= 6:
                        d._feature(builder, control, slots[j], _w2core_e2_Fraction(B.angles[26 + j], _w2core_e2_MODULUS))
                    else:
                        d._feature(builder, control, slots[j], _w2core_e2_Fraction(1, 8) if j == 7 else _w2core_e2_Fraction(1, 4))

            def visit(pos):
                rotate(pos)
                k = pos_slot[pos]
                if k <= 8:
                    feature(k)
            held_r2 = {}
            late2 = [pr for pr in _w2core_e2_pairs(2) if pr not in r2_holds]
            cswap_stage(0, _w2core_e2_pairs(0))
            cswap_stage(1, _w2core_e2_pairs(1))
            cswap_stage(2, late2)
            e = {k: (13 - k, 13 + k) for k in range(1, 13)}
            f = {k: (13 + k, (12 - k) % 26) for k in range(0, 13)}
            held = {}

            def e_forward(k):
                if k in e_hold:
                    held[k] = hold(3, *e[k])
                else:
                    cswap(3, *e[k])

            def e_undo(k):
                if k in e_hold:
                    release(3, *e[k], held.pop(k))
                else:
                    cswap(3, *e[k])

            def f_round_trip(k):
                i, j = f[k]
                if k in f_hold:
                    anc = hold(4, i, j)
                    visit(i)
                    visit(j)
                    release(4, i, j, anc)
                else:
                    cswap(4, i, j)
                    visit(i)
                    visit(j)
                    cswap(4, i, j)

            def r2_open(step):
                for pr, (first, last) in r2_holds.items():
                    if first == step:
                        held_r2[pr] = hold(2, *pr)

            def r2_close(step):
                for pr, (first, last) in r2_holds.items():
                    if last == step:
                        release(2, *pr, held_r2.pop(pr))
            r2_open(0)
            e_forward(1)
            f_round_trip(0)
            r2_close(0)
            for k in range(1, 13):
                if k == _w2core_e2_P_RETIRED_STEPS[1] + 1:
                    pw = real.alloc_qubits(1)[0]
                    assert real.num_allocated_qubits <= _w2core_e2_QMAX, ('endpoint width at p rebuild', real.num_allocated_qubits)
                    d.xor_polynomial(real, flags, pw, (6, 10))
                    variables[4] = pw
                r2_open(k)
                if k + 1 <= 12:
                    e_forward(k + 1)
                f_round_trip(k)
                e_undo(k)
                r2_close(k)
            assert not held and (not held_r2) and (rotated == set(range(26))) and (featured == set(range(9)))
            real.cz(flags[1], flags[3])
            cswap_stage(2, late2)
            cswap_stage(1, _w2core_e2_pairs(1))
            cswap_stage(0, _w2core_e2_pairs(0))
            assert B.angles[33] == 0
            d._erase_polynomial(real, variables[4], flags, (6, 10))
            real.x(one)
            real.free(one)
            for q in signs.values():
                real.x(q)
            real.cx(v[1], u[9])
            for q in u[:9]:
                real.cx(v[0], q)
            if _w2core_e2_RETIRE_V9 is not None:
                assert v9w in builder.spare
                named = {'v%d' % i: v[i] for i in range(12)}
                named.update({'s%d' % k: token.history[k] for k in token.history})
                gvals, kept = _w2core_e2__emit_form(real, _w2core_e2_RETIRE_V9, named, v9w, keep=_w2core_e2_V10_FROM_G1)
                real.push_condition(m9)
                real.z(v9w)
                real.pop_condition()
                real.free(m9)
                builder.spare.remove(v9w)
            if _w2core_e2_RETIRE_V9 is not None and _w2core_e2_V10_FROM_G1:
                assert retire_v10 and v10 in builder.spare
                g1 = gvals[len(_w2core_e2_RETIRE_V9['inputs']) + 1]
                real.cx(v9w, v10)
                real.cx(g1, v10)
                wa, wb, ops = _w2core_e2__pair_forms(real, [h13, g1], [v9w, h14])
                real.ccx(wa, wb, v10)
                _w2core_e2__undo(real, ops)
                _w2core_e2__erase_helpers(real, kept)
                real.push_condition(m10)
                real.z(v10)
                real.pop_condition()
                real.free(m10)
                builder.spare.remove(v10)
            elif retire_v10:
                assert v10 in builder.spare
                hh = real.alloc_qubits(1)[0]
                real.ccx(v8, h15, hh)
                for q in (h13, v8, v9, h14, hh):
                    real.cx(q, v10)
                real.cx(h14, v8)
                real.cx(hh, v8)
                real.cx(h14, v9)
                real.ccx(v8, v9, v10)
                real.cx(h14, v9)
                real.cx(hh, v8)
                real.cx(h14, v8)
                mm = real.alloc_bits(1)[0]
                real.hmr(hh, mm)
                real.push_condition(mm)
                real.cz(v8, h15)
                real.pop_condition()
                real.free(mm)
                real.free(hh)
                real.push_condition(m10)
                real.z(v10)
                real.pop_condition()
                real.free(m10)
                builder.spare.remove(v10)
            d._sigma25_frame(real, v, u, inverse=True)
            if retire_v11:
                assert builder.spare == [v11]
                real.cx(h12, v11)
                real.cx(v10, v11)
                real.ccx(v10, h13, v11)
            assert real.num_allocated_qubits == 43
            _w2core_e2_RESULT.update(max_extra=builder.max_extra)
        return raw_endpoint

    class _w2core_e2__quadratic:

        def __init__(self, builder, real, d, variables, terms):
            self.args = (builder, real, d, variables, terms)

        def __enter__(self):
            builder, real, d, variables, terms = self.args
            self.q = builder.alloc_qubits(1)[0]
            d.xor_polynomial(real, variables, self.q, terms)
            return self.q

        def __exit__(self, *exc):
            builder, real, d, variables, terms = self.args
            d._erase_polynomial(builder, self.q, variables, terms)
            return False
    _w2core_e2_RESULT = {}

def _initialize_relocate_cs2():
    global _relocate_cs2_Fraction, _relocate_cs2_INTEGRATED_ROOT, _relocate_cs2_L, _relocate_cs2_R, _relocate_cs2_TQ, _relocate_cs2_X, _relocate_cs2__IntegratedPath, _relocate_cs2___file__, _relocate_cs2___name__, _relocate_cs2_angle, _relocate_cs2_b, _relocate_cs2_bits, _relocate_cs2_cs, _relocate_cs2_dst, _relocate_cs2_dyadic, _relocate_cs2_f45, _relocate_cs2_f7, _relocate_cs2_head, _relocate_cs2_i, _relocate_cs2_inserted, _relocate_cs2_k, _relocate_cs2_kmsim, _relocate_cs2_le15, _relocate_cs2_lines, _relocate_cs2_lt4, _relocate_cs2_need, _relocate_cs2_newangle, _relocate_cs2_np, _relocate_cs2_ops, _relocate_cs2_out, _relocate_cs2_p, _relocate_cs2_q1, _relocate_cs2_q21, _relocate_cs2_q21new, _relocate_cs2_r, _relocate_cs2_regs, _relocate_cs2_sim, _relocate_cs2_sim2, _relocate_cs2_site, _relocate_cs2_src, _relocate_cs2_sys, _relocate_cs2_text, _relocate_cs2_tq
    _relocate_cs2__IntegratedPath = _import_component('pathlib', 'agents/micro47/scripts/relocate_cs2.py', False).Path
    _relocate_cs2_INTEGRATED_ROOT = _relocate_cs2__IntegratedPath(_relocate_cs2___file__).resolve().parents[3]
    _relocate_cs2_sys = _import_component('sys', 'agents/micro47/scripts/relocate_cs2.py', True)
    _relocate_cs2_sys.path.insert(0, '' + str(_relocate_cs2_INTEGRATED_ROOT) + '/tools')
    _relocate_cs2_np = _import_component('numpy', 'agents/micro47/scripts/relocate_cs2.py', False)
    _relocate_cs2_kmsim = _import_component('kmsim', 'agents/micro47/scripts/relocate_cs2.py', True)
    _relocate_cs2_Fraction = _import_component('fractions', 'agents/micro47/scripts/relocate_cs2.py', False).Fraction
    _relocate_cs2_src, _relocate_cs2_dst = (_relocate_cs2_sys.argv[1], _relocate_cs2_sys.argv[2])
    _relocate_cs2_text = open(_relocate_cs2_src).read()
    _relocate_cs2_lines = _relocate_cs2_text.split('\n')
    _relocate_cs2_head = 0
    while _relocate_cs2_lines[_relocate_cs2_head].split()[0] in ('APPEND_TO_REGISTER', 'REGISTER'):
        _relocate_cs2_head += 1
    _relocate_cs2_ops, _relocate_cs2_regs = _relocate_cs2_kmsim.parse(_relocate_cs2_text)
    _relocate_cs2_L = lambda i: _relocate_cs2_lines[_relocate_cs2_head + i].strip()
    _relocate_cs2_cs = None
    for _relocate_cs2_i in range(len(_relocate_cs2_ops) - 13):
        if not (_relocate_cs2_L(_relocate_cs2_i + 1) == 'CX q23 q22' and _relocate_cs2_L(_relocate_cs2_i + 2).startswith('CCX q22 q25 ') and (_relocate_cs2_L(_relocate_cs2_i + 3) == 'CX q23 q22')):
            continue
        _relocate_cs2_tq = _relocate_cs2_L(_relocate_cs2_i + 2).split()[3]
        if _relocate_cs2_L(_relocate_cs2_i + 4) == 'Z_POW %s 0.25' % _relocate_cs2_tq and _relocate_cs2_L(_relocate_cs2_i + 5).startswith('CX %s ' % _relocate_cs2_tq) and _relocate_cs2_L(_relocate_cs2_i + 6).endswith(' 1.75') and (_relocate_cs2_L(_relocate_cs2_i + 7) == _relocate_cs2_L(_relocate_cs2_i + 5)) and _relocate_cs2_L(_relocate_cs2_i + 8).startswith('HMR %s ' % _relocate_cs2_tq) and (_relocate_cs2_L(_relocate_cs2_i + 10) == 'CZ q22 q25') and (_relocate_cs2_L(_relocate_cs2_i + 11) == 'CZ q23 q25') and (_relocate_cs2_L(_relocate_cs2_i + 12) == 'POP_CONDITION'):
            _relocate_cs2_r = _relocate_cs2_L(_relocate_cs2_i + 5).split()[2]
            assert _relocate_cs2_L(_relocate_cs2_i).startswith('Z_POW %s ' % _relocate_cs2_r) and _relocate_cs2_L(_relocate_cs2_i + 6) == 'Z_POW %s 1.75' % _relocate_cs2_r, (_relocate_cs2_L(_relocate_cs2_i), _relocate_cs2_L(_relocate_cs2_i + 6))
            _relocate_cs2_b = _relocate_cs2_L(_relocate_cs2_i + 8).split()[2]
            assert _relocate_cs2_L(_relocate_cs2_i + 9) == 'PUSH_CONDITION if %s' % _relocate_cs2_b
            _relocate_cs2_cs = (_relocate_cs2_i, _relocate_cs2_r, _relocate_cs2_tq)
            break
    assert _relocate_cs2_cs, 'CS block not found'
    _relocate_cs2_k, _relocate_cs2_R, _relocate_cs2_TQ = _relocate_cs2_cs
    _relocate_cs2_angle = _relocate_cs2_Fraction(_relocate_cs2_L(_relocate_cs2_k).split()[2])
    assert _relocate_cs2_Fraction(1, 4) < _relocate_cs2_angle < _relocate_cs2_Fraction(1, 4) + _relocate_cs2_Fraction(1, 10 ** 6), _relocate_cs2_angle
    _relocate_cs2_newangle = _relocate_cs2_angle - _relocate_cs2_Fraction(1, 4)
    _relocate_cs2_site = None
    for _relocate_cs2_i in range(min(2000, len(_relocate_cs2_ops))):
        if _relocate_cs2_L(_relocate_cs2_i) == 'CCX q36 q1 q21':
            _relocate_cs2_site = _relocate_cs2_i
            break
    assert _relocate_cs2_site is not None, 'normalization CCX q36 q1 q21 not found'
    _relocate_cs2_sim = _relocate_cs2_kmsim.Sim(_relocate_cs2_ops, _relocate_cs2_regs['x'])
    _relocate_cs2_X = _relocate_cs2_np.arange(1, _relocate_cs2_sim.n + 1)

    def _relocate_cs2_bits(v):
        return _relocate_cs2_np.unpackbits(v.view(_relocate_cs2_np.uint8), bitorder='little')[:_relocate_cs2_sim.n].astype(_relocate_cs2_np.int64)
    _relocate_cs2_sim.run(stop=_relocate_cs2_site)
    _relocate_cs2_lt4, _relocate_cs2_le15, _relocate_cs2_q1, _relocate_cs2_q21 = (_relocate_cs2_bits(_relocate_cs2_sim.get('q36')), _relocate_cs2_bits(_relocate_cs2_sim.get('q35')), _relocate_cs2_bits(_relocate_cs2_sim.get('q1')), _relocate_cs2_bits(_relocate_cs2_sim.get('q21')))
    assert _relocate_cs2_np.array_equal(_relocate_cs2_lt4, (_relocate_cs2_X < 4).astype(_relocate_cs2_np.int64)), 'q36 != [x<4]'
    assert _relocate_cs2_np.array_equal(_relocate_cs2_le15, (_relocate_cs2_X <= 15).astype(_relocate_cs2_np.int64)), 'q35 != [x<=15]'
    _relocate_cs2_p = _relocate_cs2_lt4 & _relocate_cs2_q1
    _relocate_cs2_q21new = _relocate_cs2_q21 ^ _relocate_cs2_p
    _relocate_cs2_inserted = (_relocate_cs2_le15 - _relocate_cs2_lt4 + (_relocate_cs2_q21 - _relocate_cs2_q21new)) % 4
    _relocate_cs2_sim2 = _relocate_cs2_kmsim.Sim(_relocate_cs2_ops, _relocate_cs2_regs['x'])
    _relocate_cs2_sim2.run(stop=_relocate_cs2_k + 2)
    _relocate_cs2_f45 = _relocate_cs2_bits(_relocate_cs2_sim2.get(_relocate_cs2_R))
    _relocate_cs2_sim2.run(start=_relocate_cs2_k + 2, stop=_relocate_cs2_k + 4)
    _relocate_cs2_f7 = _relocate_cs2_bits(_relocate_cs2_sim2.get(_relocate_cs2_TQ))
    assert _relocate_cs2_np.array_equal(_relocate_cs2_f7, (_relocate_cs2_X <= 15).astype(_relocate_cs2_np.int64)), 'endpoint temp != [x<=15]'
    _relocate_cs2_need = (_relocate_cs2_f7 & _relocate_cs2_f45) % 4
    assert _relocate_cs2_np.array_equal(_relocate_cs2_inserted, _relocate_cs2_need), 'inserted Clifford phase != endpoint CS phase'
    print('verified on', _relocate_cs2_sim.n, 'inputs: endpoint CS at op', _relocate_cs2_k, '(rotation', _relocate_cs2_R, _relocate_cs2_angle, '->', _relocate_cs2_newangle, '); Clifford site at op', _relocate_cs2_site, '; [x=1] count', int(_relocate_cs2_p.sum()))

    def _relocate_cs2_dyadic(fr):
        num, den = (fr.numerator, fr.denominator)
        kk = den.bit_length() - 1
        digits = str(num * 5 ** kk).rjust(kk + 1, '0')
        whole, frac = (digits[:-kk], digits[-kk:].rstrip('0'))
        return (whole or '0') + ('.' + frac if frac else '')
    assert _relocate_cs2_Fraction(_relocate_cs2_dyadic(_relocate_cs2_newangle)) == _relocate_cs2_newangle
    _relocate_cs2_out = _relocate_cs2_lines[:_relocate_cs2_head]
    for _relocate_cs2_i in range(len(_relocate_cs2_lines) - _relocate_cs2_head):
        if _relocate_cs2_i == _relocate_cs2_site:
            _relocate_cs2_out += ['Z_POW q35 0.5', 'Z_POW q36 1.5', 'Z_POW q21 0.5', _relocate_cs2_lines[_relocate_cs2_head + _relocate_cs2_i], 'Z_POW q21 1.5']
            continue
        if _relocate_cs2_k + 1 <= _relocate_cs2_i <= _relocate_cs2_k + 12:
            continue
        if _relocate_cs2_i == _relocate_cs2_k:
            _relocate_cs2_out.append('Z_POW %s %s' % (_relocate_cs2_R, _relocate_cs2_dyadic(_relocate_cs2_newangle)))
            continue
        _relocate_cs2_out.append(_relocate_cs2_lines[_relocate_cs2_head + _relocate_cs2_i])
    open(_relocate_cs2_dst, 'w').write('\n'.join(_relocate_cs2_out))
    print('wrote', _relocate_cs2_dst)

def _initialize_block_replay():
    global _block_replay_INTEGRATED_ROOT, _block_replay__IntegratedPath, _block_replay___file__, _block_replay___name__, _block_replay_replay

    def _block_replay_replay(builder, plan, wire_map, ext_bits=None):
        h = dict(wire_map)
        bits = dict(ext_bits or {})
        own_bits = {}
        ccx = 0

        def q(w):
            if w not in h:
                h[w] = builder.alloc_qubits(1)[0]
            return h[w]

        def bit(name):
            return bits[name]
        for item in plan['plan']:
            kind = item[0]
            if kind == 'ZERO':
                w = item[1]
                if w in h:
                    builder.free(h.pop(w))
                continue
            _, qs, bs, cond = item
            if kind == 'PUSH_CONDITION':
                builder.push_condition(bit(cond))
                continue
            if kind == 'POP_CONDITION':
                builder.pop_condition()
                continue
            if kind == 'HMR':
                name = bs[0]
                if name in own_bits:
                    builder.free(own_bits.pop(name))
                b = builder.alloc_bits(1)[0]
                own_bits[name] = b
                bits[name] = b
                assert cond is None
                builder.hmr(q(qs[0]), b)
                continue
            if cond is not None:
                builder.push_condition(bit(cond))
            args = [q(w) for w in qs]
            if kind == 'X':
                builder.x(args[0])
            elif kind == 'Z':
                builder.z(args[0])
            elif kind == 'CX':
                builder.cx(args[0], args[1])
            elif kind == 'CZ':
                builder.cz(args[0], args[1])
            elif kind == 'CCX':
                builder.ccx(args[0], args[1], args[2])
                ccx += 1
            elif kind == 'SWAP':
                builder.swap(args[0], args[1])
            else:
                raise AssertionError(('unsupported donor op', kind))
            if cond is not None:
                builder.pop_condition()
        for name, b in own_bits.items():
            builder.free(b)
        assert ccx == plan['ccx']
        return h

def _initialize_paid_R_cleanup_q48():
    global _paid_R_cleanup_q48_CERT, _paid_R_cleanup_q48_CERT_PATH, _paid_R_cleanup_q48_CERT_SHA, _paid_R_cleanup_q48_EXPECTED, _paid_R_cleanup_q48_FULL, _paid_R_cleanup_q48_Fraction, _paid_R_cleanup_q48_HERE, _paid_R_cleanup_q48_INTEGRATED_ROOT, _paid_R_cleanup_q48_LAST_REPORT, _paid_R_cleanup_q48_Path, _paid_R_cleanup_q48__IntegratedPath, _paid_R_cleanup_q48___file__, _paid_R_cleanup_q48___name__, _paid_R_cleanup_q48_capture_R_before_inverse, _paid_R_cleanup_q48_cleanup_joint18, _paid_R_cleanup_q48_finish_R_capture, _paid_R_cleanup_q48_hashlib, _paid_R_cleanup_q48_json
    _paid_R_cleanup_q48__IntegratedPath = _import_component('pathlib', 'agents/width/src/paid_R_cleanup_q48.py', False).Path
    _paid_R_cleanup_q48_INTEGRATED_ROOT = _paid_R_cleanup_q48__IntegratedPath(_paid_R_cleanup_q48___file__).resolve().parents[3]
    _paid_R_cleanup_q48_Path = _import_component('pathlib', 'agents/width/src/paid_R_cleanup_q48.py', False).Path
    _paid_R_cleanup_q48_Fraction = _import_component('fractions', 'agents/width/src/paid_R_cleanup_q48.py', False).Fraction
    _paid_R_cleanup_q48_HERE = _paid_R_cleanup_q48_Path('' + str(_paid_R_cleanup_q48_INTEGRATED_ROOT) + '/work/pro2_q47_loader/work/loaders/q47_loader_native_v1')
    _paid_R_cleanup_q48_CERT_SHA = '9c4b4aea56ad334f7082608d3a24193d900390c76e578e48aa67a88456664ff7'
    _paid_R_cleanup_q48_CERT_PATH = _paid_R_cleanup_q48_HERE / 'paid_R_cleanup_certificate.json'
    _paid_R_cleanup_q48_CERT = _json_loads(_read_text(_paid_R_cleanup_q48_CERT_PATH))
    _paid_R_cleanup_q48_EXPECTED = _paid_R_cleanup_q48_Fraction(*_paid_R_cleanup_q48_CERT['selected']['mean_fraction'])
    assert _paid_R_cleanup_q48_EXPECTED == _paid_R_cleanup_q48_Fraction(809, 128)
    _paid_R_cleanup_q48_FULL = (1 << 128) - 1
    _paid_R_cleanup_q48_LAST_REPORT = None

    def _paid_R_cleanup_q48_cleanup_joint18(builder, address7, A13, H5, product, debts, *, table_api):
        """Erase A13/H5, all phase helpers and paid p; retain all26 body owners."""
        global _paid_R_cleanup_q48_LAST_REPORT
        api = table_api
        cb = api.cb
        address, A, H = (list(address7), list(A13), list(H5))
        assert (len(address), len(A), len(H)) == (7, 13, 5)
        assert len(set(address + A + H + [product])) == 26
        assert isinstance(debts, api.TableDebts)
        assert builder.max_qubits in (46, 47, 48) and builder.num_allocated_qubits == 45
        truths = api.model_truths()
        raw = list(truths['address'])
        output_truths = list(truths['A']) + list(truths['H'])
        assert len(output_truths) == 18
        paid_truth = raw[1] & (raw[2] ^ raw[5])
        base_truths = raw + [paid_truth]
        assert paid_truth == int(_paid_R_cleanup_q48_CERT['free_coordinate']['truth'], 16)
        flushed = debts.flush(builder, address + A + H[:3], raw + output_truths[:16])
        assert not debts.pending and flushed['quadratic_rank'] == 128
        selected = _paid_R_cleanup_q48_CERT['selected']
        masks = selected['masks']
        assert len(masks) == len(cb.BinarySpan(masks).pivots) == 18
        framed = [cb.parity_function(m, output_truths) for m in masks]
        outputs = A + H
        api.emit_affine_frame(builder, address, outputs, [m << 8 for m in masks])
        producers = []
        helper_truths = []
        for item in _paid_R_cleanup_q48_CERT['bank_steps']:
            plan = api.plan_from_json(item['plan'])
            truth = int(item['truth'], 16)
            assert plan.width == 8 + len(producers) and plan.and_count == 1
            assert plan.evaluate_factored_functions(base_truths + helper_truths, _paid_R_cleanup_q48_FULL) == truth
            producers.append(plan)
            helper_truths.append(truth)
        helpers = []
        present = []
        live = list(outputs)
        trace = [45]
        users = [set() for _ in producers]
        compute_sites = 0
        for item in selected['erasures']:
            index = item['output_index']
            assert len(live) == index + 1
            old = live.pop()
            outcome = builder.alloc_bits(1)[0]
            builder.hmr(old, outcome)
            builder.free(old)
            prefix = item['min_prefix']
            if prefix and (not helpers):
                helpers = list(builder.alloc_qubits(len(producers)))
                present = list(builder.alloc_bits(len(producers)))
                for flag in present:
                    builder.bit_store(flag, False)
            for j in item['needed']:
                users[j].add(index)
                missing = builder.alloc_bits(1)[0]
                builder.bit_store(missing, True)
                builder.cx(present[j], missing)
                builder.push_condition(outcome)
                builder.push_condition(missing)
                cb.emit_xor(builder, address + [product] + helpers[:j], helpers[j], producers[j])
                builder.bit_store(present[j], True)
                builder.pop_condition()
                builder.pop_condition()
                builder.free(missing)
                compute_sites += 1
            plan = api.plan_from_json(item['plan'])
            variables = address + [product] + helpers[:prefix] + live
            assert plan.width == len(variables)
            assert plan.evaluate_functions(base_truths + helper_truths[:prefix] + framed[:index], _paid_R_cleanup_q48_FULL) == framed[index]
            cb.emit_phase(builder, variables, outcome, plan)
            builder.free(outcome)
            trace.append(builder.num_allocated_qubits)
        assert not live and len(helpers) == len(present) == len(producers)
        for j in reversed(range(len(producers))):
            builder.push_condition(present[j])
            cb.emit_erase(builder, address + [product] + helpers[:j], [helpers[j]], [producers[j]])
            builder.pop_condition()
            builder.free(helpers[j])
            trace.append(builder.num_allocated_qubits)
        for flag in present:
            builder.free(flag)
        assert builder.num_allocated_qubits == 27
        paid_plan = api.plan_from_json(_paid_R_cleanup_q48_CERT['free_coordinate']['final_erase_plan'])
        assert paid_plan.width == 7 and paid_plan.evaluate_functions(raw, _paid_R_cleanup_q48_FULL) == paid_truth
        cb.emit_erase(builder, address, [product], [paid_plan])
        builder.free(product)
        trace.append(builder.num_allocated_qubits)
        assert [sorted(s) for s in users] == selected['users']
        expected = sum((1 - _paid_R_cleanup_q48_Fraction(1, 1 << len(s)) for s in users), _paid_R_cleanup_q48_Fraction(0))
        assert expected == _paid_R_cleanup_q48_EXPECTED and builder.num_allocated_qubits == 26
        assert max(trace) <= selected['cleanup_peak_bound'] <= 47 and (not debts.pending)
        _paid_R_cleanup_q48_LAST_REPORT = dict(status='EMITTED_PAID_R18_COMPONENT_NATIVE_PROOF_PENDING', expected_Toffolis=float(expected), expected_fraction=[expected.numerator, expected.denominator], entry=45, return_owners=26, capture_peak=45, cleanup_peak_bound=selected['cleanup_peak_bound'], trace=trace, output_signs_repaid=18, paid_product_sign_repaid=True, helper_signs_all_branches_repaid=True, incoming_table_debts_repaid=flushed['outcomes'], incoming_flush_unchanged=True, compute_sites=compute_sites, helper_activation_users=[sorted(s) for s in users], producer_added_Toffolis=0, producer_added_CNOTs=3, root_frame_and_arithmetic_callbacks_external_and_unchanged=True, certificate_sha256=_paid_R_cleanup_q48_CERT_SHA)
        return _paid_R_cleanup_q48_LAST_REPORT

def _initialize_patch_coef2_q46():
    global _patch_coef2_q46_INTEGRATED_ROOT, _patch_coef2_q46_STATE, _patch_coef2_q46__IntegratedPath, _patch_coef2_q46___file__, _patch_coef2_q46___name__, _patch_coef2_q46_apply, _patch_coef2_q46_make
    _patch_coef2_q46_STATE = dict(calls=0, converted=None, applied=0)

    def _patch_coef2_q46_make(baseline, previous_forward, previous_erase):
        km = baseline.km

        def forward_add_disposable(arithmetic, builder, source, target, *, carry_in, erase_input):
            assert isinstance(carry_in, km.q) and callable(erase_input)
            a, b, preserve = arithmetic._inputs(source, target, carry_in, False)
            width = len(b)
            debts = {}
            released = False
            assert preserve is None
            if not width:
                return (arithmetic.CarryDebt(debts, width), False)
            if width == 1:
                builder.cx(a[0], b[0])
                builder.cx(carry_in, b[0])
                return (arithmetic.CarryDebt(debts, width), False)

            def measure(carry, position):
                if carry is False:
                    return
                outcome = builder.alloc_bits(1)[0]
                builder.hmr(carry, outcome)
                builder.free(carry)
                debts[position] = outcome
            carry = carry_in
            for index, (aa, bb) in enumerate(zip(a[:-2], b[:-2])):
                frame = arithmetic._compute_carry(builder, aa, bb, carry, preserve=preserve)
                arithmetic._sum_keep_carry(builder, frame)
                if index == 0:
                    assert frame.incoming == carry_in and frame.outgoing is not False and (frame.outgoing != carry_in)
                    erase_input(carry_in)
                    released = True
                if index:
                    measure(carry, index)
                carry = frame.outgoing
            arithmetic._finish_top(builder, a, b, carry, preserve)
            if width > 2:
                measure(carry, width - 2)
            return (arithmetic.CarryDebt(debts, width), released)

        def overflow_forward_disposable(builder, residual, source, target, token):
            if token.saved_bit is None:
                return
            assert not token.plan.signed_source
            sigma = residual[token.plan.last - 1]
            top = target[token.window - 1]
            saved = token.saved_bit
            builder.cx(sigma, saved)
            builder.cx(sigma, top)
            builder.x(top)
            wrap = builder.alloc_qubits(1)[0]
            builder.ccx(saved, top, wrap)
            high = target[token.window:]
            for wire in high:
                builder.cx(sigma, wire)

            def erase_wrap(value):
                builder.del_and(saved, top, value)
                builder.free(value)
            token.overflow_debt, released = forward_add_disposable(baseline.ar, builder, [], high, carry_in=wrap, erase_input=erase_wrap)
            for wire in high:
                builder.cx(sigma, wire)
            if not released:
                erase_wrap(wrap)
            builder.x(top)
            builder.cx(sigma, top)
            builder.cx(sigma, saved)

        def second_forward(builder, v, D, H):
            assert len(D) == 13 and len(H) == 5 and (v[11] is None)
            h3, h4, d11 = (H[3], H[4], D[11])
            m = builder.alloc_bits(1)[0]
            builder.hmr(D[12], m)
            builder.free(D[12])
            D[12] = None
            S = [v[8]] + list(H)
            snapshot = builder.alloc_qubits(1)[0]
            builder.cx(D[6], snapshot)
            token = baseline.ar.DeferredBoundedToken(baseline.SimpleNamespace(last=5, signed_source=False), snapshot, 7, [])
            for i in range(5):
                k = 4 - i
                carry = baseline._coefficient_carry(builder, S, v[i], k)
                for q in D[:7]:
                    builder.cx(v[i], q)
                debt, released = forward_add_disposable(baseline.ar, builder, S[k + 1:], D[:7], carry_in=carry, erase_input=lambda value, i=i, k=k: baseline._clear_coefficient_carry(builder, S, v[i], k, value))
                token.row_debts.append(debt)
                for q in D[:7]:
                    builder.cx(v[i], q)
                if not released:
                    baseline._clear_coefficient_carry(builder, S, v[i], k, carry)
            builder.cx(h3, h4)
            builder.ccx(d11, h3, h4)
            builder.push_condition(m)
            builder.z(h4)
            builder.pop_condition()
            builder.free(m)
            D[12] = h4
            _patch_coef2_q46_STATE['converted'] = h4
            _patch_coef2_q46_STATE['applied'] += 1
            overflow_forward_disposable(builder, v[:5], S, D, token)
            return token

        def coefficient_forward(builder, v, D, H):
            _patch_coef2_q46_STATE['calls'] += 1
            if _patch_coef2_q46_STATE['calls'] == 2:
                return second_forward(builder, v, D, H)
            return previous_forward(builder, v, D, H)

        def erase_high_H(builder, v, D, H, *, initial=False):
            h4 = _patch_coef2_q46_STATE['converted']
            if h4 is not None and (not initial) and (len(H) == 5) and (H[4] is h4):
                assert D[12] is h4
                _patch_coef2_q46_STATE['converted'] = None
                variables = [D[i] for i in (9, 10, 11, 12)] + [H[2], v[10]]
                baseline._erase(builder, H[3], variables, baseline.H3_CURRENT)
                return list(H[:3])
            return previous_erase(builder, v, D, H, initial=initial)
        return (coefficient_forward, erase_high_H)

    def _patch_coef2_q46_apply(ctx):
        bl = ctx.baseline
        for name in ('_erase', 'H3_CURRENT', '_coefficient_carry', '_clear_coefficient_carry', 'SimpleNamespace', 'ar', 'km'):
            assert hasattr(bl, name), name
        bl.coefficient_forward, bl.erase_high_H = _patch_coef2_q46_make(bl, bl.coefficient_forward, bl.erase_high_H)

def _initialize_patch_coefdisp():
    global _patch_coefdisp_INTEGRATED_ROOT, _patch_coefdisp__IntegratedPath, _patch_coefdisp___file__, _patch_coefdisp___name__, _patch_coefdisp_apply, _patch_coefdisp_make

    def _patch_coefdisp_make(baseline):
        km = baseline.km

        def forward_add_disposable(arithmetic, builder, source, target, *, carry_in, erase_input):
            assert isinstance(carry_in, km.q) and callable(erase_input)
            a, b, preserve = arithmetic._inputs(source, target, carry_in, False)
            width = len(b)
            debts = {}
            released = False
            assert preserve is None
            if not width:
                return (arithmetic.CarryDebt(debts, width), False)
            if width == 1:
                builder.cx(a[0], b[0])
                builder.cx(carry_in, b[0])
                return (arithmetic.CarryDebt(debts, width), False)

            def measure(carry, position):
                if carry is False:
                    return
                outcome = builder.alloc_bits(1)[0]
                builder.hmr(carry, outcome)
                builder.free(carry)
                debts[position] = outcome
            carry = carry_in
            for index, (aa, bb) in enumerate(zip(a[:-2], b[:-2])):
                frame = arithmetic._compute_carry(builder, aa, bb, carry, preserve=preserve)
                arithmetic._sum_keep_carry(builder, frame)
                if index == 0:
                    assert frame.incoming == carry_in and frame.outgoing is not False and (frame.outgoing != carry_in)
                    erase_input(carry_in)
                    released = True
                if index:
                    measure(carry, index)
                carry = frame.outgoing
            arithmetic._finish_top(builder, a, b, carry, preserve)
            if width > 2:
                measure(carry, width - 2)
            return (arithmetic.CarryDebt(debts, width), released)

        def overflow_forward_disposable(builder, residual, source, target, token):
            if token.saved_bit is None:
                return
            assert not token.plan.signed_source
            sigma = residual[token.plan.last - 1]
            top = target[token.window - 1]
            saved = token.saved_bit
            builder.cx(sigma, saved)
            builder.cx(sigma, top)
            builder.x(top)
            wrap = builder.alloc_qubits(1)[0]
            builder.ccx(saved, top, wrap)
            high = target[token.window:]
            for wire in high:
                builder.cx(sigma, wire)

            def erase_wrap(value):
                builder.del_and(saved, top, value)
                builder.free(value)
            token.overflow_debt, released = forward_add_disposable(baseline.ar, builder, [], high, carry_in=wrap, erase_input=erase_wrap)
            for wire in high:
                builder.cx(sigma, wire)
            if not released:
                erase_wrap(wrap)
            builder.x(top)
            builder.cx(sigma, top)
            builder.cx(sigma, saved)

        def coefficient_forward(builder, v, D, H):
            S = [v[8]] + list(H)
            snapshot = builder.alloc_qubits(1)[0]
            builder.cx(D[6], snapshot)
            token = baseline.ar.DeferredBoundedToken(baseline.SimpleNamespace(last=5, signed_source=False), snapshot, 7, [])
            for i in range(5):
                k = 4 - i
                carry = baseline._coefficient_carry(builder, S, v[i], k)
                for q in D[:7]:
                    builder.cx(v[i], q)
                debt, released = forward_add_disposable(baseline.ar, builder, S[k + 1:], D[:7], carry_in=carry, erase_input=lambda value, i=i, k=k: baseline._clear_coefficient_carry(builder, S, v[i], k, value))
                token.row_debts.append(debt)
                for q in D[:7]:
                    builder.cx(v[i], q)
                if not released:
                    baseline._clear_coefficient_carry(builder, S, v[i], k, carry)
            overflow_forward_disposable(builder, v[:5], S, D, token)
            return token
        return coefficient_forward

    def _patch_coefdisp_apply(ctx):
        ctx.baseline.coefficient_forward = _patch_coefdisp_make(ctx.baseline)

def _initialize_patch_donor_first60():
    global _patch_donor_first60_EXPECT, _patch_donor_first60_HERE, _patch_donor_first60_INTEGRATED_ROOT, _patch_donor_first60_PLAN_FILES, _patch_donor_first60_Path, _patch_donor_first60_REPORT, _patch_donor_first60_USE, _patch_donor_first60__IntegratedPath, _patch_donor_first60___file__, _patch_donor_first60___name__, _patch_donor_first60__plan, _patch_donor_first60_apply, _patch_donor_first60_json, _patch_donor_first60_os, _patch_donor_first60_replay
    _patch_donor_first60__IntegratedPath = _import_component('pathlib', 'patches/patch_donor_first60.py', False).Path
    _patch_donor_first60_INTEGRATED_ROOT = _patch_donor_first60__IntegratedPath(_patch_donor_first60___file__).resolve().parents[1]
    _patch_donor_first60_Path = _import_component('pathlib', 'patches/patch_donor_first60.py', False).Path
    _patch_donor_first60_HERE = _patch_donor_first60_Path('' + str(_patch_donor_first60_INTEGRATED_ROOT) + '/agents/width')
    _patch_donor_first60_USE = dict(first=True, second=False)
    _patch_donor_first60_PLAN_FILES = dict(first=_patch_donor_first60_HERE / 'plans/L1_first60.json', second=_patch_donor_first60_HERE / 'plans/L2_second78.json')
    _patch_donor_first60_EXPECT = dict(first=dict(ccx=60, hmr=42), second=dict(ccx=78, hmr=63))
    _patch_donor_first60_REPORT = {}

    def _patch_donor_first60__plan(which):
        data = _json_loads(_read_text(_patch_donor_first60_PLAN_FILES[which]))
        assert data['ccx'] == _patch_donor_first60_EXPECT[which]['ccx'] and data['hmr'] == _patch_donor_first60_EXPECT[which]['hmr']
        return data

    def _patch_donor_first60_replay(builder, data, address7, debts):
        owner = data['entry_owner']
        v_wires = {}
        for w, (role, i) in owner.items():
            if role == 'v':
                v_wires[i] = w
        h = {}
        for i in range(7):
            h[v_wires[5 + i]] = address7[i]
        entry = set(h)
        assert set(data['touched_entry']) <= entry, 'donor block touches an entry wire we did not map'
        ccx = hmr = 0
        for item in data['plan']:
            kind = item[0]
            if kind == 'ALLOC':
                continue
            if kind == 'ZERO':
                w = item[1]
                if w in h:
                    builder.free(h.pop(w))
                continue
            wires = item[1]
            for w in wires:
                if w not in h:
                    h[w] = builder.alloc_qubits(1)[0]
            q = [h[w] for w in wires]
            if kind == 'X':
                builder.x(q[0])
            elif kind == 'CX':
                builder.cx(q[0], q[1])
            elif kind == 'CCX':
                builder.ccx(q[0], q[1], q[2])
                ccx += 1
            elif kind == 'SWAP':
                builder.swap(q[0], q[1])
            elif kind == 'HMR':
                debts.erase(builder, q[0], int(item[2], 16))
                hmr += 1
            else:
                raise AssertionError(kind)
        D = [h[w] for w in data['outputs']['D']]
        H = [h[w] for w in data['outputs']['H']]
        assert len(D) == 13 and len(H) == 3
        return (D, H, dict(ccx=ccx, hmr=hmr))

    def _patch_donor_first60_apply(ctx):
        tables = ctx.tables
        original = tables.load_joint16

        def load_joint16(builder, address7, *, variant, debts):
            if not _patch_donor_first60_USE.get(variant):
                return original(builder, address7, variant=variant, debts=debts)
            assert isinstance(debts, tables.TableDebts)
            before = debts.total_recorded
            D, H, counts = _patch_donor_first60_replay(builder, _patch_donor_first60__plan(variant), list(address7), debts)
            assert debts.total_recorded - before == _patch_donor_first60_EXPECT[variant]['hmr']
            _patch_donor_first60_REPORT[variant] = counts
            return (D, H)
        tables.load_joint16 = load_joint16

def _initialize_patch_endpoint_v9e2():
    global _patch_endpoint_v9e2_E_HOLD, _patch_endpoint_v9e2_FORM, _patch_endpoint_v9e2_F_HOLD, _patch_endpoint_v9e2_INTEGRATED_ROOT, _patch_endpoint_v9e2_Path, _patch_endpoint_v9e2_R2, _patch_endpoint_v9e2_ROLE, _patch_endpoint_v9e2__CORE, _patch_endpoint_v9e2__FORM_PATH, _patch_endpoint_v9e2__IntegratedPath, _patch_endpoint_v9e2___file__, _patch_endpoint_v9e2___name__, _patch_endpoint_v9e2__core, _patch_endpoint_v9e2__f, _patch_endpoint_v9e2__spec, _patch_endpoint_v9e2_a, _patch_endpoint_v9e2_apply, _patch_endpoint_v9e2_b, _patch_endpoint_v9e2_c, _patch_endpoint_v9e2_d, _patch_endpoint_v9e2_hashlib, _patch_endpoint_v9e2_importlib, _patch_endpoint_v9e2_json, _patch_endpoint_v9e2_os, _patch_endpoint_v9e2_x
    _patch_endpoint_v9e2__IntegratedPath = _import_component('pathlib', 'patches/patch_endpoint_v9e2.py', False).Path
    _patch_endpoint_v9e2_INTEGRATED_ROOT = _patch_endpoint_v9e2__IntegratedPath(_patch_endpoint_v9e2___file__).resolve().parents[1]
    _patch_endpoint_v9e2_os = _import_component('os', 'patches/patch_endpoint_v9e2.py', True)
    _patch_endpoint_v9e2_Path = _import_component('pathlib', 'patches/patch_endpoint_v9e2.py', False).Path
    _patch_endpoint_v9e2__CORE = _patch_endpoint_v9e2_Path('' + str(_patch_endpoint_v9e2_INTEGRATED_ROOT) + '/agents/composer/p/w2core_e2.py')
    _patch_endpoint_v9e2__spec = _spec('width2_walk8_core_v9', _patch_endpoint_v9e2__CORE)
    _patch_endpoint_v9e2__core = _new_module(_patch_endpoint_v9e2__spec)
    _patch_endpoint_v9e2__spec.loader.exec_module(_patch_endpoint_v9e2__core)
    _patch_endpoint_v9e2__core.QMAX = 46
    _patch_endpoint_v9e2_ROLE = {'q18': 'v8', 'q17': 'v7', 'q9': 's12', 'q34': 's13', 'q36': 's14', 'q0': 's15', 'q30': 's16', 'q32': 's17'}
    if _patch_endpoint_v9e2_os.environ.get('W2_V9_PLACEHOLDER') == '1':
        _patch_endpoint_v9e2_FORM = dict(inputs=[], gates=[], output=dict(constant=0, terms=[]))
    else:
        _patch_endpoint_v9e2__f = _json_loads(_read_text(_patch_endpoint_v9e2_Path(_patch_endpoint_v9e2_os.environ.get('W2_V9_FORM', '' + str(_patch_endpoint_v9e2_INTEGRATED_ROOT) + '/agents/composer/p/v9_form_e2.json'))))
        assert _patch_endpoint_v9e2__f['status'] == 'SAT'
        _patch_endpoint_v9e2_FORM = dict(inputs=[_patch_endpoint_v9e2_ROLE[x] for x in _patch_endpoint_v9e2__f['inputs']], gates=_patch_endpoint_v9e2__f['gates'], output=_patch_endpoint_v9e2__f['output'])
    _patch_endpoint_v9e2__core.RETIRE_V9 = _patch_endpoint_v9e2_FORM
    _patch_endpoint_v9e2__core.V10_FROM_G1 = True
    _patch_endpoint_v9e2_E_HOLD = set((int(x) for x in _patch_endpoint_v9e2_os.environ.get('W2_E_HOLD', ','.join(map(str, range(1, 13)))).split(',') if x))
    _patch_endpoint_v9e2_F_HOLD = set((int(x) for x in _patch_endpoint_v9e2_os.environ.get('W2_F_HOLD', ','.join(map(str, range(13)))).split(',') if x))
    _patch_endpoint_v9e2_R2 = {(a, b): (c, d) for a, b, c, d in _json_loads(_patch_endpoint_v9e2_os.environ.get('W2_R2', '[[11,13,0,2],[10,14,0,3],[7,17,3,6],[6,18,4,7]]'))}

    def _patch_endpoint_v9e2_apply(ctx):
        divider = ctx.phase.BINDING.divider
        assert divider is ctx.old.divider
        divider.phase_endpoint = _patch_endpoint_v9e2__core.make_endpoint(ctx.phase, _patch_endpoint_v9e2_E_HOLD, _patch_endpoint_v9e2_F_HOLD, _patch_endpoint_v9e2_R2)

def _initialize_patch_fwd_narrow():
    global _patch_fwd_narrow_INTEGRATED_ROOT, _patch_fwd_narrow__IntegratedPath, _patch_fwd_narrow___file__, _patch_fwd_narrow___name__, _patch_fwd_narrow_apply

    def _patch_fwd_narrow_apply(ctx):
        norm = ctx.components['normalization']
        route_lane, rows = (norm.route_lane, norm.FORWARD_ROWS)
        assert all((rows[j - 1] >> 6 & 1 == 0 for j in (2, 4, 6, 8, 10)))

        def forward(builder, x, flags):
            x = list(x)
            flags = list(flags)
            assert len(x) == 22 and len(flags) == 4
            h = x[21]
            builder.x(h)
            P = {1: h}
            builder.cx(h, x[0])
            builder.cx(h, x[1])
            q = builder.alloc_qubits(1)[0]
            builder.cx(h, q)
            builder.cx(x[20], q)
            P[2] = q
            builder.cx(h, x[20])
            builder.cx(q, x[20])
            builder.x(h)
            builder.cx(q, h)
            builder.cx(q, x[0])
            builder.cx(q, x[1])
            for L in range(3, 21):
                i = 22 - L
                q = builder.alloc_qubits(1)[0]
                builder.x(x[i])
                builder.ccx(P[L - 1], x[i], q)
                builder.x(x[i])
                P[L] = q
                builder.cx(P[L - 1], x[i])
                builder.cx(q, x[i])
                builder.cx(q, h)
                builder.cx(q, x[0])
                if L <= 19:
                    builder.cx(q, x[1])
                if L % 2 == 0:
                    odd, low, up = (P[L - 1], P[L - 2], P[L])
                    m = builder.alloc_bits(1)[0]
                    builder.hmr(odd, m)
                    builder.push_condition(m)
                    builder.z(low)
                    builder.cz(low, h)
                    builder.cz(up, h)
                    builder.pop_condition()
                    builder.free(m)
                    builder.free(odd)
                    del P[L - 1]
            T = [P[2 * j] for j in range(1, 11)]
            builder.ccx(T[-1], x[1], h)
            builder.x(x[0])
            builder.cx(h, x[0])
            builder.x(x[1])
            builder.cx(h, x[1])
            for bit, flag in enumerate(flags):
                for j in range(1 << bit, 11, 1 << bit):
                    builder.cx(T[j - 1], flag)
            route_lane(builder, x[0::2], T)
            route_lane(builder, x[1:21:2], T)
            builder.x(x[20])
            builder.cx(x[21], x[20])
            k0 = flags[0]
            for j in (1, 3, 5, 7, 9):
                q = T[j - 1]
                outcome = builder.alloc_bits(1)[0]
                builder.hmr(q, outcome)
                builder.push_condition(outcome)
                upper = T[j]
                builder.z(upper)
                if j == 1:
                    builder.z(k0)
                else:
                    builder.cz(k0, T[j - 2])
                builder.cz(k0, upper)
                builder.pop_condition()
                builder.free(outcome)
                builder.free(q)
            for j in (2, 4, 6, 8, 10):
                q, row = (T[j - 1], rows[j - 1])
                outcome = builder.alloc_bits(1)[0]
                builder.hmr(q, outcome)
                builder.push_condition(outcome)
                for mask in range(1, 11):
                    if row >> mask - 1 & 1 == 0:
                        continue
                    controls = [flags[i] for i in range(4) if mask >> i & 1]
                    if len(controls) == 1:
                        builder.z(controls[0])
                    else:
                        assert len(controls) == 2
                        builder.cz(*controls)
                builder.pop_condition()
                builder.free(outcome)
                builder.free(q)
        norm.forward = forward

def _initialize_patch_h2ret():
    global _patch_h2ret_INTEGRATED_ROOT, _patch_h2ret_STATE, _patch_h2ret__IntegratedPath, _patch_h2ret___file__, _patch_h2ret___name__, _patch_h2ret__and_into, _patch_h2ret__form, _patch_h2ret__unform, _patch_h2ret_apply, _patch_h2ret_rebuild_h2
    _patch_h2ret_STATE = dict(erase_calls=0, hlow=None, outcome=None, applied=0)

    def _patch_h2ret__form(builder, wires):
        """XOR of wires onto a fresh temporary (returns (wire, owned))."""
        if len(wires) == 1:
            return (wires[0], False)
        t = builder.alloc_qubits(1)[0]
        for w in wires:
            builder.cx(w, t)
        return (t, True)

    def _patch_h2ret__unform(builder, t, owned, wires):
        if owned:
            for w in wires:
                builder.cx(w, t)
            builder.free(t)

    def _patch_h2ret__and_into(builder, left, right, target):
        a, oa = _patch_h2ret__form(builder, left)
        b, ob = _patch_h2ret__form(builder, right)
        builder.ccx(a, b, target)
        _patch_h2ret__unform(builder, b, ob, right)
        _patch_h2ret__unform(builder, a, oa, left)

    def _patch_h2ret_rebuild_h2(builder, D, H0, H1):
        D9, D10, D11, D12 = (D[9], D[10], D[11], D[12])
        L0 = [D9, D10, D11, H1]
        R0 = [D10, H0]
        M = [D9, D10, D11, D12, H0, H1]
        t = builder.alloc_qubits(1)[0]
        for w in (D10, D11, D12):
            builder.cx(w, t)
        _patch_h2ret__and_into(builder, [D9, D11], [D9, H1], t)
        g0 = builder.alloc_qubits(1)[0]
        _patch_h2ret__and_into(builder, L0, R0, g0)
        _patch_h2ret__and_into(builder, [g0], M, t)
        m = builder.alloc_bits(1)[0]
        builder.hmr(g0, m)
        builder.free(g0)
        a, oa = _patch_h2ret__form(builder, L0)
        b, ob = _patch_h2ret__form(builder, R0)
        builder.push_condition(m)
        builder.cz(a, b)
        builder.pop_condition()
        _patch_h2ret__unform(builder, b, ob, R0)
        _patch_h2ret__unform(builder, a, oa, L0)
        builder.free(m)
        return t

    def _patch_h2ret_apply(ctx):
        bl = ctx.baseline
        lc = ctx.components['lifecycle']
        previous_erase = bl.erase_high_H
        previous_inverse = lc.product_inverse
        previous_cleanup = bl.seed_cleanup

        def erase_high_H(builder, v, D, H, *, initial=False):
            out = previous_erase(builder, v, D, H, initial=initial)
            if not initial:
                _patch_h2ret_STATE['erase_calls'] += 1
                if _patch_h2ret_STATE['erase_calls'] == 2:
                    out = list(out)
                    _patch_h2ret_STATE['hlow'] = out
            return out

        def product_inverse(builder, v, D, word, token, dirty):
            hlow = _patch_h2ret_STATE['hlow']
            assert hlow is not None and len(hlow) == 3 and (hlow[2] is not None)
            h2 = hlow[2]
            assert sum((1 for q in dirty if q is h2)) == 1
            m = builder.alloc_bits(1)[0]
            builder.hmr(h2, m)
            builder.free(h2)
            hlow[2] = None
            _patch_h2ret_STATE['outcome'] = m
            dirty = [q for q in dirty if q is not h2]
            return previous_inverse(builder, v, D, word, token, dirty)

        def seed_cleanup(builder, v, D, seed, token):
            out = previous_cleanup(builder, v, D, seed, token)
            hlow = _patch_h2ret_STATE['hlow']
            if hlow is not None and hlow[2] is None:
                t = _patch_h2ret_rebuild_h2(builder, D, hlow[0], hlow[1])
                m = _patch_h2ret_STATE['outcome']
                _patch_h2ret_STATE['outcome'] = None
                builder.push_condition(m)
                builder.z(t)
                builder.pop_condition()
                builder.free(m)
                hlow[2] = t
                _patch_h2ret_STATE['applied'] += 1
            return out
        bl.erase_high_H = erase_high_H
        lc.product_inverse = product_inverse
        bl.seed_cleanup = seed_cleanup

def _initialize_patch_hret_sat_s15k7a():
    global _patch_hret_sat_s15k7a_EXTRA, _patch_hret_sat_s15k7a_FORCE, _patch_hret_sat_s15k7a_FORMULAS, _patch_hret_sat_s15k7a_INTEGRATED_ROOT, _patch_hret_sat_s15k7a_Path, _patch_hret_sat_s15k7a_RETIRE, _patch_hret_sat_s15k7a__IntegratedPath, _patch_hret_sat_s15k7a__RELAXED, _patch_hret_sat_s15k7a__ROLES, _patch_hret_sat_s15k7a__SAT, _patch_hret_sat_s15k7a___file__, _patch_hret_sat_s15k7a___name__, _patch_hret_sat_s15k7a__cleanup, _patch_hret_sat_s15k7a__emit_sat, _patch_hret_sat_s15k7a__feed_row, _patch_hret_sat_s15k7a__json, _patch_hret_sat_s15k7a__k, _patch_hret_sat_s15k7a__kernel, _patch_hret_sat_s15k7a__pair_forms, _patch_hret_sat_s15k7a__plan, _patch_hret_sat_s15k7a__undo, _patch_hret_sat_s15k7a_apply, _patch_hret_sat_s15k7a_cleanup_divider, _patch_hret_sat_s15k7a_f, _patch_hret_sat_s15k7a_i, _patch_hret_sat_s15k7a_importlib, _patch_hret_sat_s15k7a_json, _patch_hret_sat_s15k7a_k, _patch_hret_sat_s15k7a_os, _patch_hret_sat_s15k7a_p, _patch_hret_sat_s15k7a_restore, _patch_hret_sat_s15k7a_restore_sat, _patch_hret_sat_s15k7a_sys
    _patch_hret_sat_s15k7a__IntegratedPath = _import_component('pathlib', 'patches/patch_hret_sat_s15k7a.py', False).Path
    _patch_hret_sat_s15k7a_INTEGRATED_ROOT = _patch_hret_sat_s15k7a__IntegratedPath(_patch_hret_sat_s15k7a___file__).resolve().parents[1]
    _patch_hret_sat_s15k7a_os = _import_component('os', 'patches/patch_hret_sat_s15k7a.py', True)
    _patch_hret_sat_s15k7a_sys = _import_component('sys', 'patches/patch_hret_sat_s15k7a.py', True)
    _patch_hret_sat_s15k7a_Path = _import_component('pathlib', 'patches/patch_hret_sat_s15k7a.py', False).Path
    _patch_hret_sat_s15k7a__RELAXED = _patch_hret_sat_s15k7a_Path('' + str(_patch_hret_sat_s15k7a_INTEGRATED_ROOT) + '/agents/divider/src/top12_kernel_relaxed.py')
    _patch_hret_sat_s15k7a_FORMULAS = {13: dict(parents=[('v', 8), ('v', 9), ('v', 10), ('v', 11), ('next',)], helpers=[dict(width=5, constant=0, linear=2, edges=[(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)])], decoder=dict(width=6, constant=0, linear=46, edges=[(1, 3), (1, 5), (3, 4), (4, 5)]), ands=2), 14: dict(parents=[('v', 7), ('v', 8), ('v', 9), ('v', 10), ('v', 11), ('next',)], helpers=[dict(width=6, constant=0, linear=0, edges=[(1, 3)]), dict(width=6, constant=0, linear=16, edges=[(0, 1), (0, 2), (0, 4), (1, 4), (1, 5), (2, 4), (2, 5), (4, 5)])], decoder=dict(width=8, constant=0, linear=186, edges=[(0, 2), (0, 3), (0, 4), (0, 5), (0, 7), (1, 2), (1, 4), (1, 6), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 4), (3, 5), (3, 6), (4, 5), (4, 7), (5, 7), (6, 7)]), ands=4)}
    _patch_hret_sat_s15k7a_EXTRA = _patch_hret_sat_s15k7a_Path('' + str(_patch_hret_sat_s15k7a_INTEGRATED_ROOT) + '/agents/divider/build_base/extra_formulas.json')
    if _exists(_patch_hret_sat_s15k7a_EXTRA):
        _patch_hret_sat_s15k7a_json = _import_component('json', 'patches/patch_hret_sat_s15k7a.py', True)
        for _patch_hret_sat_s15k7a_k, _patch_hret_sat_s15k7a_f in _json_loads(_read_text(_patch_hret_sat_s15k7a_EXTRA)).items():
            _patch_hret_sat_s15k7a_FORMULAS[int(_patch_hret_sat_s15k7a_k)] = dict(parents=[tuple(p) for p in _patch_hret_sat_s15k7a_f['parents']], helpers=_patch_hret_sat_s15k7a_f['helpers'], decoder=_patch_hret_sat_s15k7a_f['decoder'], ands=_patch_hret_sat_s15k7a_f['ands'], nested=_patch_hret_sat_s15k7a_f.get('nested', False))
    _patch_hret_sat_s15k7a_RETIRE = tuple((int(x) for x in _patch_hret_sat_s15k7a_os.environ.get('DIVIDER_RETIRE', '13,14').split(',')))
    if _patch_hret_sat_s15k7a_os.environ.get('DIVIDER_PLACEHOLDER'):
        for _patch_hret_sat_s15k7a__k in _patch_hret_sat_s15k7a_RETIRE:
            _patch_hret_sat_s15k7a_FORMULAS.setdefault(_patch_hret_sat_s15k7a__k, dict(parents=[('v', 0)], helpers=[], decoder=dict(width=1, constant=0, linear=1, edges=[]), ands=0))
    _patch_hret_sat_s15k7a_FORCE = int(_patch_hret_sat_s15k7a_os.environ.get('DIVIDER_FORCE_CAP', '0'))
    _patch_hret_sat_s15k7a__SAT = {}
    _patch_hret_sat_s15k7a__SAT[15] = _json_loads(_read_text(_patch_hret_sat_s15k7a_Path('' + str(_patch_hret_sat_s15k7a_INTEGRATED_ROOT) + '/agents/composer/p/hret_s15k7a_s15.json')))
    assert _patch_hret_sat_s15k7a__SAT[15]['status'] == 'SAT'
    _patch_hret_sat_s15k7a__ROLES = dict((x.split('=') for x in 'q16=v6,q17=v7,q18=v8,q19=v9,q20=v10,q42=v11,q30=next'.split(',')))
    _patch_hret_sat_s15k7a__ROLES.update({'v%d' % i: 'v%d' % i for i in range(12)})
    _patch_hret_sat_s15k7a__ROLES.update({'s%d' % (k + 1): 'next' for k in _patch_hret_sat_s15k7a__SAT})
    if _patch_hret_sat_s15k7a__SAT:
        _patch_hret_sat_s15k7a_RETIRE = tuple(sorted(set(_patch_hret_sat_s15k7a_RETIRE) | set(_patch_hret_sat_s15k7a__SAT)))

    def _patch_hret_sat_s15k7a__pair_forms(b, SA, SB):
        SA = list(dict.fromkeys(SA))
        SB = list(dict.fromkeys(SB))
        ops = []
        a = SA[0]
        for w in SA[1:]:
            b.cx(w, a)
            ops.append((w, a))
        if a in SB:
            SBc = set(SA) - {a} ^ set(SB) - {a}
            SBc.add(a)
        else:
            SBc = set(SB)
        cands = [w for w in SB if w in SBc and w != a] + [w for w in SA if w in SBc and w != a] + [w for w in SBc if w != a]
        assert cands, 'degenerate AND'
        bp = cands[0]
        for w in [x for x in SB + SA + [a] if x in SBc and x != bp]:
            if (w, bp) in ops:
                continue
            b.cx(w, bp)
            ops.append((w, bp))
        return (a, bp, ops)

    def _patch_hret_sat_s15k7a__undo(b, ops):
        for c, t in reversed(ops):
            b.cx(c, t)

    def _patch_hret_sat_s15k7a__emit_sat(b, form, wires, target):
        n = len(form['inputs'])
        gates = form['gates']
        vals = list(wires)
        used_later = [any((n + i in g2['left'] or n + i in g2['right'] for g2 in gates[i + 1:])) for i in range(len(gates))]
        out_terms = set(form['output']['terms'])
        helpers = []
        for j in out_terms:
            if j < n:
                b.cx(vals[j], target)
        if form['output']['constant']:
            b.x(target)
        for i, g in enumerate(gates):
            lw = [vals[j] for j in g['left']]
            rw = [vals[j] for j in g['right']]
            h = b.alloc_qubits(1)[0] if used_later[i] else target
            wa, wb, ops = _patch_hret_sat_s15k7a__pair_forms(b, lw, rw)
            b.ccx(wa, wb, h)
            _patch_hret_sat_s15k7a__undo(b, ops)
            if used_later[i]:
                vals.append(h)
                helpers.append((h, lw, rw))
                if n + i in out_terms:
                    b.cx(h, target)
            else:
                assert n + i in out_terms
                vals.append(None)
        for h, lw, rw in reversed(helpers):
            m = b.alloc_bits(1)[0]
            b.hmr(h, m)
            b.free(h)
            wa, wb, ops = _patch_hret_sat_s15k7a__pair_forms(b, lw, rw)
            b.push_condition(m)
            b.cz(wa, wb)
            b.pop_condition()
            _patch_hret_sat_s15k7a__undo(b, ops)
            b.free(m)

    def _patch_hret_sat_s15k7a_restore_sat(d, b, token, k, outcome):
        form = _patch_hret_sat_s15k7a__SAT[k]
        v = token.v
        wires = []
        for name in form['inputs']:
            role = _patch_hret_sat_s15k7a__ROLES[name]
            wires.append(token.u[-1] if role == 'next' else v[int(role[1:])])
        s = b.alloc_qubits(1)[0]
        _patch_hret_sat_s15k7a__emit_sat(b, form, wires, s)
        b.push_condition(outcome)
        b.z(s)
        b.pop_condition()
        b.free(outcome)
        token.history[k] = s
        initial = list(token.initial_u)
        initial[25 - k] = s
        token.initial_u = tuple(initial)
        return s

    def _patch_hret_sat_s15k7a__kernel(b):
        if b.max_qubits >= 48:
            return _patch_hret_sat_s15k7a_sys.modules['top12_kernel']
        name = 'divider_top12_kernel_relaxed'
        if name not in _patch_hret_sat_s15k7a_sys.modules:
            spec = _spec(name, _patch_hret_sat_s15k7a__RELAXED)
            module = _new_module(spec)
            _patch_hret_sat_s15k7a_sys.modules[name] = module
            spec.loader.exec_module(module)
        return _patch_hret_sat_s15k7a_sys.modules[name]

    def _patch_hret_sat_s15k7a__plan(d, p):
        return d.cb.factor_polynomial(p['width'], bool(p['constant']), p['linear'], set(map(tuple, p['edges'])))

    def _patch_hret_sat_s15k7a_restore(d, b, token, k, outcome):
        f = _patch_hret_sat_s15k7a_FORMULAS[k]
        v = token.v
        base = [v[x[1]] if x[0] == 'v' else token.u[-1] for x in f['parents']]
        helpers, hplans, hvars = ([], [], [])
        for h in f['helpers']:
            variables = base + helpers[:h['width'] - len(base)]
            p = _patch_hret_sat_s15k7a__plan(d, h)
            g = b.alloc_qubits(1)[0]
            d.cb.emit_xor(b, variables, g, p)
            helpers.append(g)
            hplans.append(p)
            hvars.append(variables)
        dplan = _patch_hret_sat_s15k7a__plan(d, f['decoder'])
        assert sum((p.and_count for p in hplans)) + dplan.and_count == f['ands'], (k, [p.and_count for p in hplans], dplan.and_count)
        s = b.alloc_qubits(1)[0]
        d.cb.emit_xor(b, base + helpers, s, dplan)
        b.push_condition(outcome)
        b.z(s)
        b.pop_condition()
        b.free(outcome)
        for g, p, variables in reversed(list(zip(helpers, hplans, hvars))):
            d._erase(b, g, variables, p)
        token.history[k] = s
        initial = list(token.initial_u)
        initial[25 - k] = s
        token.initial_u = tuple(initial)
        return s

    def _patch_hret_sat_s15k7a__feed_row(d, b, token, j):
        v = token.v
        u = token.u
        low = u[0]
        target = u[1:]
        sign = token.history[j]
        cur = token.P[23 - j] if j < 24 else None
        debt = token._debt
        carry = d._feed_carry(b, v, low, cur, sign)
        d._frame(b, sign, target)
        d._leading_offset(b, target, inverse=True)
        released = d.inverse_add(b, v[1:], target, debt, carry_in=carry, dirty_wires=d._dirty(token), carry_lifecycle=(lambda value: d._feed_erase(b, value, v, low, cur, sign), lambda: d._feed_carry(b, v, low, cur, sign)))
        d._frame(b, sign, target)
        if not released:
            d._feed_erase(b, carry, v, low, cur, sign)
        if cur is not None:
            b.cx(cur, low)
        b.cx(sign, low)
        b.cx(v[0], low)
        token.P[24 - j] = low
        token.u = target + [sign]
        del token.history[j]

    def _patch_hret_sat_s15k7a_cleanup_divider(d, b, token):
        original_cap = b.max_qubits
        if _patch_hret_sat_s15k7a_FORCE:
            b.set_max_qubits(_patch_hret_sat_s15k7a_FORCE)
        try:
            return _patch_hret_sat_s15k7a__cleanup(d, b, token)
        finally:
            if _patch_hret_sat_s15k7a_FORCE:
                b.set_max_qubits(original_cap)

    def _patch_hret_sat_s15k7a__cleanup(d, b, token):
        assert b.max_qubits >= 46 and b.num_allocated_qubits == 43
        assert not token.consumed and len(token.rows) == 24
        assert sorted(token.history) == list(range(12, 25))
        token.consumed = True
        v = token.v
        old_sign = token.history.pop(12)
        next_sign = token.history[13]
        outcome = b.alloc_bits(1)[0]
        b.hmr(old_sign, outcome)
        b.free(old_sign)
        b.push_condition(outcome)
        b.z(v[11])
        b.z(v[10])
        b.cz(v[10], next_sign)
        b.pop_condition()
        b.free(outcome)
        outcomes = {}
        for k in _patch_hret_sat_s15k7a_RETIRE:
            w = token.history.pop(k)
            o = b.alloc_bits(1)[0]
            b.hmr(w, o)
            b.free(w)
            outcomes[k] = o
        data = 42 - len(_patch_hret_sat_s15k7a_RETIRE)
        assert b.num_allocated_qubits == data
        for j, k, debt in reversed(token.rows):
            if j in outcomes:
                if j in _patch_hret_sat_s15k7a__SAT:
                    _patch_hret_sat_s15k7a_restore_sat(d, b, token, j, outcomes.pop(j))
                else:
                    _patch_hret_sat_s15k7a_restore(d, b, token, j, outcomes.pop(j))
                data += 1
                assert b.num_allocated_qubits == data
            if j == 12:
                assert not token.history and (not outcomes)
                rebuilt = b.alloc_qubits(1)[0]
                b.cx(v[11], rebuilt)
                b.cx(v[10], rebuilt)
                b.ccx(v[10], token.u[-1], rebuilt)
                token.history[12] = rebuilt
                initial = list(token.initial_u)
                assert initial[13] == old_sign
                initial[13] = rebuilt
                token.initial_u = tuple(initial)
                if b.max_qubits >= 47:
                    result = _patch_hret_sat_s15k7a__kernel(b).last_feed_and_initial(d, b, token, debt)
                else:
                    token._debt = debt
                    _patch_hret_sat_s15k7a__feed_row(d, b, token, 12)
                    assert debt.consumed and (not debt.measurements)
                    assert tuple(token.u) == token.initial_u and (not token.history)
                    token.P = d.cleanup_u12(b, v, token.P, token.u)
                    result = list(token.P)
                assert all((x.consumed and (not x.measurements) for _, _, x in token.rows))
                assert b.num_allocated_qubits == 31
                return result
            u = token.u
            if j <= 24:
                token._debt = debt
                _patch_hret_sat_s15k7a__feed_row(d, b, token, j)
            else:
                b.cx(v[0], u[0])
                sign = u[0]
                target = u[k + 1:]
                d._frame(b, sign, target)
                d._leading_offset(b, target, inverse=True)
                d.inverse_add(b, v[k + 1:], target, debt, carry_in=v[k], dirty_wires=d._dirty(token))
                d._frame(b, sign, target)
                token.u = u[1:] + u[:1]
            assert debt.consumed and (not debt.measurements) and (b.num_allocated_qubits == data), (j, b.num_allocated_qubits)
        raise AssertionError('The final feed was not reached')

    def _patch_hret_sat_s15k7a_apply(ctx):
        divider = ctx.old.divider

        def bound(b, token):
            return _patch_hret_sat_s15k7a_cleanup_divider(divider, b, token)
        divider.cleanup_divider = bound

def _initialize_patch_ld_first20_56b8():
    global _patch_ld_first20_56b8_DEFAULT, _patch_ld_first20_56b8_DEFAULT_SHA, _patch_ld_first20_56b8_INTEGRATED_ROOT, _patch_ld_first20_56b8_MODEL_SHA, _patch_ld_first20_56b8_Path, _patch_ld_first20_56b8_REPORT, _patch_ld_first20_56b8__IntegratedPath, _patch_ld_first20_56b8___file__, _patch_ld_first20_56b8___name__, _patch_ld_first20_56b8__certificate, _patch_ld_first20_56b8_apply, _patch_ld_first20_56b8_hashlib, _patch_ld_first20_56b8_json, _patch_ld_first20_56b8_os
    _patch_ld_first20_56b8__IntegratedPath = _import_component('pathlib', 'patches/patch_ld_first20_56b8.py', False).Path
    _patch_ld_first20_56b8_INTEGRATED_ROOT = _patch_ld_first20_56b8__IntegratedPath(_patch_ld_first20_56b8___file__).resolve().parents[1]
    _patch_ld_first20_56b8_hashlib = _import_component('hashlib', 'patches/patch_ld_first20_56b8.py', True)
    _patch_ld_first20_56b8_os = _import_component('os', 'patches/patch_ld_first20_56b8.py', True)
    _patch_ld_first20_56b8_Path = _import_component('pathlib', 'patches/patch_ld_first20_56b8.py', False).Path
    _patch_ld_first20_56b8_DEFAULT = _patch_ld_first20_56b8_Path('' + str(_patch_ld_first20_56b8_INTEGRATED_ROOT) + '/agents/loader2/certs/first_cap20_56b8.json')
    _patch_ld_first20_56b8_DEFAULT_SHA = 'f09657772c5fdba988c5dae5e599c003e635cc000d4aa53093362d0846332ec9'
    _patch_ld_first20_56b8_REPORT = {}

    def _patch_ld_first20_56b8__certificate():
        path = _patch_ld_first20_56b8_Path(_patch_ld_first20_56b8_os.environ.get('LD_FIRST_JSON', str(_patch_ld_first20_56b8_DEFAULT)))
        raw = _read_bytes(path)
        sha = _patch_ld_first20_56b8_hashlib.sha256(raw).hexdigest()
        if path == _patch_ld_first20_56b8_DEFAULT and _patch_ld_first20_56b8_DEFAULT_SHA:
            pass
        data = _json_loads(raw)
        assert data['status'] == 'COMPLETE_MATHEMATICAL_LOADER_NOT_NATIVE'
        pass
        assert data['fixed_address_slots'] == list(range(7)) and data['reusable_input_slots'] == []
        assert data['work_cap'] == data['work_peak'] == 20
        hmr = sum((len(st['discarded_truths']) for st in data['steps'] if st['kind'] == 'Clifford_frame_then_HMR'))
        _patch_ld_first20_56b8_REPORT.update(path=str(path), sha256=sha, Toffolis=data['Toffolis'], HMR_debts=hmr)
        return (data, hmr)

    def _patch_ld_first20_56b8_apply(ctx):
        tables = ctx.tables
        original = tables.load_joint16
        km, cb = (tables.km, tables.cb)
        data, hmr_expected = _patch_ld_first20_56b8__certificate()

        def load_joint16(builder, address7, *, variant, debts):
            if variant != 'first':
                return original(builder, address7, variant=variant, debts=debts)
            address = list(address7)
            if len(address) != 7 or len(set(address)) != 7 or (not all((isinstance(q, km.q) for q in address))):
                raise ValueError('Expected seven current, distinct quantum address owners.')
            if not isinstance(debts, tables.TableDebts):
                raise TypeError('Expected the shared pinned TableDebts owner.')
            entry = builder.num_allocated_qubits
            before_debts = debts.total_recorded
            fixed = list(address)
            work = []
            cap = data['work_cap']
            available = list(builder.alloc_qubits(cap))
            offset = 1 + len(fixed)
            count = 0
            for item in data['steps']:
                kind = item['kind']
                if kind in ('bank', 'CCX_new_coordinate'):
                    target = available.pop(0)
                    plan = tables.plan_from_json(item['plan'])
                    cb.emit_xor(builder, fixed + work, target, plan)
                    work.append(target)
                    count += plan.and_count
                elif kind == 'Clifford_zero_dependent_coordinate':
                    index = item['index']
                    target = work[index]
                    tables._BASE._affine_xor(builder, fixed, work[:index], target, item['expression'])
                    work.pop(index)
                    available.append(target)
                elif kind == 'Clifford_frame_then_HMR':
                    assert item['affine_fixed_offset'] == offset
                    tables.emit_affine_frame(builder, fixed, work, item['full_affine_rows'])
                    kept = item['retained_count']
                    discard = work[kept:]
                    assert len(discard) == len(item['discarded_truths'])
                    for wire, truth in zip(discard, item['discarded_truths']):
                        debts.erase(builder, wire, int(truth, 16))
                        available.append(wire)
                    work = work[:kept]
                elif kind == 'virtual_affine_product':
                    pass
                elif kind == 'XOR_product_existing_coordinate':
                    assert item['target_index'] == 0
                    plan = tables.plan_from_json(item['plan'])
                    cb.emit_xor(builder, fixed + work[1:], work[0], plan)
                    count += plan.and_count
                elif kind == 'final_output_Clifford_frame':
                    tables.emit_affine_frame(builder, fixed, work, [int(row) << offset for row in item['matrix_rows']])
                else:
                    raise AssertionError(('Unknown loader operation', kind))
                assert len(work) + len(available) == cap and len(set(work + available)) == cap
                assert not set(fixed) & set(work + available)
            assert len(work) == 16 and count == data['Toffolis']
            assert debts.total_recorded - before_debts == hmr_expected
            if available:
                builder.free(tables.array(available))
            assert builder.num_allocated_qubits == entry + 16
            _patch_ld_first20_56b8_REPORT['emitted'] = dict(Toffolis=count, HMR=hmr_expected)
            return (list(work[:13]), list(work[13:]))
        tables.load_joint16 = load_joint16

def _initialize_patch_proddisp():
    global _patch_proddisp_INTEGRATED_ROOT, _patch_proddisp__IntegratedPath, _patch_proddisp___file__, _patch_proddisp___name__, _patch_proddisp_apply, _patch_proddisp_make

    def _patch_proddisp_make(baseline):
        km = baseline.km

        def forward_add_disposable(arithmetic, builder, source, target, *, carry_in, erase_input):
            assert isinstance(carry_in, km.q) and callable(erase_input)
            a, b, preserve = arithmetic._inputs(source, target, carry_in, False)
            width = len(b)
            debts = {}
            released = False
            assert preserve is None and width > 2

            def measure(carry, position):
                if carry is False:
                    return
                outcome = builder.alloc_bits(1)[0]
                builder.hmr(carry, outcome)
                builder.free(carry)
                debts[position] = outcome
            carry = carry_in
            for index, (aa, bb) in enumerate(zip(a[:-2], b[:-2])):
                frame = arithmetic._compute_carry(builder, aa, bb, carry, preserve=preserve)
                arithmetic._sum_keep_carry(builder, frame)
                if index == 0:
                    assert frame.incoming == carry_in and frame.outgoing is not False and (frame.outgoing != carry_in)
                    erase_input(carry_in)
                    released = True
                if index:
                    measure(carry, index)
                carry = frame.outgoing
            arithmetic._finish_top(builder, a, b, carry, preserve)
            measure(carry, width - 2)
            return (arithmetic.CarryDebt(debts, width), released)

        def product_forward(builder, D, seed, h):
            word = list(seed) + list(h)
            C = [False] + list(D)
            rows = []
            builder.x(word[15])
            for i in range(10):
                q = word[6 + i]
                target = word[:6 + i]
                source = C[9 - i:] if i < 9 else C
                for t in target:
                    builder.cx(q, t)
                carry = baseline._product_carry(builder, C, q, i)
                if i < 8:
                    debt, released = forward_add_disposable(baseline.product_ar, builder, source, target, carry_in=carry, erase_input=lambda value, i=i, q=q: baseline._clear_product_carry(builder, C, q, i, value))
                    assert released
                else:
                    debt = baseline.product_ar.forward_add(builder, source, target, carry_in=carry)
                    released = False
                rows.append(debt)
                if not released:
                    baseline._clear_product_carry(builder, C, q, i, carry)
                for t in target:
                    builder.cx(q, t)
            builder.x(word[15])
            return (word, baseline.ProductToken(rows))
        return product_forward

    def _patch_proddisp_apply(ctx):
        ctx.baseline.product_forward = _patch_proddisp_make(ctx.baseline)

def _initialize_patch_q47_decoder_resynth2():
    global _patch_q47_decoder_resynth2_DATA, _patch_q47_decoder_resynth2_HERE, _patch_q47_decoder_resynth2_INTEGRATED_ROOT, _patch_q47_decoder_resynth2_Path, _patch_q47_decoder_resynth2_REPORT, _patch_q47_decoder_resynth2_T2_SHA_PREFIX, _patch_q47_decoder_resynth2__IntegratedPath, _patch_q47_decoder_resynth2___file__, _patch_q47_decoder_resynth2___name__, _patch_q47_decoder_resynth2__bits, _patch_q47_decoder_resynth2__emit, _patch_q47_decoder_resynth2__erase_cap, _patch_q47_decoder_resynth2_apply, _patch_q47_decoder_resynth2_copy, _patch_q47_decoder_resynth2_hashlib, _patch_q47_decoder_resynth2_json, _patch_q47_decoder_resynth2_rewrite, _patch_q47_decoder_resynth2_sys
    _patch_q47_decoder_resynth2__IntegratedPath = _import_component('pathlib', 'patches/patch_q47_decoder_resynth2.py', False).Path
    _patch_q47_decoder_resynth2_INTEGRATED_ROOT = _patch_q47_decoder_resynth2__IntegratedPath(_patch_q47_decoder_resynth2___file__).resolve().parents[1]
    _patch_q47_decoder_resynth2_copy = _import_component('copy', 'patches/patch_q47_decoder_resynth2.py', True)
    _patch_q47_decoder_resynth2_sys = _import_component('sys', 'patches/patch_q47_decoder_resynth2.py', True)
    _patch_q47_decoder_resynth2_Path = _import_component('pathlib', 'patches/patch_q47_decoder_resynth2.py', False).Path
    _patch_q47_decoder_resynth2_HERE = _patch_q47_decoder_resynth2_Path('' + str(_patch_q47_decoder_resynth2_INTEGRATED_ROOT) + '/agents/normroot')
    _patch_q47_decoder_resynth2_DATA = _patch_q47_decoder_resynth2_HERE / 'q47_t2_rewrite.json'
    _patch_q47_decoder_resynth2_REPORT = {}

    def _patch_q47_decoder_resynth2__bits(v):
        out, i = ([], 0)
        while v:
            if v & 1:
                out.append(i)
            v >>= 1
            i += 1
        return out

    def _patch_q47_decoder_resynth2__emit(plan, variables, target):
        ent = []
        if plan['constant']:
            ent.append(['X', [target], [], None])
        for b in _patch_q47_decoder_resynth2__bits(plan['product_linear']):
            ent.append(['CX', [variables[b], target], [], None])
        for left, right, i, j in plan['products']:
            frame = [(variables[k], variables[i]) for k in _patch_q47_decoder_resynth2__bits(left) if k != i]
            frame += [(variables[k], variables[j]) for k in _patch_q47_decoder_resynth2__bits(right) if k != j]
            ent += [['CX', [a, b], [], None] for a, b in frame]
            ent.append(['CCX', [variables[i], variables[j], target], [], None])
            ent += [['CX', [a, b], [], None] for a, b in reversed(frame)]
        return ent

    def _patch_q47_decoder_resynth2__erase_cap(fix):
        v = fix['variables']
        ent = []
        if fix['constant']:
            ent.append(['X', ['qcap'], [], None])
        ent.append(['HMR', ['qcap'], ['bcap_normroot'], None])
        for b in _patch_q47_decoder_resynth2__bits(fix['linear']):
            ent.append(['Z', [v[b]], [], 'bcap_normroot'])
        for i, j in fix['edges']:
            ent.append(['CZ', [v[i], v[j]], [], 'bcap_normroot'])
        ent.append(['ZERO', 'qcap'])
        return ent

    def _patch_q47_decoder_resynth2_rewrite(T2, d):
        lo = T2['lo']
        cap_op, (ca, cb, ct) = (d['capture']['donor_op'], d['capture']['ccx'])
        segs = {d['q21']['donor_target']: d['q21'], d['q13']['donor_target']: d['q13']}
        dele = {}
        for tgt, s in segs.items():
            for k in s['segment_donor_ops']:
                dele[k] = tgt
        insert = {d['q21']['reader_donor_op']: _patch_q47_decoder_resynth2__emit(d['q21']['plan'], d['q21']['variables'], d['q21']['donor_target']) + _patch_q47_decoder_resynth2__erase_cap(d['cap_fix']), d['q13']['reader_donor_op']: _patch_q47_decoder_resynth2__emit(d['q13']['plan'], d['q13']['variables'], d['q13']['donor_target'])}
        spans = {tgt: (min(s['segment_donor_ops']), s['reader_donor_op']) for tgt, s in segs.items()}
        out, op = ([], lo)
        deleted = 0
        for item in T2['plan']:
            if item[0] == 'ZERO':
                w = item[1]
                if w in spans and spans[w][0] <= op <= spans[w][1]:
                    continue
                out.append(item)
                continue
            if op in insert:
                out.extend(insert[op])
            if op == cap_op:
                assert item[0] == 'CCX' and item[1] == [ca, cb, ct], item
                out.append(['CX', [ct, 'qcap'], [], None])
                out.append(item)
                out.append(['CX', [ct, 'qcap'], [], None])
            elif op in dele:
                tgt = dele[op]
                assert item[0] in ('X', 'CX', 'CCX') and item[1][-1] == tgt and (item[3] is None), item
                deleted += 1
            else:
                for tgt, (s0, s1) in spans.items():
                    if s0 <= op < s1:
                        assert tgt not in item[1], ('target read inside its segment', op, item)
                out.append(item)
            op += 1
        assert deleted == len(dele)
        new = dict(T2)
        new['plan'] = out
        new['ccx'] = T2['ccx'] - 2
        return new

    def _patch_q47_decoder_resynth2_apply(ctx):
        body = _patch_q47_decoder_resynth2_sys.modules.get('variant_patch_patch_w47_body')
        if body is None or getattr(body, 'TAIL', None) != 'donor':
            _patch_q47_decoder_resynth2_REPORT['status'] = 'inactive'
            return
        plan_path = _patch_q47_decoder_resynth2_Path('' + str(_patch_q47_decoder_resynth2_INTEGRATED_ROOT) + '/agents/width/plans/T2_decoder_capture.json')
        pass
        tail = body._tail_modules()
        assert tail['T2']['ccx'] == 20 and tail['T2']['lo'] == 26385
        tail['T2'] = _patch_q47_decoder_resynth2_rewrite(_patch_q47_decoder_resynth2_copy.deepcopy(tail['T2']), _json_loads(_read_text(_patch_q47_decoder_resynth2_DATA)))
        _patch_q47_decoder_resynth2_REPORT['status'] = 'T2 decoder 20 -> 18 CCX'

def _initialize_patch_second46_c19_70nb1():
    global _patch_second46_c19_70nb1_CERT, _patch_second46_c19_70nb1_CERT_SHA256, _patch_second46_c19_70nb1_HERE, _patch_second46_c19_70nb1_INTEGRATED_ROOT, _patch_second46_c19_70nb1_LOADERS, _patch_second46_c19_70nb1_Path, _patch_second46_c19_70nb1_REPORT, _patch_second46_c19_70nb1__IntegratedPath, _patch_second46_c19_70nb1___file__, _patch_second46_c19_70nb1___name__, _patch_second46_c19_70nb1_apply, _patch_second46_c19_70nb1_hashlib, _patch_second46_c19_70nb1_importlib, _patch_second46_c19_70nb1_os, _patch_second46_c19_70nb1_sys
    _patch_second46_c19_70nb1__IntegratedPath = _import_component('pathlib', 'patches/patch_second46_c19_70nb1.py', False).Path
    _patch_second46_c19_70nb1_INTEGRATED_ROOT = _patch_second46_c19_70nb1__IntegratedPath(_patch_second46_c19_70nb1___file__).resolve().parents[1]
    _patch_second46_c19_70nb1_Path = _import_component('pathlib', 'patches/patch_second46_c19_70nb1.py', False).Path
    _patch_second46_c19_70nb1_os = _import_component('os', 'patches/patch_second46_c19_70nb1.py', True)
    _patch_second46_c19_70nb1_sys = _import_component('sys', 'patches/patch_second46_c19_70nb1.py', True)
    _patch_second46_c19_70nb1_HERE = _patch_second46_c19_70nb1_Path(_patch_second46_c19_70nb1___file__).resolve().parent
    _patch_second46_c19_70nb1_LOADERS = _patch_second46_c19_70nb1_HERE / 'q46_loaders.py'
    if not _exists(_patch_second46_c19_70nb1_LOADERS):
        _patch_second46_c19_70nb1_LOADERS = _patch_second46_c19_70nb1_Path('' + str(_patch_second46_c19_70nb1_INTEGRATED_ROOT) + '/agents/tk_q46/p/q46_loaders.py')
    _patch_second46_c19_70nb1_CERT = '' + str(_patch_second46_c19_70nb1_INTEGRATED_ROOT) + '/agents/loader2/certs/second_cap19_70nb1.json'
    _patch_second46_c19_70nb1_CERT_SHA256 = '3b4621d63f719928b38a3f2838de2c8d718aa6bbcdbc5a70eec706b2365e5c51'
    _patch_second46_c19_70nb1_REPORT = {}

    def _patch_second46_c19_70nb1_apply(ctx):
        pass
        _patch_second46_c19_70nb1_os.environ['TK46_SECOND_JSON'] = _patch_second46_c19_70nb1_CERT
        _patch_second46_c19_70nb1_REPORT['certificate'] = _patch_second46_c19_70nb1_CERT
        _patch_second46_c19_70nb1_REPORT['certificate_sha256'] = _patch_second46_c19_70nb1_CERT_SHA256
        name = 'tk46_q46_second_loader'
        assert name not in _patch_second46_c19_70nb1_sys.modules
        spec = _spec(name, _patch_second46_c19_70nb1_LOADERS)
        module = _new_module(spec)
        _patch_second46_c19_70nb1_sys.modules[name] = module
        spec.loader.exec_module(module)
        assert _patch_second46_c19_70nb1_Path(module.OWN_SECOND).resolve() == _patch_second46_c19_70nb1_Path(_patch_second46_c19_70nb1_CERT).resolve()
        tables = ctx.tables
        adapted = module.adapter(tables)
        original = tables.load_joint16

        def load_joint16(builder, address7, *, variant, debts):
            if variant == 'second':
                return adapted.load_joint16(builder, address7, variant='second', debts=debts)
            return original(builder, address7, variant=variant, debts=debts)
        tables.load_joint16 = load_joint16

def _initialize_patch_seedinv():
    global _patch_seedinv_INTEGRATED_ROOT, _patch_seedinv_STATE, _patch_seedinv__IntegratedPath, _patch_seedinv___file__, _patch_seedinv___name__, _patch_seedinv_apply, _patch_seedinv_make_seed_cleanup, _patch_seedinv_product_inverse
    _patch_seedinv_STATE = {}

    def _patch_seedinv_product_inverse(builder, v, D, word, token, dirty, *, baseline):
        km = baseline.km
        D, word, dirty = (list(D), list(word), list(dirty))
        assert len(D) == 13 and len(word) == 16 and (len(token.rows) == 10)
        entry = builder.num_allocated_qubits
        outcomes = {}
        for i in (0, 1, 3):
            old = v[i]
            assert isinstance(old, km.q) and dirty.count(old) == 1
            m = builder.alloc_bits(1)[0]
            builder.hmr(old, m)
            builder.free(old)
            outcomes[i] = m
            v[i] = None
            dirty.remove(old)
        C = [False] + D
        builder.x(word[15])
        for i in reversed(range(10)):
            debt = token.rows[i]
            q = word[6 + i]
            target = word[:6 + i]
            source = C[9 - i:] if i < 9 else C
            for t in target:
                builder.cx(q, t)
            carry = baseline._product_carry(builder, C, q, i)

            def erase(value, i=i, q=q):
                baseline._clear_product_carry(builder, C, q, i, value)

            def regenerate(i=i, q=q):
                return baseline._product_carry(builder, C, q, i)
            released = baseline.product_ar.inverse_add(builder, source, target, debt, carry_in=carry, dirty_wires=dirty + word[6:], carry_lifecycle=(erase, regenerate) if i < 8 else None)
            if not released:
                baseline._clear_product_carry(builder, C, q, i, carry)
            for t in target:
                builder.cx(q, t)
            assert debt.consumed and (not debt.measurements)
        builder.x(word[15])
        assert builder.num_allocated_qubits == entry - 3
        _patch_seedinv_STATE['outcomes'] = outcomes
        return (word[:6], word[6:])

    def _patch_seedinv_make_seed_cleanup(b):
        ar, km = (b.ar, b.km)

        def seed_cleanup(builder, v, D, seed, token):
            seed = list(seed)
            assert len(seed) == 6 and len(token.rows) == 3
            assert all((v[i] is None for i in (0, 1, 3)))
            outcomes = _patch_seedinv_STATE.pop('outcomes')
            for j in reversed(range(3)):
                ar.inverse_signed_row(builder, D, seed[:3 + j], token.rows[j], shift=-(11 - j), sign=seed[3 + j])
            builder.x(km.array(seed[:3]))
            builder.free(km.array(seed[:3]))
            for j, i in enumerate((0, 1, 3)):
                builder.x(seed[3 + j])
                v[i] = seed[3 + j]
            b.seed_root_frame(builder, v, inverse=True)
            for i in (0, 1, 3):
                m = outcomes.pop(i)
                builder.push_condition(m)
                builder.z(v[i])
                builder.pop_condition()
                builder.free(m)
            assert all((d.consumed and (not d.measurements) for d in token.rows))
        return seed_cleanup

    def _patch_seedinv_apply(ctx):
        baseline = ctx.baseline
        lifecycle = ctx.components['lifecycle']

        def installed(builder, v, D, word, token, dirty):
            return _patch_seedinv_product_inverse(builder, v, D, word, token, dirty, baseline=baseline)
        lifecycle.product_inverse = installed
        baseline.seed_cleanup = _patch_seedinv_make_seed_cleanup(baseline)

def _initialize_patch_w47_body():
    global _patch_w47_body_A6_AROUND_PRODUCT, _patch_w47_body_A6_EARLY, _patch_w47_body_CTX, _patch_w47_body_DONOR, _patch_w47_body_INTEGRATED_ROOT, _patch_w47_body_PACK, _patch_w47_body_Path, _patch_w47_body_SNAPSHOT2_TAIL, _patch_w47_body_SNAP_PATH, _patch_w47_body_STATE, _patch_w47_body_TAIL, _patch_w47_body_UNPACK_AFTER_SEED, _patch_w47_body__IntegratedPath, _patch_w47_body__TAIL, _patch_w47_body___file__, _patch_w47_body___name__, _patch_w47_body__load_src, _patch_w47_body__mark, _patch_w47_body__pack, _patch_w47_body__role_map, _patch_w47_body__snapshot_module, _patch_w47_body__tail_modules, _patch_w47_body_apply, _patch_w47_body_emit_body, _patch_w47_body_importlib, _patch_w47_body_sys, _patch_w47_body_types, _patch_w47_body_unpack_h0, _patch_w47_body_unpack_h0_after_seed
    _patch_w47_body__IntegratedPath = _import_component('pathlib', 'patches/patch_w47_body.py', False).Path
    _patch_w47_body_INTEGRATED_ROOT = _patch_w47_body__IntegratedPath(_patch_w47_body___file__).resolve().parents[1]
    _patch_w47_body_types = _import_component('types', 'patches/patch_w47_body.py', True)
    _patch_w47_body_sys = _import_component('sys', 'patches/patch_w47_body.py', True)
    _patch_w47_body_Path = _import_component('pathlib', 'patches/patch_w47_body.py', False).Path
    _patch_w47_body_CTX = None
    _patch_w47_body_STATE = dict(flags=None, packed=False)
    _patch_w47_body_SNAPSHOT2_TAIL = True
    _patch_w47_body_TAIL = 'donor'
    _patch_w47_body_A6_AROUND_PRODUCT = True
    _patch_w47_body_A6_EARLY = True
    _patch_w47_body_PACK = False
    _patch_w47_body_SNAP_PATH = _patch_w47_body_Path('' + str(_patch_w47_body_INTEGRATED_ROOT) + '/agents/width/src/decoder_snapshot_cleanup_q48.py')

    def _patch_w47_body__snapshot_module():
        name = 'width_pro2_decoder_snapshot_cleanup_q48'
        if name not in _patch_w47_body_sys.modules:
            spec = _spec(name, _patch_w47_body_SNAP_PATH)
            module = _new_module(spec)
            _patch_w47_body_sys.modules[name] = module
            spec.loader.exec_module(module)
        return _patch_w47_body_sys.modules[name]

    def _patch_w47_body__pack(builder, h0, Q, c, flags):
        b = builder
        b.x(h0)
        for q in (Q[2], Q[3], Q[4], c):
            b.cx(q, h0)
        b.cx(h0, flags[2])
        b.cx(h0, flags[3])
        m = b.alloc_bits(1)[0]
        b.hmr(h0, m)
        b.free(h0)
        b.push_condition(m)
        b.cz(flags[2], flags[3])
        b.pop_condition()
        b.free(m)

    def _patch_w47_body_unpack_h0(builder, v, h, flags):
        b = builder
        assert h[0] is None
        q = b.alloc_qubits(1)[0]
        b.ccx(flags[2], flags[3], q)
        b.cx(q, flags[2])
        b.cx(q, flags[3])
        t = b.alloc_qubits(1)[0]
        b.cx(v[0], v[1])
        b.cx(v[0], v[2])
        b.ccx(v[1], v[2], t)
        b.cx(v[0], v[2])
        b.cx(v[0], v[1])
        b.x(q)
        b.cx(v[2], q)
        b.cx(v[4], q)
        b.cx(v[0], v[3])
        b.x(v[3])
        b.ccx(t, v[3], q)
        b.x(v[3])
        b.cx(v[0], v[3])
        m = b.alloc_bits(1)[0]
        b.hmr(t, m)
        b.free(t)
        b.cx(v[0], v[1])
        b.cx(v[0], v[2])
        b.push_condition(m)
        b.cz(v[1], v[2])
        b.pop_condition()
        b.cx(v[0], v[2])
        b.cx(v[0], v[1])
        b.free(m)
        h = list(h)
        h[0] = q
        return h
    _patch_w47_body_UNPACK_AFTER_SEED = True

    def _patch_w47_body_unpack_h0_after_seed(builder, v, h, flags, seed):
        """2 Toffolis. Measured on all inputs at seed_ready (raw v0..v4 unchanged by the seed):
    (v0^v1)(v0^v2) == v0 ^ v3 ^ 1 ^ seed[5], hence
    h0 = f2'f3' ^ v0 ^ v2 ^ v3 ^ v4 ^ seed[5]*(v0^v3^1)."""
        b = builder
        assert h[0] is None and len(seed) == 6
        q = b.alloc_qubits(1)[0]
        b.ccx(flags[2], flags[3], q)
        b.cx(q, flags[2])
        b.cx(q, flags[3])
        for w in (v[0], v[2], v[3], v[4]):
            b.cx(w, q)
        b.cx(v[0], v[3])
        b.x(v[3])
        b.ccx(seed[5], v[3], q)
        b.x(v[3])
        b.cx(v[0], v[3])
        h = list(h)
        h[0] = q
        return h

    def _patch_w47_body_apply(ctx):
        global _patch_w47_body_CTX
        _patch_w47_body_CTX = ctx
        if not _patch_w47_body_PACK:
            return
        norm_mod = ctx.components['normalization']
        root_mod = ctx.components['root']
        norm_forward = norm_mod.forward

        def normalization_forward(builder, original, flags):
            _patch_w47_body_STATE['flags'] = list(flags)
            return norm_forward(builder, original, flags)
        new_norm = _patch_w47_body_types.SimpleNamespace(**{k: getattr(norm_mod, k) for k in dir(norm_mod) if not k.startswith('__')})
        new_norm.forward = normalization_forward
        ctx.components['normalization'] = new_norm
        original_clear = root_mod.carry_clear
        original_forward = root_mod.forward

        def forward(builder, norm):
            norm = list(norm)
            h0 = norm[0]
            flags = _patch_w47_body_STATE['flags']
            if flags is None:
                km = _patch_w47_body_CTX.km
                flags = [km.q(22 + i) for i in range(4)]
                _patch_w47_body_STATE['flags'] = flags
            assert len(flags) == 4

            def carry_clear(b, Q, p, c):
                if not _patch_w47_body_STATE['packed']:
                    _patch_w47_body_STATE['packed'] = True
                    _patch_w47_body__pack(b, h0, Q, c, flags)
                return original_clear(b, Q, p, c)
            root_mod.carry_clear = carry_clear
            try:
                out = original_forward(builder, norm)
            finally:
                root_mod.carry_clear = original_clear
            assert _patch_w47_body_STATE['packed']
            residual = list(out['residual'])
            assert residual[0] == h0
            residual[0] = None
            return dict(root=out['root'], residual=residual)
        new_root = _patch_w47_body_types.SimpleNamespace(**{k: getattr(root_mod, k) for k in dir(root_mod) if not k.startswith('__')})
        new_root.forward = forward
        ctx.components['root'] = new_root
    _patch_w47_body_DONOR = _patch_w47_body_Path('' + str(_patch_w47_body_INTEGRATED_ROOT) + '/work/pro1_013/narrow/arithmetic_round3/native/candidate11r2/candidate11r2.build.json')
    _patch_w47_body__TAIL = {}

    def _patch_w47_body__load_src(name, path):
        if name not in _patch_w47_body_sys.modules:
            spec = _spec(name, path)
            module = _new_module(spec)
            _patch_w47_body_sys.modules[name] = module
            spec.loader.exec_module(module)
        return _patch_w47_body_sys.modules[name]

    def _patch_w47_body__tail_modules():
        if not _patch_w47_body__TAIL:
            json = _import_component('json', 'patches/patch_w47_body.py', True)
            W = _patch_w47_body_Path('' + str(_patch_w47_body_INTEGRATED_ROOT) + '/agents/width')
            _patch_w47_body__TAIL['T1'] = _json_loads(_read_text(W / 'plans/T1_late_metadata.json'))
            _patch_w47_body__TAIL['T2'] = _json_loads(_read_text(W / 'plans/T2_decoder_capture.json'))
            assert _patch_w47_body__TAIL['T1']['ccx'] == 3 and _patch_w47_body__TAIL['T2']['ccx'] == 20 and (_patch_w47_body__TAIL['T1']['external_bits'] == ['b75'])
            cuts = {c['name']: c for c in _json_loads(_read_text(_patch_w47_body_DONOR))['cuts']}
            _patch_w47_body__TAIL['T2_exit'] = cuts['raw_root_restored_with_paid_phase_product']['owners']
            _patch_w47_body__TAIL['replay'] = _patch_w47_body__load_src('width_block_replay', W / 'src/block_replay.py').replay
            _patch_w47_body__TAIL['paidR'] = _patch_w47_body__load_src('width_pro2_paid_R_cleanup_q48', W / 'src/paid_R_cleanup_q48.py')
        return _patch_w47_body__TAIL

    def _patch_w47_body__role_map(plan, ours):
        m = {}
        for w, (role, i) in plan['entry_owner'].items():
            q = ours[role][i]
            assert q is not None, (w, role, i)
            m[w] = q
        return m

    def _patch_w47_body__mark(builder, trace, label, owners=None):
        L = _patch_w47_body_CTX.components['lifecycle']
        live = builder.num_allocated_qubits
        assert live <= builder.max_qubits, (label, live)
        if trace is not None:
            trace.append(dict(label=label, live_owners=live))
        if L.CUT_HOOK is not None:
            L.CUT_HOOK(label, builder, {} if owners is None else {key: list(value) for key, value in owners.items()})

    def _patch_w47_body_emit_body(builder, v12, h10, flags4, table_module, divider_module, decode_root_callback, *, trace=None):
        """candidate10 lifecycle10.emit_body with packed h0 (absent until unpack_h0) and the snapshot2 tail."""
        L = _patch_w47_body_CTX.components['lifecycle']
        baseline = L.baseline
        assert builder.max_qubits in (46, 47, 48)
        v = list(v12)
        h = list(h10)
        flags = list(flags4)
        assert (len(v), len(h), len(flags)) == (12, 10, 4)
        if _patch_w47_body_PACK:
            assert h[0] is None and len(set(v + h[1:] + flags)) == 25
        else:
            assert h[0] is not None and len(set(v + h + flags)) == 26
        _patch_w47_body__mark(builder, trace, 'body_entry', dict(v=v, h=h, flags=flags))
        table_debts = table_module.TableDebts()
        truths = table_module.model_truths()
        D, Hlow = table_module.load_joint16(builder, v[5:], variant='first', debts=table_debts)
        D = list(D)
        H = list(Hlow)
        _patch_w47_body__mark(builder, trace, 'first_table', dict(v=v, h=h, flags=flags, D=D, H=H))
        H.append(baseline.prepare_H3_initial(builder, v, D, H))
        if _patch_w47_body_A6_AROUND_PRODUCT and _patch_w47_body_A6_EARLY:
            a6_outcome = builder.alloc_bits(1)[0]
            builder.hmr(v[11], a6_outcome)
            builder.free(v[11])
            v[11] = None
        baseline.root_R_frame(builder, v)
        H.append(baseline.prepare_H4(builder, D, H[3]))
        first = baseline.coefficient_forward(builder, v, D, H)
        _patch_w47_body__mark(builder, trace, 'first_coefficient', dict(v=v, h=h, flags=flags, D=D, H=H, snapshot=[first.saved_bit]))
        Hlow = baseline.erase_high_H(builder, v, D, H)
        for i, q in enumerate(Hlow):
            table_debts.erase(builder, q, truths['H'][i], free=True)
        first_snapshot = baseline.ar.release_saved_bit(builder, first.saved_bit)
        first.saved_bit = None
        baseline.root_R_frame(builder, v, inverse=True)
        _patch_w47_body__mark(builder, trace, 'first_metadata_retired')
        if _patch_w47_body_PACK and (not _patch_w47_body_UNPACK_AFTER_SEED):
            h = _patch_w47_body_unpack_h0(builder, v, h, flags)
            _patch_w47_body__mark(builder, trace, 'width_h0_unpacked', dict(v=v, h=h, flags=flags, D=D))
        seed, seed_token = baseline.seed_forward(builder, v, D)
        if _patch_w47_body_PACK and _patch_w47_body_UNPACK_AFTER_SEED:
            h = _patch_w47_body_unpack_h0_after_seed(builder, v, h, flags, seed)
        _patch_w47_body__mark(builder, trace, 'seed_ready', dict(v=v, h=h, flags=flags, D=D, seed=seed))
        if _patch_w47_body_A6_AROUND_PRODUCT and (not _patch_w47_body_A6_EARLY):
            a6_outcome = builder.alloc_bits(1)[0]
            builder.hmr(v[11], a6_outcome)
            builder.free(v[11])
            v[11] = None
        word, product_token = baseline.product_forward(builder, D, seed, h)
        if _patch_w47_body_A6_AROUND_PRODUCT:
            q = builder.alloc_qubits(1)[0]
            for w in (D[10], D[11], D[12]):
                builder.cx(w, q)
            builder.cx(v[10], D[10])
            builder.cx(v[10], D[11])
            builder.ccx(D[10], D[11], q)
            builder.cx(v[10], D[11])
            builder.cx(v[10], D[10])
            builder.push_condition(a6_outcome)
            builder.z(q)
            builder.pop_condition()
            builder.free(a6_outcome)
            v[11] = q
        builder.x(word[15])
        builder.cx(word[14], word[15])
        builder.free(word[15])
        P = word[:15]
        _patch_w47_body__mark(builder, trace, 'signed_product15', dict(v=v, P=P, flags=flags, D=D))
        first_D = []
        for q in D:
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            builder.free(q)
            first_D.append(m)
        _patch_w47_body__mark(builder, trace, 'coefficient_retired_for_divider', dict(v=v, P=P, flags=flags))
        P = list(divider_module.compute_phase_cleanup(builder, v, P, flags))
        assert len(P) == 15 and len(set(v + P + flags)) == 31
        _patch_w47_body__mark(builder, trace, 'divider_return', dict(v=v, P=P, flags=flags))
        baseline.root_R_frame(builder, v)
        D, Hlow = table_module.load_joint16(builder, v[5:], variant='second', debts=table_debts)
        D = list(D)
        H = list(Hlow)
        retired = {a: None for a in (0, 1, 2, 4)}
        for a in retired:
            v[5 + a] = None
        assert all((v[5 + a] is None for a in (0, 1, 2, 4)))
        assert v[8] is not None and v[10] is not None and (v[11] is not None)
        _patch_w47_body__mark(builder, trace, 'second_table', dict(v=v, P=P, flags=flags, D=D, H=H))
        baseline.ar.repay_saved_bit(builder, D[6], first_snapshot)
        H.append(baseline.prepare_H3_initial(builder, v, D, H))
        _patch_w47_body__mark(builder, trace, 'second_H3_ready', dict(v=v, P=P, flags=flags, D=D, H=H))
        q = v[11]
        m = builder.alloc_bits(1)[0]
        builder.hmr(q, m)
        builder.free(q)
        v[11] = None
        retired[6] = m
        assert set(retired) == {0, 1, 2, 4, 6} and all((retired[a] is None for a in (0, 1, 2, 4)))
        _patch_w47_body__mark(builder, trace, 'second_a6_retired', dict(v=v, P=P, flags=flags, D=D, H=H))
        H.append(baseline.prepare_H4(builder, D, H[3]))
        second = baseline.coefficient_forward(builder, v, D, H)
        _patch_w47_body__mark(builder, trace, 'second_coefficient', dict(v=v, P=P, flags=flags, D=D, H=H, snapshot=[second.saved_bit]))
        for q, m in zip(D, first_D):
            builder.push_condition(m)
            builder.z(q)
            builder.pop_condition()
            builder.free(m)
        baseline.merge_coefficient_transcripts(builder, first, second)
        Hlow = baseline.erase_high_H(builder, v, D, H)
        _patch_w47_body__mark(builder, trace, 'second_metadata_retired')
        high = builder.alloc_qubits(1)[0]
        builder.cx(P[14], high)
        builder.x(high)
        word = P + [high]
        _patch_w47_body__mark(builder, trace, 'inverse_product_data', dict(v=v, word=word, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
        dirty = [q for q in v if q is not None] + flags + Hlow + [second.saved_bit]
        seed, h = L.product_inverse(builder, v, D, word, product_token, dirty)
        baseline.seed_cleanup(builder, v, D, seed, seed_token)
        if _patch_w47_body_TAIL == 'donor':
            _patch_w47_body__mark(builder, trace, 'seed_cleared', dict(v=v, h=h, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
            tail = _patch_w47_body__tail_modules()
            wm = _patch_w47_body__role_map(tail['T1'], dict(v=v, h=h, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
            out = tail['replay'](builder, tail['T1'], wm, ext_bits={'b75': retired[6]})
            builder.free(retired[6])
            retired[6] = None
            v[11] = out['q26']
            H = list(Hlow) + [out['q9'], out['q43']]
            _patch_w47_body__mark(builder, trace, 'coefficient_sources_restored')
            baseline.coefficient_inverse(builder, v, D, H, second, [q for q in v if q is not None] + flags + h)
            _patch_w47_body__mark(builder, trace, 'A_restored', dict(v=v, h=h, flags=flags, A=D, H=H))
            wm = _patch_w47_body__role_map(tail['T2'], dict(v=v, h=h, flags=flags, A=D, H=H))
            out = tail['replay'](builder, tail['T2'], wm)
            ex = tail['T2_exit']
            v = [out[w] for w in ex['v']]
            h = [out[w] for w in ex['h']]
            flags = [out[w] for w in ex['flags']]
            D = [out[w] for w in ex['A']]
            H = [out[w] for w in ex['H']]
            product = out[ex['phase_snapshot'][0]]
            assert all((q is not None for q in v)) and len(set(v + h + flags)) == 26
            _patch_w47_body__mark(builder, trace, 'raw_root_restored_with_paid_R', dict(v=v, h=h, flags=flags, A=D, H=H, phase_snapshot=[product]))
            tail['paidR'].cleanup_joint18(builder, v[5:], D, H, product, table_debts, table_api=table_module)
        else:
            _patch_w47_body__mark(builder, trace, 'seed_cleared', dict(v=v, h=h, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
            H = list(Hlow)
            H.append(baseline.prepare_H3_current(builder, v, D, H))
            H.append(baseline.prepare_H4(builder, D, H[3]))
            _patch_w47_body__mark(builder, trace, 'coefficient_sources_restored')
            baseline.coefficient_inverse(builder, v, D, H, second, [q for q in v if q is not None] + flags + h)
            _patch_w47_body__mark(builder, trace, 'A_restored', dict(v=v, h=h, flags=flags, A=D, H=H))
            if _patch_w47_body_SNAPSHOT2_TAIL:
                snap = _patch_w47_body__snapshot_module()
                v, snapshots = snap.decode_root_with_snapshots(builder, v, D, H, retired)
                v = list(v)
                assert all((q is not None for q in v)) and len(set(v + h + flags)) == 26
                product = snap.capture_R_before_inverse(builder, v[8])
                baseline.root_R_frame(builder, v, inverse=True)
                snap.finish_R_capture(builder, v[8], v[7], product)
                _patch_w47_body__mark(builder, trace, 'raw_root_restored_with_paid_R', dict(v=v, h=h, flags=flags, A=D, H=H, snapshots=snapshots))
                snap.cleanup_joint20(builder, v[5:], D, H, snapshots, product, table_debts, table_api=table_module)
            else:
                v = list(decode_root_callback(builder, v, D, H, retired))
                assert all((q is not None for q in v)) and len(set(v + h + flags)) == 26
                baseline.root_R_frame(builder, v, inverse=True)
                _patch_w47_body__mark(builder, trace, 'raw_root_restored', dict(v=v, h=h, flags=flags, A=D, H=H))
                Hlow = baseline.erase_high_H(builder, v, D, H, initial=True)
                table_module.cleanup_joint16(builder, v[5:], D, Hlow, table_debts)
        assert not table_debts.pending
        assert first.saved_bit is None and second.saved_bit is None
        for token in (first, second):
            assert all((debt.consumed and (not debt.measurements) for debt in token.row_debts))
            assert token.overflow_debt.consumed and (not token.overflow_debt.measurements)
        assert all((debt.consumed and (not debt.measurements) for debt in product_token.rows))
        _patch_w47_body__mark(builder, trace, 'body_return', dict(v=v, h=h, flags=flags))
        return (v, h)

def _initialize_q46_loaders():
    global _q46_loaders_HERE, _q46_loaders_INTEGRATED_ROOT, _q46_loaders_LAST_REPORT, _q46_loaders_OWN_SECOND, _q46_loaders_Path, _q46_loaders_SPECS, _q46_loaders_SimpleNamespace, _q46_loaders__IntegratedPath, _q46_loaders___file__, _q46_loaders___name__, _q46_loaders__own_spec, _q46_loaders_adapter, _q46_loaders_certificate, _q46_loaders_hashlib, _q46_loaders_json, _q46_loaders_load, _q46_loaders_lru_cache, _q46_loaders_os
    _q46_loaders_Path = _import_component('pathlib', 'patches/q46_loaders.py', False).Path
    _q46_loaders_lru_cache = _import_component('functools', 'patches/q46_loaders.py', False).lru_cache
    _q46_loaders_SimpleNamespace = _import_component('types', 'patches/q46_loaders.py', False).SimpleNamespace
    _q46_loaders_hashlib = _import_component('hashlib', 'patches/q46_loaders.py', True)
    _q46_loaders_os = _import_component('os', 'patches/q46_loaders.py', True)
    _q46_loaders_OWN_SECOND = _q46_loaders_Path(_q46_loaders_os.environ.get('TK46_SECOND_JSON') or _q46_loaders_os.environ.get('LEAD_SECOND_JSON'))

    def _q46_loaders__own_spec():
        data = _json_loads(_read_text(_q46_loaders_OWN_SECOND))
        hmr = sum((len(st['discarded_truths']) for st in data['steps'] if st['kind'] == 'Clifford_frame_then_HMR'))
        return dict(path=_q46_loaders_OWN_SECOND, sha=_q46_loaders_hashlib.sha256(_read_bytes(_q46_loaders_OWN_SECOND)).hexdigest(), mode='second_framed', Toffolis=data['Toffolis'], HMR_debts=hmr, work_cap=data['work_cap'], entry=31, returned=43, peak=27 + data['work_cap'], fixed=(3, 5, 6), reused=(0, 1, 2, 4), outside=27)
    _q46_loaders_SPECS = {'second': _q46_loaders__own_spec()}

    @_q46_loaders_lru_cache(maxsize=2)
    def _q46_loaders_certificate(which):
        spec = _q46_loaders_SPECS[which]
        path = spec['path']
        pass
        data = _json_loads(_read_text(path))
        assert data['status'] == 'COMPLETE_MATHEMATICAL_LOADER_NOT_NATIVE'
        assert data['mode'] == spec['mode'] and data['Toffolis'] == spec['Toffolis']
        assert data['work_cap'] == data['work_peak'] == spec['work_cap']
        assert data['complete_other_owner_count'] == spec['outside'] and data['complete_peak'] == spec['peak']
        assert data['fixed_address_slots'] == list(spec['fixed']) and data['reusable_input_slots'] == list(spec['reused'])
        pass
        pass
        return data

    def _q46_loaders_load(builder, address7, which, debts, *, table_api):
        global _q46_loaders_LAST_REPORT
        api = table_api
        common = api.common
        km = common.km
        cb = common.cb
        spec = _q46_loaders_SPECS[which]
        data = _q46_loaders_certificate(which)
        address = list(address7)
        assert builder.max_qubits >= spec['peak'] and builder.num_allocated_qubits == spec['entry']
        assert len(address) == len(set(address)) == 7 and all((isinstance(q, km.q) for q in address))
        assert isinstance(debts, api.TableDebts)
        before = debts.total_recorded
        fixed = [address[i] for i in spec['fixed']]
        work = [address[i] for i in spec['reused']]
        cap = spec['work_cap']
        offset = 1 + len(fixed)
        available = list(builder.alloc_qubits(cap - len(work)))
        all_mutable = list(work + available)
        assert builder.num_allocated_qubits == spec['peak'] and spec['entry'] - len(work) == spec['outside']
        count = 0
        trace = [spec['peak']]
        for item in data['steps']:
            kind = item['kind']
            if kind in ('bank', 'CCX_new_coordinate'):
                target = available.pop(0)
                plan = common.plan_from_json(item['plan'])
                cb.emit_xor(builder, fixed + work, target, plan)
                work.append(target)
                count += plan.and_count
            elif kind == 'Clifford_zero_dependent_coordinate':
                index = item['index']
                target = work[index]
                api._BASE._affine_xor(builder, fixed, work[:index], target, item['expression'])
                work.pop(index)
                available.append(target)
            elif kind == 'Clifford_frame_then_HMR':
                assert item['affine_fixed_offset'] == offset
                api.emit_affine_frame(builder, fixed, work, item['full_affine_rows'])
                kept = item['retained_count']
                discard = work[kept:]
                assert len(discard) == len(item['discarded_truths'])
                for wire, truth in zip(discard, item['discarded_truths']):
                    debts.erase(builder, wire, int(truth, 16))
                    available.append(wire)
                work = work[:kept]
            elif kind == 'virtual_affine_product':
                pass
            elif kind == 'XOR_product_existing_coordinate':
                assert item['target_index'] == 0
                plan = common.plan_from_json(item['plan'])
                cb.emit_xor(builder, fixed + work[1:], work[0], plan)
                count += plan.and_count
            elif kind == 'final_output_Clifford_frame':
                api.emit_affine_frame(builder, fixed, work, [int(row) << offset for row in item['matrix_rows']])
            else:
                raise AssertionError(('Unknown exact loader step', kind))
            assert len(work) + len(available) == cap and len(set(work + available)) == cap
            assert not set(fixed) & set(work + available)
            trace.append(builder.num_allocated_qubits)
        assert len(work) == 16 and count == spec['Toffolis']
        assert debts.total_recorded - before == spec['HMR_debts']
        if available:
            builder.free(common.array(available))
        trace.append(builder.num_allocated_qubits)
        assert builder.num_allocated_qubits == spec['returned'] and max(trace) == spec['peak']
        _q46_loaders_LAST_REPORT = dict(loader=which, Toffolis=count, HMR_debts=debts.total_recorded - before, entry=spec['entry'], outside_mutable_owners=spec['outside'], work_cap=cap, existing_input_work=len(spec['reused']), fresh_zero_owners=cap - len(spec['reused']), fixed_address_slots=list(spec['fixed']), retired_address_slots=list(spec['reused']), returned=spec['returned'], peak=max(trace), owner_trace=trace, fixed_owners=list(map(str, fixed)), mutable_owners=list(map(str, all_mutable)), output_owners=list(map(str, work)), paper_sha256=spec['sha'], all_debts_in_original_raw128_order=True)
        return (list(work[:13]), list(work[13:]))

    def _q46_loaders_adapter(original_tables07):

        def load_joint16(builder, address7, *, variant, debts):
            assert variant in _q46_loaders_SPECS
            return _q46_loaders_load(builder, address7, variant, debts, table_api=original_tables07)
        result = _q46_loaders_SimpleNamespace(**{k: v for k, v in vars(original_tables07).items() if not k.startswith('__')})
        result.load_joint16 = load_joint16
        result._source_api = original_tables07
        result.RESOURCES = {k: dict(v) for k, v in original_tables07.RESOURCES.items()}
        for which, s in _q46_loaders_SPECS.items():
            result.RESOURCES[which].update(Toffolis=s['Toffolis'], HMR_debts=s['HMR_debts'], other_fixed_owners=s['outside'], work_cap=s['work_cap'], existing_input_work=len(s['reused']), new_zero_owners=s['work_cap'] - len(s['reused']), complete_peak=s['peak'], return_owners=s['returned'])
        assert result.TableDebts is original_tables07.TableDebts
        return result

def _initialize_audit_affine():
    global _audit_affine_INTEGRATED_ROOT, _audit_affine_Path, _audit_affine__IntegratedPath, _audit_affine___file__, _audit_affine___name__, _audit_affine_argparse, _audit_affine_json, _audit_affine_kmsim, _audit_affine_main, _audit_affine_np, _audit_affine_stage_of, _audit_affine_sys, _audit_affine_time
    _audit_affine_argparse = _import_component('argparse', 'tools/audit_affine.py', True)
    _audit_affine_json = _import_component('json', 'tools/audit_affine.py', True)
    _audit_affine_sys = _import_component('sys', 'tools/audit_affine.py', True)
    _audit_affine_time = _import_component('time', 'tools/audit_affine.py', True)
    _audit_affine_Path = _import_component('pathlib', 'tools/audit_affine.py', False).Path
    _audit_affine_np = _import_component('numpy', 'tools/audit_affine.py', False)
    _audit_affine_sys.path.insert(0, str(_audit_affine_Path(_audit_affine___file__).resolve().parent))
    _audit_affine_kmsim = _import_component('kmsim', 'tools/audit_affine.py', True)

    def _audit_affine_stage_of(cuts, index):
        for cut in cuts:
            if index < cut['instruction_cut']:
                return cut['name']
        return 'final_layout'

    def _audit_affine_main():
        ap = _audit_affine_argparse.ArgumentParser()
        ap.add_argument('kmx', type=_audit_affine_Path)
        ap.add_argument('--build', type=_audit_affine_Path)
        ap.add_argument('--out', type=_audit_affine_Path, required=True)
        ap.add_argument('--seed', type=int, default=0)
        args = ap.parse_args()
        began = _audit_affine_time.monotonic()
        ops, registers = _audit_affine_kmsim.parse(_read_text(args.kmx))
        xreg = registers['x']
        qwires = _audit_affine_kmsim.quantum_wires(ops)
        cuts = _json_loads(_read_text(args.build))['cuts'] if args.build else []
        sim = _audit_affine_kmsim.Sim(ops, xreg, seed=args.seed)
        sampler = _audit_affine_kmsim.Sampler(sim)
        findings, gates = ([], [])
        nonzero = {w: bool(sim.get(w).any()) for w in qwires}
        live_profile = _audit_affine_np.zeros(len(ops), dtype=_audit_affine_np.int16)
        stats = dict(tested=0)

        def before(index, s):
            kind, a, condition, angle, line = ops[index]
            if kind not in _audit_affine_kmsim.TOFFOLI_LIKE:
                return
            mask = s.active_mask(condition)
            active = 1.0 if mask is None else float(_audit_affine_np.bitwise_count(mask).sum()) / s.n
            if kind == 'CCX':
                products = [('ab', s.get(a[0]) & s.get(a[1]))]
            elif kind == 'CSWAP':
                products = [('c(x^y)', s.get(a[0]) & (s.get(a[1]) ^ s.get(a[2])))]
            else:
                products = [('ab', s.get(a[0]) & s.get(a[1])), ('ac', s.get(a[0]) & s.get(a[2])), ('bc', s.get(a[1]) & s.get(a[2]))]
            record = dict(op=index, line=line, kind=kind, args=list(a), condition=condition, depth=len(s.stack) - 1, active=active, stage=_audit_affine_stage_of(cuts, index))
            gates.append(record)
            if active == 0.0:
                record['never_active'] = True
                return
            for label, product in products:
                stats['tested'] += 1
                relation = _audit_affine_kmsim.affine_relation(s, sampler, product, qwires, mask)
                if relation is not None:
                    wires, constant = relation
                    found = dict(record, product=label, relation_wires=wires, relation_constant=int(constant), product_identically_zero=not wires and (not constant))
                    findings.append(found)
                    print(_audit_affine_json.dumps(found), flush=True)
                    break

        def after(index, s):
            kind, a, condition, angle, line = ops[index]
            for w in a:
                if w in nonzero:
                    nonzero[w] = bool(s.get(w).any())
            live_profile[index] = sum(nonzero.values())
        sim.run(before=before, after=after)
        final = {w: bool(sim.get(w).any()) for w in qwires}
        restored = _audit_affine_np.array_equal(sim.value(xreg), sim.xs)
        scratch_zero = not any((final[w] for w in qwires if w not in xreg))
        peak = int(live_profile.max())
        peak_ops = _audit_affine_np.flatnonzero(live_profile == peak)
        runs, start = ([], None)
        for i in peak_ops.tolist():
            if start is None:
                start = prev = i
            elif i == prev + 1:
                prev = i
            else:
                runs.append((start, prev))
                start = prev = i
        if start is not None:
            runs.append((start, prev))
        result = dict(status='AUDIT_CANDIDATES_ONLY_NOT_PROVED', kmx=str(args.kmx), inputs=sim.n, seed=args.seed, operations=len(ops), toffoli_like_static=sim.toffoli_static, toffoli_like_mean=sim.toffoli_executed / sim.n, input_restored=bool(restored), scratch_zero=bool(scratch_zero), products_tested=stats['tested'], findings=findings, expected_saving=sum((f['active'] for f in findings)), live_peak=peak, live_peak_runs=[dict(first=a, last=b, stage=_audit_affine_stage_of(cuts, a)) for a, b in runs], sample_size=len(sampler.positions), seconds=_audit_affine_time.monotonic() - began)
        args.out.write_text(_audit_affine_json.dumps(result, indent=1) + '\n')
        _audit_affine_np.save(args.out.with_suffix('.live.npy'), live_profile)
        args.out.with_suffix('.gates.json').write_text(_audit_affine_json.dumps(gates) + '\n')
        print(_audit_affine_json.dumps({k: v for k, v in result.items() if k not in ('findings', 'live_peak_runs')}, indent=1))
        print('peak runs:', len(runs), [(r['first'], r['last'], r['stage']) for r in result['live_peak_runs']][:40])
    if _audit_affine___name__ == '__main__':
        _audit_affine_main()

def _initialize_audit_pairs():
    global _audit_pairs_INTEGRATED_ROOT, _audit_pairs_Path, _audit_pairs__IntegratedPath, _audit_pairs___file__, _audit_pairs___name__, _audit_pairs_argparse, _audit_pairs_json, _audit_pairs_kmsim, _audit_pairs_main, _audit_pairs_np, _audit_pairs_products_of, _audit_pairs_reduce, _audit_pairs_sys, _audit_pairs_time
    _audit_pairs_argparse = _import_component('argparse', 'tools/audit_pairs.py', True)
    _audit_pairs_json = _import_component('json', 'tools/audit_pairs.py', True)
    _audit_pairs_sys = _import_component('sys', 'tools/audit_pairs.py', True)
    _audit_pairs_time = _import_component('time', 'tools/audit_pairs.py', True)
    _audit_pairs_Path = _import_component('pathlib', 'tools/audit_pairs.py', False).Path
    _audit_pairs_np = _import_component('numpy', 'tools/audit_pairs.py', False)
    _audit_pairs_sys.path.insert(0, str(_audit_pairs_Path(_audit_pairs___file__).resolve().parent))
    _audit_pairs_kmsim = _import_component('kmsim', 'tools/audit_pairs.py', True)

    def _audit_pairs_reduce(basis, v):
        while v:
            hit = basis.get(v.bit_length() - 1)
            if hit is None:
                return v
            v ^= hit
        return 0

    def _audit_pairs_products_of(s, kind, a):
        if kind == 'CCX':
            return s.get(a[0]) & s.get(a[1])
        if kind == 'CSWAP':
            return s.get(a[0]) & (s.get(a[1]) ^ s.get(a[2]))
        return None

    def _audit_pairs_main():
        ap = _audit_pairs_argparse.ArgumentParser()
        ap.add_argument('kmx', type=_audit_pairs_Path)
        ap.add_argument('--out', type=_audit_pairs_Path, required=True)
        ap.add_argument('--live', type=_audit_pairs_Path, help='.live.npy from audit_affine')
        ap.add_argument('--build', type=_audit_pairs_Path)
        args = ap.parse_args()
        began = _audit_pairs_time.monotonic()
        ops, registers = _audit_pairs_kmsim.parse(_read_text(args.kmx))
        xreg = registers['x']
        qw = _audit_pairs_kmsim.quantum_wires(ops)
        live = _audit_pairs_np.load(args.live) if args.live else None
        cuts = _json_loads(_read_text(args.build))['cuts'] if args.build else []

        def stage_of(i):
            for c in cuts:
                if i < c['instruction_cut']:
                    return c['name']
            return 'final_layout'
        sim = _audit_pairs_kmsim.Sim(ops, xreg)
        sampler = _audit_pairs_kmsim.Sampler(sim, count=4096)
        earlier = []
        hits = {}

        def before(index, s):
            kind, a, cond, angle, line = ops[index]
            if kind not in ('CCX', 'CSWAP') or len(s.stack) > 1 or cond is not None:
                return
            p = sampler.take(_audit_pairs_products_of(s, kind, a))
            basis = {}
            for w in qw:
                v = _audit_pairs_reduce(basis, sampler.take(s.get(w)))
                if v:
                    basis[v.bit_length() - 1] = v
            v = _audit_pairs_reduce(basis, sampler.take(s.ones))
            if v:
                basis[v.bit_length() - 1] = v
            rj = _audit_pairs_reduce(basis, p)
            if rj:
                for i, pi in earlier:
                    if _audit_pairs_reduce(basis, pi ^ p) == 0:
                        hits.setdefault(index, []).append(i)
            earlier.append((index, p))
        sim.run(before=before)
        print('sampled pair hits:', sum((len(v) for v in hits.values())), 'gates with a hit:', len(hits), 'seconds %.1f' % (_audit_pairs_time.monotonic() - began), flush=True)
        wanted = sorted({i for j, ii in hits.items() for i in ii[-3:]})
        stored = {}
        sim = _audit_pairs_kmsim.Sim(ops, xreg)
        sampler2 = _audit_pairs_kmsim.Sampler(sim, count=4096)
        rows = []

        def before2(index, s):
            kind, a, cond, angle, line = ops[index]
            if kind not in ('CCX', 'CSWAP'):
                return
            if index in hits:
                p = _audit_pairs_products_of(s, kind, a)
                for i in reversed(hits[index][-3:]):
                    rel = _audit_pairs_kmsim.affine_relation(s, sampler2, p ^ stored[i], qw)
                    if rel is not None:
                        span_max = int(live[i:index].max()) if live is not None else None
                        rows.append(dict(later_op=index, later_line=line, later=[kind] + list(a), earlier_op=i, earlier_line=ops[i][4], earlier=[ops[i][0]] + list(ops[i][1]), distance=index - i, max_live_between=span_max, stage=stage_of(index), relation_wires=rel[0], relation_constant=int(rel[1])))
                        break
            if index in wanted:
                stored[index] = _audit_pairs_products_of(s, kind, a).copy()
        sim.run(before=before2)
        rows.sort(key=lambda r: (r['max_live_between'] if r['max_live_between'] is not None else 0, r['distance']))
        args.out.write_text(_audit_pairs_json.dumps(dict(rows=rows, seconds=_audit_pairs_time.monotonic() - began), indent=1) + '\n')
        print('exact recomputed pairs:', len(rows))
        by = {}
        for r in rows:
            key = (r['stage'], r['max_live_between'])
            by[key] = by.get(key, 0) + 1
        for k, n in sorted(by.items(), key=lambda kv: (kv[0][1] or 0, kv[0][0])):
            print(n, k)
        for r in rows[:40]:
            print(r['later_op'], r['later'], '<-', r['earlier_op'], r['earlier'], 'dist', r['distance'], 'maxlive', r['max_live_between'], r['stage'], r['relation_wires'], r['relation_constant'])
    if _audit_pairs___name__ == '__main__':
        _audit_pairs_main()

def _initialize_build_variant():
    global _build_variant_CAND10, _build_variant_Context, _build_variant_FG, _build_variant_HERE, _build_variant_INTEGRATED_ROOT, _build_variant_NARROW, _build_variant_PatchSet, _build_variant_Path, _build_variant__IntegratedPath, _build_variant___file__, _build_variant___name__, _build_variant_argparse, _build_variant_build, _build_variant_cost_model, _build_variant_hashlib, _build_variant_importlib, _build_variant_json, _build_variant_load_patch, _build_variant_main, _build_variant_sys, _build_variant_time
    _build_variant_Path = _import_component('pathlib', 'tools/build_variant.py', False).Path
    _build_variant_argparse = _import_component('argparse', 'tools/build_variant.py', True)
    _build_variant_hashlib = _import_component('hashlib', 'tools/build_variant.py', True)
    _build_variant_json = _import_component('json', 'tools/build_variant.py', True)
    _build_variant_sys = _import_component('sys', 'tools/build_variant.py', True)
    _build_variant_time = _import_component('time', 'tools/build_variant.py', True)
    _build_variant_HERE = _build_variant_Path(_build_variant___file__).resolve().parent
    _build_variant_FG = _build_variant_HERE.parent
    _build_variant_NARROW = _build_variant_FG / 'work/c10/narrow'
    _build_variant_CAND10 = _build_variant_NARROW / 'arithmetic_round2/native/candidate10'
    _build_variant_sys.path.insert(0, str(_build_variant_CAND10))
    _build_variant_sys.path.insert(0, str(_build_variant_HERE))

    def _build_variant_load_patch(path):
        if path is None:
            return None
        spec = _spec('variant_patch_' + _build_variant_Path(path).stem, path)
        module = _new_module(spec)
        _build_variant_sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    class _build_variant_Context:
        pass

    class _build_variant_PatchSet:
        """Several patch modules applied in order; later ones win on Q and emit_body."""

        def __init__(self, modules):
            self.modules = [m for m in modules if m is not None]
            for m in self.modules:
                if hasattr(m, 'Q'):
                    self.Q = m.Q
                if hasattr(m, 'emit_body'):
                    self.emit_body = m.emit_body

        def apply(self, ctx):
            for m in self.modules:
                if hasattr(m, 'apply'):
                    m.apply(ctx)

    def _build_variant_build(patch=None, Q=None):
        variant = _import_component('arithmetic_variant', 'tools/build_variant.py', False)
        Program = _import_component('branch_prover', 'tools/build_variant.py', False).Program
        generated_text = _import_component('branch_prover', 'tools/build_variant.py', False).generated_text
        exact_expectation = _import_component('fourier_resource_expectation', 'tools/build_variant.py', False).exact_expectation
        gate = variant.accepted_gate()
        components = dict(variant.install())
        old = variant.old
        common = old.common
        base = old.load_baseline('generate')
        ctx = _build_variant_Context()
        ctx.variant, ctx.old, ctx.components, ctx.common, ctx.km = (variant, old, components, common, common.km)
        ctx.baseline = components['lifecycle'].baseline
        ctx.tables = old.local_module('tables07')
        ctx.decoder = old.inherited_module('decoder06')
        ctx.phase = old.local_module('phase07')
        ctx.base = base
        ctx.gate = gate
        width = Q if Q is not None else getattr(patch, 'Q', gate['Q'])
        if patch is not None and hasattr(patch, 'apply'):
            patch.apply(ctx)
        lifecycle = ctx.components['lifecycle']
        builder = common.km.CircuitBuilder()
        builder.set_max_qubits(width)
        original = list(builder.alloc_qubits(22))
        flags = list(builder.alloc_qubits(4))
        cuts, owner_trace = ([], [])

        def mark(label, current, owners):
            cuts.append(base.snapshot(current, label, owners))
        lifecycle.CUT_HOOK = mark
        ctx.components['normalization'].forward(builder, original, flags)
        mark('normalized', builder, dict(n=original, flags=flags))
        root = ctx.components['root'].forward(builder, original)
        v, h = (list(root['root']), list(root['residual']))
        mark('consumed_root', builder, dict(v=v, h=h, flags=flags))
        emit_body = getattr(patch, 'emit_body', None) or lifecycle.emit_body
        v, h = emit_body(builder, v, h, flags, ctx.tables, old.divider, ctx.decoder.decode_root, trace=owner_trace)
        assert len(set(v + h + flags)) == 26 and builder.num_allocated_qubits == 26
        mark('body_restored', builder, dict(v=v, h=h, flags=flags))
        norm = h + v
        ctx.components['root'].inverse(builder, norm)
        mark('root_restored', builder, dict(n=norm, flags=flags))
        ctx.components['normalization'].inverse(builder, norm, flags)
        builder.free(common.array(flags))
        mark('logical_input_restored', builder, dict(x=norm))
        layout = base.restore_input_layout(builder, norm, original, width)
        circuit = common.with_registers(builder.finish_circuit(), dict(x=original))
        text = generated_text(circuit)
        pass
        return (ctx, circuit, text, cuts, owner_trace, layout)

    def _build_variant_cost_model(resources, Q, margin_units64=124370688):
        math = _import_component('math', 'tools/build_variant.py', True)
        mean = resources['mean_numeric']
        rotations = mean['generic_rotations']
        eps = math.pi * margin_units64 / 2 ** 64 / rotations if rotations else None
        charge = rotations * (0.56 * math.log2(1 / eps) + 5.3) / 4 if rotations else 0.0
        per_shot = mean['toffoli_like'] + mean['T'] / 4 + charge
        return dict(Q=Q, toffoli_like=mean['toffoli_like'], T=mean['T'], generic_rotations=rotations, rotation_charge=charge, per_shot=per_shot, modelled_cost=Q * per_shot, label='modelled from exact gate expectation; margin assumed unchanged; not measured')

    def _build_variant_main():
        ap = _build_variant_argparse.ArgumentParser()
        ap.add_argument('--out', type=_build_variant_Path, required=True)
        ap.add_argument('--patch', type=_build_variant_Path, action='append', default=[])
        ap.add_argument('--postpass', type=_build_variant_Path)
        ap.add_argument('--name', default='variant')
        ap.add_argument('--Q', type=int)
        args = ap.parse_args()
        began = _build_variant_time.monotonic()
        patch = _build_variant_PatchSet([_build_variant_load_patch(path) for path in args.patch]) if args.patch else None
        ctx, circuit, text, cuts, owner_trace, layout = _build_variant_build(patch, args.Q)
        Program = _import_component('branch_prover', 'tools/build_variant.py', False).Program
        generated_text = _import_component('branch_prover', 'tools/build_variant.py', False).generated_text
        exact_expectation = _import_component('fourier_resource_expectation', 'tools/build_variant.py', False).exact_expectation
        km = ctx.km
        postpass_report = None
        if args.postpass is not None:
            postpass = _import_component('postpass', 'tools/build_variant.py', True)
            text, postpass_report = postpass.apply_rewrites(text, _json_loads(_read_text(args.postpass)))
            circuit = km.Circuit(text)
            text = generated_text(circuit)
        program, resources = (Program(text), exact_expectation(text))
        assert list(circuit.register_data) == ['x'] and len(circuit.register_data['x']) == 22
        assert program.modulus == 1 << 50, program.modulus
        args.out.mkdir(parents=True, exist_ok=True)
        kmb = args.out / (args.name + '.kmb')
        circuit.to_file(str(kmb), format='kmb')
        kmb.with_suffix('.kmx').write_text(text)
        model = _build_variant_cost_model(resources, circuit.num_qubits)
        report = dict(status='EMITTED_VARIANT_NOT_YET_PROVED_OR_QUALIFIED', name=args.name, base='candidate10 generator, unmodified pinned sources', patch=[str(path) for path in args.patch], patch_sha256=[_build_variant_hashlib.sha256(_read_bytes(path)).hexdigest() for path in args.patch], postpass=str(args.postpass) if args.postpass else None, postpass_report=postpass_report, Q=circuit.num_qubits, exact_native_expectation=resources, cost_model=model, cuts=cuts, owner_trace=owner_trace, final_Clifford_layout_swaps=layout, actual_HMR_variables=program.measurements, native_operations=len(program.operations), kmb_sha256=_build_variant_hashlib.sha256(_read_bytes(kmb)).hexdigest(), native_text_sha256=_build_variant_hashlib.sha256(text.encode()).hexdigest(), emission_seconds=_build_variant_time.monotonic() - began, official_verifier=False, no_submission=True)
        kmb.with_suffix('.build.json').write_text(_build_variant_json.dumps(report, indent=2) + '\n')
        print(_build_variant_json.dumps(dict(name=args.name, kmb=str(kmb), kmb_sha256=report['kmb_sha256'], cost_model=model, static=resources['static'], HMR=program.measurements, seconds=report['emission_seconds']), indent=1), flush=True)
    if _build_variant___name__ == '__main__':
        _build_variant_main()

def _initialize_hold_pass():
    global _hold_pass_INTEGRATED_ROOT, _hold_pass_Path, _hold_pass__IntegratedPath, _hold_pass___file__, _hold_pass___name__, _hold_pass_analyse, _hold_pass_ap, _hold_pass_apply_chains, _hold_pass_argparse, _hold_pass_args, _hold_pass_bisect, _hold_pass_chains, _hold_pass_chains_from_pairs, _hold_pass_json, _hold_pass_kmsim, _hold_pass_plan_chain, _hold_pass_report, _hold_pass_sys, _hold_pass_text
    _hold_pass_bisect = _import_component('bisect', 'tools/hold_pass.py', True)
    _hold_pass_json = _import_component('json', 'tools/hold_pass.py', True)
    _hold_pass_sys = _import_component('sys', 'tools/hold_pass.py', True)
    _hold_pass_Path = _import_component('pathlib', 'tools/hold_pass.py', False).Path
    _hold_pass_sys.path.insert(0, str(_hold_pass_Path(_hold_pass___file__).resolve().parent))
    _hold_pass_kmsim = _import_component('kmsim', 'tools/hold_pass.py', True)

    def _hold_pass_analyse(text):
        ops, registers = _hold_pass_kmsim.parse(text)
        qw = _hold_pass_kmsim.quantum_wires(ops)
        depth, block_start, stack = ([], [], [])
        for i, (kind, a, cond, angle, line) in enumerate(ops):
            if kind == 'PUSH_CONDITION':
                depth.append(len(stack))
                block_start.append(stack[0] if stack else i)
                stack.append(i)
            elif kind == 'POP_CONDITION':
                stack.pop()
                depth.append(len(stack))
                block_start.append(stack[0] if stack else i)
            else:
                depth.append(len(stack))
                block_start.append(stack[0] if stack else i)
        refs = {w: [] for w in qw}
        for i, (kind, a, cond, angle, line) in enumerate(ops):
            for w in a:
                if w in refs:
                    e = block_start[i]
                    if not refs[w] or refs[w][-1] != e:
                        refs[w].append(e)
        sim = _hold_pass_kmsim.Sim(ops, registers['x'])
        nonzero = {w: bool(sim.get(w).any()) for w in qw}
        transitions = {w: [(-1, nonzero[w])] for w in qw}

        def after(index, s):
            for w in ops[index][1]:
                if w in nonzero:
                    now = bool(s.get(w).any())
                    if now != nonzero[w]:
                        nonzero[w] = now
                        transitions[w].append((index, now))
        sim.run(after=after)

        def zero_before(w, t):
            """Wire identically zero just before op t (after op t-1)."""
            tr = transitions[w]
            k = _hold_pass_bisect.bisect_right([x[0] for x in tr], t - 1) - 1
            return not tr[k][1]

        def next_ref(w, t):
            r = refs[w]
            k = _hold_pass_bisect.bisect_left(r, t)
            return r[k] if k < len(r) else 10 ** 9
        return (ops, qw, depth, zero_before, next_ref)

    def _hold_pass_plan_chain(ops, qw, depth, zero_before, next_ref, chain):
        g0, gk = (chain[0], chain[-1])
        for g in chain:
            assert ops[g][0] == 'CCX' and depth[g] == 0 and (ops[g][2] is None), (g, ops[g])
        used = set()
        for g in chain:
            used.update(ops[g][1])

        def pick(t, exclude):
            best = None
            for w in qw:
                if w in exclude or w in used or (not zero_before(w, t)):
                    continue
                r = next_ref(w, t)
                if r <= t:
                    continue
                if best is None or r > best[0]:
                    best = (r, w)
            return best
        hops, holder_at = ([], {})
        choice = pick(g0, set())
        assert choice is not None, 'no free wire at chain start'
        until, holder = choice
        start_holder = holder
        t = g0
        schedule = [(g0, holder)]
        while until <= gk:
            assert depth[until] == 0
            nxt = pick(until, {holder})
            assert nxt is not None and nxt[0] > until, ('no free wire to hop to', until)
            hops.append((until, holder, nxt[1]))
            until, holder = nxt
            schedule.append((hops[-1][0], holder))

        def holder_for(g):
            current = schedule[0][1]
            for when, w in schedule[1:]:
                if when <= g:
                    current = w
            return current
        return dict(chain=chain, hops=hops, holders={g: holder_for(g) for g in chain})

    def _hold_pass_apply_chains(text, chains):
        """Apply chains one at a time, latest first (edits never shift earlier op indices)."""
        report = []
        for chain in sorted(chains, key=lambda c: -c[0]):
            ops, qw, depth, zero_before, next_ref = _hold_pass_analyse(text)
            plan = _hold_pass_plan_chain(ops, qw, depth, zero_before, next_ref, chain)
            lines = text.split('\n')
            used_bits = {int(tok[1:]) for line in lines for tok in line.split() if tok.startswith('b') and tok[1:].isdigit()}
            bit = f'b{(max(used_bits) + 1 if used_bits else 0)}'
            insert_before, replace = ({}, {})
            for when, old, new in plan['hops']:
                insert_before.setdefault(when, []).extend([f'CX {old} {new}', f'CX {new} {old}'])
            for n, g in enumerate(chain):
                a, b, t = ops[g][1]
                S = plan['holders'][g]
                if n == 0:
                    new = [f'CCX {a} {b} {S}', f'CX {S} {t}']
                elif n < len(chain) - 1:
                    new = [f'CX {S} {t}']
                else:
                    new = [f'CX {S} {t}', f'HMR {S} {bit}', f'CZ {a} {b} if {bit}']
                replace[g] = new
            for index in sorted(set(insert_before) | set(replace), reverse=True):
                line_no = ops[index][4] - 1
                new_lines = insert_before.get(index, []) + replace.get(index, [lines[line_no]])
                lines[line_no:line_no + 1] = new_lines
            text = '\n'.join(lines)
            report.append(dict(chain=chain, gates=[' '.join((ops[g][0],) + ops[g][1]) for g in chain], hops=len(plan['hops']), holders=sorted(set(plan['holders'].values())), expected_toffoli_saving=len(chain) - 1))
        return (text, report)

    def _hold_pass_chains_from_pairs(pairs, Q=48):
        """Link exact-equality pairs with a spare wire (max live between < Q) into chains."""
        link = {}
        for r in pairs:
            if r['relation_wires'] or r['relation_constant'] or r['later'][0] != 'CCX' or (r['earlier'][0] != 'CCX'):
                continue
            if r['max_live_between'] is None or r['max_live_between'] >= Q:
                continue
            link[r['later_op']] = r['earlier_op']
        chains, seen = ([], set())
        for later in sorted(link, reverse=True):
            if later in seen:
                continue
            chain = [later]
            while chain[-1] in link:
                chain.append(link[chain[-1]])
            seen.update(chain)
            chains.append(sorted(chain))
        return chains
    if _hold_pass___name__ == '__main__':
        _hold_pass_argparse = _import_component('argparse', 'tools/hold_pass.py', True)
        _hold_pass_ap = _hold_pass_argparse.ArgumentParser()
        _hold_pass_ap.add_argument('kmx', type=_hold_pass_Path)
        _hold_pass_ap.add_argument('pairs', type=_hold_pass_Path)
        _hold_pass_ap.add_argument('--out', type=_hold_pass_Path, required=True)
        _hold_pass_ap.add_argument('--Q', type=int, default=48)
        _hold_pass_args = _hold_pass_ap.parse_args()
        _hold_pass_chains = _hold_pass_chains_from_pairs(_json_loads(_read_text(_hold_pass_args.pairs))['rows'], _hold_pass_args.Q)
        _hold_pass_text, _hold_pass_report = _hold_pass_apply_chains(_read_text(_hold_pass_args.kmx), _hold_pass_chains)
        _hold_pass_args.out.write_text(_hold_pass_text)
        _hold_pass_args.out.with_suffix('.hold.json').write_text(_hold_pass_json.dumps(_hold_pass_report, indent=1) + '\n')
        print(_hold_pass_json.dumps(_hold_pass_report, indent=1))

def _initialize_kmsim():
    global _kmsim_INTEGRATED_ROOT, _kmsim_MAX_X, _kmsim_Sampler, _kmsim_Sim, _kmsim_TOFFOLI_LIKE, _kmsim__IntegratedPath, _kmsim___file__, _kmsim___name__, _kmsim_affine_relation, _kmsim_annotations, _kmsim_first_set, _kmsim_np, _kmsim_pack_bits, _kmsim_parse, _kmsim_quantum_wires, _kmsim_solve_span
    _kmsim_np = _import_component('numpy', 'tools/kmsim.py', False)
    _kmsim_MAX_X = 3133452
    _kmsim_TOFFOLI_LIKE = ('CCX', 'CCZ', 'CSWAP')

    def _kmsim_parse(text):
        """Return (ops, registers). op = (kind, args, condition, angle, line_number)."""
        ops, registers, register_ids = ([], {}, {})
        for number, line in enumerate(text.splitlines(), 1):
            tokens = line.split()
            if not tokens or tokens[0].startswith('#'):
                continue
            kind, arguments = (tokens[0], tokens[1:])
            if kind in ('INFO_TAG', 'DEBUG_PRINT'):
                continue
            if kind == 'APPEND_TO_REGISTER':
                register_ids.setdefault(arguments[1], []).append(arguments[0])
                continue
            if kind == 'REGISTER':
                registers[arguments[1].strip('"')] = register_ids[arguments[0]]
                continue
            condition = None
            if 'if' in arguments:
                index = arguments.index('if')
                assert index == len(arguments) - 2, line
                condition = arguments[-1]
                arguments = arguments[:index]
            angle = None
            if kind == 'Z_POW':
                angle = arguments[-1]
                arguments = arguments[:-1]
            ops.append((kind, tuple(arguments), condition, angle, number))
        return (ops, registers)

    def _kmsim_pack_bits(bits):
        """bool/uint8 vector -> little-endian uint64 words."""
        raw = _kmsim_np.packbits(_kmsim_np.asarray(bits, dtype=_kmsim_np.uint8), bitorder='little')
        pad = -len(raw) % 8
        if pad:
            raw = _kmsim_np.concatenate([raw, _kmsim_np.zeros(pad, dtype=_kmsim_np.uint8)])
        return raw.view('<u8').copy()

    class _kmsim_Sim:
        """Bit-sliced execution. state[wire] is uint64[W]; absent wires are zero."""

        def __init__(self, ops, xreg, xs=None, seed=0):
            self.ops = ops
            self.xs = _kmsim_np.arange(1, _kmsim_MAX_X + 1, dtype=_kmsim_np.uint64) if xs is None else _kmsim_np.asarray(xs, dtype=_kmsim_np.uint64)
            self.n = len(self.xs)
            self.W = (self.n + 63) // 64
            self.ones = _kmsim_pack_bits(_kmsim_np.ones(self.n, dtype=_kmsim_np.uint8))
            if len(self.ones) < self.W:
                self.ones = _kmsim_np.concatenate([self.ones, _kmsim_np.zeros(self.W - len(self.ones), dtype=_kmsim_np.uint64)])
            self.zero = _kmsim_np.zeros(self.W, dtype=_kmsim_np.uint64)
            self.rng = _kmsim_np.random.default_rng(seed)
            self.state = {}
            for i, wire in enumerate(xreg):
                self.state[wire] = _kmsim_pack_bits(self.xs >> _kmsim_np.uint64(i) & _kmsim_np.uint64(1))
            self.stack = [None]
            self.toffoli_executed = 0
            self.toffoli_static = 0

        def get(self, wire):
            value = self.state.get(wire)
            return self.zero if value is None else value

        def active_mask(self, condition):
            mask = self.stack[-1]
            if condition is not None:
                bit = self.get(condition)
                mask = bit if mask is None else mask & bit
            return mask

        def step(self, index):
            kind, a, condition, angle, _ = self.ops[index]
            if kind == 'PUSH_CONDITION':
                self.stack.append(self.active_mask(condition))
                return
            if kind == 'POP_CONDITION':
                self.stack.pop()
                return
            mask = self.active_mask(condition)
            full = mask is None
            s = self.state
            if kind in _kmsim_TOFFOLI_LIKE:
                self.toffoli_static += 1
                self.toffoli_executed += self.n if full else int(_kmsim_np.bitwise_count(mask).sum())
            if kind == 'X':
                s[a[0]] = self.get(a[0]) ^ (self.ones if full else mask)
            elif kind == 'CX':
                c = self.get(a[0])
                s[a[1]] = self.get(a[1]) ^ (c if full else c & mask)
            elif kind == 'CCX':
                p = self.get(a[0]) & self.get(a[1])
                s[a[2]] = self.get(a[2]) ^ (p if full else p & mask)
            elif kind == 'SWAP':
                x, y = (self.get(a[0]), self.get(a[1]))
                if full:
                    s[a[0]], s[a[1]] = (y, x)
                else:
                    d = (x ^ y) & mask
                    s[a[0]], s[a[1]] = (x ^ d, y ^ d)
            elif kind == 'CSWAP':
                x, y = (self.get(a[1]), self.get(a[2]))
                d = (x ^ y) & self.get(a[0])
                if not full:
                    d = d & mask
                s[a[1]], s[a[2]] = (x ^ d, y ^ d)
            elif kind in ('Z', 'CZ', 'CCZ', 'NEG', 'Z_POW'):
                pass
            elif kind == 'HMR':
                outcome = self.rng.integers(0, 1 << 64, self.W, dtype=_kmsim_np.uint64) & self.ones
                if full:
                    s[a[0]] = self.zero
                    s[a[1]] = outcome
                else:
                    s[a[0]] = self.get(a[0]) & ~mask
                    s[a[1]] = self.get(a[1]) & ~mask | outcome & mask
            elif kind == 'R':
                value = self.get(a[0])
                if (value if full else value & mask).any():
                    raise AssertionError(f'Reset of nonzero {a[0]} at op {index}')
            elif kind == 'BIT_STORE0':
                s[a[0]] = self.zero if full else self.get(a[0]) & ~mask
            elif kind == 'BIT_STORE1':
                s[a[0]] = self.ones.copy() if full else self.get(a[0]) | mask
            elif kind == 'BIT_INVERT':
                s[a[0]] = self.get(a[0]) ^ (self.ones if full else mask)
            else:
                raise AssertionError(kind)

        def run(self, before=None, after=None, start=0, stop=None):
            stop = len(self.ops) if stop is None else stop
            for index in range(start, stop):
                if before is not None:
                    before(index, self)
                self.step(index)
                if after is not None:
                    after(index, self)
            return self

        def value(self, wires):
            """Integer value per input of a little-endian wire list (None = 0)."""
            out = _kmsim_np.zeros(self.n, dtype=_kmsim_np.uint64)
            for i, wire in enumerate(wires):
                if wire is None:
                    continue
                bits = _kmsim_np.unpackbits(self.get(wire).view(_kmsim_np.uint8), bitorder='little')[:self.n]
                out |= bits.astype(_kmsim_np.uint64) << _kmsim_np.uint64(i)
            return out

    def _kmsim_quantum_wires(ops):
        names = set()
        for kind, a, condition, angle, _ in ops:
            for w in a:
                if w.startswith('q'):
                    names.add(w)
        return sorted(names, key=lambda w: int(w[1:]))

    class _kmsim_Sampler:
        """Refinable sample of input positions for GF(2) span pre-filtering."""

        def __init__(self, sim, count=4096, seed=1):
            rng = _kmsim_np.random.default_rng(seed)
            picks = set((int(v) for v in rng.integers(0, sim.n, count)))
            xs = sim.xs
            if len(xs) == _kmsim_MAX_X:
                for i in range(22):
                    for v in ((1 << i) - 1, 1 << i, (1 << i) + 1):
                        if 1 <= v <= _kmsim_MAX_X:
                            picks.add(v - 1)
                picks.update((0, _kmsim_MAX_X - 1))
            self.positions = sorted(picks)
            self._index()

        def _index(self):
            p = _kmsim_np.array(self.positions, dtype=_kmsim_np.int64)
            self.word = p >> 6
            self.bit = (p & 63).astype(_kmsim_np.uint64)

        def add(self, position):
            self.positions.append(int(position))
            self._index()

        def take(self, vector):
            bits = (vector[self.word] >> self.bit & _kmsim_np.uint64(1)).astype(_kmsim_np.uint8)
            return int.from_bytes(_kmsim_np.packbits(bits, bitorder='little').tobytes(), 'little')

    def _kmsim_solve_span(vectors, target):
        """Subset mask of `vectors` (python ints) whose XOR equals target, else None."""
        basis = {}
        for index, v in enumerate(vectors):
            combo = 1 << index
            while v:
                pivot = v.bit_length() - 1
                hit = basis.get(pivot)
                if hit is None:
                    basis[pivot] = (v, combo)
                    break
                v ^= hit[0]
                combo ^= hit[1]
        v, combo = (target, 0)
        while v:
            hit = basis.get(v.bit_length() - 1)
            if hit is None:
                return None
            v ^= hit[0]
            combo ^= hit[1]
        return combo

    def _kmsim_first_set(vector):
        words = _kmsim_np.flatnonzero(vector)
        if not len(words):
            return None
        w = int(words[0])
        value = int(vector[w])
        return w * 64 + ((value & -value).bit_length() - 1)

    def _kmsim_affine_relation(sim, sampler, target, names, mask=None, max_refine=64):
        """Exact: is `target` (uint64 vector) = XOR of a subset of names (+const) on the domain?

    Returns (list_of_wire_names, constant_bit) or None. With a mask, equality is
    only required on masked inputs. Sample solve + exact check + counterexample
    refinement, so a returned relation holds on every simulated input.
    """

        def restrict(v):
            return v if mask is None else v & mask
        ones = sim.ones if mask is None else mask
        t_full = restrict(target)
        for _ in range(max_refine):
            vectors = [sampler.take(restrict(sim.get(w))) for w in names] + [sampler.take(ones)]
            combo = _kmsim_solve_span(vectors, sampler.take(t_full))
            if combo is None:
                return None
            acc = t_full.copy()
            chosen = []
            for i, w in enumerate(names):
                if combo >> i & 1:
                    acc ^= restrict(sim.get(w))
                    chosen.append(w)
            constant = combo >> len(names) & 1
            if constant:
                acc ^= ones
            bad = _kmsim_first_set(acc)
            if bad is None:
                return (chosen, constant)
            sampler.add(bad)
        return None

def _initialize_kmx_to_kmb():
    global _kmx_to_kmb_CAND10, _kmx_to_kmb_FG, _kmx_to_kmb_HERE, _kmx_to_kmb_INTEGRATED_ROOT, _kmx_to_kmb_Path, _kmx_to_kmb__IntegratedPath, _kmx_to_kmb___file__, _kmx_to_kmb___name__, _kmx_to_kmb_argparse, _kmx_to_kmb_hashlib, _kmx_to_kmb_json, _kmx_to_kmb_main, _kmx_to_kmb_sys, _kmx_to_kmb_time
    _kmx_to_kmb_Path = _import_component('pathlib', 'tools/kmx_to_kmb.py', False).Path
    _kmx_to_kmb_argparse = _import_component('argparse', 'tools/kmx_to_kmb.py', True)
    _kmx_to_kmb_hashlib = _import_component('hashlib', 'tools/kmx_to_kmb.py', True)
    _kmx_to_kmb_json = _import_component('json', 'tools/kmx_to_kmb.py', True)
    _kmx_to_kmb_sys = _import_component('sys', 'tools/kmx_to_kmb.py', True)
    _kmx_to_kmb_time = _import_component('time', 'tools/kmx_to_kmb.py', True)
    _kmx_to_kmb_HERE = _kmx_to_kmb_Path(_kmx_to_kmb___file__).resolve().parent
    _kmx_to_kmb_FG = _kmx_to_kmb_HERE.parent
    _kmx_to_kmb_CAND10 = _kmx_to_kmb_FG / 'work/c10/narrow/arithmetic_round2/native/candidate10'
    _kmx_to_kmb_sys.path.insert(0, str(_kmx_to_kmb_CAND10))
    _kmx_to_kmb_sys.path.insert(0, str(_kmx_to_kmb_HERE))

    def _kmx_to_kmb_main():
        ap = _kmx_to_kmb_argparse.ArgumentParser()
        ap.add_argument('kmx', type=_kmx_to_kmb_Path)
        ap.add_argument('--out', type=_kmx_to_kmb_Path, required=True)
        ap.add_argument('--provenance', type=_kmx_to_kmb_Path, action='append', default=[])
        args = ap.parse_args()
        began = _kmx_to_kmb_time.monotonic()
        variant = _import_component('arithmetic_variant', 'tools/kmx_to_kmb.py', False)
        Program = _import_component('branch_prover', 'tools/kmx_to_kmb.py', False).Program
        generated_text = _import_component('branch_prover', 'tools/kmx_to_kmb.py', False).generated_text
        exact_expectation = _import_component('fourier_resource_expectation', 'tools/kmx_to_kmb.py', False).exact_expectation
        cost_model = _import_component('build_variant', 'tools/kmx_to_kmb.py', False).cost_model
        km = variant.old.common.km
        circuit = km.Circuit(_read_text(args.kmx))
        text = generated_text(circuit)
        program, resources = (Program(text), exact_expectation(text))
        assert list(circuit.register_data) == ['x'] and len(circuit.register_data['x']) == 22
        assert program.modulus == 1 << 50
        args.out.parent.mkdir(parents=True, exist_ok=True)
        circuit.to_file(str(args.out), format='kmb')
        args.out.with_suffix('.kmx').write_text(text)
        report = dict(status='COMPILED_FROM_TEXT_NOT_YET_PROVED_OR_QUALIFIED', source_kmx=str(args.kmx), source_kmx_sha256=_kmx_to_kmb_hashlib.sha256(_read_bytes(args.kmx)).hexdigest(), provenance={str(p): _json_loads(_read_text(p)) for p in args.provenance}, Q=circuit.num_qubits, exact_native_expectation=resources, cost_model=cost_model(resources, circuit.num_qubits), actual_HMR_variables=program.measurements, native_operations=len(program.operations), kmb_sha256=_kmx_to_kmb_hashlib.sha256(_read_bytes(args.out)).hexdigest(), native_text_sha256=_kmx_to_kmb_hashlib.sha256(text.encode()).hexdigest(), seconds=_kmx_to_kmb_time.monotonic() - began, official_verifier=False, no_submission=True)
        args.out.with_suffix('.build.json').write_text(_kmx_to_kmb_json.dumps(report, indent=2) + '\n')
        print(_kmx_to_kmb_json.dumps(dict(kmb=str(args.out), kmb_sha256=report['kmb_sha256'], cost_model=report['cost_model'], static=resources['static'], HMR=program.measurements), indent=1), flush=True)
    if _kmx_to_kmb___name__ == '__main__':
        _kmx_to_kmb_main()

def _initialize_merge_zpow():
    global _merge_zpow_Fraction, _merge_zpow_INTEGRATED_ROOT, _merge_zpow_Path, _merge_zpow__IntegratedPath, _merge_zpow___file__, _merge_zpow___name__, _merge_zpow_argparse, _merge_zpow_dyadic, _merge_zpow_hashlib, _merge_zpow_json, _merge_zpow_kind_of, _merge_zpow_kmsim, _merge_zpow_main, _merge_zpow_sys
    _merge_zpow_argparse = _import_component('argparse', 'tools/merge_zpow.py', True)
    _merge_zpow_hashlib = _import_component('hashlib', 'tools/merge_zpow.py', True)
    _merge_zpow_json = _import_component('json', 'tools/merge_zpow.py', True)
    _merge_zpow_sys = _import_component('sys', 'tools/merge_zpow.py', True)
    _merge_zpow_Fraction = _import_component('fractions', 'tools/merge_zpow.py', False).Fraction
    _merge_zpow_Path = _import_component('pathlib', 'tools/merge_zpow.py', False).Path
    _merge_zpow_sys.path.insert(0, str(_merge_zpow_Path(_merge_zpow___file__).resolve().parent))
    _merge_zpow_kmsim = _import_component('kmsim', 'tools/merge_zpow.py', True)

    def _merge_zpow_dyadic(fr):
        """Exact decimal string of a non-negative dyadic rational."""
        fr = fr % 2
        if fr == 0:
            return '0'
        num, den = (fr.numerator, fr.denominator)
        assert den & den - 1 == 0
        k = den.bit_length() - 1
        digits = str(num * 5 ** k).rjust(k + 1, '0')
        whole, frac = (digits[:-k] if k else digits, digits[-k:] if k else '')
        frac = frac.rstrip('0')
        return whole + ('.' + frac if frac else '')

    def _merge_zpow_kind_of(angle):
        if angle % _merge_zpow_Fraction(1, 2) == 0:
            return 'clifford'
        if angle % _merge_zpow_Fraction(1, 4) == 0:
            return 't'
        return 'rotation'

    def _merge_zpow_main():
        ap = _merge_zpow_argparse.ArgumentParser()
        ap.add_argument('kmx', type=_merge_zpow_Path)
        ap.add_argument('--out', type=_merge_zpow_Path, required=True)
        args = ap.parse_args()
        text = _read_text(args.kmx)
        ops, registers = _merge_zpow_kmsim.parse(text)
        sim = _merge_zpow_kmsim.Sim(ops, registers['x'])
        gates = []

        def before(index, s):
            kind, a, cond, angle, line = ops[index]
            if kind == 'Z_POW' and cond is None and (len(s.stack) == 1):
                vector = s.get(a[0])
                gates.append(dict(op=index, line=line, wire=a[0], angle=_merge_zpow_Fraction(angle), key=_merge_zpow_hashlib.sha256(vector.tobytes()).hexdigest(), nonzero=bool(vector.any())))
        sim.run(before=before)
        groups = {}
        for g in gates:
            groups.setdefault(g['key'], []).append(g)
        lines = text.split('\n')
        delete, report = (set(), [])
        for key, members in groups.items():
            if len(members) < 2 or not members[0]['nonzero']:
                continue
            if all((_merge_zpow_kind_of(m['angle']) == 'clifford' for m in members)):
                continue
            total = sum((m['angle'] for m in members)) % 2
            keep = members[0]
            before_kinds = [_merge_zpow_kind_of(m['angle']) for m in members]
            if total == 0:
                delete.update((m['line'] - 1 for m in members))
            else:
                lines[keep['line'] - 1] = f"Z_POW {keep['wire']} {_merge_zpow_dyadic(total)}"
                delete.update((m['line'] - 1 for m in members[1:]))
            report.append(dict(lines=[m['line'] for m in members], wires=[m['wire'] for m in members], angles=[str(m['angle']) for m in members], before=before_kinds, merged=str(total), after=_merge_zpow_kind_of(total) if total else 'removed'))
        out = '\n'.join((line for i, line in enumerate(lines) if i not in delete))
        args.out.write_text(out)
        count = lambda ks, name: sum((1 for k in ks if k == name))
        all_before = [_merge_zpow_kind_of(g['angle']) for g in gates]
        summary = dict(z_pow_gates=len(gates), groups_merged=len(report), t_before=count(all_before, 't'), rotations_before=count(all_before, 'rotation'), merges=report)
        args.out.with_suffix('.zpow.json').write_text(_merge_zpow_json.dumps(summary, indent=1) + '\n')
        print(_merge_zpow_json.dumps({k: v for k, v in summary.items() if k != 'merges'}), [(r['before'], r['after']) for r in report])
    if _merge_zpow___name__ == '__main__':
        _merge_zpow_main()

def _initialize_postpass():
    global _postpass_INTEGRATED_ROOT, _postpass_Path, _postpass__IntegratedPath, _postpass___file__, _postpass___name__, _postpass__ccx, _postpass_ap, _postpass_apply_rewrites, _postpass_argparse, _postpass_args, _postpass_json, _postpass_k, _postpass_records, _postpass_report, _postpass_sys, _postpass_text, _postpass_v
    _postpass_json = _import_component('json', 'tools/postpass.py', True)

    def _postpass__ccx(a, b, t, wires, constant, fresh_bit):
        wires = list(wires)
        if t not in wires:
            out = [f'CX {w} {t}' for w in wires]
            if constant:
                out.append(f'X {t}')
            return (out, False)
        rest = [w for w in wires if w != t]
        affine = [f'CX {w} {t}' for w in rest] + ([f'X {t}'] if constant else [])
        return (affine + [f'HMR {t} {fresh_bit}', f'CZ {a} {b} if {fresh_bit}'] + affine, True)

    def _postpass_apply_rewrites(text, records):
        lines = text.split('\n')
        used = set()
        for line in lines:
            for token in line.split():
                if token.startswith('b') and token[1:].isdigit():
                    used.add(int(token[1:]))
        next_bit = max(used) + 1 if used else 0
        applied = []
        for record in sorted(records, key=lambda r: r['line']):
            index = record['line'] - 1
            tokens = lines[index].split()
            kind, arguments = (tokens[0], tokens[1:])
            assert kind == record['kind'] and arguments == list(record['args']), (record, lines[index])
            wires, constant = (list(record['relation_wires']), int(record['relation_constant']))
            fresh = f'b{next_bit}'
            if kind == 'CCX':
                a, b, t = arguments
                assert record['product'] == 'ab'
                new, used_bit = _postpass__ccx(a, b, t, wires, constant, fresh)
            elif kind == 'CSWAP':
                c, x, y = arguments
                assert record['product'] == 'c(x^y)'
                moved = set(wires)
                if x in moved:
                    moved ^= {y}
                ordered = [w for w in wires if w in moved] + sorted(moved - set(wires))
                middle, used_bit = _postpass__ccx(c, x, y, ordered, constant, fresh)
                new = [f'CX {y} {x}'] + middle + [f'CX {y} {x}']
            elif kind == 'CCZ':
                pair = record['product']
                names = dict(zip('abc', arguments))
                third = names[({'a', 'b', 'c'} - set(pair)).pop()]
                new = [f'Z {third}' if w == third else f'CZ {w} {third}' for w in wires]
                if constant:
                    new.append(f'Z {third}')
                used_bit = False
            else:
                raise AssertionError(kind)
            if used_bit:
                next_bit += 1
            lines[index] = '\n'.join(new) if new else '# removed ' + lines[index]
            applied.append(dict(line=record['line'], op=record.get('op'), old=' '.join(tokens), new=new, stage=record.get('stage'), active=record.get('active', 1.0)))
        out = '\n'.join((line for line in lines if not line.startswith('# removed ')))
        return (out, dict(applied=len(applied), expected_toffoli_saving=sum((a['active'] for a in applied)), rewrites=applied))
    if _postpass___name__ == '__main__':
        _postpass_argparse = _import_component('argparse', 'tools/postpass.py', True)
        _postpass_sys = _import_component('sys', 'tools/postpass.py', True)
        _postpass_Path = _import_component('pathlib', 'tools/postpass.py', False).Path
        _postpass_ap = _postpass_argparse.ArgumentParser()
        _postpass_ap.add_argument('kmx', type=_postpass_Path)
        _postpass_ap.add_argument('records', type=_postpass_Path)
        _postpass_ap.add_argument('--out', type=_postpass_Path, required=True)
        _postpass_args = _postpass_ap.parse_args()
        _postpass_records = _json_loads(_read_text(_postpass_args.records))
        _postpass_records = _postpass_records['findings'] if isinstance(_postpass_records, dict) else _postpass_records
        _postpass_text, _postpass_report = _postpass_apply_rewrites(_read_text(_postpass_args.kmx), _postpass_records)
        _postpass_args.out.write_text(_postpass_text)
        print(_postpass_json.dumps({k: v for k, v in _postpass_report.items() if k != 'rewrites'}))

def _initialize_candidate10_setup():
    global _candidate10_setup_BASE, _candidate10_setup_GATE_SHA, _candidate10_setup_HERE, _candidate10_setup_INTEGRATED_ROOT, _candidate10_setup_NARROW, _candidate10_setup_Path, _candidate10_setup_ROUND, _candidate10_setup__INSTALLED, _candidate10_setup__IntegratedPath, _candidate10_setup___file__, _candidate10_setup___name__, _candidate10_setup_accepted_gate, _candidate10_setup_check_manifest, _candidate10_setup_hashlib, _candidate10_setup_importlib, _candidate10_setup_install, _candidate10_setup_json, _candidate10_setup_load, _candidate10_setup_name, _candidate10_setup_old, _candidate10_setup_os, _candidate10_setup_sha, _candidate10_setup_sys, _candidate10_setup_verify_sources
    _candidate10_setup_Path = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', False).Path
    _candidate10_setup_os = _import_component('os', 'work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', True)
    _candidate10_setup_sys = _import_component('sys', 'work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', True)
    for _candidate10_setup_name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        _candidate10_setup_os.environ[_candidate10_setup_name] = '1'
    _candidate10_setup_HERE = _candidate10_setup_Path(_candidate10_setup___file__).resolve().parent
    _candidate10_setup_NARROW = _candidate10_setup_HERE.parents[2]
    _candidate10_setup_BASE = _candidate10_setup_NARROW / 'native/candidate07'

    def _candidate10_setup_load(name, path):
        path = _candidate10_setup_Path(path).resolve()
        pass
        if name not in _candidate10_setup_sys.modules:
            spec = _spec(name, path)
            module = _new_module(spec)
            _candidate10_setup_sys.modules[name] = module
            spec.loader.exec_module(module)
        module = _candidate10_setup_sys.modules[name]
        pass
        return module
    _candidate10_setup_old = _candidate10_setup_load('variant', _candidate10_setup_BASE / 'variant.py')
    _candidate10_setup__INSTALLED = None

    def _candidate10_setup_accepted_gate():
        return {'Q': 48, 'adapter_paths': {'normalization': 'arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', 'root': 'arithmetic_round2/research/root_normalization/native_rn3/root192.py', 'divider': 'arithmetic_round2/research/divider/native_ar004/adapter.py', 'product': 'arithmetic_round2/research/product_coefficient/native_v3/adapter.py', 'coefficient': 'arithmetic_round2/research/product_coefficient/native_transfer.py'}}

    def _candidate10_setup_install():
        global _candidate10_setup__INSTALLED
        gate = _candidate10_setup_accepted_gate()
        if _candidate10_setup__INSTALLED is None:
            _candidate10_setup_old.install()
            modules = {name: _candidate10_setup_load('candidate10_adapter_' + name, _candidate10_setup_NARROW / path) for name, path in gate['adapter_paths'].items()}
            lifecycle10 = _import_component('lifecycle10', 'work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', True)
            pass
            lifecycle = lifecycle10
            baseline = _candidate10_setup_old.inherited_module('lifecycle06').baseline
            lifecycle.baseline = baseline
            modules['lifecycle'] = lifecycle
            coefficient = modules['coefficient']
            product = modules['product']

            def coefficient_inverse(builder, v, D, H, token, dirty):
                return coefficient.coefficient_inverse(builder, v, D, H, token, dirty, baseline=baseline)

            def product_inverse(builder, v, D, word, token, dirty):
                return product.product_inverse(builder, v, D, word, token, dirty, baseline=baseline)
            baseline.coefficient_inverse = coefficient_inverse
            lifecycle.product_inverse = product_inverse
            modules['divider'].install(_candidate10_setup_old.divider)
            _candidate10_setup__INSTALLED = modules
        pass
        return _candidate10_setup__INSTALLED

def _initialize_lifecycle10():
    global _lifecycle10_CUT_HOOK, _lifecycle10_INTEGRATED_ROOT, _lifecycle10__IntegratedPath, _lifecycle10___file__, _lifecycle10___name__, _lifecycle10__mark, _lifecycle10_baseline, _lifecycle10_emit_body, _lifecycle10_product_inverse
    _lifecycle10_baseline = None
    _lifecycle10_product_inverse = None
    _lifecycle10_CUT_HOOK = None

def _initialize_history12_kernel():
    global _history12_kernel_INTEGRATED_ROOT, _history12_kernel__IntegratedPath, _history12_kernel___file__, _history12_kernel___name__, _history12_kernel_base, _history12_kernel_cleanup_divider
    _history12_kernel_base = _import_component('top12_kernel', 'work/c10/narrow/arithmetic_round2/research/divider/history12_kernel.py', False)

def _initialize_native_ar004_divider():
    global _native_ar004_divider_ACCEPTANCE, _native_ar004_divider_ACCEPTANCE_SHA, _native_ar004_divider_CONTRACT, _native_ar004_divider_HERE, _native_ar004_divider_INTEGRATED_ROOT, _native_ar004_divider_KERNEL, _native_ar004_divider_KERNEL_SHA, _native_ar004_divider_NARROW, _native_ar004_divider_Path, _native_ar004_divider_TOP_KERNEL, _native_ar004_divider_TOP_KERNEL_SHA, _native_ar004_divider__IntegratedPath, _native_ar004_divider___file__, _native_ar004_divider___name__, _native_ar004_divider_bind, _native_ar004_divider_hashlib, _native_ar004_divider_importlib, _native_ar004_divider_install, _native_ar004_divider_json, _native_ar004_divider_kernel, _native_ar004_divider_load, _native_ar004_divider_sha, _native_ar004_divider_sys, _native_ar004_divider_verify
    _native_ar004_divider_Path = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', False).Path
    _native_ar004_divider_sys = _import_component('sys', 'work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', True)
    _native_ar004_divider_HERE = _native_ar004_divider_Path(_native_ar004_divider___file__).resolve().parent
    _native_ar004_divider_KERNEL = _native_ar004_divider_HERE.parent / 'history12_kernel.py'
    _native_ar004_divider_TOP_KERNEL = _native_ar004_divider_HERE.parent / 'top12_kernel.py'

    def _native_ar004_divider_load(name, path):
        if name not in _native_ar004_divider_sys.modules:
            spec = _spec(name, path)
            module = _new_module(spec)
            _native_ar004_divider_sys.modules[name] = module
            spec.loader.exec_module(module)
        module = _native_ar004_divider_sys.modules[name]
        pass
        return module

    def _native_ar004_divider_kernel():
        pass
        base = _native_ar004_divider_load('top12_kernel', _native_ar004_divider_TOP_KERNEL)
        result = _native_ar004_divider_load('_ar004_frozen_history12_kernel', _native_ar004_divider_KERNEL)
        assert result.base is base
        return result

    def _native_ar004_divider_bind(divider):
        pass
        pass
        pass
        pass
        implementation = _native_ar004_divider_kernel()

        def cleanup(builder, token):
            return implementation.cleanup_divider(divider, builder, token)
        return cleanup

    def _native_ar004_divider_install(divider):
        forward, phase, initializer = (divider.compute_divider, divider.phase_endpoint, divider.initialize_u12)
        divider.cleanup_divider = _native_ar004_divider_bind(divider)
        assert divider.compute_divider is forward and divider.phase_endpoint is phase
        assert divider.initialize_u12 is initializer
        return divider

def _initialize_top12_kernel():
    global _top12_kernel_INTEGRATED_ROOT, _top12_kernel_MAJORITY_TRUTH, _top12_kernel__IntegratedPath, _top12_kernel___file__, _top12_kernel___name__, _top12_kernel__compute_carry, _top12_kernel__erase_carry, _top12_kernel__phase_borrow, _top12_kernel__phase_terminal, _top12_kernel_cleanup_divider, _top12_kernel_cleanup_initial_missing12, _top12_kernel_initial_bit_plan, _top12_kernel_inverse_lower12, _top12_kernel_last_feed_and_initial, _top12_kernel_pa, _top12_kernel_phase_quadratic

def _initialize_native_transfer():
    global _native_transfer_COMPONENT_CONTRACT, _native_transfer_INTEGRATED_ROOT, _native_transfer__IntegratedPath, _native_transfer___file__, _native_transfer___name__, _native_transfer_coefficient_inverse, _native_transfer_inverse_low6

    def _native_transfer_inverse_low6(builder, source, target, debt, *, carry_in, top_outcome, ar, omit_wrap=False):
        source = list(source)
        b = list(target)
        km = ar.km
        assert len(b) == 6 and 1 <= len(source) <= 5
        assert debt.width == 7 and (not debt.consumed)
        assert set(debt.measurements) == {1, 2, 3, 4, 5}
        assert isinstance(carry_in, km.q) and isinstance(top_outcome, km.b)
        assert len(set(source + b + [carry_in])) == len(source) + len(b) + 1
        assert builder.max_qubits - builder.num_allocated_qubits >= 5
        entry = builder.num_allocated_qubits
        a = source + [False] * (6 - len(source))
        assert a[5] is False
        debt.consumed = True
        builder.x(km.array(b))
        frames = []
        carry = carry_in
        for i in range(5):
            frame = ar._compute_carry(builder, a[i], b[i], carry, preserve=None)
            assert isinstance(frame.outgoing, km.q)
            outcome = debt.measurements.pop(i + 1)
            builder.push_condition(outcome)
            builder.z(frame.outgoing)
            builder.pop_condition()
            builder.free(outcome)
            frames.append(frame)
            carry = frame.outgoing
        if not omit_wrap:
            builder.push_condition(top_outcome)
            ar.phase_quadratic(builder, [False, b[5], carry], ar.MAJORITY_TRUTH)
            builder.pop_condition()
        builder.cx(carry, b[5])
        for frame in reversed(frames):
            ar._erase_carry(builder, frame, write_sum=True)
        builder.x(km.array(b))
        assert not debt.measurements and builder.num_allocated_qubits == entry

    def _native_transfer_coefficient_inverse(builder, v, D, H, token, dirty, *, baseline, omit_wrap=False, omit_saved=False):
        """Drop-in logical API with an explicit immutable baseline dependency."""
        ar = baseline.ar
        km = baseline.km
        assert len(D) == 13 and len(H) == 5 and (token.window == 7)
        assert len(token.row_debts) == 5 and token.saved_bit is not None
        assert token.saved_bit not in list(D) + list(H)
        S = [v[8]] + list(H)
        entry = builder.num_allocated_qubits
        ar._deferred_overflow(builder, v[:5], S, D, token, inverse=True)
        assert builder.num_allocated_qubits == entry and token.overflow_debt.consumed
        saved = token.saved_bit
        top = D[6]
        phase = builder.alloc_bits(1)[0]
        builder.hmr(top, phase)
        builder.cx(saved, top)
        builder.cx(top, saved)
        builder.free(saved)
        token.saved_bit = None
        for i in reversed(range(5)):
            k = 4 - i
            carry = baseline._coefficient_carry(builder, S, v[i], k)
            for q in D[:6]:
                builder.cx(v[i], q)
            _native_transfer_inverse_low6(builder, S[k + 1:], D[:6], token.row_debts[i], carry_in=carry, top_outcome=phase, ar=ar, omit_wrap=omit_wrap)
            for q in D[:6]:
                builder.cx(v[i], q)
            baseline._clear_coefficient_carry(builder, S, v[i], k, carry)
        if omit_saved:
            builder.free(phase)
        else:
            ar.repay_saved_bit(builder, top, phase)
        assert all((d.consumed and (not d.measurements) for d in token.row_debts))
        assert token.overflow_debt.consumed and (not token.overflow_debt.measurements)
        assert builder.num_allocated_qubits == entry - 1

def _initialize_native_v3_product():
    global _native_v3_product_COMPONENT_CONTRACT, _native_v3_product_INTEGRATED_ROOT, _native_v3_product__IntegratedPath, _native_v3_product___file__, _native_v3_product___name__, _native_v3_product_product_inverse, _native_v3_product_restore_v3

def _initialize_normalization9475():
    global _normalization9475_ACCEPTANCE, _normalization9475_ACCEPTANCE_SHA, _normalization9475_CONTRACT, _normalization9475_CONTROLS, _normalization9475_FORWARD_ROWS, _normalization9475_FRAME, _normalization9475_HERE, _normalization9475_INTEGRATED_ROOT, _normalization9475_MASKS, _normalization9475_MAX_X, _normalization9475_NARROW, _normalization9475_Path, _normalization9475__IntegratedPath, _normalization9475___file__, _normalization9475___name__, _normalization9475_cb, _normalization9475_checked, _normalization9475_forward, _normalization9475_hashlib, _normalization9475_importlib, _normalization9475_inverse, _normalization9475_joint_last_phase, _normalization9475_json, _normalization9475_km, _normalization9475_measured, _normalization9475_old, _normalization9475_path, _normalization9475_prefix_phase, _normalization9475_prepare, _normalization9475_route_lane, _normalization9475_spec, _normalization9475_sys, _normalization9475_thermometer_matrix
    _normalization9475_Path = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', False).Path
    _normalization9475_sys = _import_component('sys', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', True)
    _normalization9475_HERE = _normalization9475_Path(_normalization9475___file__).resolve().parent
    _normalization9475_NARROW = _normalization9475_HERE.parents[3]
    _normalization9475_path = _normalization9475_NARROW / 'research/quantized_producer/pair_normalization.py'
    _normalization9475_spec = _spec('_round2_rn2df_private_pair_normalizer', _normalization9475_path)
    _normalization9475_old = _new_module(_normalization9475_spec)
    _normalization9475_sys.modules[_normalization9475_spec.name] = _normalization9475_old
    _normalization9475_spec.loader.exec_module(_normalization9475_old)
    _normalization9475_km, _normalization9475_cb = (_normalization9475_old.km, _normalization9475_old.cb)
    _normalization9475_thermometer_matrix = _import_component('thermometer_cleanup', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', False).thermometer_matrix
    _normalization9475_FORWARD_ROWS = tuple(_normalization9475_thermometer_matrix(10))
    assert tuple((j for j, row in enumerate(_normalization9475_FORWARD_ROWS, 1) if row >> 6 & 1)) == (1, 3, 5, 7)
    _normalization9475_MASKS = tuple(range(1, 9))
    _normalization9475_FRAME = [['cx', 7, 6], ['cx', 7, 5], ['cx', 7, 4], ['cx', 7, 3], ['cx', 7, 2], ['cx', 7, 1], ['cx', 7, 0], ['cx', 6, 4], ['cx', 6, 2], ['cx', 6, 0], ['cx', 5, 4], ['cx', 5, 1], ['cx', 5, 0], ['cx', 4, 0], ['cx', 3, 2], ['cx', 3, 1], ['cx', 3, 0], ['cx', 2, 0], ['cx', 1, 0]]
    _normalization9475_CONTROLS = [{'first': 0, 'second': 1, 'terms': [1, 2, 3, 4, 5, 6, 7, 8]}, {'first': 2, 'second': 3, 'terms': [1, 2, 3, 4, 5, 6, 7, 8]}, {'first': 4, 'second': 5, 'terms': [1, 2, 3, 4, 5, 6, 7, 8]}, {'first': 6, 'second': 7, 'terms': [1, 2, 3, 4, 5, 6, 7, 8]}, {'first': 8, 'second': 9, 'terms': [1, 2, 3, 4, 5, 6, 7, 8]}, {'first': 0, 'second': 2, 'terms': [1, 3, 5, 7]}, {'first': 1, 'second': 3, 'terms': [2, 4, 6, 8]}, {'first': 4, 'second': 6, 'terms': [1, 3, 5, 7]}, {'first': 5, 'second': 7, 'terms': [2, 4, 6, 8]}, {'first': 8, 'second': 10, 'terms': [1, 3, 5, 7]}, {'first': 0, 'second': 4, 'terms': [1, 5]}, {'first': 1, 'second': 5, 'terms': [2, 6]}, {'first': 2, 'second': 6, 'terms': [3, 7]}, {'first': 3, 'second': 7, 'terms': [4, 8]}, {'first': 0, 'second': 8, 'terms': [1]}, {'first': 1, 'second': 9, 'terms': [2]}, {'first': 2, 'second': 10, 'terms': [3]}]

    def _normalization9475_route_lane(builder, lane, T):
        count = 0
        for op in _normalization9475_old.operations(len(lane)):
            terms = [i for i in op['prefix_terms'] if i <= 10]
            assert terms and 0 not in terms
            control = T[terms[0] - 1]
            others = [T[i - 1] for i in terms[1:]]
            for q in others:
                builder.cx(q, control)
            builder.cswap(control, lane[op['first']], lane[op['second']])
            count += 1
            for q in reversed(others):
                builder.cx(q, control)
        assert count == {10: 15, 11: 17}[len(lane)]

    def _normalization9475_forward(builder, x, flags):
        x = list(x)
        flags = list(flags)
        P = []
        assert len(x) == 22 and len(flags) == 4
        for length in range(1, 21):
            q = builder.alloc_qubits(1)[0]
            data = x[22 - length]
            if length == 1:
                builder.x(q)
                builder.cx(data, q)
            elif length == 2:
                builder.cx(P[-1], q)
                builder.cx(data, q)
            else:
                builder.x(data)
                builder.ccx(P[-1], data, q)
                builder.x(data)
            P.append(q)
        T = P[1::2]
        for bit, flag in enumerate(flags):
            for j in range(1 << bit, 11, 1 << bit):
                builder.cx(T[j - 1], flag)
        for position in range(2, 22):
            for prefix in (21 - position, 22 - position):
                if prefix == 0:
                    builder.x(x[position])
                else:
                    builder.cx(P[prefix - 1], x[position])
        builder.x(x[21])
        for q in P:
            builder.cx(q, x[21])
        builder.x(x[1])
        builder.ccx(T[-1], x[1], x[21])
        builder.x(x[1])
        for target, prefixes in ((x[0], P), (x[1], P[:-1])):
            builder.x(target)
            builder.cx(x[21], target)
            for q in prefixes:
                builder.cx(q, target)
        _normalization9475_route_lane(builder, x[0::2], T)
        _normalization9475_route_lane(builder, x[1:21:2], T)
        builder.x(x[20])
        builder.cx(x[21], x[20])
        for j in range(1, 11):
            q = P[2 * j - 2]
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            if j == 1:
                _normalization9475_cb.emit_phase(builder, [T[0], x[21]], m, _normalization9475_old.ODD_FIRST)
            else:
                _normalization9475_cb.emit_phase(builder, [T[j - 2], T[j - 1], x[21]], m, _normalization9475_old.ODD_OTHER)
            builder.free(m)
            builder.free(q)
        parity = builder.alloc_bits(1)[0]
        builder.bit_store(parity, False)
        for q, row in zip(T, _normalization9475_FORWARD_ROWS):
            outcome = builder.alloc_bits(1)[0]
            builder.hmr(q, outcome)
            builder.push_condition(outcome)
            for mask in range(1, 11):
                if row >> mask - 1 & 1 == 0 or mask == 7:
                    continue
                controls = [flags[i] for i in range(4) if mask >> i & 1]
                if len(controls) == 1:
                    builder.z(controls[0])
                else:
                    assert len(controls) == 2
                    builder.cz(*controls)
            builder.pop_condition()
            if row >> 7 - 1 & 1:
                builder.cx(outcome, parity)
            builder.free(outcome)
            builder.free(q)
        builder.push_condition(parity)
        builder.ccz(*flags[:3])
        builder.pop_condition()
        builder.free(parity)

    def _normalization9475_prepare(builder, flags):
        monomials = {1 << i: q for i, q in enumerate(flags)}
        helpers = []
        for mask in _normalization9475_MASKS:
            if mask in monomials:
                continue
            low = mask & -mask
            q = builder.alloc_qubits(1)[0]
            builder.ccx(monomials[mask ^ low], monomials[low], q)
            monomials[mask] = q
            helpers.append(q)
        assert len(helpers) == 4
        wires = [monomials[m] for m in _normalization9475_MASKS]
        for name, a, b in _normalization9475_FRAME:
            if name == 'cx':
                builder.cx(wires[a], wires[b])
            else:
                builder.swap(wires[a], wires[b])
        return (dict(zip(range(1, 9), wires)), helpers)

    def _normalization9475_measured(builder, q, role=None):
        outcome = builder.alloc_bits(1)[0]
        if role is not None and hasattr(builder, 'select_outcome'):
            builder.select_outcome(outcome, role)
        builder.hmr(q, outcome)
        return outcome

    def _normalization9475_prefix_phase(builder, outcome, previous, a, b):
        builder.push_condition(outcome)
        builder.z(previous)
        builder.cz(previous, a)
        builder.cz(previous, b)
        builder.ccz(previous, a, b)
        builder.pop_condition()

    def _normalization9475_joint_last_phase(builder, x, mB, m3, *, omit_final_helper_fix=False):
        builder.cx(x[21], x[20])
        builder.x(x[20])
        for i in (18, 19, 16, 17):
            builder.x(x[i])
        a, t2 = list(builder.alloc_qubits(2))
        ma, mt = list(builder.alloc_bits(2))
        builder.bit_store(ma, False)
        builder.bit_store(mt, False)
        builder.push_condition(m3)
        builder.ccx(x[20], x[18], a)
        builder.ccx(a, x[19], t2)
        builder.push_condition(mB)
        builder.z(t2)
        builder.pop_condition()
        builder.ccz(t2, x[16], x[17])
        builder.hmr(t2, mt)
        builder.push_condition(mt)
        builder.cz(a, x[19])
        builder.pop_condition()
        builder.hmr(a, ma)
        builder.push_condition(ma)
        if not omit_final_helper_fix:
            builder.cz(x[20], x[18])
        builder.pop_condition()
        builder.pop_condition()
        builder.free(mt)
        builder.free(ma)
        builder.free(t2)
        builder.free(a)
        builder.x(m3)
        builder.push_condition(m3)
        builder.push_condition(mB)
        builder.ccz(x[20], x[18], x[19])
        builder.pop_condition()
        builder.pop_condition()
        builder.x(m3)
        for i in (17, 16, 19, 18):
            builder.x(x[i])
        builder.x(x[20])
        builder.cx(x[21], x[20])

    def _normalization9475_inverse(builder, x, flags, *, omit_final_helper_fix=False):
        x, flags = (list(x), list(flags))
        T, helpers = _normalization9475_prepare(builder, flags)
        for operation in reversed(_normalization9475_CONTROLS):
            terms = operation['terms']
            control, others = (T[terms[0]], [T[j] for j in terms[1:]])
            for q in others:
                builder.cx(q, control)
            for lane in range(2):
                builder.cswap(control, x[2 * operation['first'] + lane], x[2 * operation['second'] + lane])
            for q in reversed(others):
                builder.cx(q, control)
        A = T.pop(1)
        builder.x(A)
        builder.cx(x[20], A)
        builder.cx(x[21], A)
        T[9] = A
        mB = _normalization9475_measured(builder, T.pop(2), 'B')
        _normalization9475_prefix_phase(builder, mB, T[9], x[2], x[3])
        for j in reversed(range(4, 10)):
            outcome = _normalization9475_measured(builder, T[j])
            _normalization9475_prefix_phase(builder, outcome, T[j - 1], x[22 - 2 * j], x[23 - 2 * j])
            builder.free(outcome)
        m3 = _normalization9475_measured(builder, T[3], 'T3')
        builder.free(_normalization9475_km.array(helpers))
        _normalization9475_joint_last_phase(builder, x, mB, m3, omit_final_helper_fix=omit_final_helper_fix)
        builder.free(mB)
        builder.free(m3)

def _initialize_root192():
    global _root192_ENGINE, _root192_HERE, _root192_INTEGRATED_ROOT, _root192_NARROW, _root192_ORIGINAL_FORWARD, _root192_ORIGINAL_INVERSE, _root192_ORIGINAL_ROOT_STEP, _root192_Path, _root192__IntegratedPath, _root192___file__, _root192___name__, _root192__a2_xor, _root192__carry_frame, _root192__p_frame, _root192__private, _root192_arithmetic, _root192_arr, _root192_carry_clear, _root192_carry_prepare, _root192_convert_high, _root192_forward, _root192_hashlib, _root192_importlib, _root192_initial_low_xor, _root192_inverse, _root192_json, _root192_km, _root192_last_step, _root192_original, _root192_sys
    _root192_Path = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', False).Path
    _root192_sys = _import_component('sys', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', True)
    _root192_HERE = _root192_Path(_root192___file__).resolve().parent
    _root192_NARROW = _root192_HERE.parents[3]
    _root192_ENGINE = _root192_NARROW / 'checkpoint002/cleanroom/baseline_stage97/engine'
    _root192_sys.path[:0] = [str(_root192_NARROW / 'base/official/kickmix'), str(_root192_ENGINE)]
    _root192_km = _import_component('kickmix', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', False)

    def _root192__private(name, path, expected):
        pass
        spec = _spec(name, path)
        module = _new_module(spec)
        _root192_sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    _root192_original = _root192__private('_round2_rn3_immutable_odd_sqrt', _root192_NARROW / 'checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', '0a60a631cb97dc39ea0e76e7ab2dc26300fd4f96218a73e0e56262c59586c144')
    _root192_arithmetic = _root192__private('fusion._round2_rn3_immutable_arithmetic', _root192_ENGINE / 'fusion/arithmetic.py', '154621ee98dd8139eab601d5d794be881a5ebf38ebe1c542cf69b8fb97ee1453')
    _root192_original.add = _root192_arithmetic.add
    _root192_ORIGINAL_ROOT_STEP = _root192_original._root_step

    def _root192_arr(wires):
        return _root192_km.array(list(wires))

    def _root192_last_step(builder, remainder, older, b, *, initial=False, inverse=False):
        """The inherited j11 zero-pair rule plus the new j12 carry alias."""
        remainder = list(remainder)
        older = list(older)
        j = len(remainder) - 3
        if j < 11:
            return _root192_ORIGINAL_ROOT_STEP(builder, remainder, older, b, initial=initial, inverse=inverse)
        assert j in (11, 12) and (not initial) and isinstance(b, _root192_km.q)
        assert len(set(remainder + older + [b])) == len(remainder) + len(older) + 1
        low = remainder[:3]
        high = remainder[3:]
        if hasattr(builder, 'values'):
            pair = builder.full if inverse else 0
            assert builder.value(low[0]) == builder.value(low[1]) == pair
            if j == 12:
                expected = builder.full ^ builder.value(b) ^ builder.value(older[0]) if inverse else builder.full
                assert builder.value(high[0]) == expected, ('j12_first_high', inverse)
        if not inverse:
            builder.x(low[0])
            builder.x(low[1])
        builder.cx(b, _root192_arr(high))
        if inverse:
            _root192_original._add_leading_one(builder, high, inverse=True)
        if j == 12:
            builder.cx(b, high[0])
            builder.cx(older[0], high[0])
            _root192_original.add(builder, older[1:], high[1:], carry_in=older[0], subtract=inverse)
        else:
            _root192_original.add(builder, older, high, carry_in=b, subtract=inverse)
        if not inverse:
            _root192_original._add_leading_one(builder, high)
        builder.cx(b, _root192_arr(high))
        if inverse:
            builder.x(low[0])
            builder.x(low[1])

    def _root192_initial_low_xor(builder, Q, low):
        """The preconversion low word is (1,1,1,1 xor Q1 xor Q2)."""
        builder.x(_root192_arr(low))
        builder.cx(Q[1], low[3])
        builder.cx(Q[2], low[3])

    def _root192__p_frame(builder, Q):
        builder.cx(Q[2], Q[0])
        builder.cx(Q[2], Q[1])

    def _root192__carry_frame(builder, Q, p):
        builder.x(Q[3])
        for q in Q[:3]:
            builder.cx(q, Q[3])
        builder.x(p)
        builder.cx(Q[0], p)
        builder.cx(Q[2], p)

    def _root192__a2_xor(builder, Q, target):
        builder.x(target)
        for q in Q[:3]:
            builder.cx(q, target)

    def _root192_carry_prepare(builder, Q):
        p, c = builder.alloc_qubits(2)
        _root192__p_frame(builder, Q)
        builder.ccx(Q[0], Q[1], p)
        _root192__p_frame(builder, Q)
        _root192__a2_xor(builder, Q, c)
        _root192__carry_frame(builder, Q, p)
        builder.ccx(Q[3], p, c)
        _root192__carry_frame(builder, Q, p)
        return (p, c)

    def _root192_carry_clear(builder, Q, p, c):
        _root192__a2_xor(builder, Q, c)
        _root192__carry_frame(builder, Q, p)
        builder.del_and(Q[3], p, c)
        _root192__carry_frame(builder, Q, p)
        builder.free(c)
        _root192__p_frame(builder, Q)
        builder.del_and(Q[0], Q[1], p)
        _root192__p_frame(builder, Q)
        builder.free(p)

    def _root192_convert_high(builder, Q, high, *, inverse=False):
        p, c = _root192_carry_prepare(builder, Q)
        builder.cx(Q[0], _root192_arr(high))
        if inverse:
            _root192_original._add_leading_one(builder, high, inverse=True)
        _root192_original.add(builder, Q[4:], high, carry_in=c, subtract=inverse)
        if not inverse:
            _root192_original._add_leading_one(builder, high)
        builder.cx(Q[0], _root192_arr(high))
        _root192_carry_clear(builder, Q, p, c)

    def _root192_forward(builder, norm):
        norm = list(norm)
        assert len(norm) == 22 and len(set(norm)) == 22
        builder.x(norm[20])
        builder.cx(norm[20], norm[21])
        remainder = norm[20:22]
        roots = []
        for j in range(1, 13):
            pair = norm[20 - 2 * j:22 - 2 * j] if j <= 10 else list(builder.alloc_qubits(2))
            if j == 1:
                b = True
                older = []
                remainder = pair + remainder
            else:
                b = remainder[-1]
                builder.x(b)
                older = roots
                roots = [b] + roots
                remainder = pair + remainder[:-1]
            _root192_last_step(builder, remainder, older, b, initial=j == 1)
        b = remainder[-1]
        builder.x(b)
        Q = [b] + roots
        W = remainder[:-1]
        _root192_initial_low_xor(builder, Q, W[:4])
        builder.free(_root192_arr(W[:4]))
        _root192_convert_high(builder, Q, W[4:])
        assert Q == norm[10:] and W[4:] == norm[:10]
        return dict(root=Q, residual=W[4:])

    def _root192_inverse(builder, norm):
        norm = list(norm)
        Q = norm[10:]
        high = norm[:10]
        _root192_convert_high(builder, Q, high, inverse=True)
        low = list(builder.alloc_qubits(4))
        _root192_initial_low_xor(builder, Q, low)
        W = low + high
        b = Q[0]
        roots = Q[1:]
        builder.x(b)
        remainder = W + [b]
        for j in reversed(range(1, 13)):
            pair = remainder[:2]
            if j == 1:
                b = True
                older = []
            else:
                b = roots[0]
                older = roots[1:]
            _root192_last_step(builder, remainder, older, b, initial=j == 1, inverse=True)
            if j == 1:
                remainder = remainder[2:]
            else:
                remainder = remainder[2:] + [b]
                builder.x(b)
                roots = older
            if j >= 11:
                builder.free(_root192_arr(pair))
            else:
                assert pair == norm[20 - 2 * j:22 - 2 * j]
        assert remainder == norm[20:] and (not roots)
        builder.cx(norm[20], norm[21])
        builder.x(norm[20])
        return norm

def _initialize_branch_prover():
    global _branch_prover_Callable, _branch_prover_Fraction, _branch_prover_INTEGRATED_ROOT, _branch_prover_Mapping, _branch_prover_Operation, _branch_prover_Program, _branch_prover_Sequence, _branch_prover__IntegratedPath, _branch_prover___file__, _branch_prover___name__, _branch_prover_annotations, _branch_prover_dataclass, _branch_prover_exhaustively_check, _branch_prover_generated_text, _branch_prover_integer_bits, _branch_prover_integer_of, _branch_prover_io, _branch_prover_itertools, _branch_prover_math, _branch_prover_shlex, _branch_prover_symbolic_check
    _branch_prover_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', False).dataclass
    _branch_prover_Fraction = _import_component('fractions', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', False).Fraction
    _branch_prover_io = _import_component('io', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', True)
    _branch_prover_math = _import_component('math', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', True)
    _branch_prover_shlex = _import_component('shlex', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', True)

    @_branch_prover_dataclass(frozen=True)
    class _branch_prover_Operation:
        kind: str
        arguments: tuple[str, ...]
        condition: str | None = None
        half_turns: Fraction | None = None
        event: int | None = None

    def _branch_prover_generated_text(circuit) -> str:
        """Serialize a circuit produced by this task; never takes a reference path."""
        stream = _branch_prover_io.StringIO()
        circuit.to_file(stream, format='kmx')
        return stream.getvalue()

    class _branch_prover_Program:
        """Exact bit/phase semantics for the small gate set used by our kernels."""

        def __init__(self, text: str):
            self.operations = []
            self.registers = {}
            register_ids = {}
            self.wires = set()
            self.measurements = 0
            denominators = [1]
            ignored = {'INFO_TAG', 'DEBUG_PRINT'}
            arities = {'X': 1, 'CX': 2, 'CCX': 3, 'SWAP': 2, 'CSWAP': 3, 'Z': 1, 'CZ': 2, 'CCZ': 3, 'NEG': 0, 'HMR': 2, 'R': 1, 'Z_POW': 2, 'BIT_STORE0': 1, 'BIT_STORE1': 1, 'BIT_INVERT': 1, 'PUSH_CONDITION': 0, 'POP_CONDITION': 0}
            for number, line in enumerate(text.splitlines(), 1):
                tokens = _branch_prover_shlex.split(line, comments=True)
                if not tokens:
                    continue
                kind, *arguments = tokens
                if kind in ignored:
                    continue
                if kind == 'APPEND_TO_REGISTER':
                    register_ids.setdefault(arguments[1], []).append(arguments[0])
                    continue
                if kind == 'REGISTER':
                    self.registers[arguments[1]] = register_ids[arguments[0]]
                    continue
                condition = None
                if 'if' in arguments:
                    index = arguments.index('if')
                    if index != len(arguments) - 2:
                        raise ValueError(f'Unsupported condition on line {number}: {line}')
                    condition = arguments[-1]
                    arguments = arguments[:index]
                    self.wires.add(condition)
                if kind not in arities or len(arguments) != arities[kind]:
                    raise ValueError(f'Unsupported instruction on line {number}: {line}')
                angle = None
                if kind == 'Z_POW':
                    angle = _branch_prover_Fraction(arguments[-1])
                    arguments = arguments[:-1]
                    denominators.append(angle.denominator)
                event = None
                if kind == 'HMR':
                    event = self.measurements
                    self.measurements += 1
                self.wires.update(arguments)
                self.operations.append(_branch_prover_Operation(kind, tuple(arguments), condition, angle, event))
            self.denominator = _branch_prover_math.lcm(*denominators)
            self.modulus = 2 * self.denominator
            self.phase_steps = {i: int(op.half_turns * self.denominator) for i, op in enumerate(self.operations) if op.kind == 'Z_POW'}

        @property
        def quantum_wires(self):
            return sorted((wire for wire in self.wires if wire.startswith('q')), key=lambda item: int(item[1:]))

        def execute(self, initial: Mapping[str, int], transcript: int=0):
            state = {wire: 0 for wire in self.wires}
            state.update(initial)
            state['0'], state['1'] = (0, 1)
            state['False'], state['True'] = (0, 1)
            phase = 0
            stack = [True]
            den = self.denominator
            for index, op in enumerate(self.operations):
                k, a = (op.kind, op.arguments)
                active = stack[-1] and (op.condition is None or bool(state[op.condition]))
                if k == 'PUSH_CONDITION':
                    stack.append(active)
                    continue
                if k == 'POP_CONDITION':
                    if len(stack) == 1:
                        raise AssertionError('Unmatched POP_CONDITION')
                    stack.pop()
                    continue
                if not active:
                    continue
                if k == 'X':
                    state[a[0]] ^= 1
                elif k == 'CX':
                    state[a[1]] ^= state[a[0]]
                elif k == 'CCX':
                    state[a[2]] ^= state[a[0]] & state[a[1]]
                elif k == 'SWAP':
                    state[a[0]], state[a[1]] = (state[a[1]], state[a[0]])
                elif k == 'CSWAP':
                    if state[a[0]]:
                        state[a[1]], state[a[2]] = (state[a[2]], state[a[1]])
                elif k in ('Z', 'CZ', 'CCZ', 'NEG'):
                    phase += den * _branch_prover_math.prod((state[wire] for wire in a))
                elif k == 'Z_POW':
                    phase += self.phase_steps[index] * state[a[0]]
                elif k == 'HMR':
                    outcome = transcript >> op.event & 1
                    phase += den * outcome * state[a[0]]
                    state[a[0]] = 0
                    state[a[1]] = outcome
                elif k == 'R':
                    if state[a[0]]:
                        raise AssertionError(f'Reset would erase nonzero {a[0]} at instruction {index}; input={dict(initial)}, HMR transcript={transcript}')
                elif k == 'BIT_STORE0':
                    state[a[0]] = 0
                elif k == 'BIT_STORE1':
                    state[a[0]] = 1
                elif k == 'BIT_INVERT':
                    state[a[0]] ^= 1
                else:
                    raise AssertionError(k)
            if len(stack) != 1:
                raise AssertionError('Unclosed condition stack')
            return (state, _branch_prover_Fraction(phase % self.modulus, den))

        def execute_symbolic_measurements(self, initial: Mapping[str, int]):
            """Prove all transcripts at once when quantum data is branch independent.

        Measurement-dependent phases are exact multilinear polynomials over
        integer coefficients modulo the phase period.  A monomial is indexed
        by a bit mask of measurement variables.  Multiplication uses Boolean
        idempotence m*m=m.  Vanishing of every coefficient is equivalent to
        vanishing on the complete Boolean cube, by the invertible Mobius
        transform.  This route needs no assumptions about how often any
        outcome occurs.  Measurement-conditioned data gates are rejected;
        `execute` plus exhaustive transcript enumeration handles those cases.
        """
            modulus, den = (self.modulus, self.denominator)

            def plus(left, right):
                result = dict(left)
                for monomial, coefficient in right.items():
                    total = (result.get(monomial, 0) + coefficient) % modulus
                    if total:
                        result[monomial] = total
                    else:
                        result.pop(monomial, None)
                return result

            def multiply(left, right):
                result = {}
                for a, ca in left.items():
                    for b, cb in right.items():
                        monomial = a | b
                        result[monomial] = (result.get(monomial, 0) + ca * cb) % modulus
                return {key: value for key, value in result.items() if value}

            def times(poly, factor):
                return {key: value * factor % modulus for key, value in poly.items() if value * factor % modulus}
            state = {wire: 0 for wire in self.wires}
            state.update(initial)
            state.update({'0': 0, '1': 1, 'False': 0, 'True': 1})
            classical = {wire: {0: int(value)} if value else {} for wire, value in state.items() if wire.startswith('b')}
            phase = {}
            stack = [{0: 1}]
            for index, op in enumerate(self.operations):
                kind, args = (op.kind, op.arguments)
                condition = stack[-1]
                if op.condition is not None:
                    condition = multiply(condition, classical[op.condition])
                if kind == 'PUSH_CONDITION':
                    stack.append(condition)
                    continue
                if kind == 'POP_CONDITION':
                    if len(stack) == 1:
                        raise AssertionError('Unmatched POP_CONDITION')
                    stack.pop()
                    continue
                if not condition:
                    continue
                if kind in ('Z', 'CZ', 'CCZ', 'Z_POW', 'NEG'):
                    coefficient = self.phase_steps[index] if kind == 'Z_POW' else den
                    coefficient *= _branch_prover_math.prod((state[wire] for wire in args))
                    phase = plus(phase, times(condition, coefficient))
                    continue
                if kind in ('BIT_STORE0', 'BIT_STORE1'):
                    previous = classical.get(args[0], {})
                    classical[args[0]] = plus(previous, times(multiply(condition, previous), -1))
                    if kind == 'BIT_STORE1':
                        classical[args[0]] = plus(classical[args[0]], condition)
                    continue
                if kind == 'BIT_INVERT':
                    previous = classical.get(args[0], {})
                    classical[args[0]] = plus(plus(previous, condition), times(multiply(previous, condition), -2))
                    continue
                if condition != {0: 1}:
                    raise ValueError(f'Quantum data depends on a measurement at operation {index}; use explicit exhaustive transcript enumeration')
                if kind == 'X':
                    state[args[0]] ^= 1
                elif kind == 'CX':
                    state[args[1]] ^= state[args[0]]
                elif kind == 'CCX':
                    state[args[2]] ^= state[args[0]] & state[args[1]]
                elif kind == 'SWAP':
                    state[args[0]], state[args[1]] = (state[args[1]], state[args[0]])
                elif kind == 'CSWAP':
                    if state[args[0]]:
                        state[args[1]], state[args[2]] = (state[args[2]], state[args[1]])
                elif kind == 'R':
                    if state[args[0]]:
                        raise AssertionError(f'Reset of dirty {args[0]} at operation {index}')
                elif kind == 'HMR':
                    outcome = {1 << op.event: 1}
                    phase = plus(phase, times(outcome, den * state[args[0]]))
                    state[args[0]] = 0
                    classical[args[1]] = outcome
                else:
                    raise AssertionError(kind)
            if len(stack) != 1:
                raise AssertionError('Unclosed condition stack')
            return (state, {monomial: _branch_prover_Fraction(coefficient, den) for monomial, coefficient in phase.items()})

def _initialize_codebook():
    global _codebook_BinarySpan, _codebook_Codebook, _codebook_INTEGRATED_ROOT, _codebook_QuadraticCodePlan, _codebook__IntegratedPath, _codebook___file__, _codebook___name__, _codebook_annotations, _codebook_bits, _codebook_dataclass, _codebook_emit_erase, _codebook_emit_phase, _codebook_emit_xor, _codebook_factor_polynomial, _codebook_pack_bits, _codebook_parity_function, _codebook_random, _codebook_word_functions
    _codebook_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py', False).dataclass
    _codebook_random = _import_component('random', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py', True)

    def _codebook_bits(value):
        while value:
            bit = value & -value
            yield (bit.bit_length() - 1)
            value ^= bit

    class _codebook_BinarySpan:

        def __init__(self, columns=()):
            self.pivots = {}
            self.columns = []
            self.nullspace = []
            for column in columns:
                self.add(column)

        def add(self, column):
            column = int(column)
            index = len(self.columns)
            self.columns.append(column)
            reduced, expression = (column, 1 << index)
            while reduced:
                pivot = reduced.bit_length() - 1
                if pivot not in self.pivots:
                    self.pivots[pivot] = (reduced, expression)
                    return True
                old, mask = self.pivots[pivot]
                reduced ^= old
                expression ^= mask
            self.nullspace.append(expression)
            return False

        def solve(self, target):
            reduced, expression = (int(target), 0)
            while reduced:
                pivot = reduced.bit_length() - 1
                if pivot not in self.pivots:
                    return None
                old, mask = self.pivots[pivot]
                reduced ^= old
                expression ^= mask
            return expression

    def _codebook_pack_bits(values):
        return sum(((int(value) & 1) << i for i, value in enumerate(values)))

    def _codebook_word_functions(values, width):
        values = list(values)
        return [_codebook_pack_bits((value >> bit for value in values)) for bit in range(width)]

    def _codebook_parity_function(mask, functions):
        out = 0
        for bit in _codebook_bits(mask):
            out ^= functions[bit]
        return out

    @_codebook_dataclass(frozen=True)
    class _codebook_QuadraticCodePlan:
        width: int
        constant: bool
        linear: int
        edges: tuple[tuple[int, int], ...]
        products: tuple[tuple[int, int, int, int], ...]
        product_linear: int

        @property
        def and_count(self):
            return len(self.products)

        def evaluate_bits(self, value):
            out = int(self.constant) ^ (value & self.linear).bit_count() & 1
            for i, j in self.edges:
                out ^= value >> i & 1 & (value >> j & 1)
            return out

        def evaluate_functions(self, functions, full):
            out = full if self.constant else 0
            out ^= _codebook_parity_function(self.linear, functions)
            for i, j in self.edges:
                out ^= functions[i] & functions[j]
            return out

        def evaluate_factored_functions(self, functions, full):
            out = full if self.constant else 0
            out ^= _codebook_parity_function(self.product_linear, functions)
            for left, right, i, j in self.products:
                if not (left >> i & 1 and right >> j & 1) or left >> j & 1 or right >> i & 1:
                    raise AssertionError('Product factors do not admit the declared CNOT frames.')
                out ^= _codebook_parity_function(left, functions) & _codebook_parity_function(right, functions)
            return out

    def _codebook_factor_polynomial(width, constant, linear, edges):
        original_edges = tuple(sorted(edges))
        edges = set(original_edges)
        affine = int(linear)
        products = []
        while edges:
            i, j = min(edges)
            left, right = (1 << i, 1 << j)
            for k in range(width):
                if k != i and k != j:
                    if tuple(sorted((j, k))) in edges:
                        left |= 1 << k
                    if tuple(sorted((i, k))) in edges:
                        right |= 1 << k
            for a in _codebook_bits(left):
                for b in _codebook_bits(right):
                    if a == b:
                        affine ^= 1 << a
                    else:
                        edge = tuple(sorted((a, b)))
                        if edge in edges:
                            edges.remove(edge)
                        else:
                            edges.add(edge)
            products.append((left, right, i, j))
        return _codebook_QuadraticCodePlan(width, bool(constant), int(linear), original_edges, tuple(products), affine)

    class _codebook_Codebook:

        def __init__(self, functions, size=256):
            self.functions = tuple(map(int, functions))
            self.width = len(self.functions)
            self.size = int(size)
            self.full = (1 << self.size) - 1
            if any((function & ~self.full for function in self.functions)):
                raise ValueError('Function extends beyond the codebook domain.')
            self.monomials = [()] + [(i,) for i in range(self.width)]
            self.monomials += [(i, j) for i in range(self.width) for j in range(i + 1, self.width)]
            self.columns = [self.full] + list(self.functions)
            self.columns += [self.functions[i] & self.functions[j] for i in range(self.width) for j in range(i + 1, self.width)]
            self.span = _codebook_BinarySpan(self.columns)

        def decode_expression(self, expression):
            constant, linear, edges = (False, 0, [])
            for index in _codebook_bits(expression):
                monomial = self.monomials[index]
                if not monomial:
                    constant = not constant
                elif len(monomial) == 1:
                    linear ^= 1 << monomial[0]
                else:
                    edges.append(monomial)
            return _codebook_factor_polynomial(self.width, constant, linear, edges)

        def represent(self, target, *, trials=0, seed=0, initial_plan=None):
            """Find a certified quadratic representation, optionally lower its rank.

        The deterministic search samples factorizations with fewer left factors.
        It is a heuristic over reachable codewords, not a claim of global
        multiplicative optimality. Every accepted result is checked exactly.
        """
            target = int(target)
            expression = self.span.solve(target)
            if expression is None:
                return None
            plan = self.decode_expression(expression)
            if initial_plan is not None:
                if initial_plan.width != self.width or initial_plan.evaluate_factored_functions(self.functions, self.full) != target:
                    raise ValueError('The supplied initial representation is not certified on this codebook.')
                if initial_plan.and_count < plan.and_count:
                    plan = initial_plan
            rng = _codebook_random.Random(seed)
            for _ in range(trials):
                count = plan.and_count - 1
                if count <= 0:
                    break
                if rng.randrange(3):
                    factors = [item[rng.randrange(2)] for item in plan.products]
                    rng.shuffle(factors)
                    factors = factors[:count]
                    if rng.randrange(2):
                        factors[rng.randrange(count)] = rng.getrandbits(self.width)
                else:
                    factors = [rng.getrandbits(self.width) for _ in range(count)]
                columns = [self.full] + list(self.functions)
                left_functions = [_codebook_parity_function(mask, self.functions) for mask in factors]
                columns += [left & right for left in left_functions for right in self.functions]
                solution = _codebook_BinarySpan(columns).solve(target)
                if solution is None:
                    continue
                constant = bool(solution & 1)
                linear = solution >> 1 & (1 << self.width) - 1
                edge_set = set()
                for i, left in enumerate(factors):
                    right = solution >> 1 + self.width + i * self.width & (1 << self.width) - 1
                    for a in _codebook_bits(left):
                        for b in _codebook_bits(right):
                            if a == b:
                                linear ^= 1 << a
                            else:
                                edge = tuple(sorted((a, b)))
                                if edge in edge_set:
                                    edge_set.remove(edge)
                                else:
                                    edge_set.add(edge)
                candidate = _codebook_factor_polynomial(self.width, constant, linear, edge_set)
                if candidate.and_count < plan.and_count:
                    plan = candidate
            if plan.evaluate_functions(self.functions, self.full) != target or plan.evaluate_factored_functions(self.functions, self.full) != target:
                raise AssertionError('Codebook synthesis certificate failed.')
            return plan

        def represent_kernel(self, target, *, trials=10000, seed=0, exhaustive=False):
            """Search the exact affine space of quadratic representations.

        Every nullspace vector is a polynomial vanishing on ALL codewords.
        Toggling it preserves the truth table. Alternating matrix rank divided
        by two equals the number of affine products for that representation.
        An exhaustive search is supported for small nullspaces; otherwise the
        result is explicitly a deterministic heuristic, with no optimality
        claim about representations not visited.
        """
            expression = self.span.solve(int(target))
            if expression is None:
                return (None, {'status': 'not_quadratic_on_codebook'})
            relations = list(self.span.nullspace)
            rng = _codebook_random.Random(seed)
            rng.shuffle(relations)
            width = self.width

            def adjacency(value):
                rows = [0] * width
                for index in _codebook_bits(value):
                    edge = self.monomials[index]
                    if len(edge) == 2:
                        i, j = edge
                        rows[i] ^= 1 << j
                        rows[j] ^= 1 << i
                return rows

            def rank_below(matrix, limit):
                rows = list(matrix)
                remaining = (1 << width) - 1
                products = 0
                while remaining:
                    i = (remaining & -remaining).bit_length() - 1
                    remaining ^= 1 << i
                    partners = rows[i] & remaining
                    if not partners:
                        continue
                    j = (partners & -partners).bit_length() - 1
                    remaining ^= 1 << j
                    products += 1
                    if products >= limit:
                        return products
                    ri, rj = (rows[i], rows[j])
                    for k in _codebook_bits(remaining):
                        old = rows[k]
                        if old >> j & 1:
                            rows[k] ^= ri
                        if old >> i & 1:
                            rows[k] ^= rj
                return products
            initial = self.decode_expression(expression)
            best, best_expression = (initial.and_count, expression)
            current = expression
            rows = adjacency(current)
            relation_rows = [adjacency(relation) for relation in relations]
            total = 1 << len(relations) if exhaustive else min(trials, 1 << len(relations))
            examined = 1
            for step in range(1, total):
                if exhaustive:
                    changed = (step & -step).bit_length() - 1
                else:
                    changed = rng.randrange(len(relations))
                current ^= relations[changed]
                delta = relation_rows[changed]
                rows = [row ^ change for row, change in zip(rows, delta)]
                score = rank_below(rows, best)
                examined += 1
                if score < best:
                    best, best_expression = (score, current)
                    if best == 0:
                        break
            plan = self.decode_expression(best_expression)
            if plan.and_count != best or plan.evaluate_functions(self.functions, self.full) != int(target) or plan.evaluate_factored_functions(self.functions, self.full) != int(target):
                raise AssertionError('Nullspace rank-search certificate failed.')
            return (plan, {'status': 'PROVED' if exhaustive else 'certified_heuristic', 'representations_examined': examined, 'nullspace_dimension': len(relations), 'initial_products': initial.and_count, 'products': plan.and_count, 'optimal_among_quadratic_representations': bool(exhaustive)})

        def improve_preserving_kernel(self, plan, *, rounds=64, subspace_bits=9, seed=0):
            """Reduce a certified polynomial rank inside relation subspaces.

        Randomly retain part of the current alternating matrix's kernel. The
        nullspace of those linear constraints gives truth-table relations that
        preserve it. Exhausting a small deterministic subspace of those moves
        can find lower rank without randomizing away the current structure.
        This remains a heuristic, and every returned factorization is checked.
        """
            if plan.width != self.width:
                raise ValueError('Wrong polynomial width.')
            if not self.span.nullspace or plan.and_count == 0:
                return plan
            target = plan.evaluate_functions(self.functions, self.full)
            lookup = {monomial: i for i, monomial in enumerate(self.monomials)}
            current = int(plan.constant)
            for bit in _codebook_bits(plan.linear):
                current ^= 1 << lookup[bit,]
            for edge in plan.edges:
                current ^= 1 << lookup[edge]
            width = self.width
            rng = _codebook_random.Random(seed)

            def adjacency(expression):
                rows = [0] * width
                for index in _codebook_bits(expression):
                    monomial = self.monomials[index]
                    if len(monomial) == 2:
                        a, b = monomial
                        rows[a] ^= 1 << b
                        rows[b] ^= 1 << a
                return rows

            def products_below(matrix, limit):
                rows = list(matrix)
                remaining, count = ((1 << width) - 1, 0)
                while remaining:
                    i = (remaining & -remaining).bit_length() - 1
                    remaining ^= 1 << i
                    partners = rows[i] & remaining
                    if not partners:
                        continue
                    j = (partners & -partners).bit_length() - 1
                    remaining ^= 1 << j
                    count += 1
                    if count >= limit:
                        return count
                    ri, rj = (rows[i], rows[j])
                    for k in _codebook_bits(remaining):
                        old = rows[k]
                        if old >> j & 1:
                            rows[k] ^= ri
                        if old >> i & 1:
                            rows[k] ^= rj
                return count
            relations = list(self.span.nullspace)
            relation_matrices = [adjacency(relation) for relation in relations]
            best_count = plan.and_count
            for _ in range(rounds):
                matrix = adjacency(current)
                kernel = _codebook_BinarySpan(matrix).nullspace
                if not kernel:
                    break
                k = min(len(kernel), max(1, width // 2))
                mixed = list(kernel)
                for __ in range(3 * len(mixed)):
                    if len(mixed) < 2:
                        break
                    a, b = rng.sample(range(len(mixed)), 2)
                    mixed[a] ^= mixed[b]
                rng.shuffle(mixed)
                columns = []
                for relation_matrix in relation_matrices:
                    column = 0
                    for i, vector in enumerate(mixed[:k]):
                        product = sum((((row & vector).bit_count() & 1) << bit for bit, row in enumerate(relation_matrix)))
                        column |= product << width * i
                    columns.append(column)
                moves = []
                while k >= 1:
                    mask = (1 << width * k) - 1
                    moves = _codebook_BinarySpan([column & mask for column in columns]).nullspace
                    if len(moves) >= 3:
                        break
                    k -= 1
                if not moves:
                    continue
                if len(moves) > subspace_bits:
                    compressed, span = ([], _codebook_BinarySpan())
                    while len(compressed) < subspace_bits:
                        coefficients = rng.getrandbits(len(moves))
                        if not coefficients or not span.add(coefficients):
                            continue
                        value = 0
                        for bit in _codebook_bits(coefficients):
                            value ^= moves[bit]
                        compressed.append(value)
                    moves = compressed
                deltas = []
                delta_rows = []
                for move in moves:
                    expression = 0
                    for bit in _codebook_bits(move):
                        expression ^= relations[bit]
                    deltas.append(expression)
                    delta_rows.append(adjacency(expression))
                trial_expression, trial_rows = (current, list(matrix))
                round_best, round_expression = (best_count, current)
                for step in range(1, 1 << len(moves)):
                    changed = (step & -step).bit_length() - 1
                    trial_expression ^= deltas[changed]
                    trial_rows = [row ^ delta for row, delta in zip(trial_rows, delta_rows[changed])]
                    count = products_below(trial_rows, round_best)
                    if count < round_best:
                        round_best, round_expression = (count, trial_expression)
                if round_best < best_count:
                    best_count, current = (round_best, round_expression)
                    if best_count == 0:
                        break
            result = self.decode_expression(current)
            if result.and_count != best_count or result.evaluate_functions(self.functions, self.full) != target or result.evaluate_factored_functions(self.functions, self.full) != target:
                raise AssertionError('Kernel-preserving rank-search certificate failed.')
            return result

    def _codebook_emit_xor(builder, variables, target, plan):
        """Emit a factored decoder with zero additional qubits."""
        variables = list(variables)
        if len(variables) != plan.width or target in variables:
            raise ValueError('Distinct input and target wires are required.')
        if plan.constant:
            builder.x(target)
        for bit in _codebook_bits(plan.product_linear):
            builder.cx(variables[bit], target)
        for left, right, i, j in plan.products:
            frame = [(variables[k], variables[i]) for k in _codebook_bits(left) if k != i]
            frame += [(variables[k], variables[j]) for k in _codebook_bits(right) if k != j]
            for a, b in frame:
                builder.cx(a, b)
            builder.ccx(variables[i], variables[j], target)
            for a, b in reversed(frame):
                builder.cx(a, b)

    def _codebook_emit_phase(builder, variables, outcome, plan):
        """Repay (-1)^(outcome * polynomial) using Clifford gates only."""
        variables = list(variables)
        if len(variables) != plan.width:
            raise ValueError('Wrong codebook wire count.')
        if plan.constant:
            builder.z(outcome)
        builder.push_condition(outcome)
        for bit in _codebook_bits(plan.linear):
            builder.z(variables[bit])
        for i, j in plan.edges:
            builder.cz(variables[i], variables[j])
        builder.pop_condition()

    def _codebook_emit_erase(builder, variables, targets, plans):
        """Erase known codebook functions, exactly for all measurement outcomes.

    The retained variables must have the certified codebook values throughout.
    Targets are reset to zero but remain allocated for caller reuse.
    """
        variables, targets, plans = (list(variables), list(targets), list(plans))
        if len(targets) != len(plans) or set(variables) & set(targets):
            raise ValueError('Erasure requires disjoint retained and target wires.')
        outcomes = builder.alloc_bits(len(targets))
        for target, outcome, plan in zip(targets, outcomes, plans):
            builder.hmr(target, outcome)
            _codebook_emit_phase(builder, variables, outcome, plan)
        builder.free(outcomes)

def _initialize_cyclic_phase():
    global _cyclic_phase_Fraction, _cyclic_phase_INTEGRATED_ROOT, _cyclic_phase_ThresholdPlan, _cyclic_phase__IntegratedPath, _cyclic_phase___file__, _cyclic_phase___name__, _cyclic_phase__erase_polynomial, _cyclic_phase__helper_candidates, _cyclic_phase__monomials, _cyclic_phase__pow2, _cyclic_phase__restricted_anf, _cyclic_phase__span_solution, _cyclic_phase__truth_of_terms, _cyclic_phase_annotations, _cyclic_phase_compile_polynomial, _cyclic_phase_contextmanager, _cyclic_phase_cyclic_scale_phase, _cyclic_phase_dataclass, _cyclic_phase_itertools, _cyclic_phase_km, _cyclic_phase_lru_cache, _cyclic_phase_math, _cyclic_phase_rotation_pairs, _cyclic_phase_threshold_control, _cyclic_phase_threshold_plan, _cyclic_phase_xor_polynomial
    _cyclic_phase_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', False).dataclass

    @_cyclic_phase_dataclass(frozen=True)
    class _cyclic_phase_ThresholdPlan:
        threshold: int
        max_k: int
        truth: int
        phase_terms: tuple[int, ...]
        helper_terms: tuple[int, ...] | None
        output_terms: tuple[int, ...]
        products: int

    def _cyclic_phase__erase_polynomial(builder, target, variables, terms):
        """Measure a degree<=3 function and repay its entire sign, constants too."""
        outcome = builder.alloc_bits(1)[0]
        builder.hmr(target, outcome)
        builder.free(target)
        if 0 in terms:
            builder.z(outcome)
        builder.push_condition(outcome)
        for term in terms:
            bits = [variables[i] for i in range(len(variables)) if term >> i & 1]
            if len(bits) == 1:
                builder.z(bits[0])
            elif len(bits) == 2:
                builder.cz(*bits)
            elif len(bits) == 3:
                builder.ccz(*bits)
            elif len(bits) > 3:
                raise ValueError('This cleanup accepts degree at most three.')
        builder.pop_condition()
        builder.free(outcome)

def _initialize_dirty_terminal():
    global _dirty_terminal_INTEGRATED_ROOT, _dirty_terminal__IntegratedPath, _dirty_terminal___file__, _dirty_terminal___name__, _dirty_terminal__phase, _dirty_terminal_annotations, _dirty_terminal_dirty_mcx, _dirty_terminal_dirty_mcx_cost, _dirty_terminal_dirty_mcz, _dirty_terminal_dirty_mcz_cost, _dirty_terminal_increment_cost, _dirty_terminal_km, _dirty_terminal_terminal_add, _dirty_terminal_terminal_cost, _dirty_terminal_terminal_dirty_count
    _dirty_terminal_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/dirty_terminal.py', False)

    def _dirty_terminal_dirty_mcx_cost(controls):
        if controls < 2:
            return 0
        return 1 if controls == 2 else 4 * controls - 8

    def _dirty_terminal_increment_cost(width):
        return sum((_dirty_terminal_dirty_mcx_cost(position + 1) for position in range(width)))

    def _dirty_terminal_terminal_cost(width, source_width):
        prefix = min(source_width, max(0, width - 1))
        return 2 * prefix + (0 if source_width == width else _dirty_terminal_increment_cost(width - prefix))

    def _dirty_terminal_terminal_dirty_count(width, source_width):
        return max(0, width - source_width - 2)

    def _dirty_terminal_dirty_mcz_cost(controls):
        if controls < 3:
            return 0
        return 1 if controls == 3 else 4 * controls - 12

    def _dirty_terminal_dirty_mcz(builder, controls, dirty=()):
        """Phase the product of controls, restoring every borrowed dirty bit.

    Replacing the final target toggle of each dirty-MCX ladder with CCZ
    gives two diagonal phases whose dirty contributions cancel.  Their
    remaining phase is exactly the AND of all controls, including on every
    arbitrary dirty-wire input.  No clean quantum wire is allocated.
    """
        controls, dirty = (list(controls), list(dirty))
        if not controls or not all((isinstance(w, _dirty_terminal_km.q) for w in controls + dirty)):
            raise ValueError('Dirty MCZ requires nonempty quantum controls.')
        needed = max(0, len(controls) - 3)
        dirty = dirty[:needed]
        if len(dirty) != needed:
            raise ValueError(f'{len(controls)} phase controls require {needed} dirty wires.')
        if len(set(controls + dirty)) != len(controls) + len(dirty):
            raise ValueError('Phase controls and borrowed wires must be disjoint.')
        if len(controls) == 1:
            builder.z(controls[0])
            return
        if len(controls) == 2:
            builder.cz(*controls)
            return
        if len(controls) == 3:
            builder.ccz(*controls)
            return

        def ladder(include_first):
            if include_first:
                builder.ccx(controls[0], controls[1], dirty[0])
            for index in range(1, len(dirty)):
                builder.ccx(dirty[index - 1], controls[index + 1], dirty[index])
            builder.ccz(dirty[-1], controls[-2], controls[-1])
            for index in reversed(range(1, len(dirty))):
                builder.ccx(dirty[index - 1], controls[index + 1], dirty[index])
            if include_first:
                builder.ccx(controls[0], controls[1], dirty[0])
        ladder(True)
        ladder(False)

    def _dirty_terminal_dirty_mcx(builder, controls, target, dirty=()):
        """Toggle target by the AND of controls; restore every arbitrary dirty bit.

    For n >= 3, n-2 borrowed wires and 4n-8 Toffolis suffice.  A complete
    AND ladder and a ladder omitting its first product have identical dirty
    contributions; their target toggles differ by precisely the full AND.
    Each ladder is reversed after its target operation.
    """
        controls, dirty = (list(controls), list(dirty))
        if not all((isinstance(wire, _dirty_terminal_km.q) for wire in controls + [target] + dirty)):
            raise ValueError('Dirty MCX operands must be quantum wires.')
        need = max(0, len(controls) - 2)
        dirty = dirty[:need]
        if len(dirty) != need:
            raise ValueError(f'{len(controls)} controls require {need} dirty wires.')
        if len(set(controls + [target] + dirty)) != len(controls) + 1 + len(dirty):
            raise ValueError('Dirty MCX controls, target, and borrowed wires must be disjoint.')
        if not controls:
            builder.x(target)
            return
        if len(controls) == 1:
            builder.cx(controls[0], target)
            return
        if len(controls) == 2:
            builder.ccx(controls[0], controls[1], target)
            return

        def ladder(include_first):
            if include_first:
                builder.ccx(controls[0], controls[1], dirty[0])
            for index in range(1, len(dirty)):
                builder.ccx(dirty[index - 1], controls[index + 1], dirty[index])
            builder.ccx(dirty[-1], controls[-1], target)
            for index in reversed(range(1, len(dirty))):
                builder.ccx(dirty[index - 1], controls[index + 1], dirty[index])
            if include_first:
                builder.ccx(controls[0], controls[1], dirty[0])
        ladder(True)
        ladder(False)

    def _dirty_terminal__phase(builder, measurement, wire):
        if measurement is not None:
            builder.push_condition(measurement)
            builder.z(wire)
            builder.pop_condition()

    def _dirty_terminal_terminal_add(builder, source, target, incoming, *, dirty=(), debt=None, start=0, overflow_phase=None):
        """Add an unsigned source prefix and a quantum incoming carry in place.

    `source` contains distinct quantum low bits followed by literal False
    padding, matching `target` in length.  `debt`, if supplied, owns a dict
    `measurements` keyed by the full adder's carry positions.  Repaid entries
    are popped and their classical bits freed.  All data and borrowed wires
    are restored except the modular target sum.
    """
        source, target, dirty = (list(source), list(target), list(dirty))
        width = len(target)
        if len(source) != width or not width:
            raise ValueError('The nonempty source and target widths must match.')
        if not isinstance(incoming, _dirty_terminal_km.q):
            raise ValueError('The sparse terminal requires a quantum incoming carry.')
        count = next((i for i, wire in enumerate(source) if wire is False), width)
        if any((wire is not False for wire in source[count:])):
            raise ValueError('Only an unsigned source prefix with high zero padding is supported.')
        if overflow_phase is not None and count == width:
            raise ValueError('Overflow-phase terminals require a nonempty high zero-source suffix.')
        real_source = source[:count]
        if not all((isinstance(wire, _dirty_terminal_km.q) for wire in real_source + target + dirty)):
            raise ValueError('All nonconstant operands must be quantum wires.')
        operands = real_source + target + [incoming]
        if len(set(operands)) != len(operands):
            raise ValueError('Source, target, and incoming carry must be disjoint.')
        required = _dirty_terminal_terminal_dirty_count(width, count)
        dirty = [wire for wire in dict.fromkeys(dirty) if wire not in operands]
        if len(dirty) < required:
            raise ValueError(f'The terminal requires {required} restored dirty wires.')

        def take(position):
            return None if debt is None else debt.measurements.pop(start + position, None)

        def repay(position, wire):
            measurement = take(position)
            _dirty_terminal__phase(builder, measurement, wire)
            if measurement is not None:
                builder.free(measurement)
        prefix = min(count, width - 1)
        frames = []
        carry = incoming
        for index in range(prefix):
            a, b = (source[index], target[index])
            builder.cx(a, b)
            builder.cx(a, carry)
            builder.ccx(b, carry, a)
            repay(index + 1, a)
            frames.append((a, b, carry))
            carry = a
        if count == width:
            builder.cx(source[-1], target[-1])
            builder.cx(carry, target[-1])
        else:
            high = target[prefix:]
            if overflow_phase is not None:
                builder.push_condition(overflow_phase)
                _dirty_terminal_dirty_mcz(builder, [carry] + high, dirty)
                builder.pop_condition()
            for position in reversed(range(len(high))):
                measurement = take(prefix + position) if position else None
                _dirty_terminal__phase(builder, measurement, high[position])
                _dirty_terminal_dirty_mcx(builder, [carry] + high[:position], high[position], dirty)
                _dirty_terminal__phase(builder, measurement, high[position])
                if measurement is not None:
                    builder.free(measurement)
        for a, b, carry in reversed(frames):
            builder.ccx(b, carry, a)
            builder.cx(a, carry)
            builder.cx(carry, b)
        phase_cost = _dirty_terminal_dirty_mcz_cost(width - prefix + 1) if overflow_phase is not None else 0
        return dict(toffolis=_dirty_terminal_terminal_cost(width, count) + phase_cost, clean_workspace=0, dirty_workspace=required, source_prefix=count)

def _initialize___init__():
    global ___init___INTEGRATED_ROOT, ___init____IntegratedPath, ___init_____file__, ___init_____name__

def _initialize_arithmetic():
    global _arithmetic_INTEGRATED_ROOT, _arithmetic_MAJORITY_TRUTH, _arithmetic_Sequence, _arithmetic__Frame, _arithmetic__IntegratedPath, _arithmetic___file__, _arithmetic___name__, _arithmetic__as_array, _arithmetic__compute_carry, _arithmetic__erase_carry, _arithmetic__phase_borrow, _arithmetic__phase_carry, _arithmetic__segment, _arithmetic__sum_keep_carry, _arithmetic_add, _arithmetic_annotations, _arithmetic_dataclass, _arithmetic_horner_rows, _arithmetic_km, _arithmetic_partition, _arithmetic_phase_quadratic, _arithmetic_signed_row
    _arithmetic_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).dataclass
    _arithmetic_Sequence = _import_component('typing', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).Sequence
    _arithmetic_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False)
    _arithmetic_phase_quadratic = _import_component('compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).phase_quadratic
    _arithmetic_MAJORITY_TRUTH = _import_component('compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).MAJORITY_TRUTH

    @_arithmetic_dataclass
    class _arithmetic__Frame:
        a: object
        b: object
        incoming: object
        outgoing: object
        preserve_sign: bool = False

    def _arithmetic__as_array(wires):
        return _arithmetic_km.array(list(wires))

    def _arithmetic__compute_carry(builder, a, b, incoming, *, preserve=None):
        if a is False and incoming is False:
            return _arithmetic__Frame(a, b, incoming, False)
        outgoing = builder.alloc_qubits(1)[0]
        if a is False:
            builder.ccx(incoming, b, outgoing)
        elif a == preserve and isinstance(incoming, _arithmetic_km.q):
            builder.cx(a, incoming)
            builder.cx(a, b)
            builder.ccx(incoming, b, outgoing)
            builder.cx(a, outgoing)
            return _arithmetic__Frame(a, b, incoming, outgoing, True)
        else:
            builder.cx(incoming, a)
            builder.cx(incoming, b)
            builder.ccx(a, b, outgoing)
            builder.cx(incoming, outgoing)
        return _arithmetic__Frame(a, b, incoming, outgoing)

    def _arithmetic__erase_carry(builder, frame, *, write_sum):
        a, b, incoming, outgoing = (frame.a, frame.b, frame.incoming, frame.outgoing)
        if outgoing is False:
            return
        if frame.preserve_sign:
            builder.cx(a, outgoing)
            builder.del_and(incoming, b, outgoing)
            builder.cx(a, incoming)
            builder.cx(incoming if write_sum else a, b)
        elif a is False:
            builder.del_and(incoming, b, outgoing)
            if write_sum:
                builder.cx(incoming, b)
        else:
            builder.cx(incoming, outgoing)
            builder.del_and(a, b, outgoing)
            builder.cx(incoming, a)
            if write_sum:
                builder.cx(a, b)
            else:
                builder.cx(incoming, b)
        builder.free(outgoing)

    def _arithmetic__sum_keep_carry(builder, frame):
        if frame.preserve_sign:
            builder.cx(frame.a, frame.incoming)
            builder.cx(frame.incoming, frame.b)
        elif frame.a is False:
            builder.cx(frame.incoming, frame.b)
        else:
            builder.cx(frame.incoming, frame.a)
            builder.cx(frame.a, frame.b)

    def _arithmetic__segment(builder, a, b, incoming, *, retain_outgoing, preserve=None):
        n = len(b)
        if retain_outgoing:
            frames = []
            carry = incoming
            for aa, bb in zip(a, b):
                frame = _arithmetic__compute_carry(builder, aa, bb, carry, preserve=preserve)
                frames.append(frame)
                carry = frame.outgoing
            _arithmetic__sum_keep_carry(builder, frames[-1])
            for frame in reversed(frames[:-1]):
                _arithmetic__erase_carry(builder, frame, write_sum=True)
            return carry
        if n == 1:
            builder.cx(a[0], b[0])
            builder.cx(incoming, b[0])
            return False
        frames = []
        carry = incoming
        for aa, bb in zip(a[:-2], b[:-2]):
            frame = _arithmetic__compute_carry(builder, aa, bb, carry, preserve=preserve)
            frames.append(frame)
            carry = frame.outgoing
        aa, bb = (a[-2], b[-2])
        if aa == preserve and isinstance(carry, _arithmetic_km.q):
            builder.cx(aa, carry)
            builder.cx(aa, bb)
            builder.cx(aa, b[-1])
            builder.ccx(carry, bb, b[-1])
            builder.cx(aa, carry)
            builder.cx(carry, bb)
        elif aa is False:
            builder.ccx(carry, bb, b[-1])
            builder.cx(carry, bb)
        else:
            builder.cx(carry, aa)
            builder.cx(carry, bb)
            builder.cx(carry, b[-1])
            builder.ccx(aa, bb, b[-1])
            builder.cx(carry, aa)
            builder.cx(aa, bb)
        builder.cx(a[-1], b[-1])
        for frame in reversed(frames):
            _arithmetic__erase_carry(builder, frame, write_sum=True)
        return False

    def _arithmetic__phase_carry(builder, a, b, incoming, *, preserve=None):
        """Apply (-1)**carry_out(a+b+incoming), restoring all operands."""
        frames = []
        carry = incoming
        for aa, bb in zip(a[:-1], b[:-1]):
            frame = _arithmetic__compute_carry(builder, aa, bb, carry, preserve=preserve)
            frames.append(frame)
            carry = frame.outgoing
        _arithmetic_phase_quadratic(builder, [a[-1], b[-1], carry], _arithmetic_MAJORITY_TRUTH)
        for frame in reversed(frames):
            _arithmetic__erase_carry(builder, frame, write_sum=False)

    def _arithmetic__phase_borrow(builder, a, final_sum, incoming, *, preserve=None):
        builder.x(_arithmetic__as_array(final_sum))
        _arithmetic__phase_carry(builder, a, final_sum, incoming, preserve=preserve)
        builder.x(_arithmetic__as_array(final_sum))

    def _arithmetic_partition(width: int, clean: int) -> list[int]:
        """Choose deterministic segment sizes without exceeding ``clean`` wires.

    Earlier segments keep one carry each.  A nonfinal segment of length l
    needs l fresh carries; the final segment needs only max(0,l-2), because
    the last carry goes directly into the target's most significant bit.
    """
        if width <= 0:
            return []
        if clean < 0:
            raise ValueError('clean must be nonnegative.')
        if width <= clean + 2:
            return [width]
        for boundaries in range(1, clean + 1):
            final = clean - boundaries + 2
            capacity = sum((clean - j for j in range(boundaries))) + final
            if capacity < width:
                continue
            remaining = width - final
            sizes = []
            for j in range(boundaries):
                length = min(clean - j, remaining - (boundaries - j - 1))
                if length <= 0:
                    break
                sizes.append(length)
                remaining -= length
            if len(sizes) == boundaries and remaining == 0:
                return sizes + [final]
        raise ValueError(f'{width}-bit segmented adder needs more than {clean} clean carry wires.')

    def _arithmetic_add(builder: _arithmetic_km.CircuitBuilder, source: _arithmetic_Sequence, target: _arithmetic_Sequence, *, carry_in=False, subtract: bool=False, signed_source: bool=False, carry_budget: int | None=None) -> None:
        """target += (+/-)(source+carry_in), with zero extension and clean erasure.

    All source wires, including carry_in, are preserved.  Source bits may be
    shorter than target; omitted high bits are zero, with no physical padding.
    With signed_source=True, high source positions reuse the actual sign
    wire.  An alternate majority frame preserves that shared wire throughout.
    carry_in can be a quantum bit or False.  Subtraction subtracts both terms.

    With n ordinary source bits and k carry wires, the expected Toffoli count
    is n-1 + max(0,n-2-k)/2 whenever ``partition(n,k)`` exists.  Literal zero
    bits and compile-time carry values can make actual cost lower.  All
    measurement outcomes have identical data outputs and identical phase.
    """
        source, target = (list(source), list(target))
        n = len(target)
        if not n:
            return
        source = source[:n]
        if any((not isinstance(q, _arithmetic_km.q) for q in source)):
            raise ValueError('Source must contain quantum wires; high zeros are implicit.')
        if len(set(source + target)) != len(source) + len(target):
            raise ValueError('Source and target must be disjoint distinct wires.')
        if isinstance(carry_in, _arithmetic_km.q) and carry_in in source + target:
            raise ValueError('carry_in must be disjoint from source and target.')
        if carry_in is not False and (not isinstance(carry_in, _arithmetic_km.q)):
            raise ValueError('carry_in must be a quantum wire or False.')
        available = builder.max_qubits - builder.num_allocated_qubits
        desired = max(0, n - 2) if carry_budget is None else carry_budget
        clean = int(min(available, desired, max(0, n - 2)))
        sizes = _arithmetic_partition(n, clean)
        preserve = source[-1] if signed_source and source else None
        source += [preserve if preserve is not None else False] * (n - len(source))
        if subtract:
            builder.x(_arithmetic__as_array(target))
        boundaries = []
        start = 0
        carry = carry_in
        for number, length in enumerate(sizes):
            aa, bb = (source[start:start + length], target[start:start + length])
            retain = number + 1 < len(sizes)
            outgoing = _arithmetic__segment(builder, aa, bb, carry, retain_outgoing=retain, preserve=preserve)
            if retain:
                boundaries.append((aa, bb, carry, outgoing))
            carry = outgoing
            start += length
        for aa, bb, incoming, outgoing in reversed(boundaries):
            if outgoing is False:
                continue
            result = builder.alloc_bits(1)[0]
            builder.hmr(outgoing, result)
            builder.free(outgoing)
            builder.push_condition(result)
            _arithmetic__phase_borrow(builder, aa, bb, incoming, preserve=preserve)
            builder.pop_condition()
            builder.free(result)
        if subtract:
            builder.x(_arithmetic__as_array(target))

def _initialize_arithmetic_private():
    global _arithmetic_private_INTEGRATED_ROOT, _arithmetic_private_MAJORITY_TRUTH, _arithmetic_private_Sequence, _arithmetic_private__Frame, _arithmetic_private__IntegratedPath, _arithmetic_private___file__, _arithmetic_private___name__, _arithmetic_private__as_array, _arithmetic_private__compute_carry, _arithmetic_private__erase_carry, _arithmetic_private__phase_borrow, _arithmetic_private__phase_carry, _arithmetic_private__segment, _arithmetic_private__sum_keep_carry, _arithmetic_private_add, _arithmetic_private_annotations, _arithmetic_private_dataclass, _arithmetic_private_horner_rows, _arithmetic_private_km, _arithmetic_private_partition, _arithmetic_private_phase_quadratic, _arithmetic_private_signed_row
    _arithmetic_private_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).dataclass
    _arithmetic_private_Sequence = _import_component('typing', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).Sequence
    _arithmetic_private_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False)
    _arithmetic_private_phase_quadratic = _import_component('compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).phase_quadratic
    _arithmetic_private_MAJORITY_TRUTH = _import_component('compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).MAJORITY_TRUTH

    @_arithmetic_private_dataclass
    class _arithmetic_private__Frame:
        a: object
        b: object
        incoming: object
        outgoing: object
        preserve_sign: bool = False

    def _arithmetic_private__as_array(wires):
        return _arithmetic_private_km.array(list(wires))

    def _arithmetic_private__compute_carry(builder, a, b, incoming, *, preserve=None):
        if a is False and incoming is False:
            return _arithmetic_private__Frame(a, b, incoming, False)
        outgoing = builder.alloc_qubits(1)[0]
        if a is False:
            builder.ccx(incoming, b, outgoing)
        elif a == preserve and isinstance(incoming, _arithmetic_private_km.q):
            builder.cx(a, incoming)
            builder.cx(a, b)
            builder.ccx(incoming, b, outgoing)
            builder.cx(a, outgoing)
            return _arithmetic_private__Frame(a, b, incoming, outgoing, True)
        else:
            builder.cx(incoming, a)
            builder.cx(incoming, b)
            builder.ccx(a, b, outgoing)
            builder.cx(incoming, outgoing)
        return _arithmetic_private__Frame(a, b, incoming, outgoing)

    def _arithmetic_private__erase_carry(builder, frame, *, write_sum):
        a, b, incoming, outgoing = (frame.a, frame.b, frame.incoming, frame.outgoing)
        if outgoing is False:
            return
        if frame.preserve_sign:
            builder.cx(a, outgoing)
            builder.del_and(incoming, b, outgoing)
            builder.cx(a, incoming)
            builder.cx(incoming if write_sum else a, b)
        elif a is False:
            builder.del_and(incoming, b, outgoing)
            if write_sum:
                builder.cx(incoming, b)
        else:
            builder.cx(incoming, outgoing)
            builder.del_and(a, b, outgoing)
            builder.cx(incoming, a)
            if write_sum:
                builder.cx(a, b)
            else:
                builder.cx(incoming, b)
        builder.free(outgoing)

    def _arithmetic_private__sum_keep_carry(builder, frame):
        if frame.preserve_sign:
            builder.cx(frame.a, frame.incoming)
            builder.cx(frame.incoming, frame.b)
        elif frame.a is False:
            builder.cx(frame.incoming, frame.b)
        else:
            builder.cx(frame.incoming, frame.a)
            builder.cx(frame.a, frame.b)

    def _arithmetic_private__segment(builder, a, b, incoming, *, retain_outgoing, preserve=None):
        n = len(b)
        if retain_outgoing:
            frames = []
            carry = incoming
            for aa, bb in zip(a, b):
                frame = _arithmetic_private__compute_carry(builder, aa, bb, carry, preserve=preserve)
                frames.append(frame)
                carry = frame.outgoing
            _arithmetic_private__sum_keep_carry(builder, frames[-1])
            for frame in reversed(frames[:-1]):
                _arithmetic_private__erase_carry(builder, frame, write_sum=True)
            return carry
        if n == 1:
            builder.cx(a[0], b[0])
            builder.cx(incoming, b[0])
            return False
        frames = []
        carry = incoming
        for aa, bb in zip(a[:-2], b[:-2]):
            frame = _arithmetic_private__compute_carry(builder, aa, bb, carry, preserve=preserve)
            frames.append(frame)
            carry = frame.outgoing
        aa, bb = (a[-2], b[-2])
        if aa == preserve and isinstance(carry, _arithmetic_private_km.q):
            builder.cx(aa, carry)
            builder.cx(aa, bb)
            builder.cx(aa, b[-1])
            builder.ccx(carry, bb, b[-1])
            builder.cx(aa, carry)
            builder.cx(carry, bb)
        elif aa is False:
            builder.ccx(carry, bb, b[-1])
            builder.cx(carry, bb)
        else:
            builder.cx(carry, aa)
            builder.cx(carry, bb)
            builder.cx(carry, b[-1])
            builder.ccx(aa, bb, b[-1])
            builder.cx(carry, aa)
            builder.cx(aa, bb)
        builder.cx(a[-1], b[-1])
        for frame in reversed(frames):
            _arithmetic_private__erase_carry(builder, frame, write_sum=True)
        return False

    def _arithmetic_private__phase_carry(builder, a, b, incoming, *, preserve=None):
        """Apply (-1)**carry_out(a+b+incoming), restoring all operands."""
        frames = []
        carry = incoming
        for aa, bb in zip(a[:-1], b[:-1]):
            frame = _arithmetic_private__compute_carry(builder, aa, bb, carry, preserve=preserve)
            frames.append(frame)
            carry = frame.outgoing
        _arithmetic_private_phase_quadratic(builder, [a[-1], b[-1], carry], _arithmetic_private_MAJORITY_TRUTH)
        for frame in reversed(frames):
            _arithmetic_private__erase_carry(builder, frame, write_sum=False)

    def _arithmetic_private__phase_borrow(builder, a, final_sum, incoming, *, preserve=None):
        builder.x(_arithmetic_private__as_array(final_sum))
        _arithmetic_private__phase_carry(builder, a, final_sum, incoming, preserve=preserve)
        builder.x(_arithmetic_private__as_array(final_sum))

    def _arithmetic_private_partition(width: int, clean: int) -> list[int]:
        """Choose deterministic segment sizes without exceeding ``clean`` wires.

    Earlier segments keep one carry each.  A nonfinal segment of length l
    needs l fresh carries; the final segment needs only max(0,l-2), because
    the last carry goes directly into the target's most significant bit.
    """
        if width <= 0:
            return []
        if clean < 0:
            raise ValueError('clean must be nonnegative.')
        if width <= clean + 2:
            return [width]
        for boundaries in range(1, clean + 1):
            final = clean - boundaries + 2
            capacity = sum((clean - j for j in range(boundaries))) + final
            if capacity < width:
                continue
            remaining = width - final
            sizes = []
            for j in range(boundaries):
                length = min(clean - j, remaining - (boundaries - j - 1))
                if length <= 0:
                    break
                sizes.append(length)
                remaining -= length
            if len(sizes) == boundaries and remaining == 0:
                return sizes + [final]
        raise ValueError(f'{width}-bit segmented adder needs more than {clean} clean carry wires.')

    def _arithmetic_private_add(builder: _arithmetic_private_km.CircuitBuilder, source: _arithmetic_private_Sequence, target: _arithmetic_private_Sequence, *, carry_in=False, subtract: bool=False, signed_source: bool=False, carry_budget: int | None=None) -> None:
        """target += (+/-)(source+carry_in), with zero extension and clean erasure.

    All source wires, including carry_in, are preserved.  Source bits may be
    shorter than target; omitted high bits are zero, with no physical padding.
    With signed_source=True, high source positions reuse the actual sign
    wire.  An alternate majority frame preserves that shared wire throughout.
    carry_in can be a quantum bit or False.  Subtraction subtracts both terms.

    With n ordinary source bits and k carry wires, the expected Toffoli count
    is n-1 + max(0,n-2-k)/2 whenever ``partition(n,k)`` exists.  Literal zero
    bits and compile-time carry values can make actual cost lower.  All
    measurement outcomes have identical data outputs and identical phase.
    """
        source, target = (list(source), list(target))
        n = len(target)
        if not n:
            return
        source = source[:n]
        if any((not isinstance(q, _arithmetic_private_km.q) for q in source)):
            raise ValueError('Source must contain quantum wires; high zeros are implicit.')
        if len(set(source + target)) != len(source) + len(target):
            raise ValueError('Source and target must be disjoint distinct wires.')
        if isinstance(carry_in, _arithmetic_private_km.q) and carry_in in source + target:
            raise ValueError('carry_in must be disjoint from source and target.')
        if carry_in is not False and (not isinstance(carry_in, _arithmetic_private_km.q)):
            raise ValueError('carry_in must be a quantum wire or False.')
        available = builder.max_qubits - builder.num_allocated_qubits
        desired = max(0, n - 2) if carry_budget is None else carry_budget
        clean = int(min(available, desired, max(0, n - 2)))
        sizes = _arithmetic_private_partition(n, clean)
        preserve = source[-1] if signed_source and source else None
        source += [preserve if preserve is not None else False] * (n - len(source))
        if subtract:
            builder.x(_arithmetic_private__as_array(target))
        boundaries = []
        start = 0
        carry = carry_in
        for number, length in enumerate(sizes):
            aa, bb = (source[start:start + length], target[start:start + length])
            retain = number + 1 < len(sizes)
            outgoing = _arithmetic_private__segment(builder, aa, bb, carry, retain_outgoing=retain, preserve=preserve)
            if retain:
                boundaries.append((aa, bb, carry, outgoing))
            carry = outgoing
            start += length
        for aa, bb, incoming, outgoing in reversed(boundaries):
            if outgoing is False:
                continue
            result = builder.alloc_bits(1)[0]
            builder.hmr(outgoing, result)
            builder.free(outgoing)
            builder.push_condition(result)
            _arithmetic_private__phase_borrow(builder, aa, bb, incoming, preserve=preserve)
            builder.pop_condition()
            builder.free(result)
        if subtract:
            builder.x(_arithmetic_private__as_array(target))

def _initialize_compiler():
    global _compiler_INTEGRATED_ROOT, _compiler_MAJORITY_TRUTH, _compiler_QuadraticPlan, _compiler__IntegratedPath, _compiler___file__, _compiler___name__, _compiler__product_polynomial, _compiler_anf_from_truth, _compiler_annotations, _compiler_dataclass, _compiler_lru_cache, _compiler_phase_quadratic, _compiler_synthesize_quadratic, _compiler_xor_quadratic
    _compiler_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/compiler.py', False).dataclass

    def _compiler_anf_from_truth(truth):
        coefficients = [int(v) & 1 for v in truth]
        n = (len(coefficients) - 1).bit_length()
        if len(coefficients) != 1 << n:
            raise ValueError('Truth table length must be a power of two.')
        for j in range(n):
            for mask in range(1 << n):
                if mask & 1 << j:
                    coefficients[mask] ^= coefficients[mask ^ 1 << j]
        return tuple((mask for mask, value in enumerate(coefficients) if value))

    @_compiler_dataclass(frozen=True)
    class _compiler_QuadraticPlan:
        width: int
        affine: tuple[int, ...]
        products: tuple[tuple[int, int, int, int], ...]
        truth: tuple[int, ...]

        @property
        def toffolis(self):
            return len(self.products)

        def evaluate(self, value):
            out = 0
            for monomial in self.affine:
                out ^= int(value & monomial == monomial)
            for left, right, _, _ in self.products:
                out ^= (value & left).bit_count() & 1 & ((value & right).bit_count() & 1)
            return out

    def _compiler_phase_quadratic(builder, variables, truth):
        """Compile an exact sign window to Z/CZ only, including a constant sign."""
        variables = list(variables)
        anf = _compiler_anf_from_truth(tuple(truth))
        if len(truth) != 1 << len(variables) or any((m.bit_count() > 2 for m in anf)):
            raise ValueError('Expected a quadratic phase truth table.')
        for mask in anf:
            indices = [k for k in range(len(variables)) if mask >> k & 1]
            if not indices:
                raise ValueError('Constant branch phase needs an explicit phase wire.')
            if len(indices) == 1:
                builder.z(variables[indices[0]])
            else:
                builder.cz(variables[indices[0]], variables[indices[1]])
    _compiler_MAJORITY_TRUTH = tuple((int(x.bit_count() >= 2) for x in range(8)))

def _initialize_lookup():
    global _lookup_INTEGRATED_ROOT, _lookup__IntegratedPath, _lookup___file__, _lookup___name__, _lookup__bits, _lookup_algebraic_coefficients, _lookup_annotations, _lookup_km, _lookup_load_table, _lookup_lookup_plan, _lookup_unload_table

    def _lookup_algebraic_coefficients(table, address_bits=None):
        """Return vector-valued Boolean ANF coefficients, in address-mask order."""
        values = [int(value) for value in table]
        if not values or len(values) & len(values) - 1:
            raise ValueError('A lookup table must contain a power of two entries')
        n = len(values).bit_length() - 1
        if address_bits is not None and n != address_bits:
            raise ValueError('Table size does not match its address register')
        if any((value < 0 for value in values)):
            raise ValueError('Lookup values must be nonnegative bit strings')
        for bit in range(n):
            flag = 1 << bit
            for address in range(len(values)):
                if address & flag:
                    values[address] ^= values[address ^ flag]
        return values

    def _lookup__bits(value):
        while value:
            bit = value & -value
            yield (bit.bit_length() - 1)
            value ^= bit

    def _lookup_lookup_plan(table, address_bits=None):
        coefficients = _lookup_algebraic_coefficients(table, address_bits)
        n = len(coefficients).bit_length() - 1
        needed = {mask for mask, value in enumerate(coefficients) if value}
        for mask in tuple(needed):
            while mask:
                needed.add(mask)
                mask -= 1 << mask.bit_length() - 1
        children = {mask: [] for mask in needed}
        roots = []
        for mask in sorted(needed):
            if not mask:
                continue
            parent = mask ^ 1 << mask.bit_length() - 1
            if parent:
                children[parent].append(mask)
            else:
                roots.append(mask)
        count = sum((mask.bit_count() >= 2 for mask in needed))
        scratch = max((max(0, mask.bit_count() - 1) for mask in needed if children.get(mask)), default=0)
        return {'address_bits': n, 'coefficients': coefficients, 'needed': needed, 'children': children, 'roots': roots, 'and_count': count, 'scratch_qubits': scratch}

    def _lookup_load_table(builder, table, address, target):
        """XOR table[address] into target, preserving every other qubit and phase.

    A clean target therefore receives the table value. This function is also
    its own logical inverse; it makes no assumption about target values.
    Address and target must be disjoint.  The caller may instead use the
    starter kit's lower-cost del_lookup for measurement-based table erasure.
    """
        address, target = (list(address), list(target))
        if len(set(address + target)) != len(address) + len(target):
            raise ValueError('Lookup address and target wires must be disjoint')
        table = [int(value) for value in table]
        if any((value >= 1 << len(target) for value in table)):
            raise ValueError('A table value exceeds the target width')
        plan = _lookup_lookup_plan(table, len(address))
        coefficients, children = (plan['coefficients'], plan['children'])
        available = builder.max_qubits - builder.num_allocated_qubits
        clean_limit = int(min(plan['scratch_qubits'], available))
        if clean_limit < 0:
            raise ValueError('No valid workspace budget')
        emitted_ands = 0

        def ccx(a, b, t):
            nonlocal emitted_ands
            builder.ccx(a, b, t)
            emitted_ands += 1

        def fanout(control, mask):
            for index in _lookup__bits(mask):
                builder.cx(control, target[index])

        def multiple_product(controls, mask):
            """XOR one product through an output frame, borrowing dirty data.

        With k>=3 controls and k-2 borrowed bits, a forward/reverse ladder
        followed by the same ladder without its first AND cancels every
        borrowed input term. Exactly the product of all controls survives on
        the target; every borrowed bit is restored. Cost is 4*k-8 CCX.
        """
            outputs = list(_lookup__bits(mask))
            if not outputs:
                raise AssertionError('A pruned leaf has no output')
            pivot = target[outputs[0]]
            for index in outputs[1:]:
                builder.cx(pivot, target[index])
            if len(controls) == 1:
                builder.cx(controls[0], pivot)
            elif len(controls) == 2:
                ccx(*controls, pivot)
            else:
                forbidden = set(controls) | {pivot}
                borrowed = [wire for wire in address + target if wire not in forbidden]
                needed = len(controls) - 2
                if len(borrowed) < needed:
                    raise ValueError('Insufficient dirty wires for a low-workspace lookup')
                borrowed = borrowed[:needed]
                ladder = [(controls[0], controls[1], borrowed[0])]
                ladder += [(borrowed[j - 1], controls[j + 1], borrowed[j]) for j in range(1, needed)]
                for a, b, t in ladder:
                    ccx(a, b, t)
                ccx(borrowed[-1], controls[-1], pivot)
                for a, b, t in reversed(ladder):
                    ccx(a, b, t)
                for a, b, t in ladder[1:]:
                    ccx(a, b, t)
                ccx(borrowed[-1], controls[-1], pivot)
                for a, b, t in reversed(ladder[1:]):
                    ccx(a, b, t)
            for index in reversed(outputs[1:]):
                builder.cx(pivot, target[index])

        def suffixes(mask):
            for child in children.get(mask, ()):
                yield child
                yield from suffixes(child)

        def visit(mask, product, depth):
            fanout(product, coefficients[mask])
            if depth == clean_limit:
                for descendant in suffixes(mask):
                    if coefficients[descendant]:
                        controls = [product] + [address[bit] for bit in _lookup__bits(descendant ^ mask)]
                        multiple_product(controls, coefficients[descendant])
                return
            for child in children.get(mask, ()):
                next_bit = address[child.bit_length() - 1]
                if not children.get(child):
                    multiple_product([product, next_bit], coefficients[child])
                    continue
                temporary = builder.alloc_qubits(1)[0]
                ccx(product, next_bit, temporary)
                visit(child, temporary, depth + 1)
                builder.del_and(product, next_bit, temporary)
                builder.free(temporary)
        fanout(True, coefficients[0])
        for root in plan['roots']:
            visit(root, address[root.bit_length() - 1], 0)
        return {'and_count': emitted_ands, 'scratch_qubits': clean_limit}

def _initialize_paired_arithmetic():
    global _paired_arithmetic_CarryDebt, _paired_arithmetic_DeferredBoundedToken, _paired_arithmetic_DeferredProductToken, _paired_arithmetic_INTEGRATED_ROOT, _paired_arithmetic_MAJORITY_TRUTH, _paired_arithmetic__Frame, _paired_arithmetic__IntegratedPath, _paired_arithmetic___file__, _paired_arithmetic___name__, _paired_arithmetic__compute_carry, _paired_arithmetic__deferred_overflow, _paired_arithmetic__erase_carry, _paired_arithmetic__finish_top, _paired_arithmetic__inputs, _paired_arithmetic__phase_borrow, _paired_arithmetic__row_inputs, _paired_arithmetic__segment_repay, _paired_arithmetic__sum_keep_carry, _paired_arithmetic__terminal_partition, _paired_arithmetic_annotations, _paired_arithmetic_dataclass, _paired_arithmetic_dirty_mcz_cost, _paired_arithmetic_forward_add, _paired_arithmetic_forward_bounded_rows, _paired_arithmetic_forward_growing_product, _paired_arithmetic_forward_signed_row, _paired_arithmetic_inverse_add, _paired_arithmetic_inverse_bounded_rows, _paired_arithmetic_inverse_growing_product, _paired_arithmetic_inverse_signed_row, _paired_arithmetic_km, _paired_arithmetic_partition, _paired_arithmetic_phase_quadratic, _paired_arithmetic_release_saved_bit, _paired_arithmetic_repay_saved_bit, _paired_arithmetic_terminal_add, _paired_arithmetic_terminal_cost, _paired_arithmetic_terminal_dirty_count
    _paired_arithmetic_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).dataclass
    _paired_arithmetic_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)
    _paired_arithmetic__compute_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._compute_carry
    _paired_arithmetic__erase_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._erase_carry
    _paired_arithmetic__sum_keep_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._sum_keep_carry
    _paired_arithmetic__phase_borrow = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._phase_borrow
    _paired_arithmetic_partition = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).partition
    _paired_arithmetic_phase_quadratic = _import_component('fusion.compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).phase_quadratic
    _paired_arithmetic_MAJORITY_TRUTH = _import_component('fusion.compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).MAJORITY_TRUTH
    _paired_arithmetic_terminal_add = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).terminal_add
    _paired_arithmetic_terminal_cost = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).terminal_cost
    _paired_arithmetic_terminal_dirty_count = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).terminal_dirty_count
    _paired_arithmetic_dirty_mcz_cost = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).dirty_mcz_cost

    @_paired_arithmetic_dataclass
    class _paired_arithmetic_CarryDebt:
        measurements: dict
        width: int
        consumed: bool = False

    def _paired_arithmetic__finish_top(builder, a, b, incoming, preserve):
        """Two high sum bits; the last carry goes directly into the high bit."""
        aa, bb = (a[-2], b[-2])
        if aa == preserve and isinstance(incoming, _paired_arithmetic_km.q):
            builder.cx(aa, incoming)
            builder.cx(aa, bb)
            builder.cx(aa, b[-1])
            builder.ccx(incoming, bb, b[-1])
            builder.cx(aa, incoming)
            builder.cx(incoming, bb)
        elif aa is False:
            builder.ccx(incoming, bb, b[-1])
            builder.cx(incoming, bb)
        else:
            builder.cx(incoming, aa)
            builder.cx(incoming, bb)
            builder.cx(incoming, b[-1])
            builder.ccx(aa, bb, b[-1])
            builder.cx(incoming, aa)
            builder.cx(aa, bb)
        builder.cx(a[-1], b[-1])

    def _paired_arithmetic__inputs(source, target, carry_in, signed_source):
        source, target = (list(source), list(target))
        width = len(target)
        source = source[:width]
        if any((not isinstance(q, _paired_arithmetic_km.q) for q in source)):
            raise ValueError('Source must contain quantum wires.')
        if len(set(source + target)) != len(source) + len(target):
            raise ValueError('Source and target must be disjoint distinct wires.')
        if isinstance(carry_in, _paired_arithmetic_km.q) and carry_in in source + target:
            raise ValueError('Carry-in must be disjoint from the data words.')
        if carry_in is not False and (not isinstance(carry_in, _paired_arithmetic_km.q)):
            raise ValueError('Carry-in must be a quantum wire or False.')
        preserve = source[-1] if signed_source and source else None
        source += [preserve if preserve is not None else False] * (width - len(source))
        return (source, target, preserve)

    def _paired_arithmetic_forward_add(builder, source, target, *, carry_in=False, signed_source=False):
        """target += source+carry_in, with two clean carries and deferred signs.

    The returned debt is mandatory: consume it in `inverse_add` after all
    changes to this target have been reversed.  Arbitrary diagonal phases
    and further reversible classical computation may intervene.
    """
        a, b, preserve = _paired_arithmetic__inputs(source, target, carry_in, signed_source)
        width = len(b)
        debts = {}
        if not width:
            return _paired_arithmetic_CarryDebt(debts, width)
        if width == 1:
            builder.cx(a[0], b[0])
            builder.cx(carry_in, b[0])
            return _paired_arithmetic_CarryDebt(debts, width)

        def measure(carry, position):
            if carry is False:
                return
            outcome = builder.alloc_bits(1)[0]
            builder.hmr(carry, outcome)
            builder.free(carry)
            debts[position] = outcome
        carry = carry_in
        for index, (aa, bb) in enumerate(zip(a[:-2], b[:-2])):
            frame = _paired_arithmetic__compute_carry(builder, aa, bb, carry, preserve=preserve)
            _paired_arithmetic__sum_keep_carry(builder, frame)
            if index:
                measure(carry, index)
            carry = frame.outgoing
        _paired_arithmetic__finish_top(builder, a, b, carry, preserve)
        if width > 2:
            measure(carry, width - 2)
        return _paired_arithmetic_CarryDebt(debts, width)

    def _paired_arithmetic__segment_repay(builder, a, b, incoming, *, retain_outgoing, preserve, start, debt, overflow_phase=None):

        def compute(aa, bb, carry, position):
            frame = _paired_arithmetic__compute_carry(builder, aa, bb, carry, preserve=preserve)
            outcome = debt.measurements.pop(position, None)
            if outcome is not None:
                if frame.outgoing is not False:
                    builder.push_condition(outcome)
                    builder.z(frame.outgoing)
                    builder.pop_condition()
                builder.free(outcome)
            return frame
        n = len(b)
        if retain_outgoing:
            frames, carry = ([], incoming)
            for index, (aa, bb) in enumerate(zip(a, b)):
                frame = compute(aa, bb, carry, start + index + 1)
                frames.append(frame)
                carry = frame.outgoing
            _paired_arithmetic__sum_keep_carry(builder, frames[-1])
            for frame in reversed(frames[:-1]):
                _paired_arithmetic__erase_carry(builder, frame, write_sum=True)
            return carry
        if n == 1:
            if overflow_phase is not None:
                builder.push_condition(overflow_phase)
                _paired_arithmetic_phase_quadratic(builder, [a[0], b[0], incoming], _paired_arithmetic_MAJORITY_TRUTH)
                builder.pop_condition()
            builder.cx(a[0], b[0])
            builder.cx(incoming, b[0])
            return False
        frames, carry = ([], incoming)
        for index, (aa, bb) in enumerate(zip(a[:-2], b[:-2])):
            frame = compute(aa, bb, carry, start + index + 1)
            frames.append(frame)
            carry = frame.outgoing
        if overflow_phase is not None:
            if a[-2] is not False or a[-1] is not False:
                raise ValueError('Overflow phase currently requires two high source zeros.')
            builder.push_condition(overflow_phase)
            builder.ccz(carry, b[-2], b[-1])
            builder.pop_condition()
        _paired_arithmetic__finish_top(builder, a, b, carry, preserve)
        for frame in reversed(frames):
            _paired_arithmetic__erase_carry(builder, frame, write_sum=True)
        return False

    def _paired_arithmetic__terminal_partition(a, b, incoming, clean, external_dirty, *, release_input=False, ordinary_final=False, allow_dirty_terminal=True, overflow_phase=False):
        """Cost a no-clean final segment only when the ordinary partition fails.

    Earlier target bits have already received their final values and can be
    borrowed as arbitrary dirty workspace. All borrowed bits are restored
    before the boundary-carry phase comparators execute.
    """
        width = len(b)
        states = {(0, 0): (0.0, ())}
        candidates = []
        original_source = [wire for wire in a if isinstance(wire, _paired_arithmetic_km.q)]
        for used in range(clean + 1 + int(release_input)):
            for (start, count), (cost, sizes) in list(states.items()):
                if count != used:
                    continue
                capacity = clean - used + int(release_input and used > 0)
                release_cost = 0.5 if release_input and used > 0 else 0.0
                if ordinary_final and width - start <= capacity + 2:
                    phase_cost = 0.5 if overflow_phase and width - start >= 2 else 0.0
                    candidates.append((cost + width - start - 1 + release_cost + phase_cost, sizes + (width - start,), None))
                tail = a[start:]
                real = next((i for i, wire in enumerate(tail) if wire is False), len(tail))
                prefix = tail[:real]
                distinct = len(set(prefix)) == len(prefix)
                unsigned = all((wire is False for wire in tail[real:]))
                has_carry = isinstance(incoming, _paired_arithmetic_km.q) or any((wire is not False for wire in a[:start]))
                if allow_dirty_terminal and has_carry and distinct and unsigned and (not overflow_phase or real < len(tail)):
                    forbidden = set(prefix + b[start:])
                    if not start and isinstance(incoming, _paired_arithmetic_km.q):
                        forbidden.add(incoming)
                    pool = list(b[:start]) + original_source + list(external_dirty)
                    if start and isinstance(incoming, _paired_arithmetic_km.q) and (not release_input):
                        pool.append(incoming)
                    pool = list(dict.fromkeys((wire for wire in pool if isinstance(wire, _paired_arithmetic_km.q) and wire not in forbidden)))
                    needed = _paired_arithmetic_terminal_dirty_count(width - start, real)
                    if len(pool) >= needed:
                        terminal = _paired_arithmetic_terminal_cost(width - start, real)
                        if overflow_phase:
                            terminal += 0.5 * _paired_arithmetic_dirty_mcz_cost(width - start - real + 1)
                        candidates.append((cost + terminal + release_cost, sizes + (width - start,), pool))
                if used == clean + int(release_input):
                    continue
                for length in range(1, min(capacity, width - start - 1) + 1):
                    key = (start + length, used + 1)
                    value = (cost + length + 0.5 * (length - 1), sizes + (length,))
                    if key not in states or value < states[key]:
                        states[key] = value
        if not candidates:
            raise ValueError(f'{width}-bit inverse adder has no valid {clean}-carry terminal partition.')
        cost, sizes, pool = min(candidates, key=lambda item: (item[0], item[1]))
        return (list(sizes), pool)

    def _paired_arithmetic_inverse_add(builder, source, target, debt: _paired_arithmetic_CarryDebt, *, carry_in=False, signed_source=False, carry_budget=None, dirty_wires=(), carry_lifecycle=None, overflow_phase=None, allow_dirty_overflow=False):
        """Undo the matching forward add and repay every recorded carry phase.

    If overflow_phase is a classical bit, additionally phase the final
    borrow carry by (-1)**overflow_phase.  The supported multi-bit case has
    two literal high source zeros.  Its final borrow is a three-bit product
    already exposed at the ordinary two-bit terminal, so one conditioned
    CCZ suffices without an additional clean wire.  This optional mode
    excludes dirty terminal fallbacks by default.  The optional
    allow_dirty_overflow mode compares exact sparse terminals too, paying
    their final product phase with an independently proved dirty-MCZ echo.
    """
        a, b, preserve = _paired_arithmetic__inputs(source, target, carry_in, signed_source)
        n = len(b)
        if overflow_phase is not None and (signed_source or (n >= 2 and (a[-2] is not False or a[-1] is not False))):
            raise ValueError('Overflow-phase inverse needs an unsigned source with two high zeros.')
        if debt.width != n:
            raise ValueError('This carry debt belongs to a different adder width.')
        if debt.consumed:
            raise ValueError("This forward adder's phase debt has already been consumed.")
        debt.consumed = True
        if not n:
            return
        available = builder.max_qubits - builder.num_allocated_qubits
        desired = max(0, n - 2) if carry_budget is None else carry_budget
        clean = int(min(available, desired, max(0, n - 2)))
        terminal_dirty = None
        if carry_lifecycle is not None:
            if signed_source or not isinstance(carry_in, _paired_arithmetic_km.q):
                raise ValueError('Disposable incoming carry requires an unsigned quantum-carry adder.')
            sizes, terminal_dirty = _paired_arithmetic__terminal_partition(a, b, carry_in, clean, dirty_wires, release_input=True, ordinary_final=True, allow_dirty_terminal=overflow_phase is None or allow_dirty_overflow, overflow_phase=overflow_phase is not None and allow_dirty_overflow)
        elif overflow_phase is not None and allow_dirty_overflow:
            sizes, terminal_dirty = _paired_arithmetic__terminal_partition(a, b, carry_in, clean, dirty_wires, ordinary_final=True, overflow_phase=True)
        else:
            try:
                sizes = _paired_arithmetic_partition(n, clean)
            except ValueError:
                if signed_source or overflow_phase is not None:
                    raise
                sizes, terminal_dirty = _paired_arithmetic__terminal_partition(a, b, carry_in, clean, dirty_wires)
        builder.x(_paired_arithmetic_km.array(b))
        boundaries = []
        start, carry = (0, carry_in)
        released_input = False
        for number, length in enumerate(sizes):
            aa, bb = (a[start:start + length], b[start:start + length])
            retain = number + 1 < len(sizes)
            if not retain and terminal_dirty is not None:
                _paired_arithmetic_terminal_add(builder, aa, bb, carry, dirty=terminal_dirty, debt=debt, start=start, overflow_phase=overflow_phase)
                outgoing = False
            else:
                outgoing = _paired_arithmetic__segment_repay(builder, aa, bb, carry, retain_outgoing=retain, preserve=preserve, start=start, debt=debt, overflow_phase=overflow_phase if not retain else None)
            if retain:
                recorded_incoming = carry
                if number == 0 and carry_lifecycle is not None:
                    carry_lifecycle[0](carry_in)
                    recorded_incoming = None
                    released_input = True
                boundaries.append((aa, bb, recorded_incoming, outgoing))
            carry = outgoing
            start += length
        for aa, bb, incoming, outgoing in reversed(boundaries):
            if outgoing is False:
                continue
            result = builder.alloc_bits(1)[0]
            builder.hmr(outgoing, result)
            builder.free(outgoing)
            builder.push_condition(result)
            recreated = incoming is None
            if recreated:
                incoming = carry_lifecycle[1]()
            _paired_arithmetic__phase_borrow(builder, aa, bb, incoming, preserve=preserve)
            if recreated:
                carry_lifecycle[0](incoming)
            builder.pop_condition()
            builder.free(result)
        builder.x(_paired_arithmetic_km.array(b))
        if debt.measurements:
            raise AssertionError(f'Unpaid carry positions: {sorted(debt.measurements)}')
        return released_input

    def _paired_arithmetic__row_inputs(source, target, *, shift, nearest, signed_source):
        source, target = (list(source), list(target))
        carry = False
        if shift >= 0:
            target = target[shift:]
        else:
            cut = -shift
            if signed_source and cut >= len(source):
                if nearest:
                    return ([], [], False)
                source, cut = (source[-1:], 0)
            if nearest and cut - 1 < len(source):
                carry = source[cut - 1]
            source = source[cut:]
        if not target or (not source and carry is False):
            return ([], [], False)
        return (source[:len(target)], target, carry)

    def _paired_arithmetic_forward_signed_row(builder, source, target, *, shift, sign, nearest=True, signed_source=False):
        source, target, carry = _paired_arithmetic__row_inputs(source, target, shift=shift, nearest=nearest, signed_source=signed_source)
        if isinstance(sign, _paired_arithmetic_km.q) and sign in source + target + ([carry] if isinstance(carry, _paired_arithmetic_km.q) else []):
            raise ValueError('Sign must be disjoint from row operands and rounding bit.')
        for wire in target:
            builder.cx(sign, wire)
        debt = _paired_arithmetic_forward_add(builder, source, target, carry_in=carry, signed_source=signed_source)
        for wire in target:
            builder.cx(sign, wire)
        return debt

    def _paired_arithmetic_inverse_signed_row(builder, source, target, debt, *, shift, sign, nearest=True, signed_source=False, carry_budget=None, overflow_phase=None, allow_dirty_overflow=False):
        source, target, carry = _paired_arithmetic__row_inputs(source, target, shift=shift, nearest=nearest, signed_source=signed_source)
        if isinstance(sign, _paired_arithmetic_km.q) and sign in source + target + ([carry] if isinstance(carry, _paired_arithmetic_km.q) else []):
            raise ValueError('Sign must be disjoint from row operands and rounding bit.')
        for wire in target:
            builder.cx(sign, wire)
        _paired_arithmetic_inverse_add(builder, source, target, debt, carry_in=carry, signed_source=signed_source, carry_budget=carry_budget, overflow_phase=overflow_phase, allow_dirty_overflow=allow_dirty_overflow)
        for wire in target:
            builder.cx(sign, wire)

    @_paired_arithmetic_dataclass
    class _paired_arithmetic_DeferredProductToken:
        plan: object
        row_debts: list

    @_paired_arithmetic_dataclass
    class _paired_arithmetic_DeferredBoundedToken:
        plan: object
        saved_bit: object
        window: int
        row_debts: list
        overflow_debt: object = None

    def _paired_arithmetic_release_saved_bit(builder, saved):
        """Release a saved original bit; repay it after the original is restored."""
        outcome = builder.alloc_bits(1)[0]
        builder.hmr(saved, outcome)
        builder.free(saved)
        return outcome

    def _paired_arithmetic_repay_saved_bit(builder, restored, outcome):
        """Cancel the release sign using the now-restored original bit."""
        builder.push_condition(outcome)
        builder.z(restored)
        builder.pop_condition()
        builder.free(outcome)

    def _paired_arithmetic__deferred_overflow(builder, residual, source, target, token, *, inverse, carry_budget=None, overflow_phase=None, allow_dirty_overflow=False):
        if token.saved_bit is None:
            return
        sigma = residual[token.plan.last - 1]
        if token.plan.signed_source:
            builder.cx(source[-1], sigma)
        top, saved = (target[token.window - 1], token.saved_bit)
        builder.cx(sigma, saved)
        builder.cx(sigma, top)
        builder.x(top)
        wrap = builder.alloc_qubits(1)[0]
        builder.ccx(saved, top, wrap)
        high = target[token.window:]
        for wire in high:
            builder.cx(sigma, wire)
        if inverse:
            _paired_arithmetic_inverse_add(builder, [], high, token.overflow_debt, carry_in=wrap, carry_budget=carry_budget, dirty_wires=target[:token.window], overflow_phase=overflow_phase, allow_dirty_overflow=allow_dirty_overflow)
        else:
            token.overflow_debt = _paired_arithmetic_forward_add(builder, [], high, carry_in=wrap)
        for wire in high:
            builder.cx(sigma, wire)
        builder.del_and(saved, top, wrap)
        builder.free(wrap)
        builder.x(top)
        builder.cx(sigma, top)
        builder.cx(sigma, saved)
        if token.plan.signed_source:
            builder.cx(source[-1], sigma)

def _initialize_paired_arithmetic_private():
    global _paired_arithmetic_private_CarryDebt, _paired_arithmetic_private_DeferredBoundedToken, _paired_arithmetic_private_DeferredProductToken, _paired_arithmetic_private_INTEGRATED_ROOT, _paired_arithmetic_private_MAJORITY_TRUTH, _paired_arithmetic_private__Frame, _paired_arithmetic_private__IntegratedPath, _paired_arithmetic_private___file__, _paired_arithmetic_private___name__, _paired_arithmetic_private__compute_carry, _paired_arithmetic_private__deferred_overflow, _paired_arithmetic_private__erase_carry, _paired_arithmetic_private__finish_top, _paired_arithmetic_private__inputs, _paired_arithmetic_private__phase_borrow, _paired_arithmetic_private__row_inputs, _paired_arithmetic_private__segment_repay, _paired_arithmetic_private__sum_keep_carry, _paired_arithmetic_private__terminal_partition, _paired_arithmetic_private_annotations, _paired_arithmetic_private_dataclass, _paired_arithmetic_private_dirty_mcz_cost, _paired_arithmetic_private_forward_add, _paired_arithmetic_private_forward_bounded_rows, _paired_arithmetic_private_forward_growing_product, _paired_arithmetic_private_forward_signed_row, _paired_arithmetic_private_inverse_add, _paired_arithmetic_private_inverse_bounded_rows, _paired_arithmetic_private_inverse_growing_product, _paired_arithmetic_private_inverse_signed_row, _paired_arithmetic_private_km, _paired_arithmetic_private_partition, _paired_arithmetic_private_phase_quadratic, _paired_arithmetic_private_release_saved_bit, _paired_arithmetic_private_repay_saved_bit, _paired_arithmetic_private_terminal_add, _paired_arithmetic_private_terminal_cost, _paired_arithmetic_private_terminal_dirty_count
    _paired_arithmetic_private_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).dataclass
    _paired_arithmetic_private_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)
    _paired_arithmetic_private__compute_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._compute_carry
    _paired_arithmetic_private__erase_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._erase_carry
    _paired_arithmetic_private__sum_keep_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._sum_keep_carry
    _paired_arithmetic_private__phase_borrow = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._phase_borrow
    _paired_arithmetic_private_partition = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).partition
    _paired_arithmetic_private_phase_quadratic = _import_component('fusion.compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).phase_quadratic
    _paired_arithmetic_private_MAJORITY_TRUTH = _import_component('fusion.compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).MAJORITY_TRUTH
    _paired_arithmetic_private_terminal_add = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).terminal_add
    _paired_arithmetic_private_terminal_cost = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).terminal_cost
    _paired_arithmetic_private_terminal_dirty_count = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).terminal_dirty_count
    _paired_arithmetic_private_dirty_mcz_cost = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).dirty_mcz_cost

    @_paired_arithmetic_private_dataclass
    class _paired_arithmetic_private_CarryDebt:
        measurements: dict
        width: int
        consumed: bool = False

    def _paired_arithmetic_private__finish_top(builder, a, b, incoming, preserve):
        """Two high sum bits; the last carry goes directly into the high bit."""
        aa, bb = (a[-2], b[-2])
        if aa == preserve and isinstance(incoming, _paired_arithmetic_private_km.q):
            builder.cx(aa, incoming)
            builder.cx(aa, bb)
            builder.cx(aa, b[-1])
            builder.ccx(incoming, bb, b[-1])
            builder.cx(aa, incoming)
            builder.cx(incoming, bb)
        elif aa is False:
            builder.ccx(incoming, bb, b[-1])
            builder.cx(incoming, bb)
        else:
            builder.cx(incoming, aa)
            builder.cx(incoming, bb)
            builder.cx(incoming, b[-1])
            builder.ccx(aa, bb, b[-1])
            builder.cx(incoming, aa)
            builder.cx(aa, bb)
        builder.cx(a[-1], b[-1])

    def _paired_arithmetic_private__inputs(source, target, carry_in, signed_source):
        source, target = (list(source), list(target))
        width = len(target)
        source = source[:width]
        if any((not isinstance(q, _paired_arithmetic_private_km.q) for q in source)):
            raise ValueError('Source must contain quantum wires.')
        if len(set(source + target)) != len(source) + len(target):
            raise ValueError('Source and target must be disjoint distinct wires.')
        if isinstance(carry_in, _paired_arithmetic_private_km.q) and carry_in in source + target:
            raise ValueError('Carry-in must be disjoint from the data words.')
        if carry_in is not False and (not isinstance(carry_in, _paired_arithmetic_private_km.q)):
            raise ValueError('Carry-in must be a quantum wire or False.')
        preserve = source[-1] if signed_source and source else None
        source += [preserve if preserve is not None else False] * (width - len(source))
        return (source, target, preserve)

    def _paired_arithmetic_private_forward_add(builder, source, target, *, carry_in=False, signed_source=False):
        """target += source+carry_in, with two clean carries and deferred signs.

    The returned debt is mandatory: consume it in `inverse_add` after all
    changes to this target have been reversed.  Arbitrary diagonal phases
    and further reversible classical computation may intervene.
    """
        a, b, preserve = _paired_arithmetic_private__inputs(source, target, carry_in, signed_source)
        width = len(b)
        debts = {}
        if not width:
            return _paired_arithmetic_private_CarryDebt(debts, width)
        if width == 1:
            builder.cx(a[0], b[0])
            builder.cx(carry_in, b[0])
            return _paired_arithmetic_private_CarryDebt(debts, width)

        def measure(carry, position):
            if carry is False:
                return
            outcome = builder.alloc_bits(1)[0]
            builder.hmr(carry, outcome)
            builder.free(carry)
            debts[position] = outcome
        carry = carry_in
        for index, (aa, bb) in enumerate(zip(a[:-2], b[:-2])):
            frame = _paired_arithmetic_private__compute_carry(builder, aa, bb, carry, preserve=preserve)
            _paired_arithmetic_private__sum_keep_carry(builder, frame)
            if index:
                measure(carry, index)
            carry = frame.outgoing
        _paired_arithmetic_private__finish_top(builder, a, b, carry, preserve)
        if width > 2:
            measure(carry, width - 2)
        return _paired_arithmetic_private_CarryDebt(debts, width)

    def _paired_arithmetic_private__segment_repay(builder, a, b, incoming, *, retain_outgoing, preserve, start, debt, overflow_phase=None):

        def compute(aa, bb, carry, position):
            frame = _paired_arithmetic_private__compute_carry(builder, aa, bb, carry, preserve=preserve)
            outcome = debt.measurements.pop(position, None)
            if outcome is not None:
                if frame.outgoing is not False:
                    builder.push_condition(outcome)
                    builder.z(frame.outgoing)
                    builder.pop_condition()
                builder.free(outcome)
            return frame
        n = len(b)
        if retain_outgoing:
            frames, carry = ([], incoming)
            for index, (aa, bb) in enumerate(zip(a, b)):
                frame = compute(aa, bb, carry, start + index + 1)
                frames.append(frame)
                carry = frame.outgoing
            _paired_arithmetic_private__sum_keep_carry(builder, frames[-1])
            for frame in reversed(frames[:-1]):
                _paired_arithmetic_private__erase_carry(builder, frame, write_sum=True)
            return carry
        if n == 1:
            if overflow_phase is not None:
                builder.push_condition(overflow_phase)
                _paired_arithmetic_private_phase_quadratic(builder, [a[0], b[0], incoming], _paired_arithmetic_private_MAJORITY_TRUTH)
                builder.pop_condition()
            builder.cx(a[0], b[0])
            builder.cx(incoming, b[0])
            return False
        frames, carry = ([], incoming)
        for index, (aa, bb) in enumerate(zip(a[:-2], b[:-2])):
            frame = compute(aa, bb, carry, start + index + 1)
            frames.append(frame)
            carry = frame.outgoing
        if overflow_phase is not None:
            if a[-2] is not False or a[-1] is not False:
                raise ValueError('Overflow phase currently requires two high source zeros.')
            builder.push_condition(overflow_phase)
            builder.ccz(carry, b[-2], b[-1])
            builder.pop_condition()
        _paired_arithmetic_private__finish_top(builder, a, b, carry, preserve)
        for frame in reversed(frames):
            _paired_arithmetic_private__erase_carry(builder, frame, write_sum=True)
        return False

    def _paired_arithmetic_private__terminal_partition(a, b, incoming, clean, external_dirty, *, release_input=False, ordinary_final=False, allow_dirty_terminal=True, overflow_phase=False):
        """Cost a no-clean final segment only when the ordinary partition fails.

    Earlier target bits have already received their final values and can be
    borrowed as arbitrary dirty workspace. All borrowed bits are restored
    before the boundary-carry phase comparators execute.
    """
        width = len(b)
        states = {(0, 0): (0.0, ())}
        candidates = []
        original_source = [wire for wire in a if isinstance(wire, _paired_arithmetic_private_km.q)]
        for used in range(clean + 1 + int(release_input)):
            for (start, count), (cost, sizes) in list(states.items()):
                if count != used:
                    continue
                capacity = clean - used + int(release_input and used > 0)
                release_cost = 0.5 if release_input and used > 0 else 0.0
                if ordinary_final and width - start <= capacity + 2:
                    phase_cost = 0.5 if overflow_phase and width - start >= 2 else 0.0
                    candidates.append((cost + width - start - 1 + release_cost + phase_cost, sizes + (width - start,), None))
                tail = a[start:]
                real = next((i for i, wire in enumerate(tail) if wire is False), len(tail))
                prefix = tail[:real]
                distinct = len(set(prefix)) == len(prefix)
                unsigned = all((wire is False for wire in tail[real:]))
                has_carry = isinstance(incoming, _paired_arithmetic_private_km.q) or any((wire is not False for wire in a[:start]))
                if allow_dirty_terminal and has_carry and distinct and unsigned and (not overflow_phase or real < len(tail)):
                    forbidden = set(prefix + b[start:])
                    if not start and isinstance(incoming, _paired_arithmetic_private_km.q):
                        forbidden.add(incoming)
                    pool = list(b[:start]) + original_source + list(external_dirty)
                    if start and isinstance(incoming, _paired_arithmetic_private_km.q) and (not release_input):
                        pool.append(incoming)
                    pool = list(dict.fromkeys((wire for wire in pool if isinstance(wire, _paired_arithmetic_private_km.q) and wire not in forbidden)))
                    needed = _paired_arithmetic_private_terminal_dirty_count(width - start, real)
                    if len(pool) >= needed:
                        terminal = _paired_arithmetic_private_terminal_cost(width - start, real)
                        if overflow_phase:
                            terminal += 0.5 * _paired_arithmetic_private_dirty_mcz_cost(width - start - real + 1)
                        candidates.append((cost + terminal + release_cost, sizes + (width - start,), pool))
                if used == clean + int(release_input):
                    continue
                for length in range(1, min(capacity, width - start - 1) + 1):
                    key = (start + length, used + 1)
                    value = (cost + length + 0.5 * (length - 1), sizes + (length,))
                    if key not in states or value < states[key]:
                        states[key] = value
        if not candidates:
            raise ValueError(f'{width}-bit inverse adder has no valid {clean}-carry terminal partition.')
        cost, sizes, pool = min(candidates, key=lambda item: (item[0], item[1]))
        return (list(sizes), pool)

    def _paired_arithmetic_private_inverse_add(builder, source, target, debt: _paired_arithmetic_private_CarryDebt, *, carry_in=False, signed_source=False, carry_budget=None, dirty_wires=(), carry_lifecycle=None, overflow_phase=None, allow_dirty_overflow=False):
        """Undo the matching forward add and repay every recorded carry phase.

    If overflow_phase is a classical bit, additionally phase the final
    borrow carry by (-1)**overflow_phase.  The supported multi-bit case has
    two literal high source zeros.  Its final borrow is a three-bit product
    already exposed at the ordinary two-bit terminal, so one conditioned
    CCZ suffices without an additional clean wire.  This optional mode
    excludes dirty terminal fallbacks by default.  The optional
    allow_dirty_overflow mode compares exact sparse terminals too, paying
    their final product phase with an independently proved dirty-MCZ echo.
    """
        a, b, preserve = _paired_arithmetic_private__inputs(source, target, carry_in, signed_source)
        n = len(b)
        if overflow_phase is not None and (signed_source or (n >= 2 and (a[-2] is not False or a[-1] is not False))):
            raise ValueError('Overflow-phase inverse needs an unsigned source with two high zeros.')
        if debt.width != n:
            raise ValueError('This carry debt belongs to a different adder width.')
        if debt.consumed:
            raise ValueError("This forward adder's phase debt has already been consumed.")
        debt.consumed = True
        if not n:
            return
        available = builder.max_qubits - builder.num_allocated_qubits
        desired = max(0, n - 2) if carry_budget is None else carry_budget
        clean = int(min(available, desired, max(0, n - 2)))
        terminal_dirty = None
        if carry_lifecycle is not None:
            if signed_source or not isinstance(carry_in, _paired_arithmetic_private_km.q):
                raise ValueError('Disposable incoming carry requires an unsigned quantum-carry adder.')
            sizes, terminal_dirty = _paired_arithmetic_private__terminal_partition(a, b, carry_in, clean, dirty_wires, release_input=True, ordinary_final=True, allow_dirty_terminal=overflow_phase is None or allow_dirty_overflow, overflow_phase=overflow_phase is not None and allow_dirty_overflow)
        elif overflow_phase is not None and allow_dirty_overflow:
            sizes, terminal_dirty = _paired_arithmetic_private__terminal_partition(a, b, carry_in, clean, dirty_wires, ordinary_final=True, overflow_phase=True)
        else:
            try:
                sizes = _paired_arithmetic_private_partition(n, clean)
            except ValueError:
                if signed_source or overflow_phase is not None:
                    raise
                sizes, terminal_dirty = _paired_arithmetic_private__terminal_partition(a, b, carry_in, clean, dirty_wires)
        builder.x(_paired_arithmetic_private_km.array(b))
        boundaries = []
        start, carry = (0, carry_in)
        released_input = False
        for number, length in enumerate(sizes):
            aa, bb = (a[start:start + length], b[start:start + length])
            retain = number + 1 < len(sizes)
            if not retain and terminal_dirty is not None:
                _paired_arithmetic_private_terminal_add(builder, aa, bb, carry, dirty=terminal_dirty, debt=debt, start=start, overflow_phase=overflow_phase)
                outgoing = False
            else:
                outgoing = _paired_arithmetic_private__segment_repay(builder, aa, bb, carry, retain_outgoing=retain, preserve=preserve, start=start, debt=debt, overflow_phase=overflow_phase if not retain else None)
            if retain:
                recorded_incoming = carry
                if number == 0 and carry_lifecycle is not None:
                    carry_lifecycle[0](carry_in)
                    recorded_incoming = None
                    released_input = True
                boundaries.append((aa, bb, recorded_incoming, outgoing))
            carry = outgoing
            start += length
        for aa, bb, incoming, outgoing in reversed(boundaries):
            if outgoing is False:
                continue
            result = builder.alloc_bits(1)[0]
            builder.hmr(outgoing, result)
            builder.free(outgoing)
            builder.push_condition(result)
            recreated = incoming is None
            if recreated:
                incoming = carry_lifecycle[1]()
            _paired_arithmetic_private__phase_borrow(builder, aa, bb, incoming, preserve=preserve)
            if recreated:
                carry_lifecycle[0](incoming)
            builder.pop_condition()
            builder.free(result)
        builder.x(_paired_arithmetic_private_km.array(b))
        if debt.measurements:
            raise AssertionError(f'Unpaid carry positions: {sorted(debt.measurements)}')
        return released_input

    @_paired_arithmetic_private_dataclass
    class _paired_arithmetic_private_DeferredProductToken:
        plan: object
        row_debts: list

    @_paired_arithmetic_private_dataclass
    class _paired_arithmetic_private_DeferredBoundedToken:
        plan: object
        saved_bit: object
        window: int
        row_debts: list
        overflow_debt: object = None

def _initialize_quadratic_terms():
    global _quadratic_terms_INTEGRATED_ROOT, _quadratic_terms_PolynomialPlan, _quadratic_terms__IntegratedPath, _quadratic_terms___file__, _quadratic_terms___name__, _quadratic_terms_annotations, _quadratic_terms_compile_polynomial, _quadratic_terms_dataclass, _quadratic_terms_gf2_rank, _quadratic_terms_product_terms, _quadratic_terms_xor_polynomial
    _quadratic_terms_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/quadratic_terms.py', False).dataclass

    def _quadratic_terms_product_terms(left, right):
        terms = set()
        for i in range(left.bit_length()):
            if not left >> i & 1:
                continue
            for j in range(right.bit_length()):
                if right >> j & 1:
                    key = 1 << i | 1 << j
                    terms.symmetric_difference_update((key,))
        return terms

    def _quadratic_terms_gf2_rank(rows):
        pivots = {}
        for row in rows:
            while row:
                pivot = row.bit_length() - 1
                if pivot not in pivots:
                    pivots[pivot] = row
                    break
                row ^= pivots[pivot]
        return len(pivots)

    @_quadratic_terms_dataclass(frozen=True)
    class _quadratic_terms_PolynomialPlan:
        width: int
        affine: tuple[int, ...]
        products: tuple[tuple[int, int, int, int], ...]
        original: tuple[int, ...]
        alternating_rank: int

    def _quadratic_terms_compile_polynomial(width, terms):
        """Factor with exact coefficient comparison and the rank lower bound.

    An ANF coefficient is indexed by the set of its variables, as a bit mask.
    Duplicate input terms cancel.  This polynomial representation is exact
    on the entire Boolean cube, with no sampling and no truth-table limit.
    """
        remaining = set()
        for term in terms:
            term = int(term)
            if term < 0 or term >> width or term.bit_count() > 2:
                raise ValueError('Expected constant, linear, or quadratic ANF terms.')
            remaining.symmetric_difference_update((term,))
        original = tuple(sorted(remaining))
        matrix = [0] * width
        for term in original:
            if term.bit_count() == 2:
                i, j = [k for k in range(width) if term >> k & 1]
                matrix[i] ^= 1 << j
                matrix[j] ^= 1 << i
        rank = _quadratic_terms_gf2_rank(matrix)
        products = []
        while any((term.bit_count() == 2 for term in remaining)):
            edge = min((term for term in remaining if term.bit_count() == 2))
            i, j = [k for k in range(width) if edge >> k & 1]
            left, right = (1 << i, 1 << j)
            for k in range(width):
                if k == i or k == j:
                    continue
                if 1 << j | 1 << k in remaining:
                    left |= 1 << k
                if 1 << i | 1 << k in remaining:
                    right |= 1 << k
            remaining.symmetric_difference_update(_quadratic_terms_product_terms(left, right))
            products.append((left, right, i, j))
        recovered = set(remaining)
        for left, right, _, _ in products:
            recovered.symmetric_difference_update(_quadratic_terms_product_terms(left, right))
        if recovered != set(original) or len(products) * 2 != rank:
            raise AssertionError('Quadratic synthesis certificate failed.')
        return _quadratic_terms_PolynomialPlan(width, tuple(sorted(remaining)), tuple(products), original, rank)

    def _quadratic_terms_xor_polynomial(builder, variables, target, terms):
        """Emit a rank-minimal AND/XOR realization, preserving all input wires."""
        variables = list(variables)
        if len(set(variables)) != len(variables) or target in variables:
            raise ValueError('Input variables and target must be distinct.')
        plan = _quadratic_terms_compile_polynomial(len(variables), terms)
        for term in plan.affine:
            if term:
                builder.cx(variables[term.bit_length() - 1], target)
            else:
                builder.x(target)
        for left, right, i, j in plan.products:
            frames = [(variables[k], variables[i]) for k in range(plan.width) if k != i and left >> k & 1]
            frames += [(variables[k], variables[j]) for k in range(plan.width) if k != j and right >> k & 1]
            for a, b in frames:
                builder.cx(a, b)
            builder.ccx(variables[i], variables[j], target)
            for a, b in reversed(frames):
                builder.cx(a, b)
        return plan

def _initialize_stage94_bit_routing_math():
    global _stage94_bit_routing_math_INTEGRATED_ROOT, _stage94_bit_routing_math__IntegratedPath, _stage94_bit_routing_math___file__, _stage94_bit_routing_math___name__, _stage94_bit_routing_math_annotations, _stage94_bit_routing_math_certificate, _stage94_bit_routing_math_leading_indicator_terms, _stage94_bit_routing_math_lru_cache, _stage94_bit_routing_math_operations, _stage94_bit_routing_math_prefix_expression, _stage94_bit_routing_math_selector_value
    _stage94_bit_routing_math_lru_cache = _import_component('functools', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/stage94_bit_routing_math.py', False).lru_cache

    def _stage94_bit_routing_math_selector_value(leading_zeros, position, stage):
        """Return the bit-j addition selector at a current butterfly position."""
        modulus = 1 << stage
        return leading_zeros >> stage & 1 ^ int(position % modulus < leading_zeros % modulus)

    def _stage94_bit_routing_math_prefix_expression(truth, maximum):
        """Express a finite function in P_j=[ell>=j], including P_0=1."""
        if not isinstance(truth, int) or truth < 0 or truth >> maximum + 1:
            raise ValueError('A leading-zero truth mask has the wrong finite domain.')
        terms = tuple((index for index in range(maximum + 1) if truth >> index & 1 ^ (truth >> index - 1 & 1 if index else 0)))
        for leading_zeros in range(maximum + 1):
            actual = sum((leading_zeros >= term for term in terms)) & 1
            if actual != truth >> leading_zeros & 1:
                raise AssertionError('A prefix expansion failed its exact finite-domain identity.')
        return terms

    def _stage94_bit_routing_math_operations(payload_width=21):
        """Generate every physical pair and its exact mathematical selector."""
        if not isinstance(payload_width, int) or payload_width < 2:
            raise ValueError('The zero-supported payload width must be at least two.')
        result = []
        for stage in range(payload_width.bit_length()):
            distance = 1 << stage
            for first in range(payload_width):
                second = first + distance
                if first & distance or second >= payload_width:
                    continue
                truth = sum((_stage94_bit_routing_math_selector_value(leading_zeros, first, stage) << leading_zeros for leading_zeros in range(payload_width + 1)))
                result.append(dict(stage=stage, first=first, second=second, selector_truth=truth, prefix_terms=_stage94_bit_routing_math_prefix_expression(truth, payload_width)))
        return tuple(result)

    @_stage94_bit_routing_math_lru_cache(maxsize=8)
    def _stage94_bit_routing_math_certificate(payload_width=21):
        """Certify all payload symbols, all controls, and both route directions."""
        route = _stage94_bit_routing_math_operations(payload_width)
        virtual_width = 1 << payload_width.bit_length()
        contexts = payload_width + 1
        virtual_nonzero_uses = 0
        virtual_pairs_checked = 0
        counts = [0] * payload_width.bit_length()
        for operation in route:
            counts[operation['stage']] += 1
        for leading_zeros in range(contexts):
            for initial_position in range(virtual_width):
                position = initial_position
                for stage in range(payload_width.bit_length()):
                    position ^= _stage94_bit_routing_math_selector_value(leading_zeros, position, stage) << stage
                if position != (initial_position + leading_zeros) % virtual_width:
                    raise AssertionError('The full butterfly does not add its mathematical displacement.')
            live = payload_width - leading_zeros
            initial = list(range(1, live + 1)) + [0] * (virtual_width - live)
            expected = [0] * leading_zeros + list(range(1, live + 1)) + [0] * (virtual_width - payload_width)
            state = list(initial)
            for stage in range(payload_width.bit_length()):
                distance = 1 << stage
                for first in range(virtual_width):
                    if first & distance:
                        continue
                    second = first + distance
                    if not _stage94_bit_routing_math_selector_value(leading_zeros, first, stage):
                        continue
                    if second >= payload_width:
                        virtual_pairs_checked += 1
                        virtual_nonzero_uses += int(bool(state[first] or state[second]))
                    state[first], state[second] = (state[second], state[first])
            if state != expected:
                raise AssertionError('The padded butterfly did not align its independent payload symbols.')
            physical = list(initial[:payload_width])
            for operation in route:
                if operation['selector_truth'] >> leading_zeros & 1:
                    first, second = (operation['first'], operation['second'])
                    physical[first], physical[second] = (physical[second], physical[first])
            if physical != expected[:payload_width]:
                raise AssertionError('Omitting virtual pairs changed a valid physical payload.')
            for operation in reversed(route):
                if operation['selector_truth'] >> leading_zeros & 1:
                    first, second = (operation['first'], operation['second'])
                    physical[first], physical[second] = (physical[second], physical[first])
            if physical != initial[:payload_width]:
                raise AssertionError('The reversed physical butterfly did not restore its payload.')
        if virtual_nonzero_uses:
            raise AssertionError('A discarded virtual pair contains live payload information.')
        if payload_width == 21 and (counts != [10, 10, 9, 8, 5] or len(route) != 42):
            raise AssertionError('The selected twenty-one-bit route changed its exact 42-swap budget.')
        return dict(status='EXACT_ZERO_SUPPORTED_BINARY_BUTTERFLY', payload_width=payload_width, leading_zero_contexts=contexts, virtual_width=virtual_width, controlled_swaps=len(route), swaps_per_stage=counts, virtual_pairs_checked=virtual_pairs_checked, virtual_nonzero_uses=virtual_nonzero_uses, full_position_addition_proved=True, independent_payload_symbols_proved=True, forward_and_inverse_proved=True, selectors_from_prefix_thresholds=True, source_search_or_saved_plan_inputs=False)

def _initialize_thermometer_cleanup():
    global _thermometer_cleanup_INTEGRATED_ROOT, _thermometer_cleanup__IntegratedPath, _thermometer_cleanup___file__, _thermometer_cleanup___name__, _thermometer_cleanup_annotations, _thermometer_cleanup_binary_to_thermometer, _thermometer_cleanup_erase_pair_count_thermometer, _thermometer_cleanup_km, _thermometer_cleanup_linear_frame, _thermometer_cleanup_thermometer_matrix

    def _thermometer_cleanup_thermometer_matrix(maximum):
        """Return the exact threshold basis in monomial coordinates1..maximum."""
        if maximum < 1:
            raise ValueError('The maximum pair count must be positive.')
        size = 1 << maximum.bit_length()
        rows = []
        for threshold in range(1, maximum + 1):
            values = [int(k >= threshold) for k in range(size)]
            for bit in range(maximum.bit_length()):
                for k in range(size):
                    if k >> bit & 1:
                        values[k] ^= values[k ^ 1 << bit]
            row = sum((values[mask] << mask - 1 for mask in range(1, maximum + 1)))
            for k in range(maximum + 1):
                value = sum(((row >> mask - 1 & 1) * int(k & mask == mask) for mask in range(1, maximum + 1))) & 1
                if value != int(k >= threshold):
                    raise AssertionError('A threshold basis row failed an exact valid-k check.')
            rows.append(row)
        return rows

    def _thermometer_cleanup_linear_frame(rows):
        """Compile an invertible row matrix into an exact CNOT/SWAP sequence."""
        rows = list(map(int, rows))
        n = len(rows)
        operations = []
        if any((row < 0 or row >> n for row in rows)):
            raise ValueError('Linear matrix dimensions do not match.')
        for column in range(n):
            pivot = next((row for row in range(column, n) if rows[row] >> column & 1), None)
            if pivot is None:
                raise ValueError('The threshold basis is not invertible.')
            if pivot != column:
                rows[column], rows[pivot] = (rows[pivot], rows[column])
                operations.append(('swap', column, pivot))
            for row in range(n):
                if row != column and rows[row] >> column & 1:
                    rows[row] ^= rows[column]
                    operations.append(('cx', column, row))
        if rows != [1 << index for index in range(n)]:
            raise AssertionError('Linear matrix elimination failed.')
        return list(reversed(operations))

    def _thermometer_cleanup_binary_to_thermometer(builder, flags, maximum):
        """Consume the binary data frame, returning thresholds and owned helpers.

    Original flag wires remain allocated. The returned threshold wires are a
    permutation of those wires plus the newly allocated helper wires. The
    caller must finish the cleanup before reusing the original flag frame.
    """
        flags = list(flags)
        if len(flags) != maximum.bit_length() or len(set(flags)) != len(flags):
            raise ValueError('Binary flag width does not match the maximum count.')
        monomials = {1 << bit: wire for bit, wire in enumerate(flags)}
        helpers = []
        for mask in range(1, maximum + 1):
            if mask in monomials:
                continue
            bit = mask & -mask
            parent = mask ^ bit
            if parent not in monomials:
                raise AssertionError('Monomial computation is not topologically ordered.')
            wire = builder.alloc_qubits(1)[0]
            builder.ccx(monomials[parent], monomials[bit], wire)
            monomials[mask] = wire
            helpers.append(wire)
        wires = [monomials[mask] for mask in range(1, maximum + 1)]
        rows = _thermometer_cleanup_thermometer_matrix(maximum)
        for operation, left, right in _thermometer_cleanup_linear_frame(rows):
            if operation == 'cx':
                builder.cx(wires[left], wires[right])
            else:
                builder.swap(wires[left], wires[right])
        return (wires, helpers)

def _initialize_fourier_resource_expectation():
    global _fourier_resource_expectation_Fraction, _fourier_resource_expectation_INTEGRATED_ROOT, _fourier_resource_expectation_ONE, _fourier_resource_expectation_Program, _fourier_resource_expectation_ZERO, _fourier_resource_expectation__IntegratedPath, _fourier_resource_expectation___file__, _fourier_resource_expectation___name__, _fourier_resource_expectation_affine_leaves, _fourier_resource_expectation_annotations, _fourier_resource_expectation_choose, _fourier_resource_expectation_exact_expectation, _fourier_resource_expectation_json, _fourier_resource_expectation_lru_cache, _fourier_resource_expectation_probability, _fourier_resource_expectation_product, _fourier_resource_expectation_unit_cases, _fourier_resource_expectation_xor
    _fourier_resource_expectation_Fraction = _import_component('fractions', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', False).Fraction
    _fourier_resource_expectation_Program = _import_component('branch_prover', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', False).Program
    _fourier_resource_expectation_ZERO = ('affine', 0, 0)
    _fourier_resource_expectation_ONE = ('affine', 1, 0)

    def _fourier_resource_expectation_xor(*values):
        constant, mask, terms = (0, 0, set())
        pending = list(values)
        while pending:
            value = pending.pop()
            if value[0] == 'xor':
                pending.extend(value[1])
            elif value[0] == 'affine':
                constant ^= value[1]
                mask ^= value[2]
            elif value in terms:
                terms.remove(value)
            else:
                terms.add(value)
        if constant or mask:
            terms.add(('affine', constant, mask))
        if not terms:
            return _fourier_resource_expectation_ZERO
        if len(terms) == 1:
            return next(iter(terms))
        return ('xor', tuple(sorted(terms, key=repr)))

    def _fourier_resource_expectation_product(*values):
        terms = set()
        pending = list(values)
        while pending:
            value = pending.pop()
            if value == _fourier_resource_expectation_ZERO:
                return _fourier_resource_expectation_ZERO
            if value == _fourier_resource_expectation_ONE:
                continue
            if value[0] == 'and':
                pending.extend(value[1])
            else:
                terms.add(value)
        for value in tuple(terms):
            if _fourier_resource_expectation_xor(value, _fourier_resource_expectation_ONE) in terms:
                return _fourier_resource_expectation_ZERO
        if not terms:
            return _fourier_resource_expectation_ONE
        if len(terms) == 1:
            return next(iter(terms))
        return ('and', tuple(sorted(terms, key=repr)))

    def _fourier_resource_expectation_choose(condition, yes, no):
        if yes == no:
            return yes
        return _fourier_resource_expectation_xor(no, _fourier_resource_expectation_product(condition, _fourier_resource_expectation_xor(yes, no)))

    def _fourier_resource_expectation_affine_leaves(value, result):
        if value[0] == 'affine':
            result.add(value)
        else:
            for child in value[1]:
                _fourier_resource_expectation_affine_leaves(child, result)

    def _fourier_resource_expectation_probability(value, *, rank_cap=12):
        leaves = set()
        _fourier_resource_expectation_affine_leaves(value, leaves)
        basis, pivots, coordinates = ([], {}, {})
        for leaf in sorted(leaves):
            remaining, representation = (leaf[2], 0)
            while remaining:
                pivot = remaining.bit_length() - 1
                if pivot not in pivots:
                    if len(basis) >= rank_cap:
                        raise ValueError('Exact branch-probability rank exceeds the explicit cap.')
                    bit = 1 << len(basis)
                    basis.append(remaining)
                    pivots[pivot] = (remaining, bit)
                    representation ^= bit
                    remaining = 0
                    break
                row, coordinate = pivots[pivot]
                remaining ^= row
                representation ^= coordinate
            coordinates[leaf] = representation

        def evaluate(node, assignment):
            kind = node[0]
            if kind == 'affine':
                return node[1] ^ (coordinates[node] & assignment).bit_count() & 1
            if kind == 'xor':
                return sum((evaluate(child, assignment) for child in node[1])) & 1
            return int(all((evaluate(child, assignment) for child in node[1])))
        return (_fourier_resource_expectation_Fraction(sum((evaluate(value, assignment) for assignment in range(1 << len(basis)))), 1 << len(basis)), len(basis))

    def _fourier_resource_expectation_exact_expectation(text, *, rank_cap=12, include_gates=False):
        program = _fourier_resource_expectation_Program(text)
        classical = {'0': _fourier_resource_expectation_ZERO, '1': _fourier_resource_expectation_ONE, 'False': _fourier_resource_expectation_ZERO, 'True': _fourier_resource_expectation_ONE}
        stack = [_fourier_resource_expectation_ONE]
        measured = set()
        cached = {}
        totals = dict(toffoli_like=_fourier_resource_expectation_Fraction(0), T=_fourier_resource_expectation_Fraction(0), generic_rotations=_fourier_resource_expectation_Fraction(0))
        static = dict(toffoli_like=0, T=0, generic_rotations=0)
        records = []
        max_rank = 0

        def read(wire):
            if wire.startswith('q'):
                raise ValueError('A quantum wire was used as a classical accounting condition.')
            return classical.get(wire, _fourier_resource_expectation_ZERO)
        for index, op in enumerate(program.operations):
            kind, args = (op.kind, op.arguments)
            active = _fourier_resource_expectation_product(stack[-1], _fourier_resource_expectation_ONE if op.condition is None else read(op.condition))
            if kind == 'PUSH_CONDITION':
                stack.append(active)
                continue
            if kind == 'POP_CONDITION':
                if len(stack) == 1:
                    raise AssertionError('Unmatched condition pop.')
                stack.pop()
                continue
            category = None
            if kind in ('CCX', 'CCZ', 'CSWAP'):
                if not all((wire.startswith('q') for wire in args)):
                    raise ValueError('Resource accounting requires quantum Toffoli-like operands.')
                category = 'toffoli_like'
            elif kind == 'Z_POW':
                angle = op.half_turns % 2
                if angle.denominator == 4:
                    category = 'T'
                elif angle.denominator > 4:
                    category = 'generic_rotations'
            if category is not None:
                if active not in cached:
                    cached[active] = _fourier_resource_expectation_probability(active, rank_cap=rank_cap)
                chance, rank = cached[active]
                max_rank = max(max_rank, rank)
                totals[category] += chance
                static[category] += 1
                if include_gates:
                    records.append(dict(instruction=index, operation=kind, category=category, probability=str(chance), affine_rank=rank))
            if kind == 'HMR':
                if op.event in measured:
                    raise AssertionError('A syntactic outcome was reused.')
                measured.add(op.event)
                variable = ('affine', 0, 1 << op.event)
                classical[args[1]] = _fourier_resource_expectation_choose(active, variable, read(args[1]))
            elif kind in ('BIT_STORE0', 'BIT_STORE1'):
                classical[args[0]] = _fourier_resource_expectation_choose(active, _fourier_resource_expectation_ONE if kind == 'BIT_STORE1' else _fourier_resource_expectation_ZERO, read(args[0]))
            elif kind == 'BIT_INVERT' or (kind == 'X' and args[0].startswith('b')):
                classical[args[0]] = _fourier_resource_expectation_xor(read(args[0]), active)
            elif kind == 'CX' and args[1].startswith('b'):
                classical[args[1]] = _fourier_resource_expectation_xor(read(args[1]), _fourier_resource_expectation_product(active, read(args[0])))
            elif kind == 'SWAP' and any((wire.startswith('b') for wire in args)):
                raise ValueError('Classical SWAP needs an explicit accounting rule.')
        if len(stack) != 1:
            raise AssertionError('Unclosed accounting condition.')
        report = dict(status='EXACT_EXPECTATION_FROM_CLASSICAL_GUARDS', assumptions=['Every active HMR measures a computational-basis wire and has a fair independent outcome.', 'Conditional costs count instruction execution, independently of quantum control values.'], accounting='exact Boolean guards; GF2-rank enumeration of affine leaves', rank_cap=rank_cap, maximum_rank_used=max_rank, syntactic_measurements=program.measurements, static=static, mean={key: str(value) for key, value in totals.items()}, mean_numeric={key: float(value) for key, value in totals.items()}, mean_Toffoli_plus_T_quarter=str(totals['toffoli_like'] + totals['T'] / 4), independent_condition_depth_not_assumed=True, official_verified=False)
        if include_gates:
            report['charged_gates'] = records
        return report

    def _fourier_resource_expectation_unit_cases():
        o = ('affine', 0, 1)
        t = ('affine', 0, 2)
        either = _fourier_resource_expectation_xor(o, t, _fourier_resource_expectation_product(o, t))
        assert _fourier_resource_expectation_probability(_fourier_resource_expectation_product(either, o))[0] == _fourier_resource_expectation_Fraction(1, 2)
        assert _fourier_resource_expectation_probability(either)[0] == _fourier_resource_expectation_Fraction(3, 4)
        assert _fourier_resource_expectation_probability(_fourier_resource_expectation_xor(o, t))[0] == _fourier_resource_expectation_Fraction(1, 2)
        assert _fourier_resource_expectation_probability(_fourier_resource_expectation_product(o, _fourier_resource_expectation_xor(o, _fourier_resource_expectation_ONE)))[0] == 0
        m = ('affine', 0, 4)
        assert _fourier_resource_expectation_probability(_fourier_resource_expectation_choose(o, m, _fourier_resource_expectation_ONE))[0] == _fourier_resource_expectation_Fraction(3, 4)
        assert _fourier_resource_expectation_probability(_fourier_resource_expectation_product(o, _fourier_resource_expectation_choose(o, m, _fourier_resource_expectation_ONE)))[0] == _fourier_resource_expectation_Fraction(1, 4)
        return dict(status='PASS', cases=6, correlated_OR_nested_guard_checked=True, conditional_HMR_old_destination_checked=True)
    if _fourier_resource_expectation___name__ == '__main__':
        _fourier_resource_expectation_json = _import_component('json', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', True)
        print(_fourier_resource_expectation_json.dumps(_fourier_resource_expectation_unit_cases(), sort_keys=True))

def _initialize_consuming_odd_sqrt():
    global _consuming_odd_sqrt_INTEGRATED_ROOT, _consuming_odd_sqrt_Path, _consuming_odd_sqrt_ROOT, _consuming_odd_sqrt__IntegratedPath, _consuming_odd_sqrt___file__, _consuming_odd_sqrt___name__, _consuming_odd_sqrt__add_leading_one, _consuming_odd_sqrt__arr, _consuming_odd_sqrt__low_finish, _consuming_odd_sqrt__low_prepare, _consuming_odd_sqrt__low_remainder_xor, _consuming_odd_sqrt__root_step, _consuming_odd_sqrt_add, _consuming_odd_sqrt_forward, _consuming_odd_sqrt_inverse, _consuming_odd_sqrt_km, _consuming_odd_sqrt_sys
    _consuming_odd_sqrt_Path = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False).Path
    _consuming_odd_sqrt_sys = _import_component('sys', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', True)
    _consuming_odd_sqrt_ROOT = _consuming_odd_sqrt_Path(_consuming_odd_sqrt___file__).resolve().parents[2]
    _consuming_odd_sqrt_sys.path[:0] = [str(_consuming_odd_sqrt_ROOT / 'fusion_handoff/official/kickmix'), str(_consuming_odd_sqrt_ROOT / 'cleanroom/baseline_stage97/engine')]
    _consuming_odd_sqrt_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False)
    _consuming_odd_sqrt_add = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False).add

    def _consuming_odd_sqrt__arr(wires):
        return _consuming_odd_sqrt_km.array(list(wires))

    def _consuming_odd_sqrt__add_leading_one(builder, target, *, inverse=False):
        """Add/subtract2**(n-2) modulo2**n, entirely Clifford."""
        if len(target) < 2:
            raise ValueError('Leading-one add needs two target positions')
        if inverse:
            builder.x(target[-2])
            builder.cx(target[-2], target[-1])
        else:
            builder.cx(target[-2], target[-1])
            builder.x(target[-2])

    def _consuming_odd_sqrt__low_prepare(builder, low, b, *, inverse=False):
        """Low three bits add3 mod8. Return OR and carry, both quadratic-cleanable."""
        x0, x1, x2 = low
        u, c = builder.alloc_qubits(2)
        if inverse:
            builder.x(u)
            builder.ccx(x0, x1, u)
            builder.x(x2)
            builder.ccx(u, x2, c)
            builder.x(x2)
        else:
            builder.cx(x0, u)
            builder.cx(x1, u)
            builder.ccx(x0, x1, u)
            builder.ccx(x2, u, c)
            builder.cx(u, x2)
            builder.cx(x0, x1)
            builder.x(x1)
            builder.x(x0)
        builder.cx(b, c)
        return (u, c)

    def _consuming_odd_sqrt__low_finish(builder, low, b, u, c, *, inverse=False):
        x0, x1, x2 = low
        builder.cx(b, c)
        builder.x(x2)
        builder.del_and(u, x2, c)
        builder.x(x2)
        builder.free(c)
        if inverse:
            builder.cx(u, x2)
        builder.x(u)
        builder.del_and(x0, x1, u)
        builder.free(u)
        if inverse:
            builder.x(x0)
            builder.x(x1)
            builder.cx(x0, x1)

    def _consuming_odd_sqrt__root_step(builder, remainder, older_root, b, *, initial=False, inverse=False):
        """One non-restoring step, after routing next inputpair into remainder[:2]."""
        low = list(remainder[:3])
        high = list(remainder[3:])
        u, c = _consuming_odd_sqrt__low_prepare(builder, low, b, inverse=inverse)
        builder.cx(b, _consuming_odd_sqrt__arr(high))
        if inverse:
            if not initial:
                _consuming_odd_sqrt__add_leading_one(builder, high, inverse=True)
            _consuming_odd_sqrt_add(builder, older_root, high, carry_in=c, subtract=True)
        else:
            _consuming_odd_sqrt_add(builder, older_root, high, carry_in=c)
            if not initial:
                _consuming_odd_sqrt__add_leading_one(builder, high)
        builder.cx(b, _consuming_odd_sqrt__arr(high))
        _consuming_odd_sqrt__low_finish(builder, low, b, u, c, inverse=inverse)

def _initialize_consuming_odd_sqrt_private():
    global _consuming_odd_sqrt_private_INTEGRATED_ROOT, _consuming_odd_sqrt_private_Path, _consuming_odd_sqrt_private_ROOT, _consuming_odd_sqrt_private__IntegratedPath, _consuming_odd_sqrt_private___file__, _consuming_odd_sqrt_private___name__, _consuming_odd_sqrt_private__add_leading_one, _consuming_odd_sqrt_private__arr, _consuming_odd_sqrt_private__low_finish, _consuming_odd_sqrt_private__low_prepare, _consuming_odd_sqrt_private__low_remainder_xor, _consuming_odd_sqrt_private__root_step, _consuming_odd_sqrt_private_add, _consuming_odd_sqrt_private_forward, _consuming_odd_sqrt_private_inverse, _consuming_odd_sqrt_private_km, _consuming_odd_sqrt_private_sys
    _consuming_odd_sqrt_private_Path = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False).Path
    _consuming_odd_sqrt_private_sys = _import_component('sys', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', True)
    _consuming_odd_sqrt_private_ROOT = _consuming_odd_sqrt_private_Path(_consuming_odd_sqrt_private___file__).resolve().parents[2]
    _consuming_odd_sqrt_private_sys.path[:0] = [str(_consuming_odd_sqrt_private_ROOT / 'fusion_handoff/official/kickmix'), str(_consuming_odd_sqrt_private_ROOT / 'cleanroom/baseline_stage97/engine')]
    _consuming_odd_sqrt_private_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False)
    _consuming_odd_sqrt_private_add = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False).add

    def _consuming_odd_sqrt_private__arr(wires):
        return _consuming_odd_sqrt_private_km.array(list(wires))

    def _consuming_odd_sqrt_private__add_leading_one(builder, target, *, inverse=False):
        """Add/subtract2**(n-2) modulo2**n, entirely Clifford."""
        if len(target) < 2:
            raise ValueError('Leading-one add needs two target positions')
        if inverse:
            builder.x(target[-2])
            builder.cx(target[-2], target[-1])
        else:
            builder.cx(target[-2], target[-1])
            builder.x(target[-2])

    def _consuming_odd_sqrt_private__low_prepare(builder, low, b, *, inverse=False):
        """Low three bits add3 mod8. Return OR and carry, both quadratic-cleanable."""
        x0, x1, x2 = low
        u, c = builder.alloc_qubits(2)
        if inverse:
            builder.x(u)
            builder.ccx(x0, x1, u)
            builder.x(x2)
            builder.ccx(u, x2, c)
            builder.x(x2)
        else:
            builder.cx(x0, u)
            builder.cx(x1, u)
            builder.ccx(x0, x1, u)
            builder.ccx(x2, u, c)
            builder.cx(u, x2)
            builder.cx(x0, x1)
            builder.x(x1)
            builder.x(x0)
        builder.cx(b, c)
        return (u, c)

    def _consuming_odd_sqrt_private__low_finish(builder, low, b, u, c, *, inverse=False):
        x0, x1, x2 = low
        builder.cx(b, c)
        builder.x(x2)
        builder.del_and(u, x2, c)
        builder.x(x2)
        builder.free(c)
        if inverse:
            builder.cx(u, x2)
        builder.x(u)
        builder.del_and(x0, x1, u)
        builder.free(u)
        if inverse:
            builder.x(x0)
            builder.x(x1)
            builder.cx(x0, x1)

    def _consuming_odd_sqrt_private__root_step(builder, remainder, older_root, b, *, initial=False, inverse=False):
        """One non-restoring step, after routing next inputpair into remainder[:2]."""
        low = list(remainder[:3])
        high = list(remainder[3:])
        u, c = _consuming_odd_sqrt_private__low_prepare(builder, low, b, inverse=inverse)
        builder.cx(b, _consuming_odd_sqrt_private__arr(high))
        if inverse:
            if not initial:
                _consuming_odd_sqrt_private__add_leading_one(builder, high, inverse=True)
            _consuming_odd_sqrt_private_add(builder, older_root, high, carry_in=c, subtract=True)
        else:
            _consuming_odd_sqrt_private_add(builder, older_root, high, carry_in=c)
            if not initial:
                _consuming_odd_sqrt_private__add_leading_one(builder, high)
        builder.cx(b, _consuming_odd_sqrt_private__arr(high))
        _consuming_odd_sqrt_private__low_finish(builder, low, b, u, c, inverse=inverse)

    def _consuming_odd_sqrt_private__low_remainder_xor(builder, Q, low):
        """XOR (-QÂ²-Q-1) mod16 into low, using one CCX and no ancilla."""
        q0, q1, q2, q3 = Q[:4]
        builder.x(_consuming_odd_sqrt_private__arr(low))
        builder.cx(q0, low[1])
        builder.cx(q1, low[1])
        builder.cx(q1, low[2])
        builder.cx(q2, low[2])
        builder.cx(q3, low[3])
        builder.cx(q2, low[3])
        builder.cx(q2, q0)
        builder.cx(q2, q1)
        builder.ccx(q0, q1, low[3])
        builder.cx(q2, q1)
        builder.cx(q2, q0)

    def _consuming_odd_sqrt_private_forward(builder, norm):
        norm = list(norm)
        if len(norm) != 22 or len(set(norm)) != 22:
            raise ValueError('Expected22 distinct input wires')
        builder.x(norm[20])
        builder.cx(norm[20], norm[21])
        remainder = norm[20:22]
        root = []
        for j in range(1, 13):
            pair = norm[20 - 2 * j:22 - 2 * j] if j <= 10 else list(builder.alloc_qubits(2))
            if j == 1:
                b = True
                older = []
                remainder = pair + remainder
            else:
                b = remainder[-1]
                builder.x(b)
                older = root
                root = [b] + root
                remainder = pair + remainder[:-1]
            _consuming_odd_sqrt_private__root_step(builder, remainder, older, b, initial=j == 1)
        b = remainder[-1]
        builder.x(b)
        Q = [b] + root
        W = remainder[:-1]
        high = W[1:]
        builder.cx(b, _consuming_odd_sqrt_private__arr(high))
        _consuming_odd_sqrt_private_add(builder, root, high, carry_in=b)
        _consuming_odd_sqrt_private__add_leading_one(builder, high)
        builder.cx(b, _consuming_odd_sqrt_private__arr(high))
        _consuming_odd_sqrt_private__low_remainder_xor(builder, Q, W[:4])
        builder.free(_consuming_odd_sqrt_private__arr(W[:4]))
        if Q != norm[10:] or W[4:] != norm[:10]:
            raise AssertionError('In-place output layout changed')
        return dict(root=Q, residual=W[4:])

    def _consuming_odd_sqrt_private_inverse(builder, norm):
        norm = list(norm)
        if len(norm) != 22 or len(set(norm)) != 22:
            raise ValueError('Expected22 distinct input wires')
        Q = norm[10:]
        W = list(builder.alloc_qubits(4)) + norm[:10]
        _consuming_odd_sqrt_private__low_remainder_xor(builder, Q, W[:4])
        b = Q[0]
        root = Q[1:]
        high = W[1:]
        builder.cx(b, _consuming_odd_sqrt_private__arr(high))
        _consuming_odd_sqrt_private__add_leading_one(builder, high, inverse=True)
        _consuming_odd_sqrt_private_add(builder, root, high, carry_in=b, subtract=True)
        builder.cx(b, _consuming_odd_sqrt_private__arr(high))
        builder.x(b)
        remainder = W + [b]
        for j in reversed(range(1, 13)):
            pair = remainder[:2]
            if j == 1:
                b = True
                older = []
            else:
                b = root[0]
                older = root[1:]
            _consuming_odd_sqrt_private__root_step(builder, remainder, older, b, initial=j == 1, inverse=True)
            if j == 1:
                remainder = remainder[2:]
            else:
                remainder = remainder[2:] + [b]
                builder.x(b)
                root = older
            if j >= 11:
                builder.free(_consuming_odd_sqrt_private__arr(pair))
            elif pair != norm[20 - 2 * j:22 - 2 * j]:
                raise AssertionError('Restored inputpair layout changed')
        if remainder != norm[20:] or root:
            raise AssertionError('Initial remainder layout changed')
        builder.cx(norm[20], norm[21])
        builder.x(norm[20])
        return norm

def _initialize_common():
    global _common_ENGINE, _common_HERE, _common_INTEGRATED_ROOT, _common_KICKMIX, _common_MODEL, _common_MODEL_PATH, _common_MODEL_SHA, _common_NARROW, _common_Path, _common_TESTS, _common_TOOLING, _common__IntegratedPath, _common___file__, _common___name__, _common_array, _common_cb, _common_checked_json, _common_current_gate, _common_hashlib, _common_json, _common_km, _common_os, _common_plan_from_json, _common_sys, _common_verify_gate_sources, _common_with_registers
    _common__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate01/common.py', False).Path
    _common_INTEGRATED_ROOT = _common__IntegratedPath(_common___file__).resolve().parents[5]
    _common_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate01/common.py', False).Path
    _common_os = _import_component('os', 'work/c10/narrow/native/candidate01/common.py', True)
    _common_sys = _import_component('sys', 'work/c10/narrow/native/candidate01/common.py', True)
    _common_json = _import_component('json', 'work/c10/narrow/native/candidate01/common.py', True)
    _common_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate01/common.py', True)
    _common_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _common_os.environ['OMP_NUM_THREADS'] = '1'
    _common_HERE = _common_Path(_common___file__).resolve().parent
    _common_NARROW = _common_HERE.parents[1]
    _common_ENGINE = _common_NARROW / 'checkpoint002/cleanroom/baseline_stage97/engine'
    _common_TESTS = _common_NARROW / 'checkpoint002/cleanroom/baseline_stage97/tests'
    _common_TOOLING = _common_NARROW / 'checkpoint002/cleanroom/baseline_stage97/tooling'
    _common_KICKMIX = _common_NARROW / 'base/official/kickmix'
    _common_sys.path[:0] = [str(_common_KICKMIX), str(_common_ENGINE), str(_common_TESTS), str(_common_TOOLING), str(_common_NARROW / 'checkpoint002/cleanroom/odd_sqrt')]
    _common_km = _import_component('kickmix', 'work/c10/narrow/native/candidate01/common.py', False)
    _common_cb = _import_component('codebook', 'work/c10/narrow/native/candidate01/common.py', False)
    _common_MODEL_PATH = _common_NARROW / 'research/recompute_root/models/phasefit_z1_K7_G4_m37_virtual_quadS2_36_12c0.json'
    _common_MODEL_SHA = '24fff823faa911afe93d02afc3ded0bbd156a210a85f1265c989a087f8fd1219'
    _common_MODEL = _json_loads(_read_text(_common_MODEL_PATH))

    def _common_checked_json(path, sha):
        path = _common_Path(path)
        raw = _read_bytes(path)
        actual = _common_hashlib.sha256(raw).hexdigest()
        pass
        return _json_loads(raw)

    def _common_plan_from_json(p):
        return _common_cb.QuadraticCodePlan(p['width'], p['constant'], p['linear'], tuple((tuple(x) for x in p['edges'])), tuple((tuple(x) for x in p['products'])), p['product_linear'])

    def _common_array(wires):
        return _common_km.array(list(wires))

    def _common_with_registers(circuit, registers):
        """Declare input metadata without making reusable builder owners permanent.

Kickmix's create_quantum_register reserves permanent builder-owned wires,
which cannot be freed during an in-place consuming computation. Allocate
input wires normally and attach their ORIGINAL physical register identities
to the emitted own circuit. Metadata adds no gates and no new qubits.
"""
        generated_text = _import_component('branch_prover', 'work/c10/narrow/native/candidate01/common.py', False).generated_text
        assert circuit.num_registers == 0, 'Register metadata was already attached.'
        declarations = []
        all_wires = []
        for index, (name, wires) in enumerate(registers.items()):
            wires = list(wires)
            assert all((isinstance(q, _common_km.q) for q in wires))
            all_wires.extend(wires)
            declarations.extend((f'APPEND_TO_REGISTER {q} r{index}' for q in wires))
            declarations.append(f'REGISTER r{index} {_common_json.dumps(name)}')
        assert len(set(all_wires)) == len(all_wires)
        result = _common_km.Circuit('\n'.join(declarations) + '\n' + generated_text(circuit))
        assert result.num_qubits == circuit.num_qubits
        assert list(result.register_data) == list(registers)
        for name, wires in registers.items():
            assert list(result.register_data[name]) == list(wires)
        return result

    def _common_current_gate():
        return _common_checked_json(_common_NARROW / 'research/lifecycle_schedule/post008_gate_v4.json', '0e49c0e309c3a816d9e0512d5d815de44a1fc5a1de3b5eff866330c6017954b3')

    def _common_verify_gate_sources():
        gate = _common_current_gate()
        pass
        return gate

def _initialize_divider():
    global _divider_ACTIVE, _divider_CENTRES, _divider_CONTROLS, _divider_DividerToken, _divider_FEED3, _divider_FEED4, _divider_Fraction, _divider_HIGH, _divider_INTEGRATED_ROOT, _divider_LOCAL, _divider_NARROW, _divider_OLDQ0, _divider_OLDQ1, _divider_P13, _divider_P14, _divider_THRESHOLDS, _divider__IntegratedPath, _divider___file__, _divider___name__, _divider__affine_control, _divider__compose, _divider__dirty, _divider__erase, _divider__erase_polynomial, _divider__feature, _divider__feed_carry, _divider__feed_erase, _divider__feed_variables, _divider__frame, _divider__leading_offset, _divider__route, _divider__sigma25_frame, _divider__slots, _divider__threshold, _divider_annotations, _divider_array, _divider_cb, _divider_checked_json, _divider_cleanup_divider, _divider_cleanup_u12, _divider_compute_divider, _divider_compute_phase_cleanup, _divider_contextmanager, _divider_dataclass, _divider_field, _divider_forward_add, _divider_initialize_u12, _divider_inverse_add, _divider_km, _divider_phase_endpoint, _divider_plan_from_json, _divider_xor_polynomial
    _divider_contextmanager = _import_component('contextlib', 'work/c10/narrow/native/candidate01/divider.py', False).contextmanager
    _divider_dataclass = _import_component('dataclasses', 'work/c10/narrow/native/candidate01/divider.py', False).dataclass
    _divider_field = _import_component('dataclasses', 'work/c10/narrow/native/candidate01/divider.py', False).field
    _divider_Fraction = _import_component('fractions', 'work/c10/narrow/native/candidate01/divider.py', False).Fraction
    _divider_cb = _import_component('common', 'work/c10/narrow/native/candidate01/divider.py', False).cb
    _divider_NARROW = _import_component('common', 'work/c10/narrow/native/candidate01/divider.py', False).NARROW
    _divider_checked_json = _import_component('common', 'work/c10/narrow/native/candidate01/divider.py', False).checked_json
    _divider_plan_from_json = _import_component('common', 'work/c10/narrow/native/candidate01/divider.py', False).plan_from_json
    _divider_array = _import_component('common', 'work/c10/narrow/native/candidate01/divider.py', False).array
    _divider_forward_add = _import_component('paired_arithmetic', 'work/c10/narrow/native/candidate01/divider.py', False).forward_add
    _divider_inverse_add = _import_component('paired_arithmetic', 'work/c10/narrow/native/candidate01/divider.py', False).inverse_add
    _divider_xor_polynomial = _import_component('quadratic_terms', 'work/c10/narrow/native/candidate01/divider.py', False).xor_polynomial
    _divider__erase_polynomial = _import_component('cyclic_phase', 'work/c10/narrow/native/candidate01/divider.py', False)._erase_polynomial
    _divider_LOCAL = _divider_checked_json(_divider_NARROW / 'research/recompute_root/initializer_u12/local_algebra.json', '978c2adafd8d3355558a5e672982623372d459dec610273e1e43847681cc4c14')
    _divider_P13 = _divider_cb.factor_polynomial(5, False, 13, set())
    _divider_P14 = _divider_cb.factor_polynomial(5, True, 23, {(0, 2), (0, 3), (2, 3)})
    _divider_OLDQ0 = _divider_cb.factor_polynomial(4, True, 7, set())
    _divider_OLDQ1 = _divider_cb.factor_polynomial(4, True, 12, {(0, 1), (0, 2), (1, 2)})
    _divider_HIGH = _divider_cb.factor_polynomial(6, False, 39, {(3, 4), (3, 5), (4, 5)})
    _divider_FEED4 = _divider_cb.factor_polynomial(4, False, 3, {(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)})
    _divider_FEED3 = _divider_cb.factor_polynomial(3, False, 3, {(0, 1), (1, 2)})
    assert _divider_FEED4.and_count == _divider_FEED3.and_count == 1

    def _divider__compose(plan, mapping, width):
        constant = int(plan.constant)
        linear = 0
        edges = set()
        for i in _divider_cb.bits(plan.linear):
            constant ^= mapping[i][0]
            linear ^= mapping[i][1]
        for i, j in plan.edges:
            ca, ma = mapping[i]
            cc, mc = mapping[j]
            constant ^= ca * cc
            if ca:
                linear ^= mc
            if cc:
                linear ^= ma
            for a in _divider_cb.bits(ma):
                for b in _divider_cb.bits(mc):
                    if a == b:
                        linear ^= 1 << a
                    else:
                        edge = tuple(sorted((a, b)))
                        if edge in edges:
                            edges.remove(edge)
                        else:
                            edges.add(edge)
        return _divider_cb.factor_polynomial(width, constant, linear, edges)

    def _divider__erase(builder, target, variables, plan):
        assert target not in variables
        m = builder.alloc_bits(1)[0]
        builder.hmr(target, m)
        _divider_cb.emit_phase(builder, variables, m, plan)
        builder.free(m)
        builder.free(target)

    def _divider_initialize_u12(builder, v, P, u):
        """24 CCX forward; b13 and b14 become classical measurements, fully paid."""
        P = list(P)
        carry = list(builder.alloc_qubits(2))
        for q in (v[0], P[13], P[12]):
            builder.cx(q, u[0])
        env = {'v0': v[0], 'v1': v[1], 'p12': P[12], 'p13': P[13], 'p14': P[14], 'u0': u[0], 'u1': u[1], 'q0': carry[0], 'q1': carry[1]}
        for item in _divider_LOCAL['best_low']['plans']:
            _divider_cb.emit_xor(builder, [env[name] for name in item['inputs']], env[item['output']], _divider_plan_from_json(item['plan']))
        variables = [v[0], v[1], P[12], u[0], u[1]]
        _divider__erase(builder, P[13], variables, _divider_P13)
        _divider__erase(builder, P[14], variables, _divider_P14)
        P[13] = None
        P[14] = None
        for i in range(2, 13):
            nextcarry = list(builder.alloc_qubits(2 if i < 12 else 1))
            if i < 12:
                aq = v[i]
                bq = v[i - 1]
                builder.x(aq)
                builder.x(bq)
            else:
                aq = u[13]
                bq = v[11]
                builder.x(bq)
            q0, q1 = carry
            builder.x(u[i])
            for q in (aq, bq, q0):
                builder.cx(q, u[i])
            for which, target in enumerate(nextcarry):
                _divider_cb.emit_xor(builder, [aq, bq, q0, q1], target, _divider_plan_from_json(_divider_LOCAL['high_forward'][f'next{which}']['plan']))
            variables = [aq, bq, u[i], nextcarry[0]]
            _divider__erase(builder, q0, variables, _divider_OLDQ0)
            _divider__erase(builder, q1, variables, _divider_OLDQ1)
            if i < 12:
                builder.x(aq)
            builder.x(bq)
            carry = nextcarry
        builder.cx(carry[0], u[13])
        builder.cx(u[13], carry[0])
        builder.free(carry[0])
        return P

    def _divider_cleanup_u12(builder, v, P, u):
        """One CCX; reconstruct product on current owners and HMR all u bits."""
        P = list(P)
        P[13], P[14] = list(builder.alloc_qubits(2))
        variables = [v[0], v[1], P[12], u[0], u[1]]
        _divider_cb.emit_xor(builder, variables, P[13], _divider_P13)
        _divider_cb.emit_xor(builder, variables, P[14], _divider_P14)

        def aa(i):
            return (1, 1 << i) if 0 <= i < 12 else (0, 0)

        def bb(i):
            return (1, 0) if i in (0, 13) else (1, 1 << i - 1)
        for i in reversed(range(4, 14)):
            phase = _divider__compose(_divider_HIGH, [aa(i), bb(i), aa(i - 2), aa(i - 3), aa(i - 1), (0, 1 << 12)], 13)
            _divider__erase(builder, u[i], list(v) + [u[i - 1]], phase)
        for i in reversed(range(4)):
            item = _divider_LOCAL['low_cleanup'][i]
            env = {f'v{j}': v[j] for j in range(i + 1)}
            env.update(p12=P[12], p13=P[13], p14=P[14])
            env.update({f'u{j}': u[j] for j in range(i)})
            _divider__erase(builder, u[i], [env[name] for name in item['inputs']], _divider_plan_from_json(item['plan']))
        return P

    def _divider__frame(builder, sign, target):
        for q in target:
            builder.x(q)
            builder.cx(sign, q)

    def _divider__leading_offset(builder, target, inverse=False):
        if inverse:
            builder.x(target[-2])
            builder.cx(target[-2], target[-1])
        else:
            builder.cx(target[-2], target[-1])
            builder.x(target[-2])

    def _divider__feed_variables(v, low, cur, sign):
        return ([v[0], low, sign], _divider_FEED3) if cur is None else ([v[0], low, cur, sign], _divider_FEED4)

    def _divider__feed_carry(builder, v, low, cur, sign):
        variables, plan = _divider__feed_variables(v, low, cur, sign)
        carry = builder.alloc_qubits(1)[0]
        _divider_cb.emit_xor(builder, variables, carry, plan)
        return carry

    def _divider__feed_erase(builder, carry, v, low, cur, sign):
        variables, plan = _divider__feed_variables(v, low, cur, sign)
        _divider__erase(builder, carry, variables, plan)

    @_divider_dataclass
    class _divider_DividerToken:
        v: list
        P: list
        flags: list
        u: list
        initial_u: tuple
        history: dict = _divider_field(default_factory=dict)
        rows: list = _divider_field(default_factory=list)
        consumed: bool = False

    def _divider__dirty(token):
        forbidden = set(token.v + token.u)
        wires = token.flags + [q for q in token.P if q is not None] + list(token.history.values())
        return list(dict.fromkeys((q for q in wires if q not in forbidden)))

    def _divider_compute_divider(builder, v12, P15, flags4):
        """Compute the m37 balanced endpoint, preserving every quotient owner."""
        v = list(v12)
        P = list(P15)
        flags = list(flags4)
        assert len(v) == 12 and len(P) == 15 and (len(flags) == 4)
        assert len(set(v + P + flags)) == 31
        assert builder.num_allocated_qubits == 31, 'Unpriced retained owner before divider'
        u = list(builder.alloc_qubits(14))
        initial_u = tuple(u)
        P = _divider_initialize_u12(builder, v, P, u)
        token = _divider_DividerToken(v, P, flags, u, initial_u)
        assert builder.num_allocated_qubits == 43
        for j in range(12, 36):
            u = token.u
            if j <= 24:
                prev = token.P[24 - j]
                cur = token.P[23 - j] if j < 24 else None
                assert prev is not None
                sign = u[-1]
                target = u[:-1]
                carry = _divider__feed_carry(builder, v, prev, cur, sign)
                _divider__frame(builder, sign, target)
                debt = _divider_forward_add(builder, v[1:], target, carry_in=carry)
                _divider__leading_offset(builder, target)
                _divider__frame(builder, sign, target)
                builder.cx(v[0], prev)
                builder.cx(sign, prev)
                if cur is not None:
                    builder.cx(cur, prev)
                _divider__feed_erase(builder, carry, v, prev, cur, sign)
                token.u = [prev] + target
                token.history[j] = sign
                token.P[24 - j] = None
                k = 0
            else:
                k = j - 26 if j >= 28 else 0
                u = [u[-1]] + u[:-1]
                sign = u[0]
                target = u[k + 1:]
                _divider__frame(builder, sign, target)
                debt = _divider_forward_add(builder, v[k + 1:], target, carry_in=v[k])
                _divider__leading_offset(builder, target)
                _divider__frame(builder, sign, target)
                builder.cx(v[0], u[0])
                token.u = u
            token.rows.append((j, k, debt))
            assert builder.num_allocated_qubits == 43, (j, builder.num_allocated_qubits)
        assert sorted(token.history) == list(range(12, 25)) and all((q is None for q in token.P))
        return token

    def _divider_cleanup_divider(builder, token):
        """Reverse all rows, pay every CarryDebt, then clear direct u12."""
        assert not token.consumed
        token.consumed = True
        v = token.v
        for j, k, debt in reversed(token.rows):
            u = token.u
            if j <= 24:
                low = u[0]
                target = u[1:]
                sign = token.history[j]
                cur = token.P[23 - j] if j < 24 else None
                if j < 24:
                    assert cur is not None
                carry = _divider__feed_carry(builder, v, low, cur, sign)
                _divider__frame(builder, sign, target)
                _divider__leading_offset(builder, target, inverse=True)
                _divider_inverse_add(builder, v[1:], target, debt, carry_in=carry, dirty_wires=_divider__dirty(token))
                _divider__frame(builder, sign, target)
                _divider__feed_erase(builder, carry, v, low, cur, sign)
                if cur is not None:
                    builder.cx(cur, low)
                builder.cx(sign, low)
                builder.cx(v[0], low)
                token.P[24 - j] = low
                token.u = target + [sign]
                del token.history[j]
            else:
                builder.cx(v[0], u[0])
                sign = u[0]
                target = u[k + 1:]
                _divider__frame(builder, sign, target)
                _divider__leading_offset(builder, target, inverse=True)
                _divider_inverse_add(builder, v[k + 1:], target, debt, carry_in=v[k], dirty_wires=_divider__dirty(token))
                _divider__frame(builder, sign, target)
                token.u = u[1:] + u[:1]
            assert debt.consumed and (not debt.measurements)
            assert builder.num_allocated_qubits == 43
        assert tuple(token.u) == token.initial_u and (not token.history)
        token.P = _divider_cleanup_u12(builder, v, token.P, token.u)
        assert builder.num_allocated_qubits == 31 and all((q is not None for q in token.P))
        return list(token.P)
    _divider_CENTRES = (0, -2, -6, 0, -1)
    _divider_ACTIVE = (30, 6, 27, 3, 17, 9, 18, 10, 23, 15, 20)
    _divider_CONTROLS = ((2, 4, 8), (0, 4, 16), (0, 2, 4, 16), (0, 1, 4, 8), (0, 1))
    _divider_THRESHOLDS = {1: (1, 2, 4, 8, 16, 3, 5, 9, 17), 2: (2, 4, 8, 16), 3: (4, 8, 3, 17), 4: (4, 8), 5: (8, 16, 32, 5, 17), 6: (8, 16, 32), 7: (8, 17), 8: (8,), 9: (9, 10), 10: (32,)}

    @_divider_contextmanager
    def _divider__affine_control(builder, variables, terms):
        linear = [t.bit_length() - 1 for t in terms if t]
        assert linear and all((t == 0 or t.bit_count() == 1 for t in terms))
        pivot = variables[linear[0]]
        for i in linear[1:]:
            builder.cx(variables[i], pivot)
        if 0 in terms:
            builder.x(pivot)
        try:
            yield pivot
        finally:
            if 0 in terms:
                builder.x(pivot)
            for i in reversed(linear[1:]):
                builder.cx(variables[i], pivot)

    @_divider_contextmanager
    def _divider__threshold(builder, variables, t):
        terms = _divider_THRESHOLDS[t]
        if max((x.bit_count() for x in terms)) <= 1:
            with _divider__affine_control(builder, variables, terms) as q:
                yield q
        else:
            q = builder.alloc_qubits(1)[0]
            _divider_xor_polynomial(builder, variables, q, terms)
            try:
                yield q
            finally:
                _divider__erase_polynomial(builder, q, variables, terms)

    def _divider__route(builder, word, variables, inverse=False):
        stages = list(range(5))
        if inverse:
            stages.reverse()
        for stage in stages:
            with _divider__affine_control(builder, variables, _divider_CONTROLS[stage]) as q:
                for i in range(27):
                    k = (_divider_CENTRES[stage] - i) % 27
                    if i < k:
                        builder.cswap(q, word[i], word[k])

    def _divider__slots():
        word = list(range(27))
        for stage, centre in enumerate(_divider_CENTRES):
            if _divider_ACTIVE[0] >> stage & 1:
                word = [word[(centre - i) % 27] for i in range(27)]
        inverse = {v: i for i, v in enumerate(word)}
        return [inverse[i] for i in range(27)]

    def _divider__feature(builder, control, data, turns):
        turns = _divider_Fraction(turns) % 1
        if turns == _divider_Fraction(1, 2):
            builder.cz(control, data)
        elif turns in (_divider_Fraction(1, 4), _divider_Fraction(3, 4)):
            sign = 1 if turns == _divider_Fraction(1, 4) else -1
            builder.z_pow(control, _divider_Fraction(sign, 4))
            builder.z_pow(data, _divider_Fraction(sign, 4))
            builder.cx(control, data)
            builder.z_pow(data, _divider_Fraction(-sign, 4))
            builder.cx(control, data)
        else:
            q = builder.alloc_qubits(1)[0]
            builder.ccx(control, data, q)
            builder.z_pow(q, 2 * turns)
            builder.del_and(control, data, q)
            builder.free(q)

    def _divider__sigma25_frame(builder, v, u, inverse=False):
        for q in (v[10], v[0], v[1]):
            builder.cx(q, u[10])
        builder.cx(u[8], u[9])
        builder.cx(v[1], v[0])
        builder.ccx(u[9], v[0], u[10])
        builder.cx(v[1], v[0])
        builder.cx(u[8], u[9])

    def _divider_phase_endpoint(builder, token):
        """146 CCX-equivalents +4 T +34 arbitrary rotations, N27 cyclic model."""
        v, u, flags = (token.v, token.u, token.flags)
        assert builder.num_allocated_qubits == 43
        _divider__sigma25_frame(builder, v, u)
        for q in u[:9]:
            builder.cx(v[0], q)
        builder.cx(v[1], u[9])
        signs = {**token.history, 25: u[10], 26: u[9], 36: u[13]}
        signs.update({j: u[35 - j] for j in range(27, 36)})
        for q in signs.values():
            builder.x(q)
        ones = list(builder.alloc_qubits(2))
        builder.x(_divider_array(ones))
        word = [ones[0]] + [signs[37 - i] for i in range(1, 26)] + [ones[1]]
        assert len(set(word)) == 27
        p, c = list(builder.alloc_qubits(2))
        _divider_xor_polynomial(builder, flags, p, (6, 10))
        _divider_xor_polynomial(builder, flags, c, (10,))
        variables = flags + [p, c]
        _divider__route(builder, word, variables)
        slots = [word[i] for i in _divider__slots()]
        factor = 1 << 27
        for i, q in enumerate(slots):
            units = (1 << i) + (factor if i == 0 else 0)
            builder.z_pow(q, _divider_Fraction(2 * units, 1 << 37))
        for j in range(10):
            angle = _divider_Fraction(factor * (1 << j), 1 << 37)
            if j == 0:
                with _divider__threshold(builder, variables, 1) as q:
                    builder.x(q)
                    builder.z_pow(q, -2 * angle)
                    builder.x(q)
            elif j == 9:
                builder.z_pow(c, 2 * angle)
            else:
                with _divider__threshold(builder, variables, j + 1) as q:
                    _divider__feature(builder, q, slots[j], angle)
        _divider__route(builder, word, variables, inverse=True)
        _divider__erase_polynomial(builder, c, flags, (10,))
        _divider__erase_polynomial(builder, p, flags, (6, 10))
        builder.x(_divider_array(ones))
        builder.free(_divider_array(ones))
        for q in signs.values():
            builder.x(q)
        builder.cx(v[1], u[9])
        for q in u[:9]:
            builder.cx(v[0], q)
        _divider__sigma25_frame(builder, v, u, inverse=True)
        assert builder.num_allocated_qubits == 43

    def _divider_compute_phase_cleanup(builder, v12, P15, flags4):
        token = _divider_compute_divider(builder, v12, P15, flags4)
        _divider_phase_endpoint(builder, token)
        return _divider_cleanup_divider(builder, token)

def _initialize_generate():
    global _generate_ENGINE, _generate_HERE, _generate_INTEGRATED_ROOT, _generate_KICKMIX, _generate_MODEL, _generate_MODEL_PATH, _generate_MODEL_SHA, _generate_NARROW, _generate_Path, _generate_Program, _generate_TESTS, _generate_TOOLING, _generate__IntegratedPath, _generate___file__, _generate___name__, _generate_argparse, _generate_array, _generate_build, _generate_cb, _generate_checked_json, _generate_consuming_root, _generate_current_gate, _generate_decode_root, _generate_exact_expectation, _generate_generated_text, _generate_hashlib, _generate_json, _generate_km, _generate_main, _generate_normalization, _generate_os, _generate_plan_from_json, _generate_restore_input_layout, _generate_snapshot, _generate_sys, _generate_time, _generate_verify_gate_sources, _generate_with_registers
    _import_star('_generate_', _import_component('common', 'work/c10/narrow/native/candidate01/generate.py', False))
    _generate_argparse = _import_component('argparse', 'work/c10/narrow/native/candidate01/generate.py', True)
    _generate_time = _import_component('time', 'work/c10/narrow/native/candidate01/generate.py', True)
    _generate_normalization = _import_component('normalization', 'work/c10/narrow/native/candidate01/generate.py', True)
    _generate_consuming_root = _import_component('consuming_odd_sqrt', 'work/c10/narrow/native/candidate01/generate.py', False)
    _generate_decode_root = _import_component('root_decode', 'work/c10/narrow/native/candidate01/generate.py', False).decode_root
    _generate_restore_input_layout = _import_component('layout', 'work/c10/narrow/native/candidate01/generate.py', False).restore_input_layout
    _generate_generated_text = _import_component('branch_prover', 'work/c10/narrow/native/candidate01/generate.py', False).generated_text
    _generate_Program = _import_component('branch_prover', 'work/c10/narrow/native/candidate01/generate.py', False).Program
    _generate_exact_expectation = _import_component('fourier_resource_expectation', 'work/c10/narrow/native/candidate01/generate.py', False).exact_expectation

    def _generate_snapshot(builder, name, owners):
        circuit = builder.finish_circuit()
        text = _generate_generated_text(circuit)
        return dict(name=name, live_qubits=builder.num_allocated_qubits, peak_so_far=circuit.num_qubits, instruction_cut=len(_generate_Program(text).operations), owners={k: [str(q) for q in v] for k, v in owners.items()}, cumulative_expected=_generate_exact_expectation(text)['mean_numeric'])

    def _generate_build():
        tables = _import_component('tables', 'work/c10/narrow/native/candidate01/generate.py', True)
        divider = _import_component('divider', 'work/c10/narrow/native/candidate01/generate.py', True)
        lifecycle = _import_component('lifecycle', 'work/c10/narrow/native/candidate01/generate.py', True)
        gate = _generate_verify_gate_sources()
        builder = _generate_km.CircuitBuilder()
        builder.set_max_qubits(49)
        original = list(builder.alloc_qubits(22))
        flags = list(builder.alloc_qubits(4))
        _generate_normalization.forward(builder, original, flags)
        cuts = [_generate_snapshot(builder, 'normalized', dict(n=original, flags=flags))]
        root = _generate_consuming_root.forward(builder, original)
        v = list(root['root'])
        h = list(root['residual'])
        cuts.append(_generate_snapshot(builder, 'consumed_root', dict(v=v, h=h, flags=flags)))
        v, h = lifecycle.emit_body(builder, v, h, flags, tables, divider, _generate_decode_root)
        assert len(set(v + h + flags)) == 26 and builder.num_allocated_qubits == 26
        cuts.append(_generate_snapshot(builder, 'body_restored', dict(v=v, h=h, flags=flags)))
        norm = h + v
        _generate_consuming_root.inverse(builder, norm)
        cuts.append(_generate_snapshot(builder, 'root_restored', dict(n=norm, flags=flags)))
        _generate_normalization.inverse(builder, norm, flags)
        builder.free(_generate_array(flags))
        cuts.append(_generate_snapshot(builder, 'logical_input_restored', dict(x=norm)))
        layout = _generate_restore_input_layout(builder, norm, original, 49)
        circuit = _generate_with_registers(builder.finish_circuit(), dict(x=original))
        text = _generate_generated_text(circuit)
        resources = _generate_exact_expectation(text)
        actual = resources['mean_numeric']
        expected = gate['primary']
        assert circuit.num_qubits == 49, ('width_gate', circuit.num_qubits)
        assert actual['toffoli_like'] == expected['Toffolis_expected'], ('Toffoli_gate', actual, expected)
        assert actual['T'] == expected['T'] and actual['generic_rotations'] == expected['R'], ('phase_gate', actual)
        assert list(circuit.register_data) == ['x'] and list(circuit.register_data['x']) == original
        report = dict(status='EMITTED_NATIVE_CANDIDATE_NOT_YET_PROVED_OR_OFFICIALLY_VERIFIED', Q=circuit.num_qubits, exact_native_expectation=resources, paper_rotation_charge=expected['rotation_charge'], paper_cost=expected['paper_cost'], model_sha256=_generate_MODEL_SHA, gate_sha256=_generate_hashlib.sha256(_read_bytes(_generate_NARROW / 'research/lifecycle_schedule/post008_gate_v4.json')).hexdigest(), cuts=cuts, final_Clifford_layout_swaps=layout, official_verifier=False, no_submission=True)
        return (circuit, text, report)

    def _generate_main():
        ap = _generate_argparse.ArgumentParser()
        ap.add_argument('--output', type=_generate_Path, default=_generate_HERE / 'candidate01.kmb')
        args = ap.parse_args()
        started = _generate_time.monotonic()
        circuit, text, report = _generate_build()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        circuit.to_file(str(args.output), format='kmb')
        args.output.with_suffix('.kmx').write_text(text)
        report.update(kmb_sha256=_generate_hashlib.sha256(_read_bytes(args.output)).hexdigest(), bytes=args.output.stat().st_size, emission_seconds=_generate_time.monotonic() - started, native_sources={p.name: _generate_hashlib.sha256(_read_bytes(p)).hexdigest() for p in sorted(_generate_HERE.glob('*.py'))})
        args.output.with_suffix('.build.json').write_text(_generate_json.dumps(report, indent=2) + '\n')
        print(_generate_json.dumps(report, indent=2), flush=True)
    if _generate___name__ == '__main__':
        _generate_main()

def _initialize_layout():
    global _layout_INTEGRATED_ROOT, _layout__IntegratedPath, _layout___file__, _layout___name__, _layout_array, _layout_km, _layout_restore_input_layout
    _layout_array = _import_component('common', 'work/c10/narrow/native/candidate01/layout.py', False).array

    def _layout_restore_input_layout(builder, current, original, cap=49):
        current = list(current)
        original = list(original)
        assert len(current) == len(original) == 22
        assert len(set(current)) == len(set(original)) == 22
        assert builder.num_allocated_qubits == 22
        spare = list(builder.alloc_qubits(cap - 22))
        all_wires = set(current + spare)
        assert len(all_wires) == cap and set(original) <= all_wires
        swaps = []
        for bit, target in enumerate(original):
            source = current[bit]
            if source == target:
                continue
            builder.swap(source, target)
            swaps.append((str(source), str(target)))
            for other in range(bit + 1, 22):
                if current[other] == target:
                    current[other] = source
            current[bit] = target
        assert current == original
        builder.free(_layout_array(sorted(all_wires - set(original), key=str)))
        assert builder.num_allocated_qubits == 22
        return swaps

def _initialize_lifecycle():
    global _lifecycle_AR_SHA, _lifecycle_CUT_HOOK, _lifecycle_ENGINE, _lifecycle_H3_CURRENT, _lifecycle_H3_INITIAL, _lifecycle_H4_PLAN, _lifecycle_INTEGRATED_ROOT, _lifecycle_METADATA, _lifecycle_MODEL, _lifecycle_NARROW, _lifecycle_ProductToken, _lifecycle_SEED, _lifecycle_SeedToken, _lifecycle_SimpleNamespace, _lifecycle__IntegratedPath, _lifecycle___file__, _lifecycle___name__, _lifecycle__clear_coefficient_carry, _lifecycle__clear_product_carry, _lifecycle__coefficient_carry, _lifecycle__erase, _lifecycle__literal_inputs, _lifecycle__mark, _lifecycle__merge_debts, _lifecycle__product_carry, _lifecycle__spec, _lifecycle_annotations, _lifecycle_ar, _lifecycle_array, _lifecycle_cb, _lifecycle_checked_json, _lifecycle_coefficient_forward, _lifecycle_coefficient_inverse, _lifecycle_dataclass, _lifecycle_emit_body, _lifecycle_erase_high_H, _lifecycle_hashlib, _lifecycle_importlib, _lifecycle_km, _lifecycle_merge_coefficient_transcripts, _lifecycle_plan_from_json, _lifecycle_prepare_H3_current, _lifecycle_prepare_H3_initial, _lifecycle_prepare_H4, _lifecycle_product_ar, _lifecycle_product_forward, _lifecycle_product_inverse, _lifecycle_root_R_frame, _lifecycle_seed_cleanup, _lifecycle_seed_forward, _lifecycle_seed_root_frame, _lifecycle_sys
    _lifecycle_dataclass = _import_component('dataclasses', 'work/c10/narrow/native/candidate01/lifecycle.py', False).dataclass
    _lifecycle_SimpleNamespace = _import_component('types', 'work/c10/narrow/native/candidate01/lifecycle.py', False).SimpleNamespace
    _lifecycle_sys = _import_component('sys', 'work/c10/narrow/native/candidate01/lifecycle.py', True)
    _lifecycle_km = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).km
    _lifecycle_cb = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).cb
    _lifecycle_NARROW = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).NARROW
    _lifecycle_ENGINE = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).ENGINE
    _lifecycle_checked_json = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).checked_json
    _lifecycle_plan_from_json = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).plan_from_json
    _lifecycle_array = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).array
    _lifecycle_ar = _import_component('paired_arithmetic', 'work/c10/narrow/native/candidate01/lifecycle.py', False)
    _lifecycle_SEED = _lifecycle_checked_json(_lifecycle_NARROW / 'research/lifecycle_schedule/seed_phase_cleanup_conditional.json', '71f0fcb5645fd32cf128c310c5e5cba406d1ad33c02b4f37e51869ee845ed466')['certificate']
    _lifecycle_METADATA = _lifecycle_checked_json(_lifecycle_NARROW / 'research/lifecycle_schedule/slope_h3_h4_retirement_v3.json', '1e5afe12bc0a9005bb3705afdc564f30c0861d99970d31f71d9b7c2556e17721')['certificate']
    _lifecycle_H3_INITIAL = _lifecycle_plan_from_json(_lifecycle_METADATA['H3_initial']['plan'])
    _lifecycle_H3_CURRENT = _lifecycle_plan_from_json(_lifecycle_METADATA['H3_current']['plan'])
    _lifecycle_H4_PLAN = _lifecycle_plan_from_json(_lifecycle_METADATA['H4']['plan'])

    def _lifecycle__literal_inputs(source, target, carry_in, signed_source):
        source, target = (list(source), list(target))
        width = len(target)
        source = source[:width]
        if any((q is not False and (not isinstance(q, _lifecycle_km.q)) for q in source)):
            raise ValueError('Product source contains a nonwire/nonzero constant.')
        real = [q for q in source if isinstance(q, _lifecycle_km.q)]
        if len(set(real + target)) != len(real) + len(target):
            raise ValueError('Product data wires alias.')
        if isinstance(carry_in, _lifecycle_km.q) and carry_in in real + target:
            raise ValueError('Product carry aliases data.')
        if carry_in is not False and (not isinstance(carry_in, _lifecycle_km.q)):
            raise ValueError('Invalid product carry.')
        preserve = real[-1] if signed_source and real else None
        source += [preserve if preserve is not None else False] * (width - len(source))
        return (source, target, preserve)
    _lifecycle__spec = _spec('_candidate01_product_paired', _lifecycle_ENGINE / 'paired_arithmetic.py')
    _lifecycle_product_ar = _new_module(_lifecycle__spec)
    _lifecycle_sys.modules[_lifecycle__spec.name] = _lifecycle_product_ar
    _lifecycle__spec.loader.exec_module(_lifecycle_product_ar)
    _lifecycle_product_ar._inputs = _lifecycle__literal_inputs

    def _lifecycle__erase(builder, target, variables, plan):
        outcome = builder.alloc_bits(1)[0]
        builder.hmr(target, outcome)
        _lifecycle_cb.emit_phase(builder, list(variables), outcome, plan)
        builder.free(outcome)
        builder.free(target)

    def _lifecycle_root_R_frame(builder, v, *, inverse=False):
        operations = [('cx', v[7], v[8]), ('cx', v[7], v[10]), ('ccx', v[6], v[10], v[8]), ('cx', v[7], v[10])]
        if inverse:
            operations.reverse()
        for name, *wires in operations:
            getattr(builder, name)(*wires)

    def _lifecycle_seed_root_frame(builder, v, *, inverse=False):
        operations = [('cx', v[2], v[0]), ('cx', v[2], v[1]), ('cx', v[2], v[3]), ('ccx', v[0], v[1], v[3]), ('cx', v[1], v[0])]
        if inverse:
            operations.reverse()
        for name, *wires in operations:
            getattr(builder, name)(*wires)

    def _lifecycle_prepare_H3_initial(builder, v, A, Hlow):
        q = builder.alloc_qubits(1)[0]
        _lifecycle_cb.emit_xor(builder, [A[i] for i in (10, 11, 12)] + [Hlow[2], v[10], v[11]], q, _lifecycle_H3_INITIAL)
        return q

    def _lifecycle_prepare_H4(builder, D, H3):
        q = builder.alloc_qubits(1)[0]
        _lifecycle_cb.emit_xor(builder, [D[11], D[12], H3], q, _lifecycle_H4_PLAN)
        return q

    def _lifecycle_erase_high_H(builder, v, D, H, *, initial=False):
        """Erase H4 first, retaining H3 until its dependent phase is paid."""
        _lifecycle__erase(builder, H[4], [D[11], D[12], H[3]], _lifecycle_H4_PLAN)
        variables = [D[i] for i in (10, 11, 12)] + [H[2], v[10], v[11]] if initial else [D[i] for i in (9, 10, 11, 12)] + [H[2], v[10]]
        _lifecycle__erase(builder, H[3], variables, _lifecycle_H3_INITIAL if initial else _lifecycle_H3_CURRENT)
        return list(H[:3])

    def _lifecycle__coefficient_carry(builder, S, sign, k):
        q = builder.alloc_qubits(1)[0]
        if k:
            builder.cx(S[k], S[k - 1])
            builder.ccx(sign, S[k - 1], q)
            builder.cx(S[k], S[k - 1])
            builder.cx(S[k], q)
        else:
            builder.x(sign)
            builder.ccx(sign, S[0], q)
            builder.x(sign)
        return q

    def _lifecycle__clear_coefficient_carry(builder, S, sign, k, q):
        if k:
            builder.cx(S[k], q)
            builder.cx(S[k], S[k - 1])
            builder.del_and(sign, S[k - 1], q)
            builder.cx(S[k], S[k - 1])
        else:
            builder.x(sign)
            builder.del_and(sign, S[0], q)
            builder.x(sign)
        builder.free(q)

    def _lifecycle_coefficient_forward(builder, v, D, H):
        S = [v[8]] + list(H)
        snapshot = builder.alloc_qubits(1)[0]
        builder.cx(D[6], snapshot)
        token = _lifecycle_ar.DeferredBoundedToken(_lifecycle_SimpleNamespace(last=5, signed_source=False), snapshot, 7, [])
        for i in range(5):
            k = 4 - i
            carry = _lifecycle__coefficient_carry(builder, S, v[i], k)
            for q in D[:7]:
                builder.cx(v[i], q)
            token.row_debts.append(_lifecycle_ar.forward_add(builder, S[k + 1:], D[:7], carry_in=carry))
            for q in D[:7]:
                builder.cx(v[i], q)
            _lifecycle__clear_coefficient_carry(builder, S, v[i], k, carry)
        _lifecycle_ar._deferred_overflow(builder, v[:5], S, D, token, inverse=False)
        return token

    def _lifecycle__merge_debts(builder, first, second):
        assert not first.consumed and (not second.consumed) and (first.width == second.width)
        for position, outcome in list(first.measurements.items()):
            other = second.measurements.get(position)
            if other is None:
                second.measurements[position] = outcome
            else:
                builder.cx(outcome, other)
                builder.free(outcome)
        first.measurements.clear()
        first.consumed = True

    def _lifecycle_merge_coefficient_transcripts(builder, first, second):
        assert first.window == second.window == 7 and len(first.row_debts) == len(second.row_debts) == 5
        for a, b in zip(first.row_debts, second.row_debts):
            _lifecycle__merge_debts(builder, a, b)
        _lifecycle__merge_debts(builder, first.overflow_debt, second.overflow_debt)

    def _lifecycle_coefficient_inverse(builder, v, D, H, token, dirty):
        S = [v[8]] + list(H)
        _lifecycle_ar._deferred_overflow(builder, v[:5], S, D, token, inverse=True)
        saved = _lifecycle_ar.release_saved_bit(builder, token.saved_bit)
        token.saved_bit = None
        for i in reversed(range(5)):
            k = 4 - i
            carry = _lifecycle__coefficient_carry(builder, S, v[i], k)
            for q in D[:7]:
                builder.cx(v[i], q)
            _lifecycle_ar.inverse_add(builder, S[k + 1:], D[:7], token.row_debts[i], carry_in=carry, dirty_wires=dirty)
            for q in D[:7]:
                builder.cx(v[i], q)
            _lifecycle__clear_coefficient_carry(builder, S, v[i], k, carry)
        _lifecycle_ar.repay_saved_bit(builder, D[6], saved)
        assert all((d.consumed and (not d.measurements) for d in token.row_debts))
        assert token.overflow_debt.consumed and (not token.overflow_debt.measurements)

    @_lifecycle_dataclass
    class _lifecycle_SeedToken:
        rows: list

    def _lifecycle_seed_forward(builder, v, D):
        _lifecycle_seed_root_frame(builder, v)
        seed = list(builder.alloc_qubits(3))
        builder.x(_lifecycle_array(seed))
        rows = []
        for i, control in enumerate((v[0], v[1], v[3])):
            builder.x(control)
            rows.append(_lifecycle_ar.forward_signed_row(builder, D, seed, shift=-(11 - i), sign=control))
            builder.x(control)
            q = builder.alloc_qubits(1)[0]
            builder.x(q)
            builder.cx(control, q)
            seed.append(q)
        _lifecycle_seed_root_frame(builder, v, inverse=True)
        return (seed, _lifecycle_SeedToken(rows))

    def _lifecycle_seed_cleanup(builder, v, D, seed, token):
        seed = list(seed)
        _lifecycle_seed_root_frame(builder, v)
        raw = list(D[8:13]) + [v[0], v[1], v[3]]
        _lifecycle__erase(builder, seed[5], raw, _lifecycle_plan_from_json(_lifecycle_SEED['initial_seed5_erasure']))
        helpers = []
        for item in _lifecycle_SEED['persistent_helpers']:
            q = builder.alloc_qubits(1)[0]
            _lifecycle_cb.emit_xor(builder, raw + helpers, q, _lifecycle_plan_from_json(item['plan']))
            helpers.append(q)
        carries = []
        for debt in token.rows:
            carries.extend((debt.measurements[position] for position in sorted(debt.measurements)))
        assert len(carries) == len(_lifecycle_SEED['carry_phase_plans']) == 6
        for outcome, plan in zip(carries, _lifecycle_SEED['carry_phase_plans']):
            _lifecycle_cb.emit_phase(builder, raw + helpers + seed[:5], outcome, _lifecycle_plan_from_json(plan))
            builder.free(outcome)
        for debt in token.rows:
            debt.measurements.clear()
            debt.consumed = True
        m = builder.alloc_bits(1)[0]
        builder.hmr(seed[4], m)
        builder.free(seed[4])
        fifth = builder.alloc_qubits(1)[0]
        builder.push_condition(m)
        _lifecycle_cb.emit_xor(builder, raw + helpers, fifth, _lifecycle_plan_from_json(_lifecycle_SEED['conditional_helper']['plan']))
        builder.pop_condition()
        _lifecycle_cb.emit_phase(builder, raw + helpers + [fifth] + seed[:4], m, _lifecycle_plan_from_json(_lifecycle_SEED['seed4_erasure']['plan']))
        aux = builder.alloc_bits(1)[0]
        builder.hmr(fifth, aux)
        builder.push_condition(m)
        _lifecycle_cb.emit_phase(builder, raw + helpers, aux, _lifecycle_plan_from_json(_lifecycle_SEED['conditional_helper']['plan']))
        builder.pop_condition()
        builder.free(aux)
        builder.free(fifth)
        builder.free(m)
        for item in _lifecycle_SEED['remaining_seed_erasures']:
            i = item['bit']
            variables = raw + helpers + [seed[j] for j in item['remaining_seed_bits']]
            _lifecycle__erase(builder, seed[i], variables, _lifecycle_plan_from_json(item['plan']))
        for i in reversed(range(4)):
            _lifecycle__erase(builder, helpers[i], raw + helpers[:i], _lifecycle_plan_from_json(_lifecycle_SEED['persistent_helpers'][i]['plan']))
        _lifecycle_seed_root_frame(builder, v, inverse=True)

    def _lifecycle__product_carry(builder, C, q, i):
        """Return an owned rounding carry, False, or the final aliased q owner."""
        shift = 8 - i
        parity = C[8]
        if shift < 0:
            builder.cx(parity, q)
            builder.x(q)
            return q
        if shift == 0:
            assert C[0] is False
            return False
        carry = builder.alloc_qubits(1)[0]
        upper = C[shift]
        lower = C[shift - 1]
        if lower is False:
            builder.cx(parity, q)
            builder.ccx(upper, q, carry)
            builder.cx(parity, q)
        else:
            builder.cx(upper, lower)
            builder.cx(parity, q)
            builder.x(q)
            builder.ccx(lower, q, carry)
            builder.x(q)
            builder.cx(parity, q)
            builder.cx(upper, lower)
            builder.cx(upper, carry)
        return carry

    def _lifecycle__clear_product_carry(builder, C, q, i, carry):
        shift = 8 - i
        parity = C[8]
        if shift < 0:
            builder.x(q)
            builder.cx(parity, q)
            return
        if shift == 0:
            assert carry is False
            return
        upper = C[shift]
        lower = C[shift - 1]
        if lower is False:
            builder.cx(parity, q)
            builder.del_and(upper, q, carry)
            builder.cx(parity, q)
        else:
            builder.cx(upper, carry)
            builder.cx(upper, lower)
            builder.cx(parity, q)
            builder.x(q)
            builder.del_and(lower, q, carry)
            builder.x(q)
            builder.cx(parity, q)
            builder.cx(upper, lower)
        builder.free(carry)

    @_lifecycle_dataclass
    class _lifecycle_ProductToken:
        rows: list

    def _lifecycle_product_forward(builder, D, seed, h):
        word = list(seed) + list(h)
        C = [False] + list(D)
        rows = []
        builder.x(word[15])
        for i in range(10):
            q = word[6 + i]
            target = word[:6 + i]
            source = C[9 - i:] if i < 9 else C
            for t in target:
                builder.cx(q, t)
            carry = _lifecycle__product_carry(builder, C, q, i)
            rows.append(_lifecycle_product_ar.forward_add(builder, source, target, carry_in=carry))
            _lifecycle__clear_product_carry(builder, C, q, i, carry)
            for t in target:
                builder.cx(q, t)
        builder.x(word[15])
        return (word, _lifecycle_ProductToken(rows))

def _initialize_normalization():
    global _normalization_ENGINE, _normalization_HERE, _normalization_INTEGRATED_ROOT, _normalization_KICKMIX, _normalization_MAX_X, _normalization_MODEL, _normalization_MODEL_PATH, _normalization_MODEL_SHA, _normalization_NARROW, _normalization_PATH, _normalization_Path, _normalization_SHA, _normalization_TESTS, _normalization_TOOLING, _normalization__IntegratedPath, _normalization___file__, _normalization___name__, _normalization_array, _normalization_cb, _normalization_checked_json, _normalization_current_gate, _normalization_forward, _normalization_hashlib, _normalization_importlib, _normalization_inverse, _normalization_json, _normalization_km, _normalization_os, _normalization_plan_from_json, _normalization_source, _normalization_spec, _normalization_sys, _normalization_verify_gate_sources, _normalization_with_registers
    _import_star('_normalization_', _import_component('common', 'work/c10/narrow/native/candidate01/normalization.py', False))
    _normalization_PATH = _normalization_NARROW / 'research/quantized_producer/pair_normalization.py'
    _normalization_spec = _spec('native_pair_normalization_source', _normalization_PATH)
    _normalization_source = _new_module(_normalization_spec)
    _normalization_sys.modules[_normalization_spec.name] = _normalization_source
    _normalization_spec.loader.exec_module(_normalization_source)

def _initialize_root_decode():
    global _root_decode_CERT, _root_decode_ENGINE, _root_decode_HERE, _root_decode_INTEGRATED_ROOT, _root_decode_KICKMIX, _root_decode_MODEL, _root_decode_MODEL_PATH, _root_decode_MODEL_SHA, _root_decode_NARROW, _root_decode_Path, _root_decode_TESTS, _root_decode_TOOLING, _root_decode__IntegratedPath, _root_decode___file__, _root_decode___name__, _root_decode_array, _root_decode_cb, _root_decode_checked_json, _root_decode_current_gate, _root_decode_decode_root, _root_decode_hashlib, _root_decode_json, _root_decode_km, _root_decode_linear_frame, _root_decode_os, _root_decode_plan_from_json, _root_decode_sys, _root_decode_verify_gate_sources, _root_decode_with_registers
    _import_star('_root_decode_', _import_component('common', 'work/c10/narrow/native/candidate01/root_decode.py', False))
    _root_decode_linear_frame = _import_component('thermometer_cleanup', 'work/c10/narrow/native/candidate01/root_decode.py', False).linear_frame
    _root_decode_CERT = _root_decode_checked_json(_root_decode_NARROW / 'research/quantized_producer/framed_retained5_best21_snapshot.json', '3b6fa7059bee77bb9abe6c7395cd8ff2f2899843523188c60d513e6c5d381def')

    def _root_decode_decode_root(builder, v, A, H, retired_outcomes):
        """v12 has None at5,6,7,9,11; v8=R andv10=rawa5 remain.

    Return current v owners, with its R frame STILL active. The caller owns
    the final one-CCX R unframe in the separately counted4E lifecycle.
    retired_outcomes maps raw address indices0,1,2,4,6 to their HMR bits.
    """
        v = list(v)
        A = list(A)
        H = list(H)
        missing = (0, 1, 2, 4, 6)
        assert len(v) == 12 and len(A) == 13 and (len(H) == 5)
        assert all((v[5 + i] is None for i in missing))
        assert set(retired_outcomes) == set(missing)
        features = [v[8]] + A + H + [v[10]]
        outputs = []
        for record in _root_decode_CERT['plans']:
            p = _root_decode_plan_from_json(record['plan'])
            assert p.width == len(features)
            q = builder.alloc_qubits(1)[0]
            _root_decode_cb.emit_xor(builder, features, q, p)
            outputs.append(q)
            features.append(q)
        rows = [_root_decode_CERT['raw_five_from_code'][str(i)] for i in missing]
        for kind, i, j in _root_decode_linear_frame(rows):
            if kind == 'cx':
                builder.cx(outputs[i], outputs[j])
            else:
                builder.swap(outputs[i], outputs[j])
        for i, q in zip(missing, outputs):
            v[5 + i] = q
            m = retired_outcomes[i]
            builder.push_condition(m)
            builder.z(q)
            builder.pop_condition()
            builder.free(m)
        return v

def _initialize_tables():
    global _tables_Any, _tables_CODEBOOK_SHA, _tables_FROZEN, _tables_FULL, _tables_INTEGRATED_ROOT, _tables_MODEL, _tables_MODEL_SHA, _tables_NARROW, _tables_PINS, _tables_TableDebt, _tables_TableDebts, _tables__IntegratedPath, _tables___file__, _tables___name__, _tables__affine_xor, _tables__row_matrix_inverse_operations, _tables__swap, _tables_annotations, _tables_array, _tables_cb, _tables_certificate, _tables_checked_json, _tables_cleanup_joint16, _tables_dataclass, _tables_emit_affine_frame, _tables_hashlib, _tables_km, _tables_load_joint16, _tables_lru_cache, _tables_model_truths, _tables_model_values, _tables_plan_from_json
    _tables_dataclass = _import_component('dataclasses', 'work/c10/narrow/native/candidate01/tables.py', False).dataclass
    _tables_lru_cache = _import_component('functools', 'work/c10/narrow/native/candidate01/tables.py', False).lru_cache
    _tables_km = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).km
    _tables_cb = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).cb
    _tables_NARROW = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).NARROW
    _tables_MODEL = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).MODEL
    _tables_checked_json = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).checked_json
    _tables_plan_from_json = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).plan_from_json
    _tables_FROZEN = _tables_NARROW / 'research/joint_loader/frozen'
    _tables_PINS = {'first': ('loader16_first60.json', '3bcbd49ad53c0e2661bbc1112d172c854d4bf50ba4ea1f9a119a077f8e6cd9fd'), 'second': ('loader16_second73.json', '52db753c9efef945c9194ed4a39ec3b250221b69eb10e0030dc2a283f659eafc'), 'cleanup': ('retained_table_cleanup9.json', '6a48b472433918d2c51f30e6eeb1d9933fdf1aa4ae9f83b93129fd8ac103b6b5')}
    _tables_FULL = (1 << 128) - 1

    @_tables_dataclass(frozen=True)
    class _tables_TableDebt:
        outcome: Any
        truth128: int

    class _tables_TableDebts:
        """Own all recorded measurement bits until exact Clifford repayment.

Only unconditional HMR of a certified function of the original raw seven-bit
table address belongs here. Surrounding classical conditions would require a
separate guard-aware extension; they must not be omitted from a debt.
"""

        def __init__(self):
            self.pending = []
            self._owned = set()
            self.total_recorded = 0

        def record(self, outcome, truth128):
            truth128 = int(truth128)
            if not isinstance(outcome, _tables_km.b):
                raise TypeError('A table HMR outcome must be a classical bit.')
            if outcome in self._owned:
                raise ValueError('A table HMR outcome already has an owner.')
            if not 0 <= truth128 <= _tables_FULL:
                raise ValueError('A seven-bit table truth must contain at most128 rows.')
            self.pending.append(_tables_TableDebt(outcome, truth128))
            self._owned.add(outcome)
            self.total_recorded += 1

        def erase(self, builder, wire, truth128, *, free=False):
            outcome = builder.alloc_bits(1)[0]
            builder.hmr(wire, outcome)
            self.record(outcome, truth128)
            if free:
                builder.free(wire)
            return outcome

        def flush(self, builder, variables, functions):
            """Pay every complete debt using a certified current quadratic chart."""
            variables = list(variables)
            functions = list(map(int, functions))
            if len(variables) != len(functions):
                raise ValueError('Phase variables and truth coordinates differ.')
            book = _tables_cb.Codebook(functions, 128)
            if len(book.span.pivots) != 128:
                raise ValueError('The supplied table phase chart is not universal.')
            count = len(self.pending)
            for debt in self.pending:
                expression = book.span.solve(debt.truth128)
                if expression is None:
                    raise AssertionError('A pending table truth is outside the live phase chart.')
                plan = book.decode_expression(expression)
                assert plan.evaluate_functions(functions, _tables_FULL) == debt.truth128
                _tables_cb.emit_phase(builder, variables, debt.outcome, plan)
                builder.free(debt.outcome)
            self.pending.clear()
            self._owned.clear()
            return dict(outcomes=count, Toffolis=0, quadratic_rank=128)

    @_tables_lru_cache(maxsize=3)
    def _tables_certificate(which):
        name, digest = _tables_PINS[which]
        data = _tables_checked_json(_tables_FROZEN / name, digest)
        pass
        return data

    @_tables_lru_cache(maxsize=1)
    def _tables_model_values():
        return dict(A=tuple(map(int, _tables_MODEL['A'])), S=tuple(map(int, _tables_MODEL['S'])), H=tuple(map(int, _tables_MODEL['stored_slope'])))

    @_tables_lru_cache(maxsize=1)
    def _tables_model_truths():
        values = _tables_model_values()
        return dict(address=tuple(_tables_cb.word_functions(range(128), 7)), A=tuple(_tables_cb.word_functions(values['A'], 13)), S=tuple(_tables_cb.word_functions(values['S'], 6)), H=tuple(_tables_cb.word_functions(values['H'], 5)))

    def _tables__row_matrix_inverse_operations(rows, width):
        matrix = list(map(int, rows))
        ops = []
        if len(matrix) != width or any((row >> width for row in matrix)):
            raise ValueError('Wrong Clifford matrix shape.')
        for column in range(width):
            pivot = next((r for r in range(column, width) if matrix[r] >> column & 1), None)
            if pivot is None:
                raise ValueError('A requested physical Clifford frame is singular.')
            if pivot != column:
                matrix[pivot], matrix[column] = (matrix[column], matrix[pivot])
                ops.append(('swap', pivot, column))
            for row in range(width):
                if row != column and matrix[row] >> column & 1:
                    matrix[row] ^= matrix[column]
                    ops.append(('cx', column, row))
        assert matrix == [1 << i for i in range(width)]
        return tuple(reversed(ops))

    def _tables__swap(builder, a, b):
        if a == b:
            return
        builder.cx(a, b)
        builder.cx(b, a)
        builder.cx(a, b)

    def _tables_emit_affine_frame(builder, address, work, rows):
        """Apply an invertible work-wire matrix plus raw-address affine terms."""
        address = list(address)
        work = list(work)
        rows = list(map(int, rows))
        if len(address) != 7:
            raise ValueError('Expected seven unchanged raw address wires.')
        for kind, a, b in _tables__row_matrix_inverse_operations([row >> 8 for row in rows], len(work)):
            if kind == 'cx':
                builder.cx(work[a], work[b])
            else:
                _tables__swap(builder, work[a], work[b])
        for target, row in zip(work, rows):
            if row & 1:
                builder.x(target)
            for bit in range(7):
                if row >> 1 + bit & 1:
                    builder.cx(address[bit], target)

    def _tables_cleanup_joint16(builder, address7, A13, Hlow3, debts):
        """Repay all table debts and erase/free the sixteen outputs for9CCX."""
        address = list(address7)
        A = list(A13)
        H = list(Hlow3)
        if (len(address), len(A), len(H)) != (7, 13, 3):
            raise ValueError('Wrong final table chart widths.')
        if len(set(address + A + H)) != 23:
            raise ValueError('Final table chart owners overlap.')
        truths = _tables_model_truths()
        outputs = A + H
        functions = list(truths['address']) + list(truths['A']) + list(truths['H'][:3])
        flushed = debts.flush(builder, address + outputs, functions)
        data = _tables_certificate('cleanup')
        case = next((c for c in data['cases'] if c['output_count'] == 16))
        _tables_emit_affine_frame(builder, address, outputs, [int(row) << 8 for row in case['output_Clifford_basis_rows']])
        wires = {f'r{i}': wire for i, wire in enumerate(address)}
        wires.update({f'c{i}': wire for i, wire in enumerate(outputs)})
        count = 0
        for item in case['steps']:
            kind = item['kind']
            if kind == 'bank':
                variables = [wires[name] for name in item['inputs']]
                target = builder.alloc_qubits(1)[0]
                plan = _tables_plan_from_json(item['plan'])
                _tables_cb.emit_xor(builder, variables, target, plan)
                wires[item['name']] = target
                count += plan.and_count
            elif kind in ('HMR_output', 'HMR_bank'):
                variables = [wires[name] for name in item['retained']]
                target = wires.pop(item['name'])
                plan = _tables_plan_from_json(item['phase_plan'])
                _tables_cb.emit_erase(builder, variables, [target], [plan])
                builder.free(target)
            else:
                raise AssertionError(f'Unknown cleanup operation:{kind}')
        assert count == 9 and set(wires) == {f'r{i}' for i in range(7)} and (not debts.pending)
        return dict(Toffolis=9, table_debts_repaid=flushed['outcomes'], quantum_outputs_erased=16)

def _initialize_candidate02_setup():
    global _candidate02_setup_BASE, _candidate02_setup_HERE, _candidate02_setup_INPUTS, _candidate02_setup_INTEGRATED_ROOT, _candidate02_setup_NARROW, _candidate02_setup_Path, _candidate02_setup__IntegratedPath, _candidate02_setup___file__, _candidate02_setup___name__, _candidate02_setup_baseline_divider, _candidate02_setup_common, _candidate02_setup_copy, _candidate02_setup_hashlib, _candidate02_setup_importlib, _candidate02_setup_initialize_u12, _candidate02_setup_install, _candidate02_setup_json, _candidate02_setup_load_baseline, _candidate02_setup_os, _candidate02_setup_sys, _candidate02_setup_variant_gate
    _candidate02_setup_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate02/variant.py', False).Path
    _candidate02_setup_os = _import_component('os', 'work/c10/narrow/native/candidate02/variant.py', True)
    _candidate02_setup_sys = _import_component('sys', 'work/c10/narrow/native/candidate02/variant.py', True)
    _candidate02_setup_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _candidate02_setup_os.environ['OMP_NUM_THREADS'] = '1'
    _candidate02_setup_HERE = _candidate02_setup_Path(_candidate02_setup___file__).resolve().parent
    _candidate02_setup_BASE = _candidate02_setup_HERE.parent / 'candidate01'
    _candidate02_setup_sys.path.insert(0, str(_candidate02_setup_BASE))
    _candidate02_setup_common = _import_component('common', 'work/c10/narrow/native/candidate02/variant.py', True)
    _candidate02_setup_baseline_divider = _import_component('divider', 'work/c10/narrow/native/candidate02/variant.py', False)

    def _candidate02_setup_load_baseline(name):
        path = _candidate02_setup_BASE / (name + '.py')
        module_name = 'candidate02_pinned_' + name
        if module_name in _candidate02_setup_sys.modules:
            return _candidate02_setup_sys.modules[module_name]
        spec = _spec(module_name, path)
        module = _new_module(spec)
        _candidate02_setup_sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def _candidate02_setup_initialize_u12(builder, v, P, u):
        """13-CCX direct triangular construction, followed by two exact HMRs."""
        d = _candidate02_setup_baseline_divider
        P = list(P)
        for i in range(4):
            item = d.LOCAL['low_cleanup'][i]
            env = {f'v{j}': v[j] for j in range(i + 1)}
            env.update(p12=P[12], p13=P[13], p14=P[14])
            env.update({f'u{j}': u[j] for j in range(i)})
            d.cb.emit_xor(builder, [env[name] for name in item['inputs']], u[i], d.plan_from_json(item['plan']))

        def aa(i):
            return (1, 1 << i) if 0 <= i < 12 else (0, 0)

        def bb(i):
            return (1, 0) if i in (0, 13) else (1, 1 << i - 1)
        for i in range(4, 14):
            plan = d._compose(d.HIGH, [aa(i), bb(i), aa(i - 2), aa(i - 3), aa(i - 1), (0, 1 << 12)], 13)
            d.cb.emit_xor(builder, list(v) + [u[i - 1]], u[i], plan)
        variables = [v[0], v[1], P[12], u[0], u[1]]
        d._erase(builder, P[13], variables, d.P13)
        d._erase(builder, P[14], variables, d.P14)
        P[13] = None
        P[14] = None
        return P

    def _candidate02_setup_install():
        """Change only this process's imported initializer, never an on-disk file."""
        pass
        _candidate02_setup_baseline_divider.initialize_u12 = _candidate02_setup_initialize_u12
        return _candidate02_setup_baseline_divider

def _initialize_candidate03_setup():
    global _candidate03_setup_BASE, _candidate03_setup_HERE, _candidate03_setup_INTEGRATED_ROOT, _candidate03_setup_NARROW, _candidate03_setup_ORIGINAL_ROOT_STEP, _candidate03_setup_Path, _candidate03_setup__IntegratedPath, _candidate03_setup___file__, _candidate03_setup___name__, _candidate03_setup_common, _candidate03_setup_hashlib, _candidate03_setup_importlib, _candidate03_setup_install, _candidate03_setup_json, _candidate03_setup_load_baseline, _candidate03_setup_os, _candidate03_setup_path, _candidate03_setup_previous, _candidate03_setup_root, _candidate03_setup_root_step, _candidate03_setup_spec, _candidate03_setup_sys, _candidate03_setup_variant_gate
    _candidate03_setup_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate03/variant.py', False).Path
    _candidate03_setup_os = _import_component('os', 'work/c10/narrow/native/candidate03/variant.py', True)
    _candidate03_setup_sys = _import_component('sys', 'work/c10/narrow/native/candidate03/variant.py', True)
    _candidate03_setup_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _candidate03_setup_os.environ['OMP_NUM_THREADS'] = '1'
    _candidate03_setup_HERE = _candidate03_setup_Path(_candidate03_setup___file__).resolve().parent
    _candidate03_setup_path = _candidate03_setup_HERE.parent / 'candidate02/variant.py'
    _candidate03_setup_spec = _spec('candidate03_pinned_candidate02_variant', _candidate03_setup_path)
    _candidate03_setup_previous = _new_module(_candidate03_setup_spec)
    _candidate03_setup_sys.modules[_candidate03_setup_spec.name] = _candidate03_setup_previous
    _candidate03_setup_spec.loader.exec_module(_candidate03_setup_previous)
    _candidate03_setup_root = _import_component('consuming_odd_sqrt', 'work/c10/narrow/native/candidate03/variant.py', False)
    _candidate03_setup_ORIGINAL_ROOT_STEP = _candidate03_setup_root._root_step
    _candidate03_setup_common = _candidate03_setup_previous.common

    def _candidate03_setup_root_step(builder, remainder, older, b, *, initial=False, inverse=False):
        if len(remainder) < 14:
            return _candidate03_setup_ORIGINAL_ROOT_STEP(builder, remainder, older, b, initial=initial, inverse=inverse)
        assert len(remainder) in (14, 15) and (not initial) and isinstance(b, _candidate03_setup_common.km.q)
        low = list(remainder[:3])
        high = list(remainder[3:])
        older = list(older)
        assert b not in list(remainder) + older
        if not inverse:
            builder.x(low[0])
            builder.x(low[1])
        builder.cx(b, _candidate03_setup_root._arr(high))
        if inverse:
            _candidate03_setup_root._add_leading_one(builder, high, inverse=True)
            _candidate03_setup_root.add(builder, older, high, carry_in=b, subtract=True)
        else:
            _candidate03_setup_root.add(builder, older, high, carry_in=b)
            _candidate03_setup_root._add_leading_one(builder, high)
        builder.cx(b, _candidate03_setup_root._arr(high))
        if inverse:
            builder.x(low[0])
            builder.x(low[1])

    def _candidate03_setup_install():
        _candidate03_setup_previous.install()
        pass
        _candidate03_setup_root._root_step = _candidate03_setup_root_step
        return _candidate03_setup_root

    def _candidate03_setup_load_baseline(name):
        return _candidate03_setup_previous.load_baseline(name)

def _initialize_candidate04_setup():
    global _candidate04_setup_ACCEPTED, _candidate04_setup_AngleProxy, _candidate04_setup_BASE, _candidate04_setup_BOUND, _candidate04_setup_COEFFICIENTS37, _candidate04_setup_Fraction, _candidate04_setup_HERE, _candidate04_setup_INPUTS, _candidate04_setup_INTEGRATED_ROOT, _candidate04_setup_LAST_PROXY_RECORDS, _candidate04_setup_NARROW, _candidate04_setup_NEW_TURN_UNITS50, _candidate04_setup_ORIGINAL_ENDPOINT, _candidate04_setup_Path, _candidate04_setup_RESEARCH, _candidate04_setup_SITES, _candidate04_setup__INSTALLED, _candidate04_setup__IntegratedPath, _candidate04_setup___file__, _candidate04_setup___name__, _candidate04_setup_angle_class, _candidate04_setup_checked_quantized, _candidate04_setup_common, _candidate04_setup_copy, _candidate04_setup_divider, _candidate04_setup_hashlib, _candidate04_setup_importlib, _candidate04_setup_install, _candidate04_setup_json, _candidate04_setup_load_baseline, _candidate04_setup_math, _candidate04_setup_os, _candidate04_setup_path, _candidate04_setup_phase_endpoint, _candidate04_setup_previous, _candidate04_setup_r, _candidate04_setup_spec, _candidate04_setup_sys, _candidate04_setup_variant_gate, _candidate04_setup_verify_inputs
    _candidate04_setup_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate04/variant.py', False).Path
    _candidate04_setup_Fraction = _import_component('fractions', 'work/c10/narrow/native/candidate04/variant.py', False).Fraction
    _candidate04_setup_os = _import_component('os', 'work/c10/narrow/native/candidate04/variant.py', True)
    _candidate04_setup_sys = _import_component('sys', 'work/c10/narrow/native/candidate04/variant.py', True)
    _candidate04_setup_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _candidate04_setup_os.environ['OMP_NUM_THREADS'] = '1'
    _candidate04_setup_HERE = _candidate04_setup_Path(_candidate04_setup___file__).resolve().parent
    _candidate04_setup_NARROW = _candidate04_setup_HERE.parents[1]
    _candidate04_setup_RESEARCH = _candidate04_setup_NARROW / 'research/postgate_angle_refit'
    _candidate04_setup_path = _candidate04_setup_HERE.parent / 'candidate03/variant.py'
    _candidate04_setup_spec = _spec('candidate04_pinned_candidate03_variant', _candidate04_setup_path)
    _candidate04_setup_previous = _new_module(_candidate04_setup_spec)
    _candidate04_setup_sys.modules[_candidate04_setup_spec.name] = _candidate04_setup_previous
    _candidate04_setup_spec.loader.exec_module(_candidate04_setup_previous)
    _candidate04_setup_common = _candidate04_setup_previous.common
    _candidate04_setup_divider = _candidate04_setup_previous.previous.baseline_divider
    _candidate04_setup_BOUND = _json_loads(_read_text(_candidate04_setup_RESEARCH / 'quantize50_bound.json'))
    _candidate04_setup_ACCEPTED = _json_loads(_read_text(_candidate04_setup_NARROW / 'PAPER_GATE_RECEIPT_014_VARIANT.json'))
    assert _candidate04_setup_ACCEPTED['native_build_authorized'] and _candidate04_setup_ACCEPTED['preserve_candidates_01_02_03']
    assert _candidate04_setup_BOUND['proved_quantized_margin_lower_bound_units'] == _candidate04_setup_ACCEPTED['proved_margin_lower_bound_units64'] == 124286782
    _candidate04_setup_COEFFICIENTS37 = tuple(((1 << i) + (1 << 27 if i == 0 else 0) for i in range(27))) + (-(1 << 27),) + tuple((1 << 27 + j for j in range(1, 7)))
    _candidate04_setup_SITES = tuple((f'base_i{i}' for i in range(27))) + ('threshold_j0',) + tuple((f'overflow_j{j}' for j in range(1, 7)))
    _candidate04_setup_NEW_TURN_UNITS50 = tuple(_candidate04_setup_BOUND['new_generic_turn_units50'])
    assert len(_candidate04_setup_NEW_TURN_UNITS50) == len(_candidate04_setup_COEFFICIENTS37) == len(_candidate04_setup_SITES) == 34
    assert all((type(v) is int for v in _candidate04_setup_NEW_TURN_UNITS50))
    assert all(_candidate04_setup_BOUND['delta_turn_units64']), 'The literal34-change structural comparison requires all34 nonzero deltas.'
    assert [r['site'] for r in _candidate04_setup_BOUND['angle_sites']] == list(_candidate04_setup_SITES)
    _candidate04_setup_ORIGINAL_ENDPOINT = _candidate04_setup_divider.phase_endpoint
    _candidate04_setup_LAST_PROXY_RECORDS = []
    _candidate04_setup__INSTALLED = False

    def _candidate04_setup_angle_class(half_turns):
        angle = _candidate04_setup_Fraction(half_turns)
        if (2 * angle).denominator == 1:
            return 'Clifford'
        if (4 * angle).denominator == 1:
            return 'T'
        return 'generic'

    class _candidate04_setup_AngleProxy:
        """Intercept only exact z_pow angles; all allocation/data APIs delegate."""

        def __init__(self, builder):
            self.builder = builder
            self.generic = 0
            self.T = 0
            self.Clifford = 0
            self.records = []

        def __getattr__(self, name):
            return getattr(self.builder, name)

        def z_pow(self, target, half_turns):
            old = _candidate04_setup_Fraction(half_turns)
            kind = _candidate04_setup_angle_class(old)
            if kind == 'generic':
                index = self.generic
                assert index < 34, ('unexpected_generic_rotation', index, str(old))
                expected = _candidate04_setup_Fraction(2 * _candidate04_setup_COEFFICIENTS37[index], 1 << 37)
                assert old == expected, (_candidate04_setup_SITES[index], str(old), str(expected))
                new = _candidate04_setup_Fraction(2 * _candidate04_setup_NEW_TURN_UNITS50[index], 1 << 50)
                assert _candidate04_setup_angle_class(new) == 'generic'
                self.records.append(dict(index=index, site=_candidate04_setup_SITES[index], target=str(target), old_half_turns=str(old), new_half_turns=str(new)))
                self.generic += 1
                return self.builder.z_pow(target, new)
            if kind == 'T':
                self.T += 1
            else:
                self.Clifford += 1
            return self.builder.z_pow(target, old)

        def finish(self):
            assert (self.generic, self.T, self.Clifford) == (34, 4, 1), (self.generic, self.T, self.Clifford)
            return self.records

    def _candidate04_setup_phase_endpoint(builder, token):
        proxy = _candidate04_setup_AngleProxy(builder)
        result = _candidate04_setup_ORIGINAL_ENDPOINT(proxy, token)
        _candidate04_setup_LAST_PROXY_RECORDS.clear()
        _candidate04_setup_LAST_PROXY_RECORDS.extend(proxy.finish())
        return result

    def _candidate04_setup_install():
        global _candidate04_setup__INSTALLED
        pass
        if not _candidate04_setup__INSTALLED:
            _candidate04_setup_previous.install()
            assert _candidate04_setup_divider.phase_endpoint is _candidate04_setup_ORIGINAL_ENDPOINT, 'Unexpected pre-existing endpoint replacement.'
            _candidate04_setup_divider.phase_endpoint = _candidate04_setup_phase_endpoint
            _candidate04_setup__INSTALLED = True
        return _candidate04_setup_divider

    def _candidate04_setup_load_baseline(name):
        return _candidate04_setup_previous.load_baseline(name)

def _initialize_candidate05_setup():
    global _candidate05_setup_ACCEPTED, _candidate05_setup_BASE, _candidate05_setup_BOUND, _candidate05_setup_COEFFICIENTS37, _candidate05_setup_HERE, _candidate05_setup_INPUTS, _candidate05_setup_INTEGRATED_ROOT, _candidate05_setup_NARROW, _candidate05_setup_NEW_CENTRES, _candidate05_setup_NEW_TURN_UNITS50, _candidate05_setup_OLD_CENTRES, _candidate05_setup_ORIGINAL_ROUTE, _candidate05_setup_ORIGINAL_SLOTS, _candidate05_setup_PREVIOUS, _candidate05_setup_Path, _candidate05_setup_ROUTE_TRACE, _candidate05_setup_SITES, _candidate05_setup__INSTALLED, _candidate05_setup__IntegratedPath, _candidate05_setup___file__, _candidate05_setup___name__, _candidate05_setup_checked_quantized, _candidate05_setup_common, _candidate05_setup_copy, _candidate05_setup_divider, _candidate05_setup_hashlib, _candidate05_setup_importlib, _candidate05_setup_install, _candidate05_setup_json, _candidate05_setup_load_baseline, _candidate05_setup_operation_count, _candidate05_setup_previous, _candidate05_setup_proof50_module, _candidate05_setup_route, _candidate05_setup_spec, _candidate05_setup_sys, _candidate05_setup_variant_gate, _candidate05_setup_verify_inputs
    _candidate05_setup_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate05/variant.py', False).Path
    _candidate05_setup_sys = _import_component('sys', 'work/c10/narrow/native/candidate05/variant.py', True)
    _candidate05_setup_HERE = _candidate05_setup_Path(_candidate05_setup___file__).resolve().parent
    _candidate05_setup_NARROW = _candidate05_setup_HERE.parents[1]
    _candidate05_setup_PREVIOUS = _candidate05_setup_HERE.parent / 'candidate04'
    _candidate05_setup_spec = _spec('candidate05_pinned_candidate04_variant', _candidate05_setup_PREVIOUS / 'variant.py')
    _candidate05_setup_previous = _new_module(_candidate05_setup_spec)
    _candidate05_setup_sys.modules[_candidate05_setup_spec.name] = _candidate05_setup_previous
    _candidate05_setup_spec.loader.exec_module(_candidate05_setup_previous)
    _candidate05_setup_common = _candidate05_setup_previous.common
    _candidate05_setup_divider = _candidate05_setup_previous.divider
    _candidate05_setup_BOUND = _candidate05_setup_previous.BOUND
    _candidate05_setup_COEFFICIENTS37 = _candidate05_setup_previous.COEFFICIENTS37
    _candidate05_setup_NEW_TURN_UNITS50 = _candidate05_setup_previous.NEW_TURN_UNITS50
    _candidate05_setup_SITES = _candidate05_setup_previous.SITES
    _candidate05_setup_ACCEPTED = _candidate05_setup_common.checked_json(_candidate05_setup_NARROW / 'PAPER_GATE_RECEIPT_016_VARIANT.json', '141d51af466cea914cc9c318e09c34558b7c23c6247fbf5e87c9ea9f1efa7cbe')
    assert _candidate05_setup_ACCEPTED['native_build_authorized'] and _candidate05_setup_ACCEPTED['all_native_candidates_preserved'] == [1, 2, 3, 4]
    _candidate05_setup_NEW_CENTRES = tuple(_candidate05_setup_ACCEPTED['centres'])
    _candidate05_setup_OLD_CENTRES = tuple(_candidate05_setup_divider.CENTRES)
    assert _candidate05_setup_NEW_CENTRES == (-1, -3, -7, -1, -2) and _candidate05_setup_OLD_CENTRES == (0, -2, -6, 0, -1)
    _candidate05_setup_ORIGINAL_ROUTE = _candidate05_setup_divider._route
    _candidate05_setup_ORIGINAL_SLOTS = _candidate05_setup_divider._slots()
    _candidate05_setup_ROUTE_TRACE = []
    _candidate05_setup__INSTALLED = False

    def _candidate05_setup_operation_count(builder):
        Program = _import_component('branch_prover', 'work/c10/narrow/native/candidate05/variant.py', False).Program
        generated_text = _import_component('branch_prover', 'work/c10/narrow/native/candidate05/variant.py', False).generated_text
        return len(Program(generated_text(builder.finish_circuit())).operations)

    def _candidate05_setup_route(builder, word, variables, inverse=False):
        """Existing five affine controls; translated matchings; one identity skip."""
        assert len(word) == 27 and tuple(_candidate05_setup_divider.CENTRES) == _candidate05_setup_NEW_CENTRES
        start = _candidate05_setup_operation_count(builder)
        stages = list(range(5))
        if inverse:
            stages.reverse()
        old_gates = []
        new_gates = []
        omissions = []
        for stage in stages:
            with _candidate05_setup_divider._affine_control(builder, variables, _candidate05_setup_divider.CONTROLS[stage]) as control:
                for i in range(27):
                    k = (_candidate05_setup_OLD_CENTRES[stage] - i) % 27
                    if i < k:
                        old_gates.append([str(control), str(word[i]), str(word[k])])
                for i in range(27):
                    k = (_candidate05_setup_NEW_CENTRES[stage] - i) % 27
                    if i >= k:
                        continue
                    if (stage, i, k) == (0, 0, 26):
                        omissions.append(dict(stage=stage, positions=[i, k], control=str(control), owners=[str(word[i]), str(word[k])]))
                        continue
                    builder.cswap(control, word[i], word[k])
                    new_gates.append([str(control), str(word[i]), str(word[k])])
        stop = _candidate05_setup_operation_count(builder)
        assert len(old_gates) == 65 and len(new_gates) == 64 and (len(omissions) == 1)
        _candidate05_setup_ROUTE_TRACE.append(dict(inverse=inverse, start=start, stop=stop, old_cswap_arguments=old_gates, new_cswap_arguments=new_gates, omissions=omissions))

    def _candidate05_setup_install():
        global _candidate05_setup__INSTALLED
        pass
        if not _candidate05_setup__INSTALLED:
            _candidate05_setup_previous.install()
            assert _candidate05_setup_divider._route is _candidate05_setup_ORIGINAL_ROUTE
            _candidate05_setup_divider.CENTRES = _candidate05_setup_NEW_CENTRES
            _candidate05_setup_divider._route = _candidate05_setup_route
            assert _candidate05_setup_divider._slots() == _candidate05_setup_ORIGINAL_SLOTS, 'Common centre offset unexpectedly changed phase sites.'
            _candidate05_setup__INSTALLED = True
        return _candidate05_setup_divider

    def _candidate05_setup_load_baseline(name):
        return _candidate05_setup_previous.load_baseline(name)

def _initialize_decoder06():
    global _decoder06_CERT, _decoder06_EARLY_TABLE_DEBT, _decoder06_INTEGRATED_ROOT, _decoder06_MISSING, _decoder06_NARROW, _decoder06_RESOURCES, _decoder06__BASE, _decoder06__IntegratedPath, _decoder06___file__, _decoder06___name__, _decoder06_cb, _decoder06_checked_json, _decoder06_decode_root, _decoder06_km, _decoder06_plan_from_json
    _decoder06_km = _import_component('common', 'work/c10/narrow/native/candidate06/decoder06.py', False).km
    _decoder06_cb = _import_component('common', 'work/c10/narrow/native/candidate06/decoder06.py', False).cb
    _decoder06_NARROW = _import_component('common', 'work/c10/narrow/native/candidate06/decoder06.py', False).NARROW
    _decoder06_checked_json = _import_component('common', 'work/c10/narrow/native/candidate06/decoder06.py', False).checked_json
    _decoder06_plan_from_json = _import_component('common', 'work/c10/narrow/native/candidate06/decoder06.py', False).plan_from_json
    _decoder06__BASE = _import_component('tables06', 'work/c10/narrow/native/candidate06/decoder06.py', False)._BASE
    _decoder06_CERT = _decoder06_checked_json(_decoder06_NARROW / 'research/quantized_producer/framed_retained5_best21_snapshot.json', '3b6fa7059bee77bb9abe6c7395cd8ff2f2899843523188c60d513e6c5d381def')
    _decoder06_MISSING = (0, 1, 2, 4, 6)
    _decoder06_EARLY_TABLE_DEBT = (0, 1, 2, 4)

    def _decoder06_decode_root(builder, v, A, H, retired_outcomes):
        """Return v with all five values restored and its R frame still active.

    Keys0,1,2,4 MUST map to None: their exact mixed signs are owned by the
    table ledger, not by a direct raw-bit outcome. Key6 MUST be the actual
    late HMR bit. This function creates no placeholder classical bits.
    """
        v = list(v)
        A = list(A)
        H = list(H)
        assert len(v) == 12 and len(A) == 13 and (len(H) == 5)
        assert all((v[5 + i] is None for i in _decoder06_MISSING))
        assert set(retired_outcomes) == set(_decoder06_MISSING)
        assert all((retired_outcomes[i] is None for i in _decoder06_EARLY_TABLE_DEBT))
        assert isinstance(retired_outcomes[6], _decoder06_km.b)
        assert isinstance(v[8], _decoder06_km.q) and isinstance(v[10], _decoder06_km.q)
        features = [v[8]] + A + H + [v[10]]
        outputs = []
        count = 0
        for record in _decoder06_CERT['plans']:
            plan = _decoder06_plan_from_json(record['plan'])
            assert plan.width == len(features)
            q = builder.alloc_qubits(1)[0]
            _decoder06_cb.emit_xor(builder, features, q, plan)
            outputs.append(q)
            features.append(q)
            count += plan.and_count
        assert count == 21 and len(outputs) == 5
        rows = [_decoder06_CERT['raw_five_from_code'][str(i)] for i in _decoder06_MISSING]
        for kind, i, j in _decoder06__BASE._row_matrix_inverse_operations(rows, len(outputs)):
            if kind == 'cx':
                builder.cx(outputs[i], outputs[j])
            else:
                builder.swap(outputs[i], outputs[j])
        for i, q in zip(_decoder06_MISSING, outputs):
            v[5 + i] = q
            outcome = retired_outcomes[i]
            if outcome is not None:
                assert i == 6
                builder.push_condition(outcome)
                builder.z(q)
                builder.pop_condition()
                builder.free(outcome)
        return v

def _initialize_divider_cleanup06():
    global _divider_cleanup06_BASE, _divider_cleanup06_BASE_DIVIDER_SHA, _divider_cleanup06_COMPONENT_CONTRACT, _divider_cleanup06_HERE, _divider_cleanup06_INTEGRATED_ROOT, _divider_cleanup06_NARROW, _divider_cleanup06_Path, _divider_cleanup06__IntegratedPath, _divider_cleanup06___file__, _divider_cleanup06___name__, _divider_cleanup06__divider, _divider_cleanup06_bind, _divider_cleanup06_cleanup_divider, _divider_cleanup06_hashlib, _divider_cleanup06_install
    _divider_cleanup06__divider = None

    def _divider_cleanup06_bind(divider_module):
        """Bind the parent's pinned divider, without installing any hook itself."""
        global _divider_cleanup06__divider
        pass
        pass
        required = ('_feed_carry', '_feed_erase', '_frame', '_leading_offset', '_dirty', 'inverse_add', 'cleanup_u12')
        assert all((callable(getattr(divider_module, name, None)) for name in required))
        if _divider_cleanup06__divider is not None:
            assert _divider_cleanup06__divider is divider_module
        _divider_cleanup06__divider = divider_module
        return _divider_cleanup06_cleanup_divider

    def _divider_cleanup06_install(divider_module):
        """Replace only this process's inverse hook on the supplied divider."""
        divider_module.cleanup_divider = _divider_cleanup06_bind(divider_module)
        return divider_module

    def _divider_cleanup06_cleanup_divider(builder, token):
        """Reverse all24 rows, repay every phase, then return current P15 owners."""
        assert _divider_cleanup06__divider is not None, 'Parent must bind the pinned divider before use.'
        d = _divider_cleanup06__divider
        assert builder.max_qubits == 48 and builder.num_allocated_qubits == 43
        assert not token.consumed and len(token.rows) == 24
        assert [j for j, k, debt in token.rows] == list(range(12, 36))
        assert all((not debt.consumed for j, k, debt in token.rows))
        token.consumed = True
        v = token.v
        released_rows = []
        for j, k, debt in reversed(token.rows):
            u = token.u
            if j <= 24:
                low = u[0]
                target = u[1:]
                sign = token.history[j]
                cur = token.P[23 - j] if j < 24 else None
                if j < 24:
                    assert cur is not None
                carry = d._feed_carry(builder, v, low, cur, sign)
                d._frame(builder, sign, target)
                d._leading_offset(builder, target, inverse=True)
                released_input = d.inverse_add(builder, v[1:], target, debt, carry_in=carry, dirty_wires=d._dirty(token), carry_lifecycle=(lambda value: d._feed_erase(builder, value, v, low, cur, sign), lambda: d._feed_carry(builder, v, low, cur, sign)))
                d._frame(builder, sign, target)
                if not released_input:
                    d._feed_erase(builder, carry, v, low, cur, sign)
                assert released_input, 'Every pinned Q48 feed partition must release its owned input carry.'
                released_rows.append(j)
                if cur is not None:
                    builder.cx(cur, low)
                builder.cx(sign, low)
                builder.cx(v[0], low)
                token.P[24 - j] = low
                token.u = target + [sign]
                del token.history[j]
            else:
                builder.cx(v[0], u[0])
                sign = u[0]
                target = u[k + 1:]
                d._frame(builder, sign, target)
                d._leading_offset(builder, target, inverse=True)
                d.inverse_add(builder, v[k + 1:], target, debt, carry_in=v[k], dirty_wires=d._dirty(token))
                d._frame(builder, sign, target)
                token.u = u[1:] + u[:1]
            assert debt.consumed and (not debt.measurements)
            assert builder.num_allocated_qubits == 43
            live = token.v + token.flags + token.u + [q for q in token.P if q is not None] + list(token.history.values())
            assert len(live) == len(set(live)) == 43
        assert sorted(released_rows) == list(range(12, 25))
        assert tuple(token.u) == token.initial_u and (not token.history)
        token.P = d.cleanup_u12(builder, v, token.P, token.u)
        assert builder.num_allocated_qubits == 31 and all((q is not None for q in token.P))
        assert len(set(v + token.flags + list(token.P))) == 31
        assert all((debt.consumed and (not debt.measurements) for j, k, debt in token.rows))
        return list(token.P)

def _initialize_lifecycle06():
    global _lifecycle06_ACCEPTED, _lifecycle06_BASE, _lifecycle06_BASE_SHA, _lifecycle06_COMMON_SHA, _lifecycle06_COMPONENT_CONTRACT, _lifecycle06_CUT_HOOK, _lifecycle06_HERE, _lifecycle06_INTEGRATED_ROOT, _lifecycle06_NARROW, _lifecycle06_PAPER, _lifecycle06_Path, _lifecycle06__IntegratedPath, _lifecycle06___file__, _lifecycle06___name__, _lifecycle06__mark, _lifecycle06__module, _lifecycle06__name, _lifecycle06__spec, _lifecycle06_baseline, _lifecycle06_common, _lifecycle06_emit_body, _lifecycle06_hashlib, _lifecycle06_importlib, _lifecycle06_km, _lifecycle06_product_inverse, _lifecycle06_sys
    _lifecycle06_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate06/lifecycle06.py', False).Path
    _lifecycle06_sys = _import_component('sys', 'work/c10/narrow/native/candidate06/lifecycle06.py', True)
    _lifecycle06_HERE = _lifecycle06_Path(_lifecycle06___file__).resolve().parent
    _lifecycle06_NARROW = _lifecycle06_HERE.parents[1]
    _lifecycle06_BASE = _lifecycle06_HERE.parent / 'candidate01'
    _lifecycle06_sys.path.insert(0, str(_lifecycle06_BASE))
    _lifecycle06_common = _import_component('common', 'work/c10/narrow/native/candidate06/lifecycle06.py', True)
    _lifecycle06_ACCEPTED = _lifecycle06_common.checked_json(_lifecycle06_NARROW / 'PAPER_GATE_RECEIPT_018_VARIANT.json', '99ef9a891d4e99b262b1a452ea48b18c536e91e7017f018b77bc37f1793ccffd')
    assert _lifecycle06_ACCEPTED['native_build_authorized'] and _lifecycle06_ACCEPTED['Q'] == 48
    _lifecycle06_PAPER = _lifecycle06_common.checked_json(_lifecycle06_NARROW / _lifecycle06_ACCEPTED['paper_gate_path'], _lifecycle06_ACCEPTED['paper_gate_sha256'])
    assert _lifecycle06_PAPER['full_lifecycle_E'] == 563 and _lifecycle06_PAPER['expected_Toffolis'] == 1591
    _lifecycle06__name = 'candidate06_pinned_candidate01_lifecycle'
    if _lifecycle06__name not in _lifecycle06_sys.modules:
        _lifecycle06__spec = _spec(_lifecycle06__name, _lifecycle06_BASE / 'lifecycle.py')
        _lifecycle06__module = _new_module(_lifecycle06__spec)
        _lifecycle06_sys.modules[_lifecycle06__name] = _lifecycle06__module
        _lifecycle06__spec.loader.exec_module(_lifecycle06__module)
    _lifecycle06_baseline = _lifecycle06_sys.modules[_lifecycle06__name]
    _lifecycle06_COMPONENT_CONTRACT = dict(Q=48, lifecycle_E=563, product_forward_E=103, product_inverse_E=137.5, product_conditional_regeneration_E=4, coefficient_E=123, seed_E=17.5, metadata_E=7, root_frames_E=4, root_decoder_E=21, table_loaders_E=141, table_cleanup_E=9, retired_to_table_only=(0, 1, 2, 4), retired_direct_Z=(6,), final_live_owners=26)
    assert sum((_lifecycle06_COMPONENT_CONTRACT[k] for k in ('product_forward_E', 'product_inverse_E', 'coefficient_E', 'seed_E', 'metadata_E', 'root_frames_E', 'root_decoder_E', 'table_loaders_E', 'table_cleanup_E'))) == 563

def _initialize_phase06():
    global _phase06_BINDING, _phase06_Fraction, _phase06_HERE, _phase06_INTEGRATED_ROOT, _phase06_LAST_PHASE_TRACE, _phase06_LAST_PROXY_RECORDS, _phase06_NARROW, _phase06_Path, _phase06_SOURCE_PINS, _phase06_SimpleNamespace, _phase06__IntegratedPath, _phase06___file__, _phase06___name__, _phase06_compact_terms, _phase06_contextmanager, _phase06_hashlib, _phase06_install, _phase06_json, _phase06_phase_endpoint, _phase06_raw_phase_endpoint, _phase06_threshold, _phase06_verify_source_pins
    _phase06_contextmanager = _import_component('contextlib', 'work/c10/narrow/native/candidate06/phase06.py', False).contextmanager
    _phase06_Fraction = _import_component('fractions', 'work/c10/narrow/native/candidate06/phase06.py', False).Fraction
    _phase06_SimpleNamespace = _import_component('types', 'work/c10/narrow/native/candidate06/phase06.py', False).SimpleNamespace
    _phase06_BINDING = None
    _phase06_LAST_PROXY_RECORDS = []
    _phase06_LAST_PHASE_TRACE = []

    def _phase06_compact_terms(original_terms):
        """Substitute c=f1*f3 before compilation AND before HMR phase repayment."""
        terms = tuple((10 if term == 32 else term for term in original_terms))
        assert all((0 <= term < 32 and term.bit_count() <= 2 for term in terms))
        return terms

    @_phase06_contextmanager
    def _phase06_threshold(builder, variables, t):
        assert _phase06_BINDING is not None and len(variables) == 5
        d = _phase06_BINDING.divider
        terms = _phase06_compact_terms(d.THRESHOLDS[t])
        if max((term.bit_count() for term in terms)) <= 1:
            with d._affine_control(builder, variables, terms) as control:
                yield control
        else:
            control = builder.alloc_qubits(1)[0]
            d.xor_polynomial(builder, variables, control, terms)
            try:
                yield control
            finally:
                d._erase_polynomial(builder, control, variables, terms)

    def _phase06_raw_phase_endpoint(builder, token):
        """145 Toffolis,4T,34R at48 owners; raw angles are the old37-unit ones."""
        assert _phase06_BINDING is not None
        d = _phase06_BINDING.divider
        v, u, flags = (token.v, token.u, token.flags)
        assert len(v) == 12 and len(u) == 14 and (len(flags) == 4)
        assert builder.num_allocated_qubits == 43
        d._sigma25_frame(builder, v, u)
        for q in u[:9]:
            builder.cx(v[0], q)
        builder.cx(v[1], u[9])
        signs = {**token.history, 25: u[10], 26: u[9], 36: u[13]}
        signs.update({j: u[35 - j] for j in range(27, 36)})
        assert sorted(signs) == list(range(12, 37))
        for q in signs.values():
            builder.x(q)
        ones = list(builder.alloc_qubits(2))
        builder.x(d.array(ones))
        word = [ones[0]] + [signs[37 - i] for i in range(1, 26)] + [ones[1]]
        assert len(set(word)) == 27 and u[11] not in word and (u[12] not in word)
        p = builder.alloc_qubits(1)[0]
        d.xor_polynomial(builder, flags, p, (6, 10))
        variables = flags + [p]
        assert builder.num_allocated_qubits == 46
        assert d._route is _phase06_BINDING.previous05.route and tuple(d.CENTRES) == (-1, -3, -7, -1, -2)
        d._route(builder, word, variables)
        slots = [word[i] for i in d._slots()]
        factor = 1 << 27
        for i, q in enumerate(slots):
            units = (1 << i) + (factor if i == 0 else 0)
            builder.z_pow(q, _phase06_Fraction(2 * units, 1 << 37))
        for j in range(10):
            angle = _phase06_Fraction(factor * (1 << j), 1 << 37)
            if j == 0:
                with _phase06_threshold(builder, variables, 1) as q:
                    builder.x(q)
                    builder.z_pow(q, -2 * angle)
                    builder.x(q)
            elif j == 9:
                assert angle == _phase06_Fraction(1, 2)
                builder.cz(flags[1], flags[3])
            else:
                with _phase06_threshold(builder, variables, j + 1) as q:
                    d._feature(builder, q, slots[j], angle)
        d._route(builder, word, variables, inverse=True)
        d._erase_polynomial(builder, p, flags, (6, 10))
        builder.x(d.array(ones))
        builder.free(d.array(ones))
        for q in signs.values():
            builder.x(q)
        builder.cx(v[1], u[9])
        for q in u[:9]:
            builder.cx(v[0], q)
        d._sigma25_frame(builder, v, u, inverse=True)
        assert builder.num_allocated_qubits == 43

    def _phase06_phase_endpoint(builder, token):
        assert _phase06_BINDING is not None
        proxy = _phase06_BINDING.Proxy(builder)
        _phase06_raw_phase_endpoint(proxy, token)
        _phase06_LAST_PROXY_RECORDS.clear()
        _phase06_LAST_PROXY_RECORDS.extend(proxy.finish())
        _phase06_LAST_PHASE_TRACE.clear()
        _phase06_LAST_PHASE_TRACE.extend(proxy.allocations)
        _phase06_LAST_PHASE_TRACE.append(dict(event='complete', entry_owners=43, exit_owners=builder.num_allocated_qubits, observed_peak_owners=proxy.peak, generic_calls=proxy.generic, T_calls=proxy.T, direct_Clifford_Z_POW_calls=proxy.Clifford, last_overflow_implemented_as='CZ(flags1,flags3)', retained_controls=['p'], expected_Toffolis=145))

    def _phase06_install(previous05):
        """Bind only after the parent has installed the pinned candidate05 module."""
        global _phase06_BINDING
        pass
        pass
        pass
        pass
        d = previous05.divider
        prior04 = previous05.previous
        assert d._route is previous05.route and tuple(d.CENTRES) == (-1, -3, -7, -1, -2)
        assert d._slots() == previous05.ORIGINAL_SLOTS
        if _phase06_BINDING is not None:
            assert _phase06_BINDING.previous05 is previous05 and d.phase_endpoint is _phase06_phase_endpoint
            return d
        assert d.phase_endpoint is prior04.phase_endpoint, 'Unexpected phase replacement before compact binding.'

        class CompactAngleProxy(prior04.AngleProxy):

            def __init__(self, builder):
                super().__init__(builder)
                self.peak = builder.num_allocated_qubits
                self.allocations = []
                assert self.peak == 43

            def alloc_qubits(self, count):
                result = self.builder.alloc_qubits(count)
                self.peak = max(self.peak, self.builder.num_allocated_qubits)
                self.allocations.append(dict(event='allocate', count=count, owners=self.builder.num_allocated_qubits, wires=list(map(str, result))))
                assert self.builder.num_allocated_qubits <= 48, 'Unpriced compact phase owner'
                return result

            def finish(self):
                assert (self.generic, self.T, self.Clifford) == (34, 4, 0), (self.generic, self.T, self.Clifford)
                assert self.peak == 48 and self.builder.num_allocated_qubits == 43
                return self.records
        _phase06_BINDING = _phase06_SimpleNamespace(previous05=previous05, divider=d, Proxy=CompactAngleProxy)
        d.phase_endpoint = _phase06_phase_endpoint
        return d

def _initialize_tables06():
    global _tables06_BASE_PATH, _tables06_BASE_SHA, _tables06_FROZEN, _tables06_HERE, _tables06_INTEGRATED_ROOT, _tables06_MODEL_SHA, _tables06_NARROW, _tables06_PINS, _tables06_Path, _tables06_RESOURCES, _tables06_SECOND_RETIRED_ADDRESS_SLOTS, _tables06_TableDebt, _tables06_TableDebts, _tables06__BASE, _tables06__IntegratedPath, _tables06___file__, _tables06___name__, _tables06__spec, _tables06_array, _tables06_cb, _tables06_certificate, _tables06_checked_json, _tables06_cleanup_joint16, _tables06_emit_affine_frame, _tables06_hashlib, _tables06_importlib, _tables06_km, _tables06_load_joint16, _tables06_lru_cache, _tables06_model_truths, _tables06_model_values, _tables06_plan_from_json, _tables06_sys
    _tables06_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate06/tables06.py', False).Path
    _tables06_sys = _import_component('sys', 'work/c10/narrow/native/candidate06/tables06.py', True)
    _tables06_HERE = _tables06_Path(_tables06___file__).resolve().parent
    _tables06_BASE_PATH = _tables06_HERE.parent / 'candidate01/tables.py'
    _tables06__spec = _spec('_candidate06_pinned_tables01', _tables06_BASE_PATH)
    _tables06__BASE = _new_module(_tables06__spec)
    _tables06_sys.modules[_tables06__spec.name] = _tables06__BASE
    _tables06__spec.loader.exec_module(_tables06__BASE)
    _tables06_TableDebt = _tables06__BASE.TableDebt
    _tables06_TableDebts = _tables06__BASE.TableDebts
    _tables06_model_values = _tables06__BASE.model_values
    _tables06_model_truths = _tables06__BASE.model_truths
    _tables06_cleanup_joint16 = _tables06__BASE.cleanup_joint16

    def _tables06_emit_affine_frame(builder, fixed, work, rows):
        """Invertible work frame with offset8(raw7) or4(fixed R,a5,a6)."""
        fixed = list(fixed)
        work = list(work)
        rows = list(map(int, rows))
        if len(fixed) not in (3, 7):
            raise ValueError('Unexpected fixed-address chart width.')
        offset = 1 + len(fixed)
        for kind, a, b in _tables06__BASE._row_matrix_inverse_operations([row >> offset for row in rows], len(work)):
            if kind == 'cx':
                builder.cx(work[a], work[b])
            else:
                _tables06__BASE._swap(builder, work[a], work[b])
        for target, row in zip(work, rows):
            if row & 1:
                builder.x(target)
            for bit in range(len(fixed)):
                if row >> 1 + bit & 1:
                    builder.cx(fixed[bit], target)

def _initialize_candidate06_setup():
    global _candidate06_setup_ACCEPTED, _candidate06_setup_BASE, _candidate06_setup_BOUND, _candidate06_setup_COEFFICIENTS37, _candidate06_setup_GATE_PATH, _candidate06_setup_GATE_SHA, _candidate06_setup_HERE, _candidate06_setup_INTEGRATED_ROOT, _candidate06_setup_MODULES, _candidate06_setup_NARROW, _candidate06_setup_NEW_TURN_UNITS50, _candidate06_setup_PAPER, _candidate06_setup_PAPER_SHA, _candidate06_setup_PREVIOUS, _candidate06_setup_Path, _candidate06_setup_SITES, _candidate06_setup__INSTALLED, _candidate06_setup__IntegratedPath, _candidate06_setup___file__, _candidate06_setup___name__, _candidate06_setup_checked_quantized, _candidate06_setup_common, _candidate06_setup_divider, _candidate06_setup_hashlib, _candidate06_setup_importlib, _candidate06_setup_install, _candidate06_setup_json, _candidate06_setup_key, _candidate06_setup_load_baseline, _candidate06_setup_local_module, _candidate06_setup_os, _candidate06_setup_previous, _candidate06_setup_proof50_module, _candidate06_setup_spec, _candidate06_setup_sys, _candidate06_setup_variant_gate, _candidate06_setup_verify_inputs
    _candidate06_setup_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate06/variant.py', False).Path
    _candidate06_setup_os = _import_component('os', 'work/c10/narrow/native/candidate06/variant.py', True)
    _candidate06_setup_sys = _import_component('sys', 'work/c10/narrow/native/candidate06/variant.py', True)
    for _candidate06_setup_key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        _candidate06_setup_os.environ[_candidate06_setup_key] = '1'
    _candidate06_setup_HERE = _candidate06_setup_Path(_candidate06_setup___file__).resolve().parent
    _candidate06_setup_NARROW = _candidate06_setup_HERE.parents[1]
    _candidate06_setup_PREVIOUS = _candidate06_setup_HERE.parent / 'candidate05'
    _candidate06_setup_GATE_PATH = _candidate06_setup_NARROW / 'PAPER_GATE_RECEIPT_018_VARIANT.json'
    _candidate06_setup_GATE_SHA = '99ef9a891d4e99b262b1a452ea48b18c536e91e7017f018b77bc37f1793ccffd'
    _candidate06_setup_spec = _spec('candidate06_pinned_candidate05_variant', _candidate06_setup_PREVIOUS / 'variant.py')
    _candidate06_setup_previous = _new_module(_candidate06_setup_spec)
    _candidate06_setup_sys.modules[_candidate06_setup_spec.name] = _candidate06_setup_previous
    _candidate06_setup_spec.loader.exec_module(_candidate06_setup_previous)
    _candidate06_setup_common = _candidate06_setup_previous.common
    _candidate06_setup_divider = _candidate06_setup_previous.divider
    _candidate06_setup_ACCEPTED = _candidate06_setup_common.checked_json(_candidate06_setup_GATE_PATH, _candidate06_setup_GATE_SHA)
    assert _candidate06_setup_ACCEPTED['native_build_authorized'] and _candidate06_setup_ACCEPTED['all_native_candidates_preserved'] == [1, 2, 3, 4, 5]
    _candidate06_setup__INSTALLED = False
    _candidate06_setup_MODULES = {}

    def _candidate06_setup_local_module(name):
        if name not in _candidate06_setup_MODULES:
            path = _candidate06_setup_HERE / (name + '.py')
            if name in _candidate06_setup_sys.modules:
                module = _candidate06_setup_sys.modules[name]
                pass
            else:
                spec = _spec('candidate06_' + name, path)
                module = _new_module(spec)
                _candidate06_setup_sys.modules[spec.name] = module
                _candidate06_setup_sys.modules[name] = module
                spec.loader.exec_module(module)
            _candidate06_setup_MODULES[name] = module
        return _candidate06_setup_MODULES[name]

    def _candidate06_setup_install():
        global _candidate06_setup__INSTALLED
        pass
        if not _candidate06_setup__INSTALLED:
            _candidate06_setup_previous.install()
            _candidate06_setup_local_module('divider_cleanup06').install(_candidate06_setup_divider)
            _candidate06_setup_local_module('phase06').install(_candidate06_setup_previous)
            _candidate06_setup__INSTALLED = True
        return _candidate06_setup_divider

    def _candidate06_setup_load_baseline(name):
        return _candidate06_setup_previous.load_baseline(name)

def _initialize_phase07():
    global _phase07_BINDING, _phase07_CENTRES, _phase07_Fraction, _phase07_HERE, _phase07_INTEGRATED_ROOT, _phase07_LAST_ANGLE_RECORDS, _phase07_LAST_PHASE_TRACE, _phase07_MODULUS, _phase07_NARROW, _phase07_PINS, _phase07_Path, _phase07_ROUTE_TRACE, _phase07_Recorder, _phase07_SITES, _phase07_SimpleNamespace, _phase07__IntegratedPath, _phase07___file__, _phase07___name__, _phase07_angle_class, _phase07_hashlib, _phase07_install, _phase07_json, _phase07_phase_endpoint, _phase07_raw_phase_endpoint, _phase07_route26, _phase07_verify_sources
    _phase07_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate07/phase07.py', False).Path
    _phase07_Fraction = _import_component('fractions', 'work/c10/narrow/native/candidate07/phase07.py', False).Fraction
    _phase07_SimpleNamespace = _import_component('types', 'work/c10/narrow/native/candidate07/phase07.py', False).SimpleNamespace
    _phase07_HERE = _phase07_Path(_phase07___file__).resolve().parent
    _phase07_NARROW = _phase07_HERE.parents[1]
    _phase07_MODULUS = 1 << 50
    _phase07_CENTRES = (0, -2, -6, 0, -1)
    _phase07_SITES = tuple((f'base_i{i}' for i in range(26))) + tuple((f'overflow_j{j}' for j in range(7))) + ('global_one',)
    _phase07_BINDING = None
    _phase07_LAST_ANGLE_RECORDS = []
    _phase07_LAST_PHASE_TRACE = []
    _phase07_ROUTE_TRACE = []

    def _phase07_verify_sources():
        accepted = _json_loads(_read_text(_phase07_NARROW / 'PAPER_GATE_RECEIPT_022_VARIANT.json'))
        assert accepted['native_build_authorized'] and (accepted['Q'], accepted['expected_Toffolis'], accepted['T'], accepted['R']) == (48, 1584, 4, 33)
        return _json_loads(_read_text(_phase07_NARROW / 'research/ring26_phase/basis.json'))

    def _phase07_angle_class(half_turns):
        angle = _phase07_Fraction(half_turns)
        if angle % _phase07_Fraction(1, 2) == 0:
            return 'Clifford'
        if angle % _phase07_Fraction(1, 4) == 0:
            return 'T'
        return 'generic'

    class _phase07_Recorder:

        def __init__(self, builder):
            self.builder = builder
            self.peak = builder.num_allocated_qubits
            self.generic = self.T = self.Clifford = 0
            self.site = None
            self.fixed = None
            self.records = []
            self.allocations = []
            self.fixed_records = []
            assert self.peak == 43

        def __getattr__(self, name):
            return getattr(self.builder, name)

        def alloc_qubits(self, count):
            wires = self.builder.alloc_qubits(count)
            self.peak = max(self.peak, self.builder.num_allocated_qubits)
            self.allocations.append(dict(event='allocate', count=count, owners=self.builder.num_allocated_qubits, wires=list(map(str, wires))))
            assert self.builder.num_allocated_qubits <= 48, 'Unpriced ring26 endpoint owner'
            return wires

        def z_pow(self, target, half_turns):
            value = _phase07_Fraction(half_turns)
            kind = _phase07_angle_class(value)
            if kind == 'generic':
                assert self.site is not None and self.fixed is None
                i = self.site
                assert i == len(self.records) and i < 33
                assert value == _phase07_Fraction(2 * _phase07_BINDING.angles[i], _phase07_MODULUS)
                self.records.append(dict(index=i, site=_phase07_SITES[i], target=str(target), new_half_turns=str(value), turn_units50=_phase07_BINDING.angles[i], angle_class=kind, emitted=True))
                self.generic += 1
            elif kind == 'T':
                assert self.site is None and self.fixed in ('overflow_j7', 'overflow_j8')
                self.T += 1
                self.fixed_records.append(dict(site=self.fixed, half_turns=str(value), target=str(target), kind='T'))
            else:
                assert self.site is None and self.fixed == 'overflow_j9' and (value == 1)
                self.Clifford += 1
                self.fixed_records.append(dict(site=self.fixed, half_turns=str(value), target=str(target), kind='Clifford'))
            return self.builder.z_pow(target, value)

        def finish(self):
            assert (self.generic, self.T, self.Clifford) == (33, 4, 1)
            assert self.site is None and self.fixed is None
            assert len(self.records) == 34 and self.records[-1]['site'] == 'global_one' and (not self.records[-1]['emitted'])
            assert self.peak == 48 and self.builder.num_allocated_qubits == 43
            assert len(self.fixed_records) == 5
            return self.records

    def _phase07_route26(builder, word, variables, inverse=False):
        """Original centres modulo26, no candidate05 omitted pair."""
        d = _phase07_BINDING.divider
        assert len(word) == 26 and len(set(word)) == 26 and (len(variables) == 6)
        stages = list(range(5))
        gates = []
        counts = []
        if inverse:
            stages.reverse()
        for stage in stages:
            count = 0
            with d._affine_control(builder, variables, d.CONTROLS[stage]) as control:
                for i in range(26):
                    j = (_phase07_CENTRES[stage] - i) % 26
                    if i < j:
                        builder.cswap(control, word[i], word[j])
                        count += 1
                        gates.append(dict(stage=stage, positions=[i, j], arguments=list(map(str, (control, word[i], word[j])))))
            counts.append(dict(stage=stage, swaps=count))
        assert len(gates) == 61 and sorted(((row['stage'], row['swaps']) for row in counts)) == [(0, 12), (1, 12), (2, 12), (3, 12), (4, 13)]
        _phase07_ROUTE_TRACE.append(dict(inverse=inverse, ring_bits=26, centres=list(_phase07_CENTRES), omissions=[], swap_count=61, stages=counts, gates=gates))

    def _phase07_raw_phase_endpoint(builder, token):
        d = _phase07_BINDING.divider
        v, u, flags = (token.v, token.u, token.flags)
        assert (len(v), len(u), len(flags)) == (12, 14, 4) and builder.num_allocated_qubits == 43
        d._sigma25_frame(builder, v, u)
        for q in u[:9]:
            builder.cx(v[0], q)
        builder.cx(v[1], u[9])
        signs = {**token.history, 25: u[10], 26: u[9], 36: u[13]}
        signs.update({j: u[35 - j] for j in range(27, 36)})
        assert sorted(signs) == list(range(12, 37))
        for q in signs.values():
            builder.x(q)
        one = builder.alloc_qubits(1)[0]
        builder.x(one)
        word = [signs[36 - i] for i in range(25)] + [one]
        assert len(set(word)) == 26 and u[11] not in word and (u[12] not in word)
        p = builder.alloc_qubits(1)[0]
        d.xor_polynomial(builder, flags, p, (6, 10))
        c = builder.alloc_qubits(1)[0]
        d.xor_polynomial(builder, flags, c, (10,))
        variables = flags + [p, c]
        assert builder.num_allocated_qubits == 46
        _phase07_route26(builder, word, variables)
        slots = [word[i] for i in _phase07_BINDING.slots]
        for i, q in enumerate(slots):
            builder.site = i
            builder.z_pow(q, _phase07_Fraction(2 * _phase07_BINDING.angles[i], _phase07_MODULUS))
            builder.site = None
        for j in range(10):
            if j == 9:
                builder.fixed = 'overflow_j9'
                builder.z_pow(c, _phase07_Fraction(1))
                builder.fixed = None
            elif j <= 6:
                with d._threshold(builder, variables, j + 1) as control:
                    builder.site = 26 + j
                    d._feature(builder, control, slots[j], _phase07_Fraction(_phase07_BINDING.angles[26 + j], _phase07_MODULUS))
                    builder.site = None
            else:
                with d._threshold(builder, variables, j + 1) as control:
                    builder.fixed = f'overflow_j{j}'
                    d._feature(builder, control, slots[j], _phase07_Fraction(1, 8) if j == 7 else _phase07_Fraction(1, 4))
                    builder.fixed = None
        _phase07_route26(builder, word, variables, inverse=True)
        assert _phase07_BINDING.angles[33] == 0 and len(builder.records) == 33
        builder.records.append(dict(index=33, site='global_one', target=str(one), new_half_turns='0', turn_units50=0, angle_class='Clifford', emitted=False))
        d._erase_polynomial(builder, c, flags, (10,))
        d._erase_polynomial(builder, p, flags, (6, 10))
        builder.x(one)
        builder.free(one)
        for q in signs.values():
            builder.x(q)
        builder.cx(v[1], u[9])
        for q in u[:9]:
            builder.cx(v[0], q)
        d._sigma25_frame(builder, v, u, inverse=True)
        assert builder.num_allocated_qubits == 43

    def _phase07_phase_endpoint(builder, token):
        assert _phase07_BINDING is not None
        proxy = _phase07_Recorder(builder)
        _phase07_ROUTE_TRACE.clear()
        _phase07_raw_phase_endpoint(proxy, token)
        _phase07_LAST_ANGLE_RECORDS.clear()
        _phase07_LAST_ANGLE_RECORDS.extend(proxy.finish())
        _phase07_LAST_PHASE_TRACE.clear()
        _phase07_LAST_PHASE_TRACE.extend(proxy.allocations)
        _phase07_LAST_PHASE_TRACE.append(dict(event='complete', entry_owners=43, exit_owners=builder.num_allocated_qubits, observed_peak_owners=proxy.peak, generic_calls=proxy.generic, T_calls=proxy.T, direct_Clifford_Z_POW_calls=proxy.Clifford, global_identity_validated_and_omitted=True, expected_Toffolis=139, local_HMR_functions=15, all_local_outcomes_repaid_before_exit=True, no_TableDebts_transfer=True, fixed_phase_records=proxy.fixed_records))

    def _phase07_install(previous06, accepted_angles, accepted_phase_gate):
        global _phase07_BINDING
        basis = _phase07_verify_sources()
        angles = tuple(accepted_angles)
        pass
        pass
        d = previous06.divider
        assert list(angles) == accepted_phase_gate['new_angles_turn_units50']
        assert accepted_phase_gate['phase_expected_Toffolis'] == 139 and accepted_phase_gate['endpoint_peak'] == 48
        assert accepted_phase_gate['R'] == 33 and accepted_phase_gate['T'] == 4 and (accepted_phase_gate['phase_entry_exit_owners'] == 43)
        assert tuple(accepted_phase_gate['phase_site_order']) == _phase07_SITES and len(angles) == 34 and (angles[-1] == 0)
        assert all((_phase07_angle_class(_phase07_Fraction(2 * a, _phase07_MODULUS)) == 'generic' for a in angles[:33]))
        assert any((a & 1 for a in angles[:33]))
        if _phase07_BINDING is not None:
            assert _phase07_BINDING.previous06 is previous06 and _phase07_BINDING.angles == angles and (d.phase_endpoint is _phase07_phase_endpoint)
            return d
        assert d.phase_endpoint is previous06.local_module('phase06').phase_endpoint
        assert tuple((tuple(x) for x in basis['controls'])) == tuple(d.CONTROLS)
        _phase07_BINDING = _phase07_SimpleNamespace(previous06=previous06, divider=d, angles=angles, slots=tuple(basis['slots']))
        d.phase_endpoint = _phase07_phase_endpoint
        return d

def _initialize_tables07():
    global _tables07_FROZEN, _tables07_HERE, _tables07_INTEGRATED_ROOT, _tables07_MODEL_SHA, _tables07_NARROW, _tables07_PINS, _tables07_PREVIOUS_PATH, _tables07_PREVIOUS_SHA, _tables07_Path, _tables07_RESOURCES, _tables07_SECOND_RETIRED_ADDRESS_SLOTS, _tables07_TableDebt, _tables07_TableDebts, _tables07__BASE, _tables07__IntegratedPath, _tables07__OLD, _tables07___file__, _tables07___name__, _tables07_array, _tables07_cb, _tables07_certificate, _tables07_checked_json, _tables07_cleanup_joint16, _tables07_common, _tables07_emit_affine_frame, _tables07_hashlib, _tables07_inherited_module, _tables07_km, _tables07_load_joint16, _tables07_lru_cache, _tables07_model_truths, _tables07_model_values, _tables07_plan_from_json
    _tables07_lru_cache = _import_component('functools', 'work/c10/narrow/native/candidate07/tables07.py', False).lru_cache
    _tables07_common = _import_component('variant', 'work/c10/narrow/native/candidate07/tables07.py', False).common
    _tables07_inherited_module = _import_component('variant', 'work/c10/narrow/native/candidate07/tables07.py', False).inherited_module
    _tables07_km = _tables07_common.km
    _tables07_cb = _tables07_common.cb
    _tables07_NARROW = _tables07_common.NARROW
    _tables07_checked_json = _tables07_common.checked_json
    _tables07_plan_from_json = _tables07_common.plan_from_json
    _tables07_array = _tables07_common.array
    _tables07__OLD = _tables07_inherited_module('tables06')
    _tables07__BASE = _tables07__OLD._BASE
    _tables07_TableDebts = _tables07__OLD.TableDebts
    _tables07_model_truths = _tables07__OLD.model_truths
    _tables07_cleanup_joint16 = _tables07__OLD.cleanup_joint16
    _tables07_emit_affine_frame = _tables07__OLD.emit_affine_frame
    assert _tables07_TableDebts is _tables07__OLD.TableDebts and _tables07_cleanup_joint16 is _tables07__OLD.cleanup_joint16
    _tables07_FROZEN = _tables07_NARROW / 'research/joint_loader/frozen'
    _tables07_PINS = {'first': ('loader16_first61_Q48.json', '4857688e595af50828d7bedf0bc745eaaed8d10767e2e6ca6f77802887e1ad48'), 'second': ('loader16_second79_delay_Q48.json', '5276e10525e98c6dbf6dc215e2a525441ba36ce0342e3f2dd937a2720e085da1')}
    _tables07_SECOND_RETIRED_ADDRESS_SLOTS = (0, 1, 2, 4)
    _tables07_RESOURCES = {'first': dict(Toffolis=61, T=0, R=0, other_fixed_owners=26, work_cap=22, existing_input_work=0, new_zero_owners=22, complete_peak=48, return_owners=42, HMR_debts=45), 'second': dict(Toffolis=79, T=0, R=0, other_fixed_owners=27, work_cap=21, existing_input_work=4, new_zero_owners=17, complete_peak=48, return_owners=43, HMR_debts=65), 'cleanup': dict(Toffolis=9, T=0, R=0, complete_peak=44)}

    @_tables07_lru_cache(maxsize=2)
    def _tables07_certificate(which):
        name, digest = _tables07_PINS[which]
        data = _tables07_checked_json(_tables07_FROZEN / name, digest)
        pass
        assert data['status'] == 'COMPLETE_MATHEMATICAL_LOADER_NOT_NATIVE'
        assert data['Toffolis'] == _tables07_RESOURCES[which]['Toffolis']
        assert data['work_cap'] == data['work_peak'] == _tables07_RESOURCES[which]['work_cap']
        assert data['complete_peak'] == 48
        return data

    def _tables07_load_joint16(builder, address7, *, variant, debts):
        """Return current(A13,Hlow3); the second address is ALREADY R-framed.

    First: preserve raw address7, allocate22 zero owners, return16 outputs.
    Second: keep slots3,5,6=(R,rawa5,rawa6); reuse slots0,1,2,4 in workcap21
    and allocate only17 zeros. Those four old logical inputs are consumed:
    the caller sets v[5],v[6],v[7],v[9] to None before using v again.
    The shared TableDebts ledger owns all mixed/input/helper HMR outcomes.
    """
        if variant not in ('first', 'second'):
            raise ValueError('Unknown candidate07 Q48 loader variant.')
        address = list(address7)
        if len(address) != 7 or len(set(address)) != 7 or (not all((isinstance(q, _tables07_km.q) for q in address))):
            raise ValueError('Expected seven current, distinct quantum address owners.')
        if not isinstance(debts, _tables07_TableDebts):
            raise TypeError('Expected the shared pinned TableDebts owner.')
        data = _tables07_certificate(variant)
        entry = builder.num_allocated_qubits
        before_debts = debts.total_recorded
        fixed_slots = (0, 1, 2, 3, 4, 5, 6) if variant == 'first' else (3, 5, 6)
        reusable_slots = () if variant == 'first' else _tables07_SECOND_RETIRED_ADDRESS_SLOTS
        assert data['fixed_address_slots'] == list(fixed_slots)
        assert data['reusable_input_slots'] == list(reusable_slots)
        fixed = [address[i] for i in fixed_slots]
        work = [address[i] for i in reusable_slots]
        cap = data['work_cap']
        available = list(builder.alloc_qubits(cap - len(work)))
        assert len(available) == _tables07_RESOURCES[variant]['new_zero_owners']
        offset = 1 + len(fixed)
        count = 0
        for item in data['steps']:
            kind = item['kind']
            if kind in ('bank', 'CCX_new_coordinate'):
                target = available.pop(0)
                plan = _tables07_plan_from_json(item['plan'])
                _tables07_cb.emit_xor(builder, fixed + work, target, plan)
                work.append(target)
                count += plan.and_count
            elif kind == 'Clifford_zero_dependent_coordinate':
                index = item['index']
                target = work[index]
                _tables07__BASE._affine_xor(builder, fixed, work[:index], target, item['expression'])
                work.pop(index)
                available.append(target)
            elif kind == 'Clifford_frame_then_HMR':
                assert item['affine_fixed_offset'] == offset
                _tables07_emit_affine_frame(builder, fixed, work, item['full_affine_rows'])
                kept = item['retained_count']
                discard = work[kept:]
                assert len(discard) == len(item['discarded_truths'])
                for wire, truth in zip(discard, item['discarded_truths']):
                    debts.erase(builder, wire, int(truth, 16))
                    available.append(wire)
                work = work[:kept]
            elif kind == 'virtual_affine_product':
                pass
            elif kind == 'XOR_product_existing_coordinate':
                assert item['target_index'] == 0
                plan = _tables07_plan_from_json(item['plan'])
                _tables07_cb.emit_xor(builder, fixed + work[1:], work[0], plan)
                count += plan.and_count
            elif kind == 'final_output_Clifford_frame':
                _tables07_emit_affine_frame(builder, fixed, work, [int(row) << offset for row in item['matrix_rows']])
            else:
                raise AssertionError(('Unknown frozen Q48 loader operation', kind))
            assert len(work) + len(available) == cap and len(set(work + available)) == cap
            assert not set(fixed) & set(work + available)
        assert len(work) == 16 and count == _tables07_RESOURCES[variant]['Toffolis']
        assert debts.total_recorded - before_debts == _tables07_RESOURCES[variant]['HMR_debts']
        if available:
            builder.free(_tables07_array(available))
        assert builder.num_allocated_qubits == entry + 16 - len(reusable_slots)
        return (list(work[:13]), list(work[13:]))

def _initialize_candidate07_setup():
    global _candidate07_setup_ACCEPTED, _candidate07_setup_BASE, _candidate07_setup_GATE_PATH, _candidate07_setup_GATE_SHA, _candidate07_setup_HERE, _candidate07_setup_INTEGRATED_ROOT, _candidate07_setup_MODULES, _candidate07_setup_NARROW, _candidate07_setup_NEW_TURN_UNITS50, _candidate07_setup_PAPER, _candidate07_setup_PAPER_SHA, _candidate07_setup_PHASE_GATE, _candidate07_setup_PHASE_GATE_SHA, _candidate07_setup_PREVIOUS, _candidate07_setup_Path, _candidate07_setup_SITES, _candidate07_setup__INSTALLED, _candidate07_setup__IntegratedPath, _candidate07_setup___file__, _candidate07_setup___name__, _candidate07_setup_accuracy_receipt, _candidate07_setup_common, _candidate07_setup_divider, _candidate07_setup_hashlib, _candidate07_setup_importlib, _candidate07_setup_inherited_module, _candidate07_setup_install, _candidate07_setup_json, _candidate07_setup_key, _candidate07_setup_load_baseline, _candidate07_setup_local_module, _candidate07_setup_os, _candidate07_setup_previous, _candidate07_setup_spec, _candidate07_setup_sys, _candidate07_setup_variant_gate, _candidate07_setup_verify_inputs
    _candidate07_setup_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate07/variant.py', False).Path
    _candidate07_setup_os = _import_component('os', 'work/c10/narrow/native/candidate07/variant.py', True)
    _candidate07_setup_sys = _import_component('sys', 'work/c10/narrow/native/candidate07/variant.py', True)
    for _candidate07_setup_key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        _candidate07_setup_os.environ[_candidate07_setup_key] = '1'
    _candidate07_setup_HERE = _candidate07_setup_Path(_candidate07_setup___file__).resolve().parent
    _candidate07_setup_NARROW = _candidate07_setup_HERE.parents[1]
    _candidate07_setup_PREVIOUS = _candidate07_setup_HERE.parent / 'candidate06'
    _candidate07_setup_GATE_PATH = _candidate07_setup_NARROW / 'PAPER_GATE_RECEIPT_022_VARIANT.json'
    _candidate07_setup_GATE_SHA = 'f8cfe4331b37a5184a4aab17ee85b4ac892c08c2cfb863fc4b1c1b3c9978262e'
    _candidate07_setup_PAPER_SHA = '49ce6e7007b19abcd533b82a9f291b617cbc1c864a3d66287c0e63a87ebb82c4'
    _candidate07_setup_PHASE_GATE_SHA = 'b579924175ee8e73c61c2f945b2d85e8ba2e536a8dbd8288a8332628142cd569'
    _candidate07_setup_spec = _spec('candidate07_pinned_candidate06_variant', _candidate07_setup_PREVIOUS / 'variant.py')
    _candidate07_setup_previous = _new_module(_candidate07_setup_spec)
    _candidate07_setup_sys.modules[_candidate07_setup_spec.name] = _candidate07_setup_previous
    _candidate07_setup_spec.loader.exec_module(_candidate07_setup_previous)
    _candidate07_setup_common = _candidate07_setup_previous.common
    _candidate07_setup_divider = _candidate07_setup_previous.divider
    _candidate07_setup_ACCEPTED = _candidate07_setup_common.checked_json(_candidate07_setup_GATE_PATH, _candidate07_setup_GATE_SHA)
    _candidate07_setup_PAPER = _candidate07_setup_common.checked_json(_candidate07_setup_NARROW / _candidate07_setup_ACCEPTED['paper_gate_path'], _candidate07_setup_PAPER_SHA)
    _candidate07_setup_PHASE_GATE = _candidate07_setup_common.checked_json(_candidate07_setup_NARROW / _candidate07_setup_PAPER['phase_gate_path'], _candidate07_setup_PHASE_GATE_SHA)
    _candidate07_setup_NEW_TURN_UNITS50 = tuple(_candidate07_setup_PAPER['new_angles_turn_units50'])
    assert _candidate07_setup_ACCEPTED['native_build_authorized']
    assert _candidate07_setup_ACCEPTED['all_native_candidates_preserved'] == [1, 2, 3, 4, 5, 6]
    _candidate07_setup__INSTALLED = False
    _candidate07_setup_MODULES = {}

    def _candidate07_setup_local_module(name):
        if name not in _candidate07_setup_MODULES:
            path = _candidate07_setup_HERE / (name + '.py')
            if name in _candidate07_setup_sys.modules:
                module = _candidate07_setup_sys.modules[name]
                pass
            else:
                spec = _spec('candidate07_' + name, path)
                module = _new_module(spec)
                _candidate07_setup_sys.modules[spec.name] = module
                _candidate07_setup_sys.modules[name] = module
                spec.loader.exec_module(module)
            _candidate07_setup_MODULES[name] = module
        return _candidate07_setup_MODULES[name]

    def _candidate07_setup_install():
        global _candidate07_setup__INSTALLED
        pass
        if not _candidate07_setup__INSTALLED:
            _candidate07_setup_previous.install()
            _candidate07_setup_local_module('phase07').install(_candidate07_setup_previous, _candidate07_setup_NEW_TURN_UNITS50, _candidate07_setup_PHASE_GATE)
            _candidate07_setup__INSTALLED = True
        return _candidate07_setup_divider

    def _candidate07_setup_load_baseline(name):
        return _candidate07_setup_previous.load_baseline(name)

    def _candidate07_setup_inherited_module(name):
        """Keep the old module/class identity while reusing its arithmetic only."""
        return _candidate07_setup_previous.local_module(name)

def _initialize_pair_normalization():
    global _pair_normalization_COUNT_BOOK, _pair_normalization_COUNT_FULL, _pair_normalization_COUNT_G, _pair_normalization_COUNT_RAW, _pair_normalization_Counter, _pair_normalization_HERE, _pair_normalization_INTEGRATED_ROOT, _pair_normalization_MAX_X, _pair_normalization_NARROW, _pair_normalization_ODD_FIRST, _pair_normalization_ODD_OTHER, _pair_normalization_PaperCounter, _pair_normalization_Path, _pair_normalization_THRESHOLD_PLANS, _pair_normalization_TruthPhaseBuilder, _pair_normalization__IntegratedPath, _pair_normalization___file__, _pair_normalization___name__, _pair_normalization_anf_from_truth, _pair_normalization_asdict, _pair_normalization_binary_to_thermometer, _pair_normalization_cb, _pair_normalization_certify, _pair_normalization_expr, _pair_normalization_forward, _pair_normalization_hashlib, _pair_normalization_input_truths, _pair_normalization_inverse, _pair_normalization_j, _pair_normalization_json, _pair_normalization_km, _pair_normalization_main, _pair_normalization_operations, _pair_normalization_os, _pair_normalization_p, _pair_normalization_paper, _pair_normalization_route, _pair_normalization_route_certificate, _pair_normalization_small_plan, _pair_normalization_sys, _pair_normalization_t, _pair_normalization_time
    _pair_normalization_Path = _import_component('pathlib', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).Path
    _pair_normalization_os = _import_component('os', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _pair_normalization_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _pair_normalization_os.environ['OMP_NUM_THREADS'] = '1'
    _pair_normalization_sys = _import_component('sys', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _pair_normalization_json = _import_component('json', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _pair_normalization_time = _import_component('time', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _pair_normalization_HERE = _pair_normalization_Path(_pair_normalization___file__).resolve().parent
    _pair_normalization_NARROW = _pair_normalization_HERE.parents[1]
    _pair_normalization_sys.path.insert(0, str(_pair_normalization_NARROW / 'research/stream_phase'))
    _pair_normalization_PaperCounter = _import_component('drive_paper_ledger', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).PaperCounter
    _pair_normalization_km = _import_component('drive_paper_ledger', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).km
    _pair_normalization_cb = _import_component('codebook', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False)
    _pair_normalization_operations = _import_component('stage94_bit_routing_math', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).operations
    _pair_normalization_route_certificate = _import_component('stage94_bit_routing_math', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).certificate
    _pair_normalization_binary_to_thermometer = _import_component('thermometer_cleanup', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).binary_to_thermometer
    _pair_normalization_anf_from_truth = _import_component('fusion.compiler', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).anf_from_truth
    _pair_normalization_asdict = _import_component('dataclasses', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).asdict
    _pair_normalization_MAX_X = 3 * (2 ** 10 - 2) ** 2
    _pair_normalization_COUNT_FULL = (1 << 11) - 1
    _pair_normalization_COUNT_RAW = _pair_normalization_cb.word_functions(range(11), 4)
    _pair_normalization_COUNT_G = _pair_normalization_COUNT_RAW[0] & _pair_normalization_COUNT_RAW[1]
    _pair_normalization_COUNT_BOOK = _pair_normalization_cb.Codebook(_pair_normalization_COUNT_RAW + [_pair_normalization_COUNT_G], size=11)
    _pair_normalization_THRESHOLD_PLANS = []
    for _pair_normalization_j in range(1, 11):
        _pair_normalization_t = sum((int(k >= _pair_normalization_j) << k for k in range(11)))
        _pair_normalization_expr = _pair_normalization_COUNT_BOOK.span.solve(_pair_normalization_t)
        assert _pair_normalization_expr is not None
        _pair_normalization_p = _pair_normalization_COUNT_BOOK.decode_expression(_pair_normalization_expr)
        assert _pair_normalization_p.evaluate_functions(_pair_normalization_COUNT_RAW + [_pair_normalization_COUNT_G], _pair_normalization_COUNT_FULL) == _pair_normalization_t
        _pair_normalization_THRESHOLD_PLANS.append(_pair_normalization_p)

    def _pair_normalization_small_plan(n, fn):
        terms = _pair_normalization_anf_from_truth(tuple((fn(*[x >> i & 1 for i in range(n)]) for x in range(1 << n))))
        assert all((t.bit_count() <= 2 for t in terms))
        linear = sum((t for t in terms if t.bit_count() == 1))
        edges = tuple((tuple((i for i in range(n) if t >> i & 1)) for t in terms if t.bit_count() == 2))
        return _pair_normalization_cb.QuadraticCodePlan(n, 0 in terms, linear, edges, (), linear)
    _pair_normalization_ODD_FIRST = _pair_normalization_small_plan(2, lambda t1, h: 1 ^ h ^ h & t1)
    _pair_normalization_ODD_OTHER = _pair_normalization_small_plan(3, lambda prev, cur, h: prev ^ h & (prev ^ cur))

    def _pair_normalization_route(builder, x, T, inverse=False):
        seq = list(_pair_normalization_operations(11))
        if inverse:
            seq.reverse()
        swaps = 0
        for operation in seq:
            terms = [i for i in operation['prefix_terms'] if i <= 10]
            assert terms and 0 not in terms
            control = T[terms[0] - 1]
            others = [T[i - 1] for i in terms[1:]]
            for q in others:
                builder.cx(q, control)
            for lane in range(2):
                builder.cswap(control, x[2 * operation['first'] + lane], x[2 * operation['second'] + lane])
                swaps += 1
            for q in reversed(others):
                builder.cx(q, control)
        assert swaps == 34

    def _pair_normalization_forward(builder, x, flags):
        x = list(x)
        flags = list(flags)
        assert len(x) == 22 and len(flags) == 4
        P = []
        for length in range(1, 21):
            q = builder.alloc_qubits(1)[0]
            data = x[22 - length]
            if length == 1:
                builder.x(q)
                builder.cx(data, q)
            elif length == 2:
                builder.cx(P[-1], q)
                builder.cx(data, q)
            else:
                builder.x(data)
                builder.ccx(P[-1], data, q)
                builder.x(data)
            P.append(q)
        T = P[1::2]
        for bit, flag in enumerate(flags):
            for j in range(1 << bit, 11, 1 << bit):
                builder.cx(T[j - 1], flag)
        _pair_normalization_route(builder, x, T)
        for j in range(1, 11):
            q = P[2 * j - 2]
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            if j == 1:
                _pair_normalization_cb.emit_phase(builder, [T[0], x[21]], m, _pair_normalization_ODD_FIRST)
            else:
                _pair_normalization_cb.emit_phase(builder, [T[j - 2], T[j - 1], x[21]], m, _pair_normalization_ODD_OTHER)
            builder.free(m)
            builder.free(q)
        g = builder.alloc_qubits(1)[0]
        builder.ccx(flags[0], flags[1], g)
        for q, p in zip(T, _pair_normalization_THRESHOLD_PLANS):
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            _pair_normalization_cb.emit_phase(builder, flags + [g], m, p)
            builder.free(m)
            builder.free(q)
        builder.del_and(flags[0], flags[1], g)
        builder.free(g)

    def _pair_normalization_inverse(builder, x, flags):
        x = list(x)
        flags = list(flags)
        T, helpers = _pair_normalization_binary_to_thermometer(builder, flags, 10)
        _pair_normalization_route(builder, x, T, inverse=True)
        for j in reversed(range(1, 11)):
            q = T[j - 1]
            a = x[22 - 2 * j]
            bb = x[23 - 2 * j]
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            if j == 1:
                builder.z(m)
            builder.push_condition(m)
            if j == 1:
                builder.z(a)
                builder.z(bb)
                builder.cz(a, bb)
            else:
                prev = T[j - 2]
                builder.z(prev)
                builder.cz(prev, a)
                builder.cz(prev, bb)
                builder.ccz(prev, a, bb)
            builder.pop_condition()
            builder.free(m)
        builder.free(_pair_normalization_km.array(helpers))

    class _pair_normalization_Counter(_pair_normalization_PaperCounter):

        def swap(self, *args):
            pass

    class _pair_normalization_TruthPhaseBuilder(_pair_normalization_Counter):
        """Truth-vector data and independent linear HMR phase symbols."""

        def __init__(self, cap, full, valid):
            super().__init__(cap)
            self.full = full
            self.valid = valid
            self.values = {}
            self.phases = {}
            self.measurements = 0

        def alloc_qubits(self, n):
            out = super().alloc_qubits(n)
            for q in out:
                self.values[q] = 0
            return out

        def value(self, q):
            if q is True:
                return self.full
            if q is False:
                return 0
            assert isinstance(q, _pair_normalization_km.q)
            return self.values[q]

        def free(self, x):
            if isinstance(x, _pair_normalization_km.q):
                assert not self.value(x) & self.valid, ('dirty_free', str(x))
            return super().free(x)

        def x(self, q):
            assert not self.stack and isinstance(q, _pair_normalization_km.q)
            self.values[q] ^= self.full

        def cx(self, a, t):
            assert not self.stack and isinstance(t, _pair_normalization_km.q)
            self.values[t] ^= self.value(a)

        def ccx(self, a, b, t):
            assert not self.stack
            self._charge()
            self.values[t] ^= self.value(a) & self.value(b)

        def swap(self, a, b):
            self.values[a], self.values[b] = (self.values[b], self.values[a])

        def cswap(self, c, a, b):
            assert not self.stack
            self._charge()
            delta = self.value(c) & (self.value(a) ^ self.value(b))
            self.values[a] ^= delta
            self.values[b] ^= delta

        def _phase(self, value, extra=None):
            active = list(self.stack)
            if extra is not None:
                active.append(extra)
            assert len(set(active)) <= 1, ('nonlinear_measurement_phase_not_supported', active)
            key = active[0] if active else None
            self.phases[key] = self.phases.get(key, 0) ^ value

        def z(self, q):
            if isinstance(q, _pair_normalization_km.b):
                self._phase(self.full, extra=q)
            else:
                self._phase(self.value(q))

        def cz(self, a, b):
            self._phase(self.value(a) & self.value(b))

        def ccz(self, a, b, c):
            self._charge()
            self._phase(self.value(a) & self.value(b) & self.value(c))

        def hmr(self, q, m):
            assert not self.stack
            self.phases[m] = self.phases.get(m, 0) ^ self.value(q)
            self.values[q] = 0
            self.measurements += 1

        def del_and(self, a, b, t):
            assert self.value(t) & self.valid == self.value(a) & self.value(b) & self.valid
            m = self.alloc_bits(1)[0]
            self.hmr(t, m)
            self.push_condition(m)
            self.cz(a, b)
            self.pop_condition()
            self.free(m)

        def check_phase(self):
            assert all((not v & self.valid for v in self.phases.values())), 'unpaid_measurement_phase'

    def _pair_normalization_input_truths():
        nbytes = 1 << 19
        rows = []
        for i in range(22):
            if i < 3:
                data = bytes([170 if i == 0 else 204 if i == 1 else 240]) * nbytes
            else:
                length = 1 << i - 3
                data = (bytes(length) + bytes([255]) * length) * (nbytes // (2 * length))
            rows.append(int.from_bytes(data, 'little'))
        return rows

    def _pair_normalization_certify():
        start = _pair_normalization_time.monotonic()
        size = 1 << 22
        full = (1 << size) - 1
        valid = (1 << _pair_normalization_MAX_X + 1) - 2
        src = _pair_normalization_input_truths()
        b = _pair_normalization_TruthPhaseBuilder(49, full, valid)
        x = list(b.alloc_qubits(22))
        flags = list(b.alloc_qubits(4))
        for q, v in zip(x, src):
            b.values[q] = v
        expected = [0] * 22
        expected_flags = [0] * 4
        for k in range(11):
            lo = 1 << 20 - 2 * k
            hi = min(_pair_normalization_MAX_X + 1, 1 << 22 - 2 * k)
            mask = (1 << hi) - (1 << lo) if hi > lo else 0
            for i in range(2 * k, 22):
                expected[i] ^= mask & src[i - 2 * k]
            for bit in range(4):
                if k >> bit & 1:
                    expected_flags[bit] ^= mask
        _pair_normalization_forward(b, x, flags)
        assert all(((b.value(q) ^ v) & valid == 0 for q, v in zip(x, expected))), 'wrong_pair_normalization'
        assert all(((b.value(q) ^ v) & valid == 0 for q, v in zip(flags, expected_flags))), 'wrong_pair_count'
        assert b.num_allocated_qubits == 26
        b.check_phase()
        f = float(b.count)
        fpeak = b.peak
        fm = b.measurements
        _pair_normalization_inverse(b, x, flags)
        assert all(((b.value(q) ^ v) & valid == 0 for q, v in zip(x, src))), 'input_not_restored'
        assert all((b.value(q) & valid == 0 for q in flags)), 'count_not_cleared'
        assert b.num_allocated_qubits == 26
        b.check_phase()
        total = float(b.count)
        assert (f, total) == (53, 97.5), (f, total)
        return dict(status='EXACT_ALL_INPUT_AND_ALL_HMR_PHASE_CERTIFICATE_NOT_NATIVE', original_inputs=_pair_normalization_MAX_X, truth_vector_domain_bits=22, required_interval=[1, _pair_normalization_MAX_X], normalized_map='n=x*4**k, k=floor((22-bit_length(x))/2), n in[2^20,2^22)', mathematical_phase_error=0, all_original_bits_restored=True, all_scratch_and_flags_zero=True, forward_measurements=fm, total_independent_HMR_symbols=b.measurements, phase_proof='Every HMR outcome is an independent symbolic coefficient; each complete coefficient truth vector vanishes on every official input.', forward_E=f, inverse_expected_E=total - f, total_expected_E=total, peak=fpeak, T=0, R=0, seconds=_pair_normalization_time.monotonic() - start, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    def _pair_normalization_paper(cap):
        b = _pair_normalization_Counter(cap)
        x = list(b.alloc_qubits(22))
        flags = list(b.alloc_qubits(4))
        _pair_normalization_forward(b, x, flags)
        f = float(b.count)
        fp = b.peak
        assert b.num_allocated_qubits == 26
        b.peak = 26
        _pair_normalization_inverse(b, x, flags)
        assert b.num_allocated_qubits == 26
        return dict(Q_cap=cap, forward_E=f, inverse_expected_E=float(b.count) - f, total_expected_E=float(b.count), forward_peak=fp, inverse_peak=b.peak, T=0, R=0)

    def _pair_normalization_main():
        result = dict(scope='NEW_PAIR_NORMALIZATION_PAPER_AND_EXACT_BOOLEAN_ONLY', route=_pair_normalization_route_certificate(11), threshold_plans=[_pair_normalization_asdict(p) for p in _pair_normalization_THRESHOLD_PLANS], certificate=_pair_normalization_certify(), paper=[_pair_normalization_paper(q) for q in range(46, 53)], excluded_transfer='The122E Stage94 semilog/packed interface is not used.', native_gate='Use only after the full actual lifecycle ledger is updated and clears its paper gate; native proof still required.')
        (_pair_normalization_HERE / 'pair_normalization.json').write_text(_pair_normalization_json.dumps(result, indent=2) + '\n')
        print(_pair_normalization_json.dumps({'certificate': result['certificate'], 'paper': result['paper']}, indent=2))
    if _pair_normalization___name__ == '__main__':
        _pair_normalization_main()

def _initialize_pair_normalization_private():
    global _pair_normalization_private_COUNT_BOOK, _pair_normalization_private_COUNT_FULL, _pair_normalization_private_COUNT_G, _pair_normalization_private_COUNT_RAW, _pair_normalization_private_Counter, _pair_normalization_private_HERE, _pair_normalization_private_INTEGRATED_ROOT, _pair_normalization_private_MAX_X, _pair_normalization_private_NARROW, _pair_normalization_private_ODD_FIRST, _pair_normalization_private_ODD_OTHER, _pair_normalization_private_PaperCounter, _pair_normalization_private_Path, _pair_normalization_private_THRESHOLD_PLANS, _pair_normalization_private_TruthPhaseBuilder, _pair_normalization_private__IntegratedPath, _pair_normalization_private___file__, _pair_normalization_private___name__, _pair_normalization_private_anf_from_truth, _pair_normalization_private_asdict, _pair_normalization_private_binary_to_thermometer, _pair_normalization_private_cb, _pair_normalization_private_certify, _pair_normalization_private_expr, _pair_normalization_private_forward, _pair_normalization_private_hashlib, _pair_normalization_private_input_truths, _pair_normalization_private_inverse, _pair_normalization_private_j, _pair_normalization_private_json, _pair_normalization_private_km, _pair_normalization_private_main, _pair_normalization_private_operations, _pair_normalization_private_os, _pair_normalization_private_p, _pair_normalization_private_paper, _pair_normalization_private_route, _pair_normalization_private_route_certificate, _pair_normalization_private_small_plan, _pair_normalization_private_sys, _pair_normalization_private_t, _pair_normalization_private_time
    _pair_normalization_private_Path = _import_component('pathlib', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).Path
    _pair_normalization_private_os = _import_component('os', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _pair_normalization_private_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _pair_normalization_private_os.environ['OMP_NUM_THREADS'] = '1'
    _pair_normalization_private_sys = _import_component('sys', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _pair_normalization_private_json = _import_component('json', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _pair_normalization_private_time = _import_component('time', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _pair_normalization_private_HERE = _pair_normalization_private_Path(_pair_normalization_private___file__).resolve().parent
    _pair_normalization_private_NARROW = _pair_normalization_private_HERE.parents[1]
    _pair_normalization_private_sys.path.insert(0, str(_pair_normalization_private_NARROW / 'research/stream_phase'))
    _pair_normalization_private_PaperCounter = _import_component('drive_paper_ledger', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).PaperCounter
    _pair_normalization_private_km = _import_component('drive_paper_ledger', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).km
    _pair_normalization_private_cb = _import_component('codebook', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False)
    _pair_normalization_private_operations = _import_component('stage94_bit_routing_math', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).operations
    _pair_normalization_private_route_certificate = _import_component('stage94_bit_routing_math', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).certificate
    _pair_normalization_private_binary_to_thermometer = _import_component('thermometer_cleanup', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).binary_to_thermometer
    _pair_normalization_private_anf_from_truth = _import_component('fusion.compiler', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).anf_from_truth
    _pair_normalization_private_asdict = _import_component('dataclasses', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).asdict
    _pair_normalization_private_MAX_X = 3 * (2 ** 10 - 2) ** 2
    _pair_normalization_private_COUNT_FULL = (1 << 11) - 1
    _pair_normalization_private_COUNT_RAW = _pair_normalization_private_cb.word_functions(range(11), 4)
    _pair_normalization_private_COUNT_G = _pair_normalization_private_COUNT_RAW[0] & _pair_normalization_private_COUNT_RAW[1]
    _pair_normalization_private_COUNT_BOOK = _pair_normalization_private_cb.Codebook(_pair_normalization_private_COUNT_RAW + [_pair_normalization_private_COUNT_G], size=11)
    _pair_normalization_private_THRESHOLD_PLANS = []
    for _pair_normalization_private_j in range(1, 11):
        _pair_normalization_private_t = sum((int(k >= _pair_normalization_private_j) << k for k in range(11)))
        _pair_normalization_private_expr = _pair_normalization_private_COUNT_BOOK.span.solve(_pair_normalization_private_t)
        assert _pair_normalization_private_expr is not None
        _pair_normalization_private_p = _pair_normalization_private_COUNT_BOOK.decode_expression(_pair_normalization_private_expr)
        assert _pair_normalization_private_p.evaluate_functions(_pair_normalization_private_COUNT_RAW + [_pair_normalization_private_COUNT_G], _pair_normalization_private_COUNT_FULL) == _pair_normalization_private_t
        _pair_normalization_private_THRESHOLD_PLANS.append(_pair_normalization_private_p)

    def _pair_normalization_private_small_plan(n, fn):
        terms = _pair_normalization_private_anf_from_truth(tuple((fn(*[x >> i & 1 for i in range(n)]) for x in range(1 << n))))
        assert all((t.bit_count() <= 2 for t in terms))
        linear = sum((t for t in terms if t.bit_count() == 1))
        edges = tuple((tuple((i for i in range(n) if t >> i & 1)) for t in terms if t.bit_count() == 2))
        return _pair_normalization_private_cb.QuadraticCodePlan(n, 0 in terms, linear, edges, (), linear)
    _pair_normalization_private_ODD_FIRST = _pair_normalization_private_small_plan(2, lambda t1, h: 1 ^ h ^ h & t1)
    _pair_normalization_private_ODD_OTHER = _pair_normalization_private_small_plan(3, lambda prev, cur, h: prev ^ h & (prev ^ cur))

    def _pair_normalization_private_route(builder, x, T, inverse=False):
        seq = list(_pair_normalization_private_operations(11))
        if inverse:
            seq.reverse()
        swaps = 0
        for operation in seq:
            terms = [i for i in operation['prefix_terms'] if i <= 10]
            assert terms and 0 not in terms
            control = T[terms[0] - 1]
            others = [T[i - 1] for i in terms[1:]]
            for q in others:
                builder.cx(q, control)
            for lane in range(2):
                builder.cswap(control, x[2 * operation['first'] + lane], x[2 * operation['second'] + lane])
                swaps += 1
            for q in reversed(others):
                builder.cx(q, control)
        assert swaps == 34

    def _pair_normalization_private_forward(builder, x, flags):
        x = list(x)
        flags = list(flags)
        assert len(x) == 22 and len(flags) == 4
        P = []
        for length in range(1, 21):
            q = builder.alloc_qubits(1)[0]
            data = x[22 - length]
            if length == 1:
                builder.x(q)
                builder.cx(data, q)
            elif length == 2:
                builder.cx(P[-1], q)
                builder.cx(data, q)
            else:
                builder.x(data)
                builder.ccx(P[-1], data, q)
                builder.x(data)
            P.append(q)
        T = P[1::2]
        for bit, flag in enumerate(flags):
            for j in range(1 << bit, 11, 1 << bit):
                builder.cx(T[j - 1], flag)
        _pair_normalization_private_route(builder, x, T)
        for j in range(1, 11):
            q = P[2 * j - 2]
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            if j == 1:
                _pair_normalization_private_cb.emit_phase(builder, [T[0], x[21]], m, _pair_normalization_private_ODD_FIRST)
            else:
                _pair_normalization_private_cb.emit_phase(builder, [T[j - 2], T[j - 1], x[21]], m, _pair_normalization_private_ODD_OTHER)
            builder.free(m)
            builder.free(q)
        g = builder.alloc_qubits(1)[0]
        builder.ccx(flags[0], flags[1], g)
        for q, p in zip(T, _pair_normalization_private_THRESHOLD_PLANS):
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            _pair_normalization_private_cb.emit_phase(builder, flags + [g], m, p)
            builder.free(m)
            builder.free(q)
        builder.del_and(flags[0], flags[1], g)
        builder.free(g)

    def _pair_normalization_private_inverse(builder, x, flags):
        x = list(x)
        flags = list(flags)
        T, helpers = _pair_normalization_private_binary_to_thermometer(builder, flags, 10)
        _pair_normalization_private_route(builder, x, T, inverse=True)
        for j in reversed(range(1, 11)):
            q = T[j - 1]
            a = x[22 - 2 * j]
            bb = x[23 - 2 * j]
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            if j == 1:
                builder.z(m)
            builder.push_condition(m)
            if j == 1:
                builder.z(a)
                builder.z(bb)
                builder.cz(a, bb)
            else:
                prev = T[j - 2]
                builder.z(prev)
                builder.cz(prev, a)
                builder.cz(prev, bb)
                builder.ccz(prev, a, bb)
            builder.pop_condition()
            builder.free(m)
        builder.free(_pair_normalization_private_km.array(helpers))

    class _pair_normalization_private_Counter(_pair_normalization_private_PaperCounter):

        def swap(self, *args):
            pass

    class _pair_normalization_private_TruthPhaseBuilder(_pair_normalization_private_Counter):
        """Truth-vector data and independent linear HMR phase symbols."""

        def __init__(self, cap, full, valid):
            super().__init__(cap)
            self.full = full
            self.valid = valid
            self.values = {}
            self.phases = {}
            self.measurements = 0

        def alloc_qubits(self, n):
            out = super().alloc_qubits(n)
            for q in out:
                self.values[q] = 0
            return out

        def value(self, q):
            if q is True:
                return self.full
            if q is False:
                return 0
            assert isinstance(q, _pair_normalization_private_km.q)
            return self.values[q]

        def free(self, x):
            if isinstance(x, _pair_normalization_private_km.q):
                assert not self.value(x) & self.valid, ('dirty_free', str(x))
            return super().free(x)

        def x(self, q):
            assert not self.stack and isinstance(q, _pair_normalization_private_km.q)
            self.values[q] ^= self.full

        def cx(self, a, t):
            assert not self.stack and isinstance(t, _pair_normalization_private_km.q)
            self.values[t] ^= self.value(a)

        def ccx(self, a, b, t):
            assert not self.stack
            self._charge()
            self.values[t] ^= self.value(a) & self.value(b)

        def swap(self, a, b):
            self.values[a], self.values[b] = (self.values[b], self.values[a])

        def cswap(self, c, a, b):
            assert not self.stack
            self._charge()
            delta = self.value(c) & (self.value(a) ^ self.value(b))
            self.values[a] ^= delta
            self.values[b] ^= delta

        def _phase(self, value, extra=None):
            active = list(self.stack)
            if extra is not None:
                active.append(extra)
            assert len(set(active)) <= 1, ('nonlinear_measurement_phase_not_supported', active)
            key = active[0] if active else None
            self.phases[key] = self.phases.get(key, 0) ^ value

        def z(self, q):
            if isinstance(q, _pair_normalization_private_km.b):
                self._phase(self.full, extra=q)
            else:
                self._phase(self.value(q))

        def cz(self, a, b):
            self._phase(self.value(a) & self.value(b))

        def ccz(self, a, b, c):
            self._charge()
            self._phase(self.value(a) & self.value(b) & self.value(c))

        def hmr(self, q, m):
            assert not self.stack
            self.phases[m] = self.phases.get(m, 0) ^ self.value(q)
            self.values[q] = 0
            self.measurements += 1

        def del_and(self, a, b, t):
            assert self.value(t) & self.valid == self.value(a) & self.value(b) & self.valid
            m = self.alloc_bits(1)[0]
            self.hmr(t, m)
            self.push_condition(m)
            self.cz(a, b)
            self.pop_condition()
            self.free(m)

        def check_phase(self):
            assert all((not v & self.valid for v in self.phases.values())), 'unpaid_measurement_phase'

    def _pair_normalization_private_input_truths():
        nbytes = 1 << 19
        rows = []
        for i in range(22):
            if i < 3:
                data = bytes([170 if i == 0 else 204 if i == 1 else 240]) * nbytes
            else:
                length = 1 << i - 3
                data = (bytes(length) + bytes([255]) * length) * (nbytes // (2 * length))
            rows.append(int.from_bytes(data, 'little'))
        return rows

    def _pair_normalization_private_certify():
        start = _pair_normalization_private_time.monotonic()
        size = 1 << 22
        full = (1 << size) - 1
        valid = (1 << _pair_normalization_private_MAX_X + 1) - 2
        src = _pair_normalization_private_input_truths()
        b = _pair_normalization_private_TruthPhaseBuilder(49, full, valid)
        x = list(b.alloc_qubits(22))
        flags = list(b.alloc_qubits(4))
        for q, v in zip(x, src):
            b.values[q] = v
        expected = [0] * 22
        expected_flags = [0] * 4
        for k in range(11):
            lo = 1 << 20 - 2 * k
            hi = min(_pair_normalization_private_MAX_X + 1, 1 << 22 - 2 * k)
            mask = (1 << hi) - (1 << lo) if hi > lo else 0
            for i in range(2 * k, 22):
                expected[i] ^= mask & src[i - 2 * k]
            for bit in range(4):
                if k >> bit & 1:
                    expected_flags[bit] ^= mask
        _pair_normalization_private_forward(b, x, flags)
        assert all(((b.value(q) ^ v) & valid == 0 for q, v in zip(x, expected))), 'wrong_pair_normalization'
        assert all(((b.value(q) ^ v) & valid == 0 for q, v in zip(flags, expected_flags))), 'wrong_pair_count'
        assert b.num_allocated_qubits == 26
        b.check_phase()
        f = float(b.count)
        fpeak = b.peak
        fm = b.measurements
        _pair_normalization_private_inverse(b, x, flags)
        assert all(((b.value(q) ^ v) & valid == 0 for q, v in zip(x, src))), 'input_not_restored'
        assert all((b.value(q) & valid == 0 for q in flags)), 'count_not_cleared'
        assert b.num_allocated_qubits == 26
        b.check_phase()
        total = float(b.count)
        assert (f, total) == (53, 97.5), (f, total)
        return dict(status='EXACT_ALL_INPUT_AND_ALL_HMR_PHASE_CERTIFICATE_NOT_NATIVE', original_inputs=_pair_normalization_private_MAX_X, truth_vector_domain_bits=22, required_interval=[1, _pair_normalization_private_MAX_X], normalized_map='n=x*4**k, k=floor((22-bit_length(x))/2), n in[2^20,2^22)', mathematical_phase_error=0, all_original_bits_restored=True, all_scratch_and_flags_zero=True, forward_measurements=fm, total_independent_HMR_symbols=b.measurements, phase_proof='Every HMR outcome is an independent symbolic coefficient; each complete coefficient truth vector vanishes on every official input.', forward_E=f, inverse_expected_E=total - f, total_expected_E=total, peak=fpeak, T=0, R=0, seconds=_pair_normalization_private_time.monotonic() - start, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    def _pair_normalization_private_paper(cap):
        b = _pair_normalization_private_Counter(cap)
        x = list(b.alloc_qubits(22))
        flags = list(b.alloc_qubits(4))
        _pair_normalization_private_forward(b, x, flags)
        f = float(b.count)
        fp = b.peak
        assert b.num_allocated_qubits == 26
        b.peak = 26
        _pair_normalization_private_inverse(b, x, flags)
        assert b.num_allocated_qubits == 26
        return dict(Q_cap=cap, forward_E=f, inverse_expected_E=float(b.count) - f, total_expected_E=float(b.count), forward_peak=fp, inverse_peak=b.peak, T=0, R=0)

    def _pair_normalization_private_main():
        result = dict(scope='NEW_PAIR_NORMALIZATION_PAPER_AND_EXACT_BOOLEAN_ONLY', route=_pair_normalization_private_route_certificate(11), threshold_plans=[_pair_normalization_private_asdict(p) for p in _pair_normalization_private_THRESHOLD_PLANS], certificate=_pair_normalization_private_certify(), paper=[_pair_normalization_private_paper(q) for q in range(46, 53)], excluded_transfer='The122E Stage94 semilog/packed interface is not used.', native_gate='Use only after the full actual lifecycle ledger is updated and clears its paper gate; native proof still required.')
        (_pair_normalization_private_HERE / 'pair_normalization.json').write_text(_pair_normalization_private_json.dumps(result, indent=2) + '\n')
        print(_pair_normalization_private_json.dumps({'certificate': result['certificate'], 'paper': result['paper']}, indent=2))
    if _pair_normalization_private___name__ == '__main__':
        _pair_normalization_private_main()

def _initialize_drive_paper_ledger():
    global _drive_paper_ledger_Fraction, _drive_paper_ledger_HERE, _drive_paper_ledger_INTEGRATED_ROOT, _drive_paper_ledger_NARROW, _drive_paper_ledger_PaperCounter, _drive_paper_ledger_Path, _drive_paper_ledger__IntegratedPath, _drive_paper_ledger___file__, _drive_paper_ledger___name__, _drive_paper_ledger_forward_add, _drive_paper_ledger_inverse_add, _drive_paper_ledger_json, _drive_paper_ledger_km, _drive_paper_ledger_load_table, _drive_paper_ledger_main, _drive_paper_ledger_os, _drive_paper_ledger_paper, _drive_paper_ledger_sys
    _drive_paper_ledger_os = _import_component('os', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', True)
    _drive_paper_ledger_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _drive_paper_ledger_sys = _import_component('sys', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', True)
    _drive_paper_ledger_json = _import_component('json', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', True)
    _drive_paper_ledger_Path = _import_component('pathlib', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False).Path
    _drive_paper_ledger_Fraction = _import_component('fractions', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False).Fraction
    _drive_paper_ledger_HERE = _drive_paper_ledger_Path(_drive_paper_ledger___file__).resolve().parent
    _drive_paper_ledger_NARROW = _drive_paper_ledger_HERE.parents[1]
    _drive_paper_ledger_sys.path[:0] = [str(_drive_paper_ledger_NARROW / 'base/official/kickmix'), str(_drive_paper_ledger_NARROW / 'checkpoint002/cleanroom/baseline_stage97/engine')]
    _drive_paper_ledger_km = _import_component('kickmix', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False)
    _drive_paper_ledger_forward_add = _import_component('paired_arithmetic', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False).forward_add
    _drive_paper_ledger_inverse_add = _import_component('paired_arithmetic', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False).inverse_add
    _drive_paper_ledger_load_table = _import_component('fusion.lookup', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False).load_table

    class _drive_paper_ledger_PaperCounter:

        def __init__(self, cap):
            self.max_qubits = cap
            self.live = set()
            self.nextq = 0
            self.nextb = 0
            self.pool = []
            self.stack = []
            self.count = _drive_paper_ledger_Fraction(0)
            self.peak = 0

        @property
        def num_allocated_qubits(self):
            return len(self.live)

        def alloc_qubits(self, n):
            if len(self.live) + n > self.max_qubits:
                raise ValueError(f'paper allocation {len(self.live)}+{n}>{self.max_qubits}')
            out = []
            for _ in range(n):
                if self.pool:
                    q = self.pool.pop()
                else:
                    q = _drive_paper_ledger_km.q(self.nextq)
                    self.nextq += 1
                self.live.add(q)
                out.append(q)
            self.peak = max(self.peak, len(self.live))
            return _drive_paper_ledger_km.array(out)

        def alloc_bits(self, n):
            out = _drive_paper_ledger_km.array([_drive_paper_ledger_km.b(i) for i in range(self.nextb, self.nextb + n)])
            self.nextb += n
            return out

        def free(self, x):
            if isinstance(x, _drive_paper_ledger_km.q):
                assert x in self.live
                self.live.remove(x)
                self.pool.append(x)
            elif isinstance(x, _drive_paper_ledger_km.b):
                pass
            else:
                for q in x:
                    self.free(q)

        def push_condition(self, b):
            self.stack.append(b)

        def pop_condition(self):
            self.stack.pop()

        def _charge(self, n=1):
            self.count += _drive_paper_ledger_Fraction(n, 1 << len(set(self.stack)))

        def ccx(self, *a):
            self._charge()

        def ccz(self, *a):
            self._charge()

        def cswap(self, *a):
            self._charge()

        def cx(self, *a):
            pass

        def cz(self, *a):
            pass

        def x(self, *a):
            pass

        def z(self, *a):
            pass

        def hmr(self, *a):
            pass

        def del_and(self, *a):
            pass

        def bit_store(self, *a):
            pass

    def _drive_paper_ledger_paper(cap, m=37, schedule=None, mode='baseline'):
        schedule = schedule or {}
        b = _drive_paper_ledger_PaperCounter(cap)
        v = list(b.alloc_qubits(12))
        p = list(b.alloc_qubits(10 if mode == 'baseline' else 16))
        flags = list(b.alloc_qubits(4))
        u = list(b.alloc_qubits(14))
        original = list(u)
        base_data = b.num_allocated_qubits
        table = [(1 << min(k, 10) + 3) - 1 for k in range(16)]
        load_before = b.count
        _drive_paper_ledger_load_table(b, table, flags, u)
        load_forward = b.count - load_before
        extra_init = 0
        tmp = b.alloc_qubits(extra_init)
        init_before = b.count
        init = _drive_paper_ledger_forward_add(b, v, u)
        init_forward = b.count - init_before
        b.free(tmp)
        records = []
        rounds = []
        for j in range(1, m - 1):
            k = schedule.get(j, 0)
            u = [u[-1]] + u[:-1]
            phase = 'outside'
            if mode != 'baseline' and 1 <= j <= 24:
                phase = 'always' if 10 <= j <= 14 else 'masked'
            if phase == 'always':
                helper_count = 0 if mode == 'cswap' else 1
            elif phase == 'masked':
                helper_count = 2 if mode == 'cswap' else 3
            else:
                helper_count = 0
            tmp = list(b.alloc_qubits(helper_count))
            carry = tmp[-1] if tmp else v[k]
            before = b.count
            debt = _drive_paper_ledger_forward_add(b, v[k + 1:], u[k + 1:], carry_in=carry)
            rounds.append(dict(j=j, k=k, phase=phase, helpers=helper_count, forward=float(b.count - before)))
            records.append((j, k, phase, helper_count, debt))
            b.free(tmp)
        for j, k, phase, helper_count, debt in reversed(records):
            tmp = list(b.alloc_qubits(helper_count))
            carry = tmp[-1] if tmp else v[k]
            before = b.count
            _drive_paper_ledger_inverse_add(b, v[k + 1:], u[k + 1:], debt, carry_in=carry, dirty_wires=p + flags)
            rounds[j - 1]['inverse'] = float(b.count - before)
            b.free(tmp)
            u = u[1:] + u[:1]
        assert u == original
        tmp = b.alloc_qubits(extra_init)
        before = b.count
        _drive_paper_ledger_inverse_add(b, v, u, init, dirty_wires=p + flags)
        init_inverse = b.count - before
        b.free(tmp)
        before = b.count
        _drive_paper_ledger_load_table(b, table, flags, u)
        load_inverse = b.count - before
        arithmetic = b.count
        if mode == 'baseline':
            routing = _drive_paper_ledger_Fraction(0)
            routing_detail = {}
        else:
            carry_logic = 2 * (19 * (3 if mode == 'cswap' else 2) + 5 * (2 if mode == 'cswap' else 1))
            routing_detail = dict(ring16_permutation=72, threshold_preparation=54, threshold_debt=0.5, carry_logic=carry_logic, initialization_correction=8)
            routing = sum(map(_drive_paper_ledger_Fraction, routing_detail.values()))
        return dict(status='SOURCE_EXPANDED_PAPER_LEDGER_NOT_NATIVE', mode=mode, Q_cap=cap, data_registers={'root_v': 12, 'correction_with_zero_sentinel': len(p), 'flags': 4, 'u': 14}, base_data=base_data, peak_allocation=b.peak, m=m, schedule=schedule, adder_and_lookup_toffolis=float(arithmetic), routing_toffolis=float(routing), expected_toffolis=float(arithmetic + routing), T=1, R=m - 3, lookup_forward=float(load_forward), lookup_inverse=float(load_inverse), initial_add_forward=float(init_forward), initial_add_inverse=float(init_inverse), routing_detail=routing_detail, rounds=rounds)

    def _drive_paper_ledger_main():
        calibration = []
        old = _json_loads(_read_text(_drive_paper_ledger_NARROW / 'checkpoint002/cleanroom/table_arch/taper_balanced_caps.json'))
        schedule = {j: j - 26 for j in range(28, 36)}
        for row in old['rows']:
            p = _drive_paper_ledger_paper(row['Q'], 37, schedule, 'baseline')
            expected = row['counts']['toffoli_like']
            calibration.append(dict(Q=row['Q'], paper=p['expected_toffolis'], previous_native=expected, match=p['expected_toffolis'] == expected))
        assert all((x['match'] for x in calibration)), calibration
        rows = []
        schedules = [(36, {}, 'm36_exact'), (36, {j: j - 29 for j in range(30, 35)}, 'm36_tight'), (37, schedule, 'm37_balanced'), (37, {j: j - 25 for j in range(27, 36)}, 'm37_wide')]
        for cap in range(48, 53):
            for mode in ('binary', 'cswap'):
                for m, sched, name in schedules:
                    try:
                        p = _drive_paper_ledger_paper(cap, m, sched, mode)
                        p['schedule_name'] = name
                        rows.append(p)
                    except Exception as e:
                        rows.append(dict(Q_cap=cap, mode=mode, schedule_name=name, status='PAPER_SCHEDULE_BLOCKED', reason=str(e)))
        result = dict(scope='Pure Python allocation/expected-gate counter expanding existing own arithmetic source. No native CircuitBuilder, KMB, simulator, or proof of the new arithmetic. Full producer, normalization, root and rotation charge remain separate line items.', calibration=calibration, rows=rows)
        (_drive_paper_ledger_HERE / 'drive_paper_ledger.json').write_text(_drive_paper_ledger_json.dumps(result, indent=2) + '\n')
        print(_drive_paper_ledger_json.dumps(calibration))
        for r in rows:
            print(_drive_paper_ledger_json.dumps({k: v for k, v in r.items() if k not in ['rounds', 'schedule', 'routing_detail']}))
    if _drive_paper_ledger___name__ == '__main__':
        _drive_paper_ledger_main()
_PREFIXES = {('agents/composer/p/w2core_e2.py', 0): '_w2core_e2_', ('agents/micro47/scripts/relocate_cs2.py', 0): '_relocate_cs2_', ('agents/width/src/block_replay.py', 0): '_block_replay_', ('agents/width/src/paid_R_cleanup_q48.py', 0): '_paid_R_cleanup_q48_', ('patches/patch_coef2_q46.py', 0): '_patch_coef2_q46_', ('patches/patch_coefdisp.py', 0): '_patch_coefdisp_', ('patches/patch_donor_first60.py', 0): '_patch_donor_first60_', ('patches/patch_endpoint_v9e2.py', 0): '_patch_endpoint_v9e2_', ('patches/patch_fwd_narrow.py', 0): '_patch_fwd_narrow_', ('patches/patch_h2ret.py', 0): '_patch_h2ret_', ('patches/patch_hret_sat_s15k7a.py', 0): '_patch_hret_sat_s15k7a_', ('patches/patch_ld_first20_56b8.py', 0): '_patch_ld_first20_56b8_', ('patches/patch_proddisp.py', 0): '_patch_proddisp_', ('patches/patch_q47_decoder_resynth2.py', 0): '_patch_q47_decoder_resynth2_', ('patches/patch_second46_c19_70nb1.py', 0): '_patch_second46_c19_70nb1_', ('patches/patch_seedinv.py', 0): '_patch_seedinv_', ('patches/patch_w47_body.py', 0): '_patch_w47_body_', ('patches/q46_loaders.py', 0): '_q46_loaders_', ('tools/audit_affine.py', 0): '_audit_affine_', ('tools/audit_pairs.py', 0): '_audit_pairs_', ('tools/build_variant.py', 0): '_build_variant_', ('tools/hold_pass.py', 0): '_hold_pass_', ('tools/kmsim.py', 0): '_kmsim_', ('tools/kmx_to_kmb.py', 0): '_kmx_to_kmb_', ('tools/merge_zpow.py', 0): '_merge_zpow_', ('tools/postpass.py', 0): '_postpass_', ('work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', 0): '_candidate10_setup_', ('work/c10/narrow/arithmetic_round2/native/candidate10/lifecycle10.py', 0): '_lifecycle10_', ('work/c10/narrow/arithmetic_round2/research/divider/history12_kernel.py', 0): '_history12_kernel_', ('work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', 0): '_native_ar004_divider_', ('work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', 0): '_top12_kernel_', ('work/c10/narrow/arithmetic_round2/research/product_coefficient/native_transfer.py', 0): '_native_transfer_', ('work/c10/narrow/arithmetic_round2/research/product_coefficient/native_v3/adapter.py', 0): '_native_v3_product_', ('work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', 0): '_normalization9475_', ('work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', 0): '_root192_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', 0): '_branch_prover_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py', 0): '_codebook_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', 0): '_cyclic_phase_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/dirty_terminal.py', 0): '_dirty_terminal_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/__init__.py', 0): '___init___', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', 0): '_arithmetic_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', 1): '_arithmetic_private_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/compiler.py', 0): '_compiler_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/lookup.py', 0): '_lookup_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', 0): '_paired_arithmetic_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', 1): '_paired_arithmetic_private_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/quadratic_terms.py', 0): '_quadratic_terms_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/stage94_bit_routing_math.py', 0): '_stage94_bit_routing_math_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/thermometer_cleanup.py', 0): '_thermometer_cleanup_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', 0): '_fourier_resource_expectation_', ('work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', 0): '_consuming_odd_sqrt_', ('work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', 1): '_consuming_odd_sqrt_private_', ('work/c10/narrow/native/candidate01/common.py', 0): '_common_', ('work/c10/narrow/native/candidate01/divider.py', 0): '_divider_', ('work/c10/narrow/native/candidate01/generate.py', 0): '_generate_', ('work/c10/narrow/native/candidate01/layout.py', 0): '_layout_', ('work/c10/narrow/native/candidate01/lifecycle.py', 0): '_lifecycle_', ('work/c10/narrow/native/candidate01/normalization.py', 0): '_normalization_', ('work/c10/narrow/native/candidate01/root_decode.py', 0): '_root_decode_', ('work/c10/narrow/native/candidate01/tables.py', 0): '_tables_', ('work/c10/narrow/native/candidate02/variant.py', 0): '_candidate02_setup_', ('work/c10/narrow/native/candidate03/variant.py', 0): '_candidate03_setup_', ('work/c10/narrow/native/candidate04/variant.py', 0): '_candidate04_setup_', ('work/c10/narrow/native/candidate05/variant.py', 0): '_candidate05_setup_', ('work/c10/narrow/native/candidate06/decoder06.py', 0): '_decoder06_', ('work/c10/narrow/native/candidate06/divider_cleanup06.py', 0): '_divider_cleanup06_', ('work/c10/narrow/native/candidate06/lifecycle06.py', 0): '_lifecycle06_', ('work/c10/narrow/native/candidate06/phase06.py', 0): '_phase06_', ('work/c10/narrow/native/candidate06/tables06.py', 0): '_tables06_', ('work/c10/narrow/native/candidate06/variant.py', 0): '_candidate06_setup_', ('work/c10/narrow/native/candidate07/phase07.py', 0): '_phase07_', ('work/c10/narrow/native/candidate07/tables07.py', 0): '_tables07_', ('work/c10/narrow/native/candidate07/variant.py', 0): '_candidate07_setup_', ('work/c10/narrow/research/quantized_producer/pair_normalization.py', 0): '_pair_normalization_', ('work/c10/narrow/research/quantized_producer/pair_normalization.py', 1): '_pair_normalization_private_', ('work/c10/narrow/research/stream_phase/drive_paper_ledger.py', 0): '_drive_paper_ledger_'}
_GROUPS = {('agents/width/src/block_replay.py', 'width_block_replay'): 0, ('agents/width/src/paid_R_cleanup_q48.py', 'width_pro2_paid_R_cleanup_q48'): 0, ('patches/patch_coef2_q46.py', 'variant_patch_patch_coef2_q46'): 0, ('patches/patch_coefdisp.py', 'variant_patch_patch_coefdisp'): 0, ('patches/patch_donor_first60.py', 'variant_patch_patch_donor_first60'): 0, ('patches/patch_endpoint_v9e2.py', 'variant_patch_patch_endpoint_v9e2'): 0, ('patches/patch_fwd_narrow.py', 'variant_patch_patch_fwd_narrow'): 0, ('patches/patch_h2ret.py', 'variant_patch_patch_h2ret'): 0, ('patches/patch_hret_sat_s15k7a.py', 'variant_patch_patch_hret_sat_s15k7a'): 0, ('patches/patch_ld_first20_56b8.py', 'variant_patch_patch_ld_first20_56b8'): 0, ('patches/patch_proddisp.py', 'variant_patch_patch_proddisp'): 0, ('patches/patch_q47_decoder_resynth2.py', 'variant_patch_patch_q47_decoder_resynth2'): 0, ('patches/patch_second46_c19_70nb1.py', 'variant_patch_patch_second46_c19_70nb1'): 0, ('patches/patch_seedinv.py', 'variant_patch_patch_seedinv'): 0, ('patches/patch_w47_body.py', 'variant_patch_patch_w47_body'): 0, ('patches/q46_loaders.py', 'tk46_q46_second_loader'): 0, ('work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', 'arithmetic_variant'): 0, ('work/c10/narrow/arithmetic_round2/native/candidate10/lifecycle10.py', 'lifecycle10'): 0, ('work/c10/narrow/arithmetic_round2/research/divider/history12_kernel.py', '_ar004_frozen_history12_kernel'): 0, ('work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', 'candidate10_adapter_divider'): 0, ('work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', 'top12_kernel'): 0, ('work/c10/narrow/arithmetic_round2/research/product_coefficient/native_transfer.py', 'candidate10_adapter_coefficient'): 0, ('work/c10/narrow/arithmetic_round2/research/product_coefficient/native_v3/adapter.py', 'candidate10_adapter_product'): 0, ('work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', 'candidate10_adapter_normalization'): 0, ('work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', 'candidate10_adapter_root'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', 'branch_prover'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py', 'codebook'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', 'cyclic_phase'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/dirty_terminal.py', 'dirty_terminal'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/__init__.py', 'fusion'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', 'fusion.arithmetic'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', 'fusion._round2_rn3_immutable_arithmetic'): 1, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/compiler.py', 'fusion.compiler'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/lookup.py', 'fusion.lookup'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', 'paired_arithmetic'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', '_candidate01_product_paired'): 1, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/quadratic_terms.py', 'quadratic_terms'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/stage94_bit_routing_math.py', 'stage94_bit_routing_math'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/thermometer_cleanup.py', 'thermometer_cleanup'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', 'fourier_resource_expectation'): 0, ('work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', 'consuming_odd_sqrt'): 0, ('work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', '_round2_rn3_immutable_odd_sqrt'): 1, ('work/c10/narrow/native/candidate01/common.py', 'common'): 0, ('work/c10/narrow/native/candidate01/divider.py', 'divider'): 0, ('work/c10/narrow/native/candidate01/generate.py', 'candidate02_pinned_generate'): 0, ('work/c10/narrow/native/candidate01/layout.py', 'layout'): 0, ('work/c10/narrow/native/candidate01/lifecycle.py', 'candidate06_pinned_candidate01_lifecycle'): 0, ('work/c10/narrow/native/candidate01/normalization.py', 'normalization'): 0, ('work/c10/narrow/native/candidate01/root_decode.py', 'root_decode'): 0, ('work/c10/narrow/native/candidate01/tables.py', '_candidate06_pinned_tables01'): 0, ('work/c10/narrow/native/candidate02/variant.py', 'candidate03_pinned_candidate02_variant'): 0, ('work/c10/narrow/native/candidate03/variant.py', 'candidate04_pinned_candidate03_variant'): 0, ('work/c10/narrow/native/candidate04/variant.py', 'candidate05_pinned_candidate04_variant'): 0, ('work/c10/narrow/native/candidate05/variant.py', 'candidate06_pinned_candidate05_variant'): 0, ('work/c10/narrow/native/candidate06/decoder06.py', 'candidate06_decoder06'): 0, ('work/c10/narrow/native/candidate06/decoder06.py', 'decoder06'): 0, ('work/c10/narrow/native/candidate06/divider_cleanup06.py', 'candidate06_divider_cleanup06'): 0, ('work/c10/narrow/native/candidate06/divider_cleanup06.py', 'divider_cleanup06'): 0, ('work/c10/narrow/native/candidate06/lifecycle06.py', 'candidate06_lifecycle06'): 0, ('work/c10/narrow/native/candidate06/lifecycle06.py', 'lifecycle06'): 0, ('work/c10/narrow/native/candidate06/phase06.py', 'candidate06_phase06'): 0, ('work/c10/narrow/native/candidate06/phase06.py', 'phase06'): 0, ('work/c10/narrow/native/candidate06/tables06.py', 'candidate06_tables06'): 0, ('work/c10/narrow/native/candidate06/tables06.py', 'tables06'): 0, ('work/c10/narrow/native/candidate06/variant.py', 'candidate07_pinned_candidate06_variant'): 0, ('work/c10/narrow/native/candidate07/phase07.py', 'candidate07_phase07'): 0, ('work/c10/narrow/native/candidate07/phase07.py', 'phase07'): 0, ('work/c10/narrow/native/candidate07/tables07.py', 'candidate07_tables07'): 0, ('work/c10/narrow/native/candidate07/tables07.py', 'tables07'): 0, ('work/c10/narrow/native/candidate07/variant.py', 'variant'): 0, ('work/c10/narrow/research/quantized_producer/pair_normalization.py', '_round2_rn2df_private_pair_normalizer'): 0, ('work/c10/narrow/research/quantized_producer/pair_normalization.py', 'native_pair_normalization_source'): 1, ('work/c10/narrow/research/stream_phase/drive_paper_ledger.py', 'drive_paper_ledger'): 0}
_FACTORIES = {('agents/composer/p/w2core_e2.py', 0): _initialize_w2core_e2, ('agents/micro47/scripts/relocate_cs2.py', 0): _initialize_relocate_cs2, ('agents/width/src/block_replay.py', 0): _initialize_block_replay, ('agents/width/src/paid_R_cleanup_q48.py', 0): _initialize_paid_R_cleanup_q48, ('patches/patch_coef2_q46.py', 0): _initialize_patch_coef2_q46, ('patches/patch_coefdisp.py', 0): _initialize_patch_coefdisp, ('patches/patch_donor_first60.py', 0): _initialize_patch_donor_first60, ('patches/patch_endpoint_v9e2.py', 0): _initialize_patch_endpoint_v9e2, ('patches/patch_fwd_narrow.py', 0): _initialize_patch_fwd_narrow, ('patches/patch_h2ret.py', 0): _initialize_patch_h2ret, ('patches/patch_hret_sat_s15k7a.py', 0): _initialize_patch_hret_sat_s15k7a, ('patches/patch_ld_first20_56b8.py', 0): _initialize_patch_ld_first20_56b8, ('patches/patch_proddisp.py', 0): _initialize_patch_proddisp, ('patches/patch_q47_decoder_resynth2.py', 0): _initialize_patch_q47_decoder_resynth2, ('patches/patch_second46_c19_70nb1.py', 0): _initialize_patch_second46_c19_70nb1, ('patches/patch_seedinv.py', 0): _initialize_patch_seedinv, ('patches/patch_w47_body.py', 0): _initialize_patch_w47_body, ('patches/q46_loaders.py', 0): _initialize_q46_loaders, ('tools/audit_affine.py', 0): _initialize_audit_affine, ('tools/audit_pairs.py', 0): _initialize_audit_pairs, ('tools/build_variant.py', 0): _initialize_build_variant, ('tools/hold_pass.py', 0): _initialize_hold_pass, ('tools/kmsim.py', 0): _initialize_kmsim, ('tools/kmx_to_kmb.py', 0): _initialize_kmx_to_kmb, ('tools/merge_zpow.py', 0): _initialize_merge_zpow, ('tools/postpass.py', 0): _initialize_postpass, ('work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', 0): _initialize_candidate10_setup, ('work/c10/narrow/arithmetic_round2/native/candidate10/lifecycle10.py', 0): _initialize_lifecycle10, ('work/c10/narrow/arithmetic_round2/research/divider/history12_kernel.py', 0): _initialize_history12_kernel, ('work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', 0): _initialize_native_ar004_divider, ('work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', 0): _initialize_top12_kernel, ('work/c10/narrow/arithmetic_round2/research/product_coefficient/native_transfer.py', 0): _initialize_native_transfer, ('work/c10/narrow/arithmetic_round2/research/product_coefficient/native_v3/adapter.py', 0): _initialize_native_v3_product, ('work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', 0): _initialize_normalization9475, ('work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', 0): _initialize_root192, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', 0): _initialize_branch_prover, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py', 0): _initialize_codebook, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', 0): _initialize_cyclic_phase, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/dirty_terminal.py', 0): _initialize_dirty_terminal, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/__init__.py', 0): _initialize___init__, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', 0): _initialize_arithmetic, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', 1): _initialize_arithmetic_private, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/compiler.py', 0): _initialize_compiler, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/lookup.py', 0): _initialize_lookup, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', 0): _initialize_paired_arithmetic, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', 1): _initialize_paired_arithmetic_private, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/quadratic_terms.py', 0): _initialize_quadratic_terms, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/stage94_bit_routing_math.py', 0): _initialize_stage94_bit_routing_math, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/thermometer_cleanup.py', 0): _initialize_thermometer_cleanup, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', 0): _initialize_fourier_resource_expectation, ('work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', 0): _initialize_consuming_odd_sqrt, ('work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', 1): _initialize_consuming_odd_sqrt_private, ('work/c10/narrow/native/candidate01/common.py', 0): _initialize_common, ('work/c10/narrow/native/candidate01/divider.py', 0): _initialize_divider, ('work/c10/narrow/native/candidate01/generate.py', 0): _initialize_generate, ('work/c10/narrow/native/candidate01/layout.py', 0): _initialize_layout, ('work/c10/narrow/native/candidate01/lifecycle.py', 0): _initialize_lifecycle, ('work/c10/narrow/native/candidate01/normalization.py', 0): _initialize_normalization, ('work/c10/narrow/native/candidate01/root_decode.py', 0): _initialize_root_decode, ('work/c10/narrow/native/candidate01/tables.py', 0): _initialize_tables, ('work/c10/narrow/native/candidate02/variant.py', 0): _initialize_candidate02_setup, ('work/c10/narrow/native/candidate03/variant.py', 0): _initialize_candidate03_setup, ('work/c10/narrow/native/candidate04/variant.py', 0): _initialize_candidate04_setup, ('work/c10/narrow/native/candidate05/variant.py', 0): _initialize_candidate05_setup, ('work/c10/narrow/native/candidate06/decoder06.py', 0): _initialize_decoder06, ('work/c10/narrow/native/candidate06/divider_cleanup06.py', 0): _initialize_divider_cleanup06, ('work/c10/narrow/native/candidate06/lifecycle06.py', 0): _initialize_lifecycle06, ('work/c10/narrow/native/candidate06/phase06.py', 0): _initialize_phase06, ('work/c10/narrow/native/candidate06/tables06.py', 0): _initialize_tables06, ('work/c10/narrow/native/candidate06/variant.py', 0): _initialize_candidate06_setup, ('work/c10/narrow/native/candidate07/phase07.py', 0): _initialize_phase07, ('work/c10/narrow/native/candidate07/tables07.py', 0): _initialize_tables07, ('work/c10/narrow/native/candidate07/variant.py', 0): _initialize_candidate07_setup, ('work/c10/narrow/research/quantized_producer/pair_normalization.py', 0): _initialize_pair_normalization, ('work/c10/narrow/research/quantized_producer/pair_normalization.py', 1): _initialize_pair_normalization_private, ('work/c10/narrow/research/stream_phase/drive_paper_ledger.py', 0): _initialize_drive_paper_ledger}
_PATCH_ORDER = 'patch patch_fwd_narrow.py\npatch patch_w47_body.py\npatch patch_endpoint_v9e2.py\npatch patch_hret_sat_s15k7a.py\npatch patch_seedinv.py\npatch patch_coefdisp.py\npatch patch_coef2_q46.py\npatch patch_h2ret.py\npatch patch_proddisp.py\npatch patch_donor_first60.py\npatch patch_ld_first20_56b8.py\npatch patch_second46_c19_70nb1.py\npatch patch_q47_decoder_resynth2.py\nwith patch_endpoint_walk8.py\nwith q46_loaders.py\nQ 46\npost agents/micro47/scripts/relocate_cs2.py\n'
if __name__ == '__main__':
    run_stage(sys.argv[1], sys.argv[2:])
