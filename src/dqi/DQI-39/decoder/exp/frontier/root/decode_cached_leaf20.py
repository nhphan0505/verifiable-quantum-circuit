"""Use the supplied narrow isotopy inverse in the new flag-free caches."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decode_flagfree_cached as cache
from exp.inverse_search import inverse20_iso as iso


def install(entry):
    replacements = cache.replacement_ids(entry, cache.inverse6_initialized_nine,
                                         iso.inverse6_xor20)
    assert replacements
    scope = dict(entry.__globals__)
    for name in ('extraction', 'synthesize'):
        scope[name] = cache.xs.private_rebind(scope[name], replacements)
    return cache.xs.clone(entry, scope)


decode = install(cache.decode)
