"""Three further192-to189 chart gains, using alternative trace-one generators."""
from pathlib import Path
from functools import lru_cache
import json

DATA=json.loads(Path(__file__).with_name('joint_mixed_extra_tensors.json').read_text())
TERMS={int(c):tuple(tuple(t) for t in terms) for c,terms in DATA['terms'].items()}

def preferred_tensor(c):return TERMS.get(c)

def install(entry):
    import walk_bound
    edits=[];seen=set()
    for fn in walk_bound.functions(entry):
        if not {'joint_tensor','accumulator'}<=set(fn.__code__.co_names):continue
        scope=fn.__globals__
        if id(scope) in seen:continue
        seen.add(id(scope));old=scope['joint_tensor']
        changes={c:(len(old(c)),len(ts)) for c,ts in TERMS.items()}
        assert all(before==192 and after==189 for before,after in changes.values()),changes
        def factory(original):
            @lru_cache(None)
            def choose(c):return TERMS[c] if c in TERMS else original(c)
            return choose
        scope['joint_tensor']=factory(old)
        edits.append(dict(file=fn.__code__.co_filename,line=fn.__code__.co_firstlineno,
                          name=fn.__name__,charts=changes))
    assert edits,'Actual joint_tensor/accumulator owner not found'
    return edits
