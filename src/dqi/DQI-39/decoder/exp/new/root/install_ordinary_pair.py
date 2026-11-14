"""Bind paired ordinary nodes to the actual extraction owners.

The original owners are retained so an experimental process can compare two
factories without accidentally taking geometry from a previous replacement.
This is construction only; no builder or simulated input is inspected.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'exp/new/a01'))
import walk_bound

ORIGINALS = {}


def capture(entry):
    found = {}
    for fn in walk_bound.functions(entry.__globals__['extraction']):
        if 'external_ordinary_node' not in fn.__code__.co_names:
            continue
        scope = fn.__globals__
        found[id(scope)] = scope
    assert found
    for key, scope in found.items():
        if key not in ORIGINALS:
            original = scope['external_ordinary_node']
            geometry = {name: original.__globals__[name]
                        for name in ('groups', 'ks', 'combine', 'jet_reverse')}
            ORIGINALS[key] = (scope, original, geometry)
    return found


def install(entry, factory):
    found = capture(entry)
    for key, scope in found.items():
        old_scope, original, geometry = ORIGINALS[key]
        assert old_scope is scope
        scope['external_ordinary_node'] = factory(geometry)
    return len(found)
