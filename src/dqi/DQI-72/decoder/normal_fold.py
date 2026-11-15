# Copyright 2026 Syed Asad Ali
# SPDX-License-Identifier: Apache-2.0
"""Normal one-array continuant fold using Taylor coordinates and dual scaling."""
from __future__ import annotations
from functools import cache
import hashlib
import io
import json
from pathlib import Path
import sys
import kickmix as km
import numpy as np
from field_tensor import multiplication_tensor,invert_field_matrix,accumulate_product
from quantum_reciprocal import bit_matrix,compose_mask
from tower_inverse import apply_inplace_linear,rows_from_columns,xor_product
from compact_dual_scale import emit as dual_scale,FIELD


def flat(words):return km.array([wire for word in words for wire in word])


@cache
def translation_rows(length,node):
    columns=[]
    for i in range(length):
        for bit in range(12):
            column=0
            for j in range(i+1):
                if j&~i==0:
                    column|=FIELD.mul(FIELD.pow(node,i-j),1<<bit)<<(12*j)
            columns.append(column)
    return rows_from_columns(columns)


def shift(builder,words,node):
    apply_inplace_linear(builder,flat(words),translation_rows(len(words),node))


@cache
def linear_product_tensor(r):
    assert r>=2
    interpolation=invert_field_matrix([[FIELD.pow(x,k) for k in range(r)] for x in range(r)],FIELD)
    result=[]
    for point in range(r):
        left_columns=tuple(FIELD.mul(FIELD.pow(point,k),1<<bit) for k in range(2) for bit in range(12))
        right_columns=tuple(FIELD.mul(FIELD.pow(point,k),1<<bit) for k in range(r-1) for bit in range(12))
        for a,b,out in multiplication_tensor():
            output=0
            for k in range(r):output|=FIELD.mul(interpolation[k][point],out)<<(12*k)
            result.append((compose_mask(a,left_columns),compose_mask(b,right_columns),output))
    assert len(result)==42*r
    return tuple(result)


def add_linear_product(builder,P,Q,N):
    if not Q:return
    r=len(N);assert len(Q)==r-1 and len(P)==2
    accumulate_product(builder,flat(P),flat(Q),flat(N),linear_product_tensor(r))


def emit_forward(builder,P,N,D,node,trim=False):
    shift(builder,P,node);shift(builder,N,node);shift(builder,D,node)
    add_linear_product(builder,P,D[2:],N)
    xor_product(builder,P[1],D[1],N[0])
    dual_scale(builder,P[0],P[1],D[0],D[1],trim=trim)
    shift(builder,D,node)
    shift(builder,P+N,node)


def emit_reverse(builder,P,N,D,node,trim=False):
    shift(builder,P+N,node)
    shift(builder,D,node)
    dual_scale(builder,P[0],P[1],D[0],D[1],reverse=True,trim=trim)
    xor_product(builder,P[1],D[1],N[0])
    add_linear_product(builder,P,D[2:],N)
    shift(builder,D,node);shift(builder,N,node);shift(builder,P,node)


def build(r,trim=False):
    assert r>=1
    builder=km.CircuitBuilder()
    P=[builder.create_quantum_register(12,f'P{i}') for i in range(2)]
    N=[builder.create_quantum_register(12,f'N{i}') for i in range(r)]
    D=[builder.create_quantum_register(12,f'D{i}') for i in range(r+1)]
    mask=builder.create_classical_register(12*(2*r+3),'parent_phase_probe')
    emit_forward(builder,P,N,D,2,trim)
    builder.cz(mask,flat(D+P+N))
    emit_reverse(builder,P,N,D,2,trim)
    return builder.finish_circuit(),P+N+D,mask


def multiply(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]^=FIELD.mul(int(x),int(y))
    return out


def evaluate(a,x):
    value=0
    for v in reversed(a):value=FIELD.mul(value,x)^int(v)
    return value



