"""PP-004: Chuyển pha CS endpoint về normalization.

Extracted unchanged from INV-51 at 1390fe402fb1779d3798ae344de3ce73edac93f5.
Copyright 2026 Syed Asad Ali. Apache-2.0; see LICENSE.txt and NOTICE.txt.
Preserves branch/HMR correction and exact angles. Requires the INV-51 component
backend for parsing, full-domain simulation and legacy namespace isolation.
Use initialize(namespace, factory) through the backend, or run(backend, stage, args).
No config or grading outputs are created by this integration API itself.
"""
import types

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


FACTORIES = ('_initialize_relocate_cs2',)
STAGES = ('agents/micro47/scripts/relocate_cs2.py',)

def initialize(namespace, factory):
    """Initialize a legacy component in its isolated backend namespace.

    Bind the existing Python function to backend globals; no source strings,
    eval or exec are used. Mutable component state must remain in that namespace.
    """
    allowed = FACTORIES
    if factory not in allowed:
        raise ValueError(f'Unsupported factory: {factory}')
    function = globals()[factory]
    types.FunctionType(function.__code__, namespace, factory)()


def run(backend, stage, args):
    """Run a supported legacy stage with explicit backend and CLI argument list.

    The caller selects temporary output paths and must preserve its input.
    Backend is a freshly loaded INV-51 circuit module; no generator is run.
    """
    if stage not in STAGES:
        raise ValueError(f'Unsupported stage: {stage}')
    backend.run_stage(stage, list(map(str, args)))
