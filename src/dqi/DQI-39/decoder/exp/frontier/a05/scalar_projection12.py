"""Cache the complete linear first state of the trailing subfield replay."""
from types import SimpleNamespace
import scalar_projection as shared
from scalar_projection import *
import replay_erase


def erase_third12(b, head, N, D, q, cache):
    scale(b, N, inv(q))
    b.swap(N, D)
    mask = b.alloc_bits(12)
    b.hmr(N, mask)
    b.cz(cache, mask)
    ar.phase_product(b, head[0], D, mask)
    b.free(mask)
    b.cx(cache, N)
    b.cx(N, cache)
    b.free(cache)


def install(entry):
    original = entry.__globals__['extraction']
    ref = original.__globals__['ref']
    original_step = ref.scalar_step
    state = {}
    def scalar_step(b, head, N, D, q, reverse=False, first=False):
        if not reverse:
            original_step(b, head, N, D, q, reverse, first)
            if first:
                state.clear()
                cache = b.alloc_qubits(12)
                b.cx(D, cache)
                scale(b, cache, ref.ks[1])
                state.update(cache=cache, index=0)
            else:
                state['index'] += 1
                if state['index'] == 2:
                    state['third_head'] = head
        elif head is state.get('third_head'):
            erase_third12(b, head, N, D, q, state.pop('cache'))
        else:
            original_step(b, head, N, D, q, reverse, first)
    patched_ref = SimpleNamespace(**dict(vars(ref), scalar_step=scalar_step))
    extraction = combo.xsub.clone(original, dict(original.__globals__, ref=patched_ref))
    return combo.xsub.clone(entry, dict(entry.__globals__, extraction=extraction))
