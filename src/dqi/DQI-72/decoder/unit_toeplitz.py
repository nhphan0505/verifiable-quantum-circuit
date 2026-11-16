# Copyright 2026 Syed Asad Ali
# SPDX-License-Identifier: Apache-2.0
"""Zero-workspace in-place unit-series multiplication and its exact inverse."""
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
from tower_inverse import xor_product
FIELD=km.GF2Field(12)


def flat(words):return km.array([wire for word in words for wire in word])


@cache
def middle_tensor(a,b,d):
    """y_l += sum_k c_(l+k+1) * x_reversed_k, c_j=0 for j>d."""
    rank=a+b-1
    interpolation=invert_field_matrix([[FIELD.pow(x,k) for k in range(rank)] for x in range(rank)],FIELD)
    terms=[]
    for point in range(rank):
        coefficient_columns=tuple(FIELD.mul(interpolation[j][point],1<<bit) if j<rank else 0
                                  for j in range(d) for bit in range(12))
        vector_columns=tuple(FIELD.mul(FIELD.pow(point,k),1<<bit) for k in range(a) for bit in range(12))
        for left,right,output in multiplication_tensor():
            target=0
            for ell in range(b):target|=FIELD.mul(FIELD.pow(point,ell),output)<<(12*ell)
            terms.append((compose_mask(left,coefficient_columns),compose_mask(right,vector_columns),target))
    assert len(terms)==42*rank and all(x and y and z for x,y,z in terms)
    return tuple(terms)


def cross_shape(n,d):
    m=n//2;a=min(d,m);b=min(d,n-m)
    direct=sum(min(a,max(0,d-ell)) for ell in range(b))
    rank=a+b-1
    return m,a,b,direct,rank


def cross(builder,coefficients,vector):
    d=len(coefficients);m,a,b,direct,rank=cross_shape(len(vector),d)
    low=vector[m-a:m];high=vector[m:m+b]
    if rank<direct:
        accumulate_product(builder,flat(coefficients),flat(list(reversed(low))),flat(high),middle_tensor(a,b,d))
        return rank
    for ell in range(b):
        for j in range(a):
            k=a+ell-j
            if k<=d:xor_product(builder,coefficients[k-1],low[j],high[ell])
    return direct


def emit(builder,coefficients,vector,inverse=False):
    if len(vector)<2:return 0
    m=len(vector)//2
    if inverse:
        count=emit(builder,coefficients,vector[:m],True)
        count+=cross(builder,coefficients,vector)
        count+=emit(builder,coefficients,vector[m:],True)
    else:
        count=emit(builder,coefficients,vector[m:])
        count+=cross(builder,coefficients,vector)
        count+=emit(builder,coefficients,vector[:m])
    return count


@cache
def product_count(n,d):
    if n<2:return 0
    m,a,b,direct,rank=cross_shape(n,d)
    return product_count(m,d)+min(direct,rank)+product_count(n-m,d)


def build(n,d):
    assert n>=2 and d>=1
    builder=km.CircuitBuilder()
    coefficients=[builder.create_quantum_register(12,f'c{i}') for i in range(1,d+1)]
    vector=[builder.create_quantum_register(12,f'x{i}') for i in range(n)]
    probe=builder.create_classical_register(12*n,'product_phase_probe')
    counted=emit(builder,coefficients,vector)
    assert counted==product_count(n,d)
    builder.cz(probe,flat(vector))
    assert emit(builder,coefficients,vector,inverse=True)==counted
    return builder.finish_circuit(),coefficients,vector,probe



