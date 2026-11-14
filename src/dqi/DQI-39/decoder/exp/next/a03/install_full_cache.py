"""Retain a complete initialized inverse and its zero bit in one forward frame.

A fixed frame schedule; all values remain coherent. The retained copy becomes
that frame's second inverse output and is retired by the original consumer.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'exp/new/a01'))
import walk_bound


def install(entry,levels=(8,)):
    levels=frozenset(levels)
    edits=[];seen=set();count={'first':0,'second':0}
    for fn in walk_bound.functions(entry):
        if not fn.__code__.co_filename.endswith('/research/agents/a12/forward_norm_cache.py'):continue
        cells=dict(zip(fn.__code__.co_freevars,fn.__closure__ or ()))
        if fn.__name__=='inverse_zero' and {'original_inverse','frames','levels'}<=set(cells):
            cell=cells['original_inverse']
            if id(cell) in seen:continue
            seen.add(id(cell))
            assert not (levels & cells['levels'].cell_contents), 'Disable old partial cache at full-cache levels first'
            original=cell.cell_contents;frames=cells['frames'].cell_contents
            def inverse_zero(b,x,_original=original,_frames=frames):
                if not _frames:return _original(b,x)
                m,phase,g,reverse=_frames[-1]
                if reverse or m not in levels or list(x)!=list(g[-1]):return _original(b,x)
                cache=phase.setdefault('_a03_forward_full_inverse',{})
                if m in cache:
                    count['second']+=1
                    return cache.pop(m)
                ai,Z=_original(b,x)
                saved=b.alloc_qubits(len(ai));flag=b.alloc_qubits(1)[0]
                b.cx(ai,saved);b.cx(Z,flag)
                cache[m]=(saved,flag)
                count['first']+=1
                return ai,Z
            cell.cell_contents=inverse_zero
            edits.append(dict(owner=fn.__name__,kind='full_inverse',levels=sorted(levels)))
        elif fn.__name__=='solve' and {'original_solve','frames'}<=set(cells):
            cell=cells['original_solve']
            if id(cell) in seen:continue
            seen.add(id(cell));original=cell.cell_contents
            def solve(b,f,g,payloads,H=None,parent=None,reverse=False,phase=None,_original=original):
                result=_original(b,f,g,payloads,H,parent,reverse,phase)
                if not reverse and len(f)-1 in levels:
                    assert len(f)-1 not in phase.get('_a03_forward_full_inverse',{}), 'Unconsumed full inverse cache'
                return result
            cell.cell_contents=solve
            edits.append(dict(owner=fn.__name__,kind='finish_check',levels=sorted(levels)))
    assert any(e['kind']=='full_inverse' for e in edits)
    return edits,count
