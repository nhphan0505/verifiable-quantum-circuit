# Copyright 2026 Syed Asad Ali
# SPDX-License-Identifier: Apache-2.0
"""Normal confluent extraction with one reversible carried scale.

Zero final normalizers require a separate lookahead/terminal controller.
They are deliberately excluded from this component's acceptance claim.
"""
from __future__ import annotations
from functools import cache
import hashlib
import io
import json
from pathlib import Path
import sys
import kickmix as km
import numpy as np
from compact_inverse import compact_inverse_twelve,phase_inverse_twelve
from tower_inverse import apply_inplace_linear,quadratic_basis,rows_from_columns,xor_product
from quantum_reciprocal import bit_matrix,xor_linear
from dual_scale import scale_word,FIELD

def flat(words):return km.array([wire for word in words for wire in word])

@cache
def power_rows(exponent):
    return rows_from_columns([FIELD.pow(1<<bit,exponent) for bit in range(12)])

@cache
def fixed_rows(coefficient):
    assert coefficient
    return rows_from_columns([FIELD.mul(coefficient,1<<bit) for bit in range(12)])

def linear_scale(builder,word,coefficient):
    apply_inplace_linear(builder,word,fixed_rows(coefficient))

def square(builder,word,reverse=False):
    apply_inplace_linear(builder,word,power_rows(1<<11 if reverse else 2))

def erase_inverse_word(builder,scale,inverse,defer=False):
    apply_inplace_linear(builder,inverse,quadratic_basis(12)['to_tower'])
    mask=builder.alloc_bits(12)
    builder.hmr(inverse,mask);builder.free(inverse)
    if defer:return mask
    phase_inverse_twelve(builder,scale,mask)
    builder.free(mask)

def repay_inverse_mask(builder,inverse,mask):
    info=quadratic_basis(12)
    apply_inplace_linear(builder,inverse,info['to_tower'])
    builder.cz(mask,inverse)
    apply_inplace_linear(builder,inverse,info['from_tower'])
    builder.free(mask)

def scale_pair(builder,value,slope,scale,inverse,divide=False):
    temporary=builder.alloc_qubits(12)
    if divide:scale_word(builder,value,inverse,scale,temporary)
    else:scale_word(builder,value,scale,inverse,temporary)
    square(builder,scale);square(builder,inverse)
    if divide:scale_word(builder,slope,inverse,scale,temporary)
    else:scale_word(builder,slope,scale,inverse,temporary)
    square(builder,inverse,True);square(builder,scale,True)
    builder.free(temporary)

def xor_evaluation_product(builder,parameter,node_difference,value,target):
    columns=tuple(FIELD.mul(node_difference,1<<bit) for bit in range(12))
    xor_linear(builder,parameter[1],parameter[0],columns)
    xor_product(builder,parameter[0],value,target)
    xor_linear(builder,parameter[1],parameter[0],columns)

def homogeneous(builder,value,slope,scale,parameter,node_difference,reverse=False):
    p=FIELD.mul(node_difference,node_difference)
    assert p
    if reverse:
        linear_scale(builder,scale,FIELD.invert(p))
        builder.swap(value,scale)
        xor_evaluation_product(builder,parameter,node_difference,value,scale)
        linear_scale(builder,slope,FIELD.invert(p))
        square(builder,value);xor_product(builder,parameter[1],value,slope);square(builder,value,True)
    else:
        square(builder,value);xor_product(builder,parameter[1],value,slope);square(builder,value,True)
        linear_scale(builder,slope,p)
        xor_evaluation_product(builder,parameter,node_difference,value,scale)
        builder.swap(value,scale)
        linear_scale(builder,scale,p)

def emit(builder,jets,scale,reverse=False,keep_inverse=False,initial_inverse=None,deferred_masks=None):
    nodes=len(jets)
    if reverse:
        inverse=initial_inverse if initial_inverse is not None else compact_inverse_twelve(builder,scale)
        if deferred_masks is not None:
            assert len(deferred_masks)==nodes
            repay_inverse_mask(builder,inverse,deferred_masks[-1])
        for i in reversed(range(nodes)):
            u,v=jets[i]
            scale_pair(builder,u,v,scale,inverse)
            erase_inverse_word(builder,scale,inverse)
            builder.swap(u,scale)
            for j in reversed(range(i)):homogeneous(builder,u,v,scale,jets[j],i^j,True)
            if i:
                inverse=compact_inverse_twelve(builder,scale)
                if deferred_masks is not None:repay_inverse_mask(builder,inverse,deferred_masks[i-1])
                scale_pair(builder,u,v,scale,inverse,True)
        return
    inverse=None
    for i,(u,v) in enumerate(jets):
        if i:
            scale_pair(builder,u,v,scale,inverse)
            mask=erase_inverse_word(builder,scale,inverse,defer=deferred_masks is not None)
            if deferred_masks is not None:deferred_masks.append(mask)
        for j in range(i):homogeneous(builder,u,v,scale,jets[j],i^j)
        builder.swap(u,scale)
        inverse=compact_inverse_twelve(builder,scale)
        scale_pair(builder,u,v,scale,inverse,True)
    if keep_inverse:return inverse
    mask=erase_inverse_word(builder,scale,inverse,defer=deferred_masks is not None)
    if deferred_masks is not None:deferred_masks.append(mask)

def build(nodes):
    builder=km.CircuitBuilder()
    jets=[(builder.create_quantum_register(12,f'value_{i}'),
           builder.create_quantum_register(12,f'derivative_{i}')) for i in range(nodes)]
    scale=builder.alloc_qubits(12);builder.x(scale[0])
    mask=builder.create_classical_register(24*nodes+12,'parameters_and_scale_probe')
    emit(builder,jets,scale)
    builder.cz(mask,flat([word for jet in jets for word in jet]+[scale]))
    emit(builder,jets,scale,True)
    builder.x(scale[0]);builder.free(scale)
    return builder.finish_circuit(),jets,mask

def source_from_parameters(parameters):
    """Invert the projective maps algebraically, rejecting an initial pole."""
    inputs=[]
    for i,(a,b) in enumerate(parameters):
        N,D,W=1,int(a),int(b)
        for j in reversed(range(i)):
            point=i^j;p=FIELD.mul(point,point)
            P=int(parameters[j][0])^FIELD.mul(point,int(parameters[j][1]))
            oldN=FIELD.mul(D,FIELD.invert(p))
            N,D=oldN,N^FIELD.mul(P,oldN)
            W=FIELD.mul(W,FIELD.invert(p))^FIELD.mul(int(parameters[j][1]),FIELD.mul(oldN,oldN))
        if not D:return None
        reciprocal=FIELD.invert(D)
        inputs.append((FIELD.mul(N,reciprocal),FIELD.mul(W,FIELD.mul(reciprocal,reciprocal))))
    return inputs

def reference(inputs):
    parameters=[];scale=1
    for i,(u,v) in enumerate(inputs):
        N,D,W=FIELD.mul(scale,u),scale,FIELD.mul(FIELD.mul(scale,scale),v)
        for j,(a,b) in enumerate(parameters):
            point=i^j;p=FIELD.mul(point,point);P=a^FIELD.mul(point,b)
            W=FIELD.mul(p,W^FIELD.mul(b,FIELD.mul(N,N)))
            N,D=D^FIELD.mul(P,N),FIELD.mul(p,N)
        assert N
        inverse=FIELD.invert(N)
        parameters.append((FIELD.mul(D,inverse),FIELD.mul(W,FIELD.mul(inverse,inverse))))
        scale=N
    return parameters,scale


