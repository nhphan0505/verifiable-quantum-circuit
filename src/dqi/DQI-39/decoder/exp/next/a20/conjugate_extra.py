"""An additional exact186T chart using11 places selected from all17."""
from pathlib import Path
from functools import lru_cache
from types import FunctionType
import json
import conjugate_joint as prior
from eval_blocks_all17 import selected_blocks

DATA=json.loads(Path(__file__).with_name('search_conjugate_all17.json').read_text())
NEW_C=3548
route=DATA['routes'][str(NEW_C)]
frame=dict(DATA['frames'][str(route['c'])])
selected=set(frame['blocks'])
for point in range(17):
    if len(selected)==11:break
    selected.add(point)
INDICES=tuple(sorted(selected))
BLOCKS,TERMS=selected_blocks(INDICES)
frame['blocks']=[INDICES.index(i) for i in frame['blocks']]
_frame=FunctionType(prior.frame_tensor.__wrapped__.__code__,
    dict(prior.frame_tensor.__wrapped__.__globals__,FRAMES={frame['c']:frame},
         blocks=lambda:BLOCKS,tensor99_extension=lambda k:TERMS),'extra_frame_tensor')
frame_tensor=lru_cache(None)(_frame)
_preferred=FunctionType(prior.preferred_tensor.__wrapped__.__code__,
    dict(prior.preferred_tensor.__wrapped__.__globals__,ROUTES={NEW_C:route},
         frame_tensor=frame_tensor),'extra_preferred_tensor')
preferred_tensor=lru_cache(None)(_preferred)

def install(entry):
    import walk_bound
    edits=[];seen=set()
    for fn in walk_bound.functions(entry):
        if not {'joint_tensor','accumulator'}<=set(fn.__code__.co_names):continue
        scope=fn.__globals__
        if id(scope) in seen:continue
        seen.add(id(scope));old=scope['joint_tensor']
        assert len(old(0))==182 and len(old(NEW_C))==192
        assert len(preferred_tensor(NEW_C))==186
        def factory(original):
            @lru_cache(None)
            def choose(c):
                return preferred_tensor(c) if c==NEW_C else original(c)
            return choose
        scope['joint_tensor']=factory(old)
        edits.append(dict(file=fn.__code__.co_filename,line=fn.__code__.co_firstlineno,
                          name=fn.__name__,changed_c=NEW_C,terms_before=192,terms_after=186))
    assert edits
    return edits
