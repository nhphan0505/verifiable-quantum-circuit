#!/usr/bin/env python3
# Copyright 2026 Syed Asad Ali. SPDX-License-Identifier: Apache-2.0.
# Credits: Opus and Astra.
"""Classical algebra certificate for the even-degree raw Forney outer map.

No quantum circuit is generated. Dense inverse Bezout is a reference only;
it does not claim a cheap coherent implementation or a failure certificate.
"""
from __future__ import annotations
import argparse
import json
import random
from pathlib import Path

MODULUS = 0x1053


def manual_mul(a, b):
    answer = 0
    while b:
        if b & 1:
            answer ^= a
        b >>= 1
        a <<= 1
        if a & 4096:
            a ^= MODULUS
    return answer


EXP, LOG = [], [None]*4096
x = 1
for k in range(4095):
    assert LOG[x] is None
    EXP.append(x)
    LOG[x] = k
    x = manual_mul(x, 2)
assert x == 1 and len(set(EXP)) == 4095


def mul(a, b):
    return 0 if not a or not b else EXP[(LOG[a]+LOG[b]) % 4095]


def divide(a, b):
    assert b
    return 0 if not a else EXP[(LOG[a]-LOG[b]) % 4095]


def square(a):
    return mul(a, a)


def sqrt(a):
    return 0 if not a else EXP[(2048*LOG[a]) % 4095]


def trim(poly):
    out = list(poly)
    while len(out) > 1 and not out[-1]:
        out.pop()
    return out


def product(a, b):
    out = [0]*(len(a)+len(b)-1)
    for i, av in enumerate(a):
        for j, bv in enumerate(b):
            out[i+j] ^= mul(av, bv)
    return trim(out)


def remainder(a, b):
    out = trim(a)
    assert any(b)
    while len(out) >= len(b) and any(out):
        shift = len(out)-len(b)
        factor = divide(out[-1], b[-1])
        for i, value in enumerate(b):
            out[i+shift] ^= mul(value, factor)
        out = trim(out)
    return out


def bezout(a, b):
    n = max(len(a), len(b))-1
    aa = list(a)+[0]*(n+1-len(a))
    bb = list(b)+[0]*(n+1-len(b))
    matrix = [[0]*n for _ in range(n)]
    for i in range(1, n+1):
        for j in range(i):
            coefficient = mul(aa[i], bb[j]) ^ mul(aa[j], bb[i])
            for k in range(i-j):
                matrix[i-1-k][j+k] ^= coefficient
    return matrix


def solve_two(matrix, u, v):
    n = len(matrix)
    rows = [list(row)+[u[i], v[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next(i for i in range(col, n) if rows[i][col])
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [divide(a, scale) for a in rows[col]]
        for i in range(n):
            if i == col:
                continue
            factor = rows[i][col]
            for j in range(col, n+2):
                rows[i][j] ^= mul(factor, rows[col][j])
    return [row[n] for row in rows], [row[n+1] for row in rows]


def even_forney(d, omega):
    degree = len(d)-1
    assert degree % 2 == 0 and len(omega) == degree and d[-1]
    h = degree//2
    a = [sqrt(value) for value in d[::2]]
    b = [sqrt(value) for value in d[1::2]]
    hmatrix = bezout(a, b)
    # H^(2) e_last = leading(D) * odd_coefficients(D).
    for i in range(h):
        assert square(hmatrix[i][-1]) == mul(d[-1], d[2*i+1])
    u, v = list(omega[::2]), list(omega[1::2])
    q = divide(v[-1], d[-1])
    u = [value ^ mul(d[2*i+1], q) for i, value in enumerate(u)]
    u, v = solve_two(hmatrix, [sqrt(value) for value in u],
                     [sqrt(value) for value in v])
    inverse_bez = [z for pair in zip(map(square, v), map(square, u)) for z in pair]
    # Full degree-word lower Toeplitz, diagonal d[degree], then reverse.
    out = []
    for i in range(degree):
        value = 0
        for j in range(i+1):
            value ^= mul(d[degree-i+j], inverse_bez[j])
        out.append(value)
    return list(reversed(out))


def half_profile(d):
    a = trim([sqrt(value) for value in d[::2]])
    b = trim([sqrt(value) for value in d[1::2]])
    degrees = [len(a)-1]
    while any(b):
        degrees.append(len(b)-1)
        a, b = b, remainder(a, b)
    return degrees




