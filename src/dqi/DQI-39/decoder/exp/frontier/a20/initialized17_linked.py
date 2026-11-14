"""Initialized inverse with exact cubic repairs on linked (inverse(x),x)."""
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/'a17')]
import initialized17_factored as original

DATA=json.loads((HERE/'final_cubic_search.json').read_text())['found']


def rank(rows):
    basis={}
    for row in rows:
        while row:
            p=row.bit_length()-1
            if p in basis:row^=basis[p]
            else:basis[p]=row;break
    return len(basis)


def complete(rows):
    rows=list(rows)
    assert rank(rows)==len(rows)
    for i in range(12):
        if rank(rows+[1<<i])>len(rows):rows.append(1<<i)
    assert len(rows)==12
    return rows


def inverse_rows(rows):
    work=[row|(1<<(12+i)) for i,row in enumerate(rows)]
    for i in range(12):
        j=next(j for j in range(i,12) if work[j]>>i&1)
        work[i],work[j]=work[j],work[i]
        for j in range(12):
            if j!=i and work[j]>>i&1:work[j]^=work[i]
    assert all((row&4095)==1<<i for i,row in enumerate(work))
    return [row>>12 for row in work]


def columns(rows):
    return [sum(((row>>j)&1)<<i for i,row in enumerate(rows)) for j in range(12)]


MAPS={name:(columns(complete(plan['triple'])),
            columns(inverse_rows(complete(plan['triple']))))
      for name,plan in DATA.items()}


def pay_final_linked(b,live,debts):
    """Pay both late characters on all64 linked inputs and all four masks."""
    expected={("final_triple",0,1,k) for k in (2,3,4,5,8,9,10)}
    expected.update(("final_triple",0,2,k) for k in (3,4,5))
    assert set(debts)==expected
    late=debts[("final_triple",0,1,2)]
    earlier=debts[("final_triple",0,1,5)]
    b.cx(late,earlier)
    choices=b.alloc_bits(3);b.bit_store(choices,False)
    late_only,early_only,both=choices
    b.push_condition(late)
    b.cx(earlier,both)
    b.pop_condition()
    b.cx(late,late_only);b.cx(both,late_only)
    b.cx(earlier,early_only);b.cx(both,early_only)
    for name,mask in [('late',late_only),('early',early_only),('xor',both)]:
        forward,back=MAPS[name]
        b.push_condition(mask)
        original.ar.linear_inplace(b,live,forward)
        b.ccz(live[0],live[1],live[2])
        original.ar.linear_inplace(b,live,back)
        b.pop_condition()
        for term in DATA[name]['quadratic']:
            if term[0]=='constant':b.z(mask)
            elif term[0]=='linear':b.cz(live[term[1]],mask)
            else:
                assert term[0]=='pair'
                b.ccz(live[term[1]],live[term[2]],mask)
    b.free(choices)


_run=original.combo.xsub.clone(original.inverse6_initialized17_factored,
    dict(original.inverse6_initialized17_factored.__globals__,
         pay_final_cubics_factored=pay_final_linked))


def inverse6_initialized17_linked(b,x):
    return _run(b,x)


def install(entry):
    replacements={id(fn):inverse6_initialized17_linked
                  for fn in original.functions(entry)
                  if fn.__code__ is original.old.inverse6_initialized19.__code__}
    assert replacements
    scope=dict(entry.__globals__)
    for name in ('extraction','synthesize'):
        scope[name]=original.combo.xsub.private_rebind(scope[name],replacements)
    result=original.combo.xsub.clone(entry,scope)
    for name in ('convert_safe','baseline'):
        assert result.__globals__[name] is entry.__globals__[name]
    return result
