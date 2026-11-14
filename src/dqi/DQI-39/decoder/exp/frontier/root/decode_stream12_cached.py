"""Use flag-free cached twelve-bit inverses in streamed scalar calls."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'a04')]
import decode_flagfree_cached as cache
from nonzero_consume16 import functions


def stream_wrapper(original):
    def stream(b, x):
        space = 889-b.num_allocated_qubits
        if len(x) != 12 or space < 19:
            return original(b, x)
        out, flag = cache.CACHED12[space < 22](b, x, cache.jet.PLAN12, False)
        assert flag is None
        transcript = b.alloc_bits(12)
        b.hmr(x, transcript)
        b.swap(x, out)
        b.free(out)
        return transcript
    return stream


def install(entry):
    names = {'inverse_stream_noscratch', 'inverse_stream_narrow', 'stream_nonzero', 'chosen'}
    replacements = {id(fn): stream_wrapper(fn) for fn in functions(entry)
                    if fn.__name__ in names}
    assert replacements
    scope = dict(entry.__globals__)
    for name in ('extraction', 'synthesize'):
        scope[name] = cache.xs.private_rebind(scope[name], replacements)
    return cache.xs.clone(entry, scope)


decode = install(cache.combo.decode)
