"""Release unused references in completed private Python loader scopes.

This is a host-memory optimization, not a circuit optimization.  It must run
after every decoder installer has finished.  Actual imported module namespaces
are never changed.  Every live function sharing a private globals dictionary
contributes all its global names (including nested code) to the retained set.
Scopes with dynamic globals/eval/exec access are left untouched.
"""
from functools import lru_cache
import gc
from pathlib import Path
import sys
from types import CodeType, FunctionType, ModuleType

ROOT = str(Path(__file__).resolve().parents[3]) + '/'


@lru_cache(None)
def code_names(code):
    names = set(code.co_names)
    strings = set()
    for value in code.co_consts:
        if isinstance(value, CodeType):
            nn, ss = code_names(value)
            names.update(nn)
            strings.update(ss)
        elif isinstance(value, str) and value.isidentifier():
            strings.add(value)
    return frozenset(names), frozenset(strings)


def prune():
    """Drop only names no surviving function can resolve from a private scope.

    Return diagnostic counts.  No builder, operation, input, measurement, or
    simulated shot is examined.  Globally protect literal keys used by any
    explicit __globals__ accessor, for conservative cross-scope inspection.
    """
    gc.collect()
    objects = gc.get_objects()
    module_scopes = {id(vars(m)) for m in objects
                     if isinstance(m, ModuleType)}
    scopes = {}
    protected = set()
    for value in objects:
        if (isinstance(value, FunctionType)
                and value.__code__.co_filename.startswith(ROOT)
                and id(value.__globals__) not in module_scopes):
            scopes.setdefault(id(value.__globals__), [value.__globals__, set(), False])
    for value in objects:
        if not isinstance(value, FunctionType):
            continue
        scope = value.__globals__
        # Dynamic generated code may share an owned scope while its filename
        # is '<string>'. Every such function must contribute its names too.
        if id(scope) not in scopes and not value.__code__.co_filename.startswith(ROOT):
            continue
        names, strings = code_names(value.__code__)
        if '__globals__' in names:
            protected.update(strings)
        if id(scope) not in scopes:
            continue
        row = scopes[id(scope)]
        row[1].update(names)
        row[1].update(strings)
        if names.intersection({'globals', 'eval', 'exec'}):
            row[2] = True
    del objects, value
    removed = 0
    changed = 0
    skipped = 0
    compacted_bytes = 0
    for scope, names, dynamic in scopes.values():
        if dynamic:
            skipped += 1
            continue
        keep = names | protected
        dead = [key for key in scope if isinstance(key, str)
                and key not in keep and not key.startswith('__')]
        for key in dead:
            del scope[key]
        if dead:
            # Deleting dictionary entries does not shrink its hash table.
            # Rebuild the table in the SAME dictionary object: all function
            # __globals__ identities, surviving values, and insertion order
            # are preserved. Only unused host allocation capacity is freed.
            before = sys.getsizeof(scope)
            retained = {key: value for key, value in scope.items()}
            scope.clear()
            scope.update(retained)
            compacted_bytes += before - sys.getsizeof(scope)
            del retained
        removed += len(dead)
        changed += bool(dead)
    # Do not keep any old scope alive through these local references.
    count = len(scopes)
    del scopes
    collected = gc.collect()
    try:
        import ctypes
        ctypes.CDLL(None).malloc_trim(0)
    except (AttributeError, OSError):
        pass
    return dict(private_scopes=count, changed_scopes=changed,
                skipped_dynamic_scopes=skipped, removed_names=removed,
                compacted_dictionary_bytes=compacted_bytes,
                collected=collected)
