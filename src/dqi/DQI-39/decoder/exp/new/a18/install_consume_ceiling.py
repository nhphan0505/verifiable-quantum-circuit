"""Extend the existing Q900 choice to one construction-only ceiling closure.

This is a narrow arithmetic selector experiment, not a whole decoder result.
The existing producer and its norm-erasure contract are unchanged.
"""

def install(entry,ceiling=900):
    import walk_bound as walk
    edits=[]
    seen=set()
    for fn in walk.functions(entry):
        code=fn.__code__
        if (fn.__name__!='consume' or code.co_argcount!=2 or
            not code.co_filename.endswith('/exp/frontier/a12/decode_companion_preserve.py')):
            continue
        cells=dict(zip(code.co_freevars,fn.__closure__ or ()))
        assert {'inverse','ceiling'}<=set(cells)
        inv=cells['inverse'].cell_contents
        assert inv.__name__=='inverse12_keep_norm'
        assert inv.__code__.co_filename.endswith('/exp/frontier/a12/decode_trailing_normcache.py')
        cell=cells['ceiling']
        if id(cell) in seen:continue
        seen.add(id(cell))
        before=cell.cell_contents
        assert before in (889,ceiling)
        if before!=ceiling:
            cell.cell_contents=ceiling
            edits.append(dict(filename=code.co_filename,function=fn.__name__,before=before,after=ceiling))
    return edits
