"""Retire raw cache coordinates after exact norm-coordinate shears."""
from functools import lru_cache
from pathlib import Path
import inspect
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_local_forward_partial as partial
from decode_local_forward_partial import combo, jet, replacement_ids, joint

ROWS = (446783, 868352, 1573003, 24895, 90548, 196747)


@lru_cache(None)
def partial_layout(count):
    omitted = list(ROWS[:count])
    span = {0}
    for row in omitted:
        quotient = row >> 12
        assert quotient not in span
        span |= {v ^ quotient for v in tuple(span)}
    kept = []
    for quotient in (1 << j for j in range(9)):
        if quotient not in span:
            kept.append(quotient << 12)
            span |= {v ^ quotient for v in tuple(span)}
    rows = [1 << j for j in range(12)] + kept + omitted
    columns = [sum(((row >> j) & 1) << i for i, row in enumerate(rows))
               for j in range(21)]
    return tuple(columns), tuple(jet.inverse_columns(columns))


retire_raw = combo.xsub.clone(partial.retire_raw,
                              dict(partial.retire_raw.__globals__, partial_layout=partial_layout))
rebuild_raw = combo.xsub.clone(partial.rebuild_raw,
                               dict(partial.rebuild_raw.__globals__, partial_layout=partial_layout))
cached_inverse_partial = combo.xsub.clone(partial.cached_inverse_partial,
    dict(partial.cached_inverse_partial.__globals__, retire_raw=retire_raw, rebuild_raw=rebuild_raw))
source = inspect.getsource(partial.inverse24_forward_partial)
source = source.replace('if omitted > len(OMITTED):',
                        'if omitted > len(OMITTED) or b.num_allocated_qubits + 37 > 889:')
environment = dict(partial.inverse24_forward_partial.__globals__,
                   OMITTED=ROWS, cached_inverse_partial=cached_inverse_partial)
exec(compile(source, __file__, 'exec'), environment)
replacement = combo.xsub.private_rebind(environment['inverse24_forward_partial'], combo.synth.replacements)
install = combo.xsub.clone(partial.install, dict(partial.install.__globals__, replacement=replacement))
decode = install(combo.decode)
