"""Readable Fusion arithmetic/compiler, consolidated from the accepted INV-51 source.

Copyright 2026 Syed Asad Ali. Apache-2.0; see LICENSE.txt and NOTICE.txt.
Definitions use component prefixes to preserve mutable arithmetic bindings and
independent carry contexts. No source strings, archive, exec, precompiled circuit
or instruction payload is embedded. tables.json holds mathematical/config data.
"""
from __future__ import annotations
from pathlib import Path
import copy, hashlib, importlib, inspect, json, sys, types

_HERE=Path(__file__).resolve().parent
_VROOT=_HERE/'_components'
_TABLES=json.loads((_HERE/'tables.json').read_text(encoding='utf-8'))
_CACHE={}
_INITIALIZED=set()
_PROFILE={"calls":set(),"modules":set()}

class _Component:
    __slots__=('key','group','prefix','name')
    def __init__(self,key,group,name):
        object.__setattr__(self,'key',key);object.__setattr__(self,'group',group)
        object.__setattr__(self,'prefix',_PREFIXES[key,group]);object.__setattr__(self,'name',name)
    def __getattr__(self,name):
        if name=='__file__':return str(_VROOT/self.key)
        if name=='__name__':return self.name
        if name=='__dict__':return {k[len(self.prefix):]:v for k,v in globals().items() if k.startswith(self.prefix)}
        try:return globals()[self.prefix+name]
        except KeyError:raise AttributeError(name) from None
    def __setattr__(self,name,value):globals()[self.prefix+name]=value
    def __dir__(self):return ['__file__','__name__',*self.__dict__]

class _Spec:
    def __init__(self,name,path):
        self.name=name;self.key=_key(path);self.group=_GROUPS.get((self.key,name),0);self.loader=self
        if (self.key,self.group) not in _FACTORIES:raise ImportError(str(path))
    def exec_module(self,module):
        pair=(self.key,self.group)
        if pair in _INITIALIZED:return
        _PROFILE['modules'].add(pair)
        prefix=module.prefix
        globals()[prefix+'__file__']=str(_VROOT/self.key)
        globals()[prefix+'__name__']=self.name
        _FACTORIES[pair]()
        _INITIALIZED.add(pair)

def _key(path):
    try:return Path(path).resolve().relative_to(_VROOT).as_posix()
    except ValueError:return None

def _spec(name,path):return _Spec(name,path)

def _new_module(spec):
    pair=(spec.key,spec.group)
    if pair not in _CACHE:_CACHE[pair]=_Component(spec.key,spec.group,spec.name)
    return _CACHE[pair]

def _import_component(name,current,top=False):
    if name in sys.modules:return sys.modules[name.split('.')[0] if top else name]
    paths=[str(_VROOT/Path(current).parent),*sys.path]
    for directory in paths:
        key=_key(Path(directory)/(name.replace('.','/')+'.py'))
        if (key,0) in _FACTORIES:
            spec=_Spec(name,_VROOT/key);module=_new_module(spec);sys.modules[name]=module
            spec.exec_module(module)
            return module
    matches=[k for k,g in _FACTORIES if g==0 and k.endswith('/'+name.replace('.','/')+'.py')]
    if len(matches)==1:
        spec=_Spec(name,_VROOT/matches[0]);module=_new_module(spec);sys.modules[name]=module;spec.exec_module(module);return module
    return importlib.import_module(name.split('.')[0] if top else name)

def _import_star(prefix,module):
    for name in dir(module):
        if not name.startswith('_'):globals()[prefix+name]=getattr(module,name)

class _DataText(str):
    def __new__(cls,value,key):
        obj=str.__new__(cls,value);obj.key=key;return obj

class _DataBytes(bytes):
    def __new__(cls,value,key):
        obj=bytes.__new__(cls,value);obj.key=key;return obj

def _read_text(path,*args,**kwargs):
    key=_key(path)
    if key in _TABLES:return _DataText(json.dumps(_TABLES[key]),key)
    if key=='patches/PATCH_ORDER.txt':return _PATCH_ORDER
    return Path(path).read_text(*args,**kwargs)

def _read_bytes(path,*args,**kwargs):
    key=_key(path)
    if key in _TABLES:return _DataBytes(json.dumps(_TABLES[key]).encode(),key)
    if (key,0) in _FACTORIES:return inspect.getsource(_FACTORIES[key,0]).encode()
    return Path(path).read_bytes(*args,**kwargs)

def _exists(path):
    key=_key(path)
    return key in _TABLES or (key,0) in _FACTORIES or Path(path).exists()

def _json_loads(value,*args,**kwargs):
    if isinstance(value,(_DataText,_DataBytes)):return copy.deepcopy(_TABLES[value.key])
    return json.loads(value,*args,**kwargs)

def run_stage(key,args):
    sys.argv=[str(_VROOT/key),*args]
    sys.path.insert(0,str(_VROOT/Path(key).parent))
    module=_new_module(_Spec('__main__',_VROOT/key))
    _Spec('__main__',_VROOT/key).exec_module(module)

# agents/composer/p/w2core_e2.py
def _initialize__c0_w2core_e2():
    global _c0_w2core_e2_CENTRES, _c0_w2core_e2_CONTROLS, _c0_w2core_e2_ENC, _c0_w2core_e2_ENC_FN, _c0_w2core_e2_E_HOLD, _c0_w2core_e2_F_HOLD, _c0_w2core_e2_Fraction, _c0_w2core_e2_INTEGRATED_ROOT, _c0_w2core_e2_MAX_EXTRA, _c0_w2core_e2_MODULUS, _c0_w2core_e2_P_RETIRED_STEPS, _c0_w2core_e2_QMAX, _c0_w2core_e2_R2_HOLDS, _c0_w2core_e2_RESULT, _c0_w2core_e2_RETIRE_V9, _c0_w2core_e2_SpareProxy, _c0_w2core_e2_THR, _c0_w2core_e2_V10_FROM_G1, _c0_w2core_e2__IntegratedPath, _c0_w2core_e2___file__, _c0_w2core_e2___name__, _c0_w2core_e2__anf, _c0_w2core_e2__check_domain, _c0_w2core_e2__emit_form, _c0_w2core_e2__erase_helpers, _c0_w2core_e2__pair_forms, _c0_w2core_e2__quadratic, _c0_w2core_e2__undo, _c0_w2core_e2_apply, _c0_w2core_e2_fn, _c0_w2core_e2_j, _c0_w2core_e2_make_endpoint, _c0_w2core_e2_pairs
    "width2 COPY of the phase agent's walk8 core with one more retired root bit (v9) across the endpoint\n(RETIRE_V9 = form dict from tools/minand_sat.py over named inputs; set by the wrapper patch before make_endpoint).\nAt entry v9 is X-measured with NO fix (deferred repayment, as v10); at exit, before the v10 rebuild, v9 is rebuilt\nexactly into its own (spare, zero) wire from the SAT straight-line program and Z(v9) is applied on the stored outcome.\nOriginal docstring: Phase-agent patch: endpoint walk8 = walk7 with deferred repayment of the v[10] retirement:\nHMR at entry with NO fix; at exit v10 is rebuilt exactly (2 CCX) and Z(v10) is applied on the\nstored outcome, which repays (-1)^(m*v10) exactly (trick read from the divider agent's HRET\npatch). Removes the outcome-conditioned CCZ (0.5 expected).\nwalk7 = walk6 with the p-free decomposition (2,6,24,0,25):\nno stage control uses p, so p is computed once (one CCX) just before walk step 8 for the\nfeatures, instead of being computed at entry, retired and rebuilt.\nwalk6 = walk5 plus root bit v[10] retired across the endpoint\n(cubic identity v10 = s13^v8^v9^s14^h^(v8^s14^h)(v9^s14), h=v8*s15, measured on all inputs at\nentry): HMR + Clifford fix + one outcome-conditioned CCZ (0.5 expected) at entry, rebuilt with\n2 CCX into the same wire at exit; its wire is a second spare (more R2 holds; Q47 twin holds\nall 25 R3/R4 edges).\nwalk5 = walk4 plus p retired during walk steps 0-7 (no control\nthere uses p; HMR + Clifford fix CZ(f1,f2)CZ(f1,f3)), recomputed with one CCX before step 8.\nThe extra lane holds two more path-local R2 edges (four in all).\nwalk4 = walk3 with the route decomposition\n(0,4,24,0,25) (stage 2 path-local along the R3/R4 walk: two R2 edges held instead of one).\nwalk3 = walk2 (v[11] spare, R2 edge (9,11) held) plus\nsingle-helper boundary-class feature encodings.\n\nMeasured fact: in class k = j+1 the routed slot j holds the constant-one ring position, so\na feature phase theta_j*thr_{j+1}*s_j may be realised by any quadratic E_j(f0..f3,p,s_j)\nthat equals thr_{j+1}*s_j on every class k != j+1 and equals 1 at k = j+1 (s_j=1 there).\nEncodings (ANF checked on the 11 measured classes at build time):\n  j0: (f1^f2^f3^p)(s^f0) ^ f0     1 product (was 2: thr1 + AND), 1 helper (was 2)\n  j2: f0(f1^p) ^ (f2^f3)s          2 products, 1 helper (was 2)\n  j6: f0 p ^ f3 s                  2 products, 1 helper (was 2)\n  j1, j3, j7: affine threshold AND s (unchanged); j4, j5, j8: unchanged.\nEach E_j is computed into one fresh helper with xor_polynomial (rank-minimal), rotated,\nand erased with _erase_polynomial (exact Clifford repayment). With at most one feature\nhelper outside step 12, all 25 R3/R4 edges hold their difference.\n(Idea for the boundary encodings read from Pro 2's candidate11r2 kmx; derivation and\nschedule here are own work.) Replaces only divider.phase_endpoint.\n"
    _c0_w2core_e2__IntegratedPath = _import_component('pathlib', 'agents/composer/p/w2core_e2.py', False).Path
    _c0_w2core_e2_INTEGRATED_ROOT = _c0_w2core_e2__IntegratedPath(_c0_w2core_e2___file__).resolve().parents[3]
    _c0_w2core_e2_Fraction = _import_component('fractions', 'agents/composer/p/w2core_e2.py', False).Fraction
    _c0_w2core_e2_MODULUS = 1 << 50
    _c0_w2core_e2_CENTRES = (2, 6, 24, 0, 25)
    _c0_w2core_e2_CONTROLS = ((0, 4), (8,), (0, 2, 4, 8), (0, 1, 2), (0, 1))
    _c0_w2core_e2_THR = {1: (1, 2, 4, 8, 16, 3, 5, 9, 17), 2: (2, 4, 8, 16), 3: (4, 8, 3, 17), 4: (4, 8), 5: (5, 17, 6, 18, 8, 16), 6: (6, 8), 7: (8, 17), 8: (8,), 9: (9, 10)}
    _c0_w2core_e2_E_HOLD = set(range(1, 13))
    _c0_w2core_e2_F_HOLD = set(range(13))
    _c0_w2core_e2_R2_HOLDS = {(11, 13): (0, 2), (10, 14): (0, 3), (9, 15): (1, 4), (7, 17): (3, 6), (6, 18): (4, 7), (5, 19): (5, 8), (1, 23): (9, 12)}
    _c0_w2core_e2_P_RETIRED_STEPS = (0, 7)
    _c0_w2core_e2_MAX_EXTRA = 7
    _c0_w2core_e2_QMAX = 48

    def _c0_w2core_e2__anf(fn):
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
    _c0_w2core_e2_ENC_FN = {0: lambda f0, f1, f2, f3, p, s: (f1 ^ f2 ^ f3 ^ p) & (s ^ f0) ^ f0, 1: lambda f0, f1, f2, f3, p, s: (f1 ^ f2 ^ f3 ^ p) & s, 2: lambda f0, f1, f2, f3, p, s: f0 & (f1 ^ p) ^ (f2 ^ f3) & s, 3: lambda f0, f1, f2, f3, p, s: (f2 ^ f3) & s, 6: lambda f0, f1, f2, f3, p, s: f0 & p ^ f3 & s, 7: lambda f0, f1, f2, f3, p, s: f3 & s}
    _c0_w2core_e2_ENC = {j: _c0_w2core_e2__anf(fn) for j, fn in _c0_w2core_e2_ENC_FN.items()}

    def _c0_w2core_e2__check_domain():
        flags = {k: k for k in range(11)}
        flags[10] = 10
        for j, fn in _c0_w2core_e2_ENC_FN.items():
            for k in range(11):
                f = [flags[k] >> i & 1 for i in range(4)]
                p = f[1] & (f[2] ^ f[3])
                for s in (1,) if k == j + 1 else (0, 1):
                    assert fn(*f, p, s) == int(k >= j + 1) & s, (j, k, s)
    _c0_w2core_e2__check_domain()

    def _c0_w2core_e2_pairs(stage):
        centre = _c0_w2core_e2_CENTRES[stage]
        return [(i, (centre - i) % 26) for i in range(26) if i < (centre - i) % 26]

    class _c0_w2core_e2_SpareProxy:
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
            assert self._b.num_allocated_qubits <= _c0_w2core_e2_QMAX, ('endpoint width', self._b.num_allocated_qubits)
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
    _c0_w2core_e2_V10_FROM_G1 = False
    _c0_w2core_e2_RETIRE_V9 = None

    def _c0_w2core_e2__pair_forms(b, SA, SB):
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

    def _c0_w2core_e2__undo(b, ops):
        for c, t in reversed(ops):
            b.cx(c, t)

    def _c0_w2core_e2__erase_helpers(b, helpers):
        for h, lw, rw in reversed(helpers):
            m = b.alloc_bits(1)[0]
            b.hmr(h, m)
            b.free(h)
            wa, wb, ops = _c0_w2core_e2__pair_forms(b, lw, rw)
            b.push_condition(m)
            b.cz(wa, wb)
            b.pop_condition()
            _c0_w2core_e2__undo(b, ops)
            b.free(m)

    def _c0_w2core_e2__emit_form(b, form, named, target, keep=False):
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
            wa, wb, ops = _c0_w2core_e2__pair_forms(b, lw, rw)
            b.ccx(wa, wb, h)
            _c0_w2core_e2__undo(b, ops)
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
        _c0_w2core_e2__erase_helpers(b, helpers)
        return (vals, [])

    def _c0_w2core_e2_make_endpoint(phase07, e_hold=_c0_w2core_e2_E_HOLD, f_hold=_c0_w2core_e2_F_HOLD, r2_holds=_c0_w2core_e2_R2_HOLDS, retire_v11=True, retire_v10=True):

        def raw_endpoint(real, token):
            B = phase07.BINDING
            d = B.divider
            v, u, flags = (token.v, token.u, token.flags)
            assert (len(v), len(u), len(flags)) == (12, 14, 4) and real.num_allocated_qubits == 43
            h12, h13, v10, v11 = (token.history[12], token.history[13], v[10], v[11])
            h14, h15, v8, v9 = (token.history[14], token.history[15], v[8], v[9])
            builder = _c0_w2core_e2_SpareProxy(real, 43)
            builder.limit = _c0_w2core_e2_MAX_EXTRA if retire_v11 else _c0_w2core_e2_MAX_EXTRA - 1
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
            if _c0_w2core_e2_RETIRE_V9 is not None:
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
                real.z_pow(word[pos], _c0_w2core_e2_Fraction(2 * B.angles[pos_slot[pos]], _c0_w2core_e2_MODULUS))
                rotated.add(pos)

            def cswap(stage, i, j):
                with d._affine_control(real, variables, _c0_w2core_e2_CONTROLS[stage]) as ctl:
                    real.cswap(ctl, word[i], word[j])

            def cswap_stage(stage, plist):
                with d._affine_control(real, variables, _c0_w2core_e2_CONTROLS[stage]) as ctl:
                    for i, j in plist:
                        real.cswap(ctl, word[i], word[j])

            def hold(stage, i, j):
                a, b = (word[i], word[j])
                anc = builder.alloc_qubits(1)[0]
                with d._affine_control(real, variables, _c0_w2core_e2_CONTROLS[stage]) as ctl:
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
                with d._affine_control(real, variables, _c0_w2core_e2_CONTROLS[stage]) as ctl:
                    real.push_condition(m)
                    real.cz(ctl, a)
                    real.cz(ctl, b)
                    real.pop_condition()
                real.free(m)
                builder.free(anc)

            def threshold(t):
                terms = _c0_w2core_e2_THR[t]
                if max((x.bit_count() for x in terms)) <= 1:
                    return d._affine_control(real, variables, terms)
                return _c0_w2core_e2__quadratic(builder, real, d, variables, terms)

            def feature(j):
                assert j not in featured and 0 <= j <= 8
                featured.add(j)
                if j in _c0_w2core_e2_ENC:
                    terms = _c0_w2core_e2_ENC[j]
                    vars6 = variables + [slots[j]]
                    h = builder.alloc_qubits(1)[0]
                    d.xor_polynomial(real, vars6, h, terms)
                    turns = _c0_w2core_e2_Fraction(B.angles[26 + j], _c0_w2core_e2_MODULUS) if j <= 6 else _c0_w2core_e2_Fraction(1, 8)
                    real.z_pow(h, 2 * turns)
                    d._erase_polynomial(builder, h, vars6, terms)
                    return
                with threshold(j + 1) as control:
                    if j <= 6:
                        d._feature(builder, control, slots[j], _c0_w2core_e2_Fraction(B.angles[26 + j], _c0_w2core_e2_MODULUS))
                    else:
                        d._feature(builder, control, slots[j], _c0_w2core_e2_Fraction(1, 8) if j == 7 else _c0_w2core_e2_Fraction(1, 4))

            def visit(pos):
                rotate(pos)
                k = pos_slot[pos]
                if k <= 8:
                    feature(k)
            held_r2 = {}
            late2 = [pr for pr in _c0_w2core_e2_pairs(2) if pr not in r2_holds]
            cswap_stage(0, _c0_w2core_e2_pairs(0))
            cswap_stage(1, _c0_w2core_e2_pairs(1))
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
                if k == _c0_w2core_e2_P_RETIRED_STEPS[1] + 1:
                    pw = real.alloc_qubits(1)[0]
                    assert real.num_allocated_qubits <= _c0_w2core_e2_QMAX, ('endpoint width at p rebuild', real.num_allocated_qubits)
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
            cswap_stage(1, _c0_w2core_e2_pairs(1))
            cswap_stage(0, _c0_w2core_e2_pairs(0))
            assert B.angles[33] == 0
            d._erase_polynomial(real, variables[4], flags, (6, 10))
            real.x(one)
            real.free(one)
            for q in signs.values():
                real.x(q)
            real.cx(v[1], u[9])
            for q in u[:9]:
                real.cx(v[0], q)
            if _c0_w2core_e2_RETIRE_V9 is not None:
                assert v9w in builder.spare
                named = {'v%d' % i: v[i] for i in range(12)}
                named.update({'s%d' % k: token.history[k] for k in token.history})
                gvals, kept = _c0_w2core_e2__emit_form(real, _c0_w2core_e2_RETIRE_V9, named, v9w, keep=_c0_w2core_e2_V10_FROM_G1)
                real.push_condition(m9)
                real.z(v9w)
                real.pop_condition()
                real.free(m9)
                builder.spare.remove(v9w)
            if _c0_w2core_e2_RETIRE_V9 is not None and _c0_w2core_e2_V10_FROM_G1:
                assert retire_v10 and v10 in builder.spare
                g1 = gvals[len(_c0_w2core_e2_RETIRE_V9['inputs']) + 1]
                real.cx(v9w, v10)
                real.cx(g1, v10)
                wa, wb, ops = _c0_w2core_e2__pair_forms(real, [h13, g1], [v9w, h14])
                real.ccx(wa, wb, v10)
                _c0_w2core_e2__undo(real, ops)
                _c0_w2core_e2__erase_helpers(real, kept)
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
            _c0_w2core_e2_RESULT.update(max_extra=builder.max_extra)
        return raw_endpoint

    class _c0_w2core_e2__quadratic:

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
    _c0_w2core_e2_RESULT = {}

    def _c0_w2core_e2_apply(ctx):
        divider = ctx.phase.BINDING.divider
        assert divider is ctx.old.divider
        divider.phase_endpoint = _c0_w2core_e2_make_endpoint(ctx.phase)

# agents/micro47/scripts/relocate_cs2.py
def _initialize__c1_relocate_cs2():
    global _c1_relocate_cs2_Fraction, _c1_relocate_cs2_INTEGRATED_ROOT, _c1_relocate_cs2_L, _c1_relocate_cs2_R, _c1_relocate_cs2_TQ, _c1_relocate_cs2_X, _c1_relocate_cs2__IntegratedPath, _c1_relocate_cs2___file__, _c1_relocate_cs2___name__, _c1_relocate_cs2_angle, _c1_relocate_cs2_b, _c1_relocate_cs2_bits, _c1_relocate_cs2_cs, _c1_relocate_cs2_dst, _c1_relocate_cs2_dyadic, _c1_relocate_cs2_f45, _c1_relocate_cs2_f7, _c1_relocate_cs2_head, _c1_relocate_cs2_i, _c1_relocate_cs2_inserted, _c1_relocate_cs2_k, _c1_relocate_cs2_kmsim, _c1_relocate_cs2_le15, _c1_relocate_cs2_lines, _c1_relocate_cs2_lt4, _c1_relocate_cs2_need, _c1_relocate_cs2_newangle, _c1_relocate_cs2_np, _c1_relocate_cs2_ops, _c1_relocate_cs2_out, _c1_relocate_cs2_p, _c1_relocate_cs2_q1, _c1_relocate_cs2_q21, _c1_relocate_cs2_q21new, _c1_relocate_cs2_r, _c1_relocate_cs2_regs, _c1_relocate_cs2_sim, _c1_relocate_cs2_sim2, _c1_relocate_cs2_site, _c1_relocate_cs2_src, _c1_relocate_cs2_sys, _c1_relocate_cs2_text, _c1_relocate_cs2_tq
    "micro47 PHASE RELOCATION v2 of the endpoint's small-x CS correction: Clifford-only replacement (text pass).\n\nThe endpoint block (walk8 family)\n    Z_POW qR (0.25 + e) ; CX q23 q22 ; CCX q22 q25 qT ; CX q23 q22 ; Z_POW qT 0.25 ; CX qT qR ; Z_POW qR 1.75 ;\n    CX qT qR ; HMR qT b ; if b: CZ q22 q25, CZ q23 q25\napplies e*f45 plus i^(f7*f45) with f7 = [x<=15]. Measured on all inputs: f7*f45 = [x<=15] - [x<4] + [x=1].\nIn the normalization forward, at the CCX q36 q1 q21 (q36 = [x<4], q35 = [x<=15], q36*q1 = [x=1], q21 = 1 there):\n    S on q35, S^-1 on q36, and S before / S^-1 after that CCX on q21 (which gives i^[x=1])\napply exactly i^([x<=15] - [x<4] + [x=1]): four Clifford phases, no T, no Toffoli. The endpoint keeps only the\nrotation e*f45. Net: -1 Toffoli and -2 T (= -1.5 per shot). All facts are checked on the full domain first.\nUsage: relocate_cs2.py IN.kmx OUT.kmx"
    _c1_relocate_cs2__IntegratedPath = _import_component('pathlib', 'agents/micro47/scripts/relocate_cs2.py', False).Path
    _c1_relocate_cs2_INTEGRATED_ROOT = _c1_relocate_cs2__IntegratedPath(_c1_relocate_cs2___file__).resolve().parents[3]
    _c1_relocate_cs2_sys = _import_component('sys', 'agents/micro47/scripts/relocate_cs2.py', True)
    _c1_relocate_cs2_sys.path.insert(0, '' + str(_c1_relocate_cs2_INTEGRATED_ROOT) + '/tools')
    _c1_relocate_cs2_np = _import_component('numpy', 'agents/micro47/scripts/relocate_cs2.py', False)
    _c1_relocate_cs2_kmsim = _import_component('kmsim', 'agents/micro47/scripts/relocate_cs2.py', True)
    _c1_relocate_cs2_Fraction = _import_component('fractions', 'agents/micro47/scripts/relocate_cs2.py', False).Fraction
    _c1_relocate_cs2_src, _c1_relocate_cs2_dst = (_c1_relocate_cs2_sys.argv[1], _c1_relocate_cs2_sys.argv[2])
    _c1_relocate_cs2_text = open(_c1_relocate_cs2_src).read()
    _c1_relocate_cs2_lines = _c1_relocate_cs2_text.split('\n')
    _c1_relocate_cs2_head = 0
    while _c1_relocate_cs2_lines[_c1_relocate_cs2_head].split()[0] in ('APPEND_TO_REGISTER', 'REGISTER'):
        _c1_relocate_cs2_head += 1
    _c1_relocate_cs2_ops, _c1_relocate_cs2_regs = _c1_relocate_cs2_kmsim.parse(_c1_relocate_cs2_text)
    _c1_relocate_cs2_L = lambda i: _c1_relocate_cs2_lines[_c1_relocate_cs2_head + i].strip()
    _c1_relocate_cs2_cs = None
    for _c1_relocate_cs2_i in range(len(_c1_relocate_cs2_ops) - 13):
        if not (_c1_relocate_cs2_L(_c1_relocate_cs2_i + 1) == 'CX q23 q22' and _c1_relocate_cs2_L(_c1_relocate_cs2_i + 2).startswith('CCX q22 q25 ') and (_c1_relocate_cs2_L(_c1_relocate_cs2_i + 3) == 'CX q23 q22')):
            continue
        _c1_relocate_cs2_tq = _c1_relocate_cs2_L(_c1_relocate_cs2_i + 2).split()[3]
        if _c1_relocate_cs2_L(_c1_relocate_cs2_i + 4) == 'Z_POW %s 0.25' % _c1_relocate_cs2_tq and _c1_relocate_cs2_L(_c1_relocate_cs2_i + 5).startswith('CX %s ' % _c1_relocate_cs2_tq) and _c1_relocate_cs2_L(_c1_relocate_cs2_i + 6).endswith(' 1.75') and (_c1_relocate_cs2_L(_c1_relocate_cs2_i + 7) == _c1_relocate_cs2_L(_c1_relocate_cs2_i + 5)) and _c1_relocate_cs2_L(_c1_relocate_cs2_i + 8).startswith('HMR %s ' % _c1_relocate_cs2_tq) and (_c1_relocate_cs2_L(_c1_relocate_cs2_i + 10) == 'CZ q22 q25') and (_c1_relocate_cs2_L(_c1_relocate_cs2_i + 11) == 'CZ q23 q25') and (_c1_relocate_cs2_L(_c1_relocate_cs2_i + 12) == 'POP_CONDITION'):
            _c1_relocate_cs2_r = _c1_relocate_cs2_L(_c1_relocate_cs2_i + 5).split()[2]
            assert _c1_relocate_cs2_L(_c1_relocate_cs2_i).startswith('Z_POW %s ' % _c1_relocate_cs2_r) and _c1_relocate_cs2_L(_c1_relocate_cs2_i + 6) == 'Z_POW %s 1.75' % _c1_relocate_cs2_r, (_c1_relocate_cs2_L(_c1_relocate_cs2_i), _c1_relocate_cs2_L(_c1_relocate_cs2_i + 6))
            _c1_relocate_cs2_b = _c1_relocate_cs2_L(_c1_relocate_cs2_i + 8).split()[2]
            assert _c1_relocate_cs2_L(_c1_relocate_cs2_i + 9) == 'PUSH_CONDITION if %s' % _c1_relocate_cs2_b
            _c1_relocate_cs2_cs = (_c1_relocate_cs2_i, _c1_relocate_cs2_r, _c1_relocate_cs2_tq)
            break
    assert _c1_relocate_cs2_cs, 'CS block not found'
    _c1_relocate_cs2_k, _c1_relocate_cs2_R, _c1_relocate_cs2_TQ = _c1_relocate_cs2_cs
    _c1_relocate_cs2_angle = _c1_relocate_cs2_Fraction(_c1_relocate_cs2_L(_c1_relocate_cs2_k).split()[2])
    assert _c1_relocate_cs2_Fraction(1, 4) < _c1_relocate_cs2_angle < _c1_relocate_cs2_Fraction(1, 4) + _c1_relocate_cs2_Fraction(1, 10 ** 6), _c1_relocate_cs2_angle
    _c1_relocate_cs2_newangle = _c1_relocate_cs2_angle - _c1_relocate_cs2_Fraction(1, 4)
    _c1_relocate_cs2_site = None
    for _c1_relocate_cs2_i in range(min(2000, len(_c1_relocate_cs2_ops))):
        if _c1_relocate_cs2_L(_c1_relocate_cs2_i) == 'CCX q36 q1 q21':
            _c1_relocate_cs2_site = _c1_relocate_cs2_i
            break
    assert _c1_relocate_cs2_site is not None, 'normalization CCX q36 q1 q21 not found'
    _c1_relocate_cs2_sim = _c1_relocate_cs2_kmsim.Sim(_c1_relocate_cs2_ops, _c1_relocate_cs2_regs['x'])
    _c1_relocate_cs2_X = _c1_relocate_cs2_np.arange(1, _c1_relocate_cs2_sim.n + 1)

    def _c1_relocate_cs2_bits(v):
        return _c1_relocate_cs2_np.unpackbits(v.view(_c1_relocate_cs2_np.uint8), bitorder='little')[:_c1_relocate_cs2_sim.n].astype(_c1_relocate_cs2_np.int64)
    _c1_relocate_cs2_sim.run(stop=_c1_relocate_cs2_site)
    _c1_relocate_cs2_lt4, _c1_relocate_cs2_le15, _c1_relocate_cs2_q1, _c1_relocate_cs2_q21 = (_c1_relocate_cs2_bits(_c1_relocate_cs2_sim.get('q36')), _c1_relocate_cs2_bits(_c1_relocate_cs2_sim.get('q35')), _c1_relocate_cs2_bits(_c1_relocate_cs2_sim.get('q1')), _c1_relocate_cs2_bits(_c1_relocate_cs2_sim.get('q21')))
    assert _c1_relocate_cs2_np.array_equal(_c1_relocate_cs2_lt4, (_c1_relocate_cs2_X < 4).astype(_c1_relocate_cs2_np.int64)), 'q36 != [x<4]'
    assert _c1_relocate_cs2_np.array_equal(_c1_relocate_cs2_le15, (_c1_relocate_cs2_X <= 15).astype(_c1_relocate_cs2_np.int64)), 'q35 != [x<=15]'
    _c1_relocate_cs2_p = _c1_relocate_cs2_lt4 & _c1_relocate_cs2_q1
    _c1_relocate_cs2_q21new = _c1_relocate_cs2_q21 ^ _c1_relocate_cs2_p
    _c1_relocate_cs2_inserted = (_c1_relocate_cs2_le15 - _c1_relocate_cs2_lt4 + (_c1_relocate_cs2_q21 - _c1_relocate_cs2_q21new)) % 4
    _c1_relocate_cs2_sim2 = _c1_relocate_cs2_kmsim.Sim(_c1_relocate_cs2_ops, _c1_relocate_cs2_regs['x'])
    _c1_relocate_cs2_sim2.run(stop=_c1_relocate_cs2_k + 2)
    _c1_relocate_cs2_f45 = _c1_relocate_cs2_bits(_c1_relocate_cs2_sim2.get(_c1_relocate_cs2_R))
    _c1_relocate_cs2_sim2.run(start=_c1_relocate_cs2_k + 2, stop=_c1_relocate_cs2_k + 4)
    _c1_relocate_cs2_f7 = _c1_relocate_cs2_bits(_c1_relocate_cs2_sim2.get(_c1_relocate_cs2_TQ))
    assert _c1_relocate_cs2_np.array_equal(_c1_relocate_cs2_f7, (_c1_relocate_cs2_X <= 15).astype(_c1_relocate_cs2_np.int64)), 'endpoint temp != [x<=15]'
    _c1_relocate_cs2_need = (_c1_relocate_cs2_f7 & _c1_relocate_cs2_f45) % 4
    assert _c1_relocate_cs2_np.array_equal(_c1_relocate_cs2_inserted, _c1_relocate_cs2_need), 'inserted Clifford phase != endpoint CS phase'
    print('verified on', _c1_relocate_cs2_sim.n, 'inputs: endpoint CS at op', _c1_relocate_cs2_k, '(rotation', _c1_relocate_cs2_R, _c1_relocate_cs2_angle, '->', _c1_relocate_cs2_newangle, '); Clifford site at op', _c1_relocate_cs2_site, '; [x=1] count', int(_c1_relocate_cs2_p.sum()))

    def _c1_relocate_cs2_dyadic(fr):
        num, den = (fr.numerator, fr.denominator)
        kk = den.bit_length() - 1
        digits = str(num * 5 ** kk).rjust(kk + 1, '0')
        whole, frac = (digits[:-kk], digits[-kk:].rstrip('0'))
        return (whole or '0') + ('.' + frac if frac else '')
    assert _c1_relocate_cs2_Fraction(_c1_relocate_cs2_dyadic(_c1_relocate_cs2_newangle)) == _c1_relocate_cs2_newangle
    _c1_relocate_cs2_out = _c1_relocate_cs2_lines[:_c1_relocate_cs2_head]
    for _c1_relocate_cs2_i in range(len(_c1_relocate_cs2_lines) - _c1_relocate_cs2_head):
        if _c1_relocate_cs2_i == _c1_relocate_cs2_site:
            _c1_relocate_cs2_out += ['Z_POW q35 0.5', 'Z_POW q36 1.5', 'Z_POW q21 0.5', _c1_relocate_cs2_lines[_c1_relocate_cs2_head + _c1_relocate_cs2_i], 'Z_POW q21 1.5']
            continue
        if _c1_relocate_cs2_k + 1 <= _c1_relocate_cs2_i <= _c1_relocate_cs2_k + 12:
            continue
        if _c1_relocate_cs2_i == _c1_relocate_cs2_k:
            _c1_relocate_cs2_out.append('Z_POW %s %s' % (_c1_relocate_cs2_R, _c1_relocate_cs2_dyadic(_c1_relocate_cs2_newangle)))
            continue
        _c1_relocate_cs2_out.append(_c1_relocate_cs2_lines[_c1_relocate_cs2_head + _c1_relocate_cs2_i])
    open(_c1_relocate_cs2_dst, 'w').write('\n'.join(_c1_relocate_cs2_out))
    print('wrote', _c1_relocate_cs2_dst)

# agents/width/src/block_replay.py
def _initialize__c2_block_replay():
    global _c2_block_replay_INTEGRATED_ROOT, _c2_block_replay__IntegratedPath, _c2_block_replay___file__, _c2_block_replay___name__, _c2_block_replay_replay
    'Agent width: replay a donor kmx block plan (scripts/make_block_plan.py) through the builder.\n\nwire_map: donor wire -> our qubit for every donor wire live at block entry that the block may touch (by owner role).\next_bits: donor bit name -> our classical bit for bits created before the block. Scratch qubits are allocated at first\ntouch and freed when the donor wire is identically zero; donor HMR bits are fresh builder bits (freed when the donor\nname is re-measured or at block end). Returns the final donor-wire -> qubit map.\n'
    _c2_block_replay__IntegratedPath = _import_component('pathlib', 'agents/width/src/block_replay.py', False).Path
    _c2_block_replay_INTEGRATED_ROOT = _c2_block_replay__IntegratedPath(_c2_block_replay___file__).resolve().parents[3]

    def _c2_block_replay_replay(builder, plan, wire_map, ext_bits=None):
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

# agents/width/src/paid_R_cleanup_q48.py
def _initialize__c3_paid_R_cleanup_q48():
    global _c3_paid_R_cleanup_q48_CERT, _c3_paid_R_cleanup_q48_CERT_PATH, _c3_paid_R_cleanup_q48_CERT_SHA, _c3_paid_R_cleanup_q48_EXPECTED, _c3_paid_R_cleanup_q48_FULL, _c3_paid_R_cleanup_q48_Fraction, _c3_paid_R_cleanup_q48_HERE, _c3_paid_R_cleanup_q48_INTEGRATED_ROOT, _c3_paid_R_cleanup_q48_LAST_REPORT, _c3_paid_R_cleanup_q48_Path, _c3_paid_R_cleanup_q48__IntegratedPath, _c3_paid_R_cleanup_q48___file__, _c3_paid_R_cleanup_q48___name__, _c3_paid_R_cleanup_q48_capture_R_before_inverse, _c3_paid_R_cleanup_q48_cleanup_joint18, _c3_paid_R_cleanup_q48_finish_R_capture, _c3_paid_R_cleanup_q48_hashlib, _c3_paid_R_cleanup_q48_json
    'COPY by agent width of Pro 2 q47_loader_native_v1/paid_R_cleanup_q47.py (sha d1743939...): certificate read from\nthe original directory, `builder.max_qubits==47` asserts accept 47 or 48. No other change.\n\nExplicit paid-R snapshot and joint A13/H5 phase cleanup, Q48.\n\nThe caller keeps the original final root_R_frame inverse call between the\ntwo capture helpers. All preceding arithmetic/preparation calls stay intact.\nThis module owns the retained product and every joint-cleanup measurement.\n'
    _c3_paid_R_cleanup_q48__IntegratedPath = _import_component('pathlib', 'agents/width/src/paid_R_cleanup_q48.py', False).Path
    _c3_paid_R_cleanup_q48_INTEGRATED_ROOT = _c3_paid_R_cleanup_q48__IntegratedPath(_c3_paid_R_cleanup_q48___file__).resolve().parents[3]
    _c3_paid_R_cleanup_q48_Path = _import_component('pathlib', 'agents/width/src/paid_R_cleanup_q48.py', False).Path
    _c3_paid_R_cleanup_q48_Fraction = _import_component('fractions', 'agents/width/src/paid_R_cleanup_q48.py', False).Fraction
    _c3_paid_R_cleanup_q48_hashlib = _import_component('hashlib', 'agents/width/src/paid_R_cleanup_q48.py', True)
    _c3_paid_R_cleanup_q48_json = _import_component('json', 'agents/width/src/paid_R_cleanup_q48.py', True)
    _c3_paid_R_cleanup_q48_HERE = _c3_paid_R_cleanup_q48_Path('' + str(_c3_paid_R_cleanup_q48_INTEGRATED_ROOT) + '/work/pro2_q47_loader/work/loaders/q47_loader_native_v1')
    _c3_paid_R_cleanup_q48_CERT_SHA = '9c4b4aea56ad334f7082608d3a24193d900390c76e578e48aa67a88456664ff7'
    _c3_paid_R_cleanup_q48_CERT_PATH = _c3_paid_R_cleanup_q48_HERE / 'paid_R_cleanup_certificate.json'
    _c3_paid_R_cleanup_q48_CERT = _json_loads(_read_text(_c3_paid_R_cleanup_q48_CERT_PATH))
    pass
    _c3_paid_R_cleanup_q48_EXPECTED = _c3_paid_R_cleanup_q48_Fraction(*_c3_paid_R_cleanup_q48_CERT['selected']['mean_fraction'])
    assert _c3_paid_R_cleanup_q48_EXPECTED == _c3_paid_R_cleanup_q48_Fraction(809, 128)
    _c3_paid_R_cleanup_q48_FULL = (1 << 128) - 1
    _c3_paid_R_cleanup_q48_LAST_REPORT = None

    def _c3_paid_R_cleanup_q48_capture_R_before_inverse(builder, framed_a3):
        """At44 owners, copy the current framed v8=R into one new zero owner."""
        assert builder.max_qubits in (46, 47, 48) and builder.num_allocated_qubits == 44
        product = builder.alloc_qubits(1)[0]
        assert product != framed_a3
        builder.cx(framed_a3, product)
        assert builder.num_allocated_qubits == 45
        return product

    def _c3_paid_R_cleanup_q48_finish_R_capture(builder, raw_a3, raw_a2, product):
        """After the unchanged inverse frame, leave p=R+a3+a2=a1*(a2+a5)."""
        assert builder.num_allocated_qubits == 45
        assert len({raw_a3, raw_a2, product}) == 3
        builder.cx(raw_a3, product)
        builder.cx(raw_a2, product)
        return product

    def _c3_paid_R_cleanup_q48_cleanup_joint18(builder, address7, A13, H5, product, debts, *, table_api):
        """Erase A13/H5, all phase helpers and paid p; retain all26 body owners."""
        global _c3_paid_R_cleanup_q48_LAST_REPORT
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
        assert paid_truth == int(_c3_paid_R_cleanup_q48_CERT['free_coordinate']['truth'], 16)
        flushed = debts.flush(builder, address + A + H[:3], raw + output_truths[:16])
        assert not debts.pending and flushed['quadratic_rank'] == 128
        selected = _c3_paid_R_cleanup_q48_CERT['selected']
        masks = selected['masks']
        assert len(masks) == len(cb.BinarySpan(masks).pivots) == 18
        framed = [cb.parity_function(m, output_truths) for m in masks]
        outputs = A + H
        api.emit_affine_frame(builder, address, outputs, [m << 8 for m in masks])
        producers = []
        helper_truths = []
        for item in _c3_paid_R_cleanup_q48_CERT['bank_steps']:
            plan = api.plan_from_json(item['plan'])
            truth = int(item['truth'], 16)
            assert plan.width == 8 + len(producers) and plan.and_count == 1
            assert plan.evaluate_factored_functions(base_truths + helper_truths, _c3_paid_R_cleanup_q48_FULL) == truth
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
            assert plan.evaluate_functions(base_truths + helper_truths[:prefix] + framed[:index], _c3_paid_R_cleanup_q48_FULL) == framed[index]
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
        paid_plan = api.plan_from_json(_c3_paid_R_cleanup_q48_CERT['free_coordinate']['final_erase_plan'])
        assert paid_plan.width == 7 and paid_plan.evaluate_functions(raw, _c3_paid_R_cleanup_q48_FULL) == paid_truth
        cb.emit_erase(builder, address, [product], [paid_plan])
        builder.free(product)
        trace.append(builder.num_allocated_qubits)
        assert [sorted(s) for s in users] == selected['users']
        expected = sum((1 - _c3_paid_R_cleanup_q48_Fraction(1, 1 << len(s)) for s in users), _c3_paid_R_cleanup_q48_Fraction(0))
        assert expected == _c3_paid_R_cleanup_q48_EXPECTED and builder.num_allocated_qubits == 26
        assert max(trace) <= selected['cleanup_peak_bound'] <= 47 and (not debts.pending)
        _c3_paid_R_cleanup_q48_LAST_REPORT = dict(status='EMITTED_PAID_R18_COMPONENT_NATIVE_PROOF_PENDING', expected_Toffolis=float(expected), expected_fraction=[expected.numerator, expected.denominator], entry=45, return_owners=26, capture_peak=45, cleanup_peak_bound=selected['cleanup_peak_bound'], trace=trace, output_signs_repaid=18, paid_product_sign_repaid=True, helper_signs_all_branches_repaid=True, incoming_table_debts_repaid=flushed['outcomes'], incoming_flush_unchanged=True, compute_sites=compute_sites, helper_activation_users=[sorted(s) for s in users], producer_added_Toffolis=0, producer_added_CNOTs=3, root_frame_and_arithmetic_callbacks_external_and_unchanged=True, certificate_sha256=_c3_paid_R_cleanup_q48_CERT_SHA)
        return _c3_paid_R_cleanup_q48_LAST_REPORT

# patches/patch_coef2_q46.py
def _initialize__c4_patch_coef2_q46():
    global _c4_patch_coef2_q46_INTEGRATED_ROOT, _c4_patch_coef2_q46_STATE, _c4_patch_coef2_q46__IntegratedPath, _c4_patch_coef2_q46___file__, _c4_patch_coef2_q46___name__, _c4_patch_coef2_q46_apply, _c4_patch_coef2_q46_make
    'prodcoef2 patch COEF2Q46: the SECOND coefficient forward at cap 46 for +1 expected Toffoli.\n\nFact used (the pinned H4 plan, slope_h3_h4_retirement_v3.json): H4 = D12 ^ H3 ^ D11*H3, so D12 = H4 ^ H3 ^ D11*H3.\nIn the second coefficient forward D12 is idle through the five coefficient rows (rows touch D[:7]; sources are\nS = v8, H0..H4) and H4 is idle through the overflow (D[7:13] += wrap) and is erased right after the forward anyway.\nSecond call only (v[11] already retired):\n  1. X-measure D12 before the rows (outcome m): the rows then peak at 46 instead of 47;\n  2. after the rows turn the H4 wire into D12 in place (CX H3, CCX D11 H3: 1 Toffoli) and pay m by Z on the\n     rebuilt D12 owner; the overflow then also peaks at 46;\n  3. erase_high_H skips the H4 erasure of that call (H4 no longer exists; its wire is D[12]).\nRows and overflow are the COEFDISP kernels (own copy of agents/prodcoef/patch_coefdisp.py), so the debt positions\nand widths are unchanged and merge_coefficient_transcripts stays valid. The first call goes to whatever\ncoefficient_forward is live. Compose AFTER patch_coefdisp.py (and before patch_capwin46.py if that is used).\nReplaces baseline.coefficient_forward and baseline.erase_high_H (both delegate to the previous ones otherwise).\n'
    _c4_patch_coef2_q46__IntegratedPath = _import_component('pathlib', 'patches/patch_coef2_q46.py', False).Path
    _c4_patch_coef2_q46_INTEGRATED_ROOT = _c4_patch_coef2_q46__IntegratedPath(_c4_patch_coef2_q46___file__).resolve().parents[1]
    _c4_patch_coef2_q46_STATE = dict(calls=0, converted=None, applied=0)

    def _c4_patch_coef2_q46_make(baseline, previous_forward, previous_erase):
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
            _c4_patch_coef2_q46_STATE['converted'] = h4
            _c4_patch_coef2_q46_STATE['applied'] += 1
            overflow_forward_disposable(builder, v[:5], S, D, token)
            return token

        def coefficient_forward(builder, v, D, H):
            _c4_patch_coef2_q46_STATE['calls'] += 1
            if _c4_patch_coef2_q46_STATE['calls'] == 2:
                return second_forward(builder, v, D, H)
            return previous_forward(builder, v, D, H)

        def erase_high_H(builder, v, D, H, *, initial=False):
            h4 = _c4_patch_coef2_q46_STATE['converted']
            if h4 is not None and (not initial) and (len(H) == 5) and (H[4] is h4):
                assert D[12] is h4
                _c4_patch_coef2_q46_STATE['converted'] = None
                variables = [D[i] for i in (9, 10, 11, 12)] + [H[2], v[10]]
                baseline._erase(builder, H[3], variables, baseline.H3_CURRENT)
                return list(H[:3])
            return previous_erase(builder, v, D, H, initial=initial)
        return (coefficient_forward, erase_high_H)

    def _c4_patch_coef2_q46_apply(ctx):
        bl = ctx.baseline
        for name in ('_erase', 'H3_CURRENT', '_coefficient_carry', '_clear_coefficient_carry', 'SimpleNamespace', 'ar', 'km'):
            assert hasattr(bl, name), name
        bl.coefficient_forward, bl.erase_high_H = _c4_patch_coef2_q46_make(bl, bl.coefficient_forward, bl.erase_high_H)

# patches/patch_coefdisp.py
def _initialize__c5_patch_coefdisp():
    global _c5_patch_coefdisp_INTEGRATED_ROOT, _c5_patch_coefdisp__IntegratedPath, _c5_patch_coefdisp___file__, _c5_patch_coefdisp___name__, _c5_patch_coefdisp_apply, _c5_patch_coefdisp_make
    "prodcoef patch COEFDISP: coefficient forward with early release of its owned\nincoming carries (Pro 1's research/q47_forward_disposable/forward_source.py,\ncoefficient_forward_disposable + coefficient_overflow_forward_disposable +\nforward_add_disposable, copied with baseline/km bound explicitly).\n\nZero Toffolis by itself: the owned rounding carry (and the overflow wrap) is\nerased by del_and right after the first sum, so both coefficient forwards peak\nat 47. The recomputed R-frame product (ops ~5873/~6198) then has a spare wire\nover the whole first coefficient forward, which the lead's hold pass uses.\nDebt positions/widths are identical to the original (merge stays valid).\nReplaces baseline.coefficient_forward only.\n"
    _c5_patch_coefdisp__IntegratedPath = _import_component('pathlib', 'patches/patch_coefdisp.py', False).Path
    _c5_patch_coefdisp_INTEGRATED_ROOT = _c5_patch_coefdisp__IntegratedPath(_c5_patch_coefdisp___file__).resolve().parents[1]

    def _c5_patch_coefdisp_make(baseline):
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

    def _c5_patch_coefdisp_apply(ctx):
        ctx.baseline.coefficient_forward = _c5_patch_coefdisp_make(ctx.baseline)

# patches/patch_donor_first60.py
def _initialize__c6_patch_donor_first60():
    global _c6_patch_donor_first60_EXPECT, _c6_patch_donor_first60_HERE, _c6_patch_donor_first60_INTEGRATED_ROOT, _c6_patch_donor_first60_PLAN_FILES, _c6_patch_donor_first60_Path, _c6_patch_donor_first60_REPORT, _c6_patch_donor_first60_USE, _c6_patch_donor_first60__IntegratedPath, _c6_patch_donor_first60___file__, _c6_patch_donor_first60___name__, _c6_patch_donor_first60__plan, _c6_patch_donor_first60_apply, _c6_patch_donor_first60_json, _c6_patch_donor_first60_os, _c6_patch_donor_first60_replay
    "Agent width (FIRST LOADER ONLY variant, for Q47 builds where the second loader is Pro 2 second90): transplant candidate11r2's first60 / second78 loaders (Pro 2 port03) by native-text replay.\n\nThe donor loaders differ from candidate10's first61 / second79 only in their final segment (measured, rename-aware\ndiff). Their gate text is replayed from the donor kmx through our builder (plans/L1_first60.json,\nplans/L2_second78.json made by scripts/make_replay_plan.py on the full domain): scratch owners are allocated at first\ntouch and freed when the donor wire is identically zero; every donor HMR is re-emitted as TableDebts.erase with the\nmeasured 128-row truth of the raw table address, so OUR shared table cleanup (universal flush) repays it.\nReplaces only tables07.load_joint16 (per variant; env WIDTH_DONOR_L1 / WIDTH_DONOR_L2, default both on).\n"
    _c6_patch_donor_first60__IntegratedPath = _import_component('pathlib', 'patches/patch_donor_first60.py', False).Path
    _c6_patch_donor_first60_INTEGRATED_ROOT = _c6_patch_donor_first60__IntegratedPath(_c6_patch_donor_first60___file__).resolve().parents[1]
    _c6_patch_donor_first60_json = _import_component('json', 'patches/patch_donor_first60.py', True)
    _c6_patch_donor_first60_os = _import_component('os', 'patches/patch_donor_first60.py', True)
    _c6_patch_donor_first60_Path = _import_component('pathlib', 'patches/patch_donor_first60.py', False).Path
    _c6_patch_donor_first60_HERE = _c6_patch_donor_first60_Path('' + str(_c6_patch_donor_first60_INTEGRATED_ROOT) + '/agents/width')
    _c6_patch_donor_first60_USE = dict(first=True, second=False)
    _c6_patch_donor_first60_PLAN_FILES = dict(first=_c6_patch_donor_first60_HERE / 'plans/L1_first60.json', second=_c6_patch_donor_first60_HERE / 'plans/L2_second78.json')
    _c6_patch_donor_first60_EXPECT = dict(first=dict(ccx=60, hmr=42), second=dict(ccx=78, hmr=63))
    _c6_patch_donor_first60_REPORT = {}

    def _c6_patch_donor_first60__plan(which):
        data = _json_loads(_read_text(_c6_patch_donor_first60_PLAN_FILES[which]))
        assert data['ccx'] == _c6_patch_donor_first60_EXPECT[which]['ccx'] and data['hmr'] == _c6_patch_donor_first60_EXPECT[which]['hmr']
        return data

    def _c6_patch_donor_first60_replay(builder, data, address7, debts):
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

    def _c6_patch_donor_first60_apply(ctx):
        tables = ctx.tables
        original = tables.load_joint16

        def load_joint16(builder, address7, *, variant, debts):
            if not _c6_patch_donor_first60_USE.get(variant):
                return original(builder, address7, variant=variant, debts=debts)
            assert isinstance(debts, tables.TableDebts)
            before = debts.total_recorded
            D, H, counts = _c6_patch_donor_first60_replay(builder, _c6_patch_donor_first60__plan(variant), list(address7), debts)
            assert debts.total_recorded - before == _c6_patch_donor_first60_EXPECT[variant]['hmr']
            _c6_patch_donor_first60_REPORT[variant] = counts
            return (D, H)
        tables.load_joint16 = load_joint16

# patches/patch_endpoint_v9e2.py
def _initialize__c7_patch_endpoint_v9e2():
    global _c7_patch_endpoint_v9e2_E_HOLD, _c7_patch_endpoint_v9e2_FORM, _c7_patch_endpoint_v9e2_F_HOLD, _c7_patch_endpoint_v9e2_INTEGRATED_ROOT, _c7_patch_endpoint_v9e2_Path, _c7_patch_endpoint_v9e2_R2, _c7_patch_endpoint_v9e2_ROLE, _c7_patch_endpoint_v9e2__CORE, _c7_patch_endpoint_v9e2__FORM_PATH, _c7_patch_endpoint_v9e2__IntegratedPath, _c7_patch_endpoint_v9e2___file__, _c7_patch_endpoint_v9e2___name__, _c7_patch_endpoint_v9e2__core, _c7_patch_endpoint_v9e2__f, _c7_patch_endpoint_v9e2__spec, _c7_patch_endpoint_v9e2_a, _c7_patch_endpoint_v9e2_apply, _c7_patch_endpoint_v9e2_b, _c7_patch_endpoint_v9e2_c, _c7_patch_endpoint_v9e2_d, _c7_patch_endpoint_v9e2_hashlib, _c7_patch_endpoint_v9e2_importlib, _c7_patch_endpoint_v9e2_json, _c7_patch_endpoint_v9e2_os, _c7_patch_endpoint_v9e2_x
    "COMPOSER PIN e2 (frozen copy of the width2 endpoint exactly as built in runs/cmp_q46h = deliver/q46t8: patch sha 4fce573e...,\ncore agents/composer/p/w2core_e2.py = width2 core sha d7809457..., form agents/composer/p/v9_form_e2.json sha c9b1ab28...;\nwidth2 edits its files in place, so delivered builds load these frozen copies; env W2_* must be unset).\nwidth2: Q46 walk8 endpoint with root bit v9 ALSO retired across the endpoint (one more spare lane), so the\nQ47 hold sets fit at real allocation <= 46. v9 is rebuilt at exit from (v8, s12..s16) by the exact straight-line\nAND program in W2_V9_FORM (tools/minand_sat.py JSON; inputs named by wire in the measuring build, mapped to roles\nbelow). Hold sets from env W2_E_HOLD / W2_F_HOLD / W2_R2 (defaults = walk8q47's). Core = agents/width2/p/w2_walk8_core.py.\nv10 is then rebuilt with ONE AND from gate g1 of the v9 program: v10 = v9 ^ g1 ^ (s13^g1)(v9^s14) (exact on the full\ndomain; env W2_V10_G1=0 keeps the phase agent's 2-AND v10 rebuild).\nW2_V9_PLACEHOLDER=1: ANALYSIS ONLY (wrong circuit): rebuild v9 as 0, to measure the gross value.\nReplaces only divider.phase_endpoint."
    _c7_patch_endpoint_v9e2__IntegratedPath = _import_component('pathlib', 'patches/patch_endpoint_v9e2.py', False).Path
    _c7_patch_endpoint_v9e2_INTEGRATED_ROOT = _c7_patch_endpoint_v9e2__IntegratedPath(_c7_patch_endpoint_v9e2___file__).resolve().parents[1]
    _c7_patch_endpoint_v9e2_importlib = _import_component('importlib.util', 'patches/patch_endpoint_v9e2.py', True)
    _c7_patch_endpoint_v9e2_json = _import_component('json', 'patches/patch_endpoint_v9e2.py', True)
    _c7_patch_endpoint_v9e2_os = _import_component('os', 'patches/patch_endpoint_v9e2.py', True)
    _c7_patch_endpoint_v9e2_Path = _import_component('pathlib', 'patches/patch_endpoint_v9e2.py', False).Path
    _c7_patch_endpoint_v9e2__CORE = _c7_patch_endpoint_v9e2_Path('' + str(_c7_patch_endpoint_v9e2_INTEGRATED_ROOT) + '/agents/composer/p/w2core_e2.py')
    _c7_patch_endpoint_v9e2__spec = _spec('width2_walk8_core_v9', _c7_patch_endpoint_v9e2__CORE)
    _c7_patch_endpoint_v9e2__core = _new_module(_c7_patch_endpoint_v9e2__spec)
    _c7_patch_endpoint_v9e2__spec.loader.exec_module(_c7_patch_endpoint_v9e2__core)
    _c7_patch_endpoint_v9e2__core.QMAX = 46
    _c7_patch_endpoint_v9e2_ROLE = {'q18': 'v8', 'q17': 'v7', 'q9': 's12', 'q34': 's13', 'q36': 's14', 'q0': 's15', 'q30': 's16', 'q32': 's17'}
    if _c7_patch_endpoint_v9e2_os.environ.get('W2_V9_PLACEHOLDER') == '1':
        _c7_patch_endpoint_v9e2_FORM = dict(inputs=[], gates=[], output=dict(constant=0, terms=[]))
    else:
        _c7_patch_endpoint_v9e2__f = _json_loads(_read_text(_c7_patch_endpoint_v9e2_Path(_c7_patch_endpoint_v9e2_os.environ.get('W2_V9_FORM', '' + str(_c7_patch_endpoint_v9e2_INTEGRATED_ROOT) + '/agents/composer/p/v9_form_e2.json'))))
        assert _c7_patch_endpoint_v9e2__f['status'] == 'SAT'
        _c7_patch_endpoint_v9e2_FORM = dict(inputs=[_c7_patch_endpoint_v9e2_ROLE[x] for x in _c7_patch_endpoint_v9e2__f['inputs']], gates=_c7_patch_endpoint_v9e2__f['gates'], output=_c7_patch_endpoint_v9e2__f['output'])
    _c7_patch_endpoint_v9e2__core.RETIRE_V9 = _c7_patch_endpoint_v9e2_FORM
    _c7_patch_endpoint_v9e2_hashlib = _import_component('hashlib', 'patches/patch_endpoint_v9e2.py', True)
    _c7_patch_endpoint_v9e2__FORM_PATH = _c7_patch_endpoint_v9e2_Path(_c7_patch_endpoint_v9e2_os.environ.get('W2_V9_FORM', '' + str(_c7_patch_endpoint_v9e2_INTEGRATED_ROOT) + '/agents/composer/p/v9_form_e2.json'))
    _c7_patch_endpoint_v9e2__core.V10_FROM_G1 = True
    _c7_patch_endpoint_v9e2_E_HOLD = set((int(x) for x in _c7_patch_endpoint_v9e2_os.environ.get('W2_E_HOLD', ','.join(map(str, range(1, 13)))).split(',') if x))
    _c7_patch_endpoint_v9e2_F_HOLD = set((int(x) for x in _c7_patch_endpoint_v9e2_os.environ.get('W2_F_HOLD', ','.join(map(str, range(13)))).split(',') if x))
    _c7_patch_endpoint_v9e2_R2 = {(a, b): (c, d) for a, b, c, d in _json_loads(_c7_patch_endpoint_v9e2_os.environ.get('W2_R2', '[[11,13,0,2],[10,14,0,3],[7,17,3,6],[6,18,4,7]]'))}

    def _c7_patch_endpoint_v9e2_apply(ctx):
        divider = ctx.phase.BINDING.divider
        assert divider is ctx.old.divider
        divider.phase_endpoint = _c7_patch_endpoint_v9e2__core.make_endpoint(ctx.phase, _c7_patch_endpoint_v9e2_E_HOLD, _c7_patch_endpoint_v9e2_F_HOLD, _c7_patch_endpoint_v9e2_R2)

# patches/patch_fwd_narrow.py
def _initialize__c8_patch_fwd_narrow():
    global _c8_patch_fwd_narrow_INTEGRATED_ROOT, _c8_patch_fwd_narrow__IntegratedPath, _c8_patch_fwd_narrow___file__, _c8_patch_fwd_narrow___name__, _c8_patch_fwd_narrow_apply
    "Narrow forward normalization: same 18+1+32 Toffolis, no conditional CCZ, local peak 37 instead of 46.\n\nChanges against normalization9475.forward (inverse untouched, n22/flags4 interface identical):\n1. P1 = NOT x21 gets no wire: X(x21) turns x21 into P1; it is used as a CX source while it is P1 and then\n   becomes the H accumulator (H = 1 xor P1 xor ... xor P20 xor P20*NOT x1), so it is never measured.\n2. Every odd prefix P_(L-1) is measured right after P_L is computed and its CX uses are done. Its HMR\n   fix-up uses the running parity x21 = 1 xor sum_(l<=L) P_l:\n       P_(L-1) = P_(L-2) xor P_(L-2)*x21 xor P_L*x21      (L even)  -> Z/CZ only.\n   The leading-one clearing of position 22-L, and the x0/x1/H accumulations, are done as soon as P_L\n   exists (position 22-L is no longer needed as data). x1 is accumulated early; when P20 = 1 all\n   P1..P19 are 1, so the accumulated x1' equals NOT x1 and CCX(P20, x1', x21) is the base H gate.\n3. Thresholds are erased with the neighbour trick of patch_fwd_neighbor (no conditional CCZ).\n"
    _c8_patch_fwd_narrow__IntegratedPath = _import_component('pathlib', 'patches/patch_fwd_narrow.py', False).Path
    _c8_patch_fwd_narrow_INTEGRATED_ROOT = _c8_patch_fwd_narrow__IntegratedPath(_c8_patch_fwd_narrow___file__).resolve().parents[1]

    def _c8_patch_fwd_narrow_apply(ctx):
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

# patches/patch_h2ret.py
def _initialize__c9_patch_h2ret():
    global _c9_patch_h2ret_INTEGRATED_ROOT, _c9_patch_h2ret_STATE, _c9_patch_h2ret__IntegratedPath, _c9_patch_h2ret___file__, _c9_patch_h2ret___name__, _c9_patch_h2ret__and_into, _c9_patch_h2ret__form, _c9_patch_h2ret__unform, _c9_patch_h2ret_apply, _c9_patch_h2ret_rebuild_h2
    "prodcoef2 patch H2RET: retire the second-table metadata bit H2 through the whole inverse product + seed cleanup\n(one more clean wire for every inverse adder row) and rebuild it with 3 Toffolis before the late metadata (T1).\n\nMeasured fact (full domain, Q46 raw build pc2_q46a, op 22342 = inverse_product_data; 39 reachable rows of 64):\nH2 is a function of D9, D10, D11, D12, H0, H1 only, and the exact minimum-AND search (tools/minand_sat.py) gives\nk=1 UNSAT, k=2 UNSAT, k=3 SAT:\n    H2 = D10 ^ D11 ^ D12 ^ (D9^D11)(D9^H1) ^ g0*M,   g0 = (D9^D10^D11^H1)(D10^H0),   M = D9^D10^D11^D12^H0^H1.\nD (post second coefficient forward), H0 and H1 are unchanged through the inverse product (source / dirty spectators).\nH2's last use before the inverse product is the H3 erasure of the second erase_high_H call; next use is T1.\nSteps: X-measure H2 at the start of product_inverse (removed from the dirty list); after seed_cleanup rebuild it on a\nfresh wire (3 CCX; the temporary g0 is X-measured, its sign paid by CZ on its two factors); pay H2's outcome by Z on\nthe rebuilt owner; the body's Hlow list (the object returned by erase_high_H) gets the new owner in place.\nWraps baseline.erase_high_H, lifecycle.product_inverse and baseline.seed_cleanup (all delegate). Apply AFTER\npatch_seedinv.py (and after patch_coef2_q46.py if used).\n"
    _c9_patch_h2ret__IntegratedPath = _import_component('pathlib', 'patches/patch_h2ret.py', False).Path
    _c9_patch_h2ret_INTEGRATED_ROOT = _c9_patch_h2ret__IntegratedPath(_c9_patch_h2ret___file__).resolve().parents[1]
    _c9_patch_h2ret_STATE = dict(erase_calls=0, hlow=None, outcome=None, applied=0)

    def _c9_patch_h2ret__form(builder, wires):
        """XOR of wires onto a fresh temporary (returns (wire, owned))."""
        if len(wires) == 1:
            return (wires[0], False)
        t = builder.alloc_qubits(1)[0]
        for w in wires:
            builder.cx(w, t)
        return (t, True)

    def _c9_patch_h2ret__unform(builder, t, owned, wires):
        if owned:
            for w in wires:
                builder.cx(w, t)
            builder.free(t)

    def _c9_patch_h2ret__and_into(builder, left, right, target):
        a, oa = _c9_patch_h2ret__form(builder, left)
        b, ob = _c9_patch_h2ret__form(builder, right)
        builder.ccx(a, b, target)
        _c9_patch_h2ret__unform(builder, b, ob, right)
        _c9_patch_h2ret__unform(builder, a, oa, left)

    def _c9_patch_h2ret_rebuild_h2(builder, D, H0, H1):
        D9, D10, D11, D12 = (D[9], D[10], D[11], D[12])
        L0 = [D9, D10, D11, H1]
        R0 = [D10, H0]
        M = [D9, D10, D11, D12, H0, H1]
        t = builder.alloc_qubits(1)[0]
        for w in (D10, D11, D12):
            builder.cx(w, t)
        _c9_patch_h2ret__and_into(builder, [D9, D11], [D9, H1], t)
        g0 = builder.alloc_qubits(1)[0]
        _c9_patch_h2ret__and_into(builder, L0, R0, g0)
        _c9_patch_h2ret__and_into(builder, [g0], M, t)
        m = builder.alloc_bits(1)[0]
        builder.hmr(g0, m)
        builder.free(g0)
        a, oa = _c9_patch_h2ret__form(builder, L0)
        b, ob = _c9_patch_h2ret__form(builder, R0)
        builder.push_condition(m)
        builder.cz(a, b)
        builder.pop_condition()
        _c9_patch_h2ret__unform(builder, b, ob, R0)
        _c9_patch_h2ret__unform(builder, a, oa, L0)
        builder.free(m)
        return t

    def _c9_patch_h2ret_apply(ctx):
        bl = ctx.baseline
        lc = ctx.components['lifecycle']
        previous_erase = bl.erase_high_H
        previous_inverse = lc.product_inverse
        previous_cleanup = bl.seed_cleanup

        def erase_high_H(builder, v, D, H, *, initial=False):
            out = previous_erase(builder, v, D, H, initial=initial)
            if not initial:
                _c9_patch_h2ret_STATE['erase_calls'] += 1
                if _c9_patch_h2ret_STATE['erase_calls'] == 2:
                    out = list(out)
                    _c9_patch_h2ret_STATE['hlow'] = out
            return out

        def product_inverse(builder, v, D, word, token, dirty):
            hlow = _c9_patch_h2ret_STATE['hlow']
            assert hlow is not None and len(hlow) == 3 and (hlow[2] is not None)
            h2 = hlow[2]
            assert sum((1 for q in dirty if q is h2)) == 1
            m = builder.alloc_bits(1)[0]
            builder.hmr(h2, m)
            builder.free(h2)
            hlow[2] = None
            _c9_patch_h2ret_STATE['outcome'] = m
            dirty = [q for q in dirty if q is not h2]
            return previous_inverse(builder, v, D, word, token, dirty)

        def seed_cleanup(builder, v, D, seed, token):
            out = previous_cleanup(builder, v, D, seed, token)
            hlow = _c9_patch_h2ret_STATE['hlow']
            if hlow is not None and hlow[2] is None:
                t = _c9_patch_h2ret_rebuild_h2(builder, D, hlow[0], hlow[1])
                m = _c9_patch_h2ret_STATE['outcome']
                _c9_patch_h2ret_STATE['outcome'] = None
                builder.push_condition(m)
                builder.z(t)
                builder.pop_condition()
                builder.free(m)
                hlow[2] = t
                _c9_patch_h2ret_STATE['applied'] += 1
            return out
        bl.erase_high_H = erase_high_H
        lc.product_inverse = product_inverse
        bl.seed_cleanup = seed_cleanup

# patches/patch_hret_sat_s15k7a.py
def _initialize__c10_patch_hret_sat_s15k7a():
    global _c10_patch_hret_sat_s15k7a_EXTRA, _c10_patch_hret_sat_s15k7a_FORCE, _c10_patch_hret_sat_s15k7a_FORMULAS, _c10_patch_hret_sat_s15k7a_INTEGRATED_ROOT, _c10_patch_hret_sat_s15k7a_Path, _c10_patch_hret_sat_s15k7a_RETIRE, _c10_patch_hret_sat_s15k7a__IntegratedPath, _c10_patch_hret_sat_s15k7a__RELAXED, _c10_patch_hret_sat_s15k7a__ROLES, _c10_patch_hret_sat_s15k7a__SAT, _c10_patch_hret_sat_s15k7a___file__, _c10_patch_hret_sat_s15k7a___name__, _c10_patch_hret_sat_s15k7a__cleanup, _c10_patch_hret_sat_s15k7a__emit_sat, _c10_patch_hret_sat_s15k7a__feed_row, _c10_patch_hret_sat_s15k7a__json, _c10_patch_hret_sat_s15k7a__k, _c10_patch_hret_sat_s15k7a__kernel, _c10_patch_hret_sat_s15k7a__pair_forms, _c10_patch_hret_sat_s15k7a__plan, _c10_patch_hret_sat_s15k7a__undo, _c10_patch_hret_sat_s15k7a_apply, _c10_patch_hret_sat_s15k7a_cleanup_divider, _c10_patch_hret_sat_s15k7a_f, _c10_patch_hret_sat_s15k7a_i, _c10_patch_hret_sat_s15k7a_importlib, _c10_patch_hret_sat_s15k7a_json, _c10_patch_hret_sat_s15k7a_k, _c10_patch_hret_sat_s15k7a_os, _c10_patch_hret_sat_s15k7a_p, _c10_patch_hret_sat_s15k7a_restore, _c10_patch_hret_sat_s15k7a_restore_sat, _c10_patch_hret_sat_s15k7a_sys
    'COMPOSER FROZEN PIN s15k7a (forms: k=15 hret_s15k7a_s15.json sha a742f55004f9; environment W2_HRET_SAT ignored).\nwidth2 copy of the divider patch HRET q46 with SAT-form restores: env W2_HRET_SAT = "k:path.json,..." gives, for history\nsign k, an exact straight-line AND program (tools/minand_sat.py JSON) over role-named inputs (v0..v11 = token.v, "next" =\ns_{k+1} = token.u[-1] at the rebuild point); k is then also retired after the endpoint and rebuilt right before its\ninverse row from that program (factors formed in place, helpers X-measured + CZ), sign paid by Z on the rebuilt owner.\nW2_HRET_SAT_ROLES maps the JSON input names to roles (default: q16..q20,q42 -> v6..v11, q30 -> next).\nOriginal docstring: Divider patch HRET (cap-aware 48/47/46): retire history signs 13..K after the phase endpoint and rebuild each one\nright before its inverse row from root bits and the next sign; history12 retirement as in AR004.\n\nReplaces only ctx.old.divider.cleanup_divider. Forward, endpoint and phase are unchanged.\n- cap >= 48: pinned top12 kernel for the final row (as patch_hret14.py, byte-identical output).\n- cap 47:   relaxed top12 copy ((4,4,4) final-row partition), as patch_hret14_cap.py.\n- cap 46:   the final feed row j12 runs through the ordinary adaptive inverse_add (feed-carry lifecycle) and the\n            original candidate01 cleanup_u12 (1 Toffoli, peak 45), because the top12 kernel cannot fit 12 lower\n            positions at 42 data owners under 46.\nEnv DIVIDER_FORCE_CAP=46 lowers the builder cap to 46 only inside this cleanup (measurement inside a Q47 build).\nEnv DIVIDER_RETIRE="13,14" (default) selects the retired signs (15 needs its formula below).\n'
    _c10_patch_hret_sat_s15k7a__IntegratedPath = _import_component('pathlib', 'patches/patch_hret_sat_s15k7a.py', False).Path
    _c10_patch_hret_sat_s15k7a_INTEGRATED_ROOT = _c10_patch_hret_sat_s15k7a__IntegratedPath(_c10_patch_hret_sat_s15k7a___file__).resolve().parents[1]
    _c10_patch_hret_sat_s15k7a_os = _import_component('os', 'patches/patch_hret_sat_s15k7a.py', True)
    _c10_patch_hret_sat_s15k7a_sys = _import_component('sys', 'patches/patch_hret_sat_s15k7a.py', True)
    _c10_patch_hret_sat_s15k7a_importlib = _import_component('importlib.util', 'patches/patch_hret_sat_s15k7a.py', True)
    _c10_patch_hret_sat_s15k7a_Path = _import_component('pathlib', 'patches/patch_hret_sat_s15k7a.py', False).Path
    _c10_patch_hret_sat_s15k7a__RELAXED = _c10_patch_hret_sat_s15k7a_Path('' + str(_c10_patch_hret_sat_s15k7a_INTEGRATED_ROOT) + '/agents/divider/src/top12_kernel_relaxed.py')
    _c10_patch_hret_sat_s15k7a_FORMULAS = {13: dict(parents=[('v', 8), ('v', 9), ('v', 10), ('v', 11), ('next',)], helpers=[dict(width=5, constant=0, linear=2, edges=[(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)])], decoder=dict(width=6, constant=0, linear=46, edges=[(1, 3), (1, 5), (3, 4), (4, 5)]), ands=2), 14: dict(parents=[('v', 7), ('v', 8), ('v', 9), ('v', 10), ('v', 11), ('next',)], helpers=[dict(width=6, constant=0, linear=0, edges=[(1, 3)]), dict(width=6, constant=0, linear=16, edges=[(0, 1), (0, 2), (0, 4), (1, 4), (1, 5), (2, 4), (2, 5), (4, 5)])], decoder=dict(width=8, constant=0, linear=186, edges=[(0, 2), (0, 3), (0, 4), (0, 5), (0, 7), (1, 2), (1, 4), (1, 6), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 4), (3, 5), (3, 6), (4, 5), (4, 7), (5, 7), (6, 7)]), ands=4)}
    _c10_patch_hret_sat_s15k7a_EXTRA = _c10_patch_hret_sat_s15k7a_Path('' + str(_c10_patch_hret_sat_s15k7a_INTEGRATED_ROOT) + '/agents/divider/build_base/extra_formulas.json')
    if _exists(_c10_patch_hret_sat_s15k7a_EXTRA):
        _c10_patch_hret_sat_s15k7a_json = _import_component('json', 'patches/patch_hret_sat_s15k7a.py', True)
        for _c10_patch_hret_sat_s15k7a_k, _c10_patch_hret_sat_s15k7a_f in _json_loads(_read_text(_c10_patch_hret_sat_s15k7a_EXTRA)).items():
            _c10_patch_hret_sat_s15k7a_FORMULAS[int(_c10_patch_hret_sat_s15k7a_k)] = dict(parents=[tuple(p) for p in _c10_patch_hret_sat_s15k7a_f['parents']], helpers=_c10_patch_hret_sat_s15k7a_f['helpers'], decoder=_c10_patch_hret_sat_s15k7a_f['decoder'], ands=_c10_patch_hret_sat_s15k7a_f['ands'], nested=_c10_patch_hret_sat_s15k7a_f.get('nested', False))
    _c10_patch_hret_sat_s15k7a_RETIRE = tuple((int(x) for x in _c10_patch_hret_sat_s15k7a_os.environ.get('DIVIDER_RETIRE', '13,14').split(',')))
    if _c10_patch_hret_sat_s15k7a_os.environ.get('DIVIDER_PLACEHOLDER'):
        for _c10_patch_hret_sat_s15k7a__k in _c10_patch_hret_sat_s15k7a_RETIRE:
            _c10_patch_hret_sat_s15k7a_FORMULAS.setdefault(_c10_patch_hret_sat_s15k7a__k, dict(parents=[('v', 0)], helpers=[], decoder=dict(width=1, constant=0, linear=1, edges=[]), ands=0))
    _c10_patch_hret_sat_s15k7a_FORCE = int(_c10_patch_hret_sat_s15k7a_os.environ.get('DIVIDER_FORCE_CAP', '0'))
    _c10_patch_hret_sat_s15k7a__json = _import_component('json', 'patches/patch_hret_sat_s15k7a.py', False)
    _c10_patch_hret_sat_s15k7a__SAT = {}
    pass
    _c10_patch_hret_sat_s15k7a__SAT[15] = _json_loads(_read_text(_c10_patch_hret_sat_s15k7a_Path('' + str(_c10_patch_hret_sat_s15k7a_INTEGRATED_ROOT) + '/agents/composer/p/hret_s15k7a_s15.json')))
    assert _c10_patch_hret_sat_s15k7a__SAT[15]['status'] == 'SAT'
    _c10_patch_hret_sat_s15k7a__ROLES = dict((x.split('=') for x in 'q16=v6,q17=v7,q18=v8,q19=v9,q20=v10,q42=v11,q30=next'.split(',')))
    _c10_patch_hret_sat_s15k7a__ROLES.update({'v%d' % i: 'v%d' % i for i in range(12)})
    _c10_patch_hret_sat_s15k7a__ROLES.update({'s%d' % (k + 1): 'next' for k in _c10_patch_hret_sat_s15k7a__SAT})
    if _c10_patch_hret_sat_s15k7a__SAT:
        _c10_patch_hret_sat_s15k7a_RETIRE = tuple(sorted(set(_c10_patch_hret_sat_s15k7a_RETIRE) | set(_c10_patch_hret_sat_s15k7a__SAT)))

    def _c10_patch_hret_sat_s15k7a__pair_forms(b, SA, SB):
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

    def _c10_patch_hret_sat_s15k7a__undo(b, ops):
        for c, t in reversed(ops):
            b.cx(c, t)

    def _c10_patch_hret_sat_s15k7a__emit_sat(b, form, wires, target):
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
            wa, wb, ops = _c10_patch_hret_sat_s15k7a__pair_forms(b, lw, rw)
            b.ccx(wa, wb, h)
            _c10_patch_hret_sat_s15k7a__undo(b, ops)
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
            wa, wb, ops = _c10_patch_hret_sat_s15k7a__pair_forms(b, lw, rw)
            b.push_condition(m)
            b.cz(wa, wb)
            b.pop_condition()
            _c10_patch_hret_sat_s15k7a__undo(b, ops)
            b.free(m)

    def _c10_patch_hret_sat_s15k7a_restore_sat(d, b, token, k, outcome):
        form = _c10_patch_hret_sat_s15k7a__SAT[k]
        v = token.v
        wires = []
        for name in form['inputs']:
            role = _c10_patch_hret_sat_s15k7a__ROLES[name]
            wires.append(token.u[-1] if role == 'next' else v[int(role[1:])])
        s = b.alloc_qubits(1)[0]
        _c10_patch_hret_sat_s15k7a__emit_sat(b, form, wires, s)
        b.push_condition(outcome)
        b.z(s)
        b.pop_condition()
        b.free(outcome)
        token.history[k] = s
        initial = list(token.initial_u)
        initial[25 - k] = s
        token.initial_u = tuple(initial)
        return s

    def _c10_patch_hret_sat_s15k7a__kernel(b):
        if b.max_qubits >= 48:
            return _c10_patch_hret_sat_s15k7a_sys.modules['top12_kernel']
        name = 'divider_top12_kernel_relaxed'
        if name not in _c10_patch_hret_sat_s15k7a_sys.modules:
            spec = _spec(name, _c10_patch_hret_sat_s15k7a__RELAXED)
            module = _new_module(spec)
            _c10_patch_hret_sat_s15k7a_sys.modules[name] = module
            spec.loader.exec_module(module)
        return _c10_patch_hret_sat_s15k7a_sys.modules[name]

    def _c10_patch_hret_sat_s15k7a__plan(d, p):
        return d.cb.factor_polynomial(p['width'], bool(p['constant']), p['linear'], set(map(tuple, p['edges'])))

    def _c10_patch_hret_sat_s15k7a_restore(d, b, token, k, outcome):
        f = _c10_patch_hret_sat_s15k7a_FORMULAS[k]
        v = token.v
        base = [v[x[1]] if x[0] == 'v' else token.u[-1] for x in f['parents']]
        helpers, hplans, hvars = ([], [], [])
        for h in f['helpers']:
            variables = base + helpers[:h['width'] - len(base)]
            p = _c10_patch_hret_sat_s15k7a__plan(d, h)
            g = b.alloc_qubits(1)[0]
            d.cb.emit_xor(b, variables, g, p)
            helpers.append(g)
            hplans.append(p)
            hvars.append(variables)
        dplan = _c10_patch_hret_sat_s15k7a__plan(d, f['decoder'])
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

    def _c10_patch_hret_sat_s15k7a__feed_row(d, b, token, j):
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

    def _c10_patch_hret_sat_s15k7a_cleanup_divider(d, b, token):
        original_cap = b.max_qubits
        if _c10_patch_hret_sat_s15k7a_FORCE:
            b.set_max_qubits(_c10_patch_hret_sat_s15k7a_FORCE)
        try:
            return _c10_patch_hret_sat_s15k7a__cleanup(d, b, token)
        finally:
            if _c10_patch_hret_sat_s15k7a_FORCE:
                b.set_max_qubits(original_cap)

    def _c10_patch_hret_sat_s15k7a__cleanup(d, b, token):
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
        for k in _c10_patch_hret_sat_s15k7a_RETIRE:
            w = token.history.pop(k)
            o = b.alloc_bits(1)[0]
            b.hmr(w, o)
            b.free(w)
            outcomes[k] = o
        data = 42 - len(_c10_patch_hret_sat_s15k7a_RETIRE)
        assert b.num_allocated_qubits == data
        for j, k, debt in reversed(token.rows):
            if j in outcomes:
                if j in _c10_patch_hret_sat_s15k7a__SAT:
                    _c10_patch_hret_sat_s15k7a_restore_sat(d, b, token, j, outcomes.pop(j))
                else:
                    _c10_patch_hret_sat_s15k7a_restore(d, b, token, j, outcomes.pop(j))
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
                    result = _c10_patch_hret_sat_s15k7a__kernel(b).last_feed_and_initial(d, b, token, debt)
                else:
                    token._debt = debt
                    _c10_patch_hret_sat_s15k7a__feed_row(d, b, token, 12)
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
                _c10_patch_hret_sat_s15k7a__feed_row(d, b, token, j)
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

    def _c10_patch_hret_sat_s15k7a_apply(ctx):
        divider = ctx.old.divider

        def bound(b, token):
            return _c10_patch_hret_sat_s15k7a_cleanup_divider(divider, b, token)
        divider.cleanup_divider = bound

# patches/patch_ld_first20_56b8.py
def _initialize__c11_patch_ld_first20_56b8():
    global _c11_patch_ld_first20_56b8_DEFAULT, _c11_patch_ld_first20_56b8_DEFAULT_SHA, _c11_patch_ld_first20_56b8_INTEGRATED_ROOT, _c11_patch_ld_first20_56b8_MODEL_SHA, _c11_patch_ld_first20_56b8_Path, _c11_patch_ld_first20_56b8_REPORT, _c11_patch_ld_first20_56b8__IntegratedPath, _c11_patch_ld_first20_56b8___file__, _c11_patch_ld_first20_56b8___name__, _c11_patch_ld_first20_56b8__certificate, _c11_patch_ld_first20_56b8_apply, _c11_patch_ld_first20_56b8_hashlib, _c11_patch_ld_first20_56b8_json, _c11_patch_ld_first20_56b8_os
    "Agent loader2 copy of agents/loader/patch_ld_first21.py at WORK CAP 20 (raw address, all 7 slots fixed): 26 other owners\n+ 20 = 46, so a Q46 body does not need the h0 pack for the first-loader peak. Certificate\nagents/loader2/certs/first_cap20_58_tailc_330000.json (58 Toffolis; tail re-synthesis of sweep s11 seed330000 (60) at\noutputs 13-14; replay_loader_v2.py PASS, 42 HMR debts, work peak 20). Only the certificate and the cap assert differ.\n\nServes both lines (Q48: 26 other owners; Q47: 25 once h0 is packed by patch_w47_body.py; the loader itself is the\nsame). The certificate (mode first_raw, schema of the frozen loader16_first61_Q48.json, independent replay\nreplay_loader_v2.py PASS) is emitted with a line-for-line copy of candidate07 tables07.load_joint16 for variant\n'first' (every discarded truth -> shared TableDebts.erase; the universal table cleanup repays it). Replaces ONLY\nvariant='first' of tables.load_joint16: put it AFTER patch_donor_loaders.py / patch_donor_first60.py.\nEnv LD_FIRST_JSON overrides the certificate path (its sha is recorded in REPORT, not pinned).\n"
    _c11_patch_ld_first20_56b8__IntegratedPath = _import_component('pathlib', 'patches/patch_ld_first20_56b8.py', False).Path
    _c11_patch_ld_first20_56b8_INTEGRATED_ROOT = _c11_patch_ld_first20_56b8__IntegratedPath(_c11_patch_ld_first20_56b8___file__).resolve().parents[1]
    _c11_patch_ld_first20_56b8_hashlib = _import_component('hashlib', 'patches/patch_ld_first20_56b8.py', True)
    _c11_patch_ld_first20_56b8_json = _import_component('json', 'patches/patch_ld_first20_56b8.py', True)
    _c11_patch_ld_first20_56b8_os = _import_component('os', 'patches/patch_ld_first20_56b8.py', True)
    _c11_patch_ld_first20_56b8_Path = _import_component('pathlib', 'patches/patch_ld_first20_56b8.py', False).Path
    _c11_patch_ld_first20_56b8_DEFAULT = _c11_patch_ld_first20_56b8_Path('' + str(_c11_patch_ld_first20_56b8_INTEGRATED_ROOT) + '/agents/loader2/certs/first_cap20_56b8.json')
    _c11_patch_ld_first20_56b8_DEFAULT_SHA = 'f09657772c5fdba988c5dae5e599c003e635cc000d4aa53093362d0846332ec9'
    _c11_patch_ld_first20_56b8_MODEL_SHA = '24fff823faa911afe93d02afc3ded0bbd156a210a85f1265c989a087f8fd1219'
    _c11_patch_ld_first20_56b8_REPORT = {}

    def _c11_patch_ld_first20_56b8__certificate():
        path = _c11_patch_ld_first20_56b8_Path(_c11_patch_ld_first20_56b8_os.environ.get('LD_FIRST_JSON', str(_c11_patch_ld_first20_56b8_DEFAULT)))
        raw = _read_bytes(path)
        sha = _c11_patch_ld_first20_56b8_hashlib.sha256(raw).hexdigest()
        if path == _c11_patch_ld_first20_56b8_DEFAULT and _c11_patch_ld_first20_56b8_DEFAULT_SHA:
            pass
        data = _json_loads(raw)
        assert data['status'] == 'COMPLETE_MATHEMATICAL_LOADER_NOT_NATIVE'
        pass
        assert data['fixed_address_slots'] == list(range(7)) and data['reusable_input_slots'] == []
        assert data['work_cap'] == data['work_peak'] == 20
        hmr = sum((len(st['discarded_truths']) for st in data['steps'] if st['kind'] == 'Clifford_frame_then_HMR'))
        _c11_patch_ld_first20_56b8_REPORT.update(path=str(path), sha256=sha, Toffolis=data['Toffolis'], HMR_debts=hmr)
        return (data, hmr)

    def _c11_patch_ld_first20_56b8_apply(ctx):
        tables = ctx.tables
        original = tables.load_joint16
        km, cb = (tables.km, tables.cb)
        data, hmr_expected = _c11_patch_ld_first20_56b8__certificate()

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
            _c11_patch_ld_first20_56b8_REPORT['emitted'] = dict(Toffolis=count, HMR=hmr_expected)
            return (list(work[:13]), list(work[13:]))
        tables.load_joint16 = load_joint16

# patches/patch_proddisp.py
def _initialize__c12_patch_proddisp():
    global _c12_patch_proddisp_INTEGRATED_ROOT, _c12_patch_proddisp__IntegratedPath, _c12_patch_proddisp___file__, _c12_patch_proddisp___name__, _c12_patch_proddisp_apply, _c12_patch_proddisp_make
    "prodcoef patch PRODDISP: product forward with early release of the owned\nrounding carry of rows 0-7 (Pro 1's research/q47_forward_disposable/forward_source.py\nproduct_forward_disposable, copied with baseline bound; adder kernel shared\nwith patch_coefdisp.py in spirit).  Zero Toffolis; product forward peaks at 47.\nDebt positions/widths identical to the original. Replaces baseline.product_forward only.\n"
    _c12_patch_proddisp__IntegratedPath = _import_component('pathlib', 'patches/patch_proddisp.py', False).Path
    _c12_patch_proddisp_INTEGRATED_ROOT = _c12_patch_proddisp__IntegratedPath(_c12_patch_proddisp___file__).resolve().parents[1]

    def _c12_patch_proddisp_make(baseline):
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

    def _c12_patch_proddisp_apply(ctx):
        ctx.baseline.product_forward = _c12_patch_proddisp_make(ctx.baseline)

# patches/patch_q47_decoder_resynth2.py
def _initialize__c13_patch_q47_decoder_resynth2():
    global _c13_patch_q47_decoder_resynth2_DATA, _c13_patch_q47_decoder_resynth2_HERE, _c13_patch_q47_decoder_resynth2_INTEGRATED_ROOT, _c13_patch_q47_decoder_resynth2_Path, _c13_patch_q47_decoder_resynth2_REPORT, _c13_patch_q47_decoder_resynth2_T2_SHA_PREFIX, _c13_patch_q47_decoder_resynth2__IntegratedPath, _c13_patch_q47_decoder_resynth2___file__, _c13_patch_q47_decoder_resynth2___name__, _c13_patch_q47_decoder_resynth2__bits, _c13_patch_q47_decoder_resynth2__emit, _c13_patch_q47_decoder_resynth2__erase_cap, _c13_patch_q47_decoder_resynth2_apply, _c13_patch_q47_decoder_resynth2_copy, _c13_patch_q47_decoder_resynth2_hashlib, _c13_patch_q47_decoder_resynth2_json, _c13_patch_q47_decoder_resynth2_rewrite, _c13_patch_q47_decoder_resynth2_sys
    "Two donor-tail decoder outputs re-synthesised 5 -> 4 ANDs each (T2 replay plan rewrite, -2 Toffolis).\n\nData file q47_t2_rewrite.json (made by scripts/derive_q47_t2.py on runs/q47c5/build/q47c5raw.kmx, where T2 sits\n377 ops before the donor text; wire names translated to the donor's by full-domain value matching):\n  * donor q38: 5 CCX -> 4-AND plan over the live address-function wires at its first reader (op 26954);\n  * donor q36: 5 CCX -> 4-AND plan over the live address-function wires at op 26739 plus ONE captured product:\n    the product of the donor CCX at op 26527 (q44*q27, framed values) is copied into a new owner 'qcap' by a CX pair\n    around that CCX (d19-style snapshot), used as the extra variable, then erased right after q36's plan by\n    X + HMR with a Clifford fix-up (it is a quadratic function of the live address wires; the X removes the constant\n    term so no classical-bit Z is needed).\nOnly entries that target q36 / q38 inside their accumulation segments are deleted (they change no other wire).\nT2's ccx becomes 18. No-op unless the width w47 body module is loaded with TAIL == 'donor'.\n"
    _c13_patch_q47_decoder_resynth2__IntegratedPath = _import_component('pathlib', 'patches/patch_q47_decoder_resynth2.py', False).Path
    _c13_patch_q47_decoder_resynth2_INTEGRATED_ROOT = _c13_patch_q47_decoder_resynth2__IntegratedPath(_c13_patch_q47_decoder_resynth2___file__).resolve().parents[1]
    _c13_patch_q47_decoder_resynth2_copy = _import_component('copy', 'patches/patch_q47_decoder_resynth2.py', True)
    _c13_patch_q47_decoder_resynth2_hashlib = _import_component('hashlib', 'patches/patch_q47_decoder_resynth2.py', True)
    _c13_patch_q47_decoder_resynth2_json = _import_component('json', 'patches/patch_q47_decoder_resynth2.py', True)
    _c13_patch_q47_decoder_resynth2_sys = _import_component('sys', 'patches/patch_q47_decoder_resynth2.py', True)
    _c13_patch_q47_decoder_resynth2_Path = _import_component('pathlib', 'patches/patch_q47_decoder_resynth2.py', False).Path
    _c13_patch_q47_decoder_resynth2_HERE = _c13_patch_q47_decoder_resynth2_Path('' + str(_c13_patch_q47_decoder_resynth2_INTEGRATED_ROOT) + '/agents/normroot')
    _c13_patch_q47_decoder_resynth2_T2_SHA_PREFIX = '9a4cd975a1062505'
    _c13_patch_q47_decoder_resynth2_DATA = _c13_patch_q47_decoder_resynth2_HERE / 'q47_t2_rewrite.json'
    _c13_patch_q47_decoder_resynth2_REPORT = {}

    def _c13_patch_q47_decoder_resynth2__bits(v):
        out, i = ([], 0)
        while v:
            if v & 1:
                out.append(i)
            v >>= 1
            i += 1
        return out

    def _c13_patch_q47_decoder_resynth2__emit(plan, variables, target):
        ent = []
        if plan['constant']:
            ent.append(['X', [target], [], None])
        for b in _c13_patch_q47_decoder_resynth2__bits(plan['product_linear']):
            ent.append(['CX', [variables[b], target], [], None])
        for left, right, i, j in plan['products']:
            frame = [(variables[k], variables[i]) for k in _c13_patch_q47_decoder_resynth2__bits(left) if k != i]
            frame += [(variables[k], variables[j]) for k in _c13_patch_q47_decoder_resynth2__bits(right) if k != j]
            ent += [['CX', [a, b], [], None] for a, b in frame]
            ent.append(['CCX', [variables[i], variables[j], target], [], None])
            ent += [['CX', [a, b], [], None] for a, b in reversed(frame)]
        return ent

    def _c13_patch_q47_decoder_resynth2__erase_cap(fix):
        v = fix['variables']
        ent = []
        if fix['constant']:
            ent.append(['X', ['qcap'], [], None])
        ent.append(['HMR', ['qcap'], ['bcap_normroot'], None])
        for b in _c13_patch_q47_decoder_resynth2__bits(fix['linear']):
            ent.append(['Z', [v[b]], [], 'bcap_normroot'])
        for i, j in fix['edges']:
            ent.append(['CZ', [v[i], v[j]], [], 'bcap_normroot'])
        ent.append(['ZERO', 'qcap'])
        return ent

    def _c13_patch_q47_decoder_resynth2_rewrite(T2, d):
        lo = T2['lo']
        cap_op, (ca, cb, ct) = (d['capture']['donor_op'], d['capture']['ccx'])
        segs = {d['q21']['donor_target']: d['q21'], d['q13']['donor_target']: d['q13']}
        dele = {}
        for tgt, s in segs.items():
            for k in s['segment_donor_ops']:
                dele[k] = tgt
        insert = {d['q21']['reader_donor_op']: _c13_patch_q47_decoder_resynth2__emit(d['q21']['plan'], d['q21']['variables'], d['q21']['donor_target']) + _c13_patch_q47_decoder_resynth2__erase_cap(d['cap_fix']), d['q13']['reader_donor_op']: _c13_patch_q47_decoder_resynth2__emit(d['q13']['plan'], d['q13']['variables'], d['q13']['donor_target'])}
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

    def _c13_patch_q47_decoder_resynth2_apply(ctx):
        body = _c13_patch_q47_decoder_resynth2_sys.modules.get('variant_patch_patch_w47_body')
        if body is None or getattr(body, 'TAIL', None) != 'donor':
            _c13_patch_q47_decoder_resynth2_REPORT['status'] = 'inactive'
            return
        plan_path = _c13_patch_q47_decoder_resynth2_Path('' + str(_c13_patch_q47_decoder_resynth2_INTEGRATED_ROOT) + '/agents/width/plans/T2_decoder_capture.json')
        pass
        tail = body._tail_modules()
        assert tail['T2']['ccx'] == 20 and tail['T2']['lo'] == 26385
        tail['T2'] = _c13_patch_q47_decoder_resynth2_rewrite(_c13_patch_q47_decoder_resynth2_copy.deepcopy(tail['T2']), _json_loads(_read_text(_c13_patch_q47_decoder_resynth2_DATA)))
        _c13_patch_q47_decoder_resynth2_REPORT['status'] = 'T2 decoder 20 -> 18 CCX'

# patches/patch_second46_c19_70nb1.py
def _initialize__c14_patch_second46_c19_70nb1():
    global _c14_patch_second46_c19_70nb1_CERT, _c14_patch_second46_c19_70nb1_CERT_SHA256, _c14_patch_second46_c19_70nb1_HERE, _c14_patch_second46_c19_70nb1_INTEGRATED_ROOT, _c14_patch_second46_c19_70nb1_LOADERS, _c14_patch_second46_c19_70nb1_Path, _c14_patch_second46_c19_70nb1_REPORT, _c14_patch_second46_c19_70nb1__IntegratedPath, _c14_patch_second46_c19_70nb1___file__, _c14_patch_second46_c19_70nb1___name__, _c14_patch_second46_c19_70nb1_apply, _c14_patch_second46_c19_70nb1_hashlib, _c14_patch_second46_c19_70nb1_importlib, _c14_patch_second46_c19_70nb1_os, _c14_patch_second46_c19_70nb1_sys
    "LOADER2 pinned copy (made like agents/composer/mkpin.py) of agents/tk_q46/p/patch_second_q46.py: SECOND table load from the work-cap-19 second_framed\ncertificate tk46_second_framed_c19_b9_seed510016.json (SHA-256 3b4621d63f719928b38a3f2838de2c8d718aa6bbcdbc5a70eec706b2365e5c51), emitted by q46_loaders.py (cap-aware copy of the lead's q47_loaders_lead.py).\nThe certificate path is forced (environment ignored) and hash-checked. Replaces only tables07.load_joint16 for\nvariant='second'.\n"
    _c14_patch_second46_c19_70nb1__IntegratedPath = _import_component('pathlib', 'patches/patch_second46_c19_70nb1.py', False).Path
    _c14_patch_second46_c19_70nb1_INTEGRATED_ROOT = _c14_patch_second46_c19_70nb1__IntegratedPath(_c14_patch_second46_c19_70nb1___file__).resolve().parents[1]
    _c14_patch_second46_c19_70nb1_Path = _import_component('pathlib', 'patches/patch_second46_c19_70nb1.py', False).Path
    _c14_patch_second46_c19_70nb1_hashlib = _import_component('hashlib', 'patches/patch_second46_c19_70nb1.py', True)
    _c14_patch_second46_c19_70nb1_importlib = _import_component('importlib.util', 'patches/patch_second46_c19_70nb1.py', True)
    _c14_patch_second46_c19_70nb1_os = _import_component('os', 'patches/patch_second46_c19_70nb1.py', True)
    _c14_patch_second46_c19_70nb1_sys = _import_component('sys', 'patches/patch_second46_c19_70nb1.py', True)
    _c14_patch_second46_c19_70nb1_HERE = _c14_patch_second46_c19_70nb1_Path(_c14_patch_second46_c19_70nb1___file__).resolve().parent
    _c14_patch_second46_c19_70nb1_LOADERS = _c14_patch_second46_c19_70nb1_HERE / 'q46_loaders.py'
    if not _exists(_c14_patch_second46_c19_70nb1_LOADERS):
        _c14_patch_second46_c19_70nb1_LOADERS = _c14_patch_second46_c19_70nb1_Path('' + str(_c14_patch_second46_c19_70nb1_INTEGRATED_ROOT) + '/agents/tk_q46/p/q46_loaders.py')
    _c14_patch_second46_c19_70nb1_CERT = '' + str(_c14_patch_second46_c19_70nb1_INTEGRATED_ROOT) + '/agents/loader2/certs/second_cap19_70nb1.json'
    _c14_patch_second46_c19_70nb1_CERT_SHA256 = '3b4621d63f719928b38a3f2838de2c8d718aa6bbcdbc5a70eec706b2365e5c51'
    _c14_patch_second46_c19_70nb1_REPORT = {}

    def _c14_patch_second46_c19_70nb1_apply(ctx):
        pass
        _c14_patch_second46_c19_70nb1_os.environ['TK46_SECOND_JSON'] = _c14_patch_second46_c19_70nb1_CERT
        _c14_patch_second46_c19_70nb1_REPORT['certificate'] = _c14_patch_second46_c19_70nb1_CERT
        _c14_patch_second46_c19_70nb1_REPORT['certificate_sha256'] = _c14_patch_second46_c19_70nb1_CERT_SHA256
        name = 'tk46_q46_second_loader'
        assert name not in _c14_patch_second46_c19_70nb1_sys.modules
        spec = _spec(name, _c14_patch_second46_c19_70nb1_LOADERS)
        module = _new_module(spec)
        _c14_patch_second46_c19_70nb1_sys.modules[name] = module
        spec.loader.exec_module(module)
        assert _c14_patch_second46_c19_70nb1_Path(module.OWN_SECOND).resolve() == _c14_patch_second46_c19_70nb1_Path(_c14_patch_second46_c19_70nb1_CERT).resolve()
        tables = ctx.tables
        adapted = module.adapter(tables)
        original = tables.load_joint16

        def load_joint16(builder, address7, *, variant, debts):
            if variant == 'second':
                return adapted.load_joint16(builder, address7, variant='second', debts=debts)
            return original(builder, address7, variant=variant, debts=debts)
        tables.load_joint16 = load_joint16

# patches/patch_seedinv.py
def _initialize__c15_patch_seedinv():
    global _c15_patch_seedinv_INTEGRATED_ROOT, _c15_patch_seedinv_STATE, _c15_patch_seedinv__IntegratedPath, _c15_patch_seedinv___file__, _c15_patch_seedinv___name__, _c15_patch_seedinv_apply, _c15_patch_seedinv_make_seed_cleanup, _c15_patch_seedinv_product_inverse
    "prodcoef patch SEEDINV: retire raw v0, v1, v3 over the whole inverse product,\nthen recover them by running the three seed rows backwards.\n\nFacts used (exact, from the seed forward in the seed root frame):\n  seed row j (j=0,1,2) has sign s_j = NOT c_j with c = (v0', v1', v3') and its\n  sign copy is appended as seed[3+j] = s_j; rows j+1.. then add into seed[3+j].\nAfter the inverse product restores the seed, inverting seed row 2 (sign wire\nseed[5]) returns seed[4] = s1; inverting row 1 (sign seed[4]) returns\nseed[3] = s0; inverting row 0 (sign seed[3]) returns seed[0:3] = 111.  So the\nthree sign wires ARE NOT v0', NOT v1', NOT v3': one X each, then the unchanged\nseed-root inverse frame gives raw v0, v1, v3 on those wires, where their HMR\noutcomes are paid by Z.  The six seed carry debts are paid natively by the\nthree inverse rows.  No helper, no phase plan, no fresh wire.\n\nCost: inverse product runs with 41 data owners (vs 43), seed rows inverse 9,\nframe inverse 1.  Replaces lifecycle.product_inverse and baseline.seed_cleanup.\n"
    _c15_patch_seedinv__IntegratedPath = _import_component('pathlib', 'patches/patch_seedinv.py', False).Path
    _c15_patch_seedinv_INTEGRATED_ROOT = _c15_patch_seedinv__IntegratedPath(_c15_patch_seedinv___file__).resolve().parents[1]
    _c15_patch_seedinv_STATE = {}

    def _c15_patch_seedinv_product_inverse(builder, v, D, word, token, dirty, *, baseline):
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
        _c15_patch_seedinv_STATE['outcomes'] = outcomes
        return (word[:6], word[6:])

    def _c15_patch_seedinv_make_seed_cleanup(b):
        ar, km = (b.ar, b.km)

        def seed_cleanup(builder, v, D, seed, token):
            seed = list(seed)
            assert len(seed) == 6 and len(token.rows) == 3
            assert all((v[i] is None for i in (0, 1, 3)))
            outcomes = _c15_patch_seedinv_STATE.pop('outcomes')
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

    def _c15_patch_seedinv_apply(ctx):
        baseline = ctx.baseline
        lifecycle = ctx.components['lifecycle']

        def installed(builder, v, D, word, token, dirty):
            return _c15_patch_seedinv_product_inverse(builder, v, D, word, token, dirty, baseline=baseline)
        lifecycle.product_inverse = installed
        baseline.seed_cleanup = _c15_patch_seedinv_make_seed_cleanup(baseline)

# patches/patch_w47_body.py
def _initialize__c16_patch_w47_body():
    global _c16_patch_w47_body_A6_AROUND_PRODUCT, _c16_patch_w47_body_A6_EARLY, _c16_patch_w47_body_CTX, _c16_patch_w47_body_DONOR, _c16_patch_w47_body_INTEGRATED_ROOT, _c16_patch_w47_body_PACK, _c16_patch_w47_body_Path, _c16_patch_w47_body_SNAPSHOT2_TAIL, _c16_patch_w47_body_SNAP_PATH, _c16_patch_w47_body_STATE, _c16_patch_w47_body_TAIL, _c16_patch_w47_body_UNPACK_AFTER_SEED, _c16_patch_w47_body__IntegratedPath, _c16_patch_w47_body__TAIL, _c16_patch_w47_body___file__, _c16_patch_w47_body___name__, _c16_patch_w47_body__load_src, _c16_patch_w47_body__mark, _c16_patch_w47_body__pack, _c16_patch_w47_body__role_map, _c16_patch_w47_body__snapshot_module, _c16_patch_w47_body__tail_modules, _c16_patch_w47_body_apply, _c16_patch_w47_body_emit_body, _c16_patch_w47_body_importlib, _c16_patch_w47_body_sys, _c16_patch_w47_body_types, _c16_patch_w47_body_unpack_h0, _c16_patch_w47_body_unpack_h0_after_seed
    "MICRO47 COPY of agents/loader2/nopack46/patch_w47_body.py (no h0 pack, Q46): identical except A6_EARLY=True:\na6 = v[11] is X-measured right after prepare_H3_initial (its last reader before the divider) instead of after the seed,\nso it is absent through the first coefficient forward, metadata retirement, seed and product forward; the existing\n1-CCX current-D rebuild after the product forward (and the Z on the rebuilt owner that pays the HMR sign) is unchanged.\nThis gives coef1 its 46th-wire headroom at zero extra Toffolis. Copyright 2026 Syed Asad Ali, Apache-2.0; credits Opus and Astra.\n\nAGENT LOADER2 COPY (no h0 pack) of agents/tk_q46/p/patch_w47_body.py: identical except PACK=False (h0 is NOT packed\ninto the flags in the root forward and NOT unpacked after the seed), because the first loader now fits at work cap 20\n(agents/loader2/p/patch_ld_first20.py, 26 other owners + 20 = 46). Same file name on purpose (the decoder resynthesis\npatch looks the body module up by name). The same edit as agents/loader/nopack/patch_w47_body.py made for Q47.\nOriginal header: Agent width Q46 BODY (copy of patch_w47_body.py + a6 retired through the product forward, rebuilt from current D with 1 CCX).\n\nAgent width Q47 BODY: free h0 packing into the exponent flags + Pro 2 snapshot2 table-cleanup tail (one emit_body).\n\nTail: identical to patch_snapshot2.py (decoder06 + 14 capture CX, paid-R, joint20 cleanup 769/128).\nh0 packing (Pro 1 firstpack3, re-derived from its native text):\n\nMeasured from pro1_012 .../native_firstpack3/forward.kmx: it equals candidate10's root forward plus 11 ops\ninserted just before the root's final carry_clear:\n    h0' = h0 ^ 1 ^ v2 ^ v3 ^ v4 ^ c        (c = root conversion carry, still live there)\n    flags2 ^= h0', flags3 ^= h0'            (h0' = 1 only when flags2 = flags3 = 0, so code 12..15 marks h0'=1)\n    HMR h0'; CZ flags2 flags3 if outcome    (h0' == flags2 & flags3 after packing)\nUnpack (3 Toffolis, from native_firstpack3/unpacked.kmx), after the first metadata retirement (raw R frame):\n    h0 = (f2 f3) ^ 1 ^ v2 ^ v4 ^ (v0^v1)(v0^v2)(v0^v3^1);  flags2/3 restored.\nThis module supplies emit_body (a copy of candidate10 lifecycle10.emit_body that accepts an absent h0 and calls\nunpack_h0 after first_metadata_retired) and wraps components['root'].forward. All other callbacks are read from the\nlive lifecycle/baseline modules at call time, so other agents' function replacements still compose.\n"
    _c16_patch_w47_body__IntegratedPath = _import_component('pathlib', 'patches/patch_w47_body.py', False).Path
    _c16_patch_w47_body_INTEGRATED_ROOT = _c16_patch_w47_body__IntegratedPath(_c16_patch_w47_body___file__).resolve().parents[1]
    _c16_patch_w47_body_types = _import_component('types', 'patches/patch_w47_body.py', True)
    _c16_patch_w47_body_importlib = _import_component('importlib.util', 'patches/patch_w47_body.py', True)
    _c16_patch_w47_body_sys = _import_component('sys', 'patches/patch_w47_body.py', True)
    _c16_patch_w47_body_Path = _import_component('pathlib', 'patches/patch_w47_body.py', False).Path
    _c16_patch_w47_body_CTX = None
    _c16_patch_w47_body_STATE = dict(flags=None, packed=False)
    _c16_patch_w47_body_SNAPSHOT2_TAIL = True
    _c16_patch_w47_body_TAIL = 'donor'
    _c16_patch_w47_body_A6_AROUND_PRODUCT = True
    _c16_patch_w47_body_A6_EARLY = True
    _c16_patch_w47_body_PACK = False
    _c16_patch_w47_body_SNAP_PATH = _c16_patch_w47_body_Path('' + str(_c16_patch_w47_body_INTEGRATED_ROOT) + '/agents/width/src/decoder_snapshot_cleanup_q48.py')

    def _c16_patch_w47_body__snapshot_module():
        name = 'width_pro2_decoder_snapshot_cleanup_q48'
        if name not in _c16_patch_w47_body_sys.modules:
            spec = _spec(name, _c16_patch_w47_body_SNAP_PATH)
            module = _new_module(spec)
            _c16_patch_w47_body_sys.modules[name] = module
            spec.loader.exec_module(module)
        return _c16_patch_w47_body_sys.modules[name]

    def _c16_patch_w47_body__pack(builder, h0, Q, c, flags):
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

    def _c16_patch_w47_body_unpack_h0(builder, v, h, flags):
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
    _c16_patch_w47_body_UNPACK_AFTER_SEED = True

    def _c16_patch_w47_body_unpack_h0_after_seed(builder, v, h, flags, seed):
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

    def _c16_patch_w47_body_apply(ctx):
        global _c16_patch_w47_body_CTX
        _c16_patch_w47_body_CTX = ctx
        if not _c16_patch_w47_body_PACK:
            return
        norm_mod = ctx.components['normalization']
        root_mod = ctx.components['root']
        norm_forward = norm_mod.forward

        def normalization_forward(builder, original, flags):
            _c16_patch_w47_body_STATE['flags'] = list(flags)
            return norm_forward(builder, original, flags)
        new_norm = _c16_patch_w47_body_types.SimpleNamespace(**{k: getattr(norm_mod, k) for k in dir(norm_mod) if not k.startswith('__')})
        new_norm.forward = normalization_forward
        ctx.components['normalization'] = new_norm
        original_clear = root_mod.carry_clear
        original_forward = root_mod.forward

        def forward(builder, norm):
            norm = list(norm)
            h0 = norm[0]
            flags = _c16_patch_w47_body_STATE['flags']
            if flags is None:
                km = _c16_patch_w47_body_CTX.km
                flags = [km.q(22 + i) for i in range(4)]
                _c16_patch_w47_body_STATE['flags'] = flags
            assert len(flags) == 4

            def carry_clear(b, Q, p, c):
                if not _c16_patch_w47_body_STATE['packed']:
                    _c16_patch_w47_body_STATE['packed'] = True
                    _c16_patch_w47_body__pack(b, h0, Q, c, flags)
                return original_clear(b, Q, p, c)
            root_mod.carry_clear = carry_clear
            try:
                out = original_forward(builder, norm)
            finally:
                root_mod.carry_clear = original_clear
            assert _c16_patch_w47_body_STATE['packed']
            residual = list(out['residual'])
            assert residual[0] == h0
            residual[0] = None
            return dict(root=out['root'], residual=residual)
        new_root = _c16_patch_w47_body_types.SimpleNamespace(**{k: getattr(root_mod, k) for k in dir(root_mod) if not k.startswith('__')})
        new_root.forward = forward
        ctx.components['root'] = new_root
    _c16_patch_w47_body_DONOR = _c16_patch_w47_body_Path('' + str(_c16_patch_w47_body_INTEGRATED_ROOT) + '/work/pro1_013/narrow/arithmetic_round3/native/candidate11r2/candidate11r2.build.json')
    _c16_patch_w47_body__TAIL = {}

    def _c16_patch_w47_body__load_src(name, path):
        if name not in _c16_patch_w47_body_sys.modules:
            spec = _spec(name, path)
            module = _new_module(spec)
            _c16_patch_w47_body_sys.modules[name] = module
            spec.loader.exec_module(module)
        return _c16_patch_w47_body_sys.modules[name]

    def _c16_patch_w47_body__tail_modules():
        if not _c16_patch_w47_body__TAIL:
            json = _import_component('json', 'patches/patch_w47_body.py', True)
            W = _c16_patch_w47_body_Path('' + str(_c16_patch_w47_body_INTEGRATED_ROOT) + '/agents/width')
            _c16_patch_w47_body__TAIL['T1'] = _json_loads(_read_text(W / 'plans/T1_late_metadata.json'))
            _c16_patch_w47_body__TAIL['T2'] = _json_loads(_read_text(W / 'plans/T2_decoder_capture.json'))
            assert _c16_patch_w47_body__TAIL['T1']['ccx'] == 3 and _c16_patch_w47_body__TAIL['T2']['ccx'] == 20 and (_c16_patch_w47_body__TAIL['T1']['external_bits'] == ['b75'])
            cuts = {c['name']: c for c in _json_loads(_read_text(_c16_patch_w47_body_DONOR))['cuts']}
            _c16_patch_w47_body__TAIL['T2_exit'] = cuts['raw_root_restored_with_paid_phase_product']['owners']
            _c16_patch_w47_body__TAIL['replay'] = _c16_patch_w47_body__load_src('width_block_replay', W / 'src/block_replay.py').replay
            _c16_patch_w47_body__TAIL['paidR'] = _c16_patch_w47_body__load_src('width_pro2_paid_R_cleanup_q48', W / 'src/paid_R_cleanup_q48.py')
        return _c16_patch_w47_body__TAIL

    def _c16_patch_w47_body__role_map(plan, ours):
        m = {}
        for w, (role, i) in plan['entry_owner'].items():
            q = ours[role][i]
            assert q is not None, (w, role, i)
            m[w] = q
        return m

    def _c16_patch_w47_body__mark(builder, trace, label, owners=None):
        L = _c16_patch_w47_body_CTX.components['lifecycle']
        live = builder.num_allocated_qubits
        assert live <= builder.max_qubits, (label, live)
        if trace is not None:
            trace.append(dict(label=label, live_owners=live))
        if L.CUT_HOOK is not None:
            L.CUT_HOOK(label, builder, {} if owners is None else {key: list(value) for key, value in owners.items()})

    def _c16_patch_w47_body_emit_body(builder, v12, h10, flags4, table_module, divider_module, decode_root_callback, *, trace=None):
        """candidate10 lifecycle10.emit_body with packed h0 (absent until unpack_h0) and the snapshot2 tail."""
        L = _c16_patch_w47_body_CTX.components['lifecycle']
        baseline = L.baseline
        assert builder.max_qubits in (46, 47, 48)
        v = list(v12)
        h = list(h10)
        flags = list(flags4)
        assert (len(v), len(h), len(flags)) == (12, 10, 4)
        if _c16_patch_w47_body_PACK:
            assert h[0] is None and len(set(v + h[1:] + flags)) == 25
        else:
            assert h[0] is not None and len(set(v + h + flags)) == 26
        _c16_patch_w47_body__mark(builder, trace, 'body_entry', dict(v=v, h=h, flags=flags))
        table_debts = table_module.TableDebts()
        truths = table_module.model_truths()
        D, Hlow = table_module.load_joint16(builder, v[5:], variant='first', debts=table_debts)
        D = list(D)
        H = list(Hlow)
        _c16_patch_w47_body__mark(builder, trace, 'first_table', dict(v=v, h=h, flags=flags, D=D, H=H))
        H.append(baseline.prepare_H3_initial(builder, v, D, H))
        if _c16_patch_w47_body_A6_AROUND_PRODUCT and _c16_patch_w47_body_A6_EARLY:
            a6_outcome = builder.alloc_bits(1)[0]
            builder.hmr(v[11], a6_outcome)
            builder.free(v[11])
            v[11] = None
        baseline.root_R_frame(builder, v)
        H.append(baseline.prepare_H4(builder, D, H[3]))
        first = baseline.coefficient_forward(builder, v, D, H)
        _c16_patch_w47_body__mark(builder, trace, 'first_coefficient', dict(v=v, h=h, flags=flags, D=D, H=H, snapshot=[first.saved_bit]))
        Hlow = baseline.erase_high_H(builder, v, D, H)
        for i, q in enumerate(Hlow):
            table_debts.erase(builder, q, truths['H'][i], free=True)
        first_snapshot = baseline.ar.release_saved_bit(builder, first.saved_bit)
        first.saved_bit = None
        baseline.root_R_frame(builder, v, inverse=True)
        _c16_patch_w47_body__mark(builder, trace, 'first_metadata_retired')
        if _c16_patch_w47_body_PACK and (not _c16_patch_w47_body_UNPACK_AFTER_SEED):
            h = _c16_patch_w47_body_unpack_h0(builder, v, h, flags)
            _c16_patch_w47_body__mark(builder, trace, 'width_h0_unpacked', dict(v=v, h=h, flags=flags, D=D))
        seed, seed_token = baseline.seed_forward(builder, v, D)
        if _c16_patch_w47_body_PACK and _c16_patch_w47_body_UNPACK_AFTER_SEED:
            h = _c16_patch_w47_body_unpack_h0_after_seed(builder, v, h, flags, seed)
        _c16_patch_w47_body__mark(builder, trace, 'seed_ready', dict(v=v, h=h, flags=flags, D=D, seed=seed))
        if _c16_patch_w47_body_A6_AROUND_PRODUCT and (not _c16_patch_w47_body_A6_EARLY):
            a6_outcome = builder.alloc_bits(1)[0]
            builder.hmr(v[11], a6_outcome)
            builder.free(v[11])
            v[11] = None
        word, product_token = baseline.product_forward(builder, D, seed, h)
        if _c16_patch_w47_body_A6_AROUND_PRODUCT:
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
        _c16_patch_w47_body__mark(builder, trace, 'signed_product15', dict(v=v, P=P, flags=flags, D=D))
        first_D = []
        for q in D:
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            builder.free(q)
            first_D.append(m)
        _c16_patch_w47_body__mark(builder, trace, 'coefficient_retired_for_divider', dict(v=v, P=P, flags=flags))
        P = list(divider_module.compute_phase_cleanup(builder, v, P, flags))
        assert len(P) == 15 and len(set(v + P + flags)) == 31
        _c16_patch_w47_body__mark(builder, trace, 'divider_return', dict(v=v, P=P, flags=flags))
        baseline.root_R_frame(builder, v)
        D, Hlow = table_module.load_joint16(builder, v[5:], variant='second', debts=table_debts)
        D = list(D)
        H = list(Hlow)
        retired = {a: None for a in (0, 1, 2, 4)}
        for a in retired:
            v[5 + a] = None
        assert all((v[5 + a] is None for a in (0, 1, 2, 4)))
        assert v[8] is not None and v[10] is not None and (v[11] is not None)
        _c16_patch_w47_body__mark(builder, trace, 'second_table', dict(v=v, P=P, flags=flags, D=D, H=H))
        baseline.ar.repay_saved_bit(builder, D[6], first_snapshot)
        H.append(baseline.prepare_H3_initial(builder, v, D, H))
        _c16_patch_w47_body__mark(builder, trace, 'second_H3_ready', dict(v=v, P=P, flags=flags, D=D, H=H))
        q = v[11]
        m = builder.alloc_bits(1)[0]
        builder.hmr(q, m)
        builder.free(q)
        v[11] = None
        retired[6] = m
        assert set(retired) == {0, 1, 2, 4, 6} and all((retired[a] is None for a in (0, 1, 2, 4)))
        _c16_patch_w47_body__mark(builder, trace, 'second_a6_retired', dict(v=v, P=P, flags=flags, D=D, H=H))
        H.append(baseline.prepare_H4(builder, D, H[3]))
        second = baseline.coefficient_forward(builder, v, D, H)
        _c16_patch_w47_body__mark(builder, trace, 'second_coefficient', dict(v=v, P=P, flags=flags, D=D, H=H, snapshot=[second.saved_bit]))
        for q, m in zip(D, first_D):
            builder.push_condition(m)
            builder.z(q)
            builder.pop_condition()
            builder.free(m)
        baseline.merge_coefficient_transcripts(builder, first, second)
        Hlow = baseline.erase_high_H(builder, v, D, H)
        _c16_patch_w47_body__mark(builder, trace, 'second_metadata_retired')
        high = builder.alloc_qubits(1)[0]
        builder.cx(P[14], high)
        builder.x(high)
        word = P + [high]
        _c16_patch_w47_body__mark(builder, trace, 'inverse_product_data', dict(v=v, word=word, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
        dirty = [q for q in v if q is not None] + flags + Hlow + [second.saved_bit]
        seed, h = L.product_inverse(builder, v, D, word, product_token, dirty)
        baseline.seed_cleanup(builder, v, D, seed, seed_token)
        if _c16_patch_w47_body_TAIL == 'donor':
            _c16_patch_w47_body__mark(builder, trace, 'seed_cleared', dict(v=v, h=h, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
            tail = _c16_patch_w47_body__tail_modules()
            wm = _c16_patch_w47_body__role_map(tail['T1'], dict(v=v, h=h, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
            out = tail['replay'](builder, tail['T1'], wm, ext_bits={'b75': retired[6]})
            builder.free(retired[6])
            retired[6] = None
            v[11] = out['q26']
            H = list(Hlow) + [out['q9'], out['q43']]
            _c16_patch_w47_body__mark(builder, trace, 'coefficient_sources_restored')
            baseline.coefficient_inverse(builder, v, D, H, second, [q for q in v if q is not None] + flags + h)
            _c16_patch_w47_body__mark(builder, trace, 'A_restored', dict(v=v, h=h, flags=flags, A=D, H=H))
            wm = _c16_patch_w47_body__role_map(tail['T2'], dict(v=v, h=h, flags=flags, A=D, H=H))
            out = tail['replay'](builder, tail['T2'], wm)
            ex = tail['T2_exit']
            v = [out[w] for w in ex['v']]
            h = [out[w] for w in ex['h']]
            flags = [out[w] for w in ex['flags']]
            D = [out[w] for w in ex['A']]
            H = [out[w] for w in ex['H']]
            product = out[ex['phase_snapshot'][0]]
            assert all((q is not None for q in v)) and len(set(v + h + flags)) == 26
            _c16_patch_w47_body__mark(builder, trace, 'raw_root_restored_with_paid_R', dict(v=v, h=h, flags=flags, A=D, H=H, phase_snapshot=[product]))
            tail['paidR'].cleanup_joint18(builder, v[5:], D, H, product, table_debts, table_api=table_module)
        else:
            _c16_patch_w47_body__mark(builder, trace, 'seed_cleared', dict(v=v, h=h, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
            H = list(Hlow)
            H.append(baseline.prepare_H3_current(builder, v, D, H))
            H.append(baseline.prepare_H4(builder, D, H[3]))
            _c16_patch_w47_body__mark(builder, trace, 'coefficient_sources_restored')
            baseline.coefficient_inverse(builder, v, D, H, second, [q for q in v if q is not None] + flags + h)
            _c16_patch_w47_body__mark(builder, trace, 'A_restored', dict(v=v, h=h, flags=flags, A=D, H=H))
            if _c16_patch_w47_body_SNAPSHOT2_TAIL:
                snap = _c16_patch_w47_body__snapshot_module()
                v, snapshots = snap.decode_root_with_snapshots(builder, v, D, H, retired)
                v = list(v)
                assert all((q is not None for q in v)) and len(set(v + h + flags)) == 26
                product = snap.capture_R_before_inverse(builder, v[8])
                baseline.root_R_frame(builder, v, inverse=True)
                snap.finish_R_capture(builder, v[8], v[7], product)
                _c16_patch_w47_body__mark(builder, trace, 'raw_root_restored_with_paid_R', dict(v=v, h=h, flags=flags, A=D, H=H, snapshots=snapshots))
                snap.cleanup_joint20(builder, v[5:], D, H, snapshots, product, table_debts, table_api=table_module)
            else:
                v = list(decode_root_callback(builder, v, D, H, retired))
                assert all((q is not None for q in v)) and len(set(v + h + flags)) == 26
                baseline.root_R_frame(builder, v, inverse=True)
                _c16_patch_w47_body__mark(builder, trace, 'raw_root_restored', dict(v=v, h=h, flags=flags, A=D, H=H))
                Hlow = baseline.erase_high_H(builder, v, D, H, initial=True)
                table_module.cleanup_joint16(builder, v[5:], D, Hlow, table_debts)
        assert not table_debts.pending
        assert first.saved_bit is None and second.saved_bit is None
        for token in (first, second):
            assert all((debt.consumed and (not debt.measurements) for debt in token.row_debts))
            assert token.overflow_debt.consumed and (not token.overflow_debt.measurements)
        assert all((debt.consumed and (not debt.measurements) for debt in product_token.rows))
        _c16_patch_w47_body__mark(builder, trace, 'body_return', dict(v=v, h=h, flags=flags))
        return (v, h)

# patches/q46_loaders.py
def _initialize__c17_q46_loaders():
    global _c17_q46_loaders_HERE, _c17_q46_loaders_INTEGRATED_ROOT, _c17_q46_loaders_LAST_REPORT, _c17_q46_loaders_OWN_SECOND, _c17_q46_loaders_Path, _c17_q46_loaders_SPECS, _c17_q46_loaders_SimpleNamespace, _c17_q46_loaders__IntegratedPath, _c17_q46_loaders___file__, _c17_q46_loaders___name__, _c17_q46_loaders__own_spec, _c17_q46_loaders_adapter, _c17_q46_loaders_certificate, _c17_q46_loaders_hashlib, _c17_q46_loaders_json, _c17_q46_loaders_load, _c17_q46_loaders_lru_cache, _c17_q46_loaders_os
    'tk_q46 CAP-AWARE copy (work cap and complete peak read from the certificate: cap 19 -> peak 46) of the lead copy of agents/width/src/q47_loaders_own.py (itself a COPY by agent width of Pro 2 q47_loaders.py: the SECOND loader only, reading an own cap-20 search result\n(agents/width/loader_search, constructor v5_q47 run on this Mac) instead of second90_paper.json. load() unchanged.\n\nOriginal-interface first70/second90 coefficient loaders at strict Q47.\n\nAll consumed coordinates retain their exact original-raw128 phase truth in\nthe original TableDebts class. This module emits no output-test phase tags.\n'
    _c17_q46_loaders__IntegratedPath = _import_component('pathlib', 'patches/q46_loaders.py', False).Path
    _c17_q46_loaders_INTEGRATED_ROOT = _c17_q46_loaders__IntegratedPath(_c17_q46_loaders___file__).resolve().parents[1]
    _c17_q46_loaders_Path = _import_component('pathlib', 'patches/q46_loaders.py', False).Path
    _c17_q46_loaders_lru_cache = _import_component('functools', 'patches/q46_loaders.py', False).lru_cache
    _c17_q46_loaders_SimpleNamespace = _import_component('types', 'patches/q46_loaders.py', False).SimpleNamespace
    _c17_q46_loaders_hashlib = _import_component('hashlib', 'patches/q46_loaders.py', True)
    _c17_q46_loaders_json = _import_component('json', 'patches/q46_loaders.py', True)
    _c17_q46_loaders_HERE = _c17_q46_loaders_Path(_c17_q46_loaders___file__).resolve().parent
    _c17_q46_loaders_os = _import_component('os', 'patches/q46_loaders.py', True)
    _c17_q46_loaders_OWN_SECOND = _c17_q46_loaders_Path(_c17_q46_loaders_os.environ.get('TK46_SECOND_JSON') or _c17_q46_loaders_os.environ.get('LEAD_SECOND_JSON'))

    def _c17_q46_loaders__own_spec():
        data = _json_loads(_read_text(_c17_q46_loaders_OWN_SECOND))
        hmr = sum((len(st['discarded_truths']) for st in data['steps'] if st['kind'] == 'Clifford_frame_then_HMR'))
        return dict(path=_c17_q46_loaders_OWN_SECOND, sha=_c17_q46_loaders_hashlib.sha256(_read_bytes(_c17_q46_loaders_OWN_SECOND)).hexdigest(), mode='second_framed', Toffolis=data['Toffolis'], HMR_debts=hmr, work_cap=data['work_cap'], entry=31, returned=43, peak=27 + data['work_cap'], fixed=(3, 5, 6), reused=(0, 1, 2, 4), outside=27)
    _c17_q46_loaders_SPECS = {'second': _c17_q46_loaders__own_spec()}
    _c17_q46_loaders_LAST_REPORT = None

    @_c17_q46_loaders_lru_cache(maxsize=2)
    def _c17_q46_loaders_certificate(which):
        spec = _c17_q46_loaders_SPECS[which]
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

    def _c17_q46_loaders_load(builder, address7, which, debts, *, table_api):
        global _c17_q46_loaders_LAST_REPORT
        api = table_api
        common = api.common
        km = common.km
        cb = common.cb
        spec = _c17_q46_loaders_SPECS[which]
        data = _c17_q46_loaders_certificate(which)
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
        _c17_q46_loaders_LAST_REPORT = dict(loader=which, Toffolis=count, HMR_debts=debts.total_recorded - before, entry=spec['entry'], outside_mutable_owners=spec['outside'], work_cap=cap, existing_input_work=len(spec['reused']), fresh_zero_owners=cap - len(spec['reused']), fixed_address_slots=list(spec['fixed']), retired_address_slots=list(spec['reused']), returned=spec['returned'], peak=max(trace), owner_trace=trace, fixed_owners=list(map(str, fixed)), mutable_owners=list(map(str, all_mutable)), output_owners=list(map(str, work)), paper_sha256=spec['sha'], all_debts_in_original_raw128_order=True)
        return (list(work[:13]), list(work[13:]))

    def _c17_q46_loaders_adapter(original_tables07):

        def load_joint16(builder, address7, *, variant, debts):
            assert variant in _c17_q46_loaders_SPECS
            return _c17_q46_loaders_load(builder, address7, variant, debts, table_api=original_tables07)
        result = _c17_q46_loaders_SimpleNamespace(**{k: v for k, v in vars(original_tables07).items() if not k.startswith('__')})
        result.load_joint16 = load_joint16
        result._source_api = original_tables07
        result.RESOURCES = {k: dict(v) for k, v in original_tables07.RESOURCES.items()}
        for which, s in _c17_q46_loaders_SPECS.items():
            result.RESOURCES[which].update(Toffolis=s['Toffolis'], HMR_debts=s['HMR_debts'], other_fixed_owners=s['outside'], work_cap=s['work_cap'], existing_input_work=len(s['reused']), new_zero_owners=s['work_cap'] - len(s['reused']), complete_peak=s['peak'], return_owners=s['returned'])
        assert result.TableDebts is original_tables07.TableDebts
        return result

# tools/audit_affine.py
def _initialize__c18_audit_affine():
    global _c18_audit_affine_INTEGRATED_ROOT, _c18_audit_affine_Path, _c18_audit_affine__IntegratedPath, _c18_audit_affine___file__, _c18_audit_affine___name__, _c18_audit_affine_argparse, _c18_audit_affine_json, _c18_audit_affine_kmsim, _c18_audit_affine_main, _c18_audit_affine_np, _c18_audit_affine_stage_of, _c18_audit_affine_sys, _c18_audit_affine_time
    'Full-domain mechanical audit of a kickmix text circuit.\n\nFor every Toffoli-like gate, on ALL 3,133,452 official inputs (random HMR\noutcomes), test whether its AND product lies in the affine GF(2) span of the\n48 wire values just before the gate. If it does, the gate can be replaced by\nCX/X gates (product independent of the target) or by measurement-based\nuncomputation HMR + CZ (product = target xor affine), i.e. zero Toffolis.\nAlso records the live-wire profile (wires not identically zero) per operation.\n\nFindings are candidates only: acceptance needs the exact50 native proof.\n'
    _c18_audit_affine__IntegratedPath = _import_component('pathlib', 'tools/audit_affine.py', False).Path
    _c18_audit_affine_INTEGRATED_ROOT = _c18_audit_affine__IntegratedPath(_c18_audit_affine___file__).resolve().parents[1]
    _c18_audit_affine_argparse = _import_component('argparse', 'tools/audit_affine.py', True)
    _c18_audit_affine_json = _import_component('json', 'tools/audit_affine.py', True)
    _c18_audit_affine_sys = _import_component('sys', 'tools/audit_affine.py', True)
    _c18_audit_affine_time = _import_component('time', 'tools/audit_affine.py', True)
    _c18_audit_affine_Path = _import_component('pathlib', 'tools/audit_affine.py', False).Path
    _c18_audit_affine_np = _import_component('numpy', 'tools/audit_affine.py', False)
    _c18_audit_affine_sys.path.insert(0, str(_c18_audit_affine_Path(_c18_audit_affine___file__).resolve().parent))
    _c18_audit_affine_kmsim = _import_component('kmsim', 'tools/audit_affine.py', True)

    def _c18_audit_affine_stage_of(cuts, index):
        for cut in cuts:
            if index < cut['instruction_cut']:
                return cut['name']
        return 'final_layout'

    def _c18_audit_affine_main():
        ap = _c18_audit_affine_argparse.ArgumentParser()
        ap.add_argument('kmx', type=_c18_audit_affine_Path)
        ap.add_argument('--build', type=_c18_audit_affine_Path)
        ap.add_argument('--out', type=_c18_audit_affine_Path, required=True)
        ap.add_argument('--seed', type=int, default=0)
        args = ap.parse_args()
        began = _c18_audit_affine_time.monotonic()
        ops, registers = _c18_audit_affine_kmsim.parse(_read_text(args.kmx))
        xreg = registers['x']
        qwires = _c18_audit_affine_kmsim.quantum_wires(ops)
        cuts = _json_loads(_read_text(args.build))['cuts'] if args.build else []
        sim = _c18_audit_affine_kmsim.Sim(ops, xreg, seed=args.seed)
        sampler = _c18_audit_affine_kmsim.Sampler(sim)
        findings, gates = ([], [])
        nonzero = {w: bool(sim.get(w).any()) for w in qwires}
        live_profile = _c18_audit_affine_np.zeros(len(ops), dtype=_c18_audit_affine_np.int16)
        stats = dict(tested=0)

        def before(index, s):
            kind, a, condition, angle, line = ops[index]
            if kind not in _c18_audit_affine_kmsim.TOFFOLI_LIKE:
                return
            mask = s.active_mask(condition)
            active = 1.0 if mask is None else float(_c18_audit_affine_np.bitwise_count(mask).sum()) / s.n
            if kind == 'CCX':
                products = [('ab', s.get(a[0]) & s.get(a[1]))]
            elif kind == 'CSWAP':
                products = [('c(x^y)', s.get(a[0]) & (s.get(a[1]) ^ s.get(a[2])))]
            else:
                products = [('ab', s.get(a[0]) & s.get(a[1])), ('ac', s.get(a[0]) & s.get(a[2])), ('bc', s.get(a[1]) & s.get(a[2]))]
            record = dict(op=index, line=line, kind=kind, args=list(a), condition=condition, depth=len(s.stack) - 1, active=active, stage=_c18_audit_affine_stage_of(cuts, index))
            gates.append(record)
            if active == 0.0:
                record['never_active'] = True
                return
            for label, product in products:
                stats['tested'] += 1
                relation = _c18_audit_affine_kmsim.affine_relation(s, sampler, product, qwires, mask)
                if relation is not None:
                    wires, constant = relation
                    found = dict(record, product=label, relation_wires=wires, relation_constant=int(constant), product_identically_zero=not wires and (not constant))
                    findings.append(found)
                    print(_c18_audit_affine_json.dumps(found), flush=True)
                    break

        def after(index, s):
            kind, a, condition, angle, line = ops[index]
            for w in a:
                if w in nonzero:
                    nonzero[w] = bool(s.get(w).any())
            live_profile[index] = sum(nonzero.values())
        sim.run(before=before, after=after)
        final = {w: bool(sim.get(w).any()) for w in qwires}
        restored = _c18_audit_affine_np.array_equal(sim.value(xreg), sim.xs)
        scratch_zero = not any((final[w] for w in qwires if w not in xreg))
        peak = int(live_profile.max())
        peak_ops = _c18_audit_affine_np.flatnonzero(live_profile == peak)
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
        result = dict(status='AUDIT_CANDIDATES_ONLY_NOT_PROVED', kmx=str(args.kmx), inputs=sim.n, seed=args.seed, operations=len(ops), toffoli_like_static=sim.toffoli_static, toffoli_like_mean=sim.toffoli_executed / sim.n, input_restored=bool(restored), scratch_zero=bool(scratch_zero), products_tested=stats['tested'], findings=findings, expected_saving=sum((f['active'] for f in findings)), live_peak=peak, live_peak_runs=[dict(first=a, last=b, stage=_c18_audit_affine_stage_of(cuts, a)) for a, b in runs], sample_size=len(sampler.positions), seconds=_c18_audit_affine_time.monotonic() - began)
        args.out.write_text(_c18_audit_affine_json.dumps(result, indent=1) + '\n')
        _c18_audit_affine_np.save(args.out.with_suffix('.live.npy'), live_profile)
        args.out.with_suffix('.gates.json').write_text(_c18_audit_affine_json.dumps(gates) + '\n')
        print(_c18_audit_affine_json.dumps({k: v for k, v in result.items() if k not in ('findings', 'live_peak_runs')}, indent=1))
        print('peak runs:', len(runs), [(r['first'], r['last'], r['stage']) for r in result['live_peak_runs']][:40])
    if _c18_audit_affine___name__ == '__main__':
        _c18_audit_affine_main()

# tools/audit_pairs.py
def _initialize__c19_audit_pairs():
    global _c19_audit_pairs_INTEGRATED_ROOT, _c19_audit_pairs_Path, _c19_audit_pairs__IntegratedPath, _c19_audit_pairs___file__, _c19_audit_pairs___name__, _c19_audit_pairs_argparse, _c19_audit_pairs_json, _c19_audit_pairs_kmsim, _c19_audit_pairs_main, _c19_audit_pairs_np, _c19_audit_pairs_products_of, _c19_audit_pairs_reduce, _c19_audit_pairs_sys, _c19_audit_pairs_time
    'Recomputed-value scan: pairs of Toffoli-like gates (i earlier, j later) whose AND\nproducts differ only by an affine function of the wires live just before gate j:\n\n    p_j = p_i xor affine(wires at j)        on every official input.\n\nIf p_i were still held on a spare qubit at j, gate j would cost CX only. The scan\nreports each such pair, the live-wire maximum between the two gates (a spare qubit\nexists when it is below Q) and verifies the relation exactly on the full domain.\nCandidates only; a rewrite counts after the exact50 proof.\n'
    _c19_audit_pairs__IntegratedPath = _import_component('pathlib', 'tools/audit_pairs.py', False).Path
    _c19_audit_pairs_INTEGRATED_ROOT = _c19_audit_pairs__IntegratedPath(_c19_audit_pairs___file__).resolve().parents[1]
    _c19_audit_pairs_argparse = _import_component('argparse', 'tools/audit_pairs.py', True)
    _c19_audit_pairs_json = _import_component('json', 'tools/audit_pairs.py', True)
    _c19_audit_pairs_sys = _import_component('sys', 'tools/audit_pairs.py', True)
    _c19_audit_pairs_time = _import_component('time', 'tools/audit_pairs.py', True)
    _c19_audit_pairs_Path = _import_component('pathlib', 'tools/audit_pairs.py', False).Path
    _c19_audit_pairs_np = _import_component('numpy', 'tools/audit_pairs.py', False)
    _c19_audit_pairs_sys.path.insert(0, str(_c19_audit_pairs_Path(_c19_audit_pairs___file__).resolve().parent))
    _c19_audit_pairs_kmsim = _import_component('kmsim', 'tools/audit_pairs.py', True)

    def _c19_audit_pairs_reduce(basis, v):
        while v:
            hit = basis.get(v.bit_length() - 1)
            if hit is None:
                return v
            v ^= hit
        return 0

    def _c19_audit_pairs_products_of(s, kind, a):
        if kind == 'CCX':
            return s.get(a[0]) & s.get(a[1])
        if kind == 'CSWAP':
            return s.get(a[0]) & (s.get(a[1]) ^ s.get(a[2]))
        return None

    def _c19_audit_pairs_main():
        ap = _c19_audit_pairs_argparse.ArgumentParser()
        ap.add_argument('kmx', type=_c19_audit_pairs_Path)
        ap.add_argument('--out', type=_c19_audit_pairs_Path, required=True)
        ap.add_argument('--live', type=_c19_audit_pairs_Path, help='.live.npy from audit_affine')
        ap.add_argument('--build', type=_c19_audit_pairs_Path)
        args = ap.parse_args()
        began = _c19_audit_pairs_time.monotonic()
        ops, registers = _c19_audit_pairs_kmsim.parse(_read_text(args.kmx))
        xreg = registers['x']
        qw = _c19_audit_pairs_kmsim.quantum_wires(ops)
        live = _c19_audit_pairs_np.load(args.live) if args.live else None
        cuts = _json_loads(_read_text(args.build))['cuts'] if args.build else []

        def stage_of(i):
            for c in cuts:
                if i < c['instruction_cut']:
                    return c['name']
            return 'final_layout'
        sim = _c19_audit_pairs_kmsim.Sim(ops, xreg)
        sampler = _c19_audit_pairs_kmsim.Sampler(sim, count=4096)
        earlier = []
        hits = {}

        def before(index, s):
            kind, a, cond, angle, line = ops[index]
            if kind not in ('CCX', 'CSWAP') or len(s.stack) > 1 or cond is not None:
                return
            p = sampler.take(_c19_audit_pairs_products_of(s, kind, a))
            basis = {}
            for w in qw:
                v = _c19_audit_pairs_reduce(basis, sampler.take(s.get(w)))
                if v:
                    basis[v.bit_length() - 1] = v
            v = _c19_audit_pairs_reduce(basis, sampler.take(s.ones))
            if v:
                basis[v.bit_length() - 1] = v
            rj = _c19_audit_pairs_reduce(basis, p)
            if rj:
                for i, pi in earlier:
                    if _c19_audit_pairs_reduce(basis, pi ^ p) == 0:
                        hits.setdefault(index, []).append(i)
            earlier.append((index, p))
        sim.run(before=before)
        print('sampled pair hits:', sum((len(v) for v in hits.values())), 'gates with a hit:', len(hits), 'seconds %.1f' % (_c19_audit_pairs_time.monotonic() - began), flush=True)
        wanted = sorted({i for j, ii in hits.items() for i in ii[-3:]})
        stored = {}
        sim = _c19_audit_pairs_kmsim.Sim(ops, xreg)
        sampler2 = _c19_audit_pairs_kmsim.Sampler(sim, count=4096)
        rows = []

        def before2(index, s):
            kind, a, cond, angle, line = ops[index]
            if kind not in ('CCX', 'CSWAP'):
                return
            if index in hits:
                p = _c19_audit_pairs_products_of(s, kind, a)
                for i in reversed(hits[index][-3:]):
                    rel = _c19_audit_pairs_kmsim.affine_relation(s, sampler2, p ^ stored[i], qw)
                    if rel is not None:
                        span_max = int(live[i:index].max()) if live is not None else None
                        rows.append(dict(later_op=index, later_line=line, later=[kind] + list(a), earlier_op=i, earlier_line=ops[i][4], earlier=[ops[i][0]] + list(ops[i][1]), distance=index - i, max_live_between=span_max, stage=stage_of(index), relation_wires=rel[0], relation_constant=int(rel[1])))
                        break
            if index in wanted:
                stored[index] = _c19_audit_pairs_products_of(s, kind, a).copy()
        sim.run(before=before2)
        rows.sort(key=lambda r: (r['max_live_between'] if r['max_live_between'] is not None else 0, r['distance']))
        args.out.write_text(_c19_audit_pairs_json.dumps(dict(rows=rows, seconds=_c19_audit_pairs_time.monotonic() - began), indent=1) + '\n')
        print('exact recomputed pairs:', len(rows))
        by = {}
        for r in rows:
            key = (r['stage'], r['max_live_between'])
            by[key] = by.get(key, 0) + 1
        for k, n in sorted(by.items(), key=lambda kv: (kv[0][1] or 0, kv[0][0])):
            print(n, k)
        for r in rows[:40]:
            print(r['later_op'], r['later'], '<-', r['earlier_op'], r['earlier'], 'dist', r['distance'], 'maxlive', r['max_live_between'], r['stage'], r['relation_wires'], r['relation_constant'])
    if _c19_audit_pairs___name__ == '__main__':
        _c19_audit_pairs_main()

# tools/build_variant.py
def _initialize__c20_build_variant():
    global _c20_build_variant_CAND10, _c20_build_variant_Context, _c20_build_variant_FG, _c20_build_variant_HERE, _c20_build_variant_INTEGRATED_ROOT, _c20_build_variant_NARROW, _c20_build_variant_PatchSet, _c20_build_variant_Path, _c20_build_variant__IntegratedPath, _c20_build_variant___file__, _c20_build_variant___name__, _c20_build_variant_argparse, _c20_build_variant_build, _c20_build_variant_cost_model, _c20_build_variant_hashlib, _c20_build_variant_importlib, _c20_build_variant_json, _c20_build_variant_load_patch, _c20_build_variant_main, _c20_build_variant_sys, _c20_build_variant_time
    "Emit a candidate10-derived variant without editing any pinned source file.\n\nUsage (through tools/macrun.py on macOS):\n    macrun.py tools/build_variant.py --out DIR [--patch PATCH.py] [--postpass REWRITES.json] [--name NAME]\n\nThe build is candidate10's generate.build() step for step. A PATCH module may define\n    Q = 48                                   # declared peak width (builder.set_max_qubits)\n    def apply(ctx): ...                      # monkeypatch loaded modules before emission\nctx has: variant (candidate10 arithmetic_variant), old (candidate07 variant), components\n(dict: normalization, root, divider, product, coefficient, lifecycle), baseline\n(lifecycle06 baseline), tables, decoder, phase, common, km.\nA patch replaces attributes on those live module objects (e.g. components['root'] =\nmy_module, or ctx.baseline.seed_forward = my_function). Pinned files on disk stay\nbyte-identical, so every hash check in the frozen sources still runs and passes.\n\n--postpass applies kmx-level rewrite records (tools/postpass.py) to the emitted text.\n\nNothing here asserts an expected Toffoli count: the actual exact expectation of the\nemitted text is computed and reported. A variant counts only after tools/prove_any.py\n(unchanged exact50 checker and oracle, full domain, every HMR transcript) and the\nofficial verifier on salts default/1/2/3.\n"
    _c20_build_variant__IntegratedPath = _import_component('pathlib', 'tools/build_variant.py', False).Path
    _c20_build_variant_INTEGRATED_ROOT = _c20_build_variant__IntegratedPath(_c20_build_variant___file__).resolve().parents[1]
    _c20_build_variant_Path = _import_component('pathlib', 'tools/build_variant.py', False).Path
    _c20_build_variant_argparse = _import_component('argparse', 'tools/build_variant.py', True)
    _c20_build_variant_hashlib = _import_component('hashlib', 'tools/build_variant.py', True)
    _c20_build_variant_importlib = _import_component('importlib.util', 'tools/build_variant.py', True)
    _c20_build_variant_json = _import_component('json', 'tools/build_variant.py', True)
    _c20_build_variant_sys = _import_component('sys', 'tools/build_variant.py', True)
    _c20_build_variant_time = _import_component('time', 'tools/build_variant.py', True)
    _c20_build_variant_HERE = _c20_build_variant_Path(_c20_build_variant___file__).resolve().parent
    _c20_build_variant_FG = _c20_build_variant_HERE.parent
    _c20_build_variant_NARROW = _c20_build_variant_FG / 'work/c10/narrow'
    _c20_build_variant_CAND10 = _c20_build_variant_NARROW / 'arithmetic_round2/native/candidate10'
    _c20_build_variant_sys.path.insert(0, str(_c20_build_variant_CAND10))
    _c20_build_variant_sys.path.insert(0, str(_c20_build_variant_HERE))

    def _c20_build_variant_load_patch(path):
        if path is None:
            return None
        spec = _spec('variant_patch_' + _c20_build_variant_Path(path).stem, path)
        module = _new_module(spec)
        _c20_build_variant_sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    class _c20_build_variant_Context:
        pass

    class _c20_build_variant_PatchSet:
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

    def _c20_build_variant_build(patch=None, Q=None):
        variant = _import_component('arithmetic_variant', 'tools/build_variant.py', False)
        Program = _import_component('branch_prover', 'tools/build_variant.py', False).Program
        generated_text = _import_component('branch_prover', 'tools/build_variant.py', False).generated_text
        exact_expectation = _import_component('fourier_resource_expectation', 'tools/build_variant.py', False).exact_expectation
        gate = variant.accepted_gate()
        components = dict(variant.install())
        old = variant.old
        common = old.common
        base = old.load_baseline('generate')
        ctx = _c20_build_variant_Context()
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
        variant.verify_sources()
        return (ctx, circuit, text, cuts, owner_trace, layout)

    def _c20_build_variant_cost_model(resources, Q, margin_units64=124370688):
        math = _import_component('math', 'tools/build_variant.py', True)
        mean = resources['mean_numeric']
        rotations = mean['generic_rotations']
        eps = math.pi * margin_units64 / 2 ** 64 / rotations if rotations else None
        charge = rotations * (0.56 * math.log2(1 / eps) + 5.3) / 4 if rotations else 0.0
        per_shot = mean['toffoli_like'] + mean['T'] / 4 + charge
        return dict(Q=Q, toffoli_like=mean['toffoli_like'], T=mean['T'], generic_rotations=rotations, rotation_charge=charge, per_shot=per_shot, modelled_cost=Q * per_shot, label='modelled from exact gate expectation; margin assumed unchanged; not measured')

    def _c20_build_variant_main():
        ap = _c20_build_variant_argparse.ArgumentParser()
        ap.add_argument('--out', type=_c20_build_variant_Path, required=True)
        ap.add_argument('--patch', type=_c20_build_variant_Path, action='append', default=[])
        ap.add_argument('--postpass', type=_c20_build_variant_Path)
        ap.add_argument('--name', default='variant')
        ap.add_argument('--Q', type=int)
        args = ap.parse_args()
        began = _c20_build_variant_time.monotonic()
        patch = _c20_build_variant_PatchSet([_c20_build_variant_load_patch(path) for path in args.patch]) if args.patch else None
        ctx, circuit, text, cuts, owner_trace, layout = _c20_build_variant_build(patch, args.Q)
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
        model = _c20_build_variant_cost_model(resources, circuit.num_qubits)
        report = dict(status='EMITTED_VARIANT_NOT_YET_PROVED_OR_QUALIFIED', name=args.name, base='candidate10 generator, unmodified pinned sources', patch=[str(path) for path in args.patch], patch_sha256=[_c20_build_variant_hashlib.sha256(_read_bytes(path)).hexdigest() for path in args.patch], postpass=str(args.postpass) if args.postpass else None, postpass_report=postpass_report, Q=circuit.num_qubits, exact_native_expectation=resources, cost_model=model, cuts=cuts, owner_trace=owner_trace, final_Clifford_layout_swaps=layout, actual_HMR_variables=program.measurements, native_operations=len(program.operations), kmb_sha256=_c20_build_variant_hashlib.sha256(_read_bytes(kmb)).hexdigest(), native_text_sha256=_c20_build_variant_hashlib.sha256(text.encode()).hexdigest(), emission_seconds=_c20_build_variant_time.monotonic() - began, official_verifier=False, no_submission=True)
        kmb.with_suffix('.build.json').write_text(_c20_build_variant_json.dumps(report, indent=2) + '\n')
        print(_c20_build_variant_json.dumps(dict(name=args.name, kmb=str(kmb), kmb_sha256=report['kmb_sha256'], cost_model=model, static=resources['static'], HMR=program.measurements, seconds=report['emission_seconds']), indent=1), flush=True)
    if _c20_build_variant___name__ == '__main__':
        _c20_build_variant_main()

# tools/hold_pass.py
def _initialize__c21_hold_pass():
    global _c21_hold_pass_INTEGRATED_ROOT, _c21_hold_pass_Path, _c21_hold_pass__IntegratedPath, _c21_hold_pass___file__, _c21_hold_pass___name__, _c21_hold_pass_analyse, _c21_hold_pass_ap, _c21_hold_pass_apply_chains, _c21_hold_pass_argparse, _c21_hold_pass_args, _c21_hold_pass_bisect, _c21_hold_pass_chains, _c21_hold_pass_chains_from_pairs, _c21_hold_pass_json, _c21_hold_pass_kmsim, _c21_hold_pass_plan_chain, _c21_hold_pass_report, _c21_hold_pass_sys, _c21_hold_pass_text
    'Hold a recomputed AND product on a spare wire instead of paying its Toffoli again.\n\nInput: a kmx text and chains of unconditional CCX gates [g0, g1, ..., gk] (op indices) whose\nAND products are the same function of the input on the whole official domain (found and\nverified exactly by tools/audit_pairs.py), with a spare wire available between them.\n\n  g0   CCX a b t   ->  CCX a b S ; CX S t          (S: identically-zero wire nobody references)\n  gi   CCX a b t   ->  CX S t\n  gk   CCX a b t   ->  CX S t ; HMR S m ; CZ a b if m   (S returns to zero; kickback repaid)\n\nWhenever the original circuit is about to reference the current holder, the value hops to\nanother free wire (CX S S2 ; CX S2 S), always outside classically conditioned blocks.\nThe result is a candidate only: the exact50 native proof decides.\n'
    _c21_hold_pass__IntegratedPath = _import_component('pathlib', 'tools/hold_pass.py', False).Path
    _c21_hold_pass_INTEGRATED_ROOT = _c21_hold_pass__IntegratedPath(_c21_hold_pass___file__).resolve().parents[1]
    _c21_hold_pass_bisect = _import_component('bisect', 'tools/hold_pass.py', True)
    _c21_hold_pass_json = _import_component('json', 'tools/hold_pass.py', True)
    _c21_hold_pass_sys = _import_component('sys', 'tools/hold_pass.py', True)
    _c21_hold_pass_Path = _import_component('pathlib', 'tools/hold_pass.py', False).Path
    _c21_hold_pass_sys.path.insert(0, str(_c21_hold_pass_Path(_c21_hold_pass___file__).resolve().parent))
    _c21_hold_pass_kmsim = _import_component('kmsim', 'tools/hold_pass.py', True)

    def _c21_hold_pass_analyse(text):
        ops, registers = _c21_hold_pass_kmsim.parse(text)
        qw = _c21_hold_pass_kmsim.quantum_wires(ops)
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
        sim = _c21_hold_pass_kmsim.Sim(ops, registers['x'])
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
            k = _c21_hold_pass_bisect.bisect_right([x[0] for x in tr], t - 1) - 1
            return not tr[k][1]

        def next_ref(w, t):
            r = refs[w]
            k = _c21_hold_pass_bisect.bisect_left(r, t)
            return r[k] if k < len(r) else 10 ** 9
        return (ops, qw, depth, zero_before, next_ref)

    def _c21_hold_pass_plan_chain(ops, qw, depth, zero_before, next_ref, chain):
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

    def _c21_hold_pass_apply_chains(text, chains):
        """Apply chains one at a time, latest first (edits never shift earlier op indices)."""
        report = []
        for chain in sorted(chains, key=lambda c: -c[0]):
            ops, qw, depth, zero_before, next_ref = _c21_hold_pass_analyse(text)
            plan = _c21_hold_pass_plan_chain(ops, qw, depth, zero_before, next_ref, chain)
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

    def _c21_hold_pass_chains_from_pairs(pairs, Q=48):
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
    if _c21_hold_pass___name__ == '__main__':
        _c21_hold_pass_argparse = _import_component('argparse', 'tools/hold_pass.py', True)
        _c21_hold_pass_ap = _c21_hold_pass_argparse.ArgumentParser()
        _c21_hold_pass_ap.add_argument('kmx', type=_c21_hold_pass_Path)
        _c21_hold_pass_ap.add_argument('pairs', type=_c21_hold_pass_Path)
        _c21_hold_pass_ap.add_argument('--out', type=_c21_hold_pass_Path, required=True)
        _c21_hold_pass_ap.add_argument('--Q', type=int, default=48)
        _c21_hold_pass_args = _c21_hold_pass_ap.parse_args()
        _c21_hold_pass_chains = _c21_hold_pass_chains_from_pairs(_json_loads(_read_text(_c21_hold_pass_args.pairs))['rows'], _c21_hold_pass_args.Q)
        _c21_hold_pass_text, _c21_hold_pass_report = _c21_hold_pass_apply_chains(_read_text(_c21_hold_pass_args.kmx), _c21_hold_pass_chains)
        _c21_hold_pass_args.out.write_text(_c21_hold_pass_text)
        _c21_hold_pass_args.out.with_suffix('.hold.json').write_text(_c21_hold_pass_json.dumps(_c21_hold_pass_report, indent=1) + '\n')
        print(_c21_hold_pass_json.dumps(_c21_hold_pass_report, indent=1))

# tools/kmsim.py
def _initialize__c22_kmsim():
    global _c22_kmsim_INTEGRATED_ROOT, _c22_kmsim_MAX_X, _c22_kmsim_Sampler, _c22_kmsim_Sim, _c22_kmsim_TOFFOLI_LIKE, _c22_kmsim__IntegratedPath, _c22_kmsim___file__, _c22_kmsim___name__, _c22_kmsim_affine_relation, _c22_kmsim_annotations, _c22_kmsim_first_set, _c22_kmsim_np, _c22_kmsim_pack_bits, _c22_kmsim_parse, _c22_kmsim_quantum_wires, _c22_kmsim_solve_span
    'Own bit-sliced full-domain simulator for kickmix text (.kmx) circuits.\n\nEvery one of the 3,133,452 official inputs is one bit position of a uint64\nvector per wire, so one pass over the 36k native operations takes seconds.\nHMR outcomes are drawn independently per input. Phase is not tracked here:\nthis tool only FINDS candidate rewrites; a rewrite counts only after the\nunchanged exact50 native prover and the official verifier accept the circuit.\n'
    pass
    _c22_kmsim__IntegratedPath = _import_component('pathlib', 'tools/kmsim.py', False).Path
    _c22_kmsim_INTEGRATED_ROOT = _c22_kmsim__IntegratedPath(_c22_kmsim___file__).resolve().parents[1]
    _c22_kmsim_np = _import_component('numpy', 'tools/kmsim.py', False)
    _c22_kmsim_MAX_X = 3133452
    _c22_kmsim_TOFFOLI_LIKE = ('CCX', 'CCZ', 'CSWAP')

    def _c22_kmsim_parse(text):
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

    def _c22_kmsim_pack_bits(bits):
        """bool/uint8 vector -> little-endian uint64 words."""
        raw = _c22_kmsim_np.packbits(_c22_kmsim_np.asarray(bits, dtype=_c22_kmsim_np.uint8), bitorder='little')
        pad = -len(raw) % 8
        if pad:
            raw = _c22_kmsim_np.concatenate([raw, _c22_kmsim_np.zeros(pad, dtype=_c22_kmsim_np.uint8)])
        return raw.view('<u8').copy()

    class _c22_kmsim_Sim:
        """Bit-sliced execution. state[wire] is uint64[W]; absent wires are zero."""

        def __init__(self, ops, xreg, xs=None, seed=0):
            self.ops = ops
            self.xs = _c22_kmsim_np.arange(1, _c22_kmsim_MAX_X + 1, dtype=_c22_kmsim_np.uint64) if xs is None else _c22_kmsim_np.asarray(xs, dtype=_c22_kmsim_np.uint64)
            self.n = len(self.xs)
            self.W = (self.n + 63) // 64
            self.ones = _c22_kmsim_pack_bits(_c22_kmsim_np.ones(self.n, dtype=_c22_kmsim_np.uint8))
            if len(self.ones) < self.W:
                self.ones = _c22_kmsim_np.concatenate([self.ones, _c22_kmsim_np.zeros(self.W - len(self.ones), dtype=_c22_kmsim_np.uint64)])
            self.zero = _c22_kmsim_np.zeros(self.W, dtype=_c22_kmsim_np.uint64)
            self.rng = _c22_kmsim_np.random.default_rng(seed)
            self.state = {}
            for i, wire in enumerate(xreg):
                self.state[wire] = _c22_kmsim_pack_bits(self.xs >> _c22_kmsim_np.uint64(i) & _c22_kmsim_np.uint64(1))
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
            if kind in _c22_kmsim_TOFFOLI_LIKE:
                self.toffoli_static += 1
                self.toffoli_executed += self.n if full else int(_c22_kmsim_np.bitwise_count(mask).sum())
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
                outcome = self.rng.integers(0, 1 << 64, self.W, dtype=_c22_kmsim_np.uint64) & self.ones
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
            out = _c22_kmsim_np.zeros(self.n, dtype=_c22_kmsim_np.uint64)
            for i, wire in enumerate(wires):
                if wire is None:
                    continue
                bits = _c22_kmsim_np.unpackbits(self.get(wire).view(_c22_kmsim_np.uint8), bitorder='little')[:self.n]
                out |= bits.astype(_c22_kmsim_np.uint64) << _c22_kmsim_np.uint64(i)
            return out

    def _c22_kmsim_quantum_wires(ops):
        names = set()
        for kind, a, condition, angle, _ in ops:
            for w in a:
                if w.startswith('q'):
                    names.add(w)
        return sorted(names, key=lambda w: int(w[1:]))

    class _c22_kmsim_Sampler:
        """Refinable sample of input positions for GF(2) span pre-filtering."""

        def __init__(self, sim, count=4096, seed=1):
            rng = _c22_kmsim_np.random.default_rng(seed)
            picks = set((int(v) for v in rng.integers(0, sim.n, count)))
            xs = sim.xs
            if len(xs) == _c22_kmsim_MAX_X:
                for i in range(22):
                    for v in ((1 << i) - 1, 1 << i, (1 << i) + 1):
                        if 1 <= v <= _c22_kmsim_MAX_X:
                            picks.add(v - 1)
                picks.update((0, _c22_kmsim_MAX_X - 1))
            self.positions = sorted(picks)
            self._index()

        def _index(self):
            p = _c22_kmsim_np.array(self.positions, dtype=_c22_kmsim_np.int64)
            self.word = p >> 6
            self.bit = (p & 63).astype(_c22_kmsim_np.uint64)

        def add(self, position):
            self.positions.append(int(position))
            self._index()

        def take(self, vector):
            bits = (vector[self.word] >> self.bit & _c22_kmsim_np.uint64(1)).astype(_c22_kmsim_np.uint8)
            return int.from_bytes(_c22_kmsim_np.packbits(bits, bitorder='little').tobytes(), 'little')

    def _c22_kmsim_solve_span(vectors, target):
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

    def _c22_kmsim_first_set(vector):
        words = _c22_kmsim_np.flatnonzero(vector)
        if not len(words):
            return None
        w = int(words[0])
        value = int(vector[w])
        return w * 64 + ((value & -value).bit_length() - 1)

    def _c22_kmsim_affine_relation(sim, sampler, target, names, mask=None, max_refine=64):
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
            combo = _c22_kmsim_solve_span(vectors, sampler.take(t_full))
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
            bad = _c22_kmsim_first_set(acc)
            if bad is None:
                return (chosen, constant)
            sampler.add(bad)
        return None

# tools/kmx_to_kmb.py
def _initialize__c23_kmx_to_kmb():
    global _c23_kmx_to_kmb_CAND10, _c23_kmx_to_kmb_FG, _c23_kmx_to_kmb_HERE, _c23_kmx_to_kmb_INTEGRATED_ROOT, _c23_kmx_to_kmb_Path, _c23_kmx_to_kmb__IntegratedPath, _c23_kmx_to_kmb___file__, _c23_kmx_to_kmb___name__, _c23_kmx_to_kmb_argparse, _c23_kmx_to_kmb_hashlib, _c23_kmx_to_kmb_json, _c23_kmx_to_kmb_main, _c23_kmx_to_kmb_sys, _c23_kmx_to_kmb_time
    "Compile a kmx text to the canonical .kmb/.kmx pair and report its exact expected resources.\n\n    macrun.py tools/kmx_to_kmb.py IN.kmx --out DIR/NAME.kmb [--provenance FILE.json ...]\n\nWrites NAME.kmb, NAME.kmx (kickmix's own serialisation) and NAME.build.json with the exact\nguard-weighted expectation and the modelled cost. Nothing is proved or verified here.\n"
    _c23_kmx_to_kmb__IntegratedPath = _import_component('pathlib', 'tools/kmx_to_kmb.py', False).Path
    _c23_kmx_to_kmb_INTEGRATED_ROOT = _c23_kmx_to_kmb__IntegratedPath(_c23_kmx_to_kmb___file__).resolve().parents[1]
    _c23_kmx_to_kmb_Path = _import_component('pathlib', 'tools/kmx_to_kmb.py', False).Path
    _c23_kmx_to_kmb_argparse = _import_component('argparse', 'tools/kmx_to_kmb.py', True)
    _c23_kmx_to_kmb_hashlib = _import_component('hashlib', 'tools/kmx_to_kmb.py', True)
    _c23_kmx_to_kmb_json = _import_component('json', 'tools/kmx_to_kmb.py', True)
    _c23_kmx_to_kmb_sys = _import_component('sys', 'tools/kmx_to_kmb.py', True)
    _c23_kmx_to_kmb_time = _import_component('time', 'tools/kmx_to_kmb.py', True)
    _c23_kmx_to_kmb_HERE = _c23_kmx_to_kmb_Path(_c23_kmx_to_kmb___file__).resolve().parent
    _c23_kmx_to_kmb_FG = _c23_kmx_to_kmb_HERE.parent
    _c23_kmx_to_kmb_CAND10 = _c23_kmx_to_kmb_FG / 'work/c10/narrow/arithmetic_round2/native/candidate10'
    _c23_kmx_to_kmb_sys.path.insert(0, str(_c23_kmx_to_kmb_CAND10))
    _c23_kmx_to_kmb_sys.path.insert(0, str(_c23_kmx_to_kmb_HERE))

    def _c23_kmx_to_kmb_main():
        ap = _c23_kmx_to_kmb_argparse.ArgumentParser()
        ap.add_argument('kmx', type=_c23_kmx_to_kmb_Path)
        ap.add_argument('--out', type=_c23_kmx_to_kmb_Path, required=True)
        ap.add_argument('--provenance', type=_c23_kmx_to_kmb_Path, action='append', default=[])
        args = ap.parse_args()
        began = _c23_kmx_to_kmb_time.monotonic()
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
        report = dict(status='COMPILED_FROM_TEXT_NOT_YET_PROVED_OR_QUALIFIED', source_kmx=str(args.kmx), source_kmx_sha256=_c23_kmx_to_kmb_hashlib.sha256(_read_bytes(args.kmx)).hexdigest(), provenance={str(p): _json_loads(_read_text(p)) for p in args.provenance}, Q=circuit.num_qubits, exact_native_expectation=resources, cost_model=cost_model(resources, circuit.num_qubits), actual_HMR_variables=program.measurements, native_operations=len(program.operations), kmb_sha256=_c23_kmx_to_kmb_hashlib.sha256(_read_bytes(args.out)).hexdigest(), native_text_sha256=_c23_kmx_to_kmb_hashlib.sha256(text.encode()).hexdigest(), seconds=_c23_kmx_to_kmb_time.monotonic() - began, official_verifier=False, no_submission=True)
        args.out.with_suffix('.build.json').write_text(_c23_kmx_to_kmb_json.dumps(report, indent=2) + '\n')
        print(_c23_kmx_to_kmb_json.dumps(dict(kmb=str(args.out), kmb_sha256=report['kmb_sha256'], cost_model=report['cost_model'], static=resources['static'], HMR=program.measurements), indent=1), flush=True)
    if _c23_kmx_to_kmb___name__ == '__main__':
        _c23_kmx_to_kmb_main()

# tools/merge_zpow.py
def _initialize__c24_merge_zpow():
    global _c24_merge_zpow_Fraction, _c24_merge_zpow_INTEGRATED_ROOT, _c24_merge_zpow_Path, _c24_merge_zpow__IntegratedPath, _c24_merge_zpow___file__, _c24_merge_zpow___name__, _c24_merge_zpow_argparse, _c24_merge_zpow_dyadic, _c24_merge_zpow_hashlib, _c24_merge_zpow_json, _c24_merge_zpow_kind_of, _c24_merge_zpow_kmsim, _c24_merge_zpow_main, _c24_merge_zpow_sys
    'Merge Z_POW gates that act on the same Boolean feature.\n\nA Z_POW of angle a on a wire holding the bit f(x) contributes a*f(x) half-turns. Two unconditioned\nZ_POW gates whose wires hold the SAME function of the input (checked on all 3,133,452 official\ninputs, at the moment each gate acts) can be replaced by one gate with the summed angle, wherever\nthey sit in the circuit. A T-type angle folded into a generic rotation removes a T gate; two\nT-type angles on one feature become a free Clifford angle. (Idea first proved on one adjacent\npair by the normroot audit agent; this pass finds every such group by full-domain equality.)\n\nThe phase function is unchanged, so the exact50 proof against the frozen oracle still applies.\nUsage: merge_zpow.py IN.kmx --out OUT.kmx\n'
    _c24_merge_zpow__IntegratedPath = _import_component('pathlib', 'tools/merge_zpow.py', False).Path
    _c24_merge_zpow_INTEGRATED_ROOT = _c24_merge_zpow__IntegratedPath(_c24_merge_zpow___file__).resolve().parents[1]
    _c24_merge_zpow_argparse = _import_component('argparse', 'tools/merge_zpow.py', True)
    _c24_merge_zpow_hashlib = _import_component('hashlib', 'tools/merge_zpow.py', True)
    _c24_merge_zpow_json = _import_component('json', 'tools/merge_zpow.py', True)
    _c24_merge_zpow_sys = _import_component('sys', 'tools/merge_zpow.py', True)
    _c24_merge_zpow_Fraction = _import_component('fractions', 'tools/merge_zpow.py', False).Fraction
    _c24_merge_zpow_Path = _import_component('pathlib', 'tools/merge_zpow.py', False).Path
    _c24_merge_zpow_sys.path.insert(0, str(_c24_merge_zpow_Path(_c24_merge_zpow___file__).resolve().parent))
    _c24_merge_zpow_kmsim = _import_component('kmsim', 'tools/merge_zpow.py', True)

    def _c24_merge_zpow_dyadic(fr):
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

    def _c24_merge_zpow_kind_of(angle):
        if angle % _c24_merge_zpow_Fraction(1, 2) == 0:
            return 'clifford'
        if angle % _c24_merge_zpow_Fraction(1, 4) == 0:
            return 't'
        return 'rotation'

    def _c24_merge_zpow_main():
        ap = _c24_merge_zpow_argparse.ArgumentParser()
        ap.add_argument('kmx', type=_c24_merge_zpow_Path)
        ap.add_argument('--out', type=_c24_merge_zpow_Path, required=True)
        args = ap.parse_args()
        text = _read_text(args.kmx)
        ops, registers = _c24_merge_zpow_kmsim.parse(text)
        sim = _c24_merge_zpow_kmsim.Sim(ops, registers['x'])
        gates = []

        def before(index, s):
            kind, a, cond, angle, line = ops[index]
            if kind == 'Z_POW' and cond is None and (len(s.stack) == 1):
                vector = s.get(a[0])
                gates.append(dict(op=index, line=line, wire=a[0], angle=_c24_merge_zpow_Fraction(angle), key=_c24_merge_zpow_hashlib.sha256(vector.tobytes()).hexdigest(), nonzero=bool(vector.any())))
        sim.run(before=before)
        groups = {}
        for g in gates:
            groups.setdefault(g['key'], []).append(g)
        lines = text.split('\n')
        delete, report = (set(), [])
        for key, members in groups.items():
            if len(members) < 2 or not members[0]['nonzero']:
                continue
            if all((_c24_merge_zpow_kind_of(m['angle']) == 'clifford' for m in members)):
                continue
            total = sum((m['angle'] for m in members)) % 2
            keep = members[0]
            before_kinds = [_c24_merge_zpow_kind_of(m['angle']) for m in members]
            if total == 0:
                delete.update((m['line'] - 1 for m in members))
            else:
                lines[keep['line'] - 1] = f"Z_POW {keep['wire']} {_c24_merge_zpow_dyadic(total)}"
                delete.update((m['line'] - 1 for m in members[1:]))
            report.append(dict(lines=[m['line'] for m in members], wires=[m['wire'] for m in members], angles=[str(m['angle']) for m in members], before=before_kinds, merged=str(total), after=_c24_merge_zpow_kind_of(total) if total else 'removed'))
        out = '\n'.join((line for i, line in enumerate(lines) if i not in delete))
        args.out.write_text(out)
        count = lambda ks, name: sum((1 for k in ks if k == name))
        all_before = [_c24_merge_zpow_kind_of(g['angle']) for g in gates]
        summary = dict(z_pow_gates=len(gates), groups_merged=len(report), t_before=count(all_before, 't'), rotations_before=count(all_before, 'rotation'), merges=report)
        args.out.with_suffix('.zpow.json').write_text(_c24_merge_zpow_json.dumps(summary, indent=1) + '\n')
        print(_c24_merge_zpow_json.dumps({k: v for k, v in summary.items() if k != 'merges'}), [(r['before'], r['after']) for r in report])
    if _c24_merge_zpow___name__ == '__main__':
        _c24_merge_zpow_main()

# tools/postpass.py
def _initialize__c25_postpass():
    global _c25_postpass_INTEGRATED_ROOT, _c25_postpass_Path, _c25_postpass__IntegratedPath, _c25_postpass___file__, _c25_postpass___name__, _c25_postpass__ccx, _c25_postpass_ap, _c25_postpass_apply_rewrites, _c25_postpass_argparse, _c25_postpass_args, _c25_postpass_json, _c25_postpass_k, _c25_postpass_records, _c25_postpass_report, _c25_postpass_sys, _c25_postpass_text, _c25_postpass_v
    "kmx-level rewrites of Toffoli-like gates whose AND product is affine in live wires.\n\nA rewrite record (from tools/audit_affine.py) names one gate by its text line and\ngives the full-domain relation  product = XOR(relation_wires) xor relation_constant\nthat holds just before the gate on every reachable state where the gate is active.\n\n  CCX a b t, t not in relation:   CX w t (each w), X t if constant.\n  CCX a b t, t in relation:       t currently equals ab xor affine(L). Clear the affine\n                                  part with CX/X, HMR t (kickback (-1)^(m ab)), repay\n                                  with CZ a b if m, then write affine(L) back with CX/X.\n  CSWAP c x y:                    CX y x ; CCX c x y ; CX y x, with the middle gate\n                                  rewritten as above (x replaced by x xor y in the relation).\n  CCZ a b c, product 'ab' etc.:   CZ w third (Z third when w is third), Z third if constant.\n\nEvery replacement is Clifford plus measurement. Records are checked against the\ntext (kind and arguments must match) and each needs a fresh classical bit at most.\nThe result is only a candidate: the exact50 native proof decides.\n"
    _c25_postpass__IntegratedPath = _import_component('pathlib', 'tools/postpass.py', False).Path
    _c25_postpass_INTEGRATED_ROOT = _c25_postpass__IntegratedPath(_c25_postpass___file__).resolve().parents[1]
    _c25_postpass_json = _import_component('json', 'tools/postpass.py', True)

    def _c25_postpass__ccx(a, b, t, wires, constant, fresh_bit):
        wires = list(wires)
        if t not in wires:
            out = [f'CX {w} {t}' for w in wires]
            if constant:
                out.append(f'X {t}')
            return (out, False)
        rest = [w for w in wires if w != t]
        affine = [f'CX {w} {t}' for w in rest] + ([f'X {t}'] if constant else [])
        return (affine + [f'HMR {t} {fresh_bit}', f'CZ {a} {b} if {fresh_bit}'] + affine, True)

    def _c25_postpass_apply_rewrites(text, records):
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
                new, used_bit = _c25_postpass__ccx(a, b, t, wires, constant, fresh)
            elif kind == 'CSWAP':
                c, x, y = arguments
                assert record['product'] == 'c(x^y)'
                moved = set(wires)
                if x in moved:
                    moved ^= {y}
                ordered = [w for w in wires if w in moved] + sorted(moved - set(wires))
                middle, used_bit = _c25_postpass__ccx(c, x, y, ordered, constant, fresh)
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
    if _c25_postpass___name__ == '__main__':
        _c25_postpass_argparse = _import_component('argparse', 'tools/postpass.py', True)
        _c25_postpass_sys = _import_component('sys', 'tools/postpass.py', True)
        _c25_postpass_Path = _import_component('pathlib', 'tools/postpass.py', False).Path
        _c25_postpass_ap = _c25_postpass_argparse.ArgumentParser()
        _c25_postpass_ap.add_argument('kmx', type=_c25_postpass_Path)
        _c25_postpass_ap.add_argument('records', type=_c25_postpass_Path)
        _c25_postpass_ap.add_argument('--out', type=_c25_postpass_Path, required=True)
        _c25_postpass_args = _c25_postpass_ap.parse_args()
        _c25_postpass_records = _json_loads(_read_text(_c25_postpass_args.records))
        _c25_postpass_records = _c25_postpass_records['findings'] if isinstance(_c25_postpass_records, dict) else _c25_postpass_records
        _c25_postpass_text, _c25_postpass_report = _c25_postpass_apply_rewrites(_read_text(_c25_postpass_args.kmx), _c25_postpass_records)
        _c25_postpass_args.out.write_text(_c25_postpass_text)
        print(_c25_postpass_json.dumps({k: v for k, v in _c25_postpass_report.items() if k != 'rewrites'}))

# work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py
def _initialize__c26_arithmetic_setup():
    global _c26_arithmetic_setup_BASE, _c26_arithmetic_setup_GATE_SHA, _c26_arithmetic_setup_HERE, _c26_arithmetic_setup_INTEGRATED_ROOT, _c26_arithmetic_setup_NARROW, _c26_arithmetic_setup_Path, _c26_arithmetic_setup_ROUND, _c26_arithmetic_setup__INSTALLED, _c26_arithmetic_setup__IntegratedPath, _c26_arithmetic_setup___file__, _c26_arithmetic_setup___name__, _c26_arithmetic_setup_accepted_gate, _c26_arithmetic_setup_check_manifest, _c26_arithmetic_setup_hashlib, _c26_arithmetic_setup_importlib, _c26_arithmetic_setup_install, _c26_arithmetic_setup_json, _c26_arithmetic_setup_load, _c26_arithmetic_setup_name, _c26_arithmetic_setup_old, _c26_arithmetic_setup_os, _c26_arithmetic_setup_sha, _c26_arithmetic_setup_sys, _c26_arithmetic_setup_verify_sources
    'Hash-bound arithmetic adapters; protected phase and loader sources intact.'
    _c26_arithmetic_setup__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', False).Path
    _c26_arithmetic_setup_INTEGRATED_ROOT = _c26_arithmetic_setup__IntegratedPath(_c26_arithmetic_setup___file__).resolve().parents[6]
    _c26_arithmetic_setup_Path = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', False).Path
    _c26_arithmetic_setup_hashlib = _import_component('hashlib', 'work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', True)
    _c26_arithmetic_setup_importlib = _import_component('importlib.util', 'work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', True)
    _c26_arithmetic_setup_json = _import_component('json', 'work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', True)
    _c26_arithmetic_setup_os = _import_component('os', 'work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', True)
    _c26_arithmetic_setup_sys = _import_component('sys', 'work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', True)
    for _c26_arithmetic_setup_name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        _c26_arithmetic_setup_os.environ[_c26_arithmetic_setup_name] = '1'
    _c26_arithmetic_setup_HERE = _c26_arithmetic_setup_Path(_c26_arithmetic_setup___file__).resolve().parent
    _c26_arithmetic_setup_NARROW = _c26_arithmetic_setup_HERE.parents[2]
    _c26_arithmetic_setup_ROUND = _c26_arithmetic_setup_NARROW / 'arithmetic_round2'
    _c26_arithmetic_setup_BASE = _c26_arithmetic_setup_NARROW / 'native/candidate07'
    _c26_arithmetic_setup_GATE_SHA = 'eb427769c7166ea94422a4d910cd47a2284c38f46f4eb311885ed6b86e6eb714'

    def _c26_arithmetic_setup_sha(path):
        return _c26_arithmetic_setup_hashlib.sha256(_read_bytes(_c26_arithmetic_setup_Path(path))).hexdigest()

    def _c26_arithmetic_setup_check_manifest(path, root):
        manifest = _json_loads(_read_text(_c26_arithmetic_setup_Path(path)))
        pass
        return manifest

    def _c26_arithmetic_setup_verify_sources():
        """Source integrity is verified by the integrated manifest before execution."""
        pass

    def _c26_arithmetic_setup_load(name, path):
        path = _c26_arithmetic_setup_Path(path).resolve()
        pins = _json_loads(_read_text(_c26_arithmetic_setup_HERE / 'INPUTS.json'))['files']
        selected = [pin for pin in pins if (_c26_arithmetic_setup_NARROW / pin['path']).resolve() == path]
        pass
        if name not in _c26_arithmetic_setup_sys.modules:
            spec = _spec(name, path)
            module = _new_module(spec)
            _c26_arithmetic_setup_sys.modules[name] = module
            spec.loader.exec_module(module)
        module = _c26_arithmetic_setup_sys.modules[name]
        pass
        return module
    _c26_arithmetic_setup_verify_sources()
    _c26_arithmetic_setup_old = _c26_arithmetic_setup_load('variant', _c26_arithmetic_setup_BASE / 'variant.py')
    _c26_arithmetic_setup__INSTALLED = None

    def _c26_arithmetic_setup_accepted_gate():
        _c26_arithmetic_setup_verify_sources()
        pass
        gate = _json_loads(_read_text(_c26_arithmetic_setup_HERE / 'COMPLETE_GATE.json'))
        accepted = _json_loads(_read_text(_c26_arithmetic_setup_HERE / 'PARENT_ACCEPTED.json'))
        assert accepted['native_build_authorized']
        pass
        assert accepted['all_selected_components_native_proved']
        assert gate['Q'] == 48 and gate['expected_Toffolis'] == 1548.75
        assert gate['T'] == 4 and gate['R'] == 33
        assert sum(gate['components_expected_Toffolis'].values()) == gate['expected_Toffolis']
        assert gate['first_preparation_peak'] == gate['second_preparation_peak'] == gate['endpoint_peak'] == 48
        assert gate['rotation_charge'] == 230.84805946161188
        assert gate['expected_cost'] == 48 * (1548.75 + 1 + gate['rotation_charge'])
        assert gate['original_exact_minimum_margin_units64'] == 124370688
        pass
        assert gate['original_tolerance_unchanged'] and gate['protected_phase_tables_angles_oracle_unchanged']
        fit, digest = _c26_arithmetic_setup_old.accuracy_receipt()
        pass
        pass
        return gate

    def _c26_arithmetic_setup_install():
        global _c26_arithmetic_setup__INSTALLED
        gate = _c26_arithmetic_setup_accepted_gate()
        if _c26_arithmetic_setup__INSTALLED is None:
            _c26_arithmetic_setup_old.install()
            modules = {name: _c26_arithmetic_setup_load('candidate10_adapter_' + name, _c26_arithmetic_setup_NARROW / path) for name, path in gate['adapter_paths'].items()}
            lifecycle10 = _import_component('lifecycle10', 'work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', True)
            pass
            lifecycle = lifecycle10
            baseline = _c26_arithmetic_setup_old.inherited_module('lifecycle06').baseline
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
            modules['divider'].install(_c26_arithmetic_setup_old.divider)
            _c26_arithmetic_setup__INSTALLED = modules
        _c26_arithmetic_setup_verify_sources()
        return _c26_arithmetic_setup__INSTALLED

# work/c10/narrow/arithmetic_round2/native/candidate10/lifecycle10.py
def _initialize__c27_lifecycle10():
    global _c27_lifecycle10_CUT_HOOK, _c27_lifecycle10_INTEGRATED_ROOT, _c27_lifecycle10__IntegratedPath, _c27_lifecycle10___file__, _c27_lifecycle10___name__, _c27_lifecycle10__mark, _c27_lifecycle10_baseline, _c27_lifecycle10_emit_body, _c27_lifecycle10_product_inverse
    'Isolated arithmetic lifecycle; unchanged protected callbacks, mutable v3 owner.'
    _c27_lifecycle10__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/native/candidate10/lifecycle10.py', False).Path
    _c27_lifecycle10_INTEGRATED_ROOT = _c27_lifecycle10__IntegratedPath(_c27_lifecycle10___file__).resolve().parents[6]
    _c27_lifecycle10_baseline = None
    _c27_lifecycle10_product_inverse = None
    _c27_lifecycle10_CUT_HOOK = None

    def _c27_lifecycle10__mark(builder, trace, label, expected, owners=None):
        live = builder.num_allocated_qubits
        assert live == expected, (label, live, expected)
        assert live <= 48, (label, live)
        if trace is not None:
            trace.append(dict(label=label, live_owners=live))
        if _c27_lifecycle10_CUT_HOOK is not None:
            _c27_lifecycle10_CUT_HOOK(label, builder, {} if owners is None else {key: list(value) for key, value in owners.items()})

    def _c27_lifecycle10_emit_body(builder, v12, h10, flags4, table_module, divider_module, decode_root_callback, *, trace=None):
        """Compute phase and restore current(v12,h10), with no stale root handles.

    table_module.load_joint16 retains its old call shape. Its second variant
    expects the R frame already active and consumes address slots0/1/2/4.
    decode_root_callback accepts None for their already-owned table signs;
    the later raw-a6 HMR is the only separate direct root phase correction.
    """
        assert builder.max_qubits == 48
        v = list(v12)
        h = list(h10)
        flags = list(flags4)
        assert (len(v), len(h), len(flags)) == (12, 10, 4)
        assert len(set(v + h + flags)) == 26
        _c27_lifecycle10__mark(builder, trace, 'body_entry', 26, dict(v=v, h=h, flags=flags))
        table_debts = table_module.TableDebts()
        truths = table_module.model_truths()
        D, Hlow = table_module.load_joint16(builder, v[5:], variant='first', debts=table_debts)
        D = list(D)
        H = list(Hlow)
        _c27_lifecycle10__mark(builder, trace, 'first_table', 42, dict(v=v, h=h, flags=flags, D=D, H=H))
        H.append(_c27_lifecycle10_baseline.prepare_H3_initial(builder, v, D, H))
        _c27_lifecycle10_baseline.root_R_frame(builder, v)
        H.append(_c27_lifecycle10_baseline.prepare_H4(builder, D, H[3]))
        first = _c27_lifecycle10_baseline.coefficient_forward(builder, v, D, H)
        _c27_lifecycle10__mark(builder, trace, 'first_coefficient', 45, dict(v=v, h=h, flags=flags, D=D, H=H, snapshot=[first.saved_bit]))
        Hlow = _c27_lifecycle10_baseline.erase_high_H(builder, v, D, H)
        for i, q in enumerate(Hlow):
            table_debts.erase(builder, q, truths['H'][i], free=True)
        first_snapshot = _c27_lifecycle10_baseline.ar.release_saved_bit(builder, first.saved_bit)
        first.saved_bit = None
        _c27_lifecycle10_baseline.root_R_frame(builder, v, inverse=True)
        _c27_lifecycle10__mark(builder, trace, 'first_metadata_retired', 39)
        seed, seed_token = _c27_lifecycle10_baseline.seed_forward(builder, v, D)
        _c27_lifecycle10__mark(builder, trace, 'seed_ready', 45, dict(v=v, h=h, flags=flags, D=D, seed=seed))
        word, product_token = _c27_lifecycle10_baseline.product_forward(builder, D, seed, h)
        builder.x(word[15])
        builder.cx(word[14], word[15])
        builder.free(word[15])
        P = word[:15]
        _c27_lifecycle10__mark(builder, trace, 'signed_product15', 44, dict(v=v, P=P, flags=flags, D=D))
        first_D = []
        for q in D:
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            builder.free(q)
            first_D.append(m)
        _c27_lifecycle10__mark(builder, trace, 'coefficient_retired_for_divider', 31, dict(v=v, P=P, flags=flags))
        P = list(divider_module.compute_phase_cleanup(builder, v, P, flags))
        assert len(P) == 15 and len(set(v + P + flags)) == 31
        _c27_lifecycle10__mark(builder, trace, 'divider_return', 31, dict(v=v, P=P, flags=flags))
        _c27_lifecycle10_baseline.root_R_frame(builder, v)
        D, Hlow = table_module.load_joint16(builder, v[5:], variant='second', debts=table_debts)
        D = list(D)
        H = list(Hlow)
        retired = {a: None for a in (0, 1, 2, 4)}
        for a in retired:
            v[5 + a] = None
        assert all((v[5 + a] is None for a in (0, 1, 2, 4)))
        assert v[8] is not None and v[10] is not None and (v[11] is not None)
        _c27_lifecycle10__mark(builder, trace, 'second_table', 43, dict(v=v, P=P, flags=flags, D=D, H=H))
        _c27_lifecycle10_baseline.ar.repay_saved_bit(builder, D[6], first_snapshot)
        H.append(_c27_lifecycle10_baseline.prepare_H3_initial(builder, v, D, H))
        _c27_lifecycle10__mark(builder, trace, 'second_H3_ready', 44, dict(v=v, P=P, flags=flags, D=D, H=H))
        q = v[11]
        m = builder.alloc_bits(1)[0]
        builder.hmr(q, m)
        builder.free(q)
        v[11] = None
        retired[6] = m
        assert set(retired) == {0, 1, 2, 4, 6} and all((retired[a] is None for a in (0, 1, 2, 4)))
        _c27_lifecycle10__mark(builder, trace, 'second_a6_retired', 43, dict(v=v, P=P, flags=flags, D=D, H=H))
        H.append(_c27_lifecycle10_baseline.prepare_H4(builder, D, H[3]))
        second = _c27_lifecycle10_baseline.coefficient_forward(builder, v, D, H)
        _c27_lifecycle10__mark(builder, trace, 'second_coefficient', 45, dict(v=v, P=P, flags=flags, D=D, H=H, snapshot=[second.saved_bit]))
        for q, m in zip(D, first_D):
            builder.push_condition(m)
            builder.z(q)
            builder.pop_condition()
            builder.free(m)
        _c27_lifecycle10_baseline.merge_coefficient_transcripts(builder, first, second)
        Hlow = _c27_lifecycle10_baseline.erase_high_H(builder, v, D, H)
        _c27_lifecycle10__mark(builder, trace, 'second_metadata_retired', 43)
        high = builder.alloc_qubits(1)[0]
        builder.cx(P[14], high)
        builder.x(high)
        word = P + [high]
        _c27_lifecycle10__mark(builder, trace, 'inverse_product_data', 44, dict(v=v, word=word, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
        dirty = [q for q in v if q is not None] + flags + Hlow + [second.saved_bit]
        seed, h = _c27_lifecycle10_product_inverse(builder, v, D, word, product_token, dirty)
        _c27_lifecycle10_baseline.seed_cleanup(builder, v, D, seed, seed_token)
        _c27_lifecycle10__mark(builder, trace, 'seed_cleared', 38, dict(v=v, h=h, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
        H = list(Hlow)
        H.append(_c27_lifecycle10_baseline.prepare_H3_current(builder, v, D, H))
        H.append(_c27_lifecycle10_baseline.prepare_H4(builder, D, H[3]))
        _c27_lifecycle10__mark(builder, trace, 'coefficient_sources_restored', 40)
        _c27_lifecycle10_baseline.coefficient_inverse(builder, v, D, H, second, [q for q in v if q is not None] + flags + h)
        _c27_lifecycle10__mark(builder, trace, 'A_restored', 39, dict(v=v, h=h, flags=flags, A=D, H=H))
        v = list(decode_root_callback(builder, v, D, H, retired))
        assert all((q is not None for q in v)) and len(set(v + h + flags)) == 26
        _c27_lifecycle10_baseline.root_R_frame(builder, v, inverse=True)
        _c27_lifecycle10__mark(builder, trace, 'raw_root_restored', 44, dict(v=v, h=h, flags=flags, A=D, H=H))
        Hlow = _c27_lifecycle10_baseline.erase_high_H(builder, v, D, H, initial=True)
        table_module.cleanup_joint16(builder, v[5:], D, Hlow, table_debts)
        assert not table_debts.pending
        assert first.saved_bit is None and second.saved_bit is None
        for token in (first, second):
            assert all((debt.consumed and (not debt.measurements) for debt in token.row_debts))
            assert token.overflow_debt.consumed and (not token.overflow_debt.measurements)
        assert all((debt.consumed and (not debt.measurements) for debt in product_token.rows))
        _c27_lifecycle10__mark(builder, trace, 'body_return', 26, dict(v=v, h=h, flags=flags))
        return (v, h)

# work/c10/narrow/arithmetic_round2/research/divider/history12_kernel.py
def _initialize__c28_history12_kernel():
    global _c28_history12_kernel_INTEGRATED_ROOT, _c28_history12_kernel__IntegratedPath, _c28_history12_kernel___file__, _c28_history12_kernel___name__, _c28_history12_kernel_base, _c28_history12_kernel_cleanup_divider
    'Paper-only post-endpoint retirement; no forward or phase changes.'
    _c28_history12_kernel__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/divider/history12_kernel.py', False).Path
    _c28_history12_kernel_INTEGRATED_ROOT = _c28_history12_kernel__IntegratedPath(_c28_history12_kernel___file__).resolve().parents[6]
    _c28_history12_kernel_base = _import_component('top12_kernel', 'work/c10/narrow/arithmetic_round2/research/divider/history12_kernel.py', False)

    def _c28_history12_kernel_cleanup_divider(d, b, token, *, trace=None):
        assert b.max_qubits == 48 and b.num_allocated_qubits == 43
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
        assert b.num_allocated_qubits == 42
        if trace:
            trace('retired_history12', None, None)
        for j, k, debt in reversed(token.rows):
            if j == 12:
                assert not token.history and token.u[-1] == next_sign
                rebuilt = b.alloc_qubits(1)[0]
                b.cx(v[11], rebuilt)
                b.cx(v[10], rebuilt)
                b.ccx(v[10], token.u[-1], rebuilt)
                token.history[12] = rebuilt
                initial = list(token.initial_u)
                assert initial[13] == old_sign
                initial[13] = rebuilt
                token.initial_u = tuple(initial)
                if trace:
                    trace('rebuilt_history12', j, None)
                result = _c28_history12_kernel_base.last_feed_and_initial(d, b, token, debt)
                assert all((x.consumed and (not x.measurements) for _, _, x in token.rows))
                if trace:
                    trace('last_feed_and_initial', j, None)
                return result
            u = token.u
            if j <= 24:
                low = u[0]
                target = u[1:]
                sign = token.history[j]
                cur = token.P[23 - j] if j < 24 else None
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
            else:
                b.cx(v[0], u[0])
                sign = u[0]
                target = u[k + 1:]
                d._frame(b, sign, target)
                d._leading_offset(b, target, inverse=True)
                d.inverse_add(b, v[k + 1:], target, debt, carry_in=v[k], dirty_wires=d._dirty(token))
                d._frame(b, sign, target)
                token.u = u[1:] + u[:1]
            assert debt.consumed and (not debt.measurements) and (b.num_allocated_qubits == 42)
            if trace:
                trace('inverse_row', j, k)
        raise AssertionError('The final feed was not reached')

# work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py
def _initialize__c29_adapter():
    global _c29_adapter_ACCEPTANCE, _c29_adapter_ACCEPTANCE_SHA, _c29_adapter_CONTRACT, _c29_adapter_HERE, _c29_adapter_INTEGRATED_ROOT, _c29_adapter_KERNEL, _c29_adapter_KERNEL_SHA, _c29_adapter_NARROW, _c29_adapter_Path, _c29_adapter_TOP_KERNEL, _c29_adapter_TOP_KERNEL_SHA, _c29_adapter__IntegratedPath, _c29_adapter___file__, _c29_adapter___name__, _c29_adapter_bind, _c29_adapter_hashlib, _c29_adapter_importlib, _c29_adapter_install, _c29_adapter_json, _c29_adapter_kernel, _c29_adapter_load, _c29_adapter_sha, _c29_adapter_sys, _c29_adapter_verify
    'Authorized AR004 cleanup-only adapter; forward and phase stay unchanged.'
    _c29_adapter__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', False).Path
    _c29_adapter_INTEGRATED_ROOT = _c29_adapter__IntegratedPath(_c29_adapter___file__).resolve().parents[7]
    _c29_adapter_Path = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', False).Path
    _c29_adapter_hashlib = _import_component('hashlib', 'work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', True)
    _c29_adapter_importlib = _import_component('importlib.util', 'work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', True)
    _c29_adapter_json = _import_component('json', 'work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', True)
    _c29_adapter_sys = _import_component('sys', 'work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', True)
    _c29_adapter_HERE = _c29_adapter_Path(_c29_adapter___file__).resolve().parent
    _c29_adapter_NARROW = _c29_adapter_HERE.parents[3]
    _c29_adapter_KERNEL = _c29_adapter_HERE.parent / 'history12_kernel.py'
    _c29_adapter_KERNEL_SHA = '1dc5022918a0a47663ec3ad812cdff67f93ee0c1646f3e4db59ee7881c847afe'
    _c29_adapter_TOP_KERNEL = _c29_adapter_HERE.parent / 'top12_kernel.py'
    _c29_adapter_TOP_KERNEL_SHA = 'f4367db957bac36fc319389358984ecf00b6b8788b7e19894f0600cf1e68aec5'
    _c29_adapter_ACCEPTANCE = _c29_adapter_NARROW / 'arithmetic_round2/receipts/DIVIDER_HISTORY12_PAPER_ACCEPTED.json'
    _c29_adapter_ACCEPTANCE_SHA = 'd188e0b75ffa397879884f4d77c64fa409b4cada180e5253244f415d84e1d8e7'

    def _c29_adapter_sha(path):
        return _c29_adapter_hashlib.sha256(_read_bytes(_c29_adapter_Path(path))).hexdigest()

    def _c29_adapter_verify():
        pass
        assert _json_loads(_read_text(_c29_adapter_ACCEPTANCE))['native_build_authorized'] is True
        pass
        for pin in _json_loads(_read_text(_c29_adapter_HERE / 'INPUTS.json'))['files']:
            path = _c29_adapter_NARROW / pin['path']
            pass

    def _c29_adapter_load(name, path):
        if name not in _c29_adapter_sys.modules:
            spec = _spec(name, path)
            module = _new_module(spec)
            _c29_adapter_sys.modules[name] = module
            spec.loader.exec_module(module)
        module = _c29_adapter_sys.modules[name]
        pass
        return module

    def _c29_adapter_kernel():
        _c29_adapter_verify()
        base = _c29_adapter_load('top12_kernel', _c29_adapter_TOP_KERNEL)
        result = _c29_adapter_load('_ar004_frozen_history12_kernel', _c29_adapter_KERNEL)
        assert result.base is base
        return result

    def _c29_adapter_bind(divider):
        _c29_adapter_verify()
        pass
        pass
        pass
        implementation = _c29_adapter_kernel()

        def cleanup(builder, token):
            return implementation.cleanup_divider(divider, builder, token)
        return cleanup

    def _c29_adapter_install(divider):
        forward, phase, initializer = (divider.compute_divider, divider.phase_endpoint, divider.initialize_u12)
        divider.cleanup_divider = _c29_adapter_bind(divider)
        assert divider.compute_divider is forward and divider.phase_endpoint is phase
        assert divider.initialize_u12 is initializer
        return divider
    _c29_adapter_CONTRACT = dict(Q=48, divider_E=578.0, T=0, R=0, forward_unchanged=True, endpoint43_unchanged=True, inverse42_until_history13_restored=True, entry_and_return_owners=31, all24_carry_debts_required=True, returns_current_P15=True, only_frozen_model_original_domain_claimed=True)

# work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py
def _initialize__c30_top12_kernel():
    global _c30_top12_kernel_INTEGRATED_ROOT, _c30_top12_kernel_MAJORITY_TRUTH, _c30_top12_kernel__IntegratedPath, _c30_top12_kernel___file__, _c30_top12_kernel___name__, _c30_top12_kernel__compute_carry, _c30_top12_kernel__erase_carry, _c30_top12_kernel__phase_borrow, _c30_top12_kernel__phase_terminal, _c30_top12_kernel_cleanup_divider, _c30_top12_kernel_cleanup_initial_missing12, _c30_top12_kernel_initial_bit_plan, _c30_top12_kernel_inverse_lower12, _c30_top12_kernel_last_feed_and_initial, _c30_top12_kernel_pa, _c30_top12_kernel_phase_quadratic
    'Paper candidate: exact final-feed top measurement and source-aware cleanup.\n\nThis module writes no circuit or artifact and installs no global hooks.\nThe parent must separately approve a complete paper gate before native use.\n'
    _c30_top12_kernel__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', False).Path
    _c30_top12_kernel_INTEGRATED_ROOT = _c30_top12_kernel__IntegratedPath(_c30_top12_kernel___file__).resolve().parents[6]
    _c30_top12_kernel_pa = _import_component('paired_arithmetic', 'work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', False)
    _c30_top12_kernel__compute_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', False)._compute_carry
    _c30_top12_kernel__erase_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', False)._erase_carry
    _c30_top12_kernel__phase_borrow = _import_component('fusion.arithmetic', 'work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', False)._phase_borrow
    _c30_top12_kernel_phase_quadratic = _import_component('fusion.compiler', 'work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', False).phase_quadratic
    _c30_top12_kernel_MAJORITY_TRUTH = _import_component('fusion.compiler', 'work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', False).MAJORITY_TRUTH

    def _c30_top12_kernel_initial_bit_plan(d, i):

        def aa(j):
            return (1, 1 << j) if 0 <= j < 12 else (0, 0)

        def bb(j):
            return (1, 0) if j in (0, 13) else (1, 1 << j - 1)
        return d._compose(d.HIGH, [aa(i), bb(i), aa(i - 2), aa(i - 3), aa(i - 1), (0, 1 << 12)], 13)

    def _c30_top12_kernel__phase_terminal(b, a, target, incoming, *, start, debt, top_outcome):
        """Write the low sum and phase its exact final carry, with no data top."""
        frames = []
        carry = incoming
        for i, (aa, bb) in enumerate(zip(a[:-1], target[:-1])):
            frame = _c30_top12_kernel__compute_carry(b, aa, bb, carry)
            outcome = debt.measurements.pop(start + i + 1, None)
            if outcome is not None:
                if frame.outgoing is not False:
                    b.push_condition(outcome)
                    b.z(frame.outgoing)
                    b.pop_condition()
                b.free(outcome)
            frames.append(frame)
            carry = frame.outgoing
        b.push_condition(top_outcome)
        _c30_top12_kernel_phase_quadratic(b, [a[-1], target[-1], carry], _c30_top12_kernel_MAJORITY_TRUTH)
        b.pop_condition()
        assert start + len(target) not in debt.measurements
        b.cx(a[-1], target[-1])
        b.cx(carry, target[-1])
        for frame in reversed(frames):
            _c30_top12_kernel__erase_carry(b, frame, write_sum=True)

    def _c30_top12_kernel_inverse_lower12(d, b, source, target, debt, carry, top_outcome, lifecycle):
        """Exact14E Pauli-terminal inverse; all original11 debt positions paid."""
        a, target, preserve = _c30_top12_kernel_pa._inputs(source, target, carry, False)
        assert len(target) == 12 and len(source) == 11 and (preserve is None)
        assert debt.width == 13 and (not debt.consumed)
        assert sorted(debt.measurements) == list(range(1, 12))
        assert b.max_qubits == 48 and b.num_allocated_qubits == 43
        debt.consumed = True
        b.x(d.array(target))
        boundaries = []
        start = 0
        incoming = carry
        for number, length in enumerate((3, 4, 5)):
            aa = a[start:start + length]
            bb = target[start:start + length]
            if number == 2:
                _c30_top12_kernel__phase_terminal(b, aa, bb, incoming, start=start, debt=debt, top_outcome=top_outcome)
            else:
                outgoing = _c30_top12_kernel_pa._segment_repay(b, aa, bb, incoming, retain_outgoing=True, preserve=None, start=start, debt=debt)
                recorded = incoming
                if number == 0:
                    lifecycle[0](carry)
                    recorded = None
                boundaries.append((aa, bb, recorded, outgoing))
                incoming = outgoing
            start += length
        for aa, bb, incoming, outgoing in reversed(boundaries):
            outcome = b.alloc_bits(1)[0]
            b.hmr(outgoing, outcome)
            b.free(outgoing)
            b.push_condition(outcome)
            rebuilt = incoming is None
            if rebuilt:
                incoming = lifecycle[1]()
            _c30_top12_kernel__phase_borrow(b, aa, bb, incoming)
            if rebuilt:
                lifecycle[0](incoming)
            b.pop_condition()
            b.free(outcome)
        b.x(d.array(target))
        assert not debt.measurements and b.num_allocated_qubits == 42

    def _c30_top12_kernel_cleanup_initial_missing12(d, b, v, P, u, *, omit_sigma_phase=False):
        """1.5E, with one measured absent top; return fresh P13/P14 owners."""
        assert len(u) == 14 and u[12] is None and (b.num_allocated_qubits == 42)
        P = list(P)
        P[13], P[14] = list(b.alloc_qubits(2))
        variables = [v[0], v[1], P[12], u[0], u[1]]
        d.cb.emit_xor(b, variables, P[13], d.P13)
        d.cb.emit_xor(b, variables, P[14], d.P14)
        outcome = b.alloc_bits(1)[0]
        b.hmr(u[13], outcome)
        b.free(u[13])
        b.push_condition(outcome)
        b.z(v[11])
        helper = b.alloc_qubits(1)[0]
        plan = _c30_top12_kernel_initial_bit_plan(d, 12)
        d.cb.emit_xor(b, list(v) + [u[11]], helper, plan)
        if not omit_sigma_phase:
            b.cz(v[10], helper)
        d._erase(b, helper, list(v) + [u[11]], plan)
        b.pop_condition()
        b.free(outcome)
        for i in reversed(range(4, 12)):
            d._erase(b, u[i], list(v) + [u[i - 1]], _c30_top12_kernel_initial_bit_plan(d, i))
        for i in reversed(range(4)):
            item = d.LOCAL['low_cleanup'][i]
            env = {f'v{j}': v[j] for j in range(i + 1)}
            env.update(p12=P[12], p13=P[13], p14=P[14])
            env.update({f'u{j}': u[j] for j in range(i)})
            d._erase(b, u[i], [env[name] for name in item['inputs']], d.plan_from_json(item['plan']))
        assert b.num_allocated_qubits == 31
        return P

    def _c30_top12_kernel_last_feed_and_initial(d, b, token, debt, *, omit_top_phase=False, omit_sigma_phase=False):
        """Replace only inverse j12 plus cleanup_u12; forward remains unchanged."""
        assert b.max_qubits == 48 and b.num_allocated_qubits == 43
        assert sorted(token.history) == [12]
        v = token.v
        u = token.u
        low = u[0]
        target = u[1:]
        sign = token.history[12]
        cur = token.P[11]
        assert len(target) == 13 and cur is not None
        carry = d._feed_carry(b, v, low, cur, sign)
        d._frame(b, sign, target)
        d._leading_offset(b, target, inverse=True)
        top_outcome = b.alloc_bits(1)[0]
        b.hmr(target[-1], top_outcome)
        b.free(target[-1])
        retained = target[:-1]
        _c30_top12_kernel_inverse_lower12(d, b, v[1:], retained, debt, carry, top_outcome, (lambda value: d._feed_erase(b, value, v, low, cur, sign), lambda: d._feed_carry(b, v, low, cur, sign)))
        d._frame(b, sign, retained)
        if not omit_top_phase:
            d.cb.emit_phase(b, list(v) + [retained[11]], top_outcome, _c30_top12_kernel_initial_bit_plan(d, 12))
            b.z(top_outcome)
            b.push_condition(top_outcome)
            b.z(sign)
            b.pop_condition()
        b.free(top_outcome)
        b.cx(cur, low)
        b.cx(sign, low)
        b.cx(v[0], low)
        token.P[12] = low
        token.u = retained + [None, sign]
        del token.history[12]
        assert tuple(token.u[:12]) == token.initial_u[:12]
        assert sign == token.initial_u[13]
        token.P = _c30_top12_kernel_cleanup_initial_missing12(d, b, v, token.P, token.u, omit_sigma_phase=omit_sigma_phase)
        token.u = []
        return list(token.P)

    def _c30_top12_kernel_cleanup_divider(d, b, token):
        """The complete inverse, with23 unchanged rows and one source-aware row."""
        assert b.max_qubits == 48 and b.num_allocated_qubits == 43
        assert not token.consumed and len(token.rows) == 24
        token.consumed = True
        v = token.v
        for j, k, debt in reversed(token.rows):
            if j == 12:
                result = _c30_top12_kernel_last_feed_and_initial(d, b, token, debt)
                assert all((x.consumed and (not x.measurements) for _, _, x in token.rows))
                return result
            u = token.u
            if j <= 24:
                low = u[0]
                target = u[1:]
                sign = token.history[j]
                cur = token.P[23 - j] if j < 24 else None
                carry = d._feed_carry(b, v, low, cur, sign)
                d._frame(b, sign, target)
                d._leading_offset(b, target, inverse=True)
                released = d.inverse_add(b, v[1:], target, debt, carry_in=carry, dirty_wires=d._dirty(token), carry_lifecycle=(lambda value: d._feed_erase(b, value, v, low, cur, sign), lambda: d._feed_carry(b, v, low, cur, sign)))
                d._frame(b, sign, target)
                assert released
                if cur is not None:
                    b.cx(cur, low)
                b.cx(sign, low)
                b.cx(v[0], low)
                token.P[24 - j] = low
                token.u = target + [sign]
                del token.history[j]
            else:
                b.cx(v[0], u[0])
                sign = u[0]
                target = u[k + 1:]
                d._frame(b, sign, target)
                d._leading_offset(b, target, inverse=True)
                d.inverse_add(b, v[k + 1:], target, debt, carry_in=v[k], dirty_wires=d._dirty(token))
                d._frame(b, sign, target)
                token.u = u[1:] + u[:1]
            assert debt.consumed and (not debt.measurements) and (b.num_allocated_qubits == 43)
        raise AssertionError('The final row was not reached')

# work/c10/narrow/arithmetic_round2/research/product_coefficient/native_transfer.py
def _initialize__c31_native_transfer():
    global _c31_native_transfer_COMPONENT_CONTRACT, _c31_native_transfer_INTEGRATED_ROOT, _c31_native_transfer__IntegratedPath, _c31_native_transfer___file__, _c31_native_transfer___name__, _c31_native_transfer_coefficient_inverse, _c31_native_transfer_inverse_low6
    'Own coefficient-top transfer; the unchanged baseline is supplied explicitly.\n\nOnly the accepted7-bit coefficient inverse is adapted. Original forward\ncarry records, the quantum incoming source carry and all other owners are\npreserved or explicitly consumed. No phase endpoint or table code is changed.\n'
    _c31_native_transfer__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/product_coefficient/native_transfer.py', False).Path
    _c31_native_transfer_INTEGRATED_ROOT = _c31_native_transfer__IntegratedPath(_c31_native_transfer___file__).resolve().parents[6]

    def _c31_native_transfer_inverse_low6(builder, source, target, debt, *, carry_in, top_outcome, ar, omit_wrap=False):
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

    def _c31_native_transfer_coefficient_inverse(builder, v, D, H, token, dirty, *, baseline, omit_wrap=False, omit_saved=False):
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
            _c31_native_transfer_inverse_low6(builder, S[k + 1:], D[:6], token.row_debts[i], carry_in=carry, top_outcome=phase, ar=ar, omit_wrap=omit_wrap)
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
    _c31_native_transfer_COMPONENT_CONTRACT = dict(original_window=7, shortened_window=6, source_extents=[1, 2, 3, 4, 5], original_debt_positions=[1, 2, 3, 4, 5], forward_passes_E=[41, 41], inverse_E=36, total_E=118, baseline_total_E=123, saving_E=5, production_inverse_entry=40, production_inverse_peak=45, production_inverse_return=39, extra_top_transfer_CX=2, new_external_phase_debts=0)

# work/c10/narrow/arithmetic_round2/research/product_coefficient/native_v3/adapter.py
def _initialize__c32_adapter():
    global _c32_adapter_COMPONENT_CONTRACT, _c32_adapter_INTEGRATED_ROOT, _c32_adapter__IntegratedPath, _c32_adapter___file__, _c32_adapter___name__, _c32_adapter_product_inverse, _c32_adapter_restore_v3
    'AR005: retire raw v3 only while the consuming product is inverted.\n\nThe immutable baseline supplies the arithmetic and seed conventions. The\ncaller must pass its mutable root-owner list: v[3] changes physical identity.\nNo phase debt escapes the adapter, and the original seed token is untouched.\n'
    _c32_adapter__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/product_coefficient/native_v3/adapter.py', False).Path
    _c32_adapter_INTEGRATED_ROOT = _c32_adapter__IntegratedPath(_c32_adapter___file__).resolve().parents[7]

    def _c32_adapter_restore_v3(builder, v, seed, outcome, *, omit_phase=False, omit_linear_c=False, trace=None):
        assert v[3] is None and len(seed) == 6
        a, b, c = v[:3]
        assert a is not None and b is not None and (c is not None)
        q = builder.alloc_qubits(1)[0]
        builder.x(q)
        builder.cx(seed[5], q)
        if not omit_linear_c:
            builder.cx(c, q)
        builder.cx(c, a)
        builder.cx(c, b)
        builder.ccx(a, b, q)
        builder.cx(c, b)
        builder.cx(c, a)
        builder.push_condition(outcome)
        if not omit_phase:
            builder.z(q)
        builder.pop_condition()
        builder.free(outcome)
        v[3] = q
        if trace is not None:
            trace.append(dict(stage='raw_v3_restored_and_phase_paid', live=builder.num_allocated_qubits, current_v3=str(q), phase_omitted=omit_phase))
        return q

    def _c32_adapter_product_inverse(builder, v, D, word, token, dirty, *, baseline, omit_v3_phase=False, omit_original_debt=None, omit_linear_c=False, trace=None):
        """Return seed6/h10 and replace v[3] with its fresh restored owner.

Production requires all omission arguments at their defaults. They exist
solely for negative component proofs. Dirty spectators must name the actual
44-owner entry chart, including the original live v3 exactly once.
"""
        km = baseline.km
        assert isinstance(v, list) and len(v) == 12
        assert builder.max_qubits == 48 and builder.num_allocated_qubits == 44
        D, word, dirty = (list(D), list(word), list(dirty))
        assert len(D) == 13 and len(word) == 16 and (len(token.rows) == 10)
        assert len(dirty) == 15 and len(set(D + word + dirty)) == 44
        assert all((not debt.consumed for debt in token.rows))
        old_v3 = v[3]
        assert isinstance(old_v3, km.q) and dirty.count(old_v3) == 1
        assert all((v[i] is not None for i in (0, 1, 2, 3, 4, 8, 10)))
        assert all((v[i] is None for i in (5, 6, 7, 9, 11)))
        m3 = builder.alloc_bits(1)[0]
        builder.hmr(old_v3, m3)
        builder.free(old_v3)
        v[3] = None
        dirty = [q for q in dirty if q != old_v3]
        assert len(dirty) == 14 and builder.num_allocated_qubits == 43
        if trace is not None:
            trace.append(dict(stage='raw_v3_retired', live=43, retired_physical=str(old_v3), actual_measurement=str(m3), dirty=list(map(str, dirty))))
        C = [False] + D
        builder.x(word[15])
        for i in reversed(range(10)):
            debt = token.rows[i]
            if omit_original_debt is not None and i == omit_original_debt[0]:
                position = omit_original_debt[1]
                assert position in debt.measurements
                builder.free(debt.measurements.pop(position))
            q = word[6 + i]
            target = word[:6 + i]
            source = C[9 - i:] if i < 9 else C
            for t in target:
                builder.cx(q, t)
            carry = baseline._product_carry(builder, C, q, i)
            regenerations = []

            def erase(value):
                assert i < 8 and value != q
                baseline._clear_product_carry(builder, C, q, i, value)

            def regenerate():
                assert i < 8
                value = baseline._product_carry(builder, C, q, i)
                regenerations.append(str(value))
                return value
            released = baseline.product_ar.inverse_add(builder, source, target, debt, carry_in=carry, dirty_wires=dirty + word[6:], carry_lifecycle=(erase, regenerate) if i < 8 else None)
            if not released:
                baseline._clear_product_carry(builder, C, q, i, carry)
            if i == 8:
                assert carry is False and (not released)
            if i == 9:
                assert carry == q and (not released)
            for t in target:
                builder.cx(q, t)
            assert debt.consumed and (not debt.measurements)
            assert builder.num_allocated_qubits == 43
            if trace is not None:
                trace.append(dict(stage=f'inverse_row_{i}', live=43, original_debt_consumed=True, owned_carry_released=bool(released), conditional_regenerations=len(regenerations)))
        builder.x(word[15])
        seed, h = (word[:6], word[6:])
        _c32_adapter_restore_v3(builder, v, seed, m3, omit_phase=omit_v3_phase, omit_linear_c=omit_linear_c, trace=trace)
        assert builder.num_allocated_qubits == 44
        assert len(set(D + word + dirty + [v[3]])) == 44
        assert all((debt.consumed and (not debt.measurements) for debt in token.rows))
        return (seed, h)
    _c32_adapter_COMPONENT_CONTRACT = dict(Q=48, entry_data=44, inverse_data=43, return_data=44, forward_product_E=103, inverse_product_E=124.5, restored_v3_E=1, product_and_recovery_E=228.5, AR002_comparator_E=238, saving_E=9.5, mutable_v3_physical_handle=True, protected_seed_token_untouched=True, new_external_phase_debts=0, measured_v3_phase_paid_on_current_wire=True, AR002_known_zero_row_not_added=True, all_original_product_debts_consumed=True, row8_false_and_row9_alias_preserved=True)

# work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py
def _initialize__c33_normalization9475():
    global _c33_normalization9475_ACCEPTANCE, _c33_normalization9475_ACCEPTANCE_SHA, _c33_normalization9475_CONTRACT, _c33_normalization9475_CONTROLS, _c33_normalization9475_FORWARD_ROWS, _c33_normalization9475_FRAME, _c33_normalization9475_HERE, _c33_normalization9475_INTEGRATED_ROOT, _c33_normalization9475_MASKS, _c33_normalization9475_MAX_X, _c33_normalization9475_NARROW, _c33_normalization9475_Path, _c33_normalization9475__IntegratedPath, _c33_normalization9475___file__, _c33_normalization9475___name__, _c33_normalization9475_cb, _c33_normalization9475_checked, _c33_normalization9475_forward, _c33_normalization9475_hashlib, _c33_normalization9475_importlib, _c33_normalization9475_inverse, _c33_normalization9475_joint_last_phase, _c33_normalization9475_json, _c33_normalization9475_km, _c33_normalization9475_measured, _c33_normalization9475_old, _c33_normalization9475_path, _c33_normalization9475_prefix_phase, _c33_normalization9475_prepare, _c33_normalization9475_route_lane, _c33_normalization9475_spec, _c33_normalization9475_sys, _c33_normalization9475_thermometer_matrix
    'Direct normalization94.75 emitter; no inherited module or source patching.'
    _c33_normalization9475__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', False).Path
    _c33_normalization9475_INTEGRATED_ROOT = _c33_normalization9475__IntegratedPath(_c33_normalization9475___file__).resolve().parents[7]
    _c33_normalization9475_Path = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', False).Path
    _c33_normalization9475_hashlib = _import_component('hashlib', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', True)
    _c33_normalization9475_importlib = _import_component('importlib.util', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', True)
    _c33_normalization9475_json = _import_component('json', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', True)
    _c33_normalization9475_sys = _import_component('sys', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', True)
    _c33_normalization9475_HERE = _c33_normalization9475_Path(_c33_normalization9475___file__).resolve().parent
    _c33_normalization9475_NARROW = _c33_normalization9475_HERE.parents[3]
    _c33_normalization9475_ACCEPTANCE = _c33_normalization9475_NARROW / 'arithmetic_round2/receipts/NORMALIZATION9475_PAPER_ACCEPTED.json'
    _c33_normalization9475_ACCEPTANCE_SHA = 'c6e795219c98415c078c010023004def1a76b2785779955c95d1f4f3c62f40bd'

    def _c33_normalization9475_checked(path, digest):
        raw = _read_bytes(path)
        pass
        return _json_loads(raw)
    pass
    pass
    _c33_normalization9475_path = _c33_normalization9475_NARROW / 'research/quantized_producer/pair_normalization.py'
    pass
    _c33_normalization9475_spec = _spec('_round2_rn2df_private_pair_normalizer', _c33_normalization9475_path)
    _c33_normalization9475_old = _new_module(_c33_normalization9475_spec)
    _c33_normalization9475_sys.modules[_c33_normalization9475_spec.name] = _c33_normalization9475_old
    _c33_normalization9475_spec.loader.exec_module(_c33_normalization9475_old)
    _c33_normalization9475_km, _c33_normalization9475_cb = (_c33_normalization9475_old.km, _c33_normalization9475_old.cb)
    _c33_normalization9475_MAX_X = _c33_normalization9475_old.MAX_X
    _c33_normalization9475_thermometer_matrix = _import_component('thermometer_cleanup', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', False).thermometer_matrix
    _c33_normalization9475_FORWARD_ROWS = tuple(_c33_normalization9475_thermometer_matrix(10))
    assert tuple((j for j, row in enumerate(_c33_normalization9475_FORWARD_ROWS, 1) if row >> 6 & 1)) == (1, 3, 5, 7)
    _c33_normalization9475_MASKS = tuple(range(1, 9))
    _c33_normalization9475_FRAME = [['cx', 7, 6], ['cx', 7, 5], ['cx', 7, 4], ['cx', 7, 3], ['cx', 7, 2], ['cx', 7, 1], ['cx', 7, 0], ['cx', 6, 4], ['cx', 6, 2], ['cx', 6, 0], ['cx', 5, 4], ['cx', 5, 1], ['cx', 5, 0], ['cx', 4, 0], ['cx', 3, 2], ['cx', 3, 1], ['cx', 3, 0], ['cx', 2, 0], ['cx', 1, 0]]
    _c33_normalization9475_CONTROLS = [{'first': 0, 'second': 1, 'terms': [1, 2, 3, 4, 5, 6, 7, 8]}, {'first': 2, 'second': 3, 'terms': [1, 2, 3, 4, 5, 6, 7, 8]}, {'first': 4, 'second': 5, 'terms': [1, 2, 3, 4, 5, 6, 7, 8]}, {'first': 6, 'second': 7, 'terms': [1, 2, 3, 4, 5, 6, 7, 8]}, {'first': 8, 'second': 9, 'terms': [1, 2, 3, 4, 5, 6, 7, 8]}, {'first': 0, 'second': 2, 'terms': [1, 3, 5, 7]}, {'first': 1, 'second': 3, 'terms': [2, 4, 6, 8]}, {'first': 4, 'second': 6, 'terms': [1, 3, 5, 7]}, {'first': 5, 'second': 7, 'terms': [2, 4, 6, 8]}, {'first': 8, 'second': 10, 'terms': [1, 3, 5, 7]}, {'first': 0, 'second': 4, 'terms': [1, 5]}, {'first': 1, 'second': 5, 'terms': [2, 6]}, {'first': 2, 'second': 6, 'terms': [3, 7]}, {'first': 3, 'second': 7, 'terms': [4, 8]}, {'first': 0, 'second': 8, 'terms': [1]}, {'first': 1, 'second': 9, 'terms': [2]}, {'first': 2, 'second': 10, 'terms': [3]}]

    def _c33_normalization9475_route_lane(builder, lane, T):
        count = 0
        for op in _c33_normalization9475_old.operations(len(lane)):
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

    def _c33_normalization9475_forward(builder, x, flags):
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
        _c33_normalization9475_route_lane(builder, x[0::2], T)
        _c33_normalization9475_route_lane(builder, x[1:21:2], T)
        builder.x(x[20])
        builder.cx(x[21], x[20])
        for j in range(1, 11):
            q = P[2 * j - 2]
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            if j == 1:
                _c33_normalization9475_cb.emit_phase(builder, [T[0], x[21]], m, _c33_normalization9475_old.ODD_FIRST)
            else:
                _c33_normalization9475_cb.emit_phase(builder, [T[j - 2], T[j - 1], x[21]], m, _c33_normalization9475_old.ODD_OTHER)
            builder.free(m)
            builder.free(q)
        parity = builder.alloc_bits(1)[0]
        builder.bit_store(parity, False)
        for q, row in zip(T, _c33_normalization9475_FORWARD_ROWS):
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

    def _c33_normalization9475_prepare(builder, flags):
        monomials = {1 << i: q for i, q in enumerate(flags)}
        helpers = []
        for mask in _c33_normalization9475_MASKS:
            if mask in monomials:
                continue
            low = mask & -mask
            q = builder.alloc_qubits(1)[0]
            builder.ccx(monomials[mask ^ low], monomials[low], q)
            monomials[mask] = q
            helpers.append(q)
        assert len(helpers) == 4
        wires = [monomials[m] for m in _c33_normalization9475_MASKS]
        for name, a, b in _c33_normalization9475_FRAME:
            if name == 'cx':
                builder.cx(wires[a], wires[b])
            else:
                builder.swap(wires[a], wires[b])
        return (dict(zip(range(1, 9), wires)), helpers)

    def _c33_normalization9475_measured(builder, q, role=None):
        outcome = builder.alloc_bits(1)[0]
        if role is not None and hasattr(builder, 'select_outcome'):
            builder.select_outcome(outcome, role)
        builder.hmr(q, outcome)
        return outcome

    def _c33_normalization9475_prefix_phase(builder, outcome, previous, a, b):
        builder.push_condition(outcome)
        builder.z(previous)
        builder.cz(previous, a)
        builder.cz(previous, b)
        builder.ccz(previous, a, b)
        builder.pop_condition()

    def _c33_normalization9475_joint_last_phase(builder, x, mB, m3, *, omit_final_helper_fix=False):
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

    def _c33_normalization9475_inverse(builder, x, flags, *, omit_final_helper_fix=False):
        x, flags = (list(x), list(flags))
        T, helpers = _c33_normalization9475_prepare(builder, flags)
        for operation in reversed(_c33_normalization9475_CONTROLS):
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
        mB = _c33_normalization9475_measured(builder, T.pop(2), 'B')
        _c33_normalization9475_prefix_phase(builder, mB, T[9], x[2], x[3])
        for j in reversed(range(4, 10)):
            outcome = _c33_normalization9475_measured(builder, T[j])
            _c33_normalization9475_prefix_phase(builder, outcome, T[j - 1], x[22 - 2 * j], x[23 - 2 * j])
            builder.free(outcome)
        m3 = _c33_normalization9475_measured(builder, T[3], 'T3')
        builder.free(_c33_normalization9475_km.array(helpers))
        _c33_normalization9475_joint_last_phase(builder, x, mB, m3, omit_final_helper_fix=omit_final_helper_fix)
        builder.free(mB)
        builder.free(m3)
    _c33_normalization9475_CONTRACT = dict(component_E=94.75, forward_E=51.5, inverse_E=43.25, local_peak=46, global_Q=48, forward_boundary_owners=26, inverse_boundary_owners=26, T=0, R=0, exact_numeric_phase_change=0, protected_phase_loaders_unchanged=True)

# work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py
def _initialize__c34_root192():
    global _c34_root192_ENGINE, _c34_root192_HERE, _c34_root192_INTEGRATED_ROOT, _c34_root192_NARROW, _c34_root192_ORIGINAL_FORWARD, _c34_root192_ORIGINAL_INVERSE, _c34_root192_ORIGINAL_ROOT_STEP, _c34_root192_Path, _c34_root192__IntegratedPath, _c34_root192___file__, _c34_root192___name__, _c34_root192__a2_xor, _c34_root192__carry_frame, _c34_root192__p_frame, _c34_root192__private, _c34_root192_arithmetic, _c34_root192_arr, _c34_root192_carry_clear, _c34_root192_carry_prepare, _c34_root192_convert_high, _c34_root192_forward, _c34_root192_hashlib, _c34_root192_importlib, _c34_root192_initial_low_xor, _c34_root192_inverse, _c34_root192_json, _c34_root192_km, _c34_root192_last_step, _c34_root192_original, _c34_root192_sys
    'Root192 direct native emitter; immutable private helper modules only.\n\nNo inherited source/module is patched. forward/inverse preserve the same\nnorm22 owner interface and leave every exponent spectator untouched.\n'
    _c34_root192__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', False).Path
    _c34_root192_INTEGRATED_ROOT = _c34_root192__IntegratedPath(_c34_root192___file__).resolve().parents[7]
    _c34_root192_Path = _import_component('pathlib', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', False).Path
    _c34_root192_hashlib = _import_component('hashlib', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', True)
    _c34_root192_importlib = _import_component('importlib.util', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', True)
    _c34_root192_json = _import_component('json', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', True)
    _c34_root192_sys = _import_component('sys', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', True)
    _c34_root192_HERE = _c34_root192_Path(_c34_root192___file__).resolve().parent
    _c34_root192_NARROW = _c34_root192_HERE.parents[3]
    pass
    _c34_root192_ENGINE = _c34_root192_NARROW / 'checkpoint002/cleanroom/baseline_stage97/engine'
    _c34_root192_sys.path[:0] = [str(_c34_root192_NARROW / 'base/official/kickmix'), str(_c34_root192_ENGINE)]
    _c34_root192_km = _import_component('kickmix', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', False)

    def _c34_root192__private(name, path, expected):
        pass
        spec = _spec(name, path)
        module = _new_module(spec)
        _c34_root192_sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    _c34_root192_original = _c34_root192__private('_round2_rn3_immutable_odd_sqrt', _c34_root192_NARROW / 'checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', '0a60a631cb97dc39ea0e76e7ab2dc26300fd4f96218a73e0e56262c59586c144')
    _c34_root192_arithmetic = _c34_root192__private('fusion._round2_rn3_immutable_arithmetic', _c34_root192_ENGINE / 'fusion/arithmetic.py', '154621ee98dd8139eab601d5d794be881a5ebf38ebe1c542cf69b8fb97ee1453')
    _c34_root192_original.add = _c34_root192_arithmetic.add
    _c34_root192_ORIGINAL_ROOT_STEP = _c34_root192_original._root_step
    _c34_root192_ORIGINAL_FORWARD = _c34_root192_original.forward
    _c34_root192_ORIGINAL_INVERSE = _c34_root192_original.inverse

    def _c34_root192_arr(wires):
        return _c34_root192_km.array(list(wires))

    def _c34_root192_last_step(builder, remainder, older, b, *, initial=False, inverse=False):
        """The inherited j11 zero-pair rule plus the new j12 carry alias."""
        remainder = list(remainder)
        older = list(older)
        j = len(remainder) - 3
        if j < 11:
            return _c34_root192_ORIGINAL_ROOT_STEP(builder, remainder, older, b, initial=initial, inverse=inverse)
        assert j in (11, 12) and (not initial) and isinstance(b, _c34_root192_km.q)
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
        builder.cx(b, _c34_root192_arr(high))
        if inverse:
            _c34_root192_original._add_leading_one(builder, high, inverse=True)
        if j == 12:
            builder.cx(b, high[0])
            builder.cx(older[0], high[0])
            _c34_root192_original.add(builder, older[1:], high[1:], carry_in=older[0], subtract=inverse)
        else:
            _c34_root192_original.add(builder, older, high, carry_in=b, subtract=inverse)
        if not inverse:
            _c34_root192_original._add_leading_one(builder, high)
        builder.cx(b, _c34_root192_arr(high))
        if inverse:
            builder.x(low[0])
            builder.x(low[1])

    def _c34_root192_initial_low_xor(builder, Q, low):
        """The preconversion low word is (1,1,1,1 xor Q1 xor Q2)."""
        builder.x(_c34_root192_arr(low))
        builder.cx(Q[1], low[3])
        builder.cx(Q[2], low[3])

    def _c34_root192__p_frame(builder, Q):
        builder.cx(Q[2], Q[0])
        builder.cx(Q[2], Q[1])

    def _c34_root192__carry_frame(builder, Q, p):
        builder.x(Q[3])
        for q in Q[:3]:
            builder.cx(q, Q[3])
        builder.x(p)
        builder.cx(Q[0], p)
        builder.cx(Q[2], p)

    def _c34_root192__a2_xor(builder, Q, target):
        builder.x(target)
        for q in Q[:3]:
            builder.cx(q, target)

    def _c34_root192_carry_prepare(builder, Q):
        p, c = builder.alloc_qubits(2)
        _c34_root192__p_frame(builder, Q)
        builder.ccx(Q[0], Q[1], p)
        _c34_root192__p_frame(builder, Q)
        _c34_root192__a2_xor(builder, Q, c)
        _c34_root192__carry_frame(builder, Q, p)
        builder.ccx(Q[3], p, c)
        _c34_root192__carry_frame(builder, Q, p)
        return (p, c)

    def _c34_root192_carry_clear(builder, Q, p, c):
        _c34_root192__a2_xor(builder, Q, c)
        _c34_root192__carry_frame(builder, Q, p)
        builder.del_and(Q[3], p, c)
        _c34_root192__carry_frame(builder, Q, p)
        builder.free(c)
        _c34_root192__p_frame(builder, Q)
        builder.del_and(Q[0], Q[1], p)
        _c34_root192__p_frame(builder, Q)
        builder.free(p)

    def _c34_root192_convert_high(builder, Q, high, *, inverse=False):
        p, c = _c34_root192_carry_prepare(builder, Q)
        builder.cx(Q[0], _c34_root192_arr(high))
        if inverse:
            _c34_root192_original._add_leading_one(builder, high, inverse=True)
        _c34_root192_original.add(builder, Q[4:], high, carry_in=c, subtract=inverse)
        if not inverse:
            _c34_root192_original._add_leading_one(builder, high)
        builder.cx(Q[0], _c34_root192_arr(high))
        _c34_root192_carry_clear(builder, Q, p, c)

    def _c34_root192_forward(builder, norm):
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
            _c34_root192_last_step(builder, remainder, older, b, initial=j == 1)
        b = remainder[-1]
        builder.x(b)
        Q = [b] + roots
        W = remainder[:-1]
        _c34_root192_initial_low_xor(builder, Q, W[:4])
        builder.free(_c34_root192_arr(W[:4]))
        _c34_root192_convert_high(builder, Q, W[4:])
        assert Q == norm[10:] and W[4:] == norm[:10]
        return dict(root=Q, residual=W[4:])

    def _c34_root192_inverse(builder, norm):
        norm = list(norm)
        Q = norm[10:]
        high = norm[:10]
        _c34_root192_convert_high(builder, Q, high, inverse=True)
        low = list(builder.alloc_qubits(4))
        _c34_root192_initial_low_xor(builder, Q, low)
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
            _c34_root192_last_step(builder, remainder, older, b, initial=j == 1, inverse=True)
            if j == 1:
                remainder = remainder[2:]
            else:
                remainder = remainder[2:] + [b]
                builder.x(b)
                roots = older
            if j >= 11:
                builder.free(_c34_root192_arr(pair))
            else:
                assert pair == norm[20 - 2 * j:22 - 2 * j]
        assert remainder == norm[20:] and (not roots)
        builder.cx(norm[20], norm[21])
        builder.x(norm[20])
        return norm

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py
def _initialize__c35_branch_prover():
    global _c35_branch_prover_Callable, _c35_branch_prover_Fraction, _c35_branch_prover_INTEGRATED_ROOT, _c35_branch_prover_Mapping, _c35_branch_prover_Operation, _c35_branch_prover_Program, _c35_branch_prover_Sequence, _c35_branch_prover__IntegratedPath, _c35_branch_prover___file__, _c35_branch_prover___name__, _c35_branch_prover_annotations, _c35_branch_prover_dataclass, _c35_branch_prover_exhaustively_check, _c35_branch_prover_generated_text, _c35_branch_prover_integer_bits, _c35_branch_prover_integer_of, _c35_branch_prover_io, _c35_branch_prover_itertools, _c35_branch_prover_math, _c35_branch_prover_shlex, _c35_branch_prover_symbolic_check
    'Independent exhaustive checker for small generated kickmix windows.\n\nCopyright 2026 Syed Asad Ali (team syed3000)\nLicensed under the Apache License, Version 2.0.\n\nNo compiled reference circuit is loaded here.  Pass the text emitted by our own\ngenerator.  The checker assigns every input and every syntactic HMR outcome,\ntracks exact rational phase in half turns, and checks the final state.  An R is\naccepted only on a provably zero qubit, which makes every possible discarded\nmeasurement outcome harmless.  This deliberate restriction catches accidental\nuse of reset as irreversible erasure.\n\nFor computational basis t, an HMR with outcome m contributes (-1)**(m*t)\nbefore resetting t.  The checker implements this directly, independently of\nkickmix.  Inactive conditional HMRs consume their reserved transcript bit but\ndo nothing; enumeration therefore covers every possible active transcript.\n'
    pass
    _c35_branch_prover__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', False).Path
    _c35_branch_prover_INTEGRATED_ROOT = _c35_branch_prover__IntegratedPath(_c35_branch_prover___file__).resolve().parents[7]
    _c35_branch_prover_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', False).dataclass
    _c35_branch_prover_Fraction = _import_component('fractions', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', False).Fraction
    _c35_branch_prover_io = _import_component('io', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', True)
    _c35_branch_prover_itertools = _import_component('itertools', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', True)
    _c35_branch_prover_math = _import_component('math', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', True)
    _c35_branch_prover_shlex = _import_component('shlex', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', True)
    _c35_branch_prover_Callable = _import_component('typing', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', False).Callable
    _c35_branch_prover_Mapping = _import_component('typing', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', False).Mapping
    _c35_branch_prover_Sequence = _import_component('typing', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', False).Sequence

    @_c35_branch_prover_dataclass(frozen=True)
    class _c35_branch_prover_Operation:
        kind: str
        arguments: tuple[str, ...]
        condition: str | None = None
        half_turns: Fraction | None = None
        event: int | None = None

    def _c35_branch_prover_generated_text(circuit) -> str:
        """Serialize a circuit produced by this task; never takes a reference path."""
        stream = _c35_branch_prover_io.StringIO()
        circuit.to_file(stream, format='kmx')
        return stream.getvalue()

    class _c35_branch_prover_Program:
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
                tokens = _c35_branch_prover_shlex.split(line, comments=True)
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
                    angle = _c35_branch_prover_Fraction(arguments[-1])
                    arguments = arguments[:-1]
                    denominators.append(angle.denominator)
                event = None
                if kind == 'HMR':
                    event = self.measurements
                    self.measurements += 1
                self.wires.update(arguments)
                self.operations.append(_c35_branch_prover_Operation(kind, tuple(arguments), condition, angle, event))
            self.denominator = _c35_branch_prover_math.lcm(*denominators)
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
                    phase += den * _c35_branch_prover_math.prod((state[wire] for wire in a))
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
            return (state, _c35_branch_prover_Fraction(phase % self.modulus, den))

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
                    coefficient *= _c35_branch_prover_math.prod((state[wire] for wire in args))
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
            return (state, {monomial: _c35_branch_prover_Fraction(coefficient, den) for monomial, coefficient in phase.items()})

    def _c35_branch_prover_exhaustively_check(program: _c35_branch_prover_Program, input_wires: _c35_branch_prover_Sequence[str], expected: _c35_branch_prover_Callable[[_c35_branch_prover_Mapping[str, int]], tuple[_c35_branch_prover_Mapping[str, int], _c35_branch_prover_Fraction]], *, initial_constants: _c35_branch_prover_Mapping[str, int] | None=None, valid_input: _c35_branch_prover_Callable[[_c35_branch_prover_Mapping[str, int]], bool] | None=None, max_cases: int=1 << 22):
        """Check output bits, zero scratch, and exact phase for every HMR outcome.

    `expected` returns the complete nonzero-capable output wire mapping and the
    ideal phase in half turns. All quantum wires absent from the mapping must
    be zero. Classical bits are checked only if included explicitly.
    """
        total = 1 << len(input_wires) + program.measurements
        if total > max_cases:
            raise ValueError(f'Exhaustive request has {total:,} cases > {max_cases:,}')
        tested = 0
        accepted_inputs = 0
        for bits in _c35_branch_prover_itertools.product((0, 1), repeat=len(input_wires)):
            initial = dict(initial_constants or {})
            initial.update(zip(input_wires, bits))
            if valid_input is not None and (not valid_input(initial)):
                continue
            accepted_inputs += 1
            wanted, ideal_phase = expected(initial)
            ideal_phase %= 2
            for transcript in range(1 << program.measurements):
                final, phase = program.execute(initial, transcript)
                for wire in set(program.quantum_wires) | set(wanted):
                    if final.get(wire, 0) != wanted.get(wire, 0):
                        raise AssertionError(f'Output mismatch {wire}: got {final.get(wire, 0)}, expected {wanted.get(wire, 0)}; input={initial}, HMR transcript={transcript}')
                if phase != ideal_phase:
                    raise AssertionError(f'Phase mismatch: got {phase} half turns, expected {ideal_phase}; input={initial}, HMR transcript={transcript}')
                tested += 1
        return {'inputs': accepted_inputs, 'hmr_events': program.measurements, 'outcomes_per_input': 1 << program.measurements, 'cases': tested, 'status': 'PROVED'}

    def _c35_branch_prover_integer_of(state, wires):
        return sum((state.get(wire, 0) << bit for bit, wire in enumerate(wires)))

    def _c35_branch_prover_integer_bits(value, wires):
        return {wire: value >> bit & 1 for bit, wire in enumerate(wires)}

    def _c35_branch_prover_symbolic_check(program, input_wires, expected, *, initial_constants=None, valid_input=None):
        """Enumerate data inputs and symbolically prove every measurement outcome."""
        inputs = 0
        for bits in _c35_branch_prover_itertools.product((0, 1), repeat=len(input_wires)):
            initial = dict(initial_constants or {})
            initial.update(zip(input_wires, bits))
            if valid_input is not None and (not valid_input(initial)):
                continue
            inputs += 1
            wanted, ideal_phase = expected(initial)
            state, phase = program.execute_symbolic_measurements(initial)
            for wire in set(program.quantum_wires) | set(wanted):
                if state.get(wire, 0) != wanted.get(wire, 0):
                    raise AssertionError(f'Output mismatch at {wire}; input={initial}')
            ideal_phase %= 2
            expected_poly = {0: ideal_phase} if ideal_phase else {}
            if phase != expected_poly:
                raise AssertionError(f'Nonzero phase polynomial {phase}, expected {expected_poly}; input={initial}')
        return {'status': 'PROVED', 'inputs': inputs, 'hmr_events': program.measurements, 'outcomes_per_input': 1 << program.measurements, 'symbolically_proved_cases': inputs * (1 << program.measurements)}

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py
def _initialize__c36_codebook():
    global _c36_codebook_BinarySpan, _c36_codebook_Codebook, _c36_codebook_INTEGRATED_ROOT, _c36_codebook_QuadraticCodePlan, _c36_codebook__IntegratedPath, _c36_codebook___file__, _c36_codebook___name__, _c36_codebook_annotations, _c36_codebook_bits, _c36_codebook_dataclass, _c36_codebook_emit_erase, _c36_codebook_emit_phase, _c36_codebook_emit_xor, _c36_codebook_factor_polynomial, _c36_codebook_pack_bits, _c36_codebook_parity_function, _c36_codebook_random, _c36_codebook_word_functions
    'Exact synthesis on a mathematical coefficient codebook.\n\nAll inputs are truth tables produced by the coefficient fitter, never compiled\ncircuits. A quadratic representation need only agree on the supplied reachable\ncodewords. Its emitted XOR circuit is nevertheless an exact Boolean polynomial\non every wire assignment. HMR deletion is exact for either outcome because the\nsame polynomial is used to repay its complete phase.\n'
    pass
    _c36_codebook__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py', False).Path
    _c36_codebook_INTEGRATED_ROOT = _c36_codebook__IntegratedPath(_c36_codebook___file__).resolve().parents[7]
    _c36_codebook_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py', False).dataclass
    _c36_codebook_random = _import_component('random', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py', True)

    def _c36_codebook_bits(value):
        while value:
            bit = value & -value
            yield (bit.bit_length() - 1)
            value ^= bit

    class _c36_codebook_BinarySpan:

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

    def _c36_codebook_pack_bits(values):
        return sum(((int(value) & 1) << i for i, value in enumerate(values)))

    def _c36_codebook_word_functions(values, width):
        values = list(values)
        return [_c36_codebook_pack_bits((value >> bit for value in values)) for bit in range(width)]

    def _c36_codebook_parity_function(mask, functions):
        out = 0
        for bit in _c36_codebook_bits(mask):
            out ^= functions[bit]
        return out

    @_c36_codebook_dataclass(frozen=True)
    class _c36_codebook_QuadraticCodePlan:
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
            out ^= _c36_codebook_parity_function(self.linear, functions)
            for i, j in self.edges:
                out ^= functions[i] & functions[j]
            return out

        def evaluate_factored_functions(self, functions, full):
            out = full if self.constant else 0
            out ^= _c36_codebook_parity_function(self.product_linear, functions)
            for left, right, i, j in self.products:
                if not (left >> i & 1 and right >> j & 1) or left >> j & 1 or right >> i & 1:
                    raise AssertionError('Product factors do not admit the declared CNOT frames.')
                out ^= _c36_codebook_parity_function(left, functions) & _c36_codebook_parity_function(right, functions)
            return out

    def _c36_codebook_factor_polynomial(width, constant, linear, edges):
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
            for a in _c36_codebook_bits(left):
                for b in _c36_codebook_bits(right):
                    if a == b:
                        affine ^= 1 << a
                    else:
                        edge = tuple(sorted((a, b)))
                        if edge in edges:
                            edges.remove(edge)
                        else:
                            edges.add(edge)
            products.append((left, right, i, j))
        return _c36_codebook_QuadraticCodePlan(width, bool(constant), int(linear), original_edges, tuple(products), affine)

    class _c36_codebook_Codebook:

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
            self.span = _c36_codebook_BinarySpan(self.columns)

        def decode_expression(self, expression):
            constant, linear, edges = (False, 0, [])
            for index in _c36_codebook_bits(expression):
                monomial = self.monomials[index]
                if not monomial:
                    constant = not constant
                elif len(monomial) == 1:
                    linear ^= 1 << monomial[0]
                else:
                    edges.append(monomial)
            return _c36_codebook_factor_polynomial(self.width, constant, linear, edges)

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
            rng = _c36_codebook_random.Random(seed)
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
                left_functions = [_c36_codebook_parity_function(mask, self.functions) for mask in factors]
                columns += [left & right for left in left_functions for right in self.functions]
                solution = _c36_codebook_BinarySpan(columns).solve(target)
                if solution is None:
                    continue
                constant = bool(solution & 1)
                linear = solution >> 1 & (1 << self.width) - 1
                edge_set = set()
                for i, left in enumerate(factors):
                    right = solution >> 1 + self.width + i * self.width & (1 << self.width) - 1
                    for a in _c36_codebook_bits(left):
                        for b in _c36_codebook_bits(right):
                            if a == b:
                                linear ^= 1 << a
                            else:
                                edge = tuple(sorted((a, b)))
                                if edge in edge_set:
                                    edge_set.remove(edge)
                                else:
                                    edge_set.add(edge)
                candidate = _c36_codebook_factor_polynomial(self.width, constant, linear, edge_set)
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
            rng = _c36_codebook_random.Random(seed)
            rng.shuffle(relations)
            width = self.width

            def adjacency(value):
                rows = [0] * width
                for index in _c36_codebook_bits(value):
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
                    for k in _c36_codebook_bits(remaining):
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
            for bit in _c36_codebook_bits(plan.linear):
                current ^= 1 << lookup[bit,]
            for edge in plan.edges:
                current ^= 1 << lookup[edge]
            width = self.width
            rng = _c36_codebook_random.Random(seed)

            def adjacency(expression):
                rows = [0] * width
                for index in _c36_codebook_bits(expression):
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
                    for k in _c36_codebook_bits(remaining):
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
                kernel = _c36_codebook_BinarySpan(matrix).nullspace
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
                    moves = _c36_codebook_BinarySpan([column & mask for column in columns]).nullspace
                    if len(moves) >= 3:
                        break
                    k -= 1
                if not moves:
                    continue
                if len(moves) > subspace_bits:
                    compressed, span = ([], _c36_codebook_BinarySpan())
                    while len(compressed) < subspace_bits:
                        coefficients = rng.getrandbits(len(moves))
                        if not coefficients or not span.add(coefficients):
                            continue
                        value = 0
                        for bit in _c36_codebook_bits(coefficients):
                            value ^= moves[bit]
                        compressed.append(value)
                    moves = compressed
                deltas = []
                delta_rows = []
                for move in moves:
                    expression = 0
                    for bit in _c36_codebook_bits(move):
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

    def _c36_codebook_emit_xor(builder, variables, target, plan):
        """Emit a factored decoder with zero additional qubits."""
        variables = list(variables)
        if len(variables) != plan.width or target in variables:
            raise ValueError('Distinct input and target wires are required.')
        if plan.constant:
            builder.x(target)
        for bit in _c36_codebook_bits(plan.product_linear):
            builder.cx(variables[bit], target)
        for left, right, i, j in plan.products:
            frame = [(variables[k], variables[i]) for k in _c36_codebook_bits(left) if k != i]
            frame += [(variables[k], variables[j]) for k in _c36_codebook_bits(right) if k != j]
            for a, b in frame:
                builder.cx(a, b)
            builder.ccx(variables[i], variables[j], target)
            for a, b in reversed(frame):
                builder.cx(a, b)

    def _c36_codebook_emit_phase(builder, variables, outcome, plan):
        """Repay (-1)^(outcome * polynomial) using Clifford gates only."""
        variables = list(variables)
        if len(variables) != plan.width:
            raise ValueError('Wrong codebook wire count.')
        if plan.constant:
            builder.z(outcome)
        builder.push_condition(outcome)
        for bit in _c36_codebook_bits(plan.linear):
            builder.z(variables[bit])
        for i, j in plan.edges:
            builder.cz(variables[i], variables[j])
        builder.pop_condition()

    def _c36_codebook_emit_erase(builder, variables, targets, plans):
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
            _c36_codebook_emit_phase(builder, variables, outcome, plan)
        builder.free(outcomes)

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py
def _initialize__c37_cyclic_phase():
    global _c37_cyclic_phase_Fraction, _c37_cyclic_phase_INTEGRATED_ROOT, _c37_cyclic_phase_ThresholdPlan, _c37_cyclic_phase__IntegratedPath, _c37_cyclic_phase___file__, _c37_cyclic_phase___name__, _c37_cyclic_phase__erase_polynomial, _c37_cyclic_phase__helper_candidates, _c37_cyclic_phase__monomials, _c37_cyclic_phase__pow2, _c37_cyclic_phase__restricted_anf, _c37_cyclic_phase__span_solution, _c37_cyclic_phase__truth_of_terms, _c37_cyclic_phase_annotations, _c37_cyclic_phase_compile_polynomial, _c37_cyclic_phase_contextmanager, _c37_cyclic_phase_cyclic_scale_phase, _c37_cyclic_phase_dataclass, _c37_cyclic_phase_itertools, _c37_cyclic_phase_km, _c37_cyclic_phase_lru_cache, _c37_cyclic_phase_math, _c37_cyclic_phase_rotation_pairs, _c37_cyclic_phase_threshold_control, _c37_cyclic_phase_threshold_plan, _c37_cyclic_phase_xor_polynomial
    'Unsigned scaled phase by cyclic rotation, with no shift-padding register.\n\nFor a W-bit unsigned value v and any nonnegative k,\n\n    2**k*v = r + (2**W-1)*sum(2**j*r[j mod W] for j in range(k)),\n    r = ROL_W(v,k mod W).\n\nThis needs W ordinary bit rotations and at most max_k extra rotations on\nAND(bit[j], k>j).  The bit routing is a cyclic permutation of the original\nword.  Its width is W rather than W+max_k.  Comparator windows are compiled\nfrom their mathematical truth functions on the certified k range.\n'
    pass
    _c37_cyclic_phase__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', False).Path
    _c37_cyclic_phase_INTEGRATED_ROOT = _c37_cyclic_phase__IntegratedPath(_c37_cyclic_phase___file__).resolve().parents[7]
    _c37_cyclic_phase_contextmanager = _import_component('contextlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', False).contextmanager
    _c37_cyclic_phase_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', False).dataclass
    _c37_cyclic_phase_Fraction = _import_component('fractions', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', False).Fraction
    _c37_cyclic_phase_lru_cache = _import_component('functools', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', False).lru_cache
    _c37_cyclic_phase_itertools = _import_component('itertools', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', True)
    _c37_cyclic_phase_math = _import_component('math', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', True)
    _c37_cyclic_phase_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', False)
    _c37_cyclic_phase_compile_polynomial = _import_component('quadratic_terms', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', False).compile_polynomial
    _c37_cyclic_phase_xor_polynomial = _import_component('quadratic_terms', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', False).xor_polynomial

    def _c37_cyclic_phase__monomials(width, degree):
        return tuple((mask for mask in range(1 << width) if mask.bit_count() <= degree))

    def _c37_cyclic_phase__truth_of_terms(terms, size):
        return sum(((sum((int(value & term == term) for term in terms)) & 1) << value for value in range(size)))

    def _c37_cyclic_phase__restricted_anf(truth, max_value):
        """ANF on the downward-closed domain 0..max_value, with zero unused terms."""
        values = [truth >> value & 1 for value in range(16)]
        for bit in range(4):
            for mask in range(16):
                if mask >> bit & 1:
                    values[mask] ^= values[mask ^ 1 << bit]
        terms = tuple((mask for mask, coefficient in enumerate(values) if coefficient and mask <= max_value))
        full = (1 << max_value + 1) - 1
        if _c37_cyclic_phase__truth_of_terms(terms, max_value + 1) != truth & full:
            raise AssertionError('Range-restricted ANF certificate failed.')
        return terms

    def _c37_cyclic_phase__span_solution(columns, target):
        pivots, null = ({}, [])
        for index, column in enumerate(columns):
            value, expression = (column, 1 << index)
            while value:
                bit = value.bit_length() - 1
                if bit not in pivots:
                    pivots[bit] = (value, expression)
                    break
                old, old_expression = pivots[bit]
                value ^= old
                expression ^= old_expression
            if not value:
                null.append(expression)
        value, expression = (target, 0)
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                return (None, ())
            old, old_expression = pivots[bit]
            value ^= old
            expression ^= old_expression
        return (expression, tuple(null))

    @_c37_cyclic_phase_dataclass(frozen=True)
    class _c37_cyclic_phase_ThresholdPlan:
        threshold: int
        max_k: int
        truth: int
        phase_terms: tuple[int, ...]
        helper_terms: tuple[int, ...] | None
        output_terms: tuple[int, ...]
        products: int

    @_c37_cyclic_phase_lru_cache(maxsize=16)
    def _c37_cyclic_phase__helper_candidates(max_k):
        """Every distinct one-product quadratic helper on the valid flag domain."""
        monomials = tuple((mask for mask in _c37_cyclic_phase__monomials(4, 2) if mask and mask <= max_k))
        best = {}
        for selection in range(1 << len(monomials)):
            terms = tuple((mask for i, mask in enumerate(monomials) if selection >> i & 1))
            plan = _c37_cyclic_phase_compile_polynomial(4, terms)
            if len(plan.products) != 1:
                continue
            truth = _c37_cyclic_phase__truth_of_terms(terms, max_k + 1)
            key = (len(terms), terms)
            if truth not in best or key < best[truth][0]:
                best[truth] = (key, terms)
        return tuple(((truth, item[1]) for truth, item in sorted(best.items(), key=lambda item: (item[1][0], item[0]))))

    @_c37_cyclic_phase_lru_cache(maxsize=128)
    def _c37_cyclic_phase_threshold_plan(threshold, max_k=10):
        """Compile [k>=threshold] with exact truth/ANF certificates.

    The valid range max_k<=10 admits degree<=3 with only one possible cubic
    monomial.  Quadratic comparators use a minimum product-rank realization.
    Cubic comparators are exhaustively searched for a one-product helper and
    one-product final expression.  Two products are then optimal because a
    one-product XOR/affine circuit cannot contain a cubic term.
    """
        threshold, max_k = (int(threshold), int(max_k))
        if not 0 <= max_k <= 10 or not 1 <= threshold <= max_k:
            raise ValueError('Expected 1<=threshold<=max_k<=10.')
        size, full = (max_k + 1, (1 << max_k + 1) - 1)
        truth = sum((int(k >= threshold) << k for k in range(size)))
        phase_terms = _c37_cyclic_phase__restricted_anf(truth, max_k)
        if max((term.bit_count() for term in phase_terms), default=0) <= 2:
            plan = _c37_cyclic_phase_compile_polynomial(4, phase_terms)
            return _c37_cyclic_phase_ThresholdPlan(threshold, max_k, truth, phase_terms, None, phase_terms, len(plan.products))
        flags = [sum(((k >> bit & 1) << k for k in range(size))) for bit in range(4)]
        monomials = _c37_cyclic_phase__monomials(5, 2)
        for helper_truth, helper_terms in _c37_cyclic_phase__helper_candidates(max_k):
            variables = flags + [helper_truth]
            columns = []
            for term in monomials:
                column = full
                for bit in range(5):
                    if term >> bit & 1:
                        column &= variables[bit]
                columns.append(column)
            expression, null = _c37_cyclic_phase__span_solution(columns, truth)
            if expression is None:
                continue
            previous_gray, current = (0, expression)
            for selection in range(1 << len(null)):
                gray = selection ^ selection >> 1
                changed = gray ^ previous_gray
                if changed:
                    current ^= null[changed.bit_length() - 1]
                previous_gray = gray
                terms = tuple((term for i, term in enumerate(monomials) if current >> i & 1))
                output = _c37_cyclic_phase_compile_polynomial(5, terms)
                if len(output.products) > 1:
                    continue
                actual = 0
                for term in terms:
                    column = full
                    for bit in range(5):
                        if term >> bit & 1:
                            column &= variables[bit]
                    actual ^= column
                if actual != truth:
                    raise AssertionError('Threshold synthesis truth certificate failed.')
                return _c37_cyclic_phase_ThresholdPlan(threshold, max_k, truth, phase_terms, helper_terms, terms, 1 + len(output.products))
        raise ValueError('No two-product comparator was found in the exhaustive helper search.')

    def _c37_cyclic_phase__erase_polynomial(builder, target, variables, terms):
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

    @_c37_cyclic_phase_contextmanager
    def _c37_cyclic_phase_threshold_control(builder, flags, threshold, *, max_k=10, compact=None):
        """Expose a comparator bit using at most two quantum helper wires.

    The caller may use one additional AND temporary.  When three free wires
    are available, retaining the comparator's helper avoids all CCZ cleanup.
    With only two free wires, a cubic comparator releases its helper early
    and repays its one cubic phase term on the HMR-one branch.
    """
        flags = list(flags)
        if len(flags) != 4 or len(set(flags)) != 4:
            raise ValueError('Four distinct binary shift flags are required.')
        plan = _c37_cyclic_phase_threshold_plan(threshold, max_k)
        if not plan.products:
            linear = [term.bit_length() - 1 for term in plan.output_terms if term]
            if not linear:
                yield (bool(0 in plan.output_terms), plan, False)
                return
            pivot, other = (flags[linear[0]], [flags[i] for i in linear[1:]])
            for wire in other:
                builder.cx(wire, pivot)
            if 0 in plan.output_terms:
                builder.x(pivot)
            try:
                yield (pivot, plan, False)
            finally:
                if 0 in plan.output_terms:
                    builder.x(pivot)
                for wire in reversed(other):
                    builder.cx(wire, pivot)
            return
        available = builder.max_qubits - builder.num_allocated_qubits
        compact = available < 3 if compact is None else bool(compact)
        helper = None
        variables = list(flags)
        if plan.helper_terms is not None:
            helper = builder.alloc_qubits(1)[0]
            _c37_cyclic_phase_xor_polynomial(builder, flags, helper, plan.helper_terms)
            variables.append(helper)
        target = builder.alloc_qubits(1)[0]
        _c37_cyclic_phase_xor_polynomial(builder, variables, target, plan.output_terms)
        if helper is not None and compact:
            _c37_cyclic_phase__erase_polynomial(builder, helper, flags, plan.helper_terms)
            helper = None
        try:
            yield (target, plan, bool(plan.helper_terms is not None and compact))
        finally:
            if helper is None:
                _c37_cyclic_phase__erase_polynomial(builder, target, flags, plan.phase_terms)
            else:
                _c37_cyclic_phase__erase_polynomial(builder, target, variables, plan.output_terms)
                _c37_cyclic_phase__erase_polynomial(builder, helper, flags, plan.helper_terms)

    def _c37_cyclic_phase_rotation_pairs(width, amount):
        """A minimal-SWAP cycle decomposition of left rotation by amount."""
        amount %= width
        visited, pairs = (set(), [])
        for start in range(width):
            if start in visited:
                continue
            cycle, at = ([], start)
            while at not in visited:
                visited.add(at)
                cycle.append(at)
                at = (at + amount) % width
            pairs += [(start, other) for other in cycle[1:]]
        if len(pairs) != width - _c37_cyclic_phase_math.gcd(width, amount):
            raise AssertionError('Rotation cycle-count certificate failed.')
        return tuple(pairs)

    def _c37_cyclic_phase__pow2(exponent):
        return _c37_cyclic_phase_Fraction(1 << exponent) if exponent >= 0 else _c37_cyclic_phase_Fraction(1, 1 << -exponent)

    def _c37_cyclic_phase_cyclic_scale_phase(builder, value, flags, fractional_bits, *, beta=1, source_width=None, compact_thresholds=None, turn_offsets=None, complement_overflow=False):
        """Apply beta*unsigned(value)*2**k/2**fractional_bits turns exactly.

    Requires four binary flag wires and certified 0<=k<=max_k<=10.
    `source_width` may certify initially zero high padding within the W-bit
    word; this prunes the corresponding impossible overflow terms. All
    value and flag wires are restored and all helpers return to zero.

    `turn_offsets` is an optional sequence of W+max_k exact rational values:
    first the W ordinary bit features, then the max_k overflow features.
    Each value is an additive phase in turns, independently of beta. Use
    Fraction objects, integers, or exact Fraction strings; floating-point
    offsets are rejected. Any pruned, known-zero feature must have offset
    zero. These offsets deliberately change the numerical phase function;
    its model-level approximation must be verified separately.

    With `complement_overflow=True`, each overflow feature is instead
    bit[j mod W] AND [k<j+padding+1]. Its mathematical angle is negated and
    its former angle is added to that bit's baseline. This is an exact
    change of phase basis. For W8/K10/F18 it turns three baseline angles
    into S, Z, and T, leaving fifteen generic rotations. Fitted offsets
    refer to the selected basis; keep those three offsets zero to retain
    the synthesis saving.

    For an originally signed W-bit low word, the caller can flip its top bit
    around this function and decrease the earlier coarse anchor by one unit
    of 2**(W-1). That conversion must be made in both parts of the design.
    """
        range_bound = getattr(flags, 'max_k', None)
        value, flags = (list(value), list(flags))
        width = len(value)
        max_k = 10 if range_bound is None else int(range_bound)
        source_width = width if source_width is None else int(source_width)
        if len(flags) != 4 or not 0 < source_width <= width or (not 0 <= max_k <= 10):
            raise ValueError('Requires four flags and 0<source_width<=W with max_k<=10.')
        if len(set(value + flags)) != width + 4:
            raise ValueError('Phase word and flags must use distinct wires.')
        beta = _c37_cyclic_phase_Fraction(beta)
        if turn_offsets is None:
            offsets = (_c37_cyclic_phase_Fraction(0),) * (width + max_k)
        else:
            entries = tuple(turn_offsets)
            if len(entries) != width + max_k:
                raise ValueError(f'Expected {width + max_k} turn offsets in base/overflow order.')
            if any((isinstance(entry, float) for entry in entries)):
                raise TypeError('Frozen turn offsets must be exact rationals, not floats.')
            offsets = tuple((_c37_cyclic_phase_Fraction(entry) for entry in entries))
        ordinary_count = min(width, source_width + max_k)
        padding = width - source_width
        overflow_count = max(0, max_k - padding)
        if any(offsets[ordinary_count:width]) or any(offsets[width + overflow_count:]):
            raise ValueError('Pruned, known-zero phase features must have zero offsets.')
        routing = []
        swaps = 0
        for bit in reversed(range(4)):
            amount = 1 << bit
            if amount > max_k:
                continue
            pairs = _c37_cyclic_phase_rotation_pairs(width, amount)
            for a, b in pairs:
                builder.cswap(flags[bit], value[a], value[b])
            routing.append((flags[bit], pairs))
            swaps += len(pairs)
        ordinary = []
        mathematical_base = [beta * _c37_cyclic_phase__pow2(bit - fractional_bits + 1) for bit in range(width)]
        mathematical_overflow = [beta * ((1 << width) - 1) * _c37_cyclic_phase__pow2(bit - fractional_bits + 1) for bit in range(overflow_count)]
        if complement_overflow:
            for bit, angle in enumerate(mathematical_overflow):
                mathematical_base[bit % width] += angle
        for bit in range(ordinary_count):
            angle = mathematical_base[bit] + 2 * offsets[bit]
            builder.z_pow(value[bit], angle)
            ordinary.append(angle)
        corrections = []
        products, conditioned_ccz = (0, 0)
        for bit in range(overflow_count):
            threshold = bit + padding + 1
            with _c37_cyclic_phase_threshold_control(builder, flags, threshold, max_k=max_k, compact=compact_thresholds) as (control, plan, compact_used):
                if complement_overflow:
                    builder.x(control)
                temporary = builder.alloc_qubits(1)[0]
                builder.ccx(control, value[bit % width], temporary)
                angle = mathematical_overflow[bit] * (-1 if complement_overflow else 1) + 2 * offsets[width + bit]
                builder.z_pow(temporary, angle)
                builder.del_and(control, value[bit % width], temporary)
                builder.free(temporary)
                if complement_overflow:
                    builder.x(control)
                corrections.append(angle)
                products += plan.products + 1
                conditioned_ccz += int(compact_used) * sum((term.bit_count() == 3 for term in plan.phase_terms))
        for flag, pairs in reversed(routing):
            for a, b in reversed(pairs):
                builder.cswap(flag, value[a], value[b])
        return dict(width=width, max_k=max_k, source_width=source_width, complement_overflow=bool(complement_overflow), cswaps=2 * swaps, comparator_and_products=products, hmr_conditioned_ccz=conditioned_ccz, expected_toffolis=2 * swaps + products + conditioned_ccz / 2, z_pow_calls=len(ordinary) + len(corrections), half_turn_angles=[str(angle) for angle in ordinary + corrections], turn_offsets=[str(offset) for offset in offsets])

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/dirty_terminal.py
def _initialize__c38_dirty_terminal():
    global _c38_dirty_terminal_INTEGRATED_ROOT, _c38_dirty_terminal__IntegratedPath, _c38_dirty_terminal___file__, _c38_dirty_terminal___name__, _c38_dirty_terminal__phase, _c38_dirty_terminal_annotations, _c38_dirty_terminal_dirty_mcx, _c38_dirty_terminal_dirty_mcx_cost, _c38_dirty_terminal_dirty_mcz, _c38_dirty_terminal_dirty_mcz_cost, _c38_dirty_terminal_increment_cost, _c38_dirty_terminal_km, _c38_dirty_terminal_terminal_add, _c38_dirty_terminal_terminal_cost, _c38_dirty_terminal_terminal_dirty_count
    'Exact unsigned adder terminals using restored dirty workspace.\n\nThese kernels are a width fallback, not a claimed free-space adder.  A\nCuccaro majority/unmajority frame stores carries in real source bits.  The\nremaining zero-source suffix is a controlled increment whose multiple\ncontrols use restored dirty wires.  No clean quantum wire is allocated.\n\nMeasured forward carries can be repaid without extra Toffolis: phase a\nmajority while it occupies a source wire, or apply conditional Z before\nand after the controlled X whose toggle is the required carry.  The latter\necho is (-1)**(m*(b XOR (b XOR carry))) = (-1)**(m*carry).\n'
    pass
    _c38_dirty_terminal__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/dirty_terminal.py', False).Path
    _c38_dirty_terminal_INTEGRATED_ROOT = _c38_dirty_terminal__IntegratedPath(_c38_dirty_terminal___file__).resolve().parents[7]
    _c38_dirty_terminal_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/dirty_terminal.py', False)

    def _c38_dirty_terminal_dirty_mcx_cost(controls):
        if controls < 2:
            return 0
        return 1 if controls == 2 else 4 * controls - 8

    def _c38_dirty_terminal_increment_cost(width):
        return sum((_c38_dirty_terminal_dirty_mcx_cost(position + 1) for position in range(width)))

    def _c38_dirty_terminal_terminal_cost(width, source_width):
        prefix = min(source_width, max(0, width - 1))
        return 2 * prefix + (0 if source_width == width else _c38_dirty_terminal_increment_cost(width - prefix))

    def _c38_dirty_terminal_terminal_dirty_count(width, source_width):
        return max(0, width - source_width - 2)

    def _c38_dirty_terminal_dirty_mcz_cost(controls):
        if controls < 3:
            return 0
        return 1 if controls == 3 else 4 * controls - 12

    def _c38_dirty_terminal_dirty_mcz(builder, controls, dirty=()):
        """Phase the product of controls, restoring every borrowed dirty bit.

    Replacing the final target toggle of each dirty-MCX ladder with CCZ
    gives two diagonal phases whose dirty contributions cancel.  Their
    remaining phase is exactly the AND of all controls, including on every
    arbitrary dirty-wire input.  No clean quantum wire is allocated.
    """
        controls, dirty = (list(controls), list(dirty))
        if not controls or not all((isinstance(w, _c38_dirty_terminal_km.q) for w in controls + dirty)):
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

    def _c38_dirty_terminal_dirty_mcx(builder, controls, target, dirty=()):
        """Toggle target by the AND of controls; restore every arbitrary dirty bit.

    For n >= 3, n-2 borrowed wires and 4n-8 Toffolis suffice.  A complete
    AND ladder and a ladder omitting its first product have identical dirty
    contributions; their target toggles differ by precisely the full AND.
    Each ladder is reversed after its target operation.
    """
        controls, dirty = (list(controls), list(dirty))
        if not all((isinstance(wire, _c38_dirty_terminal_km.q) for wire in controls + [target] + dirty)):
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

    def _c38_dirty_terminal__phase(builder, measurement, wire):
        if measurement is not None:
            builder.push_condition(measurement)
            builder.z(wire)
            builder.pop_condition()

    def _c38_dirty_terminal_terminal_add(builder, source, target, incoming, *, dirty=(), debt=None, start=0, overflow_phase=None):
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
        if not isinstance(incoming, _c38_dirty_terminal_km.q):
            raise ValueError('The sparse terminal requires a quantum incoming carry.')
        count = next((i for i, wire in enumerate(source) if wire is False), width)
        if any((wire is not False for wire in source[count:])):
            raise ValueError('Only an unsigned source prefix with high zero padding is supported.')
        if overflow_phase is not None and count == width:
            raise ValueError('Overflow-phase terminals require a nonempty high zero-source suffix.')
        real_source = source[:count]
        if not all((isinstance(wire, _c38_dirty_terminal_km.q) for wire in real_source + target + dirty)):
            raise ValueError('All nonconstant operands must be quantum wires.')
        operands = real_source + target + [incoming]
        if len(set(operands)) != len(operands):
            raise ValueError('Source, target, and incoming carry must be disjoint.')
        required = _c38_dirty_terminal_terminal_dirty_count(width, count)
        dirty = [wire for wire in dict.fromkeys(dirty) if wire not in operands]
        if len(dirty) < required:
            raise ValueError(f'The terminal requires {required} restored dirty wires.')

        def take(position):
            return None if debt is None else debt.measurements.pop(start + position, None)

        def repay(position, wire):
            measurement = take(position)
            _c38_dirty_terminal__phase(builder, measurement, wire)
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
                _c38_dirty_terminal_dirty_mcz(builder, [carry] + high, dirty)
                builder.pop_condition()
            for position in reversed(range(len(high))):
                measurement = take(prefix + position) if position else None
                _c38_dirty_terminal__phase(builder, measurement, high[position])
                _c38_dirty_terminal_dirty_mcx(builder, [carry] + high[:position], high[position], dirty)
                _c38_dirty_terminal__phase(builder, measurement, high[position])
                if measurement is not None:
                    builder.free(measurement)
        for a, b, carry in reversed(frames):
            builder.ccx(b, carry, a)
            builder.cx(a, carry)
            builder.cx(carry, b)
        phase_cost = _c38_dirty_terminal_dirty_mcz_cost(width - prefix + 1) if overflow_phase is not None else 0
        return dict(toffolis=_c38_dirty_terminal_terminal_cost(width, count) + phase_cost, clean_workspace=0, dirty_workspace=required, source_prefix=count)

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/__init__.py
def _initialize__c39___init__():
    global _c39___init___INTEGRATED_ROOT, _c39___init____IntegratedPath, _c39___init_____file__, _c39___init_____name__
    'From-parameters inverse-square-root phase circuit.'
    _c39___init____IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/__init__.py', False).Path
    _c39___init___INTEGRATED_ROOT = _c39___init____IntegratedPath(_c39___init_____file__).resolve().parents[8]

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py
def _initialize__c40_arithmetic():
    global _c40_arithmetic_INTEGRATED_ROOT, _c40_arithmetic_MAJORITY_TRUTH, _c40_arithmetic_Sequence, _c40_arithmetic__Frame, _c40_arithmetic__IntegratedPath, _c40_arithmetic___file__, _c40_arithmetic___name__, _c40_arithmetic__as_array, _c40_arithmetic__compute_carry, _c40_arithmetic__erase_carry, _c40_arithmetic__phase_borrow, _c40_arithmetic__phase_carry, _c40_arithmetic__segment, _c40_arithmetic__sum_keep_carry, _c40_arithmetic_add, _c40_arithmetic_annotations, _c40_arithmetic_dataclass, _c40_arithmetic_horner_rows, _c40_arithmetic_km, _c40_arithmetic_partition, _c40_arithmetic_phase_quadratic, _c40_arithmetic_signed_row
    "Segmented measurement-carry addition, derived for this generator.\n\nA carry boundary is kept while the interior carries of a segment are erased.\nAfter every sum bit is final, the boundary is measured and the resulting sign\nis repaid by a borrow comparator in the measurement-one branch.  The identity\nis carry(a+b+c) = borrow((a+b+c) mod 2**n - a - c).\n\nOnly the comparator's interior carries are computed.  Its last carry is phased\nby the exact quadratic identity majority(a,b,c) = ab XOR ac XOR bc, so that\nlast step needs only CZ gates.\n"
    pass
    _c40_arithmetic__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).Path
    _c40_arithmetic_INTEGRATED_ROOT = _c40_arithmetic__IntegratedPath(_c40_arithmetic___file__).resolve().parents[8]
    _c40_arithmetic_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).dataclass
    _c40_arithmetic_Sequence = _import_component('typing', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).Sequence
    _c40_arithmetic_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False)
    _c40_arithmetic_phase_quadratic = _import_component('compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).phase_quadratic
    _c40_arithmetic_MAJORITY_TRUTH = _import_component('compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).MAJORITY_TRUTH

    @_c40_arithmetic_dataclass
    class _c40_arithmetic__Frame:
        a: object
        b: object
        incoming: object
        outgoing: object
        preserve_sign: bool = False

    def _c40_arithmetic__as_array(wires):
        return _c40_arithmetic_km.array(list(wires))

    def _c40_arithmetic__compute_carry(builder, a, b, incoming, *, preserve=None):
        if a is False and incoming is False:
            return _c40_arithmetic__Frame(a, b, incoming, False)
        outgoing = builder.alloc_qubits(1)[0]
        if a is False:
            builder.ccx(incoming, b, outgoing)
        elif a == preserve and isinstance(incoming, _c40_arithmetic_km.q):
            builder.cx(a, incoming)
            builder.cx(a, b)
            builder.ccx(incoming, b, outgoing)
            builder.cx(a, outgoing)
            return _c40_arithmetic__Frame(a, b, incoming, outgoing, True)
        else:
            builder.cx(incoming, a)
            builder.cx(incoming, b)
            builder.ccx(a, b, outgoing)
            builder.cx(incoming, outgoing)
        return _c40_arithmetic__Frame(a, b, incoming, outgoing)

    def _c40_arithmetic__erase_carry(builder, frame, *, write_sum):
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

    def _c40_arithmetic__sum_keep_carry(builder, frame):
        if frame.preserve_sign:
            builder.cx(frame.a, frame.incoming)
            builder.cx(frame.incoming, frame.b)
        elif frame.a is False:
            builder.cx(frame.incoming, frame.b)
        else:
            builder.cx(frame.incoming, frame.a)
            builder.cx(frame.a, frame.b)

    def _c40_arithmetic__segment(builder, a, b, incoming, *, retain_outgoing, preserve=None):
        n = len(b)
        if retain_outgoing:
            frames = []
            carry = incoming
            for aa, bb in zip(a, b):
                frame = _c40_arithmetic__compute_carry(builder, aa, bb, carry, preserve=preserve)
                frames.append(frame)
                carry = frame.outgoing
            _c40_arithmetic__sum_keep_carry(builder, frames[-1])
            for frame in reversed(frames[:-1]):
                _c40_arithmetic__erase_carry(builder, frame, write_sum=True)
            return carry
        if n == 1:
            builder.cx(a[0], b[0])
            builder.cx(incoming, b[0])
            return False
        frames = []
        carry = incoming
        for aa, bb in zip(a[:-2], b[:-2]):
            frame = _c40_arithmetic__compute_carry(builder, aa, bb, carry, preserve=preserve)
            frames.append(frame)
            carry = frame.outgoing
        aa, bb = (a[-2], b[-2])
        if aa == preserve and isinstance(carry, _c40_arithmetic_km.q):
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
            _c40_arithmetic__erase_carry(builder, frame, write_sum=True)
        return False

    def _c40_arithmetic__phase_carry(builder, a, b, incoming, *, preserve=None):
        """Apply (-1)**carry_out(a+b+incoming), restoring all operands."""
        frames = []
        carry = incoming
        for aa, bb in zip(a[:-1], b[:-1]):
            frame = _c40_arithmetic__compute_carry(builder, aa, bb, carry, preserve=preserve)
            frames.append(frame)
            carry = frame.outgoing
        _c40_arithmetic_phase_quadratic(builder, [a[-1], b[-1], carry], _c40_arithmetic_MAJORITY_TRUTH)
        for frame in reversed(frames):
            _c40_arithmetic__erase_carry(builder, frame, write_sum=False)

    def _c40_arithmetic__phase_borrow(builder, a, final_sum, incoming, *, preserve=None):
        builder.x(_c40_arithmetic__as_array(final_sum))
        _c40_arithmetic__phase_carry(builder, a, final_sum, incoming, preserve=preserve)
        builder.x(_c40_arithmetic__as_array(final_sum))

    def _c40_arithmetic_partition(width: int, clean: int) -> list[int]:
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

    def _c40_arithmetic_add(builder: _c40_arithmetic_km.CircuitBuilder, source: _c40_arithmetic_Sequence, target: _c40_arithmetic_Sequence, *, carry_in=False, subtract: bool=False, signed_source: bool=False, carry_budget: int | None=None) -> None:
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
        if any((not isinstance(q, _c40_arithmetic_km.q) for q in source)):
            raise ValueError('Source must contain quantum wires; high zeros are implicit.')
        if len(set(source + target)) != len(source) + len(target):
            raise ValueError('Source and target must be disjoint distinct wires.')
        if isinstance(carry_in, _c40_arithmetic_km.q) and carry_in in source + target:
            raise ValueError('carry_in must be disjoint from source and target.')
        if carry_in is not False and (not isinstance(carry_in, _c40_arithmetic_km.q)):
            raise ValueError('carry_in must be a quantum wire or False.')
        available = builder.max_qubits - builder.num_allocated_qubits
        desired = max(0, n - 2) if carry_budget is None else carry_budget
        clean = int(min(available, desired, max(0, n - 2)))
        sizes = _c40_arithmetic_partition(n, clean)
        preserve = source[-1] if signed_source and source else None
        source += [preserve if preserve is not None else False] * (n - len(source))
        if subtract:
            builder.x(_c40_arithmetic__as_array(target))
        boundaries = []
        start = 0
        carry = carry_in
        for number, length in enumerate(sizes):
            aa, bb = (source[start:start + length], target[start:start + length])
            retain = number + 1 < len(sizes)
            outgoing = _c40_arithmetic__segment(builder, aa, bb, carry, retain_outgoing=retain, preserve=preserve)
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
            _c40_arithmetic__phase_borrow(builder, aa, bb, incoming, preserve=preserve)
            builder.pop_condition()
            builder.free(result)
        if subtract:
            builder.x(_c40_arithmetic__as_array(target))

    def _c40_arithmetic_signed_row(builder: _c40_arithmetic_km.CircuitBuilder, source: _c40_arithmetic_Sequence, target: _c40_arithmetic_Sequence, *, shift: int, sign, inverse: bool=False, nearest: bool=False, signed_source: bool=False, carry_budget: int | None=None) -> None:
        """Add (1-2sign)*scaled_source, with optional rounding before the sign.

    At negative shift -s, nearest uses exactly (source>>s)+bit(source,s-1).
    With signed_source=True the shift is arithmetic.  Ties round toward
    positive infinity for both signs.  The discarded rounding
    bit is the carry-in of the adder; it costs no additional quantum wire and
    no additional carry product versus the corresponding full-width addition.
    """
        source, target = (list(source), list(target))
        carry = False
        if shift >= 0:
            target = target[shift:]
        else:
            cut = -shift
            if signed_source and cut >= len(source):
                if nearest:
                    return
                source = source[-1:]
                cut = 0
            if nearest and cut - 1 < len(source):
                carry = source[cut - 1]
            source = source[cut:]
        if not target or (not source and carry is False):
            return
        source = source[:len(target)]
        if isinstance(sign, _c40_arithmetic_km.q) and sign in source + target + ([carry] if isinstance(carry, _c40_arithmetic_km.q) else []):
            raise ValueError('Sign must be disjoint from row data and rounding bit.')
        for q in target:
            builder.cx(sign, q)
        _c40_arithmetic_add(builder, source, target, carry_in=carry, subtract=inverse, signed_source=signed_source, carry_budget=carry_budget)
        for q in target:
            builder.cx(sign, q)

    def _c40_arithmetic_horner_rows(builder, residual, source, target, *, source_fraction, target_fraction, inverse=False, nearest=None, rounding='floor', signed_source=False, carry_budget=None):
        if rounding not in ('floor', 'nearest'):
            raise ValueError('rounding must be floor or nearest')
        if nearest is None:
            nearest = rounding == 'nearest'
        residual = list(residual)
        indices = reversed(range(len(residual))) if inverse else range(len(residual))
        for i in indices:
            _c40_arithmetic_signed_row(builder, source, target, shift=i - len(residual) - 1 + target_fraction - source_fraction, sign=residual[i], inverse=inverse, nearest=nearest, signed_source=signed_source, carry_budget=carry_budget)

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py [independent arithmetic context]
def _initialize__c40_arithmetic_private():
    global _c40_arithmetic_private_INTEGRATED_ROOT, _c40_arithmetic_private_MAJORITY_TRUTH, _c40_arithmetic_private_Sequence, _c40_arithmetic_private__Frame, _c40_arithmetic_private__IntegratedPath, _c40_arithmetic_private___file__, _c40_arithmetic_private___name__, _c40_arithmetic_private__as_array, _c40_arithmetic_private__compute_carry, _c40_arithmetic_private__erase_carry, _c40_arithmetic_private__phase_borrow, _c40_arithmetic_private__phase_carry, _c40_arithmetic_private__segment, _c40_arithmetic_private__sum_keep_carry, _c40_arithmetic_private_add, _c40_arithmetic_private_annotations, _c40_arithmetic_private_dataclass, _c40_arithmetic_private_horner_rows, _c40_arithmetic_private_km, _c40_arithmetic_private_partition, _c40_arithmetic_private_phase_quadratic, _c40_arithmetic_private_signed_row
    "Segmented measurement-carry addition, derived for this generator.\n\nA carry boundary is kept while the interior carries of a segment are erased.\nAfter every sum bit is final, the boundary is measured and the resulting sign\nis repaid by a borrow comparator in the measurement-one branch.  The identity\nis carry(a+b+c) = borrow((a+b+c) mod 2**n - a - c).\n\nOnly the comparator's interior carries are computed.  Its last carry is phased\nby the exact quadratic identity majority(a,b,c) = ab XOR ac XOR bc, so that\nlast step needs only CZ gates.\n"
    pass
    _c40_arithmetic_private__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).Path
    _c40_arithmetic_private_INTEGRATED_ROOT = _c40_arithmetic_private__IntegratedPath(_c40_arithmetic_private___file__).resolve().parents[8]
    _c40_arithmetic_private_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).dataclass
    _c40_arithmetic_private_Sequence = _import_component('typing', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).Sequence
    _c40_arithmetic_private_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False)
    _c40_arithmetic_private_phase_quadratic = _import_component('compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).phase_quadratic
    _c40_arithmetic_private_MAJORITY_TRUTH = _import_component('compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', False).MAJORITY_TRUTH

    @_c40_arithmetic_private_dataclass
    class _c40_arithmetic_private__Frame:
        a: object
        b: object
        incoming: object
        outgoing: object
        preserve_sign: bool = False

    def _c40_arithmetic_private__as_array(wires):
        return _c40_arithmetic_private_km.array(list(wires))

    def _c40_arithmetic_private__compute_carry(builder, a, b, incoming, *, preserve=None):
        if a is False and incoming is False:
            return _c40_arithmetic_private__Frame(a, b, incoming, False)
        outgoing = builder.alloc_qubits(1)[0]
        if a is False:
            builder.ccx(incoming, b, outgoing)
        elif a == preserve and isinstance(incoming, _c40_arithmetic_private_km.q):
            builder.cx(a, incoming)
            builder.cx(a, b)
            builder.ccx(incoming, b, outgoing)
            builder.cx(a, outgoing)
            return _c40_arithmetic_private__Frame(a, b, incoming, outgoing, True)
        else:
            builder.cx(incoming, a)
            builder.cx(incoming, b)
            builder.ccx(a, b, outgoing)
            builder.cx(incoming, outgoing)
        return _c40_arithmetic_private__Frame(a, b, incoming, outgoing)

    def _c40_arithmetic_private__erase_carry(builder, frame, *, write_sum):
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

    def _c40_arithmetic_private__sum_keep_carry(builder, frame):
        if frame.preserve_sign:
            builder.cx(frame.a, frame.incoming)
            builder.cx(frame.incoming, frame.b)
        elif frame.a is False:
            builder.cx(frame.incoming, frame.b)
        else:
            builder.cx(frame.incoming, frame.a)
            builder.cx(frame.a, frame.b)

    def _c40_arithmetic_private__segment(builder, a, b, incoming, *, retain_outgoing, preserve=None):
        n = len(b)
        if retain_outgoing:
            frames = []
            carry = incoming
            for aa, bb in zip(a, b):
                frame = _c40_arithmetic_private__compute_carry(builder, aa, bb, carry, preserve=preserve)
                frames.append(frame)
                carry = frame.outgoing
            _c40_arithmetic_private__sum_keep_carry(builder, frames[-1])
            for frame in reversed(frames[:-1]):
                _c40_arithmetic_private__erase_carry(builder, frame, write_sum=True)
            return carry
        if n == 1:
            builder.cx(a[0], b[0])
            builder.cx(incoming, b[0])
            return False
        frames = []
        carry = incoming
        for aa, bb in zip(a[:-2], b[:-2]):
            frame = _c40_arithmetic_private__compute_carry(builder, aa, bb, carry, preserve=preserve)
            frames.append(frame)
            carry = frame.outgoing
        aa, bb = (a[-2], b[-2])
        if aa == preserve and isinstance(carry, _c40_arithmetic_private_km.q):
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
            _c40_arithmetic_private__erase_carry(builder, frame, write_sum=True)
        return False

    def _c40_arithmetic_private__phase_carry(builder, a, b, incoming, *, preserve=None):
        """Apply (-1)**carry_out(a+b+incoming), restoring all operands."""
        frames = []
        carry = incoming
        for aa, bb in zip(a[:-1], b[:-1]):
            frame = _c40_arithmetic_private__compute_carry(builder, aa, bb, carry, preserve=preserve)
            frames.append(frame)
            carry = frame.outgoing
        _c40_arithmetic_private_phase_quadratic(builder, [a[-1], b[-1], carry], _c40_arithmetic_private_MAJORITY_TRUTH)
        for frame in reversed(frames):
            _c40_arithmetic_private__erase_carry(builder, frame, write_sum=False)

    def _c40_arithmetic_private__phase_borrow(builder, a, final_sum, incoming, *, preserve=None):
        builder.x(_c40_arithmetic_private__as_array(final_sum))
        _c40_arithmetic_private__phase_carry(builder, a, final_sum, incoming, preserve=preserve)
        builder.x(_c40_arithmetic_private__as_array(final_sum))

    def _c40_arithmetic_private_partition(width: int, clean: int) -> list[int]:
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

    def _c40_arithmetic_private_add(builder: _c40_arithmetic_private_km.CircuitBuilder, source: _c40_arithmetic_private_Sequence, target: _c40_arithmetic_private_Sequence, *, carry_in=False, subtract: bool=False, signed_source: bool=False, carry_budget: int | None=None) -> None:
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
        if any((not isinstance(q, _c40_arithmetic_private_km.q) for q in source)):
            raise ValueError('Source must contain quantum wires; high zeros are implicit.')
        if len(set(source + target)) != len(source) + len(target):
            raise ValueError('Source and target must be disjoint distinct wires.')
        if isinstance(carry_in, _c40_arithmetic_private_km.q) and carry_in in source + target:
            raise ValueError('carry_in must be disjoint from source and target.')
        if carry_in is not False and (not isinstance(carry_in, _c40_arithmetic_private_km.q)):
            raise ValueError('carry_in must be a quantum wire or False.')
        available = builder.max_qubits - builder.num_allocated_qubits
        desired = max(0, n - 2) if carry_budget is None else carry_budget
        clean = int(min(available, desired, max(0, n - 2)))
        sizes = _c40_arithmetic_private_partition(n, clean)
        preserve = source[-1] if signed_source and source else None
        source += [preserve if preserve is not None else False] * (n - len(source))
        if subtract:
            builder.x(_c40_arithmetic_private__as_array(target))
        boundaries = []
        start = 0
        carry = carry_in
        for number, length in enumerate(sizes):
            aa, bb = (source[start:start + length], target[start:start + length])
            retain = number + 1 < len(sizes)
            outgoing = _c40_arithmetic_private__segment(builder, aa, bb, carry, retain_outgoing=retain, preserve=preserve)
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
            _c40_arithmetic_private__phase_borrow(builder, aa, bb, incoming, preserve=preserve)
            builder.pop_condition()
            builder.free(result)
        if subtract:
            builder.x(_c40_arithmetic_private__as_array(target))

    def _c40_arithmetic_private_signed_row(builder: _c40_arithmetic_private_km.CircuitBuilder, source: _c40_arithmetic_private_Sequence, target: _c40_arithmetic_private_Sequence, *, shift: int, sign, inverse: bool=False, nearest: bool=False, signed_source: bool=False, carry_budget: int | None=None) -> None:
        """Add (1-2sign)*scaled_source, with optional rounding before the sign.

    At negative shift -s, nearest uses exactly (source>>s)+bit(source,s-1).
    With signed_source=True the shift is arithmetic.  Ties round toward
    positive infinity for both signs.  The discarded rounding
    bit is the carry-in of the adder; it costs no additional quantum wire and
    no additional carry product versus the corresponding full-width addition.
    """
        source, target = (list(source), list(target))
        carry = False
        if shift >= 0:
            target = target[shift:]
        else:
            cut = -shift
            if signed_source and cut >= len(source):
                if nearest:
                    return
                source = source[-1:]
                cut = 0
            if nearest and cut - 1 < len(source):
                carry = source[cut - 1]
            source = source[cut:]
        if not target or (not source and carry is False):
            return
        source = source[:len(target)]
        if isinstance(sign, _c40_arithmetic_private_km.q) and sign in source + target + ([carry] if isinstance(carry, _c40_arithmetic_private_km.q) else []):
            raise ValueError('Sign must be disjoint from row data and rounding bit.')
        for q in target:
            builder.cx(sign, q)
        _c40_arithmetic_private_add(builder, source, target, carry_in=carry, subtract=inverse, signed_source=signed_source, carry_budget=carry_budget)
        for q in target:
            builder.cx(sign, q)

    def _c40_arithmetic_private_horner_rows(builder, residual, source, target, *, source_fraction, target_fraction, inverse=False, nearest=None, rounding='floor', signed_source=False, carry_budget=None):
        if rounding not in ('floor', 'nearest'):
            raise ValueError('rounding must be floor or nearest')
        if nearest is None:
            nearest = rounding == 'nearest'
        residual = list(residual)
        indices = reversed(range(len(residual))) if inverse else range(len(residual))
        for i in indices:
            _c40_arithmetic_private_signed_row(builder, source, target, shift=i - len(residual) - 1 + target_fraction - source_fraction, sign=residual[i], inverse=inverse, nearest=nearest, signed_source=signed_source, carry_budget=carry_budget)

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/compiler.py
def _initialize__c41_compiler():
    global _c41_compiler_INTEGRATED_ROOT, _c41_compiler_MAJORITY_TRUTH, _c41_compiler_QuadraticPlan, _c41_compiler__IntegratedPath, _c41_compiler___file__, _c41_compiler___name__, _c41_compiler__product_polynomial, _c41_compiler_anf_from_truth, _c41_compiler_annotations, _c41_compiler_dataclass, _c41_compiler_lru_cache, _c41_compiler_phase_quadratic, _c41_compiler_synthesize_quadratic, _c41_compiler_xor_quadratic
    'Small exact Boolean-window compiler, including phases.\n\nWindows are specified by truth tables generated from the mathematical kernel.\nNo serialized circuit is an input.  Quadratic XOR outputs are factored into\nthe minimum number of affine-linear products.  Quadratic sign outputs use\nonly Z and CZ gates.  Every proposed factorization is checked exhaustively.\n'
    pass
    _c41_compiler__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/compiler.py', False).Path
    _c41_compiler_INTEGRATED_ROOT = _c41_compiler__IntegratedPath(_c41_compiler___file__).resolve().parents[8]
    _c41_compiler_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/compiler.py', False).dataclass
    _c41_compiler_lru_cache = _import_component('functools', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/compiler.py', False).lru_cache

    def _c41_compiler_anf_from_truth(truth):
        coefficients = [int(v) & 1 for v in truth]
        n = (len(coefficients) - 1).bit_length()
        if len(coefficients) != 1 << n:
            raise ValueError('Truth table length must be a power of two.')
        for j in range(n):
            for mask in range(1 << n):
                if mask & 1 << j:
                    coefficients[mask] ^= coefficients[mask ^ 1 << j]
        return tuple((mask for mask, value in enumerate(coefficients) if value))

    def _c41_compiler__product_polynomial(left, right):
        out = set()
        for i in range(left.bit_length()):
            if not left >> i & 1:
                continue
            for j in range(right.bit_length()):
                if right >> j & 1:
                    mask = 1 << i | 1 << j
                    if mask in out:
                        out.remove(mask)
                    else:
                        out.add(mask)
        return out

    @_c41_compiler_dataclass(frozen=True)
    class _c41_compiler_QuadraticPlan:
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

    @_c41_compiler_lru_cache(maxsize=2048)
    def _c41_compiler_synthesize_quadratic(truth):
        truth = tuple(map(int, truth))
        n = (len(truth) - 1).bit_length()
        polynomial = set(_c41_compiler_anf_from_truth(truth))
        if any((mask.bit_count() > 2 for mask in polynomial)):
            raise ValueError('This exact window is not quadratic.')
        products = []
        while any((mask.bit_count() == 2 for mask in polynomial)):
            edge = min((mask for mask in polynomial if mask.bit_count() == 2))
            i, j = [k for k in range(n) if edge >> k & 1]
            left, right = (1 << i, 1 << j)
            for k in range(n):
                if k in (i, j):
                    continue
                if 1 << j | 1 << k in polynomial:
                    left |= 1 << k
                if 1 << i | 1 << k in polynomial:
                    right |= 1 << k
            polynomial.symmetric_difference_update(_c41_compiler__product_polynomial(left, right))
            products.append((left, right, i, j))
        result = _c41_compiler_QuadraticPlan(n, tuple(sorted(polynomial)), tuple(products), truth)
        if any((result.evaluate(x) != truth[x] for x in range(1 << n))):
            raise AssertionError('Internal synthesis certificate failed.')
        return result

    def _c41_compiler_xor_quadratic(builder, variables, target, truth):
        """XOR a quadratic Boolean window into target with minimum product rank.

    In-place CNOT frames form each affine factor on two pivot input wires.
    They are undone immediately, so no fresh qubits are required.  The rank
    lower bound applies to XOR/affine-product implementations of this window.
    """
        variables = list(variables)
        plan = _c41_compiler_synthesize_quadratic(tuple(truth))
        if len(variables) != plan.width or target in variables:
            raise ValueError('Distinct input wires and target are required.')
        for mask in plan.affine:
            if mask == 0:
                builder.x(target)
            else:
                builder.cx(variables[mask.bit_length() - 1], target)
        for left, right, i, j in plan.products:
            frames = [(variables[k], variables[i]) for k in range(plan.width) if k != i and left >> k & 1]
            frames += [(variables[k], variables[j]) for k in range(plan.width) if k != j and right >> k & 1]
            for a, b in frames:
                builder.cx(a, b)
            builder.ccx(variables[i], variables[j], target)
            for a, b in reversed(frames):
                builder.cx(a, b)
        return plan

    def _c41_compiler_phase_quadratic(builder, variables, truth):
        """Compile an exact sign window to Z/CZ only, including a constant sign."""
        variables = list(variables)
        anf = _c41_compiler_anf_from_truth(tuple(truth))
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
    _c41_compiler_MAJORITY_TRUTH = tuple((int(x.bit_count() >= 2) for x in range(8)))

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/lookup.py
def _initialize__c42_lookup():
    global _c42_lookup_INTEGRATED_ROOT, _c42_lookup__IntegratedPath, _c42_lookup___file__, _c42_lookup___name__, _c42_lookup__bits, _c42_lookup_algebraic_coefficients, _c42_lookup_annotations, _c42_lookup_km, _c42_lookup_load_table, _c42_lookup_lookup_plan, _c42_lookup_unload_table
    'From-table algebraic QROM with shared products and deferred fan-in.\n\nThe table is converted to its algebraic normal form by the Boolean Mobius\ntransform. A depth-first product tree computes a monomial once and fans it\ninto every coefficient bit that needs it. Temporary products use exact HMR\nand conditional-CZ deletion. At a leaf, a linear output frame lets the final\nAND target an existing output wire, so it needs no new temporary.\n\nFor an arbitrary full 8-bit table the construction needs at most 247 CCX\ngates, with six temporary qubits. Constants and affine monomials are free.\nThese are generic bounds; zero ANF columns prune whole branches. The table,\nincluding all coefficients and fan-in masks, is derived from the function\nvalues supplied by the mathematical coefficient generator.\n'
    pass
    _c42_lookup__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/lookup.py', False).Path
    _c42_lookup_INTEGRATED_ROOT = _c42_lookup__IntegratedPath(_c42_lookup___file__).resolve().parents[8]
    _c42_lookup_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/lookup.py', False)

    def _c42_lookup_algebraic_coefficients(table, address_bits=None):
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

    def _c42_lookup__bits(value):
        while value:
            bit = value & -value
            yield (bit.bit_length() - 1)
            value ^= bit

    def _c42_lookup_lookup_plan(table, address_bits=None):
        coefficients = _c42_lookup_algebraic_coefficients(table, address_bits)
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

    def _c42_lookup_load_table(builder, table, address, target):
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
        plan = _c42_lookup_lookup_plan(table, len(address))
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
            for index in _c42_lookup__bits(mask):
                builder.cx(control, target[index])

        def multiple_product(controls, mask):
            """XOR one product through an output frame, borrowing dirty data.

        With k>=3 controls and k-2 borrowed bits, a forward/reverse ladder
        followed by the same ladder without its first AND cancels every
        borrowed input term. Exactly the product of all controls survives on
        the target; every borrowed bit is restored. Cost is 4*k-8 CCX.
        """
            outputs = list(_c42_lookup__bits(mask))
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
                        controls = [product] + [address[bit] for bit in _c42_lookup__bits(descendant ^ mask)]
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

    def _c42_lookup_unload_table(builder, table, address, target):
        """Erase a table value, repaying every measurement outcome exactly.

    If the measured output mask is m, the required sign is
       (-1)**sum_j m_j * table[address]_j.
    Its algebraic normal form is bilinear in monomials of two disjoint
    address groups. One group's monomials are retained, while the other
    group's are streamed. Every cross term is a CZ, conditioned on a
    classically computed parity of the original measurement results.

    The output qubits have just been reset by HMR, so they themselves serve
    as workspace. For an 8-bit address, the balanced 4+4 split uses 22 ANDs
    and14 temporary wires; it is available whenever the target plus unused
    clean workspace supplies14 wires. Smaller splits reduce workspace.
    All target wires remain allocated and zero at return.
    """
        address, target = (list(address), list(target))
        if len(set(address + target)) != len(address) + len(target):
            raise ValueError('Unlookup requires disjoint address and target wires')
        coefficients = _c42_lookup_algebraic_coefficients(table, len(address))
        if any((value >= 1 << len(target) for value in coefficients)):
            raise ValueError('A table value exceeds target width')
        n = len(address)
        capacity = len(target) + builder.max_qubits - builder.num_allocated_qubits
        choices = []
        for left_count in range(n + 1):
            right_count = n - left_count
            left_products = (1 << left_count) - left_count - 1
            right_products = (1 << right_count) - right_count - 1
            workspace = left_products + max(0, right_count - 1)
            if workspace <= capacity:
                choices.append((left_products + right_products, workspace, left_count))
        if not choices:
            raise ValueError('Insufficient clean workspace for measurement table erasure')
        expected_ands, workspace_count, left_count = min(choices)
        right_count = n - left_count
        left_products = (1 << left_count) - left_count - 1
        extra_count = max(0, workspace_count - len(target))
        extra = list(builder.alloc_qubits(extra_count))
        workspace = (target + extra)[:workspace_count]
        outcomes = builder.alloc_bits(len(target))
        parity = builder.alloc_bits(1)[0]
        builder.hmr(_c42_lookup_km.array(target), outcomes)
        left = {1 << j: address[j] for j in range(left_count)}
        left_steps = []
        position = 0
        for mask in range(1, 1 << left_count):
            if mask.bit_count() < 2:
                continue
            last = mask.bit_length() - 1
            parent = mask ^ 1 << last
            temporary = workspace[position]
            position += 1
            builder.ccx(left[parent], address[last], temporary)
            left[mask] = temporary
            left_steps.append((left[parent], address[last], temporary))

        def sign_terms(right_mask, right_wire):
            for left_mask in range(1 << left_count):
                output_mask = coefficients[left_mask | right_mask << left_count]
                if not output_mask:
                    continue
                builder.bit_store(parity, False)
                for bit in _c42_lookup__bits(output_mask):
                    builder.cx(outcomes[bit], parity)
                if not left_mask and (not right_mask):
                    builder.z(parity)
                else:
                    builder.push_condition(parity)
                    if not left_mask:
                        builder.z(right_wire)
                    elif not right_mask:
                        builder.z(left[left_mask])
                    else:
                        builder.cz(left[left_mask], right_wire)
                    builder.pop_condition()

        def visit_right(mask, product, depth):
            sign_terms(mask, product)
            for bit in range(mask.bit_length(), right_count):
                temporary = workspace[left_products + depth]
                control = address[left_count + bit]
                builder.ccx(product, control, temporary)
                visit_right(mask | 1 << bit, temporary, depth + 1)
                builder.del_and(product, control, temporary)
        sign_terms(0, None)
        for bit in range(right_count):
            visit_right(1 << bit, address[left_count + bit], 0)
        for a, b, temporary in reversed(left_steps):
            builder.del_and(a, b, temporary)
        builder.free(_c42_lookup_km.array(extra))
        builder.free(outcomes)
        builder.free(parity)
        return {'and_count': expected_ands, 'workspace_qubits': workspace_count, 'extra_qubits': extra_count, 'left_address_bits': left_count}

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py
def _initialize__c43_paired_arithmetic():
    global _c43_paired_arithmetic_CarryDebt, _c43_paired_arithmetic_DeferredBoundedToken, _c43_paired_arithmetic_DeferredProductToken, _c43_paired_arithmetic_INTEGRATED_ROOT, _c43_paired_arithmetic_MAJORITY_TRUTH, _c43_paired_arithmetic__Frame, _c43_paired_arithmetic__IntegratedPath, _c43_paired_arithmetic___file__, _c43_paired_arithmetic___name__, _c43_paired_arithmetic__compute_carry, _c43_paired_arithmetic__deferred_overflow, _c43_paired_arithmetic__erase_carry, _c43_paired_arithmetic__finish_top, _c43_paired_arithmetic__inputs, _c43_paired_arithmetic__phase_borrow, _c43_paired_arithmetic__row_inputs, _c43_paired_arithmetic__segment_repay, _c43_paired_arithmetic__sum_keep_carry, _c43_paired_arithmetic__terminal_partition, _c43_paired_arithmetic_annotations, _c43_paired_arithmetic_dataclass, _c43_paired_arithmetic_dirty_mcz_cost, _c43_paired_arithmetic_forward_add, _c43_paired_arithmetic_forward_bounded_rows, _c43_paired_arithmetic_forward_growing_product, _c43_paired_arithmetic_forward_signed_row, _c43_paired_arithmetic_inverse_add, _c43_paired_arithmetic_inverse_bounded_rows, _c43_paired_arithmetic_inverse_growing_product, _c43_paired_arithmetic_inverse_signed_row, _c43_paired_arithmetic_km, _c43_paired_arithmetic_partition, _c43_paired_arithmetic_phase_quadratic, _c43_paired_arithmetic_release_saved_bit, _c43_paired_arithmetic_repay_saved_bit, _c43_paired_arithmetic_terminal_add, _c43_paired_arithmetic_terminal_cost, _c43_paired_arithmetic_terminal_dirty_count
    'Two-carry forward arithmetic with phase debts repaid during its inverse.\n\nOnly a compute/phase/uncompute pair is a complete operation.  A forward\nadder intentionally retains classical records of signs caused by measuring\ncarry wires.  The inverse subtraction recomputes exactly the same Boolean\ncarry functions and pays those signs by conditional Z before applying its\nordinary, exact carry cleanup.\n'
    pass
    _c43_paired_arithmetic__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).Path
    _c43_paired_arithmetic_INTEGRATED_ROOT = _c43_paired_arithmetic__IntegratedPath(_c43_paired_arithmetic___file__).resolve().parents[7]
    _c43_paired_arithmetic_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).dataclass
    _c43_paired_arithmetic_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)
    _c43_paired_arithmetic__Frame = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._Frame
    _c43_paired_arithmetic__compute_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._compute_carry
    _c43_paired_arithmetic__erase_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._erase_carry
    _c43_paired_arithmetic__sum_keep_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._sum_keep_carry
    _c43_paired_arithmetic__phase_borrow = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._phase_borrow
    _c43_paired_arithmetic_partition = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).partition
    _c43_paired_arithmetic_phase_quadratic = _import_component('fusion.compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).phase_quadratic
    _c43_paired_arithmetic_MAJORITY_TRUTH = _import_component('fusion.compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).MAJORITY_TRUTH
    _c43_paired_arithmetic_terminal_add = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).terminal_add
    _c43_paired_arithmetic_terminal_cost = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).terminal_cost
    _c43_paired_arithmetic_terminal_dirty_count = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).terminal_dirty_count
    _c43_paired_arithmetic_dirty_mcz_cost = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).dirty_mcz_cost

    @_c43_paired_arithmetic_dataclass
    class _c43_paired_arithmetic_CarryDebt:
        measurements: dict
        width: int
        consumed: bool = False

    def _c43_paired_arithmetic__finish_top(builder, a, b, incoming, preserve):
        """Two high sum bits; the last carry goes directly into the high bit."""
        aa, bb = (a[-2], b[-2])
        if aa == preserve and isinstance(incoming, _c43_paired_arithmetic_km.q):
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

    def _c43_paired_arithmetic__inputs(source, target, carry_in, signed_source):
        source, target = (list(source), list(target))
        width = len(target)
        source = source[:width]
        if any((not isinstance(q, _c43_paired_arithmetic_km.q) for q in source)):
            raise ValueError('Source must contain quantum wires.')
        if len(set(source + target)) != len(source) + len(target):
            raise ValueError('Source and target must be disjoint distinct wires.')
        if isinstance(carry_in, _c43_paired_arithmetic_km.q) and carry_in in source + target:
            raise ValueError('Carry-in must be disjoint from the data words.')
        if carry_in is not False and (not isinstance(carry_in, _c43_paired_arithmetic_km.q)):
            raise ValueError('Carry-in must be a quantum wire or False.')
        preserve = source[-1] if signed_source and source else None
        source += [preserve if preserve is not None else False] * (width - len(source))
        return (source, target, preserve)

    def _c43_paired_arithmetic_forward_add(builder, source, target, *, carry_in=False, signed_source=False):
        """target += source+carry_in, with two clean carries and deferred signs.

    The returned debt is mandatory: consume it in `inverse_add` after all
    changes to this target have been reversed.  Arbitrary diagonal phases
    and further reversible classical computation may intervene.
    """
        a, b, preserve = _c43_paired_arithmetic__inputs(source, target, carry_in, signed_source)
        width = len(b)
        debts = {}
        if not width:
            return _c43_paired_arithmetic_CarryDebt(debts, width)
        if width == 1:
            builder.cx(a[0], b[0])
            builder.cx(carry_in, b[0])
            return _c43_paired_arithmetic_CarryDebt(debts, width)

        def measure(carry, position):
            if carry is False:
                return
            outcome = builder.alloc_bits(1)[0]
            builder.hmr(carry, outcome)
            builder.free(carry)
            debts[position] = outcome
        carry = carry_in
        for index, (aa, bb) in enumerate(zip(a[:-2], b[:-2])):
            frame = _c43_paired_arithmetic__compute_carry(builder, aa, bb, carry, preserve=preserve)
            _c43_paired_arithmetic__sum_keep_carry(builder, frame)
            if index:
                measure(carry, index)
            carry = frame.outgoing
        _c43_paired_arithmetic__finish_top(builder, a, b, carry, preserve)
        if width > 2:
            measure(carry, width - 2)
        return _c43_paired_arithmetic_CarryDebt(debts, width)

    def _c43_paired_arithmetic__segment_repay(builder, a, b, incoming, *, retain_outgoing, preserve, start, debt, overflow_phase=None):

        def compute(aa, bb, carry, position):
            frame = _c43_paired_arithmetic__compute_carry(builder, aa, bb, carry, preserve=preserve)
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
            _c43_paired_arithmetic__sum_keep_carry(builder, frames[-1])
            for frame in reversed(frames[:-1]):
                _c43_paired_arithmetic__erase_carry(builder, frame, write_sum=True)
            return carry
        if n == 1:
            if overflow_phase is not None:
                builder.push_condition(overflow_phase)
                _c43_paired_arithmetic_phase_quadratic(builder, [a[0], b[0], incoming], _c43_paired_arithmetic_MAJORITY_TRUTH)
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
        _c43_paired_arithmetic__finish_top(builder, a, b, carry, preserve)
        for frame in reversed(frames):
            _c43_paired_arithmetic__erase_carry(builder, frame, write_sum=True)
        return False

    def _c43_paired_arithmetic__terminal_partition(a, b, incoming, clean, external_dirty, *, release_input=False, ordinary_final=False, allow_dirty_terminal=True, overflow_phase=False):
        """Cost a no-clean final segment only when the ordinary partition fails.

    Earlier target bits have already received their final values and can be
    borrowed as arbitrary dirty workspace. All borrowed bits are restored
    before the boundary-carry phase comparators execute.
    """
        width = len(b)
        states = {(0, 0): (0.0, ())}
        candidates = []
        original_source = [wire for wire in a if isinstance(wire, _c43_paired_arithmetic_km.q)]
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
                has_carry = isinstance(incoming, _c43_paired_arithmetic_km.q) or any((wire is not False for wire in a[:start]))
                if allow_dirty_terminal and has_carry and distinct and unsigned and (not overflow_phase or real < len(tail)):
                    forbidden = set(prefix + b[start:])
                    if not start and isinstance(incoming, _c43_paired_arithmetic_km.q):
                        forbidden.add(incoming)
                    pool = list(b[:start]) + original_source + list(external_dirty)
                    if start and isinstance(incoming, _c43_paired_arithmetic_km.q) and (not release_input):
                        pool.append(incoming)
                    pool = list(dict.fromkeys((wire for wire in pool if isinstance(wire, _c43_paired_arithmetic_km.q) and wire not in forbidden)))
                    needed = _c43_paired_arithmetic_terminal_dirty_count(width - start, real)
                    if len(pool) >= needed:
                        terminal = _c43_paired_arithmetic_terminal_cost(width - start, real)
                        if overflow_phase:
                            terminal += 0.5 * _c43_paired_arithmetic_dirty_mcz_cost(width - start - real + 1)
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

    def _c43_paired_arithmetic_inverse_add(builder, source, target, debt: _c43_paired_arithmetic_CarryDebt, *, carry_in=False, signed_source=False, carry_budget=None, dirty_wires=(), carry_lifecycle=None, overflow_phase=None, allow_dirty_overflow=False):
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
        a, b, preserve = _c43_paired_arithmetic__inputs(source, target, carry_in, signed_source)
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
            if signed_source or not isinstance(carry_in, _c43_paired_arithmetic_km.q):
                raise ValueError('Disposable incoming carry requires an unsigned quantum-carry adder.')
            sizes, terminal_dirty = _c43_paired_arithmetic__terminal_partition(a, b, carry_in, clean, dirty_wires, release_input=True, ordinary_final=True, allow_dirty_terminal=overflow_phase is None or allow_dirty_overflow, overflow_phase=overflow_phase is not None and allow_dirty_overflow)
        elif overflow_phase is not None and allow_dirty_overflow:
            sizes, terminal_dirty = _c43_paired_arithmetic__terminal_partition(a, b, carry_in, clean, dirty_wires, ordinary_final=True, overflow_phase=True)
        else:
            try:
                sizes = _c43_paired_arithmetic_partition(n, clean)
            except ValueError:
                if signed_source or overflow_phase is not None:
                    raise
                sizes, terminal_dirty = _c43_paired_arithmetic__terminal_partition(a, b, carry_in, clean, dirty_wires)
        builder.x(_c43_paired_arithmetic_km.array(b))
        boundaries = []
        start, carry = (0, carry_in)
        released_input = False
        for number, length in enumerate(sizes):
            aa, bb = (a[start:start + length], b[start:start + length])
            retain = number + 1 < len(sizes)
            if not retain and terminal_dirty is not None:
                _c43_paired_arithmetic_terminal_add(builder, aa, bb, carry, dirty=terminal_dirty, debt=debt, start=start, overflow_phase=overflow_phase)
                outgoing = False
            else:
                outgoing = _c43_paired_arithmetic__segment_repay(builder, aa, bb, carry, retain_outgoing=retain, preserve=preserve, start=start, debt=debt, overflow_phase=overflow_phase if not retain else None)
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
            _c43_paired_arithmetic__phase_borrow(builder, aa, bb, incoming, preserve=preserve)
            if recreated:
                carry_lifecycle[0](incoming)
            builder.pop_condition()
            builder.free(result)
        builder.x(_c43_paired_arithmetic_km.array(b))
        if debt.measurements:
            raise AssertionError(f'Unpaid carry positions: {sorted(debt.measurements)}')
        return released_input

    def _c43_paired_arithmetic__row_inputs(source, target, *, shift, nearest, signed_source):
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

    def _c43_paired_arithmetic_forward_signed_row(builder, source, target, *, shift, sign, nearest=True, signed_source=False):
        source, target, carry = _c43_paired_arithmetic__row_inputs(source, target, shift=shift, nearest=nearest, signed_source=signed_source)
        if isinstance(sign, _c43_paired_arithmetic_km.q) and sign in source + target + ([carry] if isinstance(carry, _c43_paired_arithmetic_km.q) else []):
            raise ValueError('Sign must be disjoint from row operands and rounding bit.')
        for wire in target:
            builder.cx(sign, wire)
        debt = _c43_paired_arithmetic_forward_add(builder, source, target, carry_in=carry, signed_source=signed_source)
        for wire in target:
            builder.cx(sign, wire)
        return debt

    def _c43_paired_arithmetic_inverse_signed_row(builder, source, target, debt, *, shift, sign, nearest=True, signed_source=False, carry_budget=None, overflow_phase=None, allow_dirty_overflow=False):
        source, target, carry = _c43_paired_arithmetic__row_inputs(source, target, shift=shift, nearest=nearest, signed_source=signed_source)
        if isinstance(sign, _c43_paired_arithmetic_km.q) and sign in source + target + ([carry] if isinstance(carry, _c43_paired_arithmetic_km.q) else []):
            raise ValueError('Sign must be disjoint from row operands and rounding bit.')
        for wire in target:
            builder.cx(sign, wire)
        _c43_paired_arithmetic_inverse_add(builder, source, target, debt, carry_in=carry, signed_source=signed_source, carry_budget=carry_budget, overflow_phase=overflow_phase, allow_dirty_overflow=allow_dirty_overflow)
        for wire in target:
            builder.cx(sign, wire)

    @_c43_paired_arithmetic_dataclass
    class _c43_paired_arithmetic_DeferredProductToken:
        plan: object
        row_debts: list

    def _c43_paired_arithmetic_forward_growing_product(builder, residual, source, plan, *, initial=()):
        """Increasing-width product with only two forward carry temporaries."""
        residual, source = (list(residual), list(source))
        accumulator = list(initial)
        if len(residual) != len(plan.shifts) or len(accumulator) != plan.initial_width:
            raise ValueError('Input widths do not match the growing-product plan.')
        debts = []
        for sign, shift, width in zip(residual, plan.shifts, plan.widths):
            if width > len(accumulator):
                more = list(builder.alloc_qubits(width - len(accumulator)))
                if accumulator:
                    for wire in more:
                        builder.cx(accumulator[-1], wire)
                accumulator.extend(more)
            debt = _c43_paired_arithmetic_forward_signed_row(builder, source, accumulator, shift=shift, sign=sign, nearest=plan.nearest, signed_source=plan.signed_source)
            debts.append(debt)
        return (_c43_paired_arithmetic_km.array(accumulator), _c43_paired_arithmetic_DeferredProductToken(plan, debts))

    def _c43_paired_arithmetic_inverse_growing_product(builder, residual, source, accumulator, token, *, carry_budget=None):
        """Repay row debts while reversing and shrinking the product word."""
        residual, source, accumulator = (list(residual), list(source), list(accumulator))
        plan = token.plan
        for index in reversed(range(len(residual))):
            width = plan.widths[index]
            _c43_paired_arithmetic_inverse_signed_row(builder, source, accumulator, token.row_debts[index], shift=plan.shifts[index], sign=residual[index], nearest=plan.nearest, signed_source=plan.signed_source, carry_budget=carry_budget)
            previous = plan.widths[index - 1] if index else plan.initial_width
            if previous < width:
                dead = accumulator[previous:]
                if previous:
                    for wire in dead:
                        builder.cx(accumulator[previous - 1], wire)
                builder.free(_c43_paired_arithmetic_km.array(dead))
                accumulator = accumulator[:previous]
        return _c43_paired_arithmetic_km.array(accumulator)

    @_c43_paired_arithmetic_dataclass
    class _c43_paired_arithmetic_DeferredBoundedToken:
        plan: object
        saved_bit: object
        window: int
        row_debts: list
        overflow_debt: object = None

    def _c43_paired_arithmetic_release_saved_bit(builder, saved):
        """Release a saved original bit; repay it after the original is restored."""
        outcome = builder.alloc_bits(1)[0]
        builder.hmr(saved, outcome)
        builder.free(saved)
        return outcome

    def _c43_paired_arithmetic_repay_saved_bit(builder, restored, outcome):
        """Cancel the release sign using the now-restored original bit."""
        builder.push_condition(outcome)
        builder.z(restored)
        builder.pop_condition()
        builder.free(outcome)

    def _c43_paired_arithmetic__deferred_overflow(builder, residual, source, target, token, *, inverse, carry_budget=None, overflow_phase=None, allow_dirty_overflow=False):
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
            _c43_paired_arithmetic_inverse_add(builder, [], high, token.overflow_debt, carry_in=wrap, carry_budget=carry_budget, dirty_wires=target[:token.window], overflow_phase=overflow_phase, allow_dirty_overflow=allow_dirty_overflow)
        else:
            token.overflow_debt = _c43_paired_arithmetic_forward_add(builder, [], high, carry_in=wrap)
        for wire in high:
            builder.cx(sigma, wire)
        builder.del_and(saved, top, wrap)
        builder.free(wrap)
        builder.x(top)
        builder.cx(sigma, top)
        builder.cx(sigma, saved)
        if token.plan.signed_source:
            builder.cx(source[-1], sigma)

    def _c43_paired_arithmetic_forward_bounded_rows(builder, residual, source, target, plan):
        """Bounded modular rows with deferred phases and two forward carries."""
        residual, source, target = (list(residual), list(source), list(target))
        if len(residual) != plan.digits:
            raise ValueError('Residual width does not match the bounded-row plan.')
        width = min(plan.window, len(target))
        saved = None
        if 0 < width < len(target):
            saved = builder.alloc_qubits(1)[0]
            builder.cx(target[width - 1], saved)
        token = _c43_paired_arithmetic_DeferredBoundedToken(plan, saved, width, [])
        if width:
            for index, shift in zip(range(plan.first, plan.last), plan.shifts):
                token.row_debts.append(_c43_paired_arithmetic_forward_signed_row(builder, source, target[:width], shift=shift, sign=residual[index], signed_source=plan.signed_source))
            _c43_paired_arithmetic__deferred_overflow(builder, residual, source, target, token, inverse=False)
        return token

    def _c43_paired_arithmetic_inverse_bounded_rows(builder, residual, source, target, token, *, carry_budget=None):
        """Reverse bounded rows, repaying the recorded signs before releasing them."""
        residual, source, target = (list(residual), list(source), list(target))
        plan = token.plan
        saved_debt = None
        if token.window:
            _c43_paired_arithmetic__deferred_overflow(builder, residual, source, target, token, inverse=True, carry_budget=carry_budget)
            if token.saved_bit is not None:
                saved_debt = _c43_paired_arithmetic_release_saved_bit(builder, token.saved_bit)
            for j in reversed(range(plan.last - plan.first)):
                index, shift = (plan.first + j, plan.shifts[j])
                _c43_paired_arithmetic_inverse_signed_row(builder, source, target[:token.window], token.row_debts[j], shift=shift, sign=residual[index], signed_source=plan.signed_source, carry_budget=carry_budget)
        if saved_debt is not None:
            _c43_paired_arithmetic_repay_saved_bit(builder, target[token.window - 1], saved_debt)

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py [independent arithmetic context]
def _initialize__c43_paired_arithmetic_private():
    global _c43_paired_arithmetic_private_CarryDebt, _c43_paired_arithmetic_private_DeferredBoundedToken, _c43_paired_arithmetic_private_DeferredProductToken, _c43_paired_arithmetic_private_INTEGRATED_ROOT, _c43_paired_arithmetic_private_MAJORITY_TRUTH, _c43_paired_arithmetic_private__Frame, _c43_paired_arithmetic_private__IntegratedPath, _c43_paired_arithmetic_private___file__, _c43_paired_arithmetic_private___name__, _c43_paired_arithmetic_private__compute_carry, _c43_paired_arithmetic_private__deferred_overflow, _c43_paired_arithmetic_private__erase_carry, _c43_paired_arithmetic_private__finish_top, _c43_paired_arithmetic_private__inputs, _c43_paired_arithmetic_private__phase_borrow, _c43_paired_arithmetic_private__row_inputs, _c43_paired_arithmetic_private__segment_repay, _c43_paired_arithmetic_private__sum_keep_carry, _c43_paired_arithmetic_private__terminal_partition, _c43_paired_arithmetic_private_annotations, _c43_paired_arithmetic_private_dataclass, _c43_paired_arithmetic_private_dirty_mcz_cost, _c43_paired_arithmetic_private_forward_add, _c43_paired_arithmetic_private_forward_bounded_rows, _c43_paired_arithmetic_private_forward_growing_product, _c43_paired_arithmetic_private_forward_signed_row, _c43_paired_arithmetic_private_inverse_add, _c43_paired_arithmetic_private_inverse_bounded_rows, _c43_paired_arithmetic_private_inverse_growing_product, _c43_paired_arithmetic_private_inverse_signed_row, _c43_paired_arithmetic_private_km, _c43_paired_arithmetic_private_partition, _c43_paired_arithmetic_private_phase_quadratic, _c43_paired_arithmetic_private_release_saved_bit, _c43_paired_arithmetic_private_repay_saved_bit, _c43_paired_arithmetic_private_terminal_add, _c43_paired_arithmetic_private_terminal_cost, _c43_paired_arithmetic_private_terminal_dirty_count
    'Two-carry forward arithmetic with phase debts repaid during its inverse.\n\nOnly a compute/phase/uncompute pair is a complete operation.  A forward\nadder intentionally retains classical records of signs caused by measuring\ncarry wires.  The inverse subtraction recomputes exactly the same Boolean\ncarry functions and pays those signs by conditional Z before applying its\nordinary, exact carry cleanup.\n'
    pass
    _c43_paired_arithmetic_private__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).Path
    _c43_paired_arithmetic_private_INTEGRATED_ROOT = _c43_paired_arithmetic_private__IntegratedPath(_c43_paired_arithmetic_private___file__).resolve().parents[7]
    _c43_paired_arithmetic_private_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).dataclass
    _c43_paired_arithmetic_private_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)
    _c43_paired_arithmetic_private__Frame = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._Frame
    _c43_paired_arithmetic_private__compute_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._compute_carry
    _c43_paired_arithmetic_private__erase_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._erase_carry
    _c43_paired_arithmetic_private__sum_keep_carry = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._sum_keep_carry
    _c43_paired_arithmetic_private__phase_borrow = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False)._phase_borrow
    _c43_paired_arithmetic_private_partition = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).partition
    _c43_paired_arithmetic_private_phase_quadratic = _import_component('fusion.compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).phase_quadratic
    _c43_paired_arithmetic_private_MAJORITY_TRUTH = _import_component('fusion.compiler', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).MAJORITY_TRUTH
    _c43_paired_arithmetic_private_terminal_add = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).terminal_add
    _c43_paired_arithmetic_private_terminal_cost = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).terminal_cost
    _c43_paired_arithmetic_private_terminal_dirty_count = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).terminal_dirty_count
    _c43_paired_arithmetic_private_dirty_mcz_cost = _import_component('dirty_terminal', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', False).dirty_mcz_cost

    @_c43_paired_arithmetic_private_dataclass
    class _c43_paired_arithmetic_private_CarryDebt:
        measurements: dict
        width: int
        consumed: bool = False

    def _c43_paired_arithmetic_private__finish_top(builder, a, b, incoming, preserve):
        """Two high sum bits; the last carry goes directly into the high bit."""
        aa, bb = (a[-2], b[-2])
        if aa == preserve and isinstance(incoming, _c43_paired_arithmetic_private_km.q):
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

    def _c43_paired_arithmetic_private__inputs(source, target, carry_in, signed_source):
        source, target = (list(source), list(target))
        width = len(target)
        source = source[:width]
        if any((not isinstance(q, _c43_paired_arithmetic_private_km.q) for q in source)):
            raise ValueError('Source must contain quantum wires.')
        if len(set(source + target)) != len(source) + len(target):
            raise ValueError('Source and target must be disjoint distinct wires.')
        if isinstance(carry_in, _c43_paired_arithmetic_private_km.q) and carry_in in source + target:
            raise ValueError('Carry-in must be disjoint from the data words.')
        if carry_in is not False and (not isinstance(carry_in, _c43_paired_arithmetic_private_km.q)):
            raise ValueError('Carry-in must be a quantum wire or False.')
        preserve = source[-1] if signed_source and source else None
        source += [preserve if preserve is not None else False] * (width - len(source))
        return (source, target, preserve)

    def _c43_paired_arithmetic_private_forward_add(builder, source, target, *, carry_in=False, signed_source=False):
        """target += source+carry_in, with two clean carries and deferred signs.

    The returned debt is mandatory: consume it in `inverse_add` after all
    changes to this target have been reversed.  Arbitrary diagonal phases
    and further reversible classical computation may intervene.
    """
        a, b, preserve = _c43_paired_arithmetic_private__inputs(source, target, carry_in, signed_source)
        width = len(b)
        debts = {}
        if not width:
            return _c43_paired_arithmetic_private_CarryDebt(debts, width)
        if width == 1:
            builder.cx(a[0], b[0])
            builder.cx(carry_in, b[0])
            return _c43_paired_arithmetic_private_CarryDebt(debts, width)

        def measure(carry, position):
            if carry is False:
                return
            outcome = builder.alloc_bits(1)[0]
            builder.hmr(carry, outcome)
            builder.free(carry)
            debts[position] = outcome
        carry = carry_in
        for index, (aa, bb) in enumerate(zip(a[:-2], b[:-2])):
            frame = _c43_paired_arithmetic_private__compute_carry(builder, aa, bb, carry, preserve=preserve)
            _c43_paired_arithmetic_private__sum_keep_carry(builder, frame)
            if index:
                measure(carry, index)
            carry = frame.outgoing
        _c43_paired_arithmetic_private__finish_top(builder, a, b, carry, preserve)
        if width > 2:
            measure(carry, width - 2)
        return _c43_paired_arithmetic_private_CarryDebt(debts, width)

    def _c43_paired_arithmetic_private__segment_repay(builder, a, b, incoming, *, retain_outgoing, preserve, start, debt, overflow_phase=None):

        def compute(aa, bb, carry, position):
            frame = _c43_paired_arithmetic_private__compute_carry(builder, aa, bb, carry, preserve=preserve)
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
            _c43_paired_arithmetic_private__sum_keep_carry(builder, frames[-1])
            for frame in reversed(frames[:-1]):
                _c43_paired_arithmetic_private__erase_carry(builder, frame, write_sum=True)
            return carry
        if n == 1:
            if overflow_phase is not None:
                builder.push_condition(overflow_phase)
                _c43_paired_arithmetic_private_phase_quadratic(builder, [a[0], b[0], incoming], _c43_paired_arithmetic_private_MAJORITY_TRUTH)
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
        _c43_paired_arithmetic_private__finish_top(builder, a, b, carry, preserve)
        for frame in reversed(frames):
            _c43_paired_arithmetic_private__erase_carry(builder, frame, write_sum=True)
        return False

    def _c43_paired_arithmetic_private__terminal_partition(a, b, incoming, clean, external_dirty, *, release_input=False, ordinary_final=False, allow_dirty_terminal=True, overflow_phase=False):
        """Cost a no-clean final segment only when the ordinary partition fails.

    Earlier target bits have already received their final values and can be
    borrowed as arbitrary dirty workspace. All borrowed bits are restored
    before the boundary-carry phase comparators execute.
    """
        width = len(b)
        states = {(0, 0): (0.0, ())}
        candidates = []
        original_source = [wire for wire in a if isinstance(wire, _c43_paired_arithmetic_private_km.q)]
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
                has_carry = isinstance(incoming, _c43_paired_arithmetic_private_km.q) or any((wire is not False for wire in a[:start]))
                if allow_dirty_terminal and has_carry and distinct and unsigned and (not overflow_phase or real < len(tail)):
                    forbidden = set(prefix + b[start:])
                    if not start and isinstance(incoming, _c43_paired_arithmetic_private_km.q):
                        forbidden.add(incoming)
                    pool = list(b[:start]) + original_source + list(external_dirty)
                    if start and isinstance(incoming, _c43_paired_arithmetic_private_km.q) and (not release_input):
                        pool.append(incoming)
                    pool = list(dict.fromkeys((wire for wire in pool if isinstance(wire, _c43_paired_arithmetic_private_km.q) and wire not in forbidden)))
                    needed = _c43_paired_arithmetic_private_terminal_dirty_count(width - start, real)
                    if len(pool) >= needed:
                        terminal = _c43_paired_arithmetic_private_terminal_cost(width - start, real)
                        if overflow_phase:
                            terminal += 0.5 * _c43_paired_arithmetic_private_dirty_mcz_cost(width - start - real + 1)
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

    def _c43_paired_arithmetic_private_inverse_add(builder, source, target, debt: _c43_paired_arithmetic_private_CarryDebt, *, carry_in=False, signed_source=False, carry_budget=None, dirty_wires=(), carry_lifecycle=None, overflow_phase=None, allow_dirty_overflow=False):
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
        a, b, preserve = _c43_paired_arithmetic_private__inputs(source, target, carry_in, signed_source)
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
            if signed_source or not isinstance(carry_in, _c43_paired_arithmetic_private_km.q):
                raise ValueError('Disposable incoming carry requires an unsigned quantum-carry adder.')
            sizes, terminal_dirty = _c43_paired_arithmetic_private__terminal_partition(a, b, carry_in, clean, dirty_wires, release_input=True, ordinary_final=True, allow_dirty_terminal=overflow_phase is None or allow_dirty_overflow, overflow_phase=overflow_phase is not None and allow_dirty_overflow)
        elif overflow_phase is not None and allow_dirty_overflow:
            sizes, terminal_dirty = _c43_paired_arithmetic_private__terminal_partition(a, b, carry_in, clean, dirty_wires, ordinary_final=True, overflow_phase=True)
        else:
            try:
                sizes = _c43_paired_arithmetic_private_partition(n, clean)
            except ValueError:
                if signed_source or overflow_phase is not None:
                    raise
                sizes, terminal_dirty = _c43_paired_arithmetic_private__terminal_partition(a, b, carry_in, clean, dirty_wires)
        builder.x(_c43_paired_arithmetic_private_km.array(b))
        boundaries = []
        start, carry = (0, carry_in)
        released_input = False
        for number, length in enumerate(sizes):
            aa, bb = (a[start:start + length], b[start:start + length])
            retain = number + 1 < len(sizes)
            if not retain and terminal_dirty is not None:
                _c43_paired_arithmetic_private_terminal_add(builder, aa, bb, carry, dirty=terminal_dirty, debt=debt, start=start, overflow_phase=overflow_phase)
                outgoing = False
            else:
                outgoing = _c43_paired_arithmetic_private__segment_repay(builder, aa, bb, carry, retain_outgoing=retain, preserve=preserve, start=start, debt=debt, overflow_phase=overflow_phase if not retain else None)
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
            _c43_paired_arithmetic_private__phase_borrow(builder, aa, bb, incoming, preserve=preserve)
            if recreated:
                carry_lifecycle[0](incoming)
            builder.pop_condition()
            builder.free(result)
        builder.x(_c43_paired_arithmetic_private_km.array(b))
        if debt.measurements:
            raise AssertionError(f'Unpaid carry positions: {sorted(debt.measurements)}')
        return released_input

    def _c43_paired_arithmetic_private__row_inputs(source, target, *, shift, nearest, signed_source):
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

    def _c43_paired_arithmetic_private_forward_signed_row(builder, source, target, *, shift, sign, nearest=True, signed_source=False):
        source, target, carry = _c43_paired_arithmetic_private__row_inputs(source, target, shift=shift, nearest=nearest, signed_source=signed_source)
        if isinstance(sign, _c43_paired_arithmetic_private_km.q) and sign in source + target + ([carry] if isinstance(carry, _c43_paired_arithmetic_private_km.q) else []):
            raise ValueError('Sign must be disjoint from row operands and rounding bit.')
        for wire in target:
            builder.cx(sign, wire)
        debt = _c43_paired_arithmetic_private_forward_add(builder, source, target, carry_in=carry, signed_source=signed_source)
        for wire in target:
            builder.cx(sign, wire)
        return debt

    def _c43_paired_arithmetic_private_inverse_signed_row(builder, source, target, debt, *, shift, sign, nearest=True, signed_source=False, carry_budget=None, overflow_phase=None, allow_dirty_overflow=False):
        source, target, carry = _c43_paired_arithmetic_private__row_inputs(source, target, shift=shift, nearest=nearest, signed_source=signed_source)
        if isinstance(sign, _c43_paired_arithmetic_private_km.q) and sign in source + target + ([carry] if isinstance(carry, _c43_paired_arithmetic_private_km.q) else []):
            raise ValueError('Sign must be disjoint from row operands and rounding bit.')
        for wire in target:
            builder.cx(sign, wire)
        _c43_paired_arithmetic_private_inverse_add(builder, source, target, debt, carry_in=carry, signed_source=signed_source, carry_budget=carry_budget, overflow_phase=overflow_phase, allow_dirty_overflow=allow_dirty_overflow)
        for wire in target:
            builder.cx(sign, wire)

    @_c43_paired_arithmetic_private_dataclass
    class _c43_paired_arithmetic_private_DeferredProductToken:
        plan: object
        row_debts: list

    def _c43_paired_arithmetic_private_forward_growing_product(builder, residual, source, plan, *, initial=()):
        """Increasing-width product with only two forward carry temporaries."""
        residual, source = (list(residual), list(source))
        accumulator = list(initial)
        if len(residual) != len(plan.shifts) or len(accumulator) != plan.initial_width:
            raise ValueError('Input widths do not match the growing-product plan.')
        debts = []
        for sign, shift, width in zip(residual, plan.shifts, plan.widths):
            if width > len(accumulator):
                more = list(builder.alloc_qubits(width - len(accumulator)))
                if accumulator:
                    for wire in more:
                        builder.cx(accumulator[-1], wire)
                accumulator.extend(more)
            debt = _c43_paired_arithmetic_private_forward_signed_row(builder, source, accumulator, shift=shift, sign=sign, nearest=plan.nearest, signed_source=plan.signed_source)
            debts.append(debt)
        return (_c43_paired_arithmetic_private_km.array(accumulator), _c43_paired_arithmetic_private_DeferredProductToken(plan, debts))

    def _c43_paired_arithmetic_private_inverse_growing_product(builder, residual, source, accumulator, token, *, carry_budget=None):
        """Repay row debts while reversing and shrinking the product word."""
        residual, source, accumulator = (list(residual), list(source), list(accumulator))
        plan = token.plan
        for index in reversed(range(len(residual))):
            width = plan.widths[index]
            _c43_paired_arithmetic_private_inverse_signed_row(builder, source, accumulator, token.row_debts[index], shift=plan.shifts[index], sign=residual[index], nearest=plan.nearest, signed_source=plan.signed_source, carry_budget=carry_budget)
            previous = plan.widths[index - 1] if index else plan.initial_width
            if previous < width:
                dead = accumulator[previous:]
                if previous:
                    for wire in dead:
                        builder.cx(accumulator[previous - 1], wire)
                builder.free(_c43_paired_arithmetic_private_km.array(dead))
                accumulator = accumulator[:previous]
        return _c43_paired_arithmetic_private_km.array(accumulator)

    @_c43_paired_arithmetic_private_dataclass
    class _c43_paired_arithmetic_private_DeferredBoundedToken:
        plan: object
        saved_bit: object
        window: int
        row_debts: list
        overflow_debt: object = None

    def _c43_paired_arithmetic_private_release_saved_bit(builder, saved):
        """Release a saved original bit; repay it after the original is restored."""
        outcome = builder.alloc_bits(1)[0]
        builder.hmr(saved, outcome)
        builder.free(saved)
        return outcome

    def _c43_paired_arithmetic_private_repay_saved_bit(builder, restored, outcome):
        """Cancel the release sign using the now-restored original bit."""
        builder.push_condition(outcome)
        builder.z(restored)
        builder.pop_condition()
        builder.free(outcome)

    def _c43_paired_arithmetic_private__deferred_overflow(builder, residual, source, target, token, *, inverse, carry_budget=None, overflow_phase=None, allow_dirty_overflow=False):
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
            _c43_paired_arithmetic_private_inverse_add(builder, [], high, token.overflow_debt, carry_in=wrap, carry_budget=carry_budget, dirty_wires=target[:token.window], overflow_phase=overflow_phase, allow_dirty_overflow=allow_dirty_overflow)
        else:
            token.overflow_debt = _c43_paired_arithmetic_private_forward_add(builder, [], high, carry_in=wrap)
        for wire in high:
            builder.cx(sigma, wire)
        builder.del_and(saved, top, wrap)
        builder.free(wrap)
        builder.x(top)
        builder.cx(sigma, top)
        builder.cx(sigma, saved)
        if token.plan.signed_source:
            builder.cx(source[-1], sigma)

    def _c43_paired_arithmetic_private_forward_bounded_rows(builder, residual, source, target, plan):
        """Bounded modular rows with deferred phases and two forward carries."""
        residual, source, target = (list(residual), list(source), list(target))
        if len(residual) != plan.digits:
            raise ValueError('Residual width does not match the bounded-row plan.')
        width = min(plan.window, len(target))
        saved = None
        if 0 < width < len(target):
            saved = builder.alloc_qubits(1)[0]
            builder.cx(target[width - 1], saved)
        token = _c43_paired_arithmetic_private_DeferredBoundedToken(plan, saved, width, [])
        if width:
            for index, shift in zip(range(plan.first, plan.last), plan.shifts):
                token.row_debts.append(_c43_paired_arithmetic_private_forward_signed_row(builder, source, target[:width], shift=shift, sign=residual[index], signed_source=plan.signed_source))
            _c43_paired_arithmetic_private__deferred_overflow(builder, residual, source, target, token, inverse=False)
        return token

    def _c43_paired_arithmetic_private_inverse_bounded_rows(builder, residual, source, target, token, *, carry_budget=None):
        """Reverse bounded rows, repaying the recorded signs before releasing them."""
        residual, source, target = (list(residual), list(source), list(target))
        plan = token.plan
        saved_debt = None
        if token.window:
            _c43_paired_arithmetic_private__deferred_overflow(builder, residual, source, target, token, inverse=True, carry_budget=carry_budget)
            if token.saved_bit is not None:
                saved_debt = _c43_paired_arithmetic_private_release_saved_bit(builder, token.saved_bit)
            for j in reversed(range(plan.last - plan.first)):
                index, shift = (plan.first + j, plan.shifts[j])
                _c43_paired_arithmetic_private_inverse_signed_row(builder, source, target[:token.window], token.row_debts[j], shift=shift, sign=residual[index], signed_source=plan.signed_source, carry_budget=carry_budget)
        if saved_debt is not None:
            _c43_paired_arithmetic_private_repay_saved_bit(builder, target[token.window - 1], saved_debt)

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/quadratic_terms.py
def _initialize__c44_quadratic_terms():
    global _c44_quadratic_terms_INTEGRATED_ROOT, _c44_quadratic_terms_PolynomialPlan, _c44_quadratic_terms__IntegratedPath, _c44_quadratic_terms___file__, _c44_quadratic_terms___name__, _c44_quadratic_terms_annotations, _c44_quadratic_terms_compile_polynomial, _c44_quadratic_terms_dataclass, _c44_quadratic_terms_gf2_rank, _c44_quadratic_terms_product_terms, _c44_quadratic_terms_xor_polynomial
    'Exact product-rank compilation from quadratic ANF, without large tables.'
    pass
    _c44_quadratic_terms__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/quadratic_terms.py', False).Path
    _c44_quadratic_terms_INTEGRATED_ROOT = _c44_quadratic_terms__IntegratedPath(_c44_quadratic_terms___file__).resolve().parents[7]
    _c44_quadratic_terms_dataclass = _import_component('dataclasses', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/quadratic_terms.py', False).dataclass

    def _c44_quadratic_terms_product_terms(left, right):
        terms = set()
        for i in range(left.bit_length()):
            if not left >> i & 1:
                continue
            for j in range(right.bit_length()):
                if right >> j & 1:
                    key = 1 << i | 1 << j
                    terms.symmetric_difference_update((key,))
        return terms

    def _c44_quadratic_terms_gf2_rank(rows):
        pivots = {}
        for row in rows:
            while row:
                pivot = row.bit_length() - 1
                if pivot not in pivots:
                    pivots[pivot] = row
                    break
                row ^= pivots[pivot]
        return len(pivots)

    @_c44_quadratic_terms_dataclass(frozen=True)
    class _c44_quadratic_terms_PolynomialPlan:
        width: int
        affine: tuple[int, ...]
        products: tuple[tuple[int, int, int, int], ...]
        original: tuple[int, ...]
        alternating_rank: int

    def _c44_quadratic_terms_compile_polynomial(width, terms):
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
        rank = _c44_quadratic_terms_gf2_rank(matrix)
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
            remaining.symmetric_difference_update(_c44_quadratic_terms_product_terms(left, right))
            products.append((left, right, i, j))
        recovered = set(remaining)
        for left, right, _, _ in products:
            recovered.symmetric_difference_update(_c44_quadratic_terms_product_terms(left, right))
        if recovered != set(original) or len(products) * 2 != rank:
            raise AssertionError('Quadratic synthesis certificate failed.')
        return _c44_quadratic_terms_PolynomialPlan(width, tuple(sorted(remaining)), tuple(products), original, rank)

    def _c44_quadratic_terms_xor_polynomial(builder, variables, target, terms):
        """Emit a rank-minimal AND/XOR realization, preserving all input wires."""
        variables = list(variables)
        if len(set(variables)) != len(variables) or target in variables:
            raise ValueError('Input variables and target must be distinct.')
        plan = _c44_quadratic_terms_compile_polynomial(len(variables), terms)
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

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/stage94_bit_routing_math.py
def _initialize__c45_stage94_bit_routing_math():
    global _c45_stage94_bit_routing_math_INTEGRATED_ROOT, _c45_stage94_bit_routing_math__IntegratedPath, _c45_stage94_bit_routing_math___file__, _c45_stage94_bit_routing_math___name__, _c45_stage94_bit_routing_math_annotations, _c45_stage94_bit_routing_math_certificate, _c45_stage94_bit_routing_math_leading_indicator_terms, _c45_stage94_bit_routing_math_lru_cache, _c45_stage94_bit_routing_math_operations, _c45_stage94_bit_routing_math_prefix_expression, _c45_stage94_bit_routing_math_selector_value
    'Exact binary butterfly for zero-supported normalization payloads.\n\nAfter removing the leading one, a twenty-two-bit positive word has a\ntwenty-one-bit payload.  If ell is its original leading-zero count, every\nlive payload symbol at position i satisfies i+ell <= 20.  A low-bit-first\nbinary butterfly adds ell to each physical position label.\n\nAt stage j the lower position bits have already been added.  Their carry\nis therefore [position mod 2**j < ell mod 2**j].  XORing this carry with\nbit j of ell gives the exact selector for the pair differing in bit j.\nVirtual pairs outside the payload contain zero throughout every valid\ncase, so they need no physical wires or gates.  All controls are freshly\nderived functions of ell, available as parities of its prefix thresholds.\n'
    pass
    _c45_stage94_bit_routing_math__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/stage94_bit_routing_math.py', False).Path
    _c45_stage94_bit_routing_math_INTEGRATED_ROOT = _c45_stage94_bit_routing_math__IntegratedPath(_c45_stage94_bit_routing_math___file__).resolve().parents[7]
    _c45_stage94_bit_routing_math_lru_cache = _import_component('functools', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/stage94_bit_routing_math.py', False).lru_cache

    def _c45_stage94_bit_routing_math_selector_value(leading_zeros, position, stage):
        """Return the bit-j addition selector at a current butterfly position."""
        modulus = 1 << stage
        return leading_zeros >> stage & 1 ^ int(position % modulus < leading_zeros % modulus)

    def _c45_stage94_bit_routing_math_prefix_expression(truth, maximum):
        """Express a finite function in P_j=[ell>=j], including P_0=1."""
        if not isinstance(truth, int) or truth < 0 or truth >> maximum + 1:
            raise ValueError('A leading-zero truth mask has the wrong finite domain.')
        terms = tuple((index for index in range(maximum + 1) if truth >> index & 1 ^ (truth >> index - 1 & 1 if index else 0)))
        for leading_zeros in range(maximum + 1):
            actual = sum((leading_zeros >= term for term in terms)) & 1
            if actual != truth >> leading_zeros & 1:
                raise AssertionError('A prefix expansion failed its exact finite-domain identity.')
        return terms

    def _c45_stage94_bit_routing_math_operations(payload_width=21):
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
                truth = sum((_c45_stage94_bit_routing_math_selector_value(leading_zeros, first, stage) << leading_zeros for leading_zeros in range(payload_width + 1)))
                result.append(dict(stage=stage, first=first, second=second, selector_truth=truth, prefix_terms=_c45_stage94_bit_routing_math_prefix_expression(truth, payload_width)))
        return tuple(result)

    @_c45_stage94_bit_routing_math_lru_cache(maxsize=8)
    def _c45_stage94_bit_routing_math_certificate(payload_width=21):
        """Certify all payload symbols, all controls, and both route directions."""
        route = _c45_stage94_bit_routing_math_operations(payload_width)
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
                    position ^= _c45_stage94_bit_routing_math_selector_value(leading_zeros, position, stage) << stage
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
                    if not _c45_stage94_bit_routing_math_selector_value(leading_zeros, first, stage):
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

    def _c45_stage94_bit_routing_math_leading_indicator_terms(position, input_width=22):
        """Return the prefix parity selecting a word's original leading one.

P_0 is the constant one, and P_input_width is zero for a positive input.
The caller treats the returned zero index as an unconditional X.
"""
        if not 0 <= position < input_width:
            raise ValueError('A leading-one position must belong to its input word.')
        first = input_width - 1 - position
        return tuple((index for index in (first, first + 1) if index < input_width))

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/thermometer_cleanup.py
def _initialize__c46_thermometer_cleanup():
    global _c46_thermometer_cleanup_INTEGRATED_ROOT, _c46_thermometer_cleanup__IntegratedPath, _c46_thermometer_cleanup___file__, _c46_thermometer_cleanup___name__, _c46_thermometer_cleanup_annotations, _c46_thermometer_cleanup_binary_to_thermometer, _c46_thermometer_cleanup_erase_pair_count_thermometer, _c46_thermometer_cleanup_km, _c46_thermometer_cleanup_linear_frame, _c46_thermometer_cleanup_thermometer_matrix
    'Erase binary leading-zero-pair counts through a small thermometer basis.\n\nFor k in0..m, the m nonconstant monomials with masks1..m and the m threshold\nfunctions [k>=j] are two linear bases of the same Boolean function space.\nOnly m-bit_length(m) monomials need AND gates; the other monomials are input\nflags. An invertible CNOT/SWAP frame converts those wires into thresholds.\n\nAfter the original input is restored, t_j=t_(j-1)*(1-a_j)*(1-b_j).\nMeasure thresholds top-down. Their exact measurement signs are a conditioned\nCCZ for j>=2, and a conditioned CZ for j=1. This is valid for both outcomes\nat every step and never assumes that an observed outcome remains absent.\n'
    pass
    _c46_thermometer_cleanup__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/thermometer_cleanup.py', False).Path
    _c46_thermometer_cleanup_INTEGRATED_ROOT = _c46_thermometer_cleanup__IntegratedPath(_c46_thermometer_cleanup___file__).resolve().parents[7]
    _c46_thermometer_cleanup_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/thermometer_cleanup.py', False)

    def _c46_thermometer_cleanup_thermometer_matrix(maximum):
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

    def _c46_thermometer_cleanup_linear_frame(rows):
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

    def _c46_thermometer_cleanup_binary_to_thermometer(builder, flags, maximum):
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
        rows = _c46_thermometer_cleanup_thermometer_matrix(maximum)
        for operation, left, right in _c46_thermometer_cleanup_linear_frame(rows):
            if operation == 'cx':
                builder.cx(wires[left], wires[right])
            else:
                builder.swap(wires[left], wires[right])
        return (wires, helpers)

    def _c46_thermometer_cleanup_erase_pair_count_thermometer(builder, x, flags):
        """Reset the binary pair count, preserving its four allocated flag wires."""
        x, flags = (list(x), list(flags))
        if len(x) < 4 or len(x) % 2:
            raise ValueError('Pair normalization needs a positive even input width.')
        maximum = (len(x) - 2) // 2
        if len(set(x + flags)) != len(x) + len(flags):
            raise ValueError('Input and count wires must be distinct.')
        thermometer, helpers = _c46_thermometer_cleanup_binary_to_thermometer(builder, flags, maximum)
        for index in reversed(range(maximum)):
            wire = thermometer[index]
            outcome = builder.alloc_bits(1)[0]
            builder.hmr(wire, outcome)
            a, b = (x[-2 * index - 1], x[-2 * index - 2])
            if not index:
                builder.z(outcome)
            builder.push_condition(outcome)
            if index:
                previous = thermometer[index - 1]
                builder.z(previous)
                builder.cz(previous, a)
                builder.cz(previous, b)
                builder.ccz(previous, a, b)
            else:
                builder.z(a)
                builder.z(b)
                builder.cz(a, b)
            builder.pop_condition()
            builder.free(outcome)
        builder.free(_c46_thermometer_cleanup_km.array(helpers))
        return dict(and_count=maximum - len(flags), conditioned_ccz_count=maximum - 1, expected_toffolis=maximum - len(flags) + (maximum - 1) / 2, temporary_qubits=len(helpers), threshold_count=maximum, exact_for_all_measurement_outcomes=True)

# work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py
def _initialize__c47_fourier_resource_expectation():
    global _c47_fourier_resource_expectation_Fraction, _c47_fourier_resource_expectation_INTEGRATED_ROOT, _c47_fourier_resource_expectation_ONE, _c47_fourier_resource_expectation_Program, _c47_fourier_resource_expectation_ZERO, _c47_fourier_resource_expectation__IntegratedPath, _c47_fourier_resource_expectation___file__, _c47_fourier_resource_expectation___name__, _c47_fourier_resource_expectation_affine_leaves, _c47_fourier_resource_expectation_annotations, _c47_fourier_resource_expectation_choose, _c47_fourier_resource_expectation_exact_expectation, _c47_fourier_resource_expectation_json, _c47_fourier_resource_expectation_lru_cache, _c47_fourier_resource_expectation_probability, _c47_fourier_resource_expectation_product, _c47_fourier_resource_expectation_unit_cases, _c47_fourier_resource_expectation_xor
    'Exact branch probabilities without assuming independent nested guards.\n\nThis is a test/accounting utility, never an input to circuit generation.  Each\nsyntactic HMR gets an independent fair bit; an inactive HMR retains its old\nclassical destination.  Affine leaves are evaluated on their exact GF(2) rank,\nso (odd OR twice) AND odd has probability 1/2, not 1/4.  A bounded rank cap\nrejects a larger expression instead of guessing its expectation.\n'
    pass
    _c47_fourier_resource_expectation__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', False).Path
    _c47_fourier_resource_expectation_INTEGRATED_ROOT = _c47_fourier_resource_expectation__IntegratedPath(_c47_fourier_resource_expectation___file__).resolve().parents[7]
    _c47_fourier_resource_expectation_Fraction = _import_component('fractions', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', False).Fraction
    _c47_fourier_resource_expectation_lru_cache = _import_component('functools', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', False).lru_cache
    _c47_fourier_resource_expectation_Program = _import_component('branch_prover', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', False).Program
    _c47_fourier_resource_expectation_ZERO = ('affine', 0, 0)
    _c47_fourier_resource_expectation_ONE = ('affine', 1, 0)

    def _c47_fourier_resource_expectation_xor(*values):
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
            return _c47_fourier_resource_expectation_ZERO
        if len(terms) == 1:
            return next(iter(terms))
        return ('xor', tuple(sorted(terms, key=repr)))

    def _c47_fourier_resource_expectation_product(*values):
        terms = set()
        pending = list(values)
        while pending:
            value = pending.pop()
            if value == _c47_fourier_resource_expectation_ZERO:
                return _c47_fourier_resource_expectation_ZERO
            if value == _c47_fourier_resource_expectation_ONE:
                continue
            if value[0] == 'and':
                pending.extend(value[1])
            else:
                terms.add(value)
        for value in tuple(terms):
            if _c47_fourier_resource_expectation_xor(value, _c47_fourier_resource_expectation_ONE) in terms:
                return _c47_fourier_resource_expectation_ZERO
        if not terms:
            return _c47_fourier_resource_expectation_ONE
        if len(terms) == 1:
            return next(iter(terms))
        return ('and', tuple(sorted(terms, key=repr)))

    def _c47_fourier_resource_expectation_choose(condition, yes, no):
        if yes == no:
            return yes
        return _c47_fourier_resource_expectation_xor(no, _c47_fourier_resource_expectation_product(condition, _c47_fourier_resource_expectation_xor(yes, no)))

    def _c47_fourier_resource_expectation_affine_leaves(value, result):
        if value[0] == 'affine':
            result.add(value)
        else:
            for child in value[1]:
                _c47_fourier_resource_expectation_affine_leaves(child, result)

    def _c47_fourier_resource_expectation_probability(value, *, rank_cap=12):
        leaves = set()
        _c47_fourier_resource_expectation_affine_leaves(value, leaves)
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
        return (_c47_fourier_resource_expectation_Fraction(sum((evaluate(value, assignment) for assignment in range(1 << len(basis)))), 1 << len(basis)), len(basis))

    def _c47_fourier_resource_expectation_exact_expectation(text, *, rank_cap=12, include_gates=False):
        program = _c47_fourier_resource_expectation_Program(text)
        classical = {'0': _c47_fourier_resource_expectation_ZERO, '1': _c47_fourier_resource_expectation_ONE, 'False': _c47_fourier_resource_expectation_ZERO, 'True': _c47_fourier_resource_expectation_ONE}
        stack = [_c47_fourier_resource_expectation_ONE]
        measured = set()
        cached = {}
        totals = dict(toffoli_like=_c47_fourier_resource_expectation_Fraction(0), T=_c47_fourier_resource_expectation_Fraction(0), generic_rotations=_c47_fourier_resource_expectation_Fraction(0))
        static = dict(toffoli_like=0, T=0, generic_rotations=0)
        records = []
        max_rank = 0

        def read(wire):
            if wire.startswith('q'):
                raise ValueError('A quantum wire was used as a classical accounting condition.')
            return classical.get(wire, _c47_fourier_resource_expectation_ZERO)
        for index, op in enumerate(program.operations):
            kind, args = (op.kind, op.arguments)
            active = _c47_fourier_resource_expectation_product(stack[-1], _c47_fourier_resource_expectation_ONE if op.condition is None else read(op.condition))
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
                    cached[active] = _c47_fourier_resource_expectation_probability(active, rank_cap=rank_cap)
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
                classical[args[1]] = _c47_fourier_resource_expectation_choose(active, variable, read(args[1]))
            elif kind in ('BIT_STORE0', 'BIT_STORE1'):
                classical[args[0]] = _c47_fourier_resource_expectation_choose(active, _c47_fourier_resource_expectation_ONE if kind == 'BIT_STORE1' else _c47_fourier_resource_expectation_ZERO, read(args[0]))
            elif kind == 'BIT_INVERT' or (kind == 'X' and args[0].startswith('b')):
                classical[args[0]] = _c47_fourier_resource_expectation_xor(read(args[0]), active)
            elif kind == 'CX' and args[1].startswith('b'):
                classical[args[1]] = _c47_fourier_resource_expectation_xor(read(args[1]), _c47_fourier_resource_expectation_product(active, read(args[0])))
            elif kind == 'SWAP' and any((wire.startswith('b') for wire in args)):
                raise ValueError('Classical SWAP needs an explicit accounting rule.')
        if len(stack) != 1:
            raise AssertionError('Unclosed accounting condition.')
        report = dict(status='EXACT_EXPECTATION_FROM_CLASSICAL_GUARDS', assumptions=['Every active HMR measures a computational-basis wire and has a fair independent outcome.', 'Conditional costs count instruction execution, independently of quantum control values.'], accounting='exact Boolean guards; GF2-rank enumeration of affine leaves', rank_cap=rank_cap, maximum_rank_used=max_rank, syntactic_measurements=program.measurements, static=static, mean={key: str(value) for key, value in totals.items()}, mean_numeric={key: float(value) for key, value in totals.items()}, mean_Toffoli_plus_T_quarter=str(totals['toffoli_like'] + totals['T'] / 4), independent_condition_depth_not_assumed=True, official_verified=False)
        if include_gates:
            report['charged_gates'] = records
        return report

    def _c47_fourier_resource_expectation_unit_cases():
        o = ('affine', 0, 1)
        t = ('affine', 0, 2)
        either = _c47_fourier_resource_expectation_xor(o, t, _c47_fourier_resource_expectation_product(o, t))
        assert _c47_fourier_resource_expectation_probability(_c47_fourier_resource_expectation_product(either, o))[0] == _c47_fourier_resource_expectation_Fraction(1, 2)
        assert _c47_fourier_resource_expectation_probability(either)[0] == _c47_fourier_resource_expectation_Fraction(3, 4)
        assert _c47_fourier_resource_expectation_probability(_c47_fourier_resource_expectation_xor(o, t))[0] == _c47_fourier_resource_expectation_Fraction(1, 2)
        assert _c47_fourier_resource_expectation_probability(_c47_fourier_resource_expectation_product(o, _c47_fourier_resource_expectation_xor(o, _c47_fourier_resource_expectation_ONE)))[0] == 0
        m = ('affine', 0, 4)
        assert _c47_fourier_resource_expectation_probability(_c47_fourier_resource_expectation_choose(o, m, _c47_fourier_resource_expectation_ONE))[0] == _c47_fourier_resource_expectation_Fraction(3, 4)
        assert _c47_fourier_resource_expectation_probability(_c47_fourier_resource_expectation_product(o, _c47_fourier_resource_expectation_choose(o, m, _c47_fourier_resource_expectation_ONE)))[0] == _c47_fourier_resource_expectation_Fraction(1, 4)
        return dict(status='PASS', cases=6, correlated_OR_nested_guard_checked=True, conditional_HMR_old_destination_checked=True)
    if _c47_fourier_resource_expectation___name__ == '__main__':
        _c47_fourier_resource_expectation_json = _import_component('json', 'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', True)
        print(_c47_fourier_resource_expectation_json.dumps(_c47_fourier_resource_expectation_unit_cases(), sort_keys=True))

# work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py
def _initialize__c48_consuming_odd_sqrt():
    global _c48_consuming_odd_sqrt_INTEGRATED_ROOT, _c48_consuming_odd_sqrt_Path, _c48_consuming_odd_sqrt_ROOT, _c48_consuming_odd_sqrt__IntegratedPath, _c48_consuming_odd_sqrt___file__, _c48_consuming_odd_sqrt___name__, _c48_consuming_odd_sqrt__add_leading_one, _c48_consuming_odd_sqrt__arr, _c48_consuming_odd_sqrt__low_finish, _c48_consuming_odd_sqrt__low_prepare, _c48_consuming_odd_sqrt__low_remainder_xor, _c48_consuming_odd_sqrt__root_step, _c48_consuming_odd_sqrt_add, _c48_consuming_odd_sqrt_forward, _c48_consuming_odd_sqrt_inverse, _c48_consuming_odd_sqrt_km, _c48_consuming_odd_sqrt_sys
    'Consume normalized22-bit norm into nearest-odd-root v12 and residual h10.\n\nFor norm in [2**20,2**22), Q=isqrt(16*norm), d=2Q+1=8193+2v,\nh=(64*norm-d*d)//64. Output h occupies the original low10 wires;\nv occupies the original high12 wires. Four appended zero wires are reset.\nThe non-restoring remainder sign is the complement of the newest root bit,\nso each old sign wire becomes an explicit root wire without a history tape.\n'
    _c48_consuming_odd_sqrt__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False).Path
    _c48_consuming_odd_sqrt_INTEGRATED_ROOT = _c48_consuming_odd_sqrt__IntegratedPath(_c48_consuming_odd_sqrt___file__).resolve().parents[6]
    _c48_consuming_odd_sqrt_Path = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False).Path
    _c48_consuming_odd_sqrt_sys = _import_component('sys', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', True)
    _c48_consuming_odd_sqrt_ROOT = _c48_consuming_odd_sqrt_Path(_c48_consuming_odd_sqrt___file__).resolve().parents[2]
    _c48_consuming_odd_sqrt_sys.path[:0] = [str(_c48_consuming_odd_sqrt_ROOT / 'fusion_handoff/official/kickmix'), str(_c48_consuming_odd_sqrt_ROOT / 'cleanroom/baseline_stage97/engine')]
    _c48_consuming_odd_sqrt_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False)
    _c48_consuming_odd_sqrt_add = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False).add

    def _c48_consuming_odd_sqrt__arr(wires):
        return _c48_consuming_odd_sqrt_km.array(list(wires))

    def _c48_consuming_odd_sqrt__add_leading_one(builder, target, *, inverse=False):
        """Add/subtract2**(n-2) modulo2**n, entirely Clifford."""
        if len(target) < 2:
            raise ValueError('Leading-one add needs two target positions')
        if inverse:
            builder.x(target[-2])
            builder.cx(target[-2], target[-1])
        else:
            builder.cx(target[-2], target[-1])
            builder.x(target[-2])

    def _c48_consuming_odd_sqrt__low_prepare(builder, low, b, *, inverse=False):
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

    def _c48_consuming_odd_sqrt__low_finish(builder, low, b, u, c, *, inverse=False):
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

    def _c48_consuming_odd_sqrt__root_step(builder, remainder, older_root, b, *, initial=False, inverse=False):
        """One non-restoring step, after routing next inputpair into remainder[:2]."""
        low = list(remainder[:3])
        high = list(remainder[3:])
        u, c = _c48_consuming_odd_sqrt__low_prepare(builder, low, b, inverse=inverse)
        builder.cx(b, _c48_consuming_odd_sqrt__arr(high))
        if inverse:
            if not initial:
                _c48_consuming_odd_sqrt__add_leading_one(builder, high, inverse=True)
            _c48_consuming_odd_sqrt_add(builder, older_root, high, carry_in=c, subtract=True)
        else:
            _c48_consuming_odd_sqrt_add(builder, older_root, high, carry_in=c)
            if not initial:
                _c48_consuming_odd_sqrt__add_leading_one(builder, high)
        builder.cx(b, _c48_consuming_odd_sqrt__arr(high))
        _c48_consuming_odd_sqrt__low_finish(builder, low, b, u, c, inverse=inverse)

    def _c48_consuming_odd_sqrt__low_remainder_xor(builder, Q, low):
        """XOR (-QÂ²-Q-1) mod16 into low, using one CCX and no ancilla."""
        q0, q1, q2, q3 = Q[:4]
        builder.x(_c48_consuming_odd_sqrt__arr(low))
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

    def _c48_consuming_odd_sqrt_forward(builder, norm):
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
            _c48_consuming_odd_sqrt__root_step(builder, remainder, older, b, initial=j == 1)
        b = remainder[-1]
        builder.x(b)
        Q = [b] + root
        W = remainder[:-1]
        high = W[1:]
        builder.cx(b, _c48_consuming_odd_sqrt__arr(high))
        _c48_consuming_odd_sqrt_add(builder, root, high, carry_in=b)
        _c48_consuming_odd_sqrt__add_leading_one(builder, high)
        builder.cx(b, _c48_consuming_odd_sqrt__arr(high))
        _c48_consuming_odd_sqrt__low_remainder_xor(builder, Q, W[:4])
        builder.free(_c48_consuming_odd_sqrt__arr(W[:4]))
        if Q != norm[10:] or W[4:] != norm[:10]:
            raise AssertionError('In-place output layout changed')
        return dict(root=Q, residual=W[4:])

    def _c48_consuming_odd_sqrt_inverse(builder, norm):
        norm = list(norm)
        if len(norm) != 22 or len(set(norm)) != 22:
            raise ValueError('Expected22 distinct input wires')
        Q = norm[10:]
        W = list(builder.alloc_qubits(4)) + norm[:10]
        _c48_consuming_odd_sqrt__low_remainder_xor(builder, Q, W[:4])
        b = Q[0]
        root = Q[1:]
        high = W[1:]
        builder.cx(b, _c48_consuming_odd_sqrt__arr(high))
        _c48_consuming_odd_sqrt__add_leading_one(builder, high, inverse=True)
        _c48_consuming_odd_sqrt_add(builder, root, high, carry_in=b, subtract=True)
        builder.cx(b, _c48_consuming_odd_sqrt__arr(high))
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
            _c48_consuming_odd_sqrt__root_step(builder, remainder, older, b, initial=j == 1, inverse=True)
            if j == 1:
                remainder = remainder[2:]
            else:
                remainder = remainder[2:] + [b]
                builder.x(b)
                root = older
            if j >= 11:
                builder.free(_c48_consuming_odd_sqrt__arr(pair))
            elif pair != norm[20 - 2 * j:22 - 2 * j]:
                raise AssertionError('Restored inputpair layout changed')
        if remainder != norm[20:] or root:
            raise AssertionError('Initial remainder layout changed')
        builder.cx(norm[20], norm[21])
        builder.x(norm[20])
        return norm

# work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py [independent arithmetic context]
def _initialize__c48_consuming_odd_sqrt_private():
    global _c48_consuming_odd_sqrt_private_INTEGRATED_ROOT, _c48_consuming_odd_sqrt_private_Path, _c48_consuming_odd_sqrt_private_ROOT, _c48_consuming_odd_sqrt_private__IntegratedPath, _c48_consuming_odd_sqrt_private___file__, _c48_consuming_odd_sqrt_private___name__, _c48_consuming_odd_sqrt_private__add_leading_one, _c48_consuming_odd_sqrt_private__arr, _c48_consuming_odd_sqrt_private__low_finish, _c48_consuming_odd_sqrt_private__low_prepare, _c48_consuming_odd_sqrt_private__low_remainder_xor, _c48_consuming_odd_sqrt_private__root_step, _c48_consuming_odd_sqrt_private_add, _c48_consuming_odd_sqrt_private_forward, _c48_consuming_odd_sqrt_private_inverse, _c48_consuming_odd_sqrt_private_km, _c48_consuming_odd_sqrt_private_sys
    'Consume normalized22-bit norm into nearest-odd-root v12 and residual h10.\n\nFor norm in [2**20,2**22), Q=isqrt(16*norm), d=2Q+1=8193+2v,\nh=(64*norm-d*d)//64. Output h occupies the original low10 wires;\nv occupies the original high12 wires. Four appended zero wires are reset.\nThe non-restoring remainder sign is the complement of the newest root bit,\nso each old sign wire becomes an explicit root wire without a history tape.\n'
    _c48_consuming_odd_sqrt_private__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False).Path
    _c48_consuming_odd_sqrt_private_INTEGRATED_ROOT = _c48_consuming_odd_sqrt_private__IntegratedPath(_c48_consuming_odd_sqrt_private___file__).resolve().parents[6]
    _c48_consuming_odd_sqrt_private_Path = _import_component('pathlib', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False).Path
    _c48_consuming_odd_sqrt_private_sys = _import_component('sys', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', True)
    _c48_consuming_odd_sqrt_private_ROOT = _c48_consuming_odd_sqrt_private_Path(_c48_consuming_odd_sqrt_private___file__).resolve().parents[2]
    _c48_consuming_odd_sqrt_private_sys.path[:0] = [str(_c48_consuming_odd_sqrt_private_ROOT / 'fusion_handoff/official/kickmix'), str(_c48_consuming_odd_sqrt_private_ROOT / 'cleanroom/baseline_stage97/engine')]
    _c48_consuming_odd_sqrt_private_km = _import_component('kickmix', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False)
    _c48_consuming_odd_sqrt_private_add = _import_component('fusion.arithmetic', 'work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', False).add

    def _c48_consuming_odd_sqrt_private__arr(wires):
        return _c48_consuming_odd_sqrt_private_km.array(list(wires))

    def _c48_consuming_odd_sqrt_private__add_leading_one(builder, target, *, inverse=False):
        """Add/subtract2**(n-2) modulo2**n, entirely Clifford."""
        if len(target) < 2:
            raise ValueError('Leading-one add needs two target positions')
        if inverse:
            builder.x(target[-2])
            builder.cx(target[-2], target[-1])
        else:
            builder.cx(target[-2], target[-1])
            builder.x(target[-2])

    def _c48_consuming_odd_sqrt_private__low_prepare(builder, low, b, *, inverse=False):
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

    def _c48_consuming_odd_sqrt_private__low_finish(builder, low, b, u, c, *, inverse=False):
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

    def _c48_consuming_odd_sqrt_private__root_step(builder, remainder, older_root, b, *, initial=False, inverse=False):
        """One non-restoring step, after routing next inputpair into remainder[:2]."""
        low = list(remainder[:3])
        high = list(remainder[3:])
        u, c = _c48_consuming_odd_sqrt_private__low_prepare(builder, low, b, inverse=inverse)
        builder.cx(b, _c48_consuming_odd_sqrt_private__arr(high))
        if inverse:
            if not initial:
                _c48_consuming_odd_sqrt_private__add_leading_one(builder, high, inverse=True)
            _c48_consuming_odd_sqrt_private_add(builder, older_root, high, carry_in=c, subtract=True)
        else:
            _c48_consuming_odd_sqrt_private_add(builder, older_root, high, carry_in=c)
            if not initial:
                _c48_consuming_odd_sqrt_private__add_leading_one(builder, high)
        builder.cx(b, _c48_consuming_odd_sqrt_private__arr(high))
        _c48_consuming_odd_sqrt_private__low_finish(builder, low, b, u, c, inverse=inverse)

    def _c48_consuming_odd_sqrt_private__low_remainder_xor(builder, Q, low):
        """XOR (-QÂ²-Q-1) mod16 into low, using one CCX and no ancilla."""
        q0, q1, q2, q3 = Q[:4]
        builder.x(_c48_consuming_odd_sqrt_private__arr(low))
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

    def _c48_consuming_odd_sqrt_private_forward(builder, norm):
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
            _c48_consuming_odd_sqrt_private__root_step(builder, remainder, older, b, initial=j == 1)
        b = remainder[-1]
        builder.x(b)
        Q = [b] + root
        W = remainder[:-1]
        high = W[1:]
        builder.cx(b, _c48_consuming_odd_sqrt_private__arr(high))
        _c48_consuming_odd_sqrt_private_add(builder, root, high, carry_in=b)
        _c48_consuming_odd_sqrt_private__add_leading_one(builder, high)
        builder.cx(b, _c48_consuming_odd_sqrt_private__arr(high))
        _c48_consuming_odd_sqrt_private__low_remainder_xor(builder, Q, W[:4])
        builder.free(_c48_consuming_odd_sqrt_private__arr(W[:4]))
        if Q != norm[10:] or W[4:] != norm[:10]:
            raise AssertionError('In-place output layout changed')
        return dict(root=Q, residual=W[4:])

    def _c48_consuming_odd_sqrt_private_inverse(builder, norm):
        norm = list(norm)
        if len(norm) != 22 or len(set(norm)) != 22:
            raise ValueError('Expected22 distinct input wires')
        Q = norm[10:]
        W = list(builder.alloc_qubits(4)) + norm[:10]
        _c48_consuming_odd_sqrt_private__low_remainder_xor(builder, Q, W[:4])
        b = Q[0]
        root = Q[1:]
        high = W[1:]
        builder.cx(b, _c48_consuming_odd_sqrt_private__arr(high))
        _c48_consuming_odd_sqrt_private__add_leading_one(builder, high, inverse=True)
        _c48_consuming_odd_sqrt_private_add(builder, root, high, carry_in=b, subtract=True)
        builder.cx(b, _c48_consuming_odd_sqrt_private__arr(high))
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
            _c48_consuming_odd_sqrt_private__root_step(builder, remainder, older, b, initial=j == 1, inverse=True)
            if j == 1:
                remainder = remainder[2:]
            else:
                remainder = remainder[2:] + [b]
                builder.x(b)
                root = older
            if j >= 11:
                builder.free(_c48_consuming_odd_sqrt_private__arr(pair))
            elif pair != norm[20 - 2 * j:22 - 2 * j]:
                raise AssertionError('Restored inputpair layout changed')
        if remainder != norm[20:] or root:
            raise AssertionError('Initial remainder layout changed')
        builder.cx(norm[20], norm[21])
        builder.x(norm[20])
        return norm

# work/c10/narrow/native/candidate01/common.py
def _initialize__c49_common():
    global _c49_common_ENGINE, _c49_common_HERE, _c49_common_INTEGRATED_ROOT, _c49_common_KICKMIX, _c49_common_MODEL, _c49_common_MODEL_PATH, _c49_common_MODEL_SHA, _c49_common_NARROW, _c49_common_Path, _c49_common_TESTS, _c49_common_TOOLING, _c49_common__IntegratedPath, _c49_common___file__, _c49_common___name__, _c49_common_array, _c49_common_cb, _c49_common_checked_json, _c49_common_current_gate, _c49_common_hashlib, _c49_common_json, _c49_common_km, _c49_common_os, _c49_common_plan_from_json, _c49_common_sys, _c49_common_verify_gate_sources, _c49_common_with_registers
    'Pinned own-source runtime for the first Q49 narrow native candidate.'
    _c49_common__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate01/common.py', False).Path
    _c49_common_INTEGRATED_ROOT = _c49_common__IntegratedPath(_c49_common___file__).resolve().parents[5]
    _c49_common_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate01/common.py', False).Path
    _c49_common_os = _import_component('os', 'work/c10/narrow/native/candidate01/common.py', True)
    _c49_common_sys = _import_component('sys', 'work/c10/narrow/native/candidate01/common.py', True)
    _c49_common_json = _import_component('json', 'work/c10/narrow/native/candidate01/common.py', True)
    _c49_common_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate01/common.py', True)
    _c49_common_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _c49_common_os.environ['OMP_NUM_THREADS'] = '1'
    _c49_common_HERE = _c49_common_Path(_c49_common___file__).resolve().parent
    _c49_common_NARROW = _c49_common_HERE.parents[1]
    _c49_common_ENGINE = _c49_common_NARROW / 'checkpoint002/cleanroom/baseline_stage97/engine'
    _c49_common_TESTS = _c49_common_NARROW / 'checkpoint002/cleanroom/baseline_stage97/tests'
    _c49_common_TOOLING = _c49_common_NARROW / 'checkpoint002/cleanroom/baseline_stage97/tooling'
    _c49_common_KICKMIX = _c49_common_NARROW / 'base/official/kickmix'
    _c49_common_sys.path[:0] = [str(_c49_common_KICKMIX), str(_c49_common_ENGINE), str(_c49_common_TESTS), str(_c49_common_TOOLING), str(_c49_common_NARROW / 'checkpoint002/cleanroom/odd_sqrt')]
    pass
    pass
    _c49_common_km = _import_component('kickmix', 'work/c10/narrow/native/candidate01/common.py', False)
    _c49_common_cb = _import_component('codebook', 'work/c10/narrow/native/candidate01/common.py', False)
    _c49_common_MODEL_PATH = _c49_common_NARROW / 'research/recompute_root/models/phasefit_z1_K7_G4_m37_virtual_quadS2_36_12c0.json'
    _c49_common_MODEL_SHA = '24fff823faa911afe93d02afc3ded0bbd156a210a85f1265c989a087f8fd1219'
    pass
    _c49_common_MODEL = _json_loads(_read_text(_c49_common_MODEL_PATH))

    def _c49_common_checked_json(path, sha):
        path = _c49_common_Path(path)
        raw = _read_bytes(path)
        actual = _c49_common_hashlib.sha256(raw).hexdigest()
        pass
        return _json_loads(raw)

    def _c49_common_plan_from_json(p):
        return _c49_common_cb.QuadraticCodePlan(p['width'], p['constant'], p['linear'], tuple((tuple(x) for x in p['edges'])), tuple((tuple(x) for x in p['products'])), p['product_linear'])

    def _c49_common_array(wires):
        return _c49_common_km.array(list(wires))

    def _c49_common_with_registers(circuit, registers):
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
            assert all((isinstance(q, _c49_common_km.q) for q in wires))
            all_wires.extend(wires)
            declarations.extend((f'APPEND_TO_REGISTER {q} r{index}' for q in wires))
            declarations.append(f'REGISTER r{index} {_c49_common_json.dumps(name)}')
        assert len(set(all_wires)) == len(all_wires)
        result = _c49_common_km.Circuit('\n'.join(declarations) + '\n' + generated_text(circuit))
        assert result.num_qubits == circuit.num_qubits
        assert list(result.register_data) == list(registers)
        for name, wires in registers.items():
            assert list(result.register_data[name]) == list(wires)
        return result

    def _c49_common_current_gate():
        return _c49_common_checked_json(_c49_common_NARROW / 'research/lifecycle_schedule/post008_gate_v4.json', '0e49c0e309c3a816d9e0512d5d815de44a1fc5a1de3b5eff866330c6017954b3')

    def _c49_common_verify_gate_sources():
        gate = _c49_common_current_gate()
        pass
        return gate

# work/c10/narrow/native/candidate01/divider.py
def _initialize__c50_divider():
    global _c50_divider_ACTIVE, _c50_divider_CENTRES, _c50_divider_CONTROLS, _c50_divider_DividerToken, _c50_divider_FEED3, _c50_divider_FEED4, _c50_divider_Fraction, _c50_divider_HIGH, _c50_divider_INTEGRATED_ROOT, _c50_divider_LOCAL, _c50_divider_NARROW, _c50_divider_OLDQ0, _c50_divider_OLDQ1, _c50_divider_P13, _c50_divider_P14, _c50_divider_THRESHOLDS, _c50_divider__IntegratedPath, _c50_divider___file__, _c50_divider___name__, _c50_divider__affine_control, _c50_divider__compose, _c50_divider__dirty, _c50_divider__erase, _c50_divider__erase_polynomial, _c50_divider__feature, _c50_divider__feed_carry, _c50_divider__feed_erase, _c50_divider__feed_variables, _c50_divider__frame, _c50_divider__leading_offset, _c50_divider__route, _c50_divider__sigma25_frame, _c50_divider__slots, _c50_divider__threshold, _c50_divider_annotations, _c50_divider_array, _c50_divider_cb, _c50_divider_checked_json, _c50_divider_cleanup_divider, _c50_divider_cleanup_u12, _c50_divider_compute_divider, _c50_divider_compute_phase_cleanup, _c50_divider_contextmanager, _c50_divider_dataclass, _c50_divider_field, _c50_divider_forward_add, _c50_divider_initialize_u12, _c50_divider_inverse_add, _c50_divider_km, _c50_divider_phase_endpoint, _c50_divider_plan_from_json, _c50_divider_xor_polynomial
    'Own Q49 consuming divider, direct u12, and endpoint phase.\n\nThe public API returns CURRENT logical product owners. No quantum owner is\nsilently deleted: consumed product information becomes a quotient-history\nowner, and the matching inverse restores it before u12 cleanup.\n'
    pass
    _c50_divider__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate01/divider.py', False).Path
    _c50_divider_INTEGRATED_ROOT = _c50_divider__IntegratedPath(_c50_divider___file__).resolve().parents[5]
    _c50_divider_contextmanager = _import_component('contextlib', 'work/c10/narrow/native/candidate01/divider.py', False).contextmanager
    _c50_divider_dataclass = _import_component('dataclasses', 'work/c10/narrow/native/candidate01/divider.py', False).dataclass
    _c50_divider_field = _import_component('dataclasses', 'work/c10/narrow/native/candidate01/divider.py', False).field
    _c50_divider_Fraction = _import_component('fractions', 'work/c10/narrow/native/candidate01/divider.py', False).Fraction
    _c50_divider_km = _import_component('common', 'work/c10/narrow/native/candidate01/divider.py', False).km
    _c50_divider_cb = _import_component('common', 'work/c10/narrow/native/candidate01/divider.py', False).cb
    _c50_divider_NARROW = _import_component('common', 'work/c10/narrow/native/candidate01/divider.py', False).NARROW
    _c50_divider_checked_json = _import_component('common', 'work/c10/narrow/native/candidate01/divider.py', False).checked_json
    _c50_divider_plan_from_json = _import_component('common', 'work/c10/narrow/native/candidate01/divider.py', False).plan_from_json
    _c50_divider_array = _import_component('common', 'work/c10/narrow/native/candidate01/divider.py', False).array
    _c50_divider_forward_add = _import_component('paired_arithmetic', 'work/c10/narrow/native/candidate01/divider.py', False).forward_add
    _c50_divider_inverse_add = _import_component('paired_arithmetic', 'work/c10/narrow/native/candidate01/divider.py', False).inverse_add
    _c50_divider_xor_polynomial = _import_component('quadratic_terms', 'work/c10/narrow/native/candidate01/divider.py', False).xor_polynomial
    _c50_divider__erase_polynomial = _import_component('cyclic_phase', 'work/c10/narrow/native/candidate01/divider.py', False)._erase_polynomial
    _c50_divider_LOCAL = _c50_divider_checked_json(_c50_divider_NARROW / 'research/recompute_root/initializer_u12/local_algebra.json', '978c2adafd8d3355558a5e672982623372d459dec610273e1e43847681cc4c14')
    _c50_divider_P13 = _c50_divider_cb.factor_polynomial(5, False, 13, set())
    _c50_divider_P14 = _c50_divider_cb.factor_polynomial(5, True, 23, {(0, 2), (0, 3), (2, 3)})
    _c50_divider_OLDQ0 = _c50_divider_cb.factor_polynomial(4, True, 7, set())
    _c50_divider_OLDQ1 = _c50_divider_cb.factor_polynomial(4, True, 12, {(0, 1), (0, 2), (1, 2)})
    _c50_divider_HIGH = _c50_divider_cb.factor_polynomial(6, False, 39, {(3, 4), (3, 5), (4, 5)})
    _c50_divider_FEED4 = _c50_divider_cb.factor_polynomial(4, False, 3, {(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)})
    _c50_divider_FEED3 = _c50_divider_cb.factor_polynomial(3, False, 3, {(0, 1), (1, 2)})
    assert _c50_divider_FEED4.and_count == _c50_divider_FEED3.and_count == 1

    def _c50_divider__compose(plan, mapping, width):
        constant = int(plan.constant)
        linear = 0
        edges = set()
        for i in _c50_divider_cb.bits(plan.linear):
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
            for a in _c50_divider_cb.bits(ma):
                for b in _c50_divider_cb.bits(mc):
                    if a == b:
                        linear ^= 1 << a
                    else:
                        edge = tuple(sorted((a, b)))
                        if edge in edges:
                            edges.remove(edge)
                        else:
                            edges.add(edge)
        return _c50_divider_cb.factor_polynomial(width, constant, linear, edges)

    def _c50_divider__erase(builder, target, variables, plan):
        assert target not in variables
        m = builder.alloc_bits(1)[0]
        builder.hmr(target, m)
        _c50_divider_cb.emit_phase(builder, variables, m, plan)
        builder.free(m)
        builder.free(target)

    def _c50_divider_initialize_u12(builder, v, P, u):
        """24 CCX forward; b13 and b14 become classical measurements, fully paid."""
        P = list(P)
        carry = list(builder.alloc_qubits(2))
        for q in (v[0], P[13], P[12]):
            builder.cx(q, u[0])
        env = {'v0': v[0], 'v1': v[1], 'p12': P[12], 'p13': P[13], 'p14': P[14], 'u0': u[0], 'u1': u[1], 'q0': carry[0], 'q1': carry[1]}
        for item in _c50_divider_LOCAL['best_low']['plans']:
            _c50_divider_cb.emit_xor(builder, [env[name] for name in item['inputs']], env[item['output']], _c50_divider_plan_from_json(item['plan']))
        variables = [v[0], v[1], P[12], u[0], u[1]]
        _c50_divider__erase(builder, P[13], variables, _c50_divider_P13)
        _c50_divider__erase(builder, P[14], variables, _c50_divider_P14)
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
                _c50_divider_cb.emit_xor(builder, [aq, bq, q0, q1], target, _c50_divider_plan_from_json(_c50_divider_LOCAL['high_forward'][f'next{which}']['plan']))
            variables = [aq, bq, u[i], nextcarry[0]]
            _c50_divider__erase(builder, q0, variables, _c50_divider_OLDQ0)
            _c50_divider__erase(builder, q1, variables, _c50_divider_OLDQ1)
            if i < 12:
                builder.x(aq)
            builder.x(bq)
            carry = nextcarry
        builder.cx(carry[0], u[13])
        builder.cx(u[13], carry[0])
        builder.free(carry[0])
        return P

    def _c50_divider_cleanup_u12(builder, v, P, u):
        """One CCX; reconstruct product on current owners and HMR all u bits."""
        P = list(P)
        P[13], P[14] = list(builder.alloc_qubits(2))
        variables = [v[0], v[1], P[12], u[0], u[1]]
        _c50_divider_cb.emit_xor(builder, variables, P[13], _c50_divider_P13)
        _c50_divider_cb.emit_xor(builder, variables, P[14], _c50_divider_P14)

        def aa(i):
            return (1, 1 << i) if 0 <= i < 12 else (0, 0)

        def bb(i):
            return (1, 0) if i in (0, 13) else (1, 1 << i - 1)
        for i in reversed(range(4, 14)):
            phase = _c50_divider__compose(_c50_divider_HIGH, [aa(i), bb(i), aa(i - 2), aa(i - 3), aa(i - 1), (0, 1 << 12)], 13)
            _c50_divider__erase(builder, u[i], list(v) + [u[i - 1]], phase)
        for i in reversed(range(4)):
            item = _c50_divider_LOCAL['low_cleanup'][i]
            env = {f'v{j}': v[j] for j in range(i + 1)}
            env.update(p12=P[12], p13=P[13], p14=P[14])
            env.update({f'u{j}': u[j] for j in range(i)})
            _c50_divider__erase(builder, u[i], [env[name] for name in item['inputs']], _c50_divider_plan_from_json(item['plan']))
        return P

    def _c50_divider__frame(builder, sign, target):
        for q in target:
            builder.x(q)
            builder.cx(sign, q)

    def _c50_divider__leading_offset(builder, target, inverse=False):
        if inverse:
            builder.x(target[-2])
            builder.cx(target[-2], target[-1])
        else:
            builder.cx(target[-2], target[-1])
            builder.x(target[-2])

    def _c50_divider__feed_variables(v, low, cur, sign):
        return ([v[0], low, sign], _c50_divider_FEED3) if cur is None else ([v[0], low, cur, sign], _c50_divider_FEED4)

    def _c50_divider__feed_carry(builder, v, low, cur, sign):
        variables, plan = _c50_divider__feed_variables(v, low, cur, sign)
        carry = builder.alloc_qubits(1)[0]
        _c50_divider_cb.emit_xor(builder, variables, carry, plan)
        return carry

    def _c50_divider__feed_erase(builder, carry, v, low, cur, sign):
        variables, plan = _c50_divider__feed_variables(v, low, cur, sign)
        _c50_divider__erase(builder, carry, variables, plan)

    @_c50_divider_dataclass
    class _c50_divider_DividerToken:
        v: list
        P: list
        flags: list
        u: list
        initial_u: tuple
        history: dict = _c50_divider_field(default_factory=dict)
        rows: list = _c50_divider_field(default_factory=list)
        consumed: bool = False

    def _c50_divider__dirty(token):
        forbidden = set(token.v + token.u)
        wires = token.flags + [q for q in token.P if q is not None] + list(token.history.values())
        return list(dict.fromkeys((q for q in wires if q not in forbidden)))

    def _c50_divider_compute_divider(builder, v12, P15, flags4):
        """Compute the m37 balanced endpoint, preserving every quotient owner."""
        v = list(v12)
        P = list(P15)
        flags = list(flags4)
        assert len(v) == 12 and len(P) == 15 and (len(flags) == 4)
        assert len(set(v + P + flags)) == 31
        assert builder.num_allocated_qubits == 31, 'Unpriced retained owner before divider'
        u = list(builder.alloc_qubits(14))
        initial_u = tuple(u)
        P = _c50_divider_initialize_u12(builder, v, P, u)
        token = _c50_divider_DividerToken(v, P, flags, u, initial_u)
        assert builder.num_allocated_qubits == 43
        for j in range(12, 36):
            u = token.u
            if j <= 24:
                prev = token.P[24 - j]
                cur = token.P[23 - j] if j < 24 else None
                assert prev is not None
                sign = u[-1]
                target = u[:-1]
                carry = _c50_divider__feed_carry(builder, v, prev, cur, sign)
                _c50_divider__frame(builder, sign, target)
                debt = _c50_divider_forward_add(builder, v[1:], target, carry_in=carry)
                _c50_divider__leading_offset(builder, target)
                _c50_divider__frame(builder, sign, target)
                builder.cx(v[0], prev)
                builder.cx(sign, prev)
                if cur is not None:
                    builder.cx(cur, prev)
                _c50_divider__feed_erase(builder, carry, v, prev, cur, sign)
                token.u = [prev] + target
                token.history[j] = sign
                token.P[24 - j] = None
                k = 0
            else:
                k = j - 26 if j >= 28 else 0
                u = [u[-1]] + u[:-1]
                sign = u[0]
                target = u[k + 1:]
                _c50_divider__frame(builder, sign, target)
                debt = _c50_divider_forward_add(builder, v[k + 1:], target, carry_in=v[k])
                _c50_divider__leading_offset(builder, target)
                _c50_divider__frame(builder, sign, target)
                builder.cx(v[0], u[0])
                token.u = u
            token.rows.append((j, k, debt))
            assert builder.num_allocated_qubits == 43, (j, builder.num_allocated_qubits)
        assert sorted(token.history) == list(range(12, 25)) and all((q is None for q in token.P))
        return token

    def _c50_divider_cleanup_divider(builder, token):
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
                carry = _c50_divider__feed_carry(builder, v, low, cur, sign)
                _c50_divider__frame(builder, sign, target)
                _c50_divider__leading_offset(builder, target, inverse=True)
                _c50_divider_inverse_add(builder, v[1:], target, debt, carry_in=carry, dirty_wires=_c50_divider__dirty(token))
                _c50_divider__frame(builder, sign, target)
                _c50_divider__feed_erase(builder, carry, v, low, cur, sign)
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
                _c50_divider__frame(builder, sign, target)
                _c50_divider__leading_offset(builder, target, inverse=True)
                _c50_divider_inverse_add(builder, v[k + 1:], target, debt, carry_in=v[k], dirty_wires=_c50_divider__dirty(token))
                _c50_divider__frame(builder, sign, target)
                token.u = u[1:] + u[:1]
            assert debt.consumed and (not debt.measurements)
            assert builder.num_allocated_qubits == 43
        assert tuple(token.u) == token.initial_u and (not token.history)
        token.P = _c50_divider_cleanup_u12(builder, v, token.P, token.u)
        assert builder.num_allocated_qubits == 31 and all((q is not None for q in token.P))
        return list(token.P)
    _c50_divider_CENTRES = (0, -2, -6, 0, -1)
    _c50_divider_ACTIVE = (30, 6, 27, 3, 17, 9, 18, 10, 23, 15, 20)
    _c50_divider_CONTROLS = ((2, 4, 8), (0, 4, 16), (0, 2, 4, 16), (0, 1, 4, 8), (0, 1))
    _c50_divider_THRESHOLDS = {1: (1, 2, 4, 8, 16, 3, 5, 9, 17), 2: (2, 4, 8, 16), 3: (4, 8, 3, 17), 4: (4, 8), 5: (8, 16, 32, 5, 17), 6: (8, 16, 32), 7: (8, 17), 8: (8,), 9: (9, 10), 10: (32,)}

    @_c50_divider_contextmanager
    def _c50_divider__affine_control(builder, variables, terms):
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

    @_c50_divider_contextmanager
    def _c50_divider__threshold(builder, variables, t):
        terms = _c50_divider_THRESHOLDS[t]
        if max((x.bit_count() for x in terms)) <= 1:
            with _c50_divider__affine_control(builder, variables, terms) as q:
                yield q
        else:
            q = builder.alloc_qubits(1)[0]
            _c50_divider_xor_polynomial(builder, variables, q, terms)
            try:
                yield q
            finally:
                _c50_divider__erase_polynomial(builder, q, variables, terms)

    def _c50_divider__route(builder, word, variables, inverse=False):
        stages = list(range(5))
        if inverse:
            stages.reverse()
        for stage in stages:
            with _c50_divider__affine_control(builder, variables, _c50_divider_CONTROLS[stage]) as q:
                for i in range(27):
                    k = (_c50_divider_CENTRES[stage] - i) % 27
                    if i < k:
                        builder.cswap(q, word[i], word[k])

    def _c50_divider__slots():
        word = list(range(27))
        for stage, centre in enumerate(_c50_divider_CENTRES):
            if _c50_divider_ACTIVE[0] >> stage & 1:
                word = [word[(centre - i) % 27] for i in range(27)]
        inverse = {v: i for i, v in enumerate(word)}
        return [inverse[i] for i in range(27)]

    def _c50_divider__feature(builder, control, data, turns):
        turns = _c50_divider_Fraction(turns) % 1
        if turns == _c50_divider_Fraction(1, 2):
            builder.cz(control, data)
        elif turns in (_c50_divider_Fraction(1, 4), _c50_divider_Fraction(3, 4)):
            sign = 1 if turns == _c50_divider_Fraction(1, 4) else -1
            builder.z_pow(control, _c50_divider_Fraction(sign, 4))
            builder.z_pow(data, _c50_divider_Fraction(sign, 4))
            builder.cx(control, data)
            builder.z_pow(data, _c50_divider_Fraction(-sign, 4))
            builder.cx(control, data)
        else:
            q = builder.alloc_qubits(1)[0]
            builder.ccx(control, data, q)
            builder.z_pow(q, 2 * turns)
            builder.del_and(control, data, q)
            builder.free(q)

    def _c50_divider__sigma25_frame(builder, v, u, inverse=False):
        for q in (v[10], v[0], v[1]):
            builder.cx(q, u[10])
        builder.cx(u[8], u[9])
        builder.cx(v[1], v[0])
        builder.ccx(u[9], v[0], u[10])
        builder.cx(v[1], v[0])
        builder.cx(u[8], u[9])

    def _c50_divider_phase_endpoint(builder, token):
        """146 CCX-equivalents +4 T +34 arbitrary rotations, N27 cyclic model."""
        v, u, flags = (token.v, token.u, token.flags)
        assert builder.num_allocated_qubits == 43
        _c50_divider__sigma25_frame(builder, v, u)
        for q in u[:9]:
            builder.cx(v[0], q)
        builder.cx(v[1], u[9])
        signs = {**token.history, 25: u[10], 26: u[9], 36: u[13]}
        signs.update({j: u[35 - j] for j in range(27, 36)})
        for q in signs.values():
            builder.x(q)
        ones = list(builder.alloc_qubits(2))
        builder.x(_c50_divider_array(ones))
        word = [ones[0]] + [signs[37 - i] for i in range(1, 26)] + [ones[1]]
        assert len(set(word)) == 27
        p, c = list(builder.alloc_qubits(2))
        _c50_divider_xor_polynomial(builder, flags, p, (6, 10))
        _c50_divider_xor_polynomial(builder, flags, c, (10,))
        variables = flags + [p, c]
        _c50_divider__route(builder, word, variables)
        slots = [word[i] for i in _c50_divider__slots()]
        factor = 1 << 27
        for i, q in enumerate(slots):
            units = (1 << i) + (factor if i == 0 else 0)
            builder.z_pow(q, _c50_divider_Fraction(2 * units, 1 << 37))
        for j in range(10):
            angle = _c50_divider_Fraction(factor * (1 << j), 1 << 37)
            if j == 0:
                with _c50_divider__threshold(builder, variables, 1) as q:
                    builder.x(q)
                    builder.z_pow(q, -2 * angle)
                    builder.x(q)
            elif j == 9:
                builder.z_pow(c, 2 * angle)
            else:
                with _c50_divider__threshold(builder, variables, j + 1) as q:
                    _c50_divider__feature(builder, q, slots[j], angle)
        _c50_divider__route(builder, word, variables, inverse=True)
        _c50_divider__erase_polynomial(builder, c, flags, (10,))
        _c50_divider__erase_polynomial(builder, p, flags, (6, 10))
        builder.x(_c50_divider_array(ones))
        builder.free(_c50_divider_array(ones))
        for q in signs.values():
            builder.x(q)
        builder.cx(v[1], u[9])
        for q in u[:9]:
            builder.cx(v[0], q)
        _c50_divider__sigma25_frame(builder, v, u, inverse=True)
        assert builder.num_allocated_qubits == 43

    def _c50_divider_compute_phase_cleanup(builder, v12, P15, flags4):
        token = _c50_divider_compute_divider(builder, v12, P15, flags4)
        _c50_divider_phase_endpoint(builder, token)
        return _c50_divider_cleanup_divider(builder, token)

# work/c10/narrow/native/candidate01/generate.py
def _initialize__c51_generate():
    global _c51_generate_ENGINE, _c51_generate_HERE, _c51_generate_INTEGRATED_ROOT, _c51_generate_KICKMIX, _c51_generate_MODEL, _c51_generate_MODEL_PATH, _c51_generate_MODEL_SHA, _c51_generate_NARROW, _c51_generate_Path, _c51_generate_Program, _c51_generate_TESTS, _c51_generate_TOOLING, _c51_generate__IntegratedPath, _c51_generate___file__, _c51_generate___name__, _c51_generate_argparse, _c51_generate_array, _c51_generate_build, _c51_generate_cb, _c51_generate_checked_json, _c51_generate_consuming_root, _c51_generate_current_gate, _c51_generate_decode_root, _c51_generate_exact_expectation, _c51_generate_generated_text, _c51_generate_hashlib, _c51_generate_json, _c51_generate_km, _c51_generate_main, _c51_generate_normalization, _c51_generate_os, _c51_generate_plan_from_json, _c51_generate_restore_input_layout, _c51_generate_snapshot, _c51_generate_sys, _c51_generate_time, _c51_generate_verify_gate_sources, _c51_generate_with_registers
    'Emit the complete own Q49 candidate after its frozen paper gate.\n\nRun under the serial resource guard. Emission and exact instruction accounting\ndo not by themselves qualify a circuit; all native and official proofs remain\nseparate evidence files.\n'
    _c51_generate__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate01/generate.py', False).Path
    _c51_generate_INTEGRATED_ROOT = _c51_generate__IntegratedPath(_c51_generate___file__).resolve().parents[5]
    _import_star('_c51_generate_', _import_component('common', 'work/c10/narrow/native/candidate01/generate.py', False))
    _c51_generate_argparse = _import_component('argparse', 'work/c10/narrow/native/candidate01/generate.py', True)
    _c51_generate_time = _import_component('time', 'work/c10/narrow/native/candidate01/generate.py', True)
    _c51_generate_normalization = _import_component('normalization', 'work/c10/narrow/native/candidate01/generate.py', True)
    pass
    _c51_generate_consuming_root = _import_component('consuming_odd_sqrt', 'work/c10/narrow/native/candidate01/generate.py', False)
    _c51_generate_decode_root = _import_component('root_decode', 'work/c10/narrow/native/candidate01/generate.py', False).decode_root
    _c51_generate_restore_input_layout = _import_component('layout', 'work/c10/narrow/native/candidate01/generate.py', False).restore_input_layout
    _c51_generate_generated_text = _import_component('branch_prover', 'work/c10/narrow/native/candidate01/generate.py', False).generated_text
    _c51_generate_Program = _import_component('branch_prover', 'work/c10/narrow/native/candidate01/generate.py', False).Program
    _c51_generate_exact_expectation = _import_component('fourier_resource_expectation', 'work/c10/narrow/native/candidate01/generate.py', False).exact_expectation

    def _c51_generate_snapshot(builder, name, owners):
        circuit = builder.finish_circuit()
        text = _c51_generate_generated_text(circuit)
        return dict(name=name, live_qubits=builder.num_allocated_qubits, peak_so_far=circuit.num_qubits, instruction_cut=len(_c51_generate_Program(text).operations), owners={k: [str(q) for q in v] for k, v in owners.items()}, cumulative_expected=_c51_generate_exact_expectation(text)['mean_numeric'])

    def _c51_generate_build():
        tables = _import_component('tables', 'work/c10/narrow/native/candidate01/generate.py', True)
        divider = _import_component('divider', 'work/c10/narrow/native/candidate01/generate.py', True)
        lifecycle = _import_component('lifecycle', 'work/c10/narrow/native/candidate01/generate.py', True)
        gate = _c51_generate_verify_gate_sources()
        builder = _c51_generate_km.CircuitBuilder()
        builder.set_max_qubits(49)
        original = list(builder.alloc_qubits(22))
        flags = list(builder.alloc_qubits(4))
        _c51_generate_normalization.forward(builder, original, flags)
        cuts = [_c51_generate_snapshot(builder, 'normalized', dict(n=original, flags=flags))]
        root = _c51_generate_consuming_root.forward(builder, original)
        v = list(root['root'])
        h = list(root['residual'])
        cuts.append(_c51_generate_snapshot(builder, 'consumed_root', dict(v=v, h=h, flags=flags)))
        v, h = lifecycle.emit_body(builder, v, h, flags, tables, divider, _c51_generate_decode_root)
        assert len(set(v + h + flags)) == 26 and builder.num_allocated_qubits == 26
        cuts.append(_c51_generate_snapshot(builder, 'body_restored', dict(v=v, h=h, flags=flags)))
        norm = h + v
        _c51_generate_consuming_root.inverse(builder, norm)
        cuts.append(_c51_generate_snapshot(builder, 'root_restored', dict(n=norm, flags=flags)))
        _c51_generate_normalization.inverse(builder, norm, flags)
        builder.free(_c51_generate_array(flags))
        cuts.append(_c51_generate_snapshot(builder, 'logical_input_restored', dict(x=norm)))
        layout = _c51_generate_restore_input_layout(builder, norm, original, 49)
        circuit = _c51_generate_with_registers(builder.finish_circuit(), dict(x=original))
        text = _c51_generate_generated_text(circuit)
        resources = _c51_generate_exact_expectation(text)
        actual = resources['mean_numeric']
        expected = gate['primary']
        assert circuit.num_qubits == 49, ('width_gate', circuit.num_qubits)
        assert actual['toffoli_like'] == expected['Toffolis_expected'], ('Toffoli_gate', actual, expected)
        assert actual['T'] == expected['T'] and actual['generic_rotations'] == expected['R'], ('phase_gate', actual)
        assert list(circuit.register_data) == ['x'] and list(circuit.register_data['x']) == original
        report = dict(status='EMITTED_NATIVE_CANDIDATE_NOT_YET_PROVED_OR_OFFICIALLY_VERIFIED', Q=circuit.num_qubits, exact_native_expectation=resources, paper_rotation_charge=expected['rotation_charge'], paper_cost=expected['paper_cost'], model_sha256=_c51_generate_MODEL_SHA, gate_sha256=_c51_generate_hashlib.sha256(_read_bytes(_c51_generate_NARROW / 'research/lifecycle_schedule/post008_gate_v4.json')).hexdigest(), cuts=cuts, final_Clifford_layout_swaps=layout, official_verifier=False, no_submission=True)
        return (circuit, text, report)

    def _c51_generate_main():
        ap = _c51_generate_argparse.ArgumentParser()
        ap.add_argument('--output', type=_c51_generate_Path, default=_c51_generate_HERE / 'candidate01.kmb')
        args = ap.parse_args()
        started = _c51_generate_time.monotonic()
        circuit, text, report = _c51_generate_build()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        circuit.to_file(str(args.output), format='kmb')
        args.output.with_suffix('.kmx').write_text(text)
        report.update(kmb_sha256=_c51_generate_hashlib.sha256(_read_bytes(args.output)).hexdigest(), bytes=args.output.stat().st_size, emission_seconds=_c51_generate_time.monotonic() - started, native_sources={p.name: _c51_generate_hashlib.sha256(_read_bytes(p)).hexdigest() for p in sorted(_c51_generate_HERE.glob('*.py'))})
        args.output.with_suffix('.build.json').write_text(_c51_generate_json.dumps(report, indent=2) + '\n')
        print(_c51_generate_json.dumps(report, indent=2), flush=True)
    if _c51_generate___name__ == '__main__':
        _c51_generate_main()

# work/c10/narrow/native/candidate01/layout.py
def _initialize__c52_layout():
    global _c52_layout_INTEGRATED_ROOT, _c52_layout__IntegratedPath, _c52_layout___file__, _c52_layout___name__, _c52_layout_array, _c52_layout_km, _c52_layout_restore_input_layout
    'Return current logical input values to the original registered owners.'
    _c52_layout__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate01/layout.py', False).Path
    _c52_layout_INTEGRATED_ROOT = _c52_layout__IntegratedPath(_c52_layout___file__).resolve().parents[5]
    _c52_layout_km = _import_component('common', 'work/c10/narrow/native/candidate01/layout.py', False).km
    _c52_layout_array = _import_component('common', 'work/c10/narrow/native/candidate01/layout.py', False).array

    def _c52_layout_restore_input_layout(builder, current, original, cap=49):
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
        builder.free(_c52_layout_array(sorted(all_wires - set(original), key=str)))
        assert builder.num_allocated_qubits == 22
        return swaps

# work/c10/narrow/native/candidate01/lifecycle.py
def _initialize__c53_lifecycle():
    global _c53_lifecycle_AR_SHA, _c53_lifecycle_CUT_HOOK, _c53_lifecycle_ENGINE, _c53_lifecycle_H3_CURRENT, _c53_lifecycle_H3_INITIAL, _c53_lifecycle_H4_PLAN, _c53_lifecycle_INTEGRATED_ROOT, _c53_lifecycle_METADATA, _c53_lifecycle_MODEL, _c53_lifecycle_NARROW, _c53_lifecycle_ProductToken, _c53_lifecycle_SEED, _c53_lifecycle_SeedToken, _c53_lifecycle_SimpleNamespace, _c53_lifecycle__IntegratedPath, _c53_lifecycle___file__, _c53_lifecycle___name__, _c53_lifecycle__clear_coefficient_carry, _c53_lifecycle__clear_product_carry, _c53_lifecycle__coefficient_carry, _c53_lifecycle__erase, _c53_lifecycle__literal_inputs, _c53_lifecycle__mark, _c53_lifecycle__merge_debts, _c53_lifecycle__product_carry, _c53_lifecycle__spec, _c53_lifecycle_annotations, _c53_lifecycle_ar, _c53_lifecycle_array, _c53_lifecycle_cb, _c53_lifecycle_checked_json, _c53_lifecycle_coefficient_forward, _c53_lifecycle_coefficient_inverse, _c53_lifecycle_dataclass, _c53_lifecycle_emit_body, _c53_lifecycle_erase_high_H, _c53_lifecycle_hashlib, _c53_lifecycle_importlib, _c53_lifecycle_km, _c53_lifecycle_merge_coefficient_transcripts, _c53_lifecycle_plan_from_json, _c53_lifecycle_prepare_H3_current, _c53_lifecycle_prepare_H3_initial, _c53_lifecycle_prepare_H4, _c53_lifecycle_product_ar, _c53_lifecycle_product_forward, _c53_lifecycle_product_inverse, _c53_lifecycle_root_R_frame, _c53_lifecycle_seed_cleanup, _c53_lifecycle_seed_forward, _c53_lifecycle_seed_root_frame, _c53_lifecycle_sys
    'Native narrow coefficient/seed/consuming-product lifecycle.\n\nAll physical arrays returned from measured/recreated registers are current.\nNo supplied source is modified. Every measurement bit has one explicit owner.\n'
    pass
    _c53_lifecycle__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate01/lifecycle.py', False).Path
    _c53_lifecycle_INTEGRATED_ROOT = _c53_lifecycle__IntegratedPath(_c53_lifecycle___file__).resolve().parents[5]
    _c53_lifecycle_dataclass = _import_component('dataclasses', 'work/c10/narrow/native/candidate01/lifecycle.py', False).dataclass
    _c53_lifecycle_SimpleNamespace = _import_component('types', 'work/c10/narrow/native/candidate01/lifecycle.py', False).SimpleNamespace
    _c53_lifecycle_importlib = _import_component('importlib.util', 'work/c10/narrow/native/candidate01/lifecycle.py', True)
    _c53_lifecycle_sys = _import_component('sys', 'work/c10/narrow/native/candidate01/lifecycle.py', True)
    _c53_lifecycle_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate01/lifecycle.py', True)
    _c53_lifecycle_km = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).km
    _c53_lifecycle_cb = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).cb
    _c53_lifecycle_NARROW = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).NARROW
    _c53_lifecycle_ENGINE = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).ENGINE
    _c53_lifecycle_MODEL = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).MODEL
    _c53_lifecycle_checked_json = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).checked_json
    _c53_lifecycle_plan_from_json = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).plan_from_json
    _c53_lifecycle_array = _import_component('common', 'work/c10/narrow/native/candidate01/lifecycle.py', False).array
    _c53_lifecycle_ar = _import_component('paired_arithmetic', 'work/c10/narrow/native/candidate01/lifecycle.py', False)
    _c53_lifecycle_AR_SHA = 'a10b28423640a50a45a6ab23d3604dd869c26943b0ed12021526e87d1fbf8ccc'
    pass
    _c53_lifecycle_SEED = _c53_lifecycle_checked_json(_c53_lifecycle_NARROW / 'research/lifecycle_schedule/seed_phase_cleanup_conditional.json', '71f0fcb5645fd32cf128c310c5e5cba406d1ad33c02b4f37e51869ee845ed466')['certificate']
    _c53_lifecycle_METADATA = _c53_lifecycle_checked_json(_c53_lifecycle_NARROW / 'research/lifecycle_schedule/slope_h3_h4_retirement_v3.json', '1e5afe12bc0a9005bb3705afdc564f30c0861d99970d31f71d9b7c2556e17721')['certificate']
    _c53_lifecycle_H3_INITIAL = _c53_lifecycle_plan_from_json(_c53_lifecycle_METADATA['H3_initial']['plan'])
    _c53_lifecycle_H3_CURRENT = _c53_lifecycle_plan_from_json(_c53_lifecycle_METADATA['H3_current']['plan'])
    _c53_lifecycle_H4_PLAN = _c53_lifecycle_plan_from_json(_c53_lifecycle_METADATA['H4']['plan'])
    _c53_lifecycle_CUT_HOOK = None

    def _c53_lifecycle__literal_inputs(source, target, carry_in, signed_source):
        source, target = (list(source), list(target))
        width = len(target)
        source = source[:width]
        if any((q is not False and (not isinstance(q, _c53_lifecycle_km.q)) for q in source)):
            raise ValueError('Product source contains a nonwire/nonzero constant.')
        real = [q for q in source if isinstance(q, _c53_lifecycle_km.q)]
        if len(set(real + target)) != len(real) + len(target):
            raise ValueError('Product data wires alias.')
        if isinstance(carry_in, _c53_lifecycle_km.q) and carry_in in real + target:
            raise ValueError('Product carry aliases data.')
        if carry_in is not False and (not isinstance(carry_in, _c53_lifecycle_km.q)):
            raise ValueError('Invalid product carry.')
        preserve = real[-1] if signed_source and real else None
        source += [preserve if preserve is not None else False] * (width - len(source))
        return (source, target, preserve)
    _c53_lifecycle__spec = _spec('_candidate01_product_paired', _c53_lifecycle_ENGINE / 'paired_arithmetic.py')
    _c53_lifecycle_product_ar = _new_module(_c53_lifecycle__spec)
    _c53_lifecycle_sys.modules[_c53_lifecycle__spec.name] = _c53_lifecycle_product_ar
    _c53_lifecycle__spec.loader.exec_module(_c53_lifecycle_product_ar)
    _c53_lifecycle_product_ar._inputs = _c53_lifecycle__literal_inputs

    def _c53_lifecycle__mark(builder, trace, label, expected=None, owners=None):
        live = builder.num_allocated_qubits
        if expected is not None:
            assert live == expected, (label, live, expected)
        if trace is not None:
            trace.append(dict(label=label, live_owners=live))
        if _c53_lifecycle_CUT_HOOK is not None:
            _c53_lifecycle_CUT_HOOK(label, builder, {} if owners is None else {key: list(value) for key, value in owners.items()})

    def _c53_lifecycle__erase(builder, target, variables, plan):
        outcome = builder.alloc_bits(1)[0]
        builder.hmr(target, outcome)
        _c53_lifecycle_cb.emit_phase(builder, list(variables), outcome, plan)
        builder.free(outcome)
        builder.free(target)

    def _c53_lifecycle_root_R_frame(builder, v, *, inverse=False):
        operations = [('cx', v[7], v[8]), ('cx', v[7], v[10]), ('ccx', v[6], v[10], v[8]), ('cx', v[7], v[10])]
        if inverse:
            operations.reverse()
        for name, *wires in operations:
            getattr(builder, name)(*wires)

    def _c53_lifecycle_seed_root_frame(builder, v, *, inverse=False):
        operations = [('cx', v[2], v[0]), ('cx', v[2], v[1]), ('cx', v[2], v[3]), ('ccx', v[0], v[1], v[3]), ('cx', v[1], v[0])]
        if inverse:
            operations.reverse()
        for name, *wires in operations:
            getattr(builder, name)(*wires)

    def _c53_lifecycle_prepare_H3_initial(builder, v, A, Hlow):
        q = builder.alloc_qubits(1)[0]
        _c53_lifecycle_cb.emit_xor(builder, [A[i] for i in (10, 11, 12)] + [Hlow[2], v[10], v[11]], q, _c53_lifecycle_H3_INITIAL)
        return q

    def _c53_lifecycle_prepare_H3_current(builder, v, D, Hlow):
        q = builder.alloc_qubits(1)[0]
        _c53_lifecycle_cb.emit_xor(builder, [D[i] for i in (9, 10, 11, 12)] + [Hlow[2], v[10]], q, _c53_lifecycle_H3_CURRENT)
        return q

    def _c53_lifecycle_prepare_H4(builder, D, H3):
        q = builder.alloc_qubits(1)[0]
        _c53_lifecycle_cb.emit_xor(builder, [D[11], D[12], H3], q, _c53_lifecycle_H4_PLAN)
        return q

    def _c53_lifecycle_erase_high_H(builder, v, D, H, *, initial=False):
        """Erase H4 first, retaining H3 until its dependent phase is paid."""
        _c53_lifecycle__erase(builder, H[4], [D[11], D[12], H[3]], _c53_lifecycle_H4_PLAN)
        variables = [D[i] for i in (10, 11, 12)] + [H[2], v[10], v[11]] if initial else [D[i] for i in (9, 10, 11, 12)] + [H[2], v[10]]
        _c53_lifecycle__erase(builder, H[3], variables, _c53_lifecycle_H3_INITIAL if initial else _c53_lifecycle_H3_CURRENT)
        return list(H[:3])

    def _c53_lifecycle__coefficient_carry(builder, S, sign, k):
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

    def _c53_lifecycle__clear_coefficient_carry(builder, S, sign, k, q):
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

    def _c53_lifecycle_coefficient_forward(builder, v, D, H):
        S = [v[8]] + list(H)
        snapshot = builder.alloc_qubits(1)[0]
        builder.cx(D[6], snapshot)
        token = _c53_lifecycle_ar.DeferredBoundedToken(_c53_lifecycle_SimpleNamespace(last=5, signed_source=False), snapshot, 7, [])
        for i in range(5):
            k = 4 - i
            carry = _c53_lifecycle__coefficient_carry(builder, S, v[i], k)
            for q in D[:7]:
                builder.cx(v[i], q)
            token.row_debts.append(_c53_lifecycle_ar.forward_add(builder, S[k + 1:], D[:7], carry_in=carry))
            for q in D[:7]:
                builder.cx(v[i], q)
            _c53_lifecycle__clear_coefficient_carry(builder, S, v[i], k, carry)
        _c53_lifecycle_ar._deferred_overflow(builder, v[:5], S, D, token, inverse=False)
        return token

    def _c53_lifecycle__merge_debts(builder, first, second):
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

    def _c53_lifecycle_merge_coefficient_transcripts(builder, first, second):
        assert first.window == second.window == 7 and len(first.row_debts) == len(second.row_debts) == 5
        for a, b in zip(first.row_debts, second.row_debts):
            _c53_lifecycle__merge_debts(builder, a, b)
        _c53_lifecycle__merge_debts(builder, first.overflow_debt, second.overflow_debt)

    def _c53_lifecycle_coefficient_inverse(builder, v, D, H, token, dirty):
        S = [v[8]] + list(H)
        _c53_lifecycle_ar._deferred_overflow(builder, v[:5], S, D, token, inverse=True)
        saved = _c53_lifecycle_ar.release_saved_bit(builder, token.saved_bit)
        token.saved_bit = None
        for i in reversed(range(5)):
            k = 4 - i
            carry = _c53_lifecycle__coefficient_carry(builder, S, v[i], k)
            for q in D[:7]:
                builder.cx(v[i], q)
            _c53_lifecycle_ar.inverse_add(builder, S[k + 1:], D[:7], token.row_debts[i], carry_in=carry, dirty_wires=dirty)
            for q in D[:7]:
                builder.cx(v[i], q)
            _c53_lifecycle__clear_coefficient_carry(builder, S, v[i], k, carry)
        _c53_lifecycle_ar.repay_saved_bit(builder, D[6], saved)
        assert all((d.consumed and (not d.measurements) for d in token.row_debts))
        assert token.overflow_debt.consumed and (not token.overflow_debt.measurements)

    @_c53_lifecycle_dataclass
    class _c53_lifecycle_SeedToken:
        rows: list

    def _c53_lifecycle_seed_forward(builder, v, D):
        _c53_lifecycle_seed_root_frame(builder, v)
        seed = list(builder.alloc_qubits(3))
        builder.x(_c53_lifecycle_array(seed))
        rows = []
        for i, control in enumerate((v[0], v[1], v[3])):
            builder.x(control)
            rows.append(_c53_lifecycle_ar.forward_signed_row(builder, D, seed, shift=-(11 - i), sign=control))
            builder.x(control)
            q = builder.alloc_qubits(1)[0]
            builder.x(q)
            builder.cx(control, q)
            seed.append(q)
        _c53_lifecycle_seed_root_frame(builder, v, inverse=True)
        return (seed, _c53_lifecycle_SeedToken(rows))

    def _c53_lifecycle_seed_cleanup(builder, v, D, seed, token):
        seed = list(seed)
        _c53_lifecycle_seed_root_frame(builder, v)
        raw = list(D[8:13]) + [v[0], v[1], v[3]]
        _c53_lifecycle__erase(builder, seed[5], raw, _c53_lifecycle_plan_from_json(_c53_lifecycle_SEED['initial_seed5_erasure']))
        helpers = []
        for item in _c53_lifecycle_SEED['persistent_helpers']:
            q = builder.alloc_qubits(1)[0]
            _c53_lifecycle_cb.emit_xor(builder, raw + helpers, q, _c53_lifecycle_plan_from_json(item['plan']))
            helpers.append(q)
        carries = []
        for debt in token.rows:
            carries.extend((debt.measurements[position] for position in sorted(debt.measurements)))
        assert len(carries) == len(_c53_lifecycle_SEED['carry_phase_plans']) == 6
        for outcome, plan in zip(carries, _c53_lifecycle_SEED['carry_phase_plans']):
            _c53_lifecycle_cb.emit_phase(builder, raw + helpers + seed[:5], outcome, _c53_lifecycle_plan_from_json(plan))
            builder.free(outcome)
        for debt in token.rows:
            debt.measurements.clear()
            debt.consumed = True
        m = builder.alloc_bits(1)[0]
        builder.hmr(seed[4], m)
        builder.free(seed[4])
        fifth = builder.alloc_qubits(1)[0]
        builder.push_condition(m)
        _c53_lifecycle_cb.emit_xor(builder, raw + helpers, fifth, _c53_lifecycle_plan_from_json(_c53_lifecycle_SEED['conditional_helper']['plan']))
        builder.pop_condition()
        _c53_lifecycle_cb.emit_phase(builder, raw + helpers + [fifth] + seed[:4], m, _c53_lifecycle_plan_from_json(_c53_lifecycle_SEED['seed4_erasure']['plan']))
        aux = builder.alloc_bits(1)[0]
        builder.hmr(fifth, aux)
        builder.push_condition(m)
        _c53_lifecycle_cb.emit_phase(builder, raw + helpers, aux, _c53_lifecycle_plan_from_json(_c53_lifecycle_SEED['conditional_helper']['plan']))
        builder.pop_condition()
        builder.free(aux)
        builder.free(fifth)
        builder.free(m)
        for item in _c53_lifecycle_SEED['remaining_seed_erasures']:
            i = item['bit']
            variables = raw + helpers + [seed[j] for j in item['remaining_seed_bits']]
            _c53_lifecycle__erase(builder, seed[i], variables, _c53_lifecycle_plan_from_json(item['plan']))
        for i in reversed(range(4)):
            _c53_lifecycle__erase(builder, helpers[i], raw + helpers[:i], _c53_lifecycle_plan_from_json(_c53_lifecycle_SEED['persistent_helpers'][i]['plan']))
        _c53_lifecycle_seed_root_frame(builder, v, inverse=True)

    def _c53_lifecycle__product_carry(builder, C, q, i):
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

    def _c53_lifecycle__clear_product_carry(builder, C, q, i, carry):
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

    @_c53_lifecycle_dataclass
    class _c53_lifecycle_ProductToken:
        rows: list

    def _c53_lifecycle_product_forward(builder, D, seed, h):
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
            carry = _c53_lifecycle__product_carry(builder, C, q, i)
            rows.append(_c53_lifecycle_product_ar.forward_add(builder, source, target, carry_in=carry))
            _c53_lifecycle__clear_product_carry(builder, C, q, i, carry)
            for t in target:
                builder.cx(q, t)
        builder.x(word[15])
        return (word, _c53_lifecycle_ProductToken(rows))

    def _c53_lifecycle_product_inverse(builder, D, word, token, dirty):
        word = list(word)
        C = [False] + list(D)
        builder.x(word[15])
        for i in reversed(range(10)):
            q = word[6 + i]
            target = word[:6 + i]
            source = C[9 - i:] if i < 9 else C
            for t in target:
                builder.cx(q, t)
            carry = _c53_lifecycle__product_carry(builder, C, q, i)
            _c53_lifecycle_product_ar.inverse_add(builder, source, target, token.rows[i], carry_in=carry, dirty_wires=dirty + word[6:])
            _c53_lifecycle__clear_product_carry(builder, C, q, i, carry)
            for t in target:
                builder.cx(q, t)
        builder.x(word[15])
        assert all((d.consumed and (not d.measurements) for d in token.rows))
        return (word[:6], word[6:])

    def _c53_lifecycle_emit_body(builder, v12, h10, flags4, table_module, divider_module, decode_root_callback, *, trace=None):
        """Compute/phase/uncompute and return current(v12,h10) physical owners."""
        v = list(v12)
        h = list(h10)
        flags = list(flags4)
        assert (len(v), len(h), len(flags)) == (12, 10, 4)
        _c53_lifecycle__mark(builder, trace, 'body_entry', 26, dict(v=v, h=h, flags=flags))
        table_debts = table_module.TableDebts()
        truths = table_module.model_truths()
        D, Hlow = table_module.load_joint16(builder, v[5:], variant='first', debts=table_debts)
        D = list(D)
        H = list(Hlow)
        _c53_lifecycle__mark(builder, trace, 'first_table', 42, dict(v=v, h=h, flags=flags, D=D, H=H))
        H.append(_c53_lifecycle_prepare_H3_initial(builder, v, D, H))
        _c53_lifecycle_root_R_frame(builder, v)
        H.append(_c53_lifecycle_prepare_H4(builder, D, H[3]))
        first = _c53_lifecycle_coefficient_forward(builder, v, D, H)
        _c53_lifecycle__mark(builder, trace, 'first_coefficient', 45, dict(v=v, h=h, flags=flags, D=D, H=H, snapshot=[first.saved_bit]))
        Hlow = _c53_lifecycle_erase_high_H(builder, v, D, H)
        for i, q in enumerate(Hlow):
            table_debts.erase(builder, q, truths['H'][i], free=True)
        first_snapshot = _c53_lifecycle_ar.release_saved_bit(builder, first.saved_bit)
        first.saved_bit = None
        _c53_lifecycle_root_R_frame(builder, v, inverse=True)
        _c53_lifecycle__mark(builder, trace, 'first_metadata_retired', 39)
        seed, seed_token = _c53_lifecycle_seed_forward(builder, v, D)
        _c53_lifecycle__mark(builder, trace, 'seed_ready', 45, dict(v=v, h=h, flags=flags, D=D, seed=seed))
        word, product_token = _c53_lifecycle_product_forward(builder, D, seed, h)
        builder.x(word[15])
        builder.cx(word[14], word[15])
        builder.free(word[15])
        P = word[:15]
        _c53_lifecycle__mark(builder, trace, 'signed_product15', 44, dict(v=v, P=P, flags=flags, D=D))
        first_D = []
        for q in D:
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            builder.free(q)
            first_D.append(m)
        _c53_lifecycle__mark(builder, trace, 'coefficient_retired_for_divider', 31, dict(v=v, P=P, flags=flags))
        P = list(divider_module.compute_phase_cleanup(builder, v, P, flags))
        assert len(P) == 15
        _c53_lifecycle__mark(builder, trace, 'divider_return', 31, dict(v=v, P=P, flags=flags))
        D, Hlow = table_module.load_joint16(builder, v[5:], variant='second', debts=table_debts)
        D = list(D)
        H = list(Hlow)
        _c53_lifecycle__mark(builder, trace, 'second_table', 47, dict(v=v, P=P, flags=flags, D=D, H=H))
        _c53_lifecycle_ar.repay_saved_bit(builder, D[6], first_snapshot)
        H.append(_c53_lifecycle_prepare_H3_initial(builder, v, D, H))
        _c53_lifecycle_root_R_frame(builder, v)
        retired = {}
        for a in (0, 1, 2, 4, 6):
            q = v[5 + a]
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            builder.free(q)
            v[5 + a] = None
            retired[a] = m
        H.append(_c53_lifecycle_prepare_H4(builder, D, H[3]))
        second = _c53_lifecycle_coefficient_forward(builder, v, D, H)
        _c53_lifecycle__mark(builder, trace, 'second_coefficient', 45, dict(v=v, P=P, flags=flags, D=D, H=H, snapshot=[second.saved_bit]))
        for q, m in zip(D, first_D):
            builder.push_condition(m)
            builder.z(q)
            builder.pop_condition()
            builder.free(m)
        _c53_lifecycle_merge_coefficient_transcripts(builder, first, second)
        Hlow = _c53_lifecycle_erase_high_H(builder, v, D, H)
        _c53_lifecycle__mark(builder, trace, 'second_metadata_retired', 43)
        high = builder.alloc_qubits(1)[0]
        builder.cx(P[14], high)
        builder.x(high)
        word = P + [high]
        _c53_lifecycle__mark(builder, trace, 'inverse_product_data', 44, dict(v=v, word=word, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
        dirty = [q for q in v if q is not None] + flags + Hlow + [second.saved_bit]
        seed, h = _c53_lifecycle_product_inverse(builder, D, word, product_token, dirty)
        _c53_lifecycle_seed_cleanup(builder, v, D, seed, seed_token)
        _c53_lifecycle__mark(builder, trace, 'seed_cleared', 38, dict(v=v, h=h, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
        H = list(Hlow)
        H.append(_c53_lifecycle_prepare_H3_current(builder, v, D, H))
        H.append(_c53_lifecycle_prepare_H4(builder, D, H[3]))
        _c53_lifecycle__mark(builder, trace, 'coefficient_sources_restored', 40)
        _c53_lifecycle_coefficient_inverse(builder, v, D, H, second, [q for q in v if q is not None] + flags + h)
        _c53_lifecycle__mark(builder, trace, 'A_restored', 39, dict(v=v, h=h, flags=flags, A=D, H=H))
        v = list(decode_root_callback(builder, v, D, H, retired))
        assert all((q is not None for q in v))
        _c53_lifecycle_root_R_frame(builder, v, inverse=True)
        _c53_lifecycle__mark(builder, trace, 'raw_root_restored', 44, dict(v=v, h=h, flags=flags, A=D, H=H))
        Hlow = _c53_lifecycle_erase_high_H(builder, v, D, H, initial=True)
        table_module.cleanup_joint16(builder, v[5:], D, Hlow, table_debts)
        assert not table_debts.pending
        _c53_lifecycle__mark(builder, trace, 'body_return', 26, dict(v=v, h=h, flags=flags))
        return (v, h)

# work/c10/narrow/native/candidate01/normalization.py
def _initialize__c54_normalization():
    global _c54_normalization_ENGINE, _c54_normalization_HERE, _c54_normalization_INTEGRATED_ROOT, _c54_normalization_KICKMIX, _c54_normalization_MAX_X, _c54_normalization_MODEL, _c54_normalization_MODEL_PATH, _c54_normalization_MODEL_SHA, _c54_normalization_NARROW, _c54_normalization_PATH, _c54_normalization_Path, _c54_normalization_SHA, _c54_normalization_TESTS, _c54_normalization_TOOLING, _c54_normalization__IntegratedPath, _c54_normalization___file__, _c54_normalization___name__, _c54_normalization_array, _c54_normalization_cb, _c54_normalization_checked_json, _c54_normalization_current_gate, _c54_normalization_forward, _c54_normalization_hashlib, _c54_normalization_importlib, _c54_normalization_inverse, _c54_normalization_json, _c54_normalization_km, _c54_normalization_os, _c54_normalization_plan_from_json, _c54_normalization_source, _c54_normalization_spec, _c54_normalization_sys, _c54_normalization_verify_gate_sources, _c54_normalization_with_registers
    'Native binding of the frozen, independently proved pair-normalization map.'
    _c54_normalization__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate01/normalization.py', False).Path
    _c54_normalization_INTEGRATED_ROOT = _c54_normalization__IntegratedPath(_c54_normalization___file__).resolve().parents[5]
    _import_star('_c54_normalization_', _import_component('common', 'work/c10/narrow/native/candidate01/normalization.py', False))
    _c54_normalization_importlib = _import_component('importlib.util', 'work/c10/narrow/native/candidate01/normalization.py', True)
    _c54_normalization_PATH = _c54_normalization_NARROW / 'research/quantized_producer/pair_normalization.py'
    _c54_normalization_SHA = '6af7fc14bc3c904efe480e2e23aee2fcbd97ad23f0a7ba324d8c05e1c8ec17fe'
    pass
    _c54_normalization_spec = _spec('native_pair_normalization_source', _c54_normalization_PATH)
    _c54_normalization_source = _new_module(_c54_normalization_spec)
    _c54_normalization_sys.modules[_c54_normalization_spec.name] = _c54_normalization_source
    _c54_normalization_spec.loader.exec_module(_c54_normalization_source)
    _c54_normalization_forward = _c54_normalization_source.forward
    _c54_normalization_inverse = _c54_normalization_source.inverse
    _c54_normalization_MAX_X = _c54_normalization_source.MAX_X

# work/c10/narrow/native/candidate01/root_decode.py
def _initialize__c55_root_decode():
    global _c55_root_decode_CERT, _c55_root_decode_ENGINE, _c55_root_decode_HERE, _c55_root_decode_INTEGRATED_ROOT, _c55_root_decode_KICKMIX, _c55_root_decode_MODEL, _c55_root_decode_MODEL_PATH, _c55_root_decode_MODEL_SHA, _c55_root_decode_NARROW, _c55_root_decode_Path, _c55_root_decode_TESTS, _c55_root_decode_TOOLING, _c55_root_decode__IntegratedPath, _c55_root_decode___file__, _c55_root_decode___name__, _c55_root_decode_array, _c55_root_decode_cb, _c55_root_decode_checked_json, _c55_root_decode_current_gate, _c55_root_decode_decode_root, _c55_root_decode_hashlib, _c55_root_decode_json, _c55_root_decode_km, _c55_root_decode_linear_frame, _c55_root_decode_os, _c55_root_decode_plan_from_json, _c55_root_decode_sys, _c55_root_decode_verify_gate_sources, _c55_root_decode_with_registers
    'Restore five retired raw root coordinates from the frozen21-AND code.'
    _c55_root_decode__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate01/root_decode.py', False).Path
    _c55_root_decode_INTEGRATED_ROOT = _c55_root_decode__IntegratedPath(_c55_root_decode___file__).resolve().parents[5]
    _import_star('_c55_root_decode_', _import_component('common', 'work/c10/narrow/native/candidate01/root_decode.py', False))
    _c55_root_decode_linear_frame = _import_component('thermometer_cleanup', 'work/c10/narrow/native/candidate01/root_decode.py', False).linear_frame
    _c55_root_decode_CERT = _c55_root_decode_checked_json(_c55_root_decode_NARROW / 'research/quantized_producer/framed_retained5_best21_snapshot.json', '3b6fa7059bee77bb9abe6c7395cd8ff2f2899843523188c60d513e6c5d381def')

    def _c55_root_decode_decode_root(builder, v, A, H, retired_outcomes):
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
        for record in _c55_root_decode_CERT['plans']:
            p = _c55_root_decode_plan_from_json(record['plan'])
            assert p.width == len(features)
            q = builder.alloc_qubits(1)[0]
            _c55_root_decode_cb.emit_xor(builder, features, q, p)
            outputs.append(q)
            features.append(q)
        rows = [_c55_root_decode_CERT['raw_five_from_code'][str(i)] for i in missing]
        for kind, i, j in _c55_root_decode_linear_frame(rows):
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

# work/c10/narrow/native/candidate01/tables.py
def _initialize__c56_tables():
    global _c56_tables_Any, _c56_tables_CODEBOOK_SHA, _c56_tables_FROZEN, _c56_tables_FULL, _c56_tables_INTEGRATED_ROOT, _c56_tables_MODEL, _c56_tables_MODEL_SHA, _c56_tables_NARROW, _c56_tables_PINS, _c56_tables_TableDebt, _c56_tables_TableDebts, _c56_tables__IntegratedPath, _c56_tables___file__, _c56_tables___name__, _c56_tables__affine_xor, _c56_tables__row_matrix_inverse_operations, _c56_tables__swap, _c56_tables_annotations, _c56_tables_array, _c56_tables_cb, _c56_tables_certificate, _c56_tables_checked_json, _c56_tables_cleanup_joint16, _c56_tables_dataclass, _c56_tables_emit_affine_frame, _c56_tables_hashlib, _c56_tables_km, _c56_tables_load_joint16, _c56_tables_lru_cache, _c56_tables_model_truths, _c56_tables_model_values, _c56_tables_plan_from_json
    'Pinned own joint A/H loaders and exact deferred table-phase cleanup.\n\nThe first/second loaders use60/73 unconditional CCX gates and return the same\nsixteen physical output meanings. All helper measurement phases are explicitly\nowned by TableDebts until the original raw address and A/H chart is restored.\n'
    pass
    _c56_tables__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate01/tables.py', False).Path
    _c56_tables_INTEGRATED_ROOT = _c56_tables__IntegratedPath(_c56_tables___file__).resolve().parents[5]
    _c56_tables_dataclass = _import_component('dataclasses', 'work/c10/narrow/native/candidate01/tables.py', False).dataclass
    _c56_tables_lru_cache = _import_component('functools', 'work/c10/narrow/native/candidate01/tables.py', False).lru_cache
    _c56_tables_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate01/tables.py', True)
    _c56_tables_Any = _import_component('typing', 'work/c10/narrow/native/candidate01/tables.py', False).Any
    _c56_tables_km = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).km
    _c56_tables_cb = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).cb
    _c56_tables_NARROW = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).NARROW
    _c56_tables_MODEL = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).MODEL
    _c56_tables_MODEL_SHA = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).MODEL_SHA
    _c56_tables_checked_json = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).checked_json
    _c56_tables_plan_from_json = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).plan_from_json
    _c56_tables_array = _import_component('common', 'work/c10/narrow/native/candidate01/tables.py', False).array
    _c56_tables_FROZEN = _c56_tables_NARROW / 'research/joint_loader/frozen'
    _c56_tables_PINS = {'first': ('loader16_first60.json', '3bcbd49ad53c0e2661bbc1112d172c854d4bf50ba4ea1f9a119a077f8e6cd9fd'), 'second': ('loader16_second73.json', '52db753c9efef945c9194ed4a39ec3b250221b69eb10e0030dc2a283f659eafc'), 'cleanup': ('retained_table_cleanup9.json', '6a48b472433918d2c51f30e6eeb1d9933fdf1aa4ae9f83b93129fd8ac103b6b5')}
    _c56_tables_CODEBOOK_SHA = '9c6073d78becea467d37805131fdcc572e530c72acef5664b08057ef883f17be'
    pass
    pass
    _c56_tables_FULL = (1 << 128) - 1

    @_c56_tables_dataclass(frozen=True)
    class _c56_tables_TableDebt:
        outcome: Any
        truth128: int

    class _c56_tables_TableDebts:
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
            if not isinstance(outcome, _c56_tables_km.b):
                raise TypeError('A table HMR outcome must be a classical bit.')
            if outcome in self._owned:
                raise ValueError('A table HMR outcome already has an owner.')
            if not 0 <= truth128 <= _c56_tables_FULL:
                raise ValueError('A seven-bit table truth must contain at most128 rows.')
            self.pending.append(_c56_tables_TableDebt(outcome, truth128))
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
            book = _c56_tables_cb.Codebook(functions, 128)
            if len(book.span.pivots) != 128:
                raise ValueError('The supplied table phase chart is not universal.')
            count = len(self.pending)
            for debt in self.pending:
                expression = book.span.solve(debt.truth128)
                if expression is None:
                    raise AssertionError('A pending table truth is outside the live phase chart.')
                plan = book.decode_expression(expression)
                assert plan.evaluate_functions(functions, _c56_tables_FULL) == debt.truth128
                _c56_tables_cb.emit_phase(builder, variables, debt.outcome, plan)
                builder.free(debt.outcome)
            self.pending.clear()
            self._owned.clear()
            return dict(outcomes=count, Toffolis=0, quadratic_rank=128)

    @_c56_tables_lru_cache(maxsize=3)
    def _c56_tables_certificate(which):
        name, digest = _c56_tables_PINS[which]
        data = _c56_tables_checked_json(_c56_tables_FROZEN / name, digest)
        pass
        return data

    @_c56_tables_lru_cache(maxsize=1)
    def _c56_tables_model_values():
        return dict(A=tuple(map(int, _c56_tables_MODEL['A'])), S=tuple(map(int, _c56_tables_MODEL['S'])), H=tuple(map(int, _c56_tables_MODEL['stored_slope'])))

    @_c56_tables_lru_cache(maxsize=1)
    def _c56_tables_model_truths():
        values = _c56_tables_model_values()
        return dict(address=tuple(_c56_tables_cb.word_functions(range(128), 7)), A=tuple(_c56_tables_cb.word_functions(values['A'], 13)), S=tuple(_c56_tables_cb.word_functions(values['S'], 6)), H=tuple(_c56_tables_cb.word_functions(values['H'], 5)))

    def _c56_tables__row_matrix_inverse_operations(rows, width):
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

    def _c56_tables__swap(builder, a, b):
        if a == b:
            return
        builder.cx(a, b)
        builder.cx(b, a)
        builder.cx(a, b)

    def _c56_tables_emit_affine_frame(builder, address, work, rows):
        """Apply an invertible work-wire matrix plus raw-address affine terms."""
        address = list(address)
        work = list(work)
        rows = list(map(int, rows))
        if len(address) != 7:
            raise ValueError('Expected seven unchanged raw address wires.')
        for kind, a, b in _c56_tables__row_matrix_inverse_operations([row >> 8 for row in rows], len(work)):
            if kind == 'cx':
                builder.cx(work[a], work[b])
            else:
                _c56_tables__swap(builder, work[a], work[b])
        for target, row in zip(work, rows):
            if row & 1:
                builder.x(target)
            for bit in range(7):
                if row >> 1 + bit & 1:
                    builder.cx(address[bit], target)

    def _c56_tables__affine_xor(builder, address, previous, target, expression):
        if expression & 1:
            builder.x(target)
        variables = list(address) + list(previous)
        for bit in _c56_tables_cb.bits(expression >> 1):
            builder.cx(variables[bit], target)

    def _c56_tables_load_joint16(builder, address7, *, variant, debts):
        """Allocate, load and return(A13,Hlow3), preserving raw address7.

    The complete reusable work pool is23/18 qubits, including all16 outputs.
    Seven/two zero helpers are released on return. Quantum input owners outside
    this function are26/31 respectively in the complete Q49 circuit.
    """
        if variant not in ('first', 'second'):
            raise ValueError('variant must be first or second.')
        address = list(address7)
        if len(address) != 7 or len(set(address)) != 7:
            raise ValueError('Expected seven distinct raw address wires.')
        if not isinstance(debts, _c56_tables_TableDebts):
            raise TypeError('Expected the shared TableDebts owner.')
        data = _c56_tables_certificate(variant)
        cap = data['work_cap']
        pool = list(builder.alloc_qubits(cap))
        available = list(pool)
        work = []
        actual_count = 0
        for item in data['steps']:
            kind = item['kind']
            if kind == 'bank':
                target = available.pop(0)
                plan = _c56_tables_plan_from_json(item['plan'])
                _c56_tables_cb.emit_xor(builder, address + work, target, plan)
                work.append(target)
                actual_count += plan.and_count
            elif kind == 'Clifford_zero_dependent_coordinate':
                index = item['index']
                target = work[index]
                _c56_tables__affine_xor(builder, address, work[:index], target, item['expression'])
                work.pop(index)
                available.append(target)
            elif kind == 'Clifford_frame_then_HMR':
                _c56_tables_emit_affine_frame(builder, address, work, item['full_affine_rows'])
                kept = item['retained_count']
                discard = work[kept:]
                assert len(discard) == len(item['discarded_truths'])
                for wire, truth in zip(discard, item['discarded_truths']):
                    debts.erase(builder, wire, int(truth, 16))
                    available.append(wire)
                work = work[:kept]
            elif kind == 'virtual_affine_product':
                pass
            elif kind == 'CCX_new_coordinate':
                target = available.pop(0)
                plan = _c56_tables_plan_from_json(item['plan'])
                _c56_tables_cb.emit_xor(builder, address + work, target, plan)
                work.append(target)
                actual_count += plan.and_count
            elif kind == 'XOR_product_existing_coordinate':
                assert item['target_index'] == 0
                plan = _c56_tables_plan_from_json(item['plan'])
                _c56_tables_cb.emit_xor(builder, address + work[1:], work[0], plan)
                actual_count += plan.and_count
            elif kind == 'final_output_Clifford_frame':
                _c56_tables_emit_affine_frame(builder, address, work, [int(row) << 8 for row in item['matrix_rows']])
            else:
                raise AssertionError(f'Unknown frozen loader operation:{kind}')
            assert len(work) + len(available) == cap and len(set(work + available)) == cap
        assert len(work) == 16 and actual_count == data['Toffolis'] == (60 if variant == 'first' else 73)
        if available:
            builder.free(_c56_tables_array(available))
        return (list(work[:13]), list(work[13:16]))

    def _c56_tables_cleanup_joint16(builder, address7, A13, Hlow3, debts):
        """Repay all table debts and erase/free the sixteen outputs for9CCX."""
        address = list(address7)
        A = list(A13)
        H = list(Hlow3)
        if (len(address), len(A), len(H)) != (7, 13, 3):
            raise ValueError('Wrong final table chart widths.')
        if len(set(address + A + H)) != 23:
            raise ValueError('Final table chart owners overlap.')
        truths = _c56_tables_model_truths()
        outputs = A + H
        functions = list(truths['address']) + list(truths['A']) + list(truths['H'][:3])
        flushed = debts.flush(builder, address + outputs, functions)
        data = _c56_tables_certificate('cleanup')
        case = next((c for c in data['cases'] if c['output_count'] == 16))
        _c56_tables_emit_affine_frame(builder, address, outputs, [int(row) << 8 for row in case['output_Clifford_basis_rows']])
        wires = {f'r{i}': wire for i, wire in enumerate(address)}
        wires.update({f'c{i}': wire for i, wire in enumerate(outputs)})
        count = 0
        for item in case['steps']:
            kind = item['kind']
            if kind == 'bank':
                variables = [wires[name] for name in item['inputs']]
                target = builder.alloc_qubits(1)[0]
                plan = _c56_tables_plan_from_json(item['plan'])
                _c56_tables_cb.emit_xor(builder, variables, target, plan)
                wires[item['name']] = target
                count += plan.and_count
            elif kind in ('HMR_output', 'HMR_bank'):
                variables = [wires[name] for name in item['retained']]
                target = wires.pop(item['name'])
                plan = _c56_tables_plan_from_json(item['phase_plan'])
                _c56_tables_cb.emit_erase(builder, variables, [target], [plan])
                builder.free(target)
            else:
                raise AssertionError(f'Unknown cleanup operation:{kind}')
        assert count == 9 and set(wires) == {f'r{i}' for i in range(7)} and (not debts.pending)
        return dict(Toffolis=9, table_debts_repaid=flushed['outcomes'], quantum_outputs_erased=16)

# work/c10/narrow/native/candidate02/variant.py
def _initialize__c57_candidate02_setup():
    global _c57_candidate02_setup_BASE, _c57_candidate02_setup_HERE, _c57_candidate02_setup_INPUTS, _c57_candidate02_setup_INTEGRATED_ROOT, _c57_candidate02_setup_NARROW, _c57_candidate02_setup_Path, _c57_candidate02_setup__IntegratedPath, _c57_candidate02_setup___file__, _c57_candidate02_setup___name__, _c57_candidate02_setup_baseline_divider, _c57_candidate02_setup_common, _c57_candidate02_setup_copy, _c57_candidate02_setup_hashlib, _c57_candidate02_setup_importlib, _c57_candidate02_setup_initialize_u12, _c57_candidate02_setup_install, _c57_candidate02_setup_json, _c57_candidate02_setup_load_baseline, _c57_candidate02_setup_os, _c57_candidate02_setup_sys, _c57_candidate02_setup_variant_gate
    'Isolated native variant; imports only pinned owned baseline sources.'
    _c57_candidate02_setup__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate02/variant.py', False).Path
    _c57_candidate02_setup_INTEGRATED_ROOT = _c57_candidate02_setup__IntegratedPath(_c57_candidate02_setup___file__).resolve().parents[5]
    _c57_candidate02_setup_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate02/variant.py', False).Path
    _c57_candidate02_setup_copy = _import_component('copy', 'work/c10/narrow/native/candidate02/variant.py', True)
    _c57_candidate02_setup_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate02/variant.py', True)
    _c57_candidate02_setup_importlib = _import_component('importlib.util', 'work/c10/narrow/native/candidate02/variant.py', True)
    _c57_candidate02_setup_json = _import_component('json', 'work/c10/narrow/native/candidate02/variant.py', True)
    _c57_candidate02_setup_os = _import_component('os', 'work/c10/narrow/native/candidate02/variant.py', True)
    _c57_candidate02_setup_sys = _import_component('sys', 'work/c10/narrow/native/candidate02/variant.py', True)
    _c57_candidate02_setup_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _c57_candidate02_setup_os.environ['OMP_NUM_THREADS'] = '1'
    _c57_candidate02_setup_HERE = _c57_candidate02_setup_Path(_c57_candidate02_setup___file__).resolve().parent
    _c57_candidate02_setup_BASE = _c57_candidate02_setup_HERE.parent / 'candidate01'
    _c57_candidate02_setup_NARROW = _c57_candidate02_setup_HERE.parents[1]
    _c57_candidate02_setup_INPUTS = _json_loads(_read_text(_c57_candidate02_setup_HERE / 'INPUTS.json'))
    pass
    _c57_candidate02_setup_sys.path.insert(0, str(_c57_candidate02_setup_BASE))
    _c57_candidate02_setup_common = _import_component('common', 'work/c10/narrow/native/candidate02/variant.py', True)
    _c57_candidate02_setup_baseline_divider = _import_component('divider', 'work/c10/narrow/native/candidate02/variant.py', False)

    def _c57_candidate02_setup_load_baseline(name):
        path = _c57_candidate02_setup_BASE / (name + '.py')
        module_name = 'candidate02_pinned_' + name
        if module_name in _c57_candidate02_setup_sys.modules:
            return _c57_candidate02_setup_sys.modules[module_name]
        spec = _spec(module_name, path)
        module = _new_module(spec)
        _c57_candidate02_setup_sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def _c57_candidate02_setup_initialize_u12(builder, v, P, u):
        """13-CCX direct triangular construction, followed by two exact HMRs."""
        d = _c57_candidate02_setup_baseline_divider
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

    def _c57_candidate02_setup_variant_gate():
        base = _c57_candidate02_setup_common.verify_gate_sources()
        accepted = _c57_candidate02_setup_common.checked_json(_c57_candidate02_setup_NARROW / 'PAPER_GATE_RECEIPT_011_VARIANT.json', '27a5fae99ae9ce4fed8602b52160618a25b56c56b30ea34b8101b64b161e53be')
        mathematical = _c57_candidate02_setup_common.checked_json(_c57_candidate02_setup_NARROW / 'research/recompute_root/initializer_u12_triangular/complete_gate.json', 'fc9626c050ad286dadcbb02ce5e901f7c651748dd804bd41c1ba564450ca7e7f')
        assert accepted['native_build_authorized_after_this_receipt'] and accepted['preserve_candidate01']
        result = _c57_candidate02_setup_copy.deepcopy(base)
        primary = result['primary']
        primary['complete_components'] = mathematical['complete_components']
        primary['Toffolis_expected'] = accepted['expected_Toffolis']
        primary['total_E'] = accepted['total_equivalents']
        primary['paper_cost'] = accepted['predicted_cost']
        primary['rotation_charge'] = accepted['rotation_charge']
        primary['margins'] = mathematical['margins']
        primary['core_change']['new_core'] = 577.5
        primary['core_change']['direct_u12'] = 14
        primary['core_change']['saving_E'] = 28.0
        primary['u12_initializer_peak'] = 45
        assert primary['Toffolis_expected'] == 1570.5 and primary['T'] == 4 and (primary['R'] == 34)
        assert primary['paper_cost'] == 89125.03208522254
        result['status'] = 'ACCEPTED_CANDIDATE02_TRIANGULAR_U12_VARIANT_GATE_NATIVE_PENDING'
        return result

    def _c57_candidate02_setup_install():
        """Change only this process's imported initializer, never an on-disk file."""
        _c57_candidate02_setup_variant_gate()
        _c57_candidate02_setup_baseline_divider.initialize_u12 = _c57_candidate02_setup_initialize_u12
        return _c57_candidate02_setup_baseline_divider

# work/c10/narrow/native/candidate03/variant.py
def _initialize__c58_candidate03_setup():
    global _c58_candidate03_setup_BASE, _c58_candidate03_setup_HERE, _c58_candidate03_setup_INTEGRATED_ROOT, _c58_candidate03_setup_NARROW, _c58_candidate03_setup_ORIGINAL_ROOT_STEP, _c58_candidate03_setup_Path, _c58_candidate03_setup__IntegratedPath, _c58_candidate03_setup___file__, _c58_candidate03_setup___name__, _c58_candidate03_setup_common, _c58_candidate03_setup_hashlib, _c58_candidate03_setup_importlib, _c58_candidate03_setup_install, _c58_candidate03_setup_json, _c58_candidate03_setup_load_baseline, _c58_candidate03_setup_os, _c58_candidate03_setup_path, _c58_candidate03_setup_previous, _c58_candidate03_setup_root, _c58_candidate03_setup_root_step, _c58_candidate03_setup_spec, _c58_candidate03_setup_sys, _c58_candidate03_setup_variant_gate
    'Isolated candidate03 root-tail specialization; no baseline file edits.'
    _c58_candidate03_setup__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate03/variant.py', False).Path
    _c58_candidate03_setup_INTEGRATED_ROOT = _c58_candidate03_setup__IntegratedPath(_c58_candidate03_setup___file__).resolve().parents[5]
    _c58_candidate03_setup_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate03/variant.py', False).Path
    _c58_candidate03_setup_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate03/variant.py', True)
    _c58_candidate03_setup_importlib = _import_component('importlib.util', 'work/c10/narrow/native/candidate03/variant.py', True)
    _c58_candidate03_setup_json = _import_component('json', 'work/c10/narrow/native/candidate03/variant.py', True)
    _c58_candidate03_setup_os = _import_component('os', 'work/c10/narrow/native/candidate03/variant.py', True)
    _c58_candidate03_setup_sys = _import_component('sys', 'work/c10/narrow/native/candidate03/variant.py', True)
    _c58_candidate03_setup_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _c58_candidate03_setup_os.environ['OMP_NUM_THREADS'] = '1'
    _c58_candidate03_setup_HERE = _c58_candidate03_setup_Path(_c58_candidate03_setup___file__).resolve().parent
    _c58_candidate03_setup_NARROW = _c58_candidate03_setup_HERE.parents[1]
    _c58_candidate03_setup_BASE = _c58_candidate03_setup_HERE.parent / 'candidate01'
    pass
    _c58_candidate03_setup_path = _c58_candidate03_setup_HERE.parent / 'candidate02/variant.py'
    _c58_candidate03_setup_spec = _spec('candidate03_pinned_candidate02_variant', _c58_candidate03_setup_path)
    _c58_candidate03_setup_previous = _new_module(_c58_candidate03_setup_spec)
    _c58_candidate03_setup_sys.modules[_c58_candidate03_setup_spec.name] = _c58_candidate03_setup_previous
    _c58_candidate03_setup_spec.loader.exec_module(_c58_candidate03_setup_previous)
    _c58_candidate03_setup_root = _import_component('consuming_odd_sqrt', 'work/c10/narrow/native/candidate03/variant.py', False)
    _c58_candidate03_setup_ORIGINAL_ROOT_STEP = _c58_candidate03_setup_root._root_step
    _c58_candidate03_setup_common = _c58_candidate03_setup_previous.common

    def _c58_candidate03_setup_root_step(builder, remainder, older, b, *, initial=False, inverse=False):
        if len(remainder) < 14:
            return _c58_candidate03_setup_ORIGINAL_ROOT_STEP(builder, remainder, older, b, initial=initial, inverse=inverse)
        assert len(remainder) in (14, 15) and (not initial) and isinstance(b, _c58_candidate03_setup_common.km.q)
        low = list(remainder[:3])
        high = list(remainder[3:])
        older = list(older)
        assert b not in list(remainder) + older
        if not inverse:
            builder.x(low[0])
            builder.x(low[1])
        builder.cx(b, _c58_candidate03_setup_root._arr(high))
        if inverse:
            _c58_candidate03_setup_root._add_leading_one(builder, high, inverse=True)
            _c58_candidate03_setup_root.add(builder, older, high, carry_in=b, subtract=True)
        else:
            _c58_candidate03_setup_root.add(builder, older, high, carry_in=b)
            _c58_candidate03_setup_root._add_leading_one(builder, high)
        builder.cx(b, _c58_candidate03_setup_root._arr(high))
        if inverse:
            builder.x(low[0])
            builder.x(low[1])

    def _c58_candidate03_setup_variant_gate():
        gate = _c58_candidate03_setup_previous.variant_gate()
        accepted = _c58_candidate03_setup_common.checked_json(_c58_candidate03_setup_NARROW / 'PAPER_GATE_RECEIPT_012_VARIANT.json', 'f11816ec390d58f379a7dc63704fab80a385bb581c73ec729c8e199697ad5131')
        assert accepted['native_build_authorized_after_this_receipt'] and accepted['preserve_candidate01'] and accepted['preserve_candidate02']
        primary = gate['primary']
        primary['complete_components']['consuming_root'] = 198
        primary['Toffolis_expected'] = accepted['expected_Toffolis']
        primary['total_E'] = accepted['total_equivalents']
        primary['paper_cost'] = accepted['predicted_cost']
        primary['root_peak_with_flags'] = 41
        primary['margins'] = {name: threshold - primary['paper_cost'] for name, threshold in [('stage97', 92278.95), ('target', 89987), ('stretch', 82740)]}
        assert primary['Toffolis_expected'] == 1562.5 and primary['T'] == 4 and (primary['R'] == 34)
        assert primary['paper_cost'] == 88733.03208522254
        gate['status'] = 'ACCEPTED_CANDIDATE03_ROOT_TAIL_GATE_NATIVE_PENDING'
        return gate

    def _c58_candidate03_setup_install():
        _c58_candidate03_setup_previous.install()
        _c58_candidate03_setup_variant_gate()
        _c58_candidate03_setup_root._root_step = _c58_candidate03_setup_root_step
        return _c58_candidate03_setup_root

    def _c58_candidate03_setup_load_baseline(name):
        return _c58_candidate03_setup_previous.load_baseline(name)

# work/c10/narrow/native/candidate04/variant.py
def _initialize__c59_candidate04_setup():
    global _c59_candidate04_setup_ACCEPTED, _c59_candidate04_setup_AngleProxy, _c59_candidate04_setup_BASE, _c59_candidate04_setup_BOUND, _c59_candidate04_setup_COEFFICIENTS37, _c59_candidate04_setup_Fraction, _c59_candidate04_setup_HERE, _c59_candidate04_setup_INPUTS, _c59_candidate04_setup_INTEGRATED_ROOT, _c59_candidate04_setup_LAST_PROXY_RECORDS, _c59_candidate04_setup_NARROW, _c59_candidate04_setup_NEW_TURN_UNITS50, _c59_candidate04_setup_ORIGINAL_ENDPOINT, _c59_candidate04_setup_Path, _c59_candidate04_setup_RESEARCH, _c59_candidate04_setup_SITES, _c59_candidate04_setup__INSTALLED, _c59_candidate04_setup__IntegratedPath, _c59_candidate04_setup___file__, _c59_candidate04_setup___name__, _c59_candidate04_setup_angle_class, _c59_candidate04_setup_checked_quantized, _c59_candidate04_setup_common, _c59_candidate04_setup_copy, _c59_candidate04_setup_divider, _c59_candidate04_setup_hashlib, _c59_candidate04_setup_importlib, _c59_candidate04_setup_install, _c59_candidate04_setup_json, _c59_candidate04_setup_load_baseline, _c59_candidate04_setup_math, _c59_candidate04_setup_os, _c59_candidate04_setup_path, _c59_candidate04_setup_phase_endpoint, _c59_candidate04_setup_previous, _c59_candidate04_setup_r, _c59_candidate04_setup_spec, _c59_candidate04_setup_sys, _c59_candidate04_setup_variant_gate, _c59_candidate04_setup_verify_inputs
    'Isolated angle-only candidate04 on the pinned candidate03 arithmetic.'
    _c59_candidate04_setup__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate04/variant.py', False).Path
    _c59_candidate04_setup_INTEGRATED_ROOT = _c59_candidate04_setup__IntegratedPath(_c59_candidate04_setup___file__).resolve().parents[5]
    _c59_candidate04_setup_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate04/variant.py', False).Path
    _c59_candidate04_setup_Fraction = _import_component('fractions', 'work/c10/narrow/native/candidate04/variant.py', False).Fraction
    _c59_candidate04_setup_copy = _import_component('copy', 'work/c10/narrow/native/candidate04/variant.py', True)
    _c59_candidate04_setup_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate04/variant.py', True)
    _c59_candidate04_setup_importlib = _import_component('importlib.util', 'work/c10/narrow/native/candidate04/variant.py', True)
    _c59_candidate04_setup_json = _import_component('json', 'work/c10/narrow/native/candidate04/variant.py', True)
    _c59_candidate04_setup_math = _import_component('math', 'work/c10/narrow/native/candidate04/variant.py', True)
    _c59_candidate04_setup_os = _import_component('os', 'work/c10/narrow/native/candidate04/variant.py', True)
    _c59_candidate04_setup_sys = _import_component('sys', 'work/c10/narrow/native/candidate04/variant.py', True)
    _c59_candidate04_setup_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _c59_candidate04_setup_os.environ['OMP_NUM_THREADS'] = '1'
    _c59_candidate04_setup_HERE = _c59_candidate04_setup_Path(_c59_candidate04_setup___file__).resolve().parent
    _c59_candidate04_setup_NARROW = _c59_candidate04_setup_HERE.parents[1]
    _c59_candidate04_setup_BASE = _c59_candidate04_setup_HERE.parent / 'candidate01'
    _c59_candidate04_setup_RESEARCH = _c59_candidate04_setup_NARROW / 'research/postgate_angle_refit'
    _c59_candidate04_setup_INPUTS = _json_loads(_read_text(_c59_candidate04_setup_HERE / 'INPUTS.json'))

    def _c59_candidate04_setup_verify_inputs():
        """Source integrity is verified by the integrated manifest before execution."""
        pass
    _c59_candidate04_setup_verify_inputs()
    _c59_candidate04_setup_path = _c59_candidate04_setup_HERE.parent / 'candidate03/variant.py'
    _c59_candidate04_setup_spec = _spec('candidate04_pinned_candidate03_variant', _c59_candidate04_setup_path)
    _c59_candidate04_setup_previous = _new_module(_c59_candidate04_setup_spec)
    _c59_candidate04_setup_sys.modules[_c59_candidate04_setup_spec.name] = _c59_candidate04_setup_previous
    _c59_candidate04_setup_spec.loader.exec_module(_c59_candidate04_setup_previous)
    _c59_candidate04_setup_common = _c59_candidate04_setup_previous.common
    _c59_candidate04_setup_divider = _c59_candidate04_setup_previous.previous.baseline_divider
    _c59_candidate04_setup_BOUND = _json_loads(_read_text(_c59_candidate04_setup_RESEARCH / 'quantize50_bound.json'))
    _c59_candidate04_setup_ACCEPTED = _json_loads(_read_text(_c59_candidate04_setup_NARROW / 'PAPER_GATE_RECEIPT_014_VARIANT.json'))
    assert _c59_candidate04_setup_ACCEPTED['native_build_authorized'] and _c59_candidate04_setup_ACCEPTED['preserve_candidates_01_02_03']
    pass
    assert _c59_candidate04_setup_BOUND['proved_quantized_margin_lower_bound_units'] == _c59_candidate04_setup_ACCEPTED['proved_margin_lower_bound_units64'] == 124286782
    _c59_candidate04_setup_COEFFICIENTS37 = tuple(((1 << i) + (1 << 27 if i == 0 else 0) for i in range(27))) + (-(1 << 27),) + tuple((1 << 27 + j for j in range(1, 7)))
    _c59_candidate04_setup_SITES = tuple((f'base_i{i}' for i in range(27))) + ('threshold_j0',) + tuple((f'overflow_j{j}' for j in range(1, 7)))
    _c59_candidate04_setup_NEW_TURN_UNITS50 = tuple(_c59_candidate04_setup_BOUND['new_generic_turn_units50'])
    assert len(_c59_candidate04_setup_NEW_TURN_UNITS50) == len(_c59_candidate04_setup_COEFFICIENTS37) == len(_c59_candidate04_setup_SITES) == 34
    assert all((type(v) is int for v in _c59_candidate04_setup_NEW_TURN_UNITS50))
    assert all(_c59_candidate04_setup_BOUND['delta_turn_units64']), 'The literal34-change structural comparison requires all34 nonzero deltas.'
    assert [r['site'] for r in _c59_candidate04_setup_BOUND['angle_sites']] == list(_c59_candidate04_setup_SITES)
    _c59_candidate04_setup_ORIGINAL_ENDPOINT = _c59_candidate04_setup_divider.phase_endpoint
    _c59_candidate04_setup_LAST_PROXY_RECORDS = []
    _c59_candidate04_setup__INSTALLED = False

    def _c59_candidate04_setup_angle_class(half_turns):
        angle = _c59_candidate04_setup_Fraction(half_turns)
        if (2 * angle).denominator == 1:
            return 'Clifford'
        if (4 * angle).denominator == 1:
            return 'T'
        return 'generic'

    def _c59_candidate04_setup_checked_quantized():
        """Require the full exact scan; the conservative bound alone cannot emit."""
        path = _c59_candidate04_setup_RESEARCH / 'quantize50.json'
        raw = _read_bytes(path)
        result = _json_loads(raw)
        assert result['status'] == 'EXACT_ALL_INPUT_QUANTIZE50_PAPER_PASS_NATIVE_PENDING'
        pass
        pass
        assert result['inputs'] == 3133452 and result['original_tolerance_unchanged']
        assert result['accuracy_decision_uses_only_integer_arithmetic']
        assert result['new_generic_turn_units50'] == list(_c59_candidate04_setup_NEW_TURN_UNITS50)
        assert result['delta_turn_units64'] == _c59_candidate04_setup_BOUND['delta_turn_units64']
        assert result['new_generic_turn_units64'] == _c59_candidate04_setup_BOUND['new_generic_turn_units64']
        assert result['maximum_generic_turn_denominator'] == 1 << 50
        assert result['all_angle_classes_exactly_generic']
        assert result['fixed_T'] == 4 and result['fixed_R'] == 34 and (result['Q'] == 49)
        assert result['expected_Toffolis'] == 1562.5
        stats = result['exact_statistics']['quantized50']
        assert stats['inputs'] == 3133452 and stats['failures'] == 0
        assert stats['minimum_margin_units'] >= _c59_candidate04_setup_ACCEPTED['proved_margin_lower_bound_units64']
        assert result['sum_absolute_angle_quantization_change_units'] == 110274
        assert result['rotation_charge'] <= _c59_candidate04_setup_ACCEPTED['rotation_charge_upper_bound'] + 1e-12
        assert result['predicted_complete_cost'] <= _c59_candidate04_setup_ACCEPTED['complete_cost_upper_bound'] + 1e-09
        assert len(result['angle_sites']) == 34
        for site, old, new, row in zip(_c59_candidate04_setup_SITES, _c59_candidate04_setup_COEFFICIENTS37, _c59_candidate04_setup_NEW_TURN_UNITS50, result['angle_sites']):
            assert row['site'] == site and row['turn_units50'] == new
            assert _c59_candidate04_setup_Fraction(row['half_turns']) == _c59_candidate04_setup_Fraction(2 * new, 1 << 50)
            assert _c59_candidate04_setup_angle_class(_c59_candidate04_setup_Fraction(2 * old, 1 << 37)) == _c59_candidate04_setup_angle_class(_c59_candidate04_setup_Fraction(2 * new, 1 << 50)) == 'generic'
        return (result, _c59_candidate04_setup_hashlib.sha256(raw).hexdigest())

    def _c59_candidate04_setup_variant_gate():
        _c59_candidate04_setup_verify_inputs()
        result = _c59_candidate04_setup_copy.deepcopy(_c59_candidate04_setup_previous.variant_gate())
        quantized, digest = _c59_candidate04_setup_checked_quantized()
        primary = result['primary']
        primary['rotation_charge'] = quantized['rotation_charge']
        primary['complete_components']['rotation_charge'] = quantized['rotation_charge']
        primary['total_E'] = quantized['predicted_complete_E']
        primary['paper_cost'] = quantized['predicted_complete_cost']
        primary['quantized_exact_minimum_margin_units64'] = quantized['exact_statistics']['quantized50']['minimum_margin_units']
        primary['proved_margin_lower_bound_units64'] = _c59_candidate04_setup_ACCEPTED['proved_margin_lower_bound_units64']
        primary['phase_grid_turns'] = '1/1125899906842624'
        primary['margins'] = {name: limit - primary['paper_cost'] for name, limit in [('stage97', 92278.95), ('target', 89987), ('stretch', 82740)]}
        assert primary['Toffolis_expected'] == 1562.5 and primary['T'] == 4 and (primary['R'] == 34) and (primary['Q'] == 49)
        assert _c59_candidate04_setup_math.isclose(primary['total_E'], 1562.5 + 1 + primary['rotation_charge'], rel_tol=0, abs_tol=1e-10)
        result['status'] = 'ACCEPTED_CANDIDATE04_FULL_DOMAIN_QUANTIZED_ANGLE_GATE_NATIVE_PENDING'
        result['candidate04_quantize50_sha256'] = digest
        return result

    class _c59_candidate04_setup_AngleProxy:
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
            old = _c59_candidate04_setup_Fraction(half_turns)
            kind = _c59_candidate04_setup_angle_class(old)
            if kind == 'generic':
                index = self.generic
                assert index < 34, ('unexpected_generic_rotation', index, str(old))
                expected = _c59_candidate04_setup_Fraction(2 * _c59_candidate04_setup_COEFFICIENTS37[index], 1 << 37)
                assert old == expected, (_c59_candidate04_setup_SITES[index], str(old), str(expected))
                new = _c59_candidate04_setup_Fraction(2 * _c59_candidate04_setup_NEW_TURN_UNITS50[index], 1 << 50)
                assert _c59_candidate04_setup_angle_class(new) == 'generic'
                self.records.append(dict(index=index, site=_c59_candidate04_setup_SITES[index], target=str(target), old_half_turns=str(old), new_half_turns=str(new)))
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

    def _c59_candidate04_setup_phase_endpoint(builder, token):
        proxy = _c59_candidate04_setup_AngleProxy(builder)
        result = _c59_candidate04_setup_ORIGINAL_ENDPOINT(proxy, token)
        _c59_candidate04_setup_LAST_PROXY_RECORDS.clear()
        _c59_candidate04_setup_LAST_PROXY_RECORDS.extend(proxy.finish())
        return result

    def _c59_candidate04_setup_install():
        global _c59_candidate04_setup__INSTALLED
        _c59_candidate04_setup_variant_gate()
        if not _c59_candidate04_setup__INSTALLED:
            _c59_candidate04_setup_previous.install()
            assert _c59_candidate04_setup_divider.phase_endpoint is _c59_candidate04_setup_ORIGINAL_ENDPOINT, 'Unexpected pre-existing endpoint replacement.'
            _c59_candidate04_setup_divider.phase_endpoint = _c59_candidate04_setup_phase_endpoint
            _c59_candidate04_setup__INSTALLED = True
        return _c59_candidate04_setup_divider

    def _c59_candidate04_setup_load_baseline(name):
        return _c59_candidate04_setup_previous.load_baseline(name)

# work/c10/narrow/native/candidate05/variant.py
def _initialize__c60_candidate05_setup():
    global _c60_candidate05_setup_ACCEPTED, _c60_candidate05_setup_BASE, _c60_candidate05_setup_BOUND, _c60_candidate05_setup_COEFFICIENTS37, _c60_candidate05_setup_HERE, _c60_candidate05_setup_INPUTS, _c60_candidate05_setup_INTEGRATED_ROOT, _c60_candidate05_setup_NARROW, _c60_candidate05_setup_NEW_CENTRES, _c60_candidate05_setup_NEW_TURN_UNITS50, _c60_candidate05_setup_OLD_CENTRES, _c60_candidate05_setup_ORIGINAL_ROUTE, _c60_candidate05_setup_ORIGINAL_SLOTS, _c60_candidate05_setup_PREVIOUS, _c60_candidate05_setup_Path, _c60_candidate05_setup_ROUTE_TRACE, _c60_candidate05_setup_SITES, _c60_candidate05_setup__INSTALLED, _c60_candidate05_setup__IntegratedPath, _c60_candidate05_setup___file__, _c60_candidate05_setup___name__, _c60_candidate05_setup_checked_quantized, _c60_candidate05_setup_common, _c60_candidate05_setup_copy, _c60_candidate05_setup_divider, _c60_candidate05_setup_hashlib, _c60_candidate05_setup_importlib, _c60_candidate05_setup_install, _c60_candidate05_setup_json, _c60_candidate05_setup_load_baseline, _c60_candidate05_setup_operation_count, _c60_candidate05_setup_previous, _c60_candidate05_setup_proof50_module, _c60_candidate05_setup_route, _c60_candidate05_setup_spec, _c60_candidate05_setup_sys, _c60_candidate05_setup_variant_gate, _c60_candidate05_setup_verify_inputs
    'Isolated candidate05; pinned04 angles and exactly one route omission.'
    _c60_candidate05_setup__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate05/variant.py', False).Path
    _c60_candidate05_setup_INTEGRATED_ROOT = _c60_candidate05_setup__IntegratedPath(_c60_candidate05_setup___file__).resolve().parents[5]
    _c60_candidate05_setup_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate05/variant.py', False).Path
    _c60_candidate05_setup_copy = _import_component('copy', 'work/c10/narrow/native/candidate05/variant.py', True)
    _c60_candidate05_setup_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate05/variant.py', True)
    _c60_candidate05_setup_importlib = _import_component('importlib.util', 'work/c10/narrow/native/candidate05/variant.py', True)
    _c60_candidate05_setup_json = _import_component('json', 'work/c10/narrow/native/candidate05/variant.py', True)
    _c60_candidate05_setup_sys = _import_component('sys', 'work/c10/narrow/native/candidate05/variant.py', True)
    _c60_candidate05_setup_HERE = _c60_candidate05_setup_Path(_c60_candidate05_setup___file__).resolve().parent
    _c60_candidate05_setup_NARROW = _c60_candidate05_setup_HERE.parents[1]
    _c60_candidate05_setup_PREVIOUS = _c60_candidate05_setup_HERE.parent / 'candidate04'
    _c60_candidate05_setup_BASE = _c60_candidate05_setup_HERE.parent / 'candidate01'
    _c60_candidate05_setup_INPUTS = _json_loads(_read_text(_c60_candidate05_setup_HERE / 'INPUTS.json'))

    def _c60_candidate05_setup_verify_inputs():
        """Source integrity is verified by the integrated manifest before execution."""
        pass
    _c60_candidate05_setup_verify_inputs()
    _c60_candidate05_setup_spec = _spec('candidate05_pinned_candidate04_variant', _c60_candidate05_setup_PREVIOUS / 'variant.py')
    _c60_candidate05_setup_previous = _new_module(_c60_candidate05_setup_spec)
    _c60_candidate05_setup_sys.modules[_c60_candidate05_setup_spec.name] = _c60_candidate05_setup_previous
    _c60_candidate05_setup_spec.loader.exec_module(_c60_candidate05_setup_previous)
    _c60_candidate05_setup_common = _c60_candidate05_setup_previous.common
    _c60_candidate05_setup_divider = _c60_candidate05_setup_previous.divider
    _c60_candidate05_setup_BOUND = _c60_candidate05_setup_previous.BOUND
    _c60_candidate05_setup_COEFFICIENTS37 = _c60_candidate05_setup_previous.COEFFICIENTS37
    _c60_candidate05_setup_NEW_TURN_UNITS50 = _c60_candidate05_setup_previous.NEW_TURN_UNITS50
    _c60_candidate05_setup_SITES = _c60_candidate05_setup_previous.SITES
    _c60_candidate05_setup_ACCEPTED = _c60_candidate05_setup_common.checked_json(_c60_candidate05_setup_NARROW / 'PAPER_GATE_RECEIPT_016_VARIANT.json', '141d51af466cea914cc9c318e09c34558b7c23c6247fbf5e87c9ea9f1efa7cbe')
    assert _c60_candidate05_setup_ACCEPTED['native_build_authorized'] and _c60_candidate05_setup_ACCEPTED['all_native_candidates_preserved'] == [1, 2, 3, 4]
    _c60_candidate05_setup_NEW_CENTRES = tuple(_c60_candidate05_setup_ACCEPTED['centres'])
    _c60_candidate05_setup_OLD_CENTRES = tuple(_c60_candidate05_setup_divider.CENTRES)
    assert _c60_candidate05_setup_NEW_CENTRES == (-1, -3, -7, -1, -2) and _c60_candidate05_setup_OLD_CENTRES == (0, -2, -6, 0, -1)
    _c60_candidate05_setup_ORIGINAL_ROUTE = _c60_candidate05_setup_divider._route
    _c60_candidate05_setup_ORIGINAL_SLOTS = _c60_candidate05_setup_divider._slots()
    _c60_candidate05_setup_ROUTE_TRACE = []
    _c60_candidate05_setup__INSTALLED = False

    def _c60_candidate05_setup_checked_quantized():
        result, digest = _c60_candidate05_setup_previous.checked_quantized()
        pass
        assert result['exact_statistics']['quantized50']['minimum_margin_units'] == 124372027
        assert result['rotation_charge'] == _c60_candidate05_setup_ACCEPTED['rotation_charge']
        return (result, digest)

    def _c60_candidate05_setup_variant_gate():
        _c60_candidate05_setup_verify_inputs()
        result = _c60_candidate05_setup_copy.deepcopy(_c60_candidate05_setup_previous.variant_gate())
        quantized, digest = _c60_candidate05_setup_checked_quantized()
        proof = _json_loads(_read_text(_c60_candidate05_setup_PREVIOUS / 'whole_native_text_all.json'))
        assert proof['whole_official_domain'] and proof['proved_inputs'] == 3133452 and proof['every_HMR_transcript_proved']
        pass
        pass
        assert sum(_c60_candidate05_setup_ACCEPTED['Toffoli_components'].values()) == 1560.5
        p = result['primary']
        p['Toffolis_expected'] = 1560.5
        p['phase']['Toffolis'] = 144
        assert p['complete_components']['phase_direct'] == 147
        p['complete_components']['phase_direct'] = 145
        p['total_E'] = _c60_candidate05_setup_ACCEPTED['complete_predicted_E']
        p['paper_cost'] = _c60_candidate05_setup_ACCEPTED['complete_predicted_cost']
        p['rotation_charge'] = _c60_candidate05_setup_ACCEPTED['rotation_charge']
        p['complete_components']['rotation_charge'] = _c60_candidate05_setup_ACCEPTED['rotation_charge']
        p['quantized_exact_minimum_margin_units64'] = 124372027
        p['margins'] = {name: limit - p['paper_cost'] for name, limit in [('stage97', 92278.95), ('target', 89987), ('stretch', 82740)]}
        assert p['Q'] == 49 and p['T'] == 4 and (p['R'] == 34)
        assert p['first_loader_peak'] == p['second_loader_peak'] == 49
        result['status'] = 'ACCEPTED_CANDIDATE05_ROUTE_ONLY_GATE_NATIVE_PENDING'
        result['candidate05_exact_Toffoli_components'] = _c60_candidate05_setup_ACCEPTED['Toffoli_components']
        return result

    def _c60_candidate05_setup_operation_count(builder):
        Program = _import_component('branch_prover', 'work/c10/narrow/native/candidate05/variant.py', False).Program
        generated_text = _import_component('branch_prover', 'work/c10/narrow/native/candidate05/variant.py', False).generated_text
        return len(Program(generated_text(builder.finish_circuit())).operations)

    def _c60_candidate05_setup_route(builder, word, variables, inverse=False):
        """Existing five affine controls; translated matchings; one identity skip."""
        assert len(word) == 27 and tuple(_c60_candidate05_setup_divider.CENTRES) == _c60_candidate05_setup_NEW_CENTRES
        start = _c60_candidate05_setup_operation_count(builder)
        stages = list(range(5))
        if inverse:
            stages.reverse()
        old_gates = []
        new_gates = []
        omissions = []
        for stage in stages:
            with _c60_candidate05_setup_divider._affine_control(builder, variables, _c60_candidate05_setup_divider.CONTROLS[stage]) as control:
                for i in range(27):
                    k = (_c60_candidate05_setup_OLD_CENTRES[stage] - i) % 27
                    if i < k:
                        old_gates.append([str(control), str(word[i]), str(word[k])])
                for i in range(27):
                    k = (_c60_candidate05_setup_NEW_CENTRES[stage] - i) % 27
                    if i >= k:
                        continue
                    if (stage, i, k) == (0, 0, 26):
                        omissions.append(dict(stage=stage, positions=[i, k], control=str(control), owners=[str(word[i]), str(word[k])]))
                        continue
                    builder.cswap(control, word[i], word[k])
                    new_gates.append([str(control), str(word[i]), str(word[k])])
        stop = _c60_candidate05_setup_operation_count(builder)
        assert len(old_gates) == 65 and len(new_gates) == 64 and (len(omissions) == 1)
        _c60_candidate05_setup_ROUTE_TRACE.append(dict(inverse=inverse, start=start, stop=stop, old_cswap_arguments=old_gates, new_cswap_arguments=new_gates, omissions=omissions))

    def _c60_candidate05_setup_install():
        global _c60_candidate05_setup__INSTALLED
        _c60_candidate05_setup_variant_gate()
        if not _c60_candidate05_setup__INSTALLED:
            _c60_candidate05_setup_previous.install()
            assert _c60_candidate05_setup_divider._route is _c60_candidate05_setup_ORIGINAL_ROUTE
            _c60_candidate05_setup_divider.CENTRES = _c60_candidate05_setup_NEW_CENTRES
            _c60_candidate05_setup_divider._route = _c60_candidate05_setup_route
            assert _c60_candidate05_setup_divider._slots() == _c60_candidate05_setup_ORIGINAL_SLOTS, 'Common centre offset unexpectedly changed phase sites.'
            _c60_candidate05_setup__INSTALLED = True
        return _c60_candidate05_setup_divider

    def _c60_candidate05_setup_load_baseline(name):
        return _c60_candidate05_setup_previous.load_baseline(name)

    def _c60_candidate05_setup_proof50_module():
        """Load frozen04 proof helpers/oracle; this variant supplies its own main."""
        name = 'candidate05_pinned_candidate04_proof50'
        if name not in _c60_candidate05_setup_sys.modules:
            _c60_candidate05_setup_sys.path.insert(0, str(_c60_candidate05_setup_PREVIOUS))
            spec = _spec(name, _c60_candidate05_setup_PREVIOUS / 'prove50.py')
            module = _new_module(spec)
            _c60_candidate05_setup_sys.modules[name] = module
            spec.loader.exec_module(module)
        module = _c60_candidate05_setup_sys.modules[name]
        assert module.variant is _c60_candidate05_setup_sys.modules['variant'] and module.MODULUS == 1 << 50
        return module

# work/c10/narrow/native/candidate06/decoder06.py
def _initialize__c61_decoder06():
    global _c61_decoder06_CERT, _c61_decoder06_EARLY_TABLE_DEBT, _c61_decoder06_INTEGRATED_ROOT, _c61_decoder06_MISSING, _c61_decoder06_NARROW, _c61_decoder06_RESOURCES, _c61_decoder06__BASE, _c61_decoder06__IntegratedPath, _c61_decoder06___file__, _c61_decoder06___name__, _c61_decoder06_cb, _c61_decoder06_checked_json, _c61_decoder06_decode_root, _c61_decoder06_km, _c61_decoder06_plan_from_json
    'Restore five root values; only a6 retains a direct HMR phase outcome.'
    _c61_decoder06__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate06/decoder06.py', False).Path
    _c61_decoder06_INTEGRATED_ROOT = _c61_decoder06__IntegratedPath(_c61_decoder06___file__).resolve().parents[5]
    _c61_decoder06_km = _import_component('common', 'work/c10/narrow/native/candidate06/decoder06.py', False).km
    _c61_decoder06_cb = _import_component('common', 'work/c10/narrow/native/candidate06/decoder06.py', False).cb
    _c61_decoder06_NARROW = _import_component('common', 'work/c10/narrow/native/candidate06/decoder06.py', False).NARROW
    _c61_decoder06_checked_json = _import_component('common', 'work/c10/narrow/native/candidate06/decoder06.py', False).checked_json
    _c61_decoder06_plan_from_json = _import_component('common', 'work/c10/narrow/native/candidate06/decoder06.py', False).plan_from_json
    _c61_decoder06__BASE = _import_component('tables06', 'work/c10/narrow/native/candidate06/decoder06.py', False)._BASE
    _c61_decoder06_CERT = _c61_decoder06_checked_json(_c61_decoder06_NARROW / 'research/quantized_producer/framed_retained5_best21_snapshot.json', '3b6fa7059bee77bb9abe6c7395cd8ff2f2899843523188c60d513e6c5d381def')
    _c61_decoder06_MISSING = (0, 1, 2, 4, 6)
    _c61_decoder06_EARLY_TABLE_DEBT = (0, 1, 2, 4)
    _c61_decoder06_RESOURCES = dict(Toffolis=21, T=0, R=0, new_value_owners=5, complete_peak=44, deferred_table_phase_indices=list(_c61_decoder06_EARLY_TABLE_DEBT), direct_phase_indices=[6])

    def _c61_decoder06_decode_root(builder, v, A, H, retired_outcomes):
        """Return v with all five values restored and its R frame still active.

    Keys0,1,2,4 MUST map to None: their exact mixed signs are owned by the
    table ledger, not by a direct raw-bit outcome. Key6 MUST be the actual
    late HMR bit. This function creates no placeholder classical bits.
    """
        v = list(v)
        A = list(A)
        H = list(H)
        assert len(v) == 12 and len(A) == 13 and (len(H) == 5)
        assert all((v[5 + i] is None for i in _c61_decoder06_MISSING))
        assert set(retired_outcomes) == set(_c61_decoder06_MISSING)
        assert all((retired_outcomes[i] is None for i in _c61_decoder06_EARLY_TABLE_DEBT))
        assert isinstance(retired_outcomes[6], _c61_decoder06_km.b)
        assert isinstance(v[8], _c61_decoder06_km.q) and isinstance(v[10], _c61_decoder06_km.q)
        features = [v[8]] + A + H + [v[10]]
        outputs = []
        count = 0
        for record in _c61_decoder06_CERT['plans']:
            plan = _c61_decoder06_plan_from_json(record['plan'])
            assert plan.width == len(features)
            q = builder.alloc_qubits(1)[0]
            _c61_decoder06_cb.emit_xor(builder, features, q, plan)
            outputs.append(q)
            features.append(q)
            count += plan.and_count
        assert count == 21 and len(outputs) == 5
        rows = [_c61_decoder06_CERT['raw_five_from_code'][str(i)] for i in _c61_decoder06_MISSING]
        for kind, i, j in _c61_decoder06__BASE._row_matrix_inverse_operations(rows, len(outputs)):
            if kind == 'cx':
                builder.cx(outputs[i], outputs[j])
            else:
                builder.swap(outputs[i], outputs[j])
        for i, q in zip(_c61_decoder06_MISSING, outputs):
            v[5 + i] = q
            outcome = retired_outcomes[i]
            if outcome is not None:
                assert i == 6
                builder.push_condition(outcome)
                builder.z(q)
                builder.pop_condition()
                builder.free(outcome)
        return v

# work/c10/narrow/native/candidate06/divider_cleanup06.py
def _initialize__c62_divider_cleanup06():
    global _c62_divider_cleanup06_BASE, _c62_divider_cleanup06_BASE_DIVIDER_SHA, _c62_divider_cleanup06_COMPONENT_CONTRACT, _c62_divider_cleanup06_HERE, _c62_divider_cleanup06_INTEGRATED_ROOT, _c62_divider_cleanup06_NARROW, _c62_divider_cleanup06_Path, _c62_divider_cleanup06__IntegratedPath, _c62_divider_cleanup06___file__, _c62_divider_cleanup06___name__, _c62_divider_cleanup06__divider, _c62_divider_cleanup06_bind, _c62_divider_cleanup06_cleanup_divider, _c62_divider_cleanup06_hashlib, _c62_divider_cleanup06_install
    'Isolated Q48 inverse divider with exact disposable feed-carry callbacks.'
    _c62_divider_cleanup06__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate06/divider_cleanup06.py', False).Path
    _c62_divider_cleanup06_INTEGRATED_ROOT = _c62_divider_cleanup06__IntegratedPath(_c62_divider_cleanup06___file__).resolve().parents[5]
    _c62_divider_cleanup06_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate06/divider_cleanup06.py', False).Path
    _c62_divider_cleanup06_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate06/divider_cleanup06.py', True)
    _c62_divider_cleanup06_HERE = _c62_divider_cleanup06_Path(_c62_divider_cleanup06___file__).resolve().parent
    _c62_divider_cleanup06_NARROW = _c62_divider_cleanup06_HERE.parents[1]
    _c62_divider_cleanup06_BASE = _c62_divider_cleanup06_HERE.parent / 'candidate01'
    _c62_divider_cleanup06_BASE_DIVIDER_SHA = 'd0dbaf6fe4227da988c9cb9e9dee847624992c7c5cce7ab347990d5b0a116c05'
    pass
    _c62_divider_cleanup06__divider = None

    def _c62_divider_cleanup06_bind(divider_module):
        """Bind the parent's pinned divider, without installing any hook itself."""
        global _c62_divider_cleanup06__divider
        pass
        pass
        required = ('_feed_carry', '_feed_erase', '_frame', '_leading_offset', '_dirty', 'inverse_add', 'cleanup_u12')
        assert all((callable(getattr(divider_module, name, None)) for name in required))
        if _c62_divider_cleanup06__divider is not None:
            assert _c62_divider_cleanup06__divider is divider_module
        _c62_divider_cleanup06__divider = divider_module
        return _c62_divider_cleanup06_cleanup_divider

    def _c62_divider_cleanup06_install(divider_module):
        """Replace only this process's inverse hook on the supplied divider."""
        divider_module.cleanup_divider = _c62_divider_cleanup06_bind(divider_module)
        return divider_module

    def _c62_divider_cleanup06_cleanup_divider(builder, token):
        """Reverse all24 rows, repay every phase, then return current P15 owners."""
        assert _c62_divider_cleanup06__divider is not None, 'Parent must bind the pinned divider before use.'
        d = _c62_divider_cleanup06__divider
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
    _c62_divider_cleanup06_COMPONENT_CONTRACT = dict(Q=48, divider_core_E=587.5, feed_conditional_regeneration_E=6.5, disposable_feed_rows=tuple(range(12, 25)), paired_debts=24, entry_live_owners=43, returned_current_product_owners=15, final_live_owners=31, initialization='Parent retains candidate02 triangular u12 initializer and original exact cleanup.')

# work/c10/narrow/native/candidate06/lifecycle06.py
def _initialize__c63_lifecycle06():
    global _c63_lifecycle06_ACCEPTED, _c63_lifecycle06_BASE, _c63_lifecycle06_BASE_SHA, _c63_lifecycle06_COMMON_SHA, _c63_lifecycle06_COMPONENT_CONTRACT, _c63_lifecycle06_CUT_HOOK, _c63_lifecycle06_HERE, _c63_lifecycle06_INTEGRATED_ROOT, _c63_lifecycle06_NARROW, _c63_lifecycle06_PAPER, _c63_lifecycle06_Path, _c63_lifecycle06__IntegratedPath, _c63_lifecycle06___file__, _c63_lifecycle06___name__, _c63_lifecycle06__mark, _c63_lifecycle06__module, _c63_lifecycle06__name, _c63_lifecycle06__spec, _c63_lifecycle06_baseline, _c63_lifecycle06_common, _c63_lifecycle06_emit_body, _c63_lifecycle06_hashlib, _c63_lifecycle06_importlib, _c63_lifecycle06_km, _c63_lifecycle06_product_inverse, _c63_lifecycle06_sys
    "Q48 lifecycle with framed input retirement and owned carry disposal.\n\nAll unchanged arithmetic comes from the hash-pinned candidate01 module.\nThis module owns only its isolated emit_body and product inverse. It never\nmodifies a previous source or the previous lifecycle module's functions.\n"
    _c63_lifecycle06__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate06/lifecycle06.py', False).Path
    _c63_lifecycle06_INTEGRATED_ROOT = _c63_lifecycle06__IntegratedPath(_c63_lifecycle06___file__).resolve().parents[5]
    _c63_lifecycle06_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate06/lifecycle06.py', False).Path
    _c63_lifecycle06_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate06/lifecycle06.py', True)
    _c63_lifecycle06_importlib = _import_component('importlib.util', 'work/c10/narrow/native/candidate06/lifecycle06.py', True)
    _c63_lifecycle06_sys = _import_component('sys', 'work/c10/narrow/native/candidate06/lifecycle06.py', True)
    _c63_lifecycle06_HERE = _c63_lifecycle06_Path(_c63_lifecycle06___file__).resolve().parent
    _c63_lifecycle06_NARROW = _c63_lifecycle06_HERE.parents[1]
    _c63_lifecycle06_BASE = _c63_lifecycle06_HERE.parent / 'candidate01'
    _c63_lifecycle06_BASE_SHA = '47b73f1f24ea027eedcbd1950cde7fc2535b32afeeb2e366ebdc4b6f1eb3c068'
    _c63_lifecycle06_COMMON_SHA = '9872e64213a4219522a87efc49d1aa549a04e43ae3fb51c9d5b762b1ea6535ab'
    pass
    pass
    _c63_lifecycle06_sys.path.insert(0, str(_c63_lifecycle06_BASE))
    _c63_lifecycle06_common = _import_component('common', 'work/c10/narrow/native/candidate06/lifecycle06.py', True)
    _c63_lifecycle06_ACCEPTED = _c63_lifecycle06_common.checked_json(_c63_lifecycle06_NARROW / 'PAPER_GATE_RECEIPT_018_VARIANT.json', '99ef9a891d4e99b262b1a452ea48b18c536e91e7017f018b77bc37f1793ccffd')
    assert _c63_lifecycle06_ACCEPTED['native_build_authorized'] and _c63_lifecycle06_ACCEPTED['Q'] == 48
    _c63_lifecycle06_PAPER = _c63_lifecycle06_common.checked_json(_c63_lifecycle06_NARROW / _c63_lifecycle06_ACCEPTED['paper_gate_path'], _c63_lifecycle06_ACCEPTED['paper_gate_sha256'])
    assert _c63_lifecycle06_PAPER['full_lifecycle_E'] == 563 and _c63_lifecycle06_PAPER['expected_Toffolis'] == 1591
    _c63_lifecycle06__name = 'candidate06_pinned_candidate01_lifecycle'
    if _c63_lifecycle06__name not in _c63_lifecycle06_sys.modules:
        _c63_lifecycle06__spec = _spec(_c63_lifecycle06__name, _c63_lifecycle06_BASE / 'lifecycle.py')
        _c63_lifecycle06__module = _new_module(_c63_lifecycle06__spec)
        _c63_lifecycle06_sys.modules[_c63_lifecycle06__name] = _c63_lifecycle06__module
        _c63_lifecycle06__spec.loader.exec_module(_c63_lifecycle06__module)
    _c63_lifecycle06_baseline = _c63_lifecycle06_sys.modules[_c63_lifecycle06__name]
    _c63_lifecycle06_km = _c63_lifecycle06_common.km
    _c63_lifecycle06_CUT_HOOK = None

    def _c63_lifecycle06__mark(builder, trace, label, expected, owners=None):
        live = builder.num_allocated_qubits
        assert live == expected, (label, live, expected)
        assert live <= 48, (label, live)
        if trace is not None:
            trace.append(dict(label=label, live_owners=live))
        if _c63_lifecycle06_CUT_HOOK is not None:
            _c63_lifecycle06_CUT_HOOK(label, builder, {} if owners is None else {key: list(value) for key, value in owners.items()})

    def _c63_lifecycle06_product_inverse(builder, D, word, token, dirty):
        """Pay all ten paired debts; dispose only the eight owned input carries."""
        assert builder.max_qubits == 48 and builder.num_allocated_qubits == 44
        assert len(D) == 13 and len(word) == 16 and (len(token.rows) == 10)
        assert all((not debt.consumed for debt in token.rows))
        word = list(word)
        C = [False] + list(D)
        builder.x(word[15])
        for i in reversed(range(10)):
            q = word[6 + i]
            target = word[:6 + i]
            source = C[9 - i:] if i < 9 else C
            for t in target:
                builder.cx(q, t)
            carry = _c63_lifecycle06_baseline._product_carry(builder, C, q, i)
            if i < 8:
                assert isinstance(carry, _c63_lifecycle06_km.q) and carry != q
                lifecycle = (lambda value: _c63_lifecycle06_baseline._clear_product_carry(builder, C, q, i, value), lambda: _c63_lifecycle06_baseline._product_carry(builder, C, q, i))
            else:
                if i == 8:
                    assert carry is False
                else:
                    assert carry == q
                lifecycle = None
            released_input = _c63_lifecycle06_baseline.product_ar.inverse_add(builder, source, target, token.rows[i], carry_in=carry, dirty_wires=dirty + word[6:], carry_lifecycle=lifecycle)
            if i < 8:
                assert released_input, 'The pinned Q48 owned-carry partition must release its input.'
            else:
                assert not released_input, 'False/aliased product carries cannot be disposed.'
            if not released_input:
                _c63_lifecycle06_baseline._clear_product_carry(builder, C, q, i, carry)
            for t in target:
                builder.cx(q, t)
            assert token.rows[i].consumed and (not token.rows[i].measurements)
            assert builder.num_allocated_qubits == 44
        builder.x(word[15])
        assert all((debt.consumed and (not debt.measurements) for debt in token.rows))
        return (word[:6], word[6:])

    def _c63_lifecycle06_emit_body(builder, v12, h10, flags4, table_module, divider_module, decode_root_callback, *, trace=None):
        """Compute phase and restore current(v12,h10), with no stale root handles.

    table_module.load_joint16 retains its old call shape. Its second variant
    expects the R frame already active and consumes address slots0/1/2/4.
    decode_root_callback accepts None for their already-owned table signs;
    the later raw-a6 HMR is the only separate direct root phase correction.
    """
        assert builder.max_qubits == 48
        v = list(v12)
        h = list(h10)
        flags = list(flags4)
        assert (len(v), len(h), len(flags)) == (12, 10, 4)
        assert len(set(v + h + flags)) == 26
        _c63_lifecycle06__mark(builder, trace, 'body_entry', 26, dict(v=v, h=h, flags=flags))
        table_debts = table_module.TableDebts()
        truths = table_module.model_truths()
        D, Hlow = table_module.load_joint16(builder, v[5:], variant='first', debts=table_debts)
        D = list(D)
        H = list(Hlow)
        _c63_lifecycle06__mark(builder, trace, 'first_table', 42, dict(v=v, h=h, flags=flags, D=D, H=H))
        H.append(_c63_lifecycle06_baseline.prepare_H3_initial(builder, v, D, H))
        _c63_lifecycle06_baseline.root_R_frame(builder, v)
        H.append(_c63_lifecycle06_baseline.prepare_H4(builder, D, H[3]))
        first = _c63_lifecycle06_baseline.coefficient_forward(builder, v, D, H)
        _c63_lifecycle06__mark(builder, trace, 'first_coefficient', 45, dict(v=v, h=h, flags=flags, D=D, H=H, snapshot=[first.saved_bit]))
        Hlow = _c63_lifecycle06_baseline.erase_high_H(builder, v, D, H)
        for i, q in enumerate(Hlow):
            table_debts.erase(builder, q, truths['H'][i], free=True)
        first_snapshot = _c63_lifecycle06_baseline.ar.release_saved_bit(builder, first.saved_bit)
        first.saved_bit = None
        _c63_lifecycle06_baseline.root_R_frame(builder, v, inverse=True)
        _c63_lifecycle06__mark(builder, trace, 'first_metadata_retired', 39)
        seed, seed_token = _c63_lifecycle06_baseline.seed_forward(builder, v, D)
        _c63_lifecycle06__mark(builder, trace, 'seed_ready', 45, dict(v=v, h=h, flags=flags, D=D, seed=seed))
        word, product_token = _c63_lifecycle06_baseline.product_forward(builder, D, seed, h)
        builder.x(word[15])
        builder.cx(word[14], word[15])
        builder.free(word[15])
        P = word[:15]
        _c63_lifecycle06__mark(builder, trace, 'signed_product15', 44, dict(v=v, P=P, flags=flags, D=D))
        first_D = []
        for q in D:
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            builder.free(q)
            first_D.append(m)
        _c63_lifecycle06__mark(builder, trace, 'coefficient_retired_for_divider', 31, dict(v=v, P=P, flags=flags))
        P = list(divider_module.compute_phase_cleanup(builder, v, P, flags))
        assert len(P) == 15 and len(set(v + P + flags)) == 31
        _c63_lifecycle06__mark(builder, trace, 'divider_return', 31, dict(v=v, P=P, flags=flags))
        _c63_lifecycle06_baseline.root_R_frame(builder, v)
        D, Hlow = table_module.load_joint16(builder, v[5:], variant='second', debts=table_debts)
        D = list(D)
        H = list(Hlow)
        retired = {a: None for a in (0, 1, 2, 4)}
        for a in retired:
            v[5 + a] = None
        assert all((v[5 + a] is None for a in (0, 1, 2, 4)))
        assert v[8] is not None and v[10] is not None and (v[11] is not None)
        _c63_lifecycle06__mark(builder, trace, 'second_table', 43, dict(v=v, P=P, flags=flags, D=D, H=H))
        _c63_lifecycle06_baseline.ar.repay_saved_bit(builder, D[6], first_snapshot)
        H.append(_c63_lifecycle06_baseline.prepare_H3_initial(builder, v, D, H))
        _c63_lifecycle06__mark(builder, trace, 'second_H3_ready', 44, dict(v=v, P=P, flags=flags, D=D, H=H))
        q = v[11]
        m = builder.alloc_bits(1)[0]
        builder.hmr(q, m)
        builder.free(q)
        v[11] = None
        retired[6] = m
        assert set(retired) == {0, 1, 2, 4, 6} and all((retired[a] is None for a in (0, 1, 2, 4)))
        _c63_lifecycle06__mark(builder, trace, 'second_a6_retired', 43, dict(v=v, P=P, flags=flags, D=D, H=H))
        H.append(_c63_lifecycle06_baseline.prepare_H4(builder, D, H[3]))
        second = _c63_lifecycle06_baseline.coefficient_forward(builder, v, D, H)
        _c63_lifecycle06__mark(builder, trace, 'second_coefficient', 45, dict(v=v, P=P, flags=flags, D=D, H=H, snapshot=[second.saved_bit]))
        for q, m in zip(D, first_D):
            builder.push_condition(m)
            builder.z(q)
            builder.pop_condition()
            builder.free(m)
        _c63_lifecycle06_baseline.merge_coefficient_transcripts(builder, first, second)
        Hlow = _c63_lifecycle06_baseline.erase_high_H(builder, v, D, H)
        _c63_lifecycle06__mark(builder, trace, 'second_metadata_retired', 43)
        high = builder.alloc_qubits(1)[0]
        builder.cx(P[14], high)
        builder.x(high)
        word = P + [high]
        _c63_lifecycle06__mark(builder, trace, 'inverse_product_data', 44, dict(v=v, word=word, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
        dirty = [q for q in v if q is not None] + flags + Hlow + [second.saved_bit]
        seed, h = _c63_lifecycle06_product_inverse(builder, D, word, product_token, dirty)
        _c63_lifecycle06_baseline.seed_cleanup(builder, v, D, seed, seed_token)
        _c63_lifecycle06__mark(builder, trace, 'seed_cleared', 38, dict(v=v, h=h, flags=flags, D=D, H=Hlow, snapshot=[second.saved_bit]))
        H = list(Hlow)
        H.append(_c63_lifecycle06_baseline.prepare_H3_current(builder, v, D, H))
        H.append(_c63_lifecycle06_baseline.prepare_H4(builder, D, H[3]))
        _c63_lifecycle06__mark(builder, trace, 'coefficient_sources_restored', 40)
        _c63_lifecycle06_baseline.coefficient_inverse(builder, v, D, H, second, [q for q in v if q is not None] + flags + h)
        _c63_lifecycle06__mark(builder, trace, 'A_restored', 39, dict(v=v, h=h, flags=flags, A=D, H=H))
        v = list(decode_root_callback(builder, v, D, H, retired))
        assert all((q is not None for q in v)) and len(set(v + h + flags)) == 26
        _c63_lifecycle06_baseline.root_R_frame(builder, v, inverse=True)
        _c63_lifecycle06__mark(builder, trace, 'raw_root_restored', 44, dict(v=v, h=h, flags=flags, A=D, H=H))
        Hlow = _c63_lifecycle06_baseline.erase_high_H(builder, v, D, H, initial=True)
        table_module.cleanup_joint16(builder, v[5:], D, Hlow, table_debts)
        assert not table_debts.pending
        assert first.saved_bit is None and second.saved_bit is None
        for token in (first, second):
            assert all((debt.consumed and (not debt.measurements) for debt in token.row_debts))
            assert token.overflow_debt.consumed and (not token.overflow_debt.measurements)
        assert all((debt.consumed and (not debt.measurements) for debt in product_token.rows))
        _c63_lifecycle06__mark(builder, trace, 'body_return', 26, dict(v=v, h=h, flags=flags))
        return (v, h)
    _c63_lifecycle06_COMPONENT_CONTRACT = dict(Q=48, lifecycle_E=563, product_forward_E=103, product_inverse_E=137.5, product_conditional_regeneration_E=4, coefficient_E=123, seed_E=17.5, metadata_E=7, root_frames_E=4, root_decoder_E=21, table_loaders_E=141, table_cleanup_E=9, retired_to_table_only=(0, 1, 2, 4), retired_direct_Z=(6,), final_live_owners=26)
    assert sum((_c63_lifecycle06_COMPONENT_CONTRACT[k] for k in ('product_forward_E', 'product_inverse_E', 'coefficient_E', 'seed_E', 'metadata_E', 'root_frames_E', 'root_decoder_E', 'table_loaders_E', 'table_cleanup_E'))) == 563

# work/c10/narrow/native/candidate06/phase06.py
def _initialize__c64_phase06():
    global _c64_phase06_BINDING, _c64_phase06_Fraction, _c64_phase06_HERE, _c64_phase06_INTEGRATED_ROOT, _c64_phase06_LAST_PHASE_TRACE, _c64_phase06_LAST_PROXY_RECORDS, _c64_phase06_NARROW, _c64_phase06_Path, _c64_phase06_SOURCE_PINS, _c64_phase06_SimpleNamespace, _c64_phase06__IntegratedPath, _c64_phase06___file__, _c64_phase06___name__, _c64_phase06_compact_terms, _c64_phase06_contextmanager, _c64_phase06_hashlib, _c64_phase06_install, _c64_phase06_json, _c64_phase06_phase_endpoint, _c64_phase06_raw_phase_endpoint, _c64_phase06_threshold, _c64_phase06_verify_source_pins
    'Explicitly bound compact Q48 endpoint; unchanged pinned04 phase angles.'
    _c64_phase06__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate06/phase06.py', False).Path
    _c64_phase06_INTEGRATED_ROOT = _c64_phase06__IntegratedPath(_c64_phase06___file__).resolve().parents[5]
    _c64_phase06_contextmanager = _import_component('contextlib', 'work/c10/narrow/native/candidate06/phase06.py', False).contextmanager
    _c64_phase06_Fraction = _import_component('fractions', 'work/c10/narrow/native/candidate06/phase06.py', False).Fraction
    _c64_phase06_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate06/phase06.py', False).Path
    _c64_phase06_SimpleNamespace = _import_component('types', 'work/c10/narrow/native/candidate06/phase06.py', False).SimpleNamespace
    _c64_phase06_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate06/phase06.py', True)
    _c64_phase06_json = _import_component('json', 'work/c10/narrow/native/candidate06/phase06.py', True)
    _c64_phase06_HERE = _c64_phase06_Path(_c64_phase06___file__).resolve().parent
    _c64_phase06_NARROW = _c64_phase06_HERE.parents[1]
    _c64_phase06_SOURCE_PINS = {'PAPER_GATE_RECEIPT_018_VARIANT.json': '99ef9a891d4e99b262b1a452ea48b18c536e91e7017f018b77bc37f1793ccffd', 'native/candidate05/variant.py': 'dc522e0881a15e7fbe99190df36d2bdbfd2b7c5438c3cd18f25d6537fecd5935', 'native/candidate04/variant.py': 'da023f7bc56995b9a8764a35c25b782f579b46e5a663e5b7100690819513e7ce', 'native/candidate01/divider.py': 'd0dbaf6fe4227da988c9cb9e9dee847624992c7c5cce7ab347990d5b0a116c05', 'research/postgate_angle_refit/quantize50.json': '8670515091475959ab0edeae03cb736cdb1cb66cd7768366e69fafb7eff8bf72', 'research/postgate_route_constants/offsets.json': '14f887ede91c2630fd3eca8386a7ac8b55a4951087bbdec009f1e1aee3414a99', 'research/stream_phase/alias_ring/phase_ledger.py': 'e8cc5a9095fd4bf29b5e77c6b58382b54ea46918102dbc10d1cad7c1edb255c3', 'research/stream_phase/alias_ring/phase_ledger.json': '88bd82007c9ce6413d0c9aa8dae65184c1322f7025e9a23c0f57534f31dc63ec', 'checkpoint002/cleanroom/baseline_stage97/engine/quadratic_terms.py': '3cf00a5af4227daee8c7d93102bc04ec4c2f25da3662e140069494d6f93f63ef', 'checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py': 'ee2619af8e8d9ef09230d1c29a73e5ca13112d6295dd13b1e9e6c03cc83316b8'}
    _c64_phase06_BINDING = None
    _c64_phase06_LAST_PROXY_RECORDS = []
    _c64_phase06_LAST_PHASE_TRACE = []

    def _c64_phase06_verify_source_pins():
        gate = _json_loads(_read_text(_c64_phase06_NARROW / 'PAPER_GATE_RECEIPT_018_VARIANT.json'))
        assert gate['native_build_authorized'] and gate['Q'] == 48 and (gate['expected_Toffolis'] == 1591)
        assert gate['T'] == 4 and gate['R'] == 34 and (gate['exact_margin_units64'] == 124372027)
        pass
        return gate

    def _c64_phase06_compact_terms(original_terms):
        """Substitute c=f1*f3 before compilation AND before HMR phase repayment."""
        terms = tuple((10 if term == 32 else term for term in original_terms))
        assert all((0 <= term < 32 and term.bit_count() <= 2 for term in terms))
        return terms

    @_c64_phase06_contextmanager
    def _c64_phase06_threshold(builder, variables, t):
        assert _c64_phase06_BINDING is not None and len(variables) == 5
        d = _c64_phase06_BINDING.divider
        terms = _c64_phase06_compact_terms(d.THRESHOLDS[t])
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

    def _c64_phase06_raw_phase_endpoint(builder, token):
        """145 Toffolis,4T,34R at48 owners; raw angles are the old37-unit ones."""
        assert _c64_phase06_BINDING is not None
        d = _c64_phase06_BINDING.divider
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
        assert d._route is _c64_phase06_BINDING.previous05.route and tuple(d.CENTRES) == (-1, -3, -7, -1, -2)
        d._route(builder, word, variables)
        slots = [word[i] for i in d._slots()]
        factor = 1 << 27
        for i, q in enumerate(slots):
            units = (1 << i) + (factor if i == 0 else 0)
            builder.z_pow(q, _c64_phase06_Fraction(2 * units, 1 << 37))
        for j in range(10):
            angle = _c64_phase06_Fraction(factor * (1 << j), 1 << 37)
            if j == 0:
                with _c64_phase06_threshold(builder, variables, 1) as q:
                    builder.x(q)
                    builder.z_pow(q, -2 * angle)
                    builder.x(q)
            elif j == 9:
                assert angle == _c64_phase06_Fraction(1, 2)
                builder.cz(flags[1], flags[3])
            else:
                with _c64_phase06_threshold(builder, variables, j + 1) as q:
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

    def _c64_phase06_phase_endpoint(builder, token):
        assert _c64_phase06_BINDING is not None
        proxy = _c64_phase06_BINDING.Proxy(builder)
        _c64_phase06_raw_phase_endpoint(proxy, token)
        _c64_phase06_LAST_PROXY_RECORDS.clear()
        _c64_phase06_LAST_PROXY_RECORDS.extend(proxy.finish())
        _c64_phase06_LAST_PHASE_TRACE.clear()
        _c64_phase06_LAST_PHASE_TRACE.extend(proxy.allocations)
        _c64_phase06_LAST_PHASE_TRACE.append(dict(event='complete', entry_owners=43, exit_owners=builder.num_allocated_qubits, observed_peak_owners=proxy.peak, generic_calls=proxy.generic, T_calls=proxy.T, direct_Clifford_Z_POW_calls=proxy.Clifford, last_overflow_implemented_as='CZ(flags1,flags3)', retained_controls=['p'], expected_Toffolis=145))

    def _c64_phase06_install(previous05):
        """Bind only after the parent has installed the pinned candidate05 module."""
        global _c64_phase06_BINDING
        _c64_phase06_verify_source_pins()
        pass
        previous05.verify_inputs()
        previous05.checked_quantized()
        d = previous05.divider
        prior04 = previous05.previous
        assert d._route is previous05.route and tuple(d.CENTRES) == (-1, -3, -7, -1, -2)
        assert d._slots() == previous05.ORIGINAL_SLOTS
        if _c64_phase06_BINDING is not None:
            assert _c64_phase06_BINDING.previous05 is previous05 and d.phase_endpoint is _c64_phase06_phase_endpoint
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
        _c64_phase06_BINDING = _c64_phase06_SimpleNamespace(previous05=previous05, divider=d, Proxy=CompactAngleProxy)
        d.phase_endpoint = _c64_phase06_phase_endpoint
        return d

# work/c10/narrow/native/candidate06/tables06.py
def _initialize__c65_tables06():
    global _c65_tables06_BASE_PATH, _c65_tables06_BASE_SHA, _c65_tables06_FROZEN, _c65_tables06_HERE, _c65_tables06_INTEGRATED_ROOT, _c65_tables06_MODEL_SHA, _c65_tables06_NARROW, _c65_tables06_PINS, _c65_tables06_Path, _c65_tables06_RESOURCES, _c65_tables06_SECOND_RETIRED_ADDRESS_SLOTS, _c65_tables06_TableDebt, _c65_tables06_TableDebts, _c65_tables06__BASE, _c65_tables06__IntegratedPath, _c65_tables06___file__, _c65_tables06___name__, _c65_tables06__spec, _c65_tables06_array, _c65_tables06_cb, _c65_tables06_certificate, _c65_tables06_checked_json, _c65_tables06_cleanup_joint16, _c65_tables06_emit_affine_frame, _c65_tables06_hashlib, _c65_tables06_importlib, _c65_tables06_km, _c65_tables06_load_joint16, _c65_tables06_lru_cache, _c65_tables06_model_truths, _c65_tables06_model_values, _c65_tables06_plan_from_json, _c65_tables06_sys
    'Isolated Q48 first61/framed-second80 coefficient table adapters.\n\nThe second loader consumes four existing address owners as mutable work.\nEvery discarded value retains its exact original-raw-address phase function.\nThe caller must mark those four logical root slots absent immediately.\n'
    _c65_tables06__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate06/tables06.py', False).Path
    _c65_tables06_INTEGRATED_ROOT = _c65_tables06__IntegratedPath(_c65_tables06___file__).resolve().parents[5]
    _c65_tables06_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate06/tables06.py', False).Path
    _c65_tables06_lru_cache = _import_component('functools', 'work/c10/narrow/native/candidate06/tables06.py', False).lru_cache
    _c65_tables06_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate06/tables06.py', True)
    _c65_tables06_importlib = _import_component('importlib.util', 'work/c10/narrow/native/candidate06/tables06.py', True)
    _c65_tables06_sys = _import_component('sys', 'work/c10/narrow/native/candidate06/tables06.py', True)
    _c65_tables06_km = _import_component('common', 'work/c10/narrow/native/candidate06/tables06.py', False).km
    _c65_tables06_cb = _import_component('common', 'work/c10/narrow/native/candidate06/tables06.py', False).cb
    _c65_tables06_NARROW = _import_component('common', 'work/c10/narrow/native/candidate06/tables06.py', False).NARROW
    _c65_tables06_MODEL_SHA = _import_component('common', 'work/c10/narrow/native/candidate06/tables06.py', False).MODEL_SHA
    _c65_tables06_checked_json = _import_component('common', 'work/c10/narrow/native/candidate06/tables06.py', False).checked_json
    _c65_tables06_plan_from_json = _import_component('common', 'work/c10/narrow/native/candidate06/tables06.py', False).plan_from_json
    _c65_tables06_array = _import_component('common', 'work/c10/narrow/native/candidate06/tables06.py', False).array
    _c65_tables06_HERE = _c65_tables06_Path(_c65_tables06___file__).resolve().parent
    _c65_tables06_BASE_PATH = _c65_tables06_HERE.parent / 'candidate01/tables.py'
    _c65_tables06_BASE_SHA = 'cf2c83b6db5d1b1e2a63f4fe6e84976192a49eabb74e370ee2376fc4300659d3'
    pass
    _c65_tables06__spec = _spec('_candidate06_pinned_tables01', _c65_tables06_BASE_PATH)
    _c65_tables06__BASE = _new_module(_c65_tables06__spec)
    _c65_tables06_sys.modules[_c65_tables06__spec.name] = _c65_tables06__BASE
    _c65_tables06__spec.loader.exec_module(_c65_tables06__BASE)
    _c65_tables06_TableDebt = _c65_tables06__BASE.TableDebt
    _c65_tables06_TableDebts = _c65_tables06__BASE.TableDebts
    _c65_tables06_model_values = _c65_tables06__BASE.model_values
    _c65_tables06_model_truths = _c65_tables06__BASE.model_truths
    _c65_tables06_cleanup_joint16 = _c65_tables06__BASE.cleanup_joint16
    _c65_tables06_FROZEN = _c65_tables06_NARROW / 'research/joint_loader/frozen'
    _c65_tables06_PINS = {'first': ('loader16_first61_Q48.json', '4857688e595af50828d7bedf0bc745eaaed8d10767e2e6ca6f77802887e1ad48'), 'second': ('loader16_second80_framed_Q48.json', 'e4f007d322caae5c77b3d61c61d73fb239126e67a488238ece442b1f51d8a805')}
    _c65_tables06_SECOND_RETIRED_ADDRESS_SLOTS = (0, 1, 2, 4)
    _c65_tables06_RESOURCES = {'first': dict(Toffolis=61, T=0, R=0, other_fixed_owners=26, work_cap=22, existing_input_work=0, new_zero_owners=22, complete_peak=48, return_owners=42, HMR_debts=45), 'second': dict(Toffolis=80, T=0, R=0, other_fixed_owners=27, work_cap=21, existing_input_work=4, new_zero_owners=17, complete_peak=48, return_owners=43, HMR_debts=64), 'cleanup': dict(Toffolis=9, T=0, R=0, complete_peak=44)}

    @_c65_tables06_lru_cache(maxsize=2)
    def _c65_tables06_certificate(which):
        name, digest = _c65_tables06_PINS[which]
        data = _c65_tables06_checked_json(_c65_tables06_FROZEN / name, digest)
        pass
        assert data['status'] == 'COMPLETE_MATHEMATICAL_LOADER_NOT_NATIVE'
        assert data['Toffolis'] == _c65_tables06_RESOURCES[which]['Toffolis']
        assert data['work_cap'] == data['work_peak'] == _c65_tables06_RESOURCES[which]['work_cap']
        assert data['complete_peak'] == 48
        return data

    def _c65_tables06_emit_affine_frame(builder, fixed, work, rows):
        """Invertible work frame with offset8(raw7) or4(fixed R,a5,a6)."""
        fixed = list(fixed)
        work = list(work)
        rows = list(map(int, rows))
        if len(fixed) not in (3, 7):
            raise ValueError('Unexpected fixed-address chart width.')
        offset = 1 + len(fixed)
        for kind, a, b in _c65_tables06__BASE._row_matrix_inverse_operations([row >> offset for row in rows], len(work)):
            if kind == 'cx':
                builder.cx(work[a], work[b])
            else:
                _c65_tables06__BASE._swap(builder, work[a], work[b])
        for target, row in zip(work, rows):
            if row & 1:
                builder.x(target)
            for bit in range(len(fixed)):
                if row >> 1 + bit & 1:
                    builder.cx(fixed[bit], target)

    def _c65_tables06_load_joint16(builder, address7, *, variant, debts):
        """Return current(A13,Hlow3); the second address is ALREADY R-framed.

    First: preserve raw address7, allocate22 zero owners, return16 outputs.
    Second: keep slots3,5,6=(R,rawa5,rawa6); reuse slots0,1,2,4 in workcap21
    and allocate only17 zeros. Those four old logical inputs are consumed:
    the caller sets v[5],v[6],v[7],v[9] to None before using v again.
    The shared TableDebts ledger owns all mixed/input/helper HMR outcomes.
    """
        if variant not in ('first', 'second'):
            raise ValueError('Unknown Q48 loader variant.')
        address = list(address7)
        if len(address) != 7 or len(set(address)) != 7 or (not all((isinstance(q, _c65_tables06_km.q) for q in address))):
            raise ValueError('Expected seven current, distinct quantum address owners.')
        if not isinstance(debts, _c65_tables06_TableDebts):
            raise TypeError('Expected the shared pinned TableDebts owner.')
        data = _c65_tables06_certificate(variant)
        entry = builder.num_allocated_qubits
        before_debts = debts.total_recorded
        fixed_slots = (0, 1, 2, 3, 4, 5, 6) if variant == 'first' else (3, 5, 6)
        reusable_slots = () if variant == 'first' else _c65_tables06_SECOND_RETIRED_ADDRESS_SLOTS
        assert data['fixed_address_slots'] == list(fixed_slots)
        assert data['reusable_input_slots'] == list(reusable_slots)
        fixed = [address[i] for i in fixed_slots]
        work = [address[i] for i in reusable_slots]
        cap = data['work_cap']
        available = list(builder.alloc_qubits(cap - len(work)))
        assert len(available) == _c65_tables06_RESOURCES[variant]['new_zero_owners']
        offset = 1 + len(fixed)
        count = 0
        for item in data['steps']:
            kind = item['kind']
            if kind in ('bank', 'CCX_new_coordinate'):
                target = available.pop(0)
                plan = _c65_tables06_plan_from_json(item['plan'])
                _c65_tables06_cb.emit_xor(builder, fixed + work, target, plan)
                work.append(target)
                count += plan.and_count
            elif kind == 'Clifford_zero_dependent_coordinate':
                index = item['index']
                target = work[index]
                _c65_tables06__BASE._affine_xor(builder, fixed, work[:index], target, item['expression'])
                work.pop(index)
                available.append(target)
            elif kind == 'Clifford_frame_then_HMR':
                assert item['affine_fixed_offset'] == offset
                _c65_tables06_emit_affine_frame(builder, fixed, work, item['full_affine_rows'])
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
                plan = _c65_tables06_plan_from_json(item['plan'])
                _c65_tables06_cb.emit_xor(builder, fixed + work[1:], work[0], plan)
                count += plan.and_count
            elif kind == 'final_output_Clifford_frame':
                _c65_tables06_emit_affine_frame(builder, fixed, work, [int(row) << offset for row in item['matrix_rows']])
            else:
                raise AssertionError(('Unknown frozen Q48 loader operation', kind))
            assert len(work) + len(available) == cap and len(set(work + available)) == cap
            assert not set(fixed) & set(work + available)
        assert len(work) == 16 and count == _c65_tables06_RESOURCES[variant]['Toffolis']
        assert debts.total_recorded - before_debts == _c65_tables06_RESOURCES[variant]['HMR_debts']
        if available:
            builder.free(_c65_tables06_array(available))
        assert builder.num_allocated_qubits == entry + 16 - len(reusable_slots)
        return (list(work[:13]), list(work[13:]))

# work/c10/narrow/native/candidate06/variant.py
def _initialize__c66_candidate06_setup():
    global _c66_candidate06_setup_ACCEPTED, _c66_candidate06_setup_BASE, _c66_candidate06_setup_BOUND, _c66_candidate06_setup_COEFFICIENTS37, _c66_candidate06_setup_GATE_PATH, _c66_candidate06_setup_GATE_SHA, _c66_candidate06_setup_HERE, _c66_candidate06_setup_INTEGRATED_ROOT, _c66_candidate06_setup_MODULES, _c66_candidate06_setup_NARROW, _c66_candidate06_setup_NEW_TURN_UNITS50, _c66_candidate06_setup_PAPER, _c66_candidate06_setup_PAPER_SHA, _c66_candidate06_setup_PREVIOUS, _c66_candidate06_setup_Path, _c66_candidate06_setup_SITES, _c66_candidate06_setup__INSTALLED, _c66_candidate06_setup__IntegratedPath, _c66_candidate06_setup___file__, _c66_candidate06_setup___name__, _c66_candidate06_setup_checked_quantized, _c66_candidate06_setup_common, _c66_candidate06_setup_divider, _c66_candidate06_setup_hashlib, _c66_candidate06_setup_importlib, _c66_candidate06_setup_install, _c66_candidate06_setup_json, _c66_candidate06_setup_key, _c66_candidate06_setup_load_baseline, _c66_candidate06_setup_local_module, _c66_candidate06_setup_os, _c66_candidate06_setup_previous, _c66_candidate06_setup_proof50_module, _c66_candidate06_setup_spec, _c66_candidate06_setup_sys, _c66_candidate06_setup_variant_gate, _c66_candidate06_setup_verify_inputs
    'Isolated, paper-authorized Q48 composition on immutable native sources.'
    _c66_candidate06_setup__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate06/variant.py', False).Path
    _c66_candidate06_setup_INTEGRATED_ROOT = _c66_candidate06_setup__IntegratedPath(_c66_candidate06_setup___file__).resolve().parents[5]
    _c66_candidate06_setup_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate06/variant.py', False).Path
    _c66_candidate06_setup_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate06/variant.py', True)
    _c66_candidate06_setup_importlib = _import_component('importlib.util', 'work/c10/narrow/native/candidate06/variant.py', True)
    _c66_candidate06_setup_json = _import_component('json', 'work/c10/narrow/native/candidate06/variant.py', True)
    _c66_candidate06_setup_os = _import_component('os', 'work/c10/narrow/native/candidate06/variant.py', True)
    _c66_candidate06_setup_sys = _import_component('sys', 'work/c10/narrow/native/candidate06/variant.py', True)
    for _c66_candidate06_setup_key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        _c66_candidate06_setup_os.environ[_c66_candidate06_setup_key] = '1'
    _c66_candidate06_setup_HERE = _c66_candidate06_setup_Path(_c66_candidate06_setup___file__).resolve().parent
    _c66_candidate06_setup_NARROW = _c66_candidate06_setup_HERE.parents[1]
    _c66_candidate06_setup_BASE = _c66_candidate06_setup_HERE.parent / 'candidate01'
    _c66_candidate06_setup_PREVIOUS = _c66_candidate06_setup_HERE.parent / 'candidate05'
    _c66_candidate06_setup_GATE_PATH = _c66_candidate06_setup_NARROW / 'PAPER_GATE_RECEIPT_018_VARIANT.json'
    _c66_candidate06_setup_GATE_SHA = '99ef9a891d4e99b262b1a452ea48b18c536e91e7017f018b77bc37f1793ccffd'
    _c66_candidate06_setup_PAPER_SHA = '912da9164095aa996317909903d50162a76eded7ff9a90cbb9299c85c013de2c'

    def _c66_candidate06_setup_verify_inputs():
        """Source integrity is verified by the integrated manifest before execution."""
        pass
    _c66_candidate06_setup_verify_inputs()
    _c66_candidate06_setup_spec = _spec('candidate06_pinned_candidate05_variant', _c66_candidate06_setup_PREVIOUS / 'variant.py')
    _c66_candidate06_setup_previous = _new_module(_c66_candidate06_setup_spec)
    _c66_candidate06_setup_sys.modules[_c66_candidate06_setup_spec.name] = _c66_candidate06_setup_previous
    _c66_candidate06_setup_spec.loader.exec_module(_c66_candidate06_setup_previous)
    _c66_candidate06_setup_common = _c66_candidate06_setup_previous.common
    _c66_candidate06_setup_divider = _c66_candidate06_setup_previous.divider
    _c66_candidate06_setup_BOUND = _c66_candidate06_setup_previous.BOUND
    _c66_candidate06_setup_COEFFICIENTS37 = _c66_candidate06_setup_previous.COEFFICIENTS37
    _c66_candidate06_setup_NEW_TURN_UNITS50 = _c66_candidate06_setup_previous.NEW_TURN_UNITS50
    _c66_candidate06_setup_SITES = _c66_candidate06_setup_previous.SITES
    _c66_candidate06_setup_ACCEPTED = _c66_candidate06_setup_common.checked_json(_c66_candidate06_setup_GATE_PATH, _c66_candidate06_setup_GATE_SHA)
    _c66_candidate06_setup_PAPER = _c66_candidate06_setup_common.checked_json(_c66_candidate06_setup_NARROW / _c66_candidate06_setup_ACCEPTED['paper_gate_path'], _c66_candidate06_setup_PAPER_SHA)
    assert _c66_candidate06_setup_ACCEPTED['native_build_authorized'] and _c66_candidate06_setup_ACCEPTED['all_native_candidates_preserved'] == [1, 2, 3, 4, 5]
    _c66_candidate06_setup__INSTALLED = False
    _c66_candidate06_setup_MODULES = {}

    def _c66_candidate06_setup_checked_quantized():
        result, digest = _c66_candidate06_setup_previous.checked_quantized()
        assert result['exact_statistics']['quantized50']['minimum_margin_units'] == 124372027
        assert result['new_generic_turn_units50'] == list(_c66_candidate06_setup_NEW_TURN_UNITS50)
        return (result, digest)

    def _c66_candidate06_setup_variant_gate():
        _c66_candidate06_setup_verify_inputs()
        quantized, digest = _c66_candidate06_setup_checked_quantized()
        assert _c66_candidate06_setup_PAPER['Q'] == 48 and _c66_candidate06_setup_PAPER['expected_Toffolis'] == 1591
        assert _c66_candidate06_setup_PAPER['T'] == 4 and _c66_candidate06_setup_PAPER['R'] == 34
        assert sum(_c66_candidate06_setup_PAPER['components_expected_Toffolis'].values()) == 1591
        assert max((row['live'] for row in _c66_candidate06_setup_PAPER['owner_cuts'])) == 48
        assert _c66_candidate06_setup_PAPER['rotation_charge'] == quantized['rotation_charge']
        assert _c66_candidate06_setup_PAPER['unchanged_original_tolerance'] and _c66_candidate06_setup_PAPER['unchanged_exact_integer50_phase_model']
        return dict(status='ACCEPTED_COMPLETE_Q48_GATE_NATIVE_PROOF_REQUIRED', Q=48, Toffolis_expected=1591, T=4, R=34, rotation_charge=_c66_candidate06_setup_PAPER['rotation_charge'], total_E=_c66_candidate06_setup_PAPER['total_E'], paper_cost=_c66_candidate06_setup_PAPER['complete_expected_cost'], complete_components=_c66_candidate06_setup_PAPER['components_expected_Toffolis'], first_loader_peak=48, second_loader_peak=48, quantized_exact_minimum_margin_units64=124372027, quantize50_sha256=digest)

    def _c66_candidate06_setup_local_module(name):
        if name not in _c66_candidate06_setup_MODULES:
            path = _c66_candidate06_setup_HERE / (name + '.py')
            if name in _c66_candidate06_setup_sys.modules:
                module = _c66_candidate06_setup_sys.modules[name]
                pass
            else:
                spec = _spec('candidate06_' + name, path)
                module = _new_module(spec)
                _c66_candidate06_setup_sys.modules[spec.name] = module
                _c66_candidate06_setup_sys.modules[name] = module
                spec.loader.exec_module(module)
            _c66_candidate06_setup_MODULES[name] = module
        return _c66_candidate06_setup_MODULES[name]

    def _c66_candidate06_setup_install():
        global _c66_candidate06_setup__INSTALLED
        _c66_candidate06_setup_variant_gate()
        if not _c66_candidate06_setup__INSTALLED:
            _c66_candidate06_setup_previous.install()
            _c66_candidate06_setup_local_module('divider_cleanup06').install(_c66_candidate06_setup_divider)
            _c66_candidate06_setup_local_module('phase06').install(_c66_candidate06_setup_previous)
            _c66_candidate06_setup__INSTALLED = True
        return _c66_candidate06_setup_divider

    def _c66_candidate06_setup_load_baseline(name):
        return _c66_candidate06_setup_previous.load_baseline(name)

    def _c66_candidate06_setup_proof50_module():
        return _c66_candidate06_setup_previous.proof50_module()

# work/c10/narrow/native/candidate07/phase07.py
def _initialize__c67_phase07():
    global _c67_phase07_BINDING, _c67_phase07_CENTRES, _c67_phase07_Fraction, _c67_phase07_HERE, _c67_phase07_INTEGRATED_ROOT, _c67_phase07_LAST_ANGLE_RECORDS, _c67_phase07_LAST_PHASE_TRACE, _c67_phase07_MODULUS, _c67_phase07_NARROW, _c67_phase07_PINS, _c67_phase07_Path, _c67_phase07_ROUTE_TRACE, _c67_phase07_Recorder, _c67_phase07_SITES, _c67_phase07_SimpleNamespace, _c67_phase07__IntegratedPath, _c67_phase07___file__, _c67_phase07___name__, _c67_phase07_angle_class, _c67_phase07_hashlib, _c67_phase07_install, _c67_phase07_json, _c67_phase07_phase_endpoint, _c67_phase07_raw_phase_endpoint, _c67_phase07_route26, _c67_phase07_verify_sources
    'Authorized26-ring endpoint, explicit new angles and complete local cleanup.'
    _c67_phase07__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate07/phase07.py', False).Path
    _c67_phase07_INTEGRATED_ROOT = _c67_phase07__IntegratedPath(_c67_phase07___file__).resolve().parents[5]
    _c67_phase07_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate07/phase07.py', False).Path
    _c67_phase07_Fraction = _import_component('fractions', 'work/c10/narrow/native/candidate07/phase07.py', False).Fraction
    _c67_phase07_SimpleNamespace = _import_component('types', 'work/c10/narrow/native/candidate07/phase07.py', False).SimpleNamespace
    _c67_phase07_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate07/phase07.py', True)
    _c67_phase07_json = _import_component('json', 'work/c10/narrow/native/candidate07/phase07.py', True)
    _c67_phase07_HERE = _c67_phase07_Path(_c67_phase07___file__).resolve().parent
    _c67_phase07_NARROW = _c67_phase07_HERE.parents[1]
    _c67_phase07_MODULUS = 1 << 50
    _c67_phase07_CENTRES = (0, -2, -6, 0, -1)
    _c67_phase07_SITES = tuple((f'base_i{i}' for i in range(26))) + tuple((f'overflow_j{j}' for j in range(7))) + ('global_one',)
    _c67_phase07_PINS = {'PAPER_GATE_RECEIPT_022_VARIANT.json': 'f8cfe4331b37a5184a4aab17ee85b4ac892c08c2cfb863fc4b1c1b3c9978262e', 'research/combined_q48_ring26/COMPLETE_GATE.json': '49ce6e7007b19abcd533b82a9f291b617cbc1c864a3d66287c0e63a87ebb82c4', 'research/ring26_phase/COMPLETE_GATE_RING26_ZERO33.json': 'b579924175ee8e73c61c2f945b2d85e8ba2e536a8dbd8288a8332628142cd569', 'research/ring26_phase/frozen/global_zero33.json': 'c0eab1edd234e32d5baa1a51a0fec46abf82165d3973ffda825d2149f67f11e5', 'research/ring26_phase/basis.json': 'a3bacdd5ef8e16acb8560a40e60e2c998f8171973b1dcc062a47503c5218d744', 'native/candidate01/divider.py': 'd0dbaf6fe4227da988c9cb9e9dee847624992c7c5cce7ab347990d5b0a116c05', 'native/candidate06/phase06.py': '4e979c47bc90317a6ac3576bc74964cf74222c2006e1630f6b17075af51ccdfb'}
    _c67_phase07_BINDING = None
    _c67_phase07_LAST_ANGLE_RECORDS = []
    _c67_phase07_LAST_PHASE_TRACE = []
    _c67_phase07_ROUTE_TRACE = []

    def _c67_phase07_verify_sources():
        accepted = _json_loads(_read_text(_c67_phase07_NARROW / 'PAPER_GATE_RECEIPT_022_VARIANT.json'))
        assert accepted['native_build_authorized'] and (accepted['Q'], accepted['expected_Toffolis'], accepted['T'], accepted['R']) == (48, 1584, 4, 33)
        return _json_loads(_read_text(_c67_phase07_NARROW / 'research/ring26_phase/basis.json'))

    def _c67_phase07_angle_class(half_turns):
        angle = _c67_phase07_Fraction(half_turns)
        if angle % _c67_phase07_Fraction(1, 2) == 0:
            return 'Clifford'
        if angle % _c67_phase07_Fraction(1, 4) == 0:
            return 'T'
        return 'generic'

    class _c67_phase07_Recorder:

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
            value = _c67_phase07_Fraction(half_turns)
            kind = _c67_phase07_angle_class(value)
            if kind == 'generic':
                assert self.site is not None and self.fixed is None
                i = self.site
                assert i == len(self.records) and i < 33
                assert value == _c67_phase07_Fraction(2 * _c67_phase07_BINDING.angles[i], _c67_phase07_MODULUS)
                self.records.append(dict(index=i, site=_c67_phase07_SITES[i], target=str(target), new_half_turns=str(value), turn_units50=_c67_phase07_BINDING.angles[i], angle_class=kind, emitted=True))
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

    def _c67_phase07_route26(builder, word, variables, inverse=False):
        """Original centres modulo26, no candidate05 omitted pair."""
        d = _c67_phase07_BINDING.divider
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
                    j = (_c67_phase07_CENTRES[stage] - i) % 26
                    if i < j:
                        builder.cswap(control, word[i], word[j])
                        count += 1
                        gates.append(dict(stage=stage, positions=[i, j], arguments=list(map(str, (control, word[i], word[j])))))
            counts.append(dict(stage=stage, swaps=count))
        assert len(gates) == 61 and sorted(((row['stage'], row['swaps']) for row in counts)) == [(0, 12), (1, 12), (2, 12), (3, 12), (4, 13)]
        _c67_phase07_ROUTE_TRACE.append(dict(inverse=inverse, ring_bits=26, centres=list(_c67_phase07_CENTRES), omissions=[], swap_count=61, stages=counts, gates=gates))

    def _c67_phase07_raw_phase_endpoint(builder, token):
        d = _c67_phase07_BINDING.divider
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
        _c67_phase07_route26(builder, word, variables)
        slots = [word[i] for i in _c67_phase07_BINDING.slots]
        for i, q in enumerate(slots):
            builder.site = i
            builder.z_pow(q, _c67_phase07_Fraction(2 * _c67_phase07_BINDING.angles[i], _c67_phase07_MODULUS))
            builder.site = None
        for j in range(10):
            if j == 9:
                builder.fixed = 'overflow_j9'
                builder.z_pow(c, _c67_phase07_Fraction(1))
                builder.fixed = None
            elif j <= 6:
                with d._threshold(builder, variables, j + 1) as control:
                    builder.site = 26 + j
                    d._feature(builder, control, slots[j], _c67_phase07_Fraction(_c67_phase07_BINDING.angles[26 + j], _c67_phase07_MODULUS))
                    builder.site = None
            else:
                with d._threshold(builder, variables, j + 1) as control:
                    builder.fixed = f'overflow_j{j}'
                    d._feature(builder, control, slots[j], _c67_phase07_Fraction(1, 8) if j == 7 else _c67_phase07_Fraction(1, 4))
                    builder.fixed = None
        _c67_phase07_route26(builder, word, variables, inverse=True)
        assert _c67_phase07_BINDING.angles[33] == 0 and len(builder.records) == 33
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

    def _c67_phase07_phase_endpoint(builder, token):
        assert _c67_phase07_BINDING is not None
        proxy = _c67_phase07_Recorder(builder)
        _c67_phase07_ROUTE_TRACE.clear()
        _c67_phase07_raw_phase_endpoint(proxy, token)
        _c67_phase07_LAST_ANGLE_RECORDS.clear()
        _c67_phase07_LAST_ANGLE_RECORDS.extend(proxy.finish())
        _c67_phase07_LAST_PHASE_TRACE.clear()
        _c67_phase07_LAST_PHASE_TRACE.extend(proxy.allocations)
        _c67_phase07_LAST_PHASE_TRACE.append(dict(event='complete', entry_owners=43, exit_owners=builder.num_allocated_qubits, observed_peak_owners=proxy.peak, generic_calls=proxy.generic, T_calls=proxy.T, direct_Clifford_Z_POW_calls=proxy.Clifford, global_identity_validated_and_omitted=True, expected_Toffolis=139, local_HMR_functions=15, all_local_outcomes_repaid_before_exit=True, no_TableDebts_transfer=True, fixed_phase_records=proxy.fixed_records))

    def _c67_phase07_install(previous06, accepted_angles, accepted_phase_gate):
        global _c67_phase07_BINDING
        basis = _c67_phase07_verify_sources()
        angles = tuple(accepted_angles)
        pass
        previous06.verify_inputs()
        d = previous06.divider
        assert list(angles) == accepted_phase_gate['new_angles_turn_units50']
        assert accepted_phase_gate['phase_expected_Toffolis'] == 139 and accepted_phase_gate['endpoint_peak'] == 48
        assert accepted_phase_gate['R'] == 33 and accepted_phase_gate['T'] == 4 and (accepted_phase_gate['phase_entry_exit_owners'] == 43)
        assert tuple(accepted_phase_gate['phase_site_order']) == _c67_phase07_SITES and len(angles) == 34 and (angles[-1] == 0)
        assert all((_c67_phase07_angle_class(_c67_phase07_Fraction(2 * a, _c67_phase07_MODULUS)) == 'generic' for a in angles[:33]))
        assert any((a & 1 for a in angles[:33]))
        if _c67_phase07_BINDING is not None:
            assert _c67_phase07_BINDING.previous06 is previous06 and _c67_phase07_BINDING.angles == angles and (d.phase_endpoint is _c67_phase07_phase_endpoint)
            return d
        assert d.phase_endpoint is previous06.local_module('phase06').phase_endpoint
        assert tuple((tuple(x) for x in basis['controls'])) == tuple(d.CONTROLS)
        _c67_phase07_BINDING = _c67_phase07_SimpleNamespace(previous06=previous06, divider=d, angles=angles, slots=tuple(basis['slots']))
        d.phase_endpoint = _c67_phase07_phase_endpoint
        return d

# work/c10/narrow/native/candidate07/tables07.py
def _initialize__c68_tables07():
    global _c68_tables07_FROZEN, _c68_tables07_HERE, _c68_tables07_INTEGRATED_ROOT, _c68_tables07_MODEL_SHA, _c68_tables07_NARROW, _c68_tables07_PINS, _c68_tables07_PREVIOUS_PATH, _c68_tables07_PREVIOUS_SHA, _c68_tables07_Path, _c68_tables07_RESOURCES, _c68_tables07_SECOND_RETIRED_ADDRESS_SLOTS, _c68_tables07_TableDebt, _c68_tables07_TableDebts, _c68_tables07__BASE, _c68_tables07__IntegratedPath, _c68_tables07__OLD, _c68_tables07___file__, _c68_tables07___name__, _c68_tables07_array, _c68_tables07_cb, _c68_tables07_certificate, _c68_tables07_checked_json, _c68_tables07_cleanup_joint16, _c68_tables07_common, _c68_tables07_emit_affine_frame, _c68_tables07_hashlib, _c68_tables07_inherited_module, _c68_tables07_km, _c68_tables07_load_joint16, _c68_tables07_lru_cache, _c68_tables07_model_truths, _c68_tables07_model_values, _c68_tables07_plan_from_json
    'Isolated Q48 first61/framed-second79 coefficient table adapters.\n\nThe second loader consumes four existing address owners as mutable work.\nEvery discarded value retains its exact original-raw-address phase function.\nThe caller must mark those four logical root slots absent immediately.\n'
    _c68_tables07__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate07/tables07.py', False).Path
    _c68_tables07_INTEGRATED_ROOT = _c68_tables07__IntegratedPath(_c68_tables07___file__).resolve().parents[5]
    _c68_tables07_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate07/tables07.py', False).Path
    _c68_tables07_lru_cache = _import_component('functools', 'work/c10/narrow/native/candidate07/tables07.py', False).lru_cache
    _c68_tables07_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate07/tables07.py', True)
    _c68_tables07_common = _import_component('variant', 'work/c10/narrow/native/candidate07/tables07.py', False).common
    _c68_tables07_inherited_module = _import_component('variant', 'work/c10/narrow/native/candidate07/tables07.py', False).inherited_module
    _c68_tables07_km = _c68_tables07_common.km
    _c68_tables07_cb = _c68_tables07_common.cb
    _c68_tables07_NARROW = _c68_tables07_common.NARROW
    _c68_tables07_MODEL_SHA = _c68_tables07_common.MODEL_SHA
    _c68_tables07_checked_json = _c68_tables07_common.checked_json
    _c68_tables07_plan_from_json = _c68_tables07_common.plan_from_json
    _c68_tables07_array = _c68_tables07_common.array
    _c68_tables07_HERE = _c68_tables07_Path(_c68_tables07___file__).resolve().parent
    _c68_tables07_PREVIOUS_PATH = _c68_tables07_HERE.parent / 'candidate06/tables06.py'
    _c68_tables07_PREVIOUS_SHA = 'f0eef9c8905b0d4e9c20bb286b33d526c0cf0f27ea4bb619c066ea7ed58a690b'
    pass
    _c68_tables07__OLD = _c68_tables07_inherited_module('tables06')
    pass
    _c68_tables07__BASE = _c68_tables07__OLD._BASE
    _c68_tables07_TableDebt = _c68_tables07__OLD.TableDebt
    _c68_tables07_TableDebts = _c68_tables07__OLD.TableDebts
    _c68_tables07_model_values = _c68_tables07__OLD.model_values
    _c68_tables07_model_truths = _c68_tables07__OLD.model_truths
    _c68_tables07_cleanup_joint16 = _c68_tables07__OLD.cleanup_joint16
    _c68_tables07_emit_affine_frame = _c68_tables07__OLD.emit_affine_frame
    assert _c68_tables07_TableDebts is _c68_tables07__OLD.TableDebts and _c68_tables07_cleanup_joint16 is _c68_tables07__OLD.cleanup_joint16
    _c68_tables07_FROZEN = _c68_tables07_NARROW / 'research/joint_loader/frozen'
    _c68_tables07_PINS = {'first': ('loader16_first61_Q48.json', '4857688e595af50828d7bedf0bc745eaaed8d10767e2e6ca6f77802887e1ad48'), 'second': ('loader16_second79_delay_Q48.json', '5276e10525e98c6dbf6dc215e2a525441ba36ce0342e3f2dd937a2720e085da1')}
    _c68_tables07_SECOND_RETIRED_ADDRESS_SLOTS = (0, 1, 2, 4)
    _c68_tables07_RESOURCES = {'first': dict(Toffolis=61, T=0, R=0, other_fixed_owners=26, work_cap=22, existing_input_work=0, new_zero_owners=22, complete_peak=48, return_owners=42, HMR_debts=45), 'second': dict(Toffolis=79, T=0, R=0, other_fixed_owners=27, work_cap=21, existing_input_work=4, new_zero_owners=17, complete_peak=48, return_owners=43, HMR_debts=65), 'cleanup': dict(Toffolis=9, T=0, R=0, complete_peak=44)}

    @_c68_tables07_lru_cache(maxsize=2)
    def _c68_tables07_certificate(which):
        name, digest = _c68_tables07_PINS[which]
        data = _c68_tables07_checked_json(_c68_tables07_FROZEN / name, digest)
        pass
        assert data['status'] == 'COMPLETE_MATHEMATICAL_LOADER_NOT_NATIVE'
        assert data['Toffolis'] == _c68_tables07_RESOURCES[which]['Toffolis']
        assert data['work_cap'] == data['work_peak'] == _c68_tables07_RESOURCES[which]['work_cap']
        assert data['complete_peak'] == 48
        return data

    def _c68_tables07_load_joint16(builder, address7, *, variant, debts):
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
        if len(address) != 7 or len(set(address)) != 7 or (not all((isinstance(q, _c68_tables07_km.q) for q in address))):
            raise ValueError('Expected seven current, distinct quantum address owners.')
        if not isinstance(debts, _c68_tables07_TableDebts):
            raise TypeError('Expected the shared pinned TableDebts owner.')
        data = _c68_tables07_certificate(variant)
        entry = builder.num_allocated_qubits
        before_debts = debts.total_recorded
        fixed_slots = (0, 1, 2, 3, 4, 5, 6) if variant == 'first' else (3, 5, 6)
        reusable_slots = () if variant == 'first' else _c68_tables07_SECOND_RETIRED_ADDRESS_SLOTS
        assert data['fixed_address_slots'] == list(fixed_slots)
        assert data['reusable_input_slots'] == list(reusable_slots)
        fixed = [address[i] for i in fixed_slots]
        work = [address[i] for i in reusable_slots]
        cap = data['work_cap']
        available = list(builder.alloc_qubits(cap - len(work)))
        assert len(available) == _c68_tables07_RESOURCES[variant]['new_zero_owners']
        offset = 1 + len(fixed)
        count = 0
        for item in data['steps']:
            kind = item['kind']
            if kind in ('bank', 'CCX_new_coordinate'):
                target = available.pop(0)
                plan = _c68_tables07_plan_from_json(item['plan'])
                _c68_tables07_cb.emit_xor(builder, fixed + work, target, plan)
                work.append(target)
                count += plan.and_count
            elif kind == 'Clifford_zero_dependent_coordinate':
                index = item['index']
                target = work[index]
                _c68_tables07__BASE._affine_xor(builder, fixed, work[:index], target, item['expression'])
                work.pop(index)
                available.append(target)
            elif kind == 'Clifford_frame_then_HMR':
                assert item['affine_fixed_offset'] == offset
                _c68_tables07_emit_affine_frame(builder, fixed, work, item['full_affine_rows'])
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
                plan = _c68_tables07_plan_from_json(item['plan'])
                _c68_tables07_cb.emit_xor(builder, fixed + work[1:], work[0], plan)
                count += plan.and_count
            elif kind == 'final_output_Clifford_frame':
                _c68_tables07_emit_affine_frame(builder, fixed, work, [int(row) << offset for row in item['matrix_rows']])
            else:
                raise AssertionError(('Unknown frozen Q48 loader operation', kind))
            assert len(work) + len(available) == cap and len(set(work + available)) == cap
            assert not set(fixed) & set(work + available)
        assert len(work) == 16 and count == _c68_tables07_RESOURCES[variant]['Toffolis']
        assert debts.total_recorded - before_debts == _c68_tables07_RESOURCES[variant]['HMR_debts']
        if available:
            builder.free(_c68_tables07_array(available))
        assert builder.num_allocated_qubits == entry + 16 - len(reusable_slots)
        return (list(work[:13]), list(work[13:]))

# work/c10/narrow/native/candidate07/variant.py
def _initialize__c69_candidate07_setup():
    global _c69_candidate07_setup_ACCEPTED, _c69_candidate07_setup_BASE, _c69_candidate07_setup_GATE_PATH, _c69_candidate07_setup_GATE_SHA, _c69_candidate07_setup_HERE, _c69_candidate07_setup_INTEGRATED_ROOT, _c69_candidate07_setup_MODULES, _c69_candidate07_setup_NARROW, _c69_candidate07_setup_NEW_TURN_UNITS50, _c69_candidate07_setup_PAPER, _c69_candidate07_setup_PAPER_SHA, _c69_candidate07_setup_PHASE_GATE, _c69_candidate07_setup_PHASE_GATE_SHA, _c69_candidate07_setup_PREVIOUS, _c69_candidate07_setup_Path, _c69_candidate07_setup_SITES, _c69_candidate07_setup__INSTALLED, _c69_candidate07_setup__IntegratedPath, _c69_candidate07_setup___file__, _c69_candidate07_setup___name__, _c69_candidate07_setup_accuracy_receipt, _c69_candidate07_setup_common, _c69_candidate07_setup_divider, _c69_candidate07_setup_hashlib, _c69_candidate07_setup_importlib, _c69_candidate07_setup_inherited_module, _c69_candidate07_setup_install, _c69_candidate07_setup_json, _c69_candidate07_setup_key, _c69_candidate07_setup_load_baseline, _c69_candidate07_setup_local_module, _c69_candidate07_setup_os, _c69_candidate07_setup_previous, _c69_candidate07_setup_spec, _c69_candidate07_setup_sys, _c69_candidate07_setup_variant_gate, _c69_candidate07_setup_verify_inputs
    'Paper-authorized Q48 composition with a new, independently checked phase.'
    _c69_candidate07_setup__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/native/candidate07/variant.py', False).Path
    _c69_candidate07_setup_INTEGRATED_ROOT = _c69_candidate07_setup__IntegratedPath(_c69_candidate07_setup___file__).resolve().parents[5]
    _c69_candidate07_setup_Path = _import_component('pathlib', 'work/c10/narrow/native/candidate07/variant.py', False).Path
    _c69_candidate07_setup_hashlib = _import_component('hashlib', 'work/c10/narrow/native/candidate07/variant.py', True)
    _c69_candidate07_setup_importlib = _import_component('importlib.util', 'work/c10/narrow/native/candidate07/variant.py', True)
    _c69_candidate07_setup_json = _import_component('json', 'work/c10/narrow/native/candidate07/variant.py', True)
    _c69_candidate07_setup_os = _import_component('os', 'work/c10/narrow/native/candidate07/variant.py', True)
    _c69_candidate07_setup_sys = _import_component('sys', 'work/c10/narrow/native/candidate07/variant.py', True)
    for _c69_candidate07_setup_key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        _c69_candidate07_setup_os.environ[_c69_candidate07_setup_key] = '1'
    _c69_candidate07_setup_HERE = _c69_candidate07_setup_Path(_c69_candidate07_setup___file__).resolve().parent
    _c69_candidate07_setup_NARROW = _c69_candidate07_setup_HERE.parents[1]
    _c69_candidate07_setup_BASE = _c69_candidate07_setup_HERE.parent / 'candidate01'
    _c69_candidate07_setup_PREVIOUS = _c69_candidate07_setup_HERE.parent / 'candidate06'
    _c69_candidate07_setup_GATE_PATH = _c69_candidate07_setup_NARROW / 'PAPER_GATE_RECEIPT_022_VARIANT.json'
    _c69_candidate07_setup_GATE_SHA = 'f8cfe4331b37a5184a4aab17ee85b4ac892c08c2cfb863fc4b1c1b3c9978262e'
    _c69_candidate07_setup_PAPER_SHA = '49ce6e7007b19abcd533b82a9f291b617cbc1c864a3d66287c0e63a87ebb82c4'
    _c69_candidate07_setup_PHASE_GATE_SHA = 'b579924175ee8e73c61c2f945b2d85e8ba2e536a8dbd8288a8332628142cd569'

    def _c69_candidate07_setup_verify_inputs():
        """Source integrity is verified by the integrated manifest before execution."""
        pass
    _c69_candidate07_setup_verify_inputs()
    _c69_candidate07_setup_spec = _spec('candidate07_pinned_candidate06_variant', _c69_candidate07_setup_PREVIOUS / 'variant.py')
    _c69_candidate07_setup_previous = _new_module(_c69_candidate07_setup_spec)
    _c69_candidate07_setup_sys.modules[_c69_candidate07_setup_spec.name] = _c69_candidate07_setup_previous
    _c69_candidate07_setup_spec.loader.exec_module(_c69_candidate07_setup_previous)
    _c69_candidate07_setup_common = _c69_candidate07_setup_previous.common
    _c69_candidate07_setup_divider = _c69_candidate07_setup_previous.divider
    _c69_candidate07_setup_ACCEPTED = _c69_candidate07_setup_common.checked_json(_c69_candidate07_setup_GATE_PATH, _c69_candidate07_setup_GATE_SHA)
    _c69_candidate07_setup_PAPER = _c69_candidate07_setup_common.checked_json(_c69_candidate07_setup_NARROW / _c69_candidate07_setup_ACCEPTED['paper_gate_path'], _c69_candidate07_setup_PAPER_SHA)
    _c69_candidate07_setup_PHASE_GATE = _c69_candidate07_setup_common.checked_json(_c69_candidate07_setup_NARROW / _c69_candidate07_setup_PAPER['phase_gate_path'], _c69_candidate07_setup_PHASE_GATE_SHA)
    _c69_candidate07_setup_NEW_TURN_UNITS50 = tuple(_c69_candidate07_setup_PAPER['new_angles_turn_units50'])
    _c69_candidate07_setup_SITES = tuple(_c69_candidate07_setup_PAPER['phase_site_order'])
    assert _c69_candidate07_setup_ACCEPTED['native_build_authorized']
    assert _c69_candidate07_setup_ACCEPTED['all_native_candidates_preserved'] == [1, 2, 3, 4, 5, 6]
    _c69_candidate07_setup__INSTALLED = False
    _c69_candidate07_setup_MODULES = {}

    def _c69_candidate07_setup_accuracy_receipt():
        """The new ring26 receipt; never substitute the old27 quantization data."""
        digest = _c69_candidate07_setup_PAPER['accuracy_receipt_sha256']
        result = _c69_candidate07_setup_common.checked_json(_c69_candidate07_setup_NARROW / _c69_candidate07_setup_PAPER['accuracy_receipt_path'], digest)
        exact = result['exact_screen']
        stats = exact['statistics']['grid50']
        assert result['status'] == 'COMPLETE_EXACT_RING26_PAPER_GATE_NATIVE_PENDING'
        assert stats['inputs'] == 3133452 and stats['failures'] == 0
        assert stats['minimum_margin_units'] == 124370688
        pass
        assert exact['direct_and_baseline_plus_delta_agree'] and exact['original_tolerance_unchanged']
        assert result['original_tolerance_unchanged'] and result['accuracy_decisions_integer']
        assert tuple(result['new_angles_units50']) == _c69_candidate07_setup_NEW_TURN_UNITS50
        assert _c69_candidate07_setup_NEW_TURN_UNITS50[-1] == 0 and any((x & 1 for x in _c69_candidate07_setup_NEW_TURN_UNITS50))
        return (result, digest)

    def _c69_candidate07_setup_variant_gate():
        _c69_candidate07_setup_verify_inputs()
        accuracy, digest = _c69_candidate07_setup_accuracy_receipt()
        assert _c69_candidate07_setup_PAPER['Q'] == 48 and _c69_candidate07_setup_PAPER['expected_Toffolis'] == 1584
        assert _c69_candidate07_setup_PAPER['T'] == 4 and _c69_candidate07_setup_PAPER['R'] == 33
        assert sum(_c69_candidate07_setup_PAPER['components_expected_Toffolis'].values()) == 1584
        assert max((row['live'] for row in _c69_candidate07_setup_PAPER['owner_cuts'])) == 48
        assert _c69_candidate07_setup_PAPER['full_lifecycle_E'] == 562 and _c69_candidate07_setup_PAPER['nonproduct_lifecycle_E'] == 321.5
        assert _c69_candidate07_setup_PAPER['first_preparation_peak'] == _c69_candidate07_setup_PAPER['second_preparation_peak'] == _c69_candidate07_setup_PAPER['endpoint_peak'] == 48
        assert _c69_candidate07_setup_PAPER['rotation_charge'] == accuracy['complete_paper_gate']['rotation_charge']
        assert _c69_candidate07_setup_PAPER['unchanged_original_tolerance'] and _c69_candidate07_setup_PAPER['new_oracle_required']
        assert _c69_candidate07_setup_PHASE_GATE['expected_Toffolis'] == 1585
        assert _c69_candidate07_setup_PHASE_GATE['phase_expected_Toffolis'] == 139
        assert tuple(_c69_candidate07_setup_PHASE_GATE['new_angles_turn_units50']) == _c69_candidate07_setup_NEW_TURN_UNITS50
        assert _c69_candidate07_setup_PHASE_GATE['zero_new_deferred_phase_debts_at_endpoint_exit']
        return dict(status='ACCEPTED_COMPLETE_Q48_RING26_GATE_NEW_NATIVE_PROOF_REQUIRED', Q=48, Toffolis_expected=1584, T=4, R=33, rotation_charge=_c69_candidate07_setup_PAPER['rotation_charge'], total_E=_c69_candidate07_setup_PAPER['total_E'], paper_cost=_c69_candidate07_setup_PAPER['complete_expected_cost'], complete_components=_c69_candidate07_setup_PAPER['components_expected_Toffolis'], first_loader_peak=48, second_loader_peak=48, endpoint_peak=48, accuracy_receipt_sha256=digest, exact_minimum_margin_units64=124370688, independent_phase_units50_sha256=_c69_candidate07_setup_PAPER['independent_phase_units50_sha256'])

    def _c69_candidate07_setup_local_module(name):
        if name not in _c69_candidate07_setup_MODULES:
            path = _c69_candidate07_setup_HERE / (name + '.py')
            if name in _c69_candidate07_setup_sys.modules:
                module = _c69_candidate07_setup_sys.modules[name]
                pass
            else:
                spec = _spec('candidate07_' + name, path)
                module = _new_module(spec)
                _c69_candidate07_setup_sys.modules[spec.name] = module
                _c69_candidate07_setup_sys.modules[name] = module
                spec.loader.exec_module(module)
            _c69_candidate07_setup_MODULES[name] = module
        return _c69_candidate07_setup_MODULES[name]

    def _c69_candidate07_setup_install():
        global _c69_candidate07_setup__INSTALLED
        _c69_candidate07_setup_variant_gate()
        if not _c69_candidate07_setup__INSTALLED:
            _c69_candidate07_setup_previous.install()
            _c69_candidate07_setup_local_module('phase07').install(_c69_candidate07_setup_previous, _c69_candidate07_setup_NEW_TURN_UNITS50, _c69_candidate07_setup_PHASE_GATE)
            _c69_candidate07_setup__INSTALLED = True
        return _c69_candidate07_setup_divider

    def _c69_candidate07_setup_load_baseline(name):
        return _c69_candidate07_setup_previous.load_baseline(name)

    def _c69_candidate07_setup_inherited_module(name):
        """Keep the old module/class identity while reusing its arithmetic only."""
        return _c69_candidate07_setup_previous.local_module(name)

# work/c10/narrow/research/quantized_producer/pair_normalization.py
def _initialize__c70_pair_normalization():
    global _c70_pair_normalization_COUNT_BOOK, _c70_pair_normalization_COUNT_FULL, _c70_pair_normalization_COUNT_G, _c70_pair_normalization_COUNT_RAW, _c70_pair_normalization_Counter, _c70_pair_normalization_HERE, _c70_pair_normalization_INTEGRATED_ROOT, _c70_pair_normalization_MAX_X, _c70_pair_normalization_NARROW, _c70_pair_normalization_ODD_FIRST, _c70_pair_normalization_ODD_OTHER, _c70_pair_normalization_PaperCounter, _c70_pair_normalization_Path, _c70_pair_normalization_THRESHOLD_PLANS, _c70_pair_normalization_TruthPhaseBuilder, _c70_pair_normalization__IntegratedPath, _c70_pair_normalization___file__, _c70_pair_normalization___name__, _c70_pair_normalization_anf_from_truth, _c70_pair_normalization_asdict, _c70_pair_normalization_binary_to_thermometer, _c70_pair_normalization_cb, _c70_pair_normalization_certify, _c70_pair_normalization_expr, _c70_pair_normalization_forward, _c70_pair_normalization_hashlib, _c70_pair_normalization_input_truths, _c70_pair_normalization_inverse, _c70_pair_normalization_j, _c70_pair_normalization_json, _c70_pair_normalization_km, _c70_pair_normalization_main, _c70_pair_normalization_operations, _c70_pair_normalization_os, _c70_pair_normalization_p, _c70_pair_normalization_paper, _c70_pair_normalization_route, _c70_pair_normalization_route_certificate, _c70_pair_normalization_small_plan, _c70_pair_normalization_sys, _c70_pair_normalization_t, _c70_pair_normalization_time
    'Direct pair normalization, exact Boolean/phase certificate and paper count.\n\nNo CircuitBuilder is instantiated. The proof packs every22-bit basis input\ninto Python integer truth vectors and checks all valid inputs simultaneously.\nEvery HMR outcome remains an independent symbolic phase coefficient.\n'
    _c70_pair_normalization__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).Path
    _c70_pair_normalization_INTEGRATED_ROOT = _c70_pair_normalization__IntegratedPath(_c70_pair_normalization___file__).resolve().parents[5]
    _c70_pair_normalization_Path = _import_component('pathlib', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).Path
    _c70_pair_normalization_os = _import_component('os', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _c70_pair_normalization_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _c70_pair_normalization_os.environ['OMP_NUM_THREADS'] = '1'
    _c70_pair_normalization_sys = _import_component('sys', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _c70_pair_normalization_json = _import_component('json', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _c70_pair_normalization_hashlib = _import_component('hashlib', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _c70_pair_normalization_time = _import_component('time', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    pass
    _c70_pair_normalization_HERE = _c70_pair_normalization_Path(_c70_pair_normalization___file__).resolve().parent
    _c70_pair_normalization_NARROW = _c70_pair_normalization_HERE.parents[1]
    _c70_pair_normalization_sys.path.insert(0, str(_c70_pair_normalization_NARROW / 'research/stream_phase'))
    _c70_pair_normalization_PaperCounter = _import_component('drive_paper_ledger', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).PaperCounter
    _c70_pair_normalization_km = _import_component('drive_paper_ledger', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).km
    _c70_pair_normalization_cb = _import_component('codebook', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False)
    _c70_pair_normalization_operations = _import_component('stage94_bit_routing_math', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).operations
    _c70_pair_normalization_route_certificate = _import_component('stage94_bit_routing_math', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).certificate
    _c70_pair_normalization_binary_to_thermometer = _import_component('thermometer_cleanup', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).binary_to_thermometer
    _c70_pair_normalization_anf_from_truth = _import_component('fusion.compiler', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).anf_from_truth
    _c70_pair_normalization_asdict = _import_component('dataclasses', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).asdict
    _c70_pair_normalization_MAX_X = 3 * (2 ** 10 - 2) ** 2
    _c70_pair_normalization_COUNT_FULL = (1 << 11) - 1
    _c70_pair_normalization_COUNT_RAW = _c70_pair_normalization_cb.word_functions(range(11), 4)
    _c70_pair_normalization_COUNT_G = _c70_pair_normalization_COUNT_RAW[0] & _c70_pair_normalization_COUNT_RAW[1]
    _c70_pair_normalization_COUNT_BOOK = _c70_pair_normalization_cb.Codebook(_c70_pair_normalization_COUNT_RAW + [_c70_pair_normalization_COUNT_G], size=11)
    _c70_pair_normalization_THRESHOLD_PLANS = []
    for _c70_pair_normalization_j in range(1, 11):
        _c70_pair_normalization_t = sum((int(k >= _c70_pair_normalization_j) << k for k in range(11)))
        _c70_pair_normalization_expr = _c70_pair_normalization_COUNT_BOOK.span.solve(_c70_pair_normalization_t)
        assert _c70_pair_normalization_expr is not None
        _c70_pair_normalization_p = _c70_pair_normalization_COUNT_BOOK.decode_expression(_c70_pair_normalization_expr)
        assert _c70_pair_normalization_p.evaluate_functions(_c70_pair_normalization_COUNT_RAW + [_c70_pair_normalization_COUNT_G], _c70_pair_normalization_COUNT_FULL) == _c70_pair_normalization_t
        _c70_pair_normalization_THRESHOLD_PLANS.append(_c70_pair_normalization_p)

    def _c70_pair_normalization_small_plan(n, fn):
        terms = _c70_pair_normalization_anf_from_truth(tuple((fn(*[x >> i & 1 for i in range(n)]) for x in range(1 << n))))
        assert all((t.bit_count() <= 2 for t in terms))
        linear = sum((t for t in terms if t.bit_count() == 1))
        edges = tuple((tuple((i for i in range(n) if t >> i & 1)) for t in terms if t.bit_count() == 2))
        return _c70_pair_normalization_cb.QuadraticCodePlan(n, 0 in terms, linear, edges, (), linear)
    _c70_pair_normalization_ODD_FIRST = _c70_pair_normalization_small_plan(2, lambda t1, h: 1 ^ h ^ h & t1)
    _c70_pair_normalization_ODD_OTHER = _c70_pair_normalization_small_plan(3, lambda prev, cur, h: prev ^ h & (prev ^ cur))

    def _c70_pair_normalization_route(builder, x, T, inverse=False):
        seq = list(_c70_pair_normalization_operations(11))
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

    def _c70_pair_normalization_forward(builder, x, flags):
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
        _c70_pair_normalization_route(builder, x, T)
        for j in range(1, 11):
            q = P[2 * j - 2]
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            if j == 1:
                _c70_pair_normalization_cb.emit_phase(builder, [T[0], x[21]], m, _c70_pair_normalization_ODD_FIRST)
            else:
                _c70_pair_normalization_cb.emit_phase(builder, [T[j - 2], T[j - 1], x[21]], m, _c70_pair_normalization_ODD_OTHER)
            builder.free(m)
            builder.free(q)
        g = builder.alloc_qubits(1)[0]
        builder.ccx(flags[0], flags[1], g)
        for q, p in zip(T, _c70_pair_normalization_THRESHOLD_PLANS):
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            _c70_pair_normalization_cb.emit_phase(builder, flags + [g], m, p)
            builder.free(m)
            builder.free(q)
        builder.del_and(flags[0], flags[1], g)
        builder.free(g)

    def _c70_pair_normalization_inverse(builder, x, flags):
        x = list(x)
        flags = list(flags)
        T, helpers = _c70_pair_normalization_binary_to_thermometer(builder, flags, 10)
        _c70_pair_normalization_route(builder, x, T, inverse=True)
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
        builder.free(_c70_pair_normalization_km.array(helpers))

    class _c70_pair_normalization_Counter(_c70_pair_normalization_PaperCounter):

        def swap(self, *args):
            pass

    class _c70_pair_normalization_TruthPhaseBuilder(_c70_pair_normalization_Counter):
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
            assert isinstance(q, _c70_pair_normalization_km.q)
            return self.values[q]

        def free(self, x):
            if isinstance(x, _c70_pair_normalization_km.q):
                assert not self.value(x) & self.valid, ('dirty_free', str(x))
            return super().free(x)

        def x(self, q):
            assert not self.stack and isinstance(q, _c70_pair_normalization_km.q)
            self.values[q] ^= self.full

        def cx(self, a, t):
            assert not self.stack and isinstance(t, _c70_pair_normalization_km.q)
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
            if isinstance(q, _c70_pair_normalization_km.b):
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

    def _c70_pair_normalization_input_truths():
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

    def _c70_pair_normalization_certify():
        start = _c70_pair_normalization_time.monotonic()
        size = 1 << 22
        full = (1 << size) - 1
        valid = (1 << _c70_pair_normalization_MAX_X + 1) - 2
        src = _c70_pair_normalization_input_truths()
        b = _c70_pair_normalization_TruthPhaseBuilder(49, full, valid)
        x = list(b.alloc_qubits(22))
        flags = list(b.alloc_qubits(4))
        for q, v in zip(x, src):
            b.values[q] = v
        expected = [0] * 22
        expected_flags = [0] * 4
        for k in range(11):
            lo = 1 << 20 - 2 * k
            hi = min(_c70_pair_normalization_MAX_X + 1, 1 << 22 - 2 * k)
            mask = (1 << hi) - (1 << lo) if hi > lo else 0
            for i in range(2 * k, 22):
                expected[i] ^= mask & src[i - 2 * k]
            for bit in range(4):
                if k >> bit & 1:
                    expected_flags[bit] ^= mask
        _c70_pair_normalization_forward(b, x, flags)
        assert all(((b.value(q) ^ v) & valid == 0 for q, v in zip(x, expected))), 'wrong_pair_normalization'
        assert all(((b.value(q) ^ v) & valid == 0 for q, v in zip(flags, expected_flags))), 'wrong_pair_count'
        assert b.num_allocated_qubits == 26
        b.check_phase()
        f = float(b.count)
        fpeak = b.peak
        fm = b.measurements
        _c70_pair_normalization_inverse(b, x, flags)
        assert all(((b.value(q) ^ v) & valid == 0 for q, v in zip(x, src))), 'input_not_restored'
        assert all((b.value(q) & valid == 0 for q in flags)), 'count_not_cleared'
        assert b.num_allocated_qubits == 26
        b.check_phase()
        total = float(b.count)
        assert (f, total) == (53, 97.5), (f, total)
        return dict(status='EXACT_ALL_INPUT_AND_ALL_HMR_PHASE_CERTIFICATE_NOT_NATIVE', original_inputs=_c70_pair_normalization_MAX_X, truth_vector_domain_bits=22, required_interval=[1, _c70_pair_normalization_MAX_X], normalized_map='n=x*4**k, k=floor((22-bit_length(x))/2), n in[2^20,2^22)', mathematical_phase_error=0, all_original_bits_restored=True, all_scratch_and_flags_zero=True, forward_measurements=fm, total_independent_HMR_symbols=b.measurements, phase_proof='Every HMR outcome is an independent symbolic coefficient; each complete coefficient truth vector vanishes on every official input.', forward_E=f, inverse_expected_E=total - f, total_expected_E=total, peak=fpeak, T=0, R=0, seconds=_c70_pair_normalization_time.monotonic() - start, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    def _c70_pair_normalization_paper(cap):
        b = _c70_pair_normalization_Counter(cap)
        x = list(b.alloc_qubits(22))
        flags = list(b.alloc_qubits(4))
        _c70_pair_normalization_forward(b, x, flags)
        f = float(b.count)
        fp = b.peak
        assert b.num_allocated_qubits == 26
        b.peak = 26
        _c70_pair_normalization_inverse(b, x, flags)
        assert b.num_allocated_qubits == 26
        return dict(Q_cap=cap, forward_E=f, inverse_expected_E=float(b.count) - f, total_expected_E=float(b.count), forward_peak=fp, inverse_peak=b.peak, T=0, R=0)

    def _c70_pair_normalization_main():
        result = dict(scope='NEW_PAIR_NORMALIZATION_PAPER_AND_EXACT_BOOLEAN_ONLY', route=_c70_pair_normalization_route_certificate(11), threshold_plans=[_c70_pair_normalization_asdict(p) for p in _c70_pair_normalization_THRESHOLD_PLANS], certificate=_c70_pair_normalization_certify(), paper=[_c70_pair_normalization_paper(q) for q in range(46, 53)], excluded_transfer='The122E Stage94 semilog/packed interface is not used.', native_gate='Use only after the full actual lifecycle ledger is updated and clears its paper gate; native proof still required.')
        (_c70_pair_normalization_HERE / 'pair_normalization.json').write_text(_c70_pair_normalization_json.dumps(result, indent=2) + '\n')
        print(_c70_pair_normalization_json.dumps({'certificate': result['certificate'], 'paper': result['paper']}, indent=2))
    if _c70_pair_normalization___name__ == '__main__':
        _c70_pair_normalization_main()

# work/c10/narrow/research/quantized_producer/pair_normalization.py [independent arithmetic context]
def _initialize__c70_pair_normalization_private():
    global _c70_pair_normalization_private_COUNT_BOOK, _c70_pair_normalization_private_COUNT_FULL, _c70_pair_normalization_private_COUNT_G, _c70_pair_normalization_private_COUNT_RAW, _c70_pair_normalization_private_Counter, _c70_pair_normalization_private_HERE, _c70_pair_normalization_private_INTEGRATED_ROOT, _c70_pair_normalization_private_MAX_X, _c70_pair_normalization_private_NARROW, _c70_pair_normalization_private_ODD_FIRST, _c70_pair_normalization_private_ODD_OTHER, _c70_pair_normalization_private_PaperCounter, _c70_pair_normalization_private_Path, _c70_pair_normalization_private_THRESHOLD_PLANS, _c70_pair_normalization_private_TruthPhaseBuilder, _c70_pair_normalization_private__IntegratedPath, _c70_pair_normalization_private___file__, _c70_pair_normalization_private___name__, _c70_pair_normalization_private_anf_from_truth, _c70_pair_normalization_private_asdict, _c70_pair_normalization_private_binary_to_thermometer, _c70_pair_normalization_private_cb, _c70_pair_normalization_private_certify, _c70_pair_normalization_private_expr, _c70_pair_normalization_private_forward, _c70_pair_normalization_private_hashlib, _c70_pair_normalization_private_input_truths, _c70_pair_normalization_private_inverse, _c70_pair_normalization_private_j, _c70_pair_normalization_private_json, _c70_pair_normalization_private_km, _c70_pair_normalization_private_main, _c70_pair_normalization_private_operations, _c70_pair_normalization_private_os, _c70_pair_normalization_private_p, _c70_pair_normalization_private_paper, _c70_pair_normalization_private_route, _c70_pair_normalization_private_route_certificate, _c70_pair_normalization_private_small_plan, _c70_pair_normalization_private_sys, _c70_pair_normalization_private_t, _c70_pair_normalization_private_time
    'Direct pair normalization, exact Boolean/phase certificate and paper count.\n\nNo CircuitBuilder is instantiated. The proof packs every22-bit basis input\ninto Python integer truth vectors and checks all valid inputs simultaneously.\nEvery HMR outcome remains an independent symbolic phase coefficient.\n'
    _c70_pair_normalization_private__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).Path
    _c70_pair_normalization_private_INTEGRATED_ROOT = _c70_pair_normalization_private__IntegratedPath(_c70_pair_normalization_private___file__).resolve().parents[5]
    _c70_pair_normalization_private_Path = _import_component('pathlib', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).Path
    _c70_pair_normalization_private_os = _import_component('os', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _c70_pair_normalization_private_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _c70_pair_normalization_private_os.environ['OMP_NUM_THREADS'] = '1'
    _c70_pair_normalization_private_sys = _import_component('sys', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _c70_pair_normalization_private_json = _import_component('json', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _c70_pair_normalization_private_hashlib = _import_component('hashlib', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    _c70_pair_normalization_private_time = _import_component('time', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', True)
    pass
    _c70_pair_normalization_private_HERE = _c70_pair_normalization_private_Path(_c70_pair_normalization_private___file__).resolve().parent
    _c70_pair_normalization_private_NARROW = _c70_pair_normalization_private_HERE.parents[1]
    _c70_pair_normalization_private_sys.path.insert(0, str(_c70_pair_normalization_private_NARROW / 'research/stream_phase'))
    _c70_pair_normalization_private_PaperCounter = _import_component('drive_paper_ledger', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).PaperCounter
    _c70_pair_normalization_private_km = _import_component('drive_paper_ledger', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).km
    _c70_pair_normalization_private_cb = _import_component('codebook', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False)
    _c70_pair_normalization_private_operations = _import_component('stage94_bit_routing_math', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).operations
    _c70_pair_normalization_private_route_certificate = _import_component('stage94_bit_routing_math', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).certificate
    _c70_pair_normalization_private_binary_to_thermometer = _import_component('thermometer_cleanup', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).binary_to_thermometer
    _c70_pair_normalization_private_anf_from_truth = _import_component('fusion.compiler', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).anf_from_truth
    _c70_pair_normalization_private_asdict = _import_component('dataclasses', 'work/c10/narrow/research/quantized_producer/pair_normalization.py', False).asdict
    _c70_pair_normalization_private_MAX_X = 3 * (2 ** 10 - 2) ** 2
    _c70_pair_normalization_private_COUNT_FULL = (1 << 11) - 1
    _c70_pair_normalization_private_COUNT_RAW = _c70_pair_normalization_private_cb.word_functions(range(11), 4)
    _c70_pair_normalization_private_COUNT_G = _c70_pair_normalization_private_COUNT_RAW[0] & _c70_pair_normalization_private_COUNT_RAW[1]
    _c70_pair_normalization_private_COUNT_BOOK = _c70_pair_normalization_private_cb.Codebook(_c70_pair_normalization_private_COUNT_RAW + [_c70_pair_normalization_private_COUNT_G], size=11)
    _c70_pair_normalization_private_THRESHOLD_PLANS = []
    for _c70_pair_normalization_private_j in range(1, 11):
        _c70_pair_normalization_private_t = sum((int(k >= _c70_pair_normalization_private_j) << k for k in range(11)))
        _c70_pair_normalization_private_expr = _c70_pair_normalization_private_COUNT_BOOK.span.solve(_c70_pair_normalization_private_t)
        assert _c70_pair_normalization_private_expr is not None
        _c70_pair_normalization_private_p = _c70_pair_normalization_private_COUNT_BOOK.decode_expression(_c70_pair_normalization_private_expr)
        assert _c70_pair_normalization_private_p.evaluate_functions(_c70_pair_normalization_private_COUNT_RAW + [_c70_pair_normalization_private_COUNT_G], _c70_pair_normalization_private_COUNT_FULL) == _c70_pair_normalization_private_t
        _c70_pair_normalization_private_THRESHOLD_PLANS.append(_c70_pair_normalization_private_p)

    def _c70_pair_normalization_private_small_plan(n, fn):
        terms = _c70_pair_normalization_private_anf_from_truth(tuple((fn(*[x >> i & 1 for i in range(n)]) for x in range(1 << n))))
        assert all((t.bit_count() <= 2 for t in terms))
        linear = sum((t for t in terms if t.bit_count() == 1))
        edges = tuple((tuple((i for i in range(n) if t >> i & 1)) for t in terms if t.bit_count() == 2))
        return _c70_pair_normalization_private_cb.QuadraticCodePlan(n, 0 in terms, linear, edges, (), linear)
    _c70_pair_normalization_private_ODD_FIRST = _c70_pair_normalization_private_small_plan(2, lambda t1, h: 1 ^ h ^ h & t1)
    _c70_pair_normalization_private_ODD_OTHER = _c70_pair_normalization_private_small_plan(3, lambda prev, cur, h: prev ^ h & (prev ^ cur))

    def _c70_pair_normalization_private_route(builder, x, T, inverse=False):
        seq = list(_c70_pair_normalization_private_operations(11))
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

    def _c70_pair_normalization_private_forward(builder, x, flags):
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
        _c70_pair_normalization_private_route(builder, x, T)
        for j in range(1, 11):
            q = P[2 * j - 2]
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            if j == 1:
                _c70_pair_normalization_private_cb.emit_phase(builder, [T[0], x[21]], m, _c70_pair_normalization_private_ODD_FIRST)
            else:
                _c70_pair_normalization_private_cb.emit_phase(builder, [T[j - 2], T[j - 1], x[21]], m, _c70_pair_normalization_private_ODD_OTHER)
            builder.free(m)
            builder.free(q)
        g = builder.alloc_qubits(1)[0]
        builder.ccx(flags[0], flags[1], g)
        for q, p in zip(T, _c70_pair_normalization_private_THRESHOLD_PLANS):
            m = builder.alloc_bits(1)[0]
            builder.hmr(q, m)
            _c70_pair_normalization_private_cb.emit_phase(builder, flags + [g], m, p)
            builder.free(m)
            builder.free(q)
        builder.del_and(flags[0], flags[1], g)
        builder.free(g)

    def _c70_pair_normalization_private_inverse(builder, x, flags):
        x = list(x)
        flags = list(flags)
        T, helpers = _c70_pair_normalization_private_binary_to_thermometer(builder, flags, 10)
        _c70_pair_normalization_private_route(builder, x, T, inverse=True)
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
        builder.free(_c70_pair_normalization_private_km.array(helpers))

    class _c70_pair_normalization_private_Counter(_c70_pair_normalization_private_PaperCounter):

        def swap(self, *args):
            pass

    class _c70_pair_normalization_private_TruthPhaseBuilder(_c70_pair_normalization_private_Counter):
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
            assert isinstance(q, _c70_pair_normalization_private_km.q)
            return self.values[q]

        def free(self, x):
            if isinstance(x, _c70_pair_normalization_private_km.q):
                assert not self.value(x) & self.valid, ('dirty_free', str(x))
            return super().free(x)

        def x(self, q):
            assert not self.stack and isinstance(q, _c70_pair_normalization_private_km.q)
            self.values[q] ^= self.full

        def cx(self, a, t):
            assert not self.stack and isinstance(t, _c70_pair_normalization_private_km.q)
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
            if isinstance(q, _c70_pair_normalization_private_km.b):
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

    def _c70_pair_normalization_private_input_truths():
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

    def _c70_pair_normalization_private_certify():
        start = _c70_pair_normalization_private_time.monotonic()
        size = 1 << 22
        full = (1 << size) - 1
        valid = (1 << _c70_pair_normalization_private_MAX_X + 1) - 2
        src = _c70_pair_normalization_private_input_truths()
        b = _c70_pair_normalization_private_TruthPhaseBuilder(49, full, valid)
        x = list(b.alloc_qubits(22))
        flags = list(b.alloc_qubits(4))
        for q, v in zip(x, src):
            b.values[q] = v
        expected = [0] * 22
        expected_flags = [0] * 4
        for k in range(11):
            lo = 1 << 20 - 2 * k
            hi = min(_c70_pair_normalization_private_MAX_X + 1, 1 << 22 - 2 * k)
            mask = (1 << hi) - (1 << lo) if hi > lo else 0
            for i in range(2 * k, 22):
                expected[i] ^= mask & src[i - 2 * k]
            for bit in range(4):
                if k >> bit & 1:
                    expected_flags[bit] ^= mask
        _c70_pair_normalization_private_forward(b, x, flags)
        assert all(((b.value(q) ^ v) & valid == 0 for q, v in zip(x, expected))), 'wrong_pair_normalization'
        assert all(((b.value(q) ^ v) & valid == 0 for q, v in zip(flags, expected_flags))), 'wrong_pair_count'
        assert b.num_allocated_qubits == 26
        b.check_phase()
        f = float(b.count)
        fpeak = b.peak
        fm = b.measurements
        _c70_pair_normalization_private_inverse(b, x, flags)
        assert all(((b.value(q) ^ v) & valid == 0 for q, v in zip(x, src))), 'input_not_restored'
        assert all((b.value(q) & valid == 0 for q in flags)), 'count_not_cleared'
        assert b.num_allocated_qubits == 26
        b.check_phase()
        total = float(b.count)
        assert (f, total) == (53, 97.5), (f, total)
        return dict(status='EXACT_ALL_INPUT_AND_ALL_HMR_PHASE_CERTIFICATE_NOT_NATIVE', original_inputs=_c70_pair_normalization_private_MAX_X, truth_vector_domain_bits=22, required_interval=[1, _c70_pair_normalization_private_MAX_X], normalized_map='n=x*4**k, k=floor((22-bit_length(x))/2), n in[2^20,2^22)', mathematical_phase_error=0, all_original_bits_restored=True, all_scratch_and_flags_zero=True, forward_measurements=fm, total_independent_HMR_symbols=b.measurements, phase_proof='Every HMR outcome is an independent symbolic coefficient; each complete coefficient truth vector vanishes on every official input.', forward_E=f, inverse_expected_E=total - f, total_expected_E=total, peak=fpeak, T=0, R=0, seconds=_c70_pair_normalization_private_time.monotonic() - start, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    def _c70_pair_normalization_private_paper(cap):
        b = _c70_pair_normalization_private_Counter(cap)
        x = list(b.alloc_qubits(22))
        flags = list(b.alloc_qubits(4))
        _c70_pair_normalization_private_forward(b, x, flags)
        f = float(b.count)
        fp = b.peak
        assert b.num_allocated_qubits == 26
        b.peak = 26
        _c70_pair_normalization_private_inverse(b, x, flags)
        assert b.num_allocated_qubits == 26
        return dict(Q_cap=cap, forward_E=f, inverse_expected_E=float(b.count) - f, total_expected_E=float(b.count), forward_peak=fp, inverse_peak=b.peak, T=0, R=0)

    def _c70_pair_normalization_private_main():
        result = dict(scope='NEW_PAIR_NORMALIZATION_PAPER_AND_EXACT_BOOLEAN_ONLY', route=_c70_pair_normalization_private_route_certificate(11), threshold_plans=[_c70_pair_normalization_private_asdict(p) for p in _c70_pair_normalization_private_THRESHOLD_PLANS], certificate=_c70_pair_normalization_private_certify(), paper=[_c70_pair_normalization_private_paper(q) for q in range(46, 53)], excluded_transfer='The122E Stage94 semilog/packed interface is not used.', native_gate='Use only after the full actual lifecycle ledger is updated and clears its paper gate; native proof still required.')
        (_c70_pair_normalization_private_HERE / 'pair_normalization.json').write_text(_c70_pair_normalization_private_json.dumps(result, indent=2) + '\n')
        print(_c70_pair_normalization_private_json.dumps({'certificate': result['certificate'], 'paper': result['paper']}, indent=2))
    if _c70_pair_normalization_private___name__ == '__main__':
        _c70_pair_normalization_private_main()

# work/c10/narrow/research/stream_phase/drive_paper_ledger.py
def _initialize__c71_drive_paper_ledger():
    global _c71_drive_paper_ledger_Fraction, _c71_drive_paper_ledger_HERE, _c71_drive_paper_ledger_INTEGRATED_ROOT, _c71_drive_paper_ledger_NARROW, _c71_drive_paper_ledger_PaperCounter, _c71_drive_paper_ledger_Path, _c71_drive_paper_ledger__IntegratedPath, _c71_drive_paper_ledger___file__, _c71_drive_paper_ledger___name__, _c71_drive_paper_ledger_forward_add, _c71_drive_paper_ledger_inverse_add, _c71_drive_paper_ledger_json, _c71_drive_paper_ledger_km, _c71_drive_paper_ledger_load_table, _c71_drive_paper_ledger_main, _c71_drive_paper_ledger_os, _c71_drive_paper_ledger_paper, _c71_drive_paper_ledger_sys
    "Source-expanded resource ledger, without constructing any native circuit.\n\nThis counter implements only allocation and gate accounting. It intentionally\nhas no finish_circuit method and produces no KMB. The arithmetic emitter's\nexisting deterministic segmentation/dirty-terminal policy supplies the paper\nschedule. This is a cost calculation, not an arithmetic or native proof.\n"
    _c71_drive_paper_ledger__IntegratedPath = _import_component('pathlib', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False).Path
    _c71_drive_paper_ledger_INTEGRATED_ROOT = _c71_drive_paper_ledger__IntegratedPath(_c71_drive_paper_ledger___file__).resolve().parents[5]
    _c71_drive_paper_ledger_os = _import_component('os', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', True)
    _c71_drive_paper_ledger_os.environ['OPENBLAS_NUM_THREADS'] = '1'
    _c71_drive_paper_ledger_sys = _import_component('sys', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', True)
    _c71_drive_paper_ledger_json = _import_component('json', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', True)
    _c71_drive_paper_ledger_Path = _import_component('pathlib', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False).Path
    _c71_drive_paper_ledger_Fraction = _import_component('fractions', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False).Fraction
    pass
    _c71_drive_paper_ledger_HERE = _c71_drive_paper_ledger_Path(_c71_drive_paper_ledger___file__).resolve().parent
    _c71_drive_paper_ledger_NARROW = _c71_drive_paper_ledger_HERE.parents[1]
    _c71_drive_paper_ledger_sys.path[:0] = [str(_c71_drive_paper_ledger_NARROW / 'base/official/kickmix'), str(_c71_drive_paper_ledger_NARROW / 'checkpoint002/cleanroom/baseline_stage97/engine')]
    _c71_drive_paper_ledger_km = _import_component('kickmix', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False)
    _c71_drive_paper_ledger_forward_add = _import_component('paired_arithmetic', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False).forward_add
    _c71_drive_paper_ledger_inverse_add = _import_component('paired_arithmetic', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False).inverse_add
    _c71_drive_paper_ledger_load_table = _import_component('fusion.lookup', 'work/c10/narrow/research/stream_phase/drive_paper_ledger.py', False).load_table

    class _c71_drive_paper_ledger_PaperCounter:

        def __init__(self, cap):
            self.max_qubits = cap
            self.live = set()
            self.nextq = 0
            self.nextb = 0
            self.pool = []
            self.stack = []
            self.count = _c71_drive_paper_ledger_Fraction(0)
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
                    q = _c71_drive_paper_ledger_km.q(self.nextq)
                    self.nextq += 1
                self.live.add(q)
                out.append(q)
            self.peak = max(self.peak, len(self.live))
            return _c71_drive_paper_ledger_km.array(out)

        def alloc_bits(self, n):
            out = _c71_drive_paper_ledger_km.array([_c71_drive_paper_ledger_km.b(i) for i in range(self.nextb, self.nextb + n)])
            self.nextb += n
            return out

        def free(self, x):
            if isinstance(x, _c71_drive_paper_ledger_km.q):
                assert x in self.live
                self.live.remove(x)
                self.pool.append(x)
            elif isinstance(x, _c71_drive_paper_ledger_km.b):
                pass
            else:
                for q in x:
                    self.free(q)

        def push_condition(self, b):
            self.stack.append(b)

        def pop_condition(self):
            self.stack.pop()

        def _charge(self, n=1):
            self.count += _c71_drive_paper_ledger_Fraction(n, 1 << len(set(self.stack)))

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

    def _c71_drive_paper_ledger_paper(cap, m=37, schedule=None, mode='baseline'):
        schedule = schedule or {}
        b = _c71_drive_paper_ledger_PaperCounter(cap)
        v = list(b.alloc_qubits(12))
        p = list(b.alloc_qubits(10 if mode == 'baseline' else 16))
        flags = list(b.alloc_qubits(4))
        u = list(b.alloc_qubits(14))
        original = list(u)
        base_data = b.num_allocated_qubits
        table = [(1 << min(k, 10) + 3) - 1 for k in range(16)]
        load_before = b.count
        _c71_drive_paper_ledger_load_table(b, table, flags, u)
        load_forward = b.count - load_before
        extra_init = 0
        tmp = b.alloc_qubits(extra_init)
        init_before = b.count
        init = _c71_drive_paper_ledger_forward_add(b, v, u)
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
            debt = _c71_drive_paper_ledger_forward_add(b, v[k + 1:], u[k + 1:], carry_in=carry)
            rounds.append(dict(j=j, k=k, phase=phase, helpers=helper_count, forward=float(b.count - before)))
            records.append((j, k, phase, helper_count, debt))
            b.free(tmp)
        for j, k, phase, helper_count, debt in reversed(records):
            tmp = list(b.alloc_qubits(helper_count))
            carry = tmp[-1] if tmp else v[k]
            before = b.count
            _c71_drive_paper_ledger_inverse_add(b, v[k + 1:], u[k + 1:], debt, carry_in=carry, dirty_wires=p + flags)
            rounds[j - 1]['inverse'] = float(b.count - before)
            b.free(tmp)
            u = u[1:] + u[:1]
        assert u == original
        tmp = b.alloc_qubits(extra_init)
        before = b.count
        _c71_drive_paper_ledger_inverse_add(b, v, u, init, dirty_wires=p + flags)
        init_inverse = b.count - before
        b.free(tmp)
        before = b.count
        _c71_drive_paper_ledger_load_table(b, table, flags, u)
        load_inverse = b.count - before
        arithmetic = b.count
        if mode == 'baseline':
            routing = _c71_drive_paper_ledger_Fraction(0)
            routing_detail = {}
        else:
            carry_logic = 2 * (19 * (3 if mode == 'cswap' else 2) + 5 * (2 if mode == 'cswap' else 1))
            routing_detail = dict(ring16_permutation=72, threshold_preparation=54, threshold_debt=0.5, carry_logic=carry_logic, initialization_correction=8)
            routing = sum(map(_c71_drive_paper_ledger_Fraction, routing_detail.values()))
        return dict(status='SOURCE_EXPANDED_PAPER_LEDGER_NOT_NATIVE', mode=mode, Q_cap=cap, data_registers={'root_v': 12, 'correction_with_zero_sentinel': len(p), 'flags': 4, 'u': 14}, base_data=base_data, peak_allocation=b.peak, m=m, schedule=schedule, adder_and_lookup_toffolis=float(arithmetic), routing_toffolis=float(routing), expected_toffolis=float(arithmetic + routing), T=1, R=m - 3, lookup_forward=float(load_forward), lookup_inverse=float(load_inverse), initial_add_forward=float(init_forward), initial_add_inverse=float(init_inverse), routing_detail=routing_detail, rounds=rounds)

    def _c71_drive_paper_ledger_main():
        calibration = []
        old = _json_loads(_read_text(_c71_drive_paper_ledger_NARROW / 'checkpoint002/cleanroom/table_arch/taper_balanced_caps.json'))
        schedule = {j: j - 26 for j in range(28, 36)}
        for row in old['rows']:
            p = _c71_drive_paper_ledger_paper(row['Q'], 37, schedule, 'baseline')
            expected = row['counts']['toffoli_like']
            calibration.append(dict(Q=row['Q'], paper=p['expected_toffolis'], previous_native=expected, match=p['expected_toffolis'] == expected))
        assert all((x['match'] for x in calibration)), calibration
        rows = []
        schedules = [(36, {}, 'm36_exact'), (36, {j: j - 29 for j in range(30, 35)}, 'm36_tight'), (37, schedule, 'm37_balanced'), (37, {j: j - 25 for j in range(27, 36)}, 'm37_wide')]
        for cap in range(48, 53):
            for mode in ('binary', 'cswap'):
                for m, sched, name in schedules:
                    try:
                        p = _c71_drive_paper_ledger_paper(cap, m, sched, mode)
                        p['schedule_name'] = name
                        rows.append(p)
                    except Exception as e:
                        rows.append(dict(Q_cap=cap, mode=mode, schedule_name=name, status='PAPER_SCHEDULE_BLOCKED', reason=str(e)))
        result = dict(scope='Pure Python allocation/expected-gate counter expanding existing own arithmetic source. No native CircuitBuilder, KMB, simulator, or proof of the new arithmetic. Full producer, normalization, root and rotation charge remain separate line items.', calibration=calibration, rows=rows)
        (_c71_drive_paper_ledger_HERE / 'drive_paper_ledger.json').write_text(_c71_drive_paper_ledger_json.dumps(result, indent=2) + '\n')
        print(_c71_drive_paper_ledger_json.dumps(calibration))
        for r in rows:
            print(_c71_drive_paper_ledger_json.dumps({k: v for k, v in r.items() if k not in ['rounds', 'schedule', 'routing_detail']}))
    if _c71_drive_paper_ledger___name__ == '__main__':
        _c71_drive_paper_ledger_main()

_PREFIXES={('agents/composer/p/w2core_e2.py', 0): '_c0_w2core_e2_', ('agents/micro47/scripts/relocate_cs2.py', 0): '_c1_relocate_cs2_', ('agents/width/src/block_replay.py', 0): '_c2_block_replay_', ('agents/width/src/paid_R_cleanup_q48.py', 0): '_c3_paid_R_cleanup_q48_', ('patches/patch_coef2_q46.py', 0): '_c4_patch_coef2_q46_', ('patches/patch_coefdisp.py', 0): '_c5_patch_coefdisp_', ('patches/patch_donor_first60.py', 0): '_c6_patch_donor_first60_', ('patches/patch_endpoint_v9e2.py', 0): '_c7_patch_endpoint_v9e2_', ('patches/patch_fwd_narrow.py', 0): '_c8_patch_fwd_narrow_', ('patches/patch_h2ret.py', 0): '_c9_patch_h2ret_', ('patches/patch_hret_sat_s15k7a.py', 0): '_c10_patch_hret_sat_s15k7a_', ('patches/patch_ld_first20_56b8.py', 0): '_c11_patch_ld_first20_56b8_', ('patches/patch_proddisp.py', 0): '_c12_patch_proddisp_', ('patches/patch_q47_decoder_resynth2.py', 0): '_c13_patch_q47_decoder_resynth2_', ('patches/patch_second46_c19_70nb1.py', 0): '_c14_patch_second46_c19_70nb1_', ('patches/patch_seedinv.py', 0): '_c15_patch_seedinv_', ('patches/patch_w47_body.py', 0): '_c16_patch_w47_body_', ('patches/q46_loaders.py', 0): '_c17_q46_loaders_', ('tools/audit_affine.py', 0): '_c18_audit_affine_', ('tools/audit_pairs.py', 0): '_c19_audit_pairs_', ('tools/build_variant.py', 0): '_c20_build_variant_', ('tools/hold_pass.py', 0): '_c21_hold_pass_', ('tools/kmsim.py', 0): '_c22_kmsim_', ('tools/kmx_to_kmb.py', 0): '_c23_kmx_to_kmb_', ('tools/merge_zpow.py', 0): '_c24_merge_zpow_', ('tools/postpass.py', 0): '_c25_postpass_', ('work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', 0): '_c26_arithmetic_setup_', ('work/c10/narrow/arithmetic_round2/native/candidate10/lifecycle10.py', 0): '_c27_lifecycle10_', ('work/c10/narrow/arithmetic_round2/research/divider/history12_kernel.py', 0): '_c28_history12_kernel_', ('work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', 0): '_c29_adapter_', ('work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', 0): '_c30_top12_kernel_', ('work/c10/narrow/arithmetic_round2/research/product_coefficient/native_transfer.py', 0): '_c31_native_transfer_', ('work/c10/narrow/arithmetic_round2/research/product_coefficient/native_v3/adapter.py', 0): '_c32_adapter_', ('work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', 0): '_c33_normalization9475_', ('work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', 0): '_c34_root192_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', 0): '_c35_branch_prover_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py', 0): '_c36_codebook_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', 0): '_c37_cyclic_phase_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/dirty_terminal.py', 0): '_c38_dirty_terminal_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/__init__.py', 0): '_c39___init___', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', 0): '_c40_arithmetic_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', 1): '_c40_arithmetic_private_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/compiler.py', 0): '_c41_compiler_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/lookup.py', 0): '_c42_lookup_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', 0): '_c43_paired_arithmetic_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', 1): '_c43_paired_arithmetic_private_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/quadratic_terms.py', 0): '_c44_quadratic_terms_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/stage94_bit_routing_math.py', 0): '_c45_stage94_bit_routing_math_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/thermometer_cleanup.py', 0): '_c46_thermometer_cleanup_', ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', 0): '_c47_fourier_resource_expectation_', ('work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', 0): '_c48_consuming_odd_sqrt_', ('work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', 1): '_c48_consuming_odd_sqrt_private_', ('work/c10/narrow/native/candidate01/common.py', 0): '_c49_common_', ('work/c10/narrow/native/candidate01/divider.py', 0): '_c50_divider_', ('work/c10/narrow/native/candidate01/generate.py', 0): '_c51_generate_', ('work/c10/narrow/native/candidate01/layout.py', 0): '_c52_layout_', ('work/c10/narrow/native/candidate01/lifecycle.py', 0): '_c53_lifecycle_', ('work/c10/narrow/native/candidate01/normalization.py', 0): '_c54_normalization_', ('work/c10/narrow/native/candidate01/root_decode.py', 0): '_c55_root_decode_', ('work/c10/narrow/native/candidate01/tables.py', 0): '_c56_tables_', ('work/c10/narrow/native/candidate02/variant.py', 0): '_c57_candidate02_setup_', ('work/c10/narrow/native/candidate03/variant.py', 0): '_c58_candidate03_setup_', ('work/c10/narrow/native/candidate04/variant.py', 0): '_c59_candidate04_setup_', ('work/c10/narrow/native/candidate05/variant.py', 0): '_c60_candidate05_setup_', ('work/c10/narrow/native/candidate06/decoder06.py', 0): '_c61_decoder06_', ('work/c10/narrow/native/candidate06/divider_cleanup06.py', 0): '_c62_divider_cleanup06_', ('work/c10/narrow/native/candidate06/lifecycle06.py', 0): '_c63_lifecycle06_', ('work/c10/narrow/native/candidate06/phase06.py', 0): '_c64_phase06_', ('work/c10/narrow/native/candidate06/tables06.py', 0): '_c65_tables06_', ('work/c10/narrow/native/candidate06/variant.py', 0): '_c66_candidate06_setup_', ('work/c10/narrow/native/candidate07/phase07.py', 0): '_c67_phase07_', ('work/c10/narrow/native/candidate07/tables07.py', 0): '_c68_tables07_', ('work/c10/narrow/native/candidate07/variant.py', 0): '_c69_candidate07_setup_', ('work/c10/narrow/research/quantized_producer/pair_normalization.py', 0): '_c70_pair_normalization_', ('work/c10/narrow/research/quantized_producer/pair_normalization.py', 1): '_c70_pair_normalization_private_', ('work/c10/narrow/research/stream_phase/drive_paper_ledger.py', 0): '_c71_drive_paper_ledger_'}
_GROUPS={('agents/width/src/block_replay.py', 'width_block_replay'): 0, ('agents/width/src/paid_R_cleanup_q48.py', 'width_pro2_paid_R_cleanup_q48'): 0, ('patches/patch_coef2_q46.py', 'variant_patch_patch_coef2_q46'): 0, ('patches/patch_coefdisp.py', 'variant_patch_patch_coefdisp'): 0, ('patches/patch_donor_first60.py', 'variant_patch_patch_donor_first60'): 0, ('patches/patch_endpoint_v9e2.py', 'variant_patch_patch_endpoint_v9e2'): 0, ('patches/patch_fwd_narrow.py', 'variant_patch_patch_fwd_narrow'): 0, ('patches/patch_h2ret.py', 'variant_patch_patch_h2ret'): 0, ('patches/patch_hret_sat_s15k7a.py', 'variant_patch_patch_hret_sat_s15k7a'): 0, ('patches/patch_ld_first20_56b8.py', 'variant_patch_patch_ld_first20_56b8'): 0, ('patches/patch_proddisp.py', 'variant_patch_patch_proddisp'): 0, ('patches/patch_q47_decoder_resynth2.py', 'variant_patch_patch_q47_decoder_resynth2'): 0, ('patches/patch_second46_c19_70nb1.py', 'variant_patch_patch_second46_c19_70nb1'): 0, ('patches/patch_seedinv.py', 'variant_patch_patch_seedinv'): 0, ('patches/patch_w47_body.py', 'variant_patch_patch_w47_body'): 0, ('patches/q46_loaders.py', 'tk46_q46_second_loader'): 0, ('work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', 'arithmetic_variant'): 0, ('work/c10/narrow/arithmetic_round2/native/candidate10/lifecycle10.py', 'lifecycle10'): 0, ('work/c10/narrow/arithmetic_round2/research/divider/history12_kernel.py', '_ar004_frozen_history12_kernel'): 0, ('work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', 'candidate10_adapter_divider'): 0, ('work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', 'top12_kernel'): 0, ('work/c10/narrow/arithmetic_round2/research/product_coefficient/native_transfer.py', 'candidate10_adapter_coefficient'): 0, ('work/c10/narrow/arithmetic_round2/research/product_coefficient/native_v3/adapter.py', 'candidate10_adapter_product'): 0, ('work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', 'candidate10_adapter_normalization'): 0, ('work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', 'candidate10_adapter_root'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', 'branch_prover'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py', 'codebook'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', 'cyclic_phase'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/dirty_terminal.py', 'dirty_terminal'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/__init__.py', 'fusion'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', 'fusion.arithmetic'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', 'fusion._round2_rn3_immutable_arithmetic'): 1, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/compiler.py', 'fusion.compiler'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/lookup.py', 'fusion.lookup'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', 'paired_arithmetic'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', '_candidate01_product_paired'): 1, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/quadratic_terms.py', 'quadratic_terms'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/stage94_bit_routing_math.py', 'stage94_bit_routing_math'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/thermometer_cleanup.py', 'thermometer_cleanup'): 0, ('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', 'fourier_resource_expectation'): 0, ('work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', 'consuming_odd_sqrt'): 0, ('work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', '_round2_rn3_immutable_odd_sqrt'): 1, ('work/c10/narrow/native/candidate01/common.py', 'common'): 0, ('work/c10/narrow/native/candidate01/divider.py', 'divider'): 0, ('work/c10/narrow/native/candidate01/generate.py', 'candidate02_pinned_generate'): 0, ('work/c10/narrow/native/candidate01/layout.py', 'layout'): 0, ('work/c10/narrow/native/candidate01/lifecycle.py', 'candidate06_pinned_candidate01_lifecycle'): 0, ('work/c10/narrow/native/candidate01/normalization.py', 'normalization'): 0, ('work/c10/narrow/native/candidate01/root_decode.py', 'root_decode'): 0, ('work/c10/narrow/native/candidate01/tables.py', '_candidate06_pinned_tables01'): 0, ('work/c10/narrow/native/candidate02/variant.py', 'candidate03_pinned_candidate02_variant'): 0, ('work/c10/narrow/native/candidate03/variant.py', 'candidate04_pinned_candidate03_variant'): 0, ('work/c10/narrow/native/candidate04/variant.py', 'candidate05_pinned_candidate04_variant'): 0, ('work/c10/narrow/native/candidate05/variant.py', 'candidate06_pinned_candidate05_variant'): 0, ('work/c10/narrow/native/candidate06/decoder06.py', 'candidate06_decoder06'): 0, ('work/c10/narrow/native/candidate06/decoder06.py', 'decoder06'): 0, ('work/c10/narrow/native/candidate06/divider_cleanup06.py', 'candidate06_divider_cleanup06'): 0, ('work/c10/narrow/native/candidate06/divider_cleanup06.py', 'divider_cleanup06'): 0, ('work/c10/narrow/native/candidate06/lifecycle06.py', 'candidate06_lifecycle06'): 0, ('work/c10/narrow/native/candidate06/lifecycle06.py', 'lifecycle06'): 0, ('work/c10/narrow/native/candidate06/phase06.py', 'candidate06_phase06'): 0, ('work/c10/narrow/native/candidate06/phase06.py', 'phase06'): 0, ('work/c10/narrow/native/candidate06/tables06.py', 'candidate06_tables06'): 0, ('work/c10/narrow/native/candidate06/tables06.py', 'tables06'): 0, ('work/c10/narrow/native/candidate06/variant.py', 'candidate07_pinned_candidate06_variant'): 0, ('work/c10/narrow/native/candidate07/phase07.py', 'candidate07_phase07'): 0, ('work/c10/narrow/native/candidate07/phase07.py', 'phase07'): 0, ('work/c10/narrow/native/candidate07/tables07.py', 'candidate07_tables07'): 0, ('work/c10/narrow/native/candidate07/tables07.py', 'tables07'): 0, ('work/c10/narrow/native/candidate07/variant.py', 'variant'): 0, ('work/c10/narrow/research/quantized_producer/pair_normalization.py', '_round2_rn2df_private_pair_normalizer'): 0, ('work/c10/narrow/research/quantized_producer/pair_normalization.py', 'native_pair_normalization_source'): 1, ('work/c10/narrow/research/stream_phase/drive_paper_ledger.py', 'drive_paper_ledger'): 0}
_FACTORIES={
('agents/composer/p/w2core_e2.py', 0):_initialize__c0_w2core_e2,
('agents/micro47/scripts/relocate_cs2.py', 0):_initialize__c1_relocate_cs2,
('agents/width/src/block_replay.py', 0):_initialize__c2_block_replay,
('agents/width/src/paid_R_cleanup_q48.py', 0):_initialize__c3_paid_R_cleanup_q48,
('patches/patch_coef2_q46.py', 0):_initialize__c4_patch_coef2_q46,
('patches/patch_coefdisp.py', 0):_initialize__c5_patch_coefdisp,
('patches/patch_donor_first60.py', 0):_initialize__c6_patch_donor_first60,
('patches/patch_endpoint_v9e2.py', 0):_initialize__c7_patch_endpoint_v9e2,
('patches/patch_fwd_narrow.py', 0):_initialize__c8_patch_fwd_narrow,
('patches/patch_h2ret.py', 0):_initialize__c9_patch_h2ret,
('patches/patch_hret_sat_s15k7a.py', 0):_initialize__c10_patch_hret_sat_s15k7a,
('patches/patch_ld_first20_56b8.py', 0):_initialize__c11_patch_ld_first20_56b8,
('patches/patch_proddisp.py', 0):_initialize__c12_patch_proddisp,
('patches/patch_q47_decoder_resynth2.py', 0):_initialize__c13_patch_q47_decoder_resynth2,
('patches/patch_second46_c19_70nb1.py', 0):_initialize__c14_patch_second46_c19_70nb1,
('patches/patch_seedinv.py', 0):_initialize__c15_patch_seedinv,
('patches/patch_w47_body.py', 0):_initialize__c16_patch_w47_body,
('patches/q46_loaders.py', 0):_initialize__c17_q46_loaders,
('tools/audit_affine.py', 0):_initialize__c18_audit_affine,
('tools/audit_pairs.py', 0):_initialize__c19_audit_pairs,
('tools/build_variant.py', 0):_initialize__c20_build_variant,
('tools/hold_pass.py', 0):_initialize__c21_hold_pass,
('tools/kmsim.py', 0):_initialize__c22_kmsim,
('tools/kmx_to_kmb.py', 0):_initialize__c23_kmx_to_kmb,
('tools/merge_zpow.py', 0):_initialize__c24_merge_zpow,
('tools/postpass.py', 0):_initialize__c25_postpass,
('work/c10/narrow/arithmetic_round2/native/candidate10/arithmetic_variant.py', 0):_initialize__c26_arithmetic_setup,
('work/c10/narrow/arithmetic_round2/native/candidate10/lifecycle10.py', 0):_initialize__c27_lifecycle10,
('work/c10/narrow/arithmetic_round2/research/divider/history12_kernel.py', 0):_initialize__c28_history12_kernel,
('work/c10/narrow/arithmetic_round2/research/divider/native_ar004/adapter.py', 0):_initialize__c29_adapter,
('work/c10/narrow/arithmetic_round2/research/divider/top12_kernel.py', 0):_initialize__c30_top12_kernel,
('work/c10/narrow/arithmetic_round2/research/product_coefficient/native_transfer.py', 0):_initialize__c31_native_transfer,
('work/c10/narrow/arithmetic_round2/research/product_coefficient/native_v3/adapter.py', 0):_initialize__c32_adapter,
('work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py', 0):_initialize__c33_normalization9475,
('work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py', 0):_initialize__c34_root192,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/branch_prover.py', 0):_initialize__c35_branch_prover,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py', 0):_initialize__c36_codebook,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/cyclic_phase.py', 0):_initialize__c37_cyclic_phase,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/dirty_terminal.py', 0):_initialize__c38_dirty_terminal,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/__init__.py', 0):_initialize__c39___init__,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', 0):_initialize__c40_arithmetic,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/arithmetic.py', 1):_initialize__c40_arithmetic_private,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/compiler.py', 0):_initialize__c41_compiler,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/fusion/lookup.py', 0):_initialize__c42_lookup,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', 0):_initialize__c43_paired_arithmetic,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py', 1):_initialize__c43_paired_arithmetic_private,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/quadratic_terms.py', 0):_initialize__c44_quadratic_terms,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/stage94_bit_routing_math.py', 0):_initialize__c45_stage94_bit_routing_math,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/thermometer_cleanup.py', 0):_initialize__c46_thermometer_cleanup,
('work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/tests/fourier_resource_expectation.py', 0):_initialize__c47_fourier_resource_expectation,
('work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', 0):_initialize__c48_consuming_odd_sqrt,
('work/c10/narrow/checkpoint002/cleanroom/odd_sqrt/consuming_odd_sqrt.py', 1):_initialize__c48_consuming_odd_sqrt_private,
('work/c10/narrow/native/candidate01/common.py', 0):_initialize__c49_common,
('work/c10/narrow/native/candidate01/divider.py', 0):_initialize__c50_divider,
('work/c10/narrow/native/candidate01/generate.py', 0):_initialize__c51_generate,
('work/c10/narrow/native/candidate01/layout.py', 0):_initialize__c52_layout,
('work/c10/narrow/native/candidate01/lifecycle.py', 0):_initialize__c53_lifecycle,
('work/c10/narrow/native/candidate01/normalization.py', 0):_initialize__c54_normalization,
('work/c10/narrow/native/candidate01/root_decode.py', 0):_initialize__c55_root_decode,
('work/c10/narrow/native/candidate01/tables.py', 0):_initialize__c56_tables,
('work/c10/narrow/native/candidate02/variant.py', 0):_initialize__c57_candidate02_setup,
('work/c10/narrow/native/candidate03/variant.py', 0):_initialize__c58_candidate03_setup,
('work/c10/narrow/native/candidate04/variant.py', 0):_initialize__c59_candidate04_setup,
('work/c10/narrow/native/candidate05/variant.py', 0):_initialize__c60_candidate05_setup,
('work/c10/narrow/native/candidate06/decoder06.py', 0):_initialize__c61_decoder06,
('work/c10/narrow/native/candidate06/divider_cleanup06.py', 0):_initialize__c62_divider_cleanup06,
('work/c10/narrow/native/candidate06/lifecycle06.py', 0):_initialize__c63_lifecycle06,
('work/c10/narrow/native/candidate06/phase06.py', 0):_initialize__c64_phase06,
('work/c10/narrow/native/candidate06/tables06.py', 0):_initialize__c65_tables06,
('work/c10/narrow/native/candidate06/variant.py', 0):_initialize__c66_candidate06_setup,
('work/c10/narrow/native/candidate07/phase07.py', 0):_initialize__c67_phase07,
('work/c10/narrow/native/candidate07/tables07.py', 0):_initialize__c68_tables07,
('work/c10/narrow/native/candidate07/variant.py', 0):_initialize__c69_candidate07_setup,
('work/c10/narrow/research/quantized_producer/pair_normalization.py', 0):_initialize__c70_pair_normalization,
('work/c10/narrow/research/quantized_producer/pair_normalization.py', 1):_initialize__c70_pair_normalization_private,
('work/c10/narrow/research/stream_phase/drive_paper_ledger.py', 0):_initialize__c71_drive_paper_ledger,
}
_PATCH_ORDER='patch patch_fwd_narrow.py\npatch patch_w47_body.py\npatch patch_endpoint_v9e2.py\npatch patch_hret_sat_s15k7a.py\npatch patch_seedinv.py\npatch patch_coefdisp.py\npatch patch_coef2_q46.py\npatch patch_h2ret.py\npatch patch_proddisp.py\npatch patch_donor_first60.py\npatch patch_ld_first20_56b8.py\npatch patch_second46_c19_70nb1.py\npatch patch_q47_decoder_resynth2.py\nwith patch_endpoint_walk8.py\nwith q46_loaders.py\nQ 46\npost agents/micro47/scripts/relocate_cs2.py\n'
if __name__=='__main__':
    run_stage(sys.argv[1],sys.argv[2:])
