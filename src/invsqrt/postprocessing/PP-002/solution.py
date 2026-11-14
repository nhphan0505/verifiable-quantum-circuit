"""PP-002: Thay cổng phi tuyến bằng quan hệ affine.

Extracted unchanged from INV-51 at 1390fe402fb1779d3798ae344de3ce73edac93f5.
Copyright 2026 Syed Asad Ali. Apache-2.0; see LICENSE.txt and NOTICE.txt.
Preserves branch/HMR correction and exact angles. Requires the INV-51 component
backend for parsing, full-domain simulation and legacy namespace isolation.
Use initialize(namespace, factory) through the backend, or run(backend, stage, args).
No config or grading outputs are created by this integration API itself.
"""
import types

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


FACTORIES = ('_initialize_audit_affine', '_initialize_postpass')
STAGES = ('tools/audit_affine.py', 'tools/postpass.py')

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
