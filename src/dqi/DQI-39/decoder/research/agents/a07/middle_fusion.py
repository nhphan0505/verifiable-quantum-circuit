"""Install the exact root/16/15 forward fusion on a private carried converter.

This is the composable installation interface. The three-frame arithmetic is
frozen in blocked_three_noscratch.py and root_fused_three.py. See PROOF.md for
the completed polynomial recurrence and the four/eight-frame handoff.

Install before private_rebind, and before or after other independent forward
Hankel installers. The reverse converter and its transcript interface remain
the original carried converter's.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import blocked_three_noscratch as arithmetic
from root_fused_three import look_solve
from ephemeral_root_block import install as install_root_lifetime


def install(cv):
    p = arithmetic.p
    cells = dict(zip(cv.__code__.co_freevars, cv.__closure__))
    short = cells['core'].cell_contents.__globals__
    scope = short['old'].direct_post.__globals__
    scope.update(
        ordinary_solve=scope['look_solve'],
        convolution=lambda b, x, y, out: scope['dk'].conv(
            b, x, y, out, len(x) + len(y) - 1),
        phase_classical_parity=arithmetic.phase_classical_parity,
    )
    for fun in (
        arithmetic.mask_word, arithmetic.erase_mask,
        arithmetic.copy_flag, arithmetic.phase_flag,
        arithmetic.payload_middle, arithmetic.pre_partial, look_solve,
    ):
        scope[fun.__name__] = p.clone(fun, scope)
    short['old'].look_solve = scope['look_solve']
    install_root_lifetime(cv, p)
    return cv
