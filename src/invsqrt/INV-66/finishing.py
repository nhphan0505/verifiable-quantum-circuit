"""Orchestrate the existing, separate PP-001..PP-005 implementations.

The arithmetic builder calls this module only on its newly generated circuit.
Hold chains are passed to PP-001 individually; remaining coordinates are updated
after each rewrite so interleaved intervals retain their original gate owners.
No quantum rewrite implementation is copied into the arithmetic generator.
"""
from pathlib import Path
import contextlib
import io
import json
import sys
from arithmetic_helpers import load_backend

def _stage(key, args, log):
    backend = load_backend()
    previous = sys.argv[:]
    try:
        with log.open('w', encoding='utf-8', newline='\n') as stream, contextlib.redirect_stdout(stream):
            backend.run_stage(key, list(map(str, args)))
    finally:
        sys.argv = previous

def remap_pending(chains, applied, hops):
    """Map operation coordinates through one PP-001 chain rewrite.

    Replacement additions occur after their original gate, while hop additions
    occur before it. Remaining chains contain disjoint gate occurrences.
    """
    insertions = [(applied[0], 1, False), (applied[-1], 2, False)]
    insertions += [(when, 2, True) for when, old, new in hops]
    return [[g + sum((delta for pos, delta, before in insertions if pos < g or (before and pos == g))) for g in chain] for chain in chains]

def _holds(text, pairs):
    backend = load_backend()
    spec = backend._Spec('inv66_hold_adapter', backend._VROOT / 'tools/hold_pass.py')
    module = backend._new_module(spec)
    spec.loader.exec_module(module)
    chains = module.chains_from_pairs(pairs, 46)
    chains = sorted(chains, key=lambda c: -c[0])
    reports = []
    while chains:
        chain = chains.pop(0)
        ops, qw, depth, zero_before, next_ref = module.analyse(text)
        plan = module.plan_chain(ops, qw, depth, zero_before, next_ref, chain)
        text, report = module.apply_chains(text, [chain])
        reports.extend(report)
        chains = remap_pending(chains, chain, plan['hops'])
    return (text, reports)

def finish(circuit, work):
    """Apply the declared finishing pipeline to a fresh in-memory circuit."""
    work = Path(work)
    work.mkdir(parents=True, exist_ok=False)
    raw = work / 'raw.kmx'
    buffer = io.BytesIO()
    circuit.to_file(buffer, format='kmx')
    raw.write_bytes(buffer.getvalue())
    first = work / 's1.audit.json'
    _stage('tools/audit_affine.py', [raw, '--out', first], work / '01-affine.log')
    pairs = work / 's1.pairs.json'
    _stage('tools/audit_pairs.py', [raw, '--live', work / 's1.audit.live.npy', '--out', pairs], work / '02-pairs.log')
    text, holds = _holds(raw.read_text(encoding='utf-8'), json.loads(pairs.read_text(encoding='utf-8'))['rows'])
    current = work / 's2.kmx'
    current.write_text(text, encoding='utf-8', newline='\n')
    rounds = []
    for index in range(1, 5):
        audit = work / f'r{index}.audit.json'
        _stage('tools/audit_affine.py', [current, '--out', audit], work / f'03-affine-{index}.log')
        findings = json.loads(audit.read_text(encoding='utf-8'))['findings']
        rounds.append(len(findings))
        if not findings:
            break
        following = work / f'r{index}.kmx'
        _stage('tools/postpass.py', [current, audit, '--out', following], work / f'04-rewrite-{index}.log')
        current = following
    merged = work / 'merged.kmx'
    _stage('tools/merge_zpow.py', [current, '--out', merged], work / '05-merge.log')
    relocated = work / 'relocated.kmx'
    _stage('agents/micro47/scripts/relocate_cs2.py', [merged, relocated], work / '06-relocate.log')
    return (relocated.read_text(encoding='utf-8'), dict(hold_chains=holds, affine_rounds=rounds, methods=['PP-001', 'PP-002', 'PP-003', 'PP-004']))
