# Copyright 2026 Syed Asad Ali
# SPDX-License-Identifier: Apache-2.0
"""Root-mask scan using the two existing constant-coefficient words."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import sys
import kickmix as km
import numpy as np
from quantum_reciprocal import bit_matrix,xor_linear
from tower_inverse import apply_inplace_linear,rows_from_columns,sum_trace

def product(a,b,field):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]^=field.mul(int(x),int(y))
    return out

def evaluate(poly,x,field):
    value=0
    for coefficient in reversed(poly):value=field.mul(value,x)^int(coefficient)
    return value

def known_reweight(x,field,nodes):
    """Invert x*M(x), omitting its squared vanishing factor at a node.

    The proper numerator's residue at a physical node a is e*a*M_a(a).
    The node-zero scan position is absent. Distinct interpolation nodes and
    a nonzero x therefore always give a unit scale in this stated gauge.
    """
    assert x and len(set(nodes))==len(nodes)
    value=x
    for node in nodes:
        if node!=x:value=field.mul(value,field.mul(x^node,x^node))
    assert value
    return field.invert(value)

def fixed_scale(builder,word,value,field):
    assert value
    if value==1:return
    columns=[field.mul(value,1<<bit) for bit in range(field.degree)]
    apply_inplace_linear(builder,word,rows_from_columns(columns))

def emit(builder,locator,values,masks,field,nodes=(),leading=None):
    degree=len(locator);bits=field.degree
    assert degree==len(values) and len(masks)==(1<<bits)-1
    ladder=builder.alloc_qubits(bits-1)
    previous=[1]+[0]*degree
    def move(point):
        nonlocal previous
        powers=[1]
        for _ in range(degree):powers.append(field.mul(powers[-1],point))
        for i in range(1,degree):
            coefficient=powers[i]^previous[i]
            columns=tuple(field.mul(coefficient,1<<bit) for bit in range(bits))
            xor_linear(builder,locator[i],locator[0],columns)
            xor_linear(builder,values[i],values[0],columns)
        constant=powers[degree]^previous[degree]
        if leading is None:
            for bit in range(bits):
                if constant>>bit&1:builder.x(locator[0][bit])
        else:
            assert len(leading)==bits and not set(leading)&set(locator[0])
            columns=tuple(field.mul(constant,1<<bit) for bit in range(bits))
            xor_linear(builder,leading,locator[0],columns)
        previous=powers
    point=1
    for position,mask in enumerate(masks):
        move(point)
        factor=known_reweight(point,field,nodes) if nodes else 1
        fixed_scale(builder,values[0],factor,field)
        builder.x(locator[0])
        builder.init_and(locator[0][0],locator[0][1],ladder[0])
        for i in range(1,bits-1):builder.init_and(ladder[i-1],locator[0][i+1],ladder[i])
        builder.ccz(mask,ladder[-1],values[0])
        for i in reversed(range(1,bits-1)):builder.del_and(ladder[i-1],locator[0][i+1],ladder[i])
        builder.del_and(locator[0][0],locator[0][1],ladder[0])
        builder.x(locator[0])
        fixed_scale(builder,values[0],field.invert(factor),field)
        point=field.mul(point,field.primitive_element)
    assert point==1
    move(0)
    builder.free(ladder)

def build(bits,degree,reweighted=True):
    field=km.GF2Field(bits);builder=km.CircuitBuilder()
    locator=[builder.create_quantum_register(bits,f'D{i}') for i in range(degree)]
    values=[builder.create_quantum_register(bits,f'R{i}') for i in range(degree)]
    retained=builder.create_quantum_register(bits,'retained_scale')
    masks=[builder.create_classical_register(bits,f'E{i}') for i in range((1<<bits)-1)]
    emit(builder,locator,values,masks,field,tuple(range(degree)) if reweighted else ())
    return builder.finish_circuit(),locator,values,retained,masks

def padding(field,gap):
    result=[0,1] if gap&1 else [1]
    deltas=[x for x in range(1,1<<field.degree) if sum_trace(x,field)==1]
    assert len(deltas)>=gap//2
    for delta in deltas[:gap//2]:result=product(result,[delta,1,1],field)
    return result


