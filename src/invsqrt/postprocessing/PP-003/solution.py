"""PP-003: Gộp pha Z_POW trên cùng hàm Boolean.

Extracted unchanged from INV-51 at 1390fe402fb1779d3798ae344de3ce73edac93f5.
Copyright 2026 Syed Asad Ali. Apache-2.0; see LICENSE.txt and NOTICE.txt.
Preserves branch/HMR correction and exact angles. Requires the INV-51 component
backend for parsing, full-domain simulation and legacy namespace isolation.
Use initialize(namespace, factory) through the backend, or run(backend, stage, args).
No config or grading outputs are created by this integration API itself.
"""
import types

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


FACTORIES = ('_initialize_merge_zpow',)
STAGES = ('tools/merge_zpow.py',)

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
