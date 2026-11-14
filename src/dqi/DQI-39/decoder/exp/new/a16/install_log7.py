"""Install the exact GF8 key scale in its two supplied arithmetic owners.

The entry graph is already isolated. No unrelated same-named function is
edited: filename, function name, arity and the absence of closure cells
are checked for each original owner. Every changed owner is recorded.
"""
import logscale7


def scale6_log_key(b,x,key,inverse=False):
    _a16_log7.scale_many(b,[x[:3],x[3:]],key,inverse)


def inverse6_unitary29(b,x):
    to,frm,kval=ar.tower(6)
    ar.linear_inplace(b,x,to)
    E=b.alloc_qubits(3)
    norm_xor_noscratch(b,x,E,kval)
    permutation3(b,E,'log_inverse')
    b.cx(x[3:],x[:3])
    _a16_log7.scale_many(b,[x[:3],x[3:]],E)
    permutation3(b,E,'log',reverse=True)
    ar._erase_norm(b,x,E,kval)
    b.free(E)
    ar.linear_inplace(b,x,frm)


def install(entry):
    import walk_bound as walk
    replacements={
        ('exp/r-main/narrow240/retimed.py','scale6_log_key'):(scale6_log_key,4),
        ('exp/r-main/narrow240/streamed.py','inverse6_unitary29'):(inverse6_unitary29,2),
    }
    changed=[]
    for fn in walk.functions(entry):
        code=fn.__code__
        for (suffix,name),(replacement,arity) in replacements.items():
            if fn.__name__!=name or not code.co_filename.replace('\\', '/').endswith(suffix):continue
            assert code.co_argcount==arity and not code.co_freevars and fn.__closure__ is None
            # These scopes already own their norm generation, source
            # erasure, field representation and GF8 log permutations.
            if name=='inverse6_unitary29':
                assert {'ar','norm_xor_noscratch','permutation3'}<=set(fn.__globals__)
            fn.__globals__['_a16_log7']=logscale7
            changed.append(dict(filename=code.co_filename,line=code.co_firstlineno,
                                name=name,globals_id=id(fn.__globals__)))
            fn.__code__=replacement.__code__
            break
    return changed
