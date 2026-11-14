"""Whole decoder replacing convert/scan/unconvert by the direct Forney scan."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT), str(HERE)]
import decode_next_best as prior
from direct_forney import scan


def owner_scope(fn):
    """Follow only the actual public body wrapper, never an arbitrary owner."""
    while 'synthesize' not in fn.__code__.co_names:
        if 'body' in fn.__code__.co_names and 'body' in fn.__globals__:
            fn = fn.__globals__['body']
        else:
            raise AssertionError((fn.__name__, fn.__code__.co_filename))
    return fn.__globals__


g = owner_scope(prior.decode)


def decode(b, S, E):
    with b.mark('mask_projection'):
        mt = g['baseline'].project(b, S, E)
    with b.mark('initial'):
        g['linear_words'](b, S, g['matrix'])
    with b.mark('extract'):
        et = g['extraction'](b, S)
    with b.mark('synthesis'):
        A, B, undo = g['synthesize'](b, S, et['pole'])
    with b.mark('direct_forney_scan'):
        scan(b, A, B, E, skip_points=g['baseline'].SELECTED,
             node_polynomial=g['Pscan'])
    with b.mark('unsynthesis'):
        undo()
    with b.mark('unextract'):
        g['extraction'](b, S, True, et)
    with b.mark('uninitial'):
        g['linear_words'](b, S, g['matrix'], True)
    with b.mark('restore_masks'):
        g['baseline'].restore(b, E, mt)


__all__ = ['decode']
