"""Change only public converter norm-retention levels, with original closures.

The source functions already implement exact creation/use/retirement of their
cache. This installer makes a fixed circuit schedule and never reads quantum
values, shots, seeds, or measurement outcomes.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'exp/new/a01'))
import walk_bound


def install(entry,forward_levels=(11,8,5),reverse_kinds=None):
    if reverse_kinds is None:reverse_kinds={11:'t6',5:'t6'}
    fs=frozenset(forward_levels);rs=frozenset(reverse_kinds)
    assert all(2<=m<=16 for m in fs|rs)
    assert all(v in ('t6','w3') for v in reverse_kinds.values())
    edits=[];seen=set()
    for fn in walk_bound.functions(entry):
        file=fn.__code__.co_filename.replace('\\', '/')
        cells=dict(zip(fn.__code__.co_freevars,fn.__closure__ or ()))
        if file.endswith('/research/agents/a12/forward_norm_cache.py'):
            if 'levels' in cells and id(cells['levels']) not in seen:
                cell=cells['levels'];seen.add(id(cell))
                before=cell.cell_contents
                assert isinstance(before,frozenset)
                cell.cell_contents=fs
                edits.append(dict(kind='forward_levels',before=sorted(before),after=sorted(fs)))
        elif file.endswith('/research/agents/a14/reverse_caches.py'):
            if 'levels' in cells and id(cells['levels']) not in seen:
                cell=cells['levels'];seen.add(id(cell))
                before=cell.cell_contents
                assert isinstance(before,frozenset)
                cell.cell_contents=rs
                edits.append(dict(kind='reverse_levels',before=sorted(before),after=sorted(rs)))
            if 'kinds' in cells and id(cells['kinds']) not in seen:
                cell=cells['kinds'];seen.add(id(cell))
                before=cell.cell_contents
                assert isinstance(before,dict)
                cell.cell_contents=dict(reverse_kinds)
                edits.append(dict(kind='reverse_kinds',before=before,after=dict(reverse_kinds)))
    assert any(e['kind']=='forward_levels' for e in edits), 'Active forward cache owner not found'
    assert any(e['kind']=='reverse_kinds' for e in edits), 'Active reverse cache owner not found'
    return edits
