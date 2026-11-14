"""Enumerate decoder call graphs without following sys.modules."""
from pathlib import Path
from functools import lru_cache
from types import FunctionType,ModuleType,SimpleNamespace,CodeType
ROOT=Path(__file__).resolve().parents[3]


@lru_cache(None)
def owned(filename):
    try:return Path(filename).resolve().is_relative_to(ROOT)
    except (TypeError,ValueError):return False


@lru_cache(None)
def names(code):
    result=set(code.co_names)
    for value in code.co_consts:
        if isinstance(value,CodeType):result.update(names(value))
    return result


def functions(entry):
    seen=set();out=[]
    def visit(value):
        if id(value) in seen:return
        seen.add(id(value))
        if isinstance(value,FunctionType):
            out.append(value)
            for name in names(value.__code__):
                if name in value.__globals__:visit(value.__globals__[name])
            for cell in value.__closure__ or ():visit(cell.cell_contents)
        elif isinstance(value,ModuleType):
            if owned(getattr(value,'__file__',None)):
                for key,item in vars(value).items():
                    if key!='__builtins__':visit(item)
        elif isinstance(value,SimpleNamespace):
            filename=getattr(value,'__file__',None)
            if filename is None or owned(filename):
                for key,item in vars(value).items():
                    if key!='__builtins__':visit(item)
        elif isinstance(value,dict):
            for key,item in value.items():
                if key!='__builtins__':visit(item)
        elif isinstance(value,(list,tuple)):
            for item in value:visit(item)
    visit(entry)
    return out
