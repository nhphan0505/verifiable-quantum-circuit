# Copyright 2026 Syed Asad Ali
# SPDX-License-Identifier: Apache-2.0
"""Normalize a locator/numerator pair, retaining the nonzero leading scalar."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import sys
import kickmix as km
import numpy as np
from compact_inverse import compact_inverse_twelve,phase_inverse_twelve
from tower_inverse import apply_inplace_linear,quadratic_basis
from dual_scale import scale_word,FIELD
from quantum_reciprocal import bit_matrix
from projective_carry import erase_inverse_word,repay_inverse_mask


def emit(builder,words,leading,reverse=False,defer=False,deferred_mask=None):
    inverse=compact_inverse_twelve(builder,leading)
    if deferred_mask is not None:repay_inverse_mask(builder,inverse,deferred_mask)
    temporary=builder.alloc_qubits(12)
    for word in words:
        if reverse:scale_word(builder,word,leading,inverse,temporary)
        else:scale_word(builder,word,inverse,leading,temporary)
    builder.free(temporary)
    return erase_inverse_word(builder,leading,inverse,defer)


def build(degree):
    builder=km.CircuitBuilder()
    locator=[builder.create_quantum_register(12,f'D{i}') for i in range(degree)]
    numerator=[builder.create_quantum_register(12,f'Omega{i}') for i in range(degree)]
    leading=builder.create_quantum_register(12,'retained_leading_scalar')
    probe=builder.create_classical_register(24*degree,'normalized_phase_probe')
    words=locator+numerator
    emit(builder,words,leading)
    builder.cz(probe,km.array([wire for word in words for wire in word]))
    emit(builder,words,leading,reverse=True)
    return builder.finish_circuit(),words,leading,probe



