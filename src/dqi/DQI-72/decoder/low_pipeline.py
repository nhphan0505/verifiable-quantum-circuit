# Copyright 2026 Syed Asad Ali
# SPDX-License-Identifier: Apache-2.0
"""Normal pipeline with12 arithmetic scratch and an untouched history input."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import random
import sys
import kickmix as km
import numpy as np
from normal_pipeline import input_map,direct_pair,polynomial_reference,parameter_coordinates,ALG,FIELD
from field_tensor import invert_binary_columns
from tower_inverse import apply_inplace_linear,rows_from_columns,xor_product,phase_product,kernel
from quantum_reciprocal import bit_matrix
from projective_carry import homogeneous,power_rows
from normal_fold import shift,add_linear_product
from lowspace_field import invert,phase_quotients

def flat(words):return km.array([wire for word in words for wire in word])

def scale_words(builder,words,source,powers=None,defer=False):
    powers=[1]*len(words) if powers is None else powers
    temporary=builder.alloc_qubits(12);masks=[]
    for word,power in zip(words,powers):
        exponent=power.bit_length()-1
        assert power==1<<exponent
        if exponent:apply_inplace_linear(builder,source,power_rows(power))
        xor_product(builder,word,source,temporary)
        if exponent:apply_inplace_linear(builder,source,power_rows(1<<((12-exponent)%12)))
        builder.swap(word,temporary)
        mask=builder.alloc_bits(12);builder.hmr(temporary,mask);masks.append(mask)
    builder.free(temporary)
    if defer:return masks
    phase_quotients(builder,source,list(zip(words,masks,powers)))
    for mask in masks:builder.free(mask)

def repay(builder,words,masks):
    for word,mask in zip(words,masks):builder.cz(mask,word);builder.free(mask)

def key_forward(builder,jets,scale):
    encodings=[None]*len(jets);normalizations=[]
    for i,(u,v) in enumerate(jets):
        if i:encodings[i]=scale_words(builder,[u,v],scale,[1,2],True)
        for j in range(i):homogeneous(builder,u,v,scale,jets[j],i^j)
        builder.swap(u,scale)
        invert(builder,scale)
        normalizations.append(scale_words(builder,[u,v],scale,[1,2],True))
    return encodings,normalizations

def key_reverse(builder,jets,scale,record,already_inverted=False):
    encodings,normalizations=record
    if not already_inverted:invert(builder,scale)
    for i in reversed(range(len(jets))):
        u,v=jets[i]
        scale_words(builder,[u,v],scale,[1,2])
        repay(builder,[u,v],normalizations[i])
        builder.swap(u,scale)
        for j in reversed(range(i)):homogeneous(builder,u,v,scale,jets[j],i^j,True)
        if i:
            invert(builder,scale)
            scale_words(builder,[u,v],scale,[1,2])
            repay(builder,[u,v],encodings[i])

def fold_forward(builder,P,N,D,node):
    shift(builder,P,node);shift(builder,N,node);shift(builder,D,node)
    add_linear_product(builder,P,D[2:],N)
    xor_product(builder,P[1],D[1],N[0])
    bmask=scale_words(builder,[P[1]],D[0],defer=True)
    xor_product(builder,P[0],D[1],P[1])
    amask=scale_words(builder,[P[0]],D[0],defer=True)
    shift(builder,D,node);shift(builder,P+N,node)
    return amask+bmask

def fold_reverse(builder,P,N,D,node,masks):
    shift(builder,P+N,node);shift(builder,D,node)
    invert(builder,D[0])
    amask=scale_words(builder,[P[0]],D[0],defer=True)
    xor_product(builder,P[0],D[1],P[1])
    bmask=scale_words(builder,[P[1]],D[0],defer=True)
    invert(builder,D[0])
    for word,mask in zip(P,amask+bmask):
        phase_product(builder,word,D[0],mask,kernel(12));builder.free(mask)
    repay(builder,P,masks)
    xor_product(builder,P[1],D[1],N[0])
    add_linear_product(builder,P,D[2:],N)
    shift(builder,D,node);shift(builder,N,node);shift(builder,P,node)

def normalize_forward(builder,words,leading):
    invert(builder,leading)
    return scale_words(builder,words,leading,defer=True)

def normalize_reverse(builder,words,leading,masks):
    invert(builder,leading)
    scale_words(builder,words,leading)
    repay(builder,words,masks)

def build(t,history_bits=10):
    assert t>=2
    builder=km.CircuitBuilder();_,binary=input_map(t)
    words=[builder.create_quantum_register(12,f'S{i}') for i in range(2*t)]
    history=builder.create_quantum_register(history_bits,'reserved_history')
    jets=[words[2*i:2*i+2] for i in range(t)]
    probe=builder.create_classical_register(12*(2*t+1)+history_bits,'low_pipeline_probe')
    apply_inplace_linear(builder,flat(words),rows_from_columns(binary))
    scale=builder.alloc_qubits(12);builder.x(scale[0])
    key_record=key_forward(builder,jets,scale)
    parameter_coordinates(builder,jets)
    head_masks=scale_words(builder,jets[-1],scale,defer=True)
    N=[scale];D=list(jets[-1]);folds=[]
    for node in reversed(range(t-1)):
        P=jets[node];masks=fold_forward(builder,P,N,D,node)
        folds.append((P,N,D,node,masks));N,D=D,list(P)+N
    leading=D[-1];normalized_words=D[:-1]+N
    normalizer_masks=normalize_forward(builder,normalized_words,leading)
    builder.cz(probe,km.array(list(flat(normalized_words+[leading]))+list(history)))
    normalize_reverse(builder,normalized_words,leading,normalizer_masks)
    for P,oldN,oldD,node,masks in reversed(folds):fold_reverse(builder,P,oldN,oldD,node,masks)
    # This inversion is also the first inversion of the reverse key.
    invert(builder,scale)
    scale_words(builder,jets[-1],scale)
    repay(builder,jets[-1],head_masks)
    parameter_coordinates(builder,jets)
    key_reverse(builder,jets,scale,key_record,already_inverted=True)
    builder.x(scale[0]);builder.free(scale)
    apply_inplace_linear(builder,flat(words),invert_binary_columns(binary))
    return builder.finish_circuit(),words,history,probe

def key_reference(inputs):
    parameters=[];scale=1
    for i,(u,v) in enumerate(inputs):
        N,D,W=FIELD.mul(scale,u),scale,FIELD.mul(FIELD.mul(scale,scale),v)
        for j,(a,b) in enumerate(parameters):
            point=i^j;p=FIELD.mul(point,point);P=a^FIELD.mul(point,b)
            W=FIELD.mul(p,W^FIELD.mul(b,FIELD.mul(N,N)))
            N,D=D^FIELD.mul(P,N),FIELD.mul(p,N)
        assert N
        scale=FIELD.invert(N)
        parameters.append((FIELD.mul(D,scale),FIELD.mul(W,FIELD.mul(scale,scale))))
    return parameters,scale


