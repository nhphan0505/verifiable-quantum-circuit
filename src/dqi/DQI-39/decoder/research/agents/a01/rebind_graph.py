"""Private rebinding for recursive function/closure graphs.

Only Python construction changes: no circuit operation or simulator state is
used. New closure cells are memoized with the function before their values are
copied, so mutually recursive kernel schedules retain the same topology.
"""
from contextlib import contextmanager
from pathlib import Path
from types import CellType, CodeType, FunctionType, ModuleType, SimpleNamespace


def private_rebind(entry, replacements, root):
    root = Path(root).resolve()
    memo, scopes, processed = {}, {}, set()

    def owned(filename):
        try:
            return Path(filename).resolve().is_relative_to(root)
        except (TypeError, ValueError):
            return False

    def names(code):
        result = set(code.co_names)
        for value in code.co_consts:
            if isinstance(value, CodeType):
                result.update(names(value))
        return result

    def copy(value):
        key = id(value)
        if key in replacements:
            return replacements[key]
        if key in memo:
            return memo[key]
        if isinstance(value, FunctionType) and owned(value.__code__.co_filename):
            old = value.__globals__
            scope = scopes.setdefault(id(old), dict(old))
            closure = None if value.__closure__ is None else tuple(
                CellType() for _ in value.__closure__)
            out = FunctionType(value.__code__, scope, value.__name__,
                               value.__defaults__, closure)
            memo[key] = out
            out.__kwdefaults__ = value.__kwdefaults__
            out.__annotations__ = dict(value.__annotations__)
            if closure is not None:
                for target, original in zip(closure, value.__closure__):
                    try:
                        contents = original.cell_contents
                    except ValueError:
                        continue
                    target.cell_contents = copy(contents)
            for name in names(value.__code__):
                token = id(old), name
                if token not in processed and name in old:
                    processed.add(token)
                    scope[name] = copy(old[name])
            return out
        if isinstance(value, FunctionType) and getattr(value, '__wrapped__', None) is not None:
            wrapped = value.__wrapped__
            if isinstance(wrapped, FunctionType) and owned(wrapped.__code__.co_filename):
                out = contextmanager(copy(wrapped))
                memo[key] = out
                return out
        if isinstance(value, SimpleNamespace) or (
                isinstance(value, ModuleType) and owned(getattr(value, '__file__', None))):
            out = ModuleType(value.__name__) if isinstance(value, ModuleType) else SimpleNamespace()
            memo[key] = out
            for name, item in vars(value).items():
                if name != '__builtins__':
                    setattr(out, name, copy(item))
            return out
        if isinstance(value, dict):
            out = {}
            memo[key] = out
            out.update((k, copy(v)) for k, v in value.items())
            return out
        if isinstance(value, (list, tuple)) and any(
                isinstance(v, (FunctionType, SimpleNamespace, dict)) for v in value):
            out = [copy(v) for v in value]
            out = tuple(out) if isinstance(value, tuple) else out
            memo[key] = out
            return out
        return value

    return copy(entry)
