# Copyright 2026 Syed Asad Ali
# SPDX-License-Identifier: Apache-2.0
"""70-T field inverse and quotient phases using an invariant norm difference."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import sys
import kickmix as km
import numpy as np
from tower_inverse import (quadratic_basis,apply_inplace_linear,init_norm,erase_norm,
                           init_inverse,init_inverse_three,erase_inverse_three,
                           xor_product,erase_product,phase_product,kernel)
from lowspace_field import partial_inverse_product_terms
from quantum_reciprocal import bit_matrix

from scalar_inverse_phase import phase_inverse_six


def difference_cache(builder,norm):
    """Return n+1/n, erasing the temporary21T inverse's scaffolds."""
    assert len(norm)==6
    cached=builder.alloc_qubits(6)
    scaffold=init_inverse(builder,norm,cached)
    assert scaffold['child'] is None
    erase_inverse_three(builder,scaffold['norm'],scaffold['inverse_norm'])
    builder.free(scaffold['inverse_norm'])
    info=quadratic_basis(6)
    apply_inplace_linear(builder,norm,info['to_tower'])
    erase_norm(builder,norm[:3],norm[3:],scaffold['norm'],info['delta'])
    builder.free(scaffold['norm'])
    apply_inplace_linear(builder,norm,info['from_tower'])
    builder.cx(norm,cached)
    return cached

def erase_difference_cache(builder,current_norm,cached):
    """The same difference is valid at either n or1/n, includingzero."""
    info=quadratic_basis(6)
    apply_inplace_linear(builder,cached,info['to_tower'])
    mask=builder.alloc_bits(6);builder.hmr(cached,mask);builder.free(cached)
    apply_inplace_linear(builder,current_norm,info['to_tower'])
    builder.cz(mask,current_norm)
    apply_inplace_linear(builder,current_norm,info['from_tower'])
    phase_inverse_six(builder,current_norm,mask)
    builder.free(mask)

def invert_twelve(builder,source):
    assert len(source)==12
    info=quadratic_basis(12)
    apply_inplace_linear(builder,source,info['to_tower'])
    left,right=source[:6],source[6:]
    norm=init_norm(builder,left,right,info['delta'])
    cached=difference_cache(builder,norm)
    builder.cx(cached,norm)
    temporary=builder.alloc_qubits(6);masks=[]
    for word in (left,right):
        xor_product(builder,word,norm,temporary)
        builder.swap(word,temporary)
        mask=builder.alloc_bits(6);builder.hmr(temporary,mask);masks.append(mask)
    builder.free(temporary)
    builder.cx(right,left)
    builder.cx(cached,norm)
    builder.cx(right,left)
    phase_product(builder,left,norm,masks[0],kernel(6))
    builder.cx(right,left)
    phase_product(builder,right,norm,masks[1],kernel(6))
    for mask in masks:builder.free(mask)
    builder.cx(cached,norm)
    erase_difference_cache(builder,norm,cached)
    erase_norm(builder,left,right,norm,info['delta']);builder.free(norm)
    apply_inplace_linear(builder,source,info['from_tower'])

def phase_quotients(builder,source,targets):
    assert len(source)==12
    info=quadratic_basis(12)
    apply_inplace_linear(builder,source,info['to_tower'])
    left,right=source[:6],source[6:]
    norm=init_norm(builder,left,right,info['delta'])
    cached=difference_cache(builder,norm);builder.cx(cached,norm)
    temporary=builder.alloc_qubits(6)
    for component,word in enumerate((left,right)):
        if component==0:builder.cx(right,left)
        xor_product(builder,word,norm,temporary)
        for value,mask,power in targets:
            phase_product(builder,value,temporary,mask,partial_inverse_product_terms(component,power))
        erase_product(builder,word,norm,temporary)
        if component==0:builder.cx(right,left)
    builder.free(temporary)
    builder.cx(cached,norm)
    erase_difference_cache(builder,norm,cached)
    erase_norm(builder,left,right,norm,info['delta']);builder.free(norm)
    apply_inplace_linear(builder,source,info['from_tower'])

def build_inverse():
    builder=km.CircuitBuilder();source=builder.create_quantum_register(12,'value')
    mask=builder.create_classical_register(12,'inverse_phase_probe')
    invert_twelve(builder,source);builder.cz(mask,source);invert_twelve(builder,source)
    return builder.finish_circuit(),source,mask

def build_phase():
    builder=km.CircuitBuilder();source=builder.create_quantum_register(12,'denominator')
    values=[builder.create_quantum_register(12,f'numerator_{j}') for j in range(3)]
    masks=[builder.create_classical_register(12,f'mask_{j}') for j in range(3)]
    phase_quotients(builder,source,list(zip(values,masks,(1,2,4))))
    return builder.finish_circuit(),source,values,masks


