"""Use the structurally constant outer implicit leader in its zero alias.

After the last synthesis fold, border is identically 1 by the prefix
recurrence; before the first reverse fold it is reclaimed as that constant.
"""
from pathlib import Path
from types import SimpleNamespace
import inspect,sys
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'root')]
import decode_root_v8
from decode_low_crt import combo


def constant_alias(b,F,targets,coeffs):
    for word,co in zip(targets,coeffs):
        for j in range(12):
            if co>>j&1:b.cx(F,word[j])


def install(entry):
    synth=entry.__globals__['synthesize'];folds=synth.__globals__['folds']
    sg=dict(folds.sg);ug=dict(folds.ug)
    for table,key in((sg,'absorb_even'),(ug,'absorb_even')):
        fn=table[key];source=inspect.getsource(fn)
        if table is sg:
            before='  old.controlled_linear_xor(b,F,r,full[-3:-1],[kap,1])'
            after='''  if k==33 and c==0:constant_alias(b,F,full[-3:-1],[kap,1])
  else:old.controlled_linear_xor(b,F,r,full[-3:-1],[kap,1])'''
        else:
            before='    old.controlled_linear_xor(b,F,r,head,co)'
            after='''    if k==33 and c==0:constant_alias(b,F,head,co)
    else:old.controlled_linear_xor(b,F,r,head,co)'''
        assert source.count(before)==1,(key,source)
        source=source.replace(before,after)
        scope=dict(fn.__globals__,constant_alias=constant_alias)
        exec(compile(source,__file__,'exec'),scope)
        table[key]=scope[fn.__name__]
    fs=SimpleNamespace(**dict(vars(folds),sg=sg,ug=ug))
    sy=combo.xsub.clone(synth,dict(synth.__globals__,folds=fs))
    result=combo.xsub.clone(entry,dict(entry.__globals__,synthesize=sy))
    assert result.__globals__['convert_safe'] is entry.__globals__['convert_safe']
    assert result.__globals__['baseline'] is entry.__globals__['baseline']
    return result


decode=install(decode_root_v8.decode)
