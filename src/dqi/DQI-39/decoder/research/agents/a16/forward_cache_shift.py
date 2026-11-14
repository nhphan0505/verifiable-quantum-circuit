"""Move only the selected forward inverse-norm cache schedule."""
from types import FunctionType

def install(cv, scalar, levels=(8, 5)):
    scope = scalar.scope_of(cv)
    seen = set(); changed = []
    def visit(fn):
        if not isinstance(fn, FunctionType) or id(fn) in seen: return
        seen.add(id(fn))
        cells = dict(zip(fn.__code__.co_freevars, fn.__closure__ or ()))
        if fn.__code__.co_filename.endswith('/a12/forward_norm_cache.py') and 'levels' in cells:
            cells['levels'].cell_contents = frozenset(levels)
            changed.append(fn.__name__)
        for cell in fn.__closure__ or ():
            try: value = cell.cell_contents
            except ValueError: continue
            if isinstance(value, FunctionType): visit(value)
    visit(scope['inverse_zero']); visit(scope['look_solve'])
    assert sorted(changed) == ['inverse_zero', 'solve'], changed
    return cv
