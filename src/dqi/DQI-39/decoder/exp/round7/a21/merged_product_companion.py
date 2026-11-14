"""Complete early-retirement return with one common cubic product phase."""
from pathlib import Path
import inspect
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(ROOT/'exp/round7/a18')]
import direct_ratio_fused_companion as prior
import early_virtual_product_companion as virtual
from direct_owned_companion import clone
from owned_fused_companion import finish_scope
from classical_mask_merge import phase_pair

source = inspect.getsource(virtual.multiply_pair_and_restore)
old = 'for x,m in zip(targets,masks):phase_three_factor(b,x,C,u,m);b.free(m)'
assert source.count(old) == 1
source = source.replace(old, 'phase_pair(b,targets,C,u,masks,phase_three_factor)\n    for m in masks:b.free(m)')
scope = dict(virtual.multiply_pair_and_restore.__globals__, phase_pair=phase_pair)
exec(compile(source, __file__, 'exec'), scope)
merged_multiplier = scope['multiply_pair_and_restore']


def finish_factory(reference, node_scope):
    owned, owner = finish_scope(node_scope['finish_fused'])
    helpers = {name: owned[name] for name in
               ('ar','merged_chart','scale_defer','inverse_stream_noscratch',
                'linear_inverse_character','phase_inverse36_pivot') if name in owned}
    ratio = clone(prior.ratio_divide, dict(prior.ratio_divide.__globals__, **helpers))
    mul = clone(merged_multiplier, dict(merged_multiplier.__globals__, **helpers))
    factory = clone(prior.plain_factory, dict(prior.plain_factory.__globals__,
                    **helpers, ratio_divide=ratio, multiply_pair_and_restore=mul))
    return factory(reference, node_scope)


normalize_first = prior.normalize_first
install = clone(prior.install, dict(prior.install.__globals__, finish_factory=finish_factory))
