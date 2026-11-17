"""Exact arithmetic reconstruction of Syed Asad Ali's Fusion Q44 circuit.

See NOTICE.txt. Source uses normalized consumed square root, two six-input
Boolean coefficient codebooks, rounded interpolation, signed seed/product,
balanced division, N27 phase walk, and debt-paying inverse arithmetic.
No original KMB/KMX, external source, gate tape or machine-local cache is read.
"""
import io
import kickmix as km
import coefficient
from arithmetic_prefix import create_prefix,arithmetic_modules
from arithmetic_body import context,forward,component
from lookup import load
from return_path import inverse


def restore_layout(cb,current,original):
    """Restore the logical input permutation, borrowing only clean owners.

    Adapted from Syed Asad Ali's tracked INV-51 layout helper. Keeping this
    small permutation routine here avoids its unused model/data dependency.
    """
    current=list(current)
    assert cb.num_allocated_qubits==22 and len(set(current))==22
    spare=list(cb.alloc_qubits(44-22))
    all_wires=set(current+spare)
    for bit,target in enumerate(original):
        source=current[bit]
        if source==target:continue
        cb.swap(source,target)
        for other in range(bit+1,22):
            if current[other]==target:current[other]=source
        current[bit]=target
    cb.free(km.array(sorted(all_wires-set(original),key=str)))
    assert current==original and cb.num_allocated_qubits==22


def build_circuit():
    native,x,flags=create_prefix()
    cb=coefficient.Builder(native)
    v=x[10:]
    D,H,bridge,pending,_=load(cb,v[6:],'first')
    token,product,first=forward(cb,v[:10],D,H,bridge,flags,x[1:10])
    ar,_,_=context()
    book=component('_inv74_return_codebook','work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/codebook.py')
    norm=inverse(cb,ar,book,token,product,first,pending)
    normal,root=arithmetic_modules()
    root.inverse(cb,norm)
    normal.inverse(cb,norm,flags)
    cb.free(km.array(flags))
    restore_layout(cb,norm,x)
    metadata=[f'APPEND_TO_REGISTER q{i} r0' for i in range(22)]+['REGISTER r0 "x"']
    text='\n'.join(metadata)+'\n'+str(cb.finish_circuit())
    return km.Circuit.from_file(io.BytesIO(text.encode('utf8')),format='kmx')
