"""PP-001: Giữ và tái sử dụng tích Boolean.

Extracted unchanged from INV-51 at 1390fe402fb1779d3798ae344de3ce73edac93f5.
Copyright 2026 Syed Asad Ali. Apache-2.0; see LICENSE.txt and NOTICE.txt.
Preserves branch/HMR correction and exact angles. Requires the INV-51 component
backend for parsing, full-domain simulation and legacy namespace isolation.
Use initialize(namespace, factory) through the backend, or run(backend, stage, args).
No config or grading outputs are created by this integration API itself.
"""
import types

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


FACTORIES = ('_initialize_audit_pairs', '_initialize_hold_pass')
STAGES = ('tools/audit_pairs.py', 'tools/hold_pass.py')

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
