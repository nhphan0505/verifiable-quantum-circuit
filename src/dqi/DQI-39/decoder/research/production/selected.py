"""Selected back half, assembled without displaced intermediate installers.

All arithmetic helpers remain in their frozen research source files. The
private-graph copy between the forward assembly and the reverse additions is
intentional: nested closure dictionaries and their shared caches must retain
the same ownership as the measured composition.
"""
from pathlib import Path
import inspect
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'research/agents' / name)
                for name in ('a12', 'a11', 'r06_joint_top', 'a09',
                             'a08', 'a07', 'a01')]
import hankel_compact
import hankel_cache_even
import joint_cached
import forward_norm_cache
import known_zero_inverse
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
scope = short['old'].look_solve.__globals__
scope['BLOCK_LEVELS'] = frozenset((14,))
scope['block_solve'] = p.clone(blocked_three_noscratch.look_solve, scope)
source = inspect.getsource(root_fused_three.look_solve)
needle = 'return ordinary_solve(b,f,g,payloads,H,parent,reverse,phase)'
assert source.count(needle) == 1
source = source.replace(needle, 'return block_solve(b,f,g,payloads,H,parent,reverse,phase)')
exec(compile(source, __file__, 'exec'), scope)
short['old'].look_solve = scope['look_solve']
cv = hankel_cache_even.install(cv)
cv = joint_cached.install(cv, root_sources=18)
cv = private_rebind(cv, p.base.replacements, p.ROOT)
decode = scalar_compact_v3.make_decoder(converter=cv, reference_decode=p.decode)
forward_norm_cache.install(scalar_compact_v3.converter_of(decode), levels=(11, 5))
known_zero_inverse.install(scalar_compact_v3.converter_of(decode))

sys.path[:0] = [str(ROOT / 'research/agents' / name)
                for name in ('a14', 'r08_weight_handoff', 'a13')]
import reverse_fusion
import reverse_caches
import weight_handoff_v3

decode = private_rebind(decode, {}, p.ROOT)
cv = scalar_compact_v3.converter_of(decode)
scope = scalar_compact_v3.scope_of(cv)
scope['payload_middle'] = p.clone(weight_handoff_v3.payload_middle, scope)
reverse_caches.install(cv)
reverse_fusion.install(cv)

from inverse_character_width import install_decoder
install_decoder(decode)
