"""Native middle products, root and degree14 fusion, and pipelined reverse norm pairs."""
from pathlib import Path
import sys
import inspect

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'research/agents' / name)
                for name in ('a09', 'a08', 'a07', 'a01')]
import hankel_compact
import middle_fusion
import blocked_three_noscratch
import root_fused_three
import scalar_compact_v3
from rebind_graph import private_rebind

p = hankel_compact.p
cv = p.install_dot_cache(p.install_base_zero(p.install_undo_zeros(
    p.install_child_inverse(p.install_retained_gaps(p.make_converter())))))
cv = middle_fusion.install(cv)
cells = dict(zip(cv.__code__.co_freevars, cv.__closure__))
short = cells['core'].cell_contents.__globals__
scope = short['old'].direct_post.__globals__
# The lifetime wrapper owns a small closure, so take the solver's actual globals.
scope = short['old'].look_solve.__globals__
scope['BLOCK_LEVELS'] = frozenset((14,))
scope['block_solve'] = p.clone(blocked_three_noscratch.look_solve, scope)
source = inspect.getsource(root_fused_three.look_solve)
needle = 'return ordinary_solve(b,f,g,payloads,H,parent,reverse,phase)'
assert source.count(needle) == 1
source = source.replace(needle, 'return block_solve(b,f,g,payloads,H,parent,reverse,phase)')
exec(compile(source, __file__, 'exec'), scope)
short['old'].look_solve = scope['look_solve']
cv = hankel_compact.install(cv)
cv = private_rebind(cv, p.base.replacements, p.ROOT)
decode = scalar_compact_v3.make_decoder(converter=cv, reference_decode=p.decode)
