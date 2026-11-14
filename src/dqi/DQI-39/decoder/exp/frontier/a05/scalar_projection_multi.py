"""Whole-block projection variants and composition-preserving installer."""
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys
from types import FunctionType, ModuleType, SimpleNamespace, CodeType
import scalar_projection as single
from scalar_projection import *


def independent(values):
    pivots = {}
    result = []
    for original in values:
        value = original
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                result.append(original)
                break
    return tuple(result)


def span_of(basis):
    span = {0}
    for value in basis:
        span |= {v ^ value for v in span}
    return frozenset(span)


@lru_cache(None)
def projection(k):
    if k <= 4:
        return single.projection(k)
    terms = tensor99_extension(K)
    blocks = [independent([w for _, w in terms[i:i+9]]) for i in range(0, 99, 9)]
    # Complete GF16 output blocks first, then choose every subspace of one
    # further block. This is a concrete finite family, not a rank lower bound.
    whole, rest = divmod(k, 4)
    options = {}
    for indices in combinations(range(len(blocks)), whole):
        basis = independent([v for i in indices for v in blocks[i]])
        if len(basis) != whole * 4:
            continue
        if not rest:
            options.setdefault(span_of(basis), basis)
            continue
        for j, block in enumerate(blocks):
            if j in indices:
                continue
            states = {span_of(basis): basis}
            for _ in range(rest):
                grown = {}
                for span, old in states.items():
                    for v in span_of(block):
                        if v in span:
                            continue
                        bigger = span | {x ^ v for x in span}
                        grown.setdefault(bigger, old + (v,))
                states = grown
            options.update(states)
    span, basis = max(options.items(), key=lambda x: (sum(v in x[0] for _, v in terms), x[1]))
    columns = independent(list(basis) + [1 << i for i in range(24)])
    to = tuple(ar.inverse_columns(columns))
    projected = tuple((m, m, ar.apply(to, w) & ~((1 << k) - 1)) for m, w in terms)
    return to, columns, tuple(t for t in projected if t[2])


def functions(entry):
    seen = set()
    out = []
    def names(code):
        result = set(code.co_names)
        for c in code.co_consts:
            if isinstance(c, CodeType):
                result.update(names(c))
        return result
    def visit(value):
        if id(value) in seen:
            return
        seen.add(id(value))
        if isinstance(value, FunctionType):
            out.append(value)
            for name in names(value.__code__):
                if name in value.__globals__:
                    visit(value.__globals__[name])
            for cell in value.__closure__ or ():
                visit(cell.cell_contents)
        elif isinstance(value, (ModuleType, SimpleNamespace)):
            path = getattr(value, '__file__', None)
            if path is None or str(KIT_ROOT) in str(path):
                for item in vars(value).values():
                    visit(item)
        elif isinstance(value, dict):
            for item in value.values():
                visit(item)
        elif isinstance(value, (tuple, list)):
            for item in value:
                visit(item)
    visit(entry)
    return out


def install(entry, cache_by_gi):
    copy = combo.xsub.clone(copy_first_projection, dict(copy_first_projection.__globals__, projection=projection))
    erase = combo.xsub.clone(erase_third_step, dict(erase_third_step.__globals__, projection=projection))
    # Preserve every already-installed arithmetic descendant of each matched
    # full_core_phase. Only these two new routines and the schedule are new.
    replacements = {}
    original_extraction = entry.__globals__['extraction']
    for function in functions(original_extraction):
        if function.__code__ is not ret.full_core_phase.__code__:
            continue
        scope = dict(function.__globals__,
                     CACHE_BY_HEADS={2 * gi: k for gi, k in cache_by_gi.items()},
                     copy_first_projection=copy, erase_third_step=erase,
                     scalar_erase_second24=scalar_erase_second24)
        replacements[id(function)] = combo.xsub.clone(full_core_phase, scope)
    assert replacements
    scope = dict(entry.__globals__, extraction=combo.xsub.private_rebind(original_extraction, replacements))
    return combo.xsub.clone(entry, scope)
