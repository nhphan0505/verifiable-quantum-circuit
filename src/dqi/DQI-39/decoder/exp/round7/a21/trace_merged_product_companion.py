"""Complete narrow reverse stage with one84T normalized trace contraction."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(ROOT/'exp/round7/a18')]
import merged_product_companion as prior
from direct_owned_companion import clone
from classical_trace_merge import phase_pair

merged_multiplier = clone(prior.merged_multiplier,
                          dict(prior.merged_multiplier.__globals__,phase_pair=phase_pair))
finish_factory = clone(prior.finish_factory,
                       dict(prior.finish_factory.__globals__,merged_multiplier=merged_multiplier))
normalize_first = prior.normalize_first
install = clone(prior.install,dict(prior.install.__globals__,finish_factory=finish_factory))
