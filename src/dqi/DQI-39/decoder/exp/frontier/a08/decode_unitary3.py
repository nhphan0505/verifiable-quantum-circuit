"""Whole-decoder control: exact in-place GF8 inversion in scalar streams."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'exp/r-main/narrow240'),str(HERE.parent/'a03')]
import decode_combo as combo
from jet_norm6 import replacement_ids
from exp.noscratch import schedules
from exp.arithmetic import field as ar


def transposition_layout(a,c):
    difference=a^c
    orthogonal=[v for v in range(1,8) if not (v&difference).bit_count()%2]
    rows=[orthogonal[0],next(v for v in orthogonal if v!=orthogonal[0]),
          next(v for v in range(1,8) if (v&difference).bit_count()%2)]
    columns=[sum(((row>>j)&1)<<i for i,row in enumerate(rows)) for j in range(3)]
    image=ar.apply(columns,a)
    return columns,ar.inverse_columns(columns),[i for i in (0,1) if not (image>>i)&1]


TRANSPOSE=[transposition_layout(a,ar.field(3).invert(a)) for a in range(1,8)
           if a<ar.field(3).invert(a)]


def inverse3_inplace(b,x):
    """The three disjoint reciprocal transpositions, with no fresh qubit."""
    for columns,back,negated in TRANSPOSE:
        ar.linear_inplace(b,x,columns)
        for i in negated:b.x(x[i])
        b.ccx(x[0],x[1],x[2])
        for i in reversed(negated):b.x(x[i])
        ar.linear_inplace(b,x,back)


def stream(b,x):
    if len(x)==3:
        inverse3_inplace(b,x)
        mask=b.alloc_bits(3);b.bit_store(mask,False)
        return mask
    return recursive(b,x)


recursive=combo.xsub.clone(schedules.inverse_stream_noscratch,
                         dict(schedules.inverse_stream_noscratch.__globals__,inverse_stream_noscratch=stream))


def install(entry):
    replacements=replacement_ids(entry,schedules.inverse_stream_noscratch,stream)
    assert replacements
    scope=dict(entry.__globals__)
    for name in ('extraction','synthesize'):
        scope[name]=combo.xsub.private_rebind(scope[name],replacements)
    return combo.xsub.clone(entry,scope)


decode=install(combo.decode)
assert decode.__globals__['convert_safe'] is combo.decode.__globals__['convert_safe']
assert decode.__globals__['baseline'] is combo.decode.__globals__['baseline']
