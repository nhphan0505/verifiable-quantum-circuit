"""Pure-query memoization for the supplied graph-copy loader, without a base import."""
from pathlib import Path
from functools import lru_cache
import inspect
import sys


def install():
    root = Path(__file__).resolve().parents[3]
    sys.path[:0] = [str(root / 'playbook/kit'),
                   str(root / 'exp/r-main/narrow240'),
                   str(root / 'research/agents/a01'), str(root)]
    import exact_subs
    import rebind_graph
    # Both supplied graph copiers ask the same pure ownership/code-name
    # questions repeatedly. Caches live inside one copy call, so the root
    # argument and all returned graph topology remain unchanged.
    for module in (exact_subs, rebind_graph):
        if getattr(module, '_query_cache_installed', False):
            continue
        source = inspect.getsource(module.private_rebind)
        for name in ('owned', 'names'):
            needle = '    def ' + name + '('
            assert source.count(needle) == 1
            source = source.replace(needle, '    @lru_cache(None)\n' + needle)
        module.__dict__['lru_cache'] = lru_cache
        exec(compile(source, __file__, 'exec'), module.__dict__)
        module._query_cache_installed = True
