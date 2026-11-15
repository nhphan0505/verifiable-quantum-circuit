# Copyright 2026 Syed Asad Ali
# SPDX-License-Identifier: Apache-2.0
"""In-place multiplication by a nonzero dual number, with retained norm."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import sys
import kickmix as km
import numpy as np
from quantum_reciprocal import bit_matrix
from tower_inverse import (init_inverse,erase_inverse,init_inverse_three,erase_inverse_three,
                           xor_product,erase_product)
FIELD=km.GF2Field(12)


def scale_word(builder,word,multiplier,inverse_multiplier,temporary):
    xor_product(builder,word,multiplier,temporary)
    builder.swap(word,temporary)
    erase_product(builder,word,inverse_multiplier,temporary)


def emit(builder,a,b,c,d,reverse=False,trim=False):
    inverse=builder.alloc_qubits(12)
    scaffold=init_inverse(builder,c,inverse)
    leaf=scaffold['child']
    if trim:
        erase_inverse_three(builder,leaf['norm'],leaf['inverse_norm'])
        builder.free(leaf['inverse_norm']);leaf['inverse_norm']=None
    temporary=builder.alloc_qubits(12)
    if reverse:
        scale_word(builder,a,inverse,c,temporary)
        xor_product(builder,a,d,b)
        scale_word(builder,b,inverse,c,temporary)
    else:
        scale_word(builder,b,c,inverse,temporary)
        xor_product(builder,a,d,b)
        scale_word(builder,a,c,inverse,temporary)
    builder.free(temporary)
    if trim:
        leaf['inverse_norm']=builder.alloc_qubits(3)
        init_inverse_three(builder,leaf['norm'],leaf['inverse_norm'])
    erase_inverse(builder,c,inverse,scaffold)
    builder.free(inverse)


def build(reverse=False,trim=False):
    builder=km.CircuitBuilder()
    words=[builder.create_quantum_register(12,name) for name in ('a','b','c','d')]
    emit(builder,*words,reverse=reverse,trim=trim)
    return builder.finish_circuit(),words


def serialized(circuit):
    stream=io.BytesIO();circuit.to_file(stream,format='kmb');return stream.getvalue()



