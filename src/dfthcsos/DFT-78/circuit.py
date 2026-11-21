"""Synthesize DFTHC ANGLE loaders using the notebook ANF generator.

Adapted from orecord, Apache-2.0. Batches implement XOR deltas on dirty
targets and uncompute prefix products through the Kickmix builder. The
tracked arrays are Tony Li v2 fit parameters, including angle-word edits.
"""

from functools import lru_cache
import io
import math
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

import kickmix as km
import numpy as np

DATA = Path(__file__).resolve().parent / "data"
ARRAY_NAMES = ("H1_I", "H2_I", "Hsym_lower", "U", "W", "angle_words", "tree_edges")


def make_deltas(words, j):
    """Consecutive batches of j words; each batch is XORed with the previous one (circuits act on a dirty target)."""
    a, n = words.shape
    k = math.ceil(n / j)
    p = np.zeros((a, k * j), dtype=np.int64)
    p[:, :n] = words
    batches = p.reshape(a, k, j).transpose(1, 0, 2)
    d = batches.copy()
    d[1:] ^= batches[:-1]
    return d

def pack(row, brot):
    return sum(int(v) << (j * brot) for j, v in enumerate(row))

def mobius_transform(table):
    """Packed-output Boolean truth table <-> ANF coefficient table over GF(2)."""
    result = list(map(int, table))
    n = (len(result) - 1).bit_length()
    for bit in range(n):
        step = 1 << bit
        for start in range(0, len(result), 2 * step):
            for off in range(step):
                result[start + step + off] ^= result[start + off]
    return result

def xor_and(b, left, right, targets):
    """targets ^= left AND right with a single Toffoli (fan-out through CNOTs)."""
    targets = list(targets)
    if not targets:
        return
    q = targets[0]
    for t in targets[1:]:
        b.cx(q, t)
    b.ccx(left, right, q)
    for t in reversed(targets[1:]):
        b.cx(q, t)

def pebbled_init(b, table, address, outputs, scratch):
    address, outputs, scratch = map(list, (address, outputs, scratch))
    H, n = len(table), len(address)
    coefficients = mobius_transform(list(table) + [0] * ((1 << n) - H))
    coefficients[H:] = [0] * ((1 << n) - H)          # rows beyond the legal range are free; zeroing them prunes monomials
    assert mobius_transform(coefficients)[:H] == list(table), 'ANF identity failed on a legal row'

    @lru_cache(None)
    def children(mask, last):
        return tuple((mask | (1 << j), j) for j in range(last + 1, n) if (mask | (1 << j)) < H)

    @lru_cache(None)
    def need(mask, last):
        return max([1 + need(c, j) for c, j in children(mask, last) if children(c, j)] + [0])

    def targets(mask):
        v = coefficients[mask]
        return [outputs[j] for j in range(len(outputs)) if (v >> j) & 1]

    def walk(mask, last, control, path, free):
        erased = []
        if mask.bit_count() == 5 and need(mask, last) > len(free):
            m = need(mask, last) - len(free)         # pebbling: free scratch by uncomputing the oldest products
            erased = path[:m]
            for a, c, t in reversed(erased):
                b.del_and(a, c, t)
                free.append(t)
        ts = targets(mask)
        if ts:
            if control is None:
                b.x(km.array(ts))
            else:
                b.cx(control, km.array(ts))
        for child, j in children(mask, last):
            if not mask:
                walk(child, j, address[j], path, free)
            elif not children(child, j):
                ts = targets(child)
                if ts:
                    xor_and(b, control, address[j], ts)
            else:
                t = free.pop()
                b.init_and(control, address[j], t)
                walk(child, j, t, path + [(control, address[j], t)], free)
                b.del_and(control, address[j], t)
                free.append(t)
        for a, c, t in erased:
            free.remove(t)
            b.init_and(a, c, t)

    walk(0, -1, None, [], scratch.copy())

def qrom_anf(delta, brot):
    a, j = delta.shape
    n = (a - 1).bit_length()
    values = [pack(row, brot) for row in delta]
    b = km.CircuitBuilder()
    sel = b.create_quantum_register(n, 'selection')
    tgt = [q for k in range(j) for q in b.create_quantum_register(brot, f'word_{k}')]
    work = b.alloc_qubits(max(1, n - 2))
    pebbled_init(b, values, sel, tgt, work)
    b.free(work)
    return b.finish_circuit()


def build_components(output, *, brot=7, batch_size=5):
    """Synthesize ANGLE loaders and write the matching numerical factorization."""
    arrays = {name: np.load(DATA / (name + ".npy"), allow_pickle=False) for name in ARRAY_NAMES}
    words = arrays["angle_words"]
    if brot != 7 or batch_size != 5 or words.min() < 0 or words.max() >= 1 << brot:
        raise ValueError("Use the committed 7-bit chemistry words in batches of five")
    output.mkdir()
    for index, delta in enumerate(make_deltas(words, batch_size)):
        circuit = qrom_anf(delta, brot)
        if circuit.num_qubits > 128:
            raise ValueError(f"ANGLE_{index} exceeds the 128-qubit limit")
        circuit.to_file(output / f"angle_k_{index}.kmb", format="kmb")
    with ZipFile(output / "submission.npz", "w") as archive:
        for name in sorted(arrays):
            stream = io.BytesIO()
            np.lib.format.write_array(stream, arrays[name], version=(1, 0), allow_pickle=False)
            info = ZipInfo(name + ".npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = ZIP_STORED
            info.external_attr = 0o600 << 16
            archive.writestr(info, stream.getvalue())
