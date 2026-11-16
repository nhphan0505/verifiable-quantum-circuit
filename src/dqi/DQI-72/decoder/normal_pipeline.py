# Copyright 2026 Syed Asad Ali
# SPDX-License-Identifier: Apache-2.0
"""Normal syndrome->monic pair->syndrome pilot, without exceptions or scan."""
from __future__ import annotations
from functools import cache
import hashlib
import io
import json
from pathlib import Path
import random
import sys
import kickmix as km
import numpy as np
from confluent_reference import Algebra,modulus,from_errors
from field_tensor import invert_field_matrix,invert_binary_columns
from tower_inverse import rows_from_columns,apply_inplace_linear
from quantum_reciprocal import bit_matrix,xor_linear
from compact_inverse import compact_inverse_twelve
from dual_scale import scale_word
from projective_carry import emit as key,erase_inverse_word,reference as key_reference
from deferred_fold import emit_forward,emit_paired_reverse
from normalization import emit as normalize

ALG=Algebra(12);FIELD=ALG.field

def flat(words):return km.array([wire for word in words for wire in word])

@cache
def input_map(t):
    nodes=list(range(t));M=modulus(ALG,nodes);n=2*t;columns=[]
    for index in range(n):
        h=[M[index+ell+1] if index+ell+1<=n else 0 for ell in range(n)]
        columns.append([value for node in nodes for value in ALG.jet(h,node)])
    matrix=[[columns[j][i] for j in range(n)] for i in range(n)]
    invert_field_matrix(matrix,FIELD)
    binary=[]
    for word in range(n):
        for bit in range(12):
            binary.append(sum(FIELD.mul(matrix[out][word],1<<bit)<<(12*out) for out in range(n)))
    return M,tuple(binary)

def parameter_coordinates(builder,jets):
    for node,(a,b) in enumerate(jets):
        xor_linear(builder,b,a,tuple(FIELD.mul(node,1<<bit) for bit in range(12)))

def scale_head(builder,words,scale,inverse,divide=False):
    temporary=builder.alloc_qubits(12)
    for word in words:
        if divide:scale_word(builder,word,inverse,scale,temporary)
        else:scale_word(builder,word,scale,inverse,temporary)
    builder.free(temporary)

def build(t,repay_fold_masks=True):
    assert t>=2
    builder=km.CircuitBuilder();_,binary=input_map(t)
    words=[builder.create_quantum_register(12,f'S{i}') for i in range(2*t)]
    jets=[words[2*i:2*i+2] for i in range(t)]
    probe=builder.create_classical_register(12*(2*t+1),'monic_pair_and_scale_probe')
    apply_inplace_linear(builder,flat(words),rows_from_columns(binary))
    scale=builder.alloc_qubits(12);builder.x(scale[0])
    key_masks=[]
    inverse=key(builder,jets,scale,keep_inverse=True,deferred_masks=key_masks)
    parameter_coordinates(builder,jets)
    scale_head(builder,jets[-1],scale,inverse)
    key_masks.append(erase_inverse_word(builder,scale,inverse,defer=True))
    N=[scale];D=list(jets[-1]);history=[]
    for node in reversed(range(t-1)):
        P=jets[node]
        measured=emit_forward(builder,P,N,D,node)
        history.append((P,N,D,node,measured))
        N,D=D,list(P)+N
    leading=D[-1];normalized_words=D[:-1]+N
    normalizer_mask=normalize(builder,normalized_words,leading,defer=True)
    builder.cz(probe,flat(normalized_words+[leading]))
    normalize(builder,normalized_words,leading,True,deferred_mask=normalizer_mask)
    for P,oldN,oldD,node,measured in reversed(history):
        emit_paired_reverse(builder,P,oldN,oldD,node,measured,repay_fold_masks)
    inverse=compact_inverse_twelve(builder,scale)
    scale_head(builder,jets[-1],scale,inverse,True)
    parameter_coordinates(builder,jets)
    key(builder,jets,scale,True,initial_inverse=inverse,deferred_masks=key_masks)
    builder.x(scale[0]);builder.free(scale)
    apply_inplace_linear(builder,flat(words),invert_binary_columns(binary))
    return builder.finish_circuit(),words,probe

def polynomial_reference(parameters,scale):
    pairs=[[int(a)^FIELD.mul(i,int(b)),int(b)] for i,(a,b) in enumerate(parameters)]
    N=[scale];D=[FIELD.mul(scale,c) for c in pairs[-1]]
    for node in reversed(range(len(pairs)-1)):
        assert ALG.evaluate_polynomial(D,node)
        parent=ALG.add(ALG.product(pairs[node],D),ALG.product([FIELD.mul(node,node),0,1],N))
        N,D=D,parent
    return N,D

def direct_pair(errors,M):
    locator=[1]
    for root,_ in errors:locator=ALG.product(locator,[root,1])
    numerator=[0]*len(errors)
    for j,(root,amplitude) in enumerate(errors):
        cofactor=[FIELD.mul(FIELD.mul(amplitude,root),ALG.evaluate_polynomial(M,root))]
        for k,(other,_) in enumerate(errors):
            if k!=j:cofactor=ALG.product(cofactor,[other,1])
        for k,value in enumerate(cofactor):numerator[k]^=value
    return numerator,locator


