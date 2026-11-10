"""Regenerate recurring rank-42 multiply-adds in the Kirill V5 synthesis pair.

The fixed V5 KMB is the source for routing, history, and stages outside
synthesis and unsynthesis. Each recognized multiply-add is regenerated from
three 12-wire words and 42 ordered bilinear terms. For each term, reversible
CNOTs compute its input parities and change the output basis, a CCX adds the
product, and the reversed CNOT list restores both input words. A multiply-add
is its own inverse. The surrounding V5 measurement and phase corrections
remain in place. No new approximation, workspace or error cutoff is used.

The generator validates all 144 field basis pairs and requires the final
binary to match the pinned V5 artifact byte for byte. This config is a
reference for the synthesis rewrite. Routing and inverse history still come
from the pinned gate stream.

Run python src/dqi/DQI-39/solution.py --config
src/dqi/DQI-39/configs/rank42_reference.json --reference /path/to/kirill_v5.kmb
with the repository's Python environment. Temporary space is required for
two KMX files and the output KMB.
"""

import argparse
from collections import Counter
from functools import reduce
import hashlib
import itertools
import json
from operator import xor
from pathlib import Path
import re
import tempfile

import kickmix as km


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REFERENCE_SHA256 = "4e9b50b1ee34b3eaf2b7f394873c2dd3dad4cddbdd1f12a348b4323b5eb41771"
STAGES = ("synthesis", "unsynthesis")
TERMS = (
    ((0, 6, 8), (0, 6, 8), (0, 2, 3, 6, 8, 9, 10, 11), 'ababccccccc'),
    ((0, 4, 5, 7, 8, 9, 10), (0, 4, 5, 7, 8, 9, 10), (0, 4, 5, 6, 7, 9, 11), 'ababababababcccccc'),
    ((5, 6, 7, 8, 9, 10), (5, 6, 7, 8, 9, 10), (0, 1, 3, 5, 7, 8, 9, 10), 'abababababccccccc'),
    ((0, 5, 7, 9, 10), (0, 5, 7, 9, 10), (1, 3, 4, 6, 8, 10, 11), 'ababababcccccc'),
    ((4, 5, 6, 7, 9, 10), (4, 5, 6, 7, 9, 10), (1, 2, 5, 6, 7, 11), 'abababababccccc'),
    ((0, 4, 6), (0, 4, 6), (2, 3, 4, 5, 7, 8, 10), 'ababcccccc'),
    ((0, 1, 2, 3, 8, 9, 10, 11), (0, 1, 2, 3, 8, 9, 10, 11), (1, 2, 4, 5, 6, 9, 11), 'abababababababcccccc'),
    ((0, 1, 2, 3, 4, 5, 8, 9, 10, 11), (0, 1, 2, 3, 4, 5, 8, 9, 10, 11), (0, 1, 2, 3, 5, 6, 8, 9), 'abababababababababccccccc'),
    ((5, 6, 9), (5, 6, 9), (1, 4, 5, 8, 10), 'ababcccc'),
    ((0, 1, 2, 3, 5, 6, 8, 10, 11), (0, 1, 2, 3, 5, 6, 8, 10, 11), (0, 2, 3, 4, 6, 9, 10), 'ababababababababcccccc'),
    ((4, 5), (4, 5), (2, 6, 8, 9, 10, 11), 'abccccc'),
    ((0, 1, 2, 3, 4, 6, 8, 10, 11), (0, 1, 2, 3, 4, 6, 8, 10, 11), (0, 3, 4, 8, 11), 'ababababababababcccc'),
    ((0, 3, 4, 5, 9, 11), (0, 3, 4, 5, 9, 11), (0, 2, 3, 6, 8, 9, 10), 'abababababcccccc'),
    ((0, 1, 2, 4, 5, 7, 10), (0, 1, 2, 4, 5, 7, 10), (0, 1, 8, 10), 'ababababababccc'),
    ((2, 5, 6, 9, 10), (2, 5, 6, 9, 10), (0, 2, 3, 4, 5, 6, 10), 'ababababcccccc'),
    ((0, 2, 3, 4, 6, 10, 11), (0, 2, 3, 4, 6, 10, 11), (1, 2, 3, 4, 5, 6, 8), 'ababababababcccccc'),
    ((1, 2, 3, 7, 9, 10, 11), (1, 2, 3, 7, 9, 10, 11), (4, 5, 8, 9), 'ababababababccc'),
    ((0, 1, 4, 6, 7, 9), (0, 1, 4, 6, 7, 9), (1, 2, 3, 6, 9), 'abababababcccc'),
    ((0, 1, 2, 5, 8, 9, 10, 11), (0, 1, 2, 5, 8, 9, 10, 11), (1, 3, 4, 5, 6, 7, 8, 9, 10), 'abababababababcccccccc'),
    ((0, 3, 6, 7, 8, 9, 10), (0, 3, 6, 7, 8, 9, 10), (0, 5, 6, 7, 10, 11), 'ababababababccccc'),
    ((2, 3, 4, 7), (2, 3, 4, 7), (0, 3, 5, 6, 7, 9), 'abababccccc'),
    ((0, 1, 3, 4, 5, 7, 8, 9, 10, 11), (0, 1, 3, 4, 5, 7, 8, 9, 10, 11), (3, 9, 10, 11), 'abababababababababccc'),
    ((1, 2, 3, 5, 6, 7, 11), (1, 2, 3, 5, 6, 7, 11), (0, 1, 4, 8, 10), 'ababababababcccc'),
    ((0, 2, 4, 6, 8, 9, 10), (0, 2, 4, 6, 8, 9, 10), (0, 1, 3, 4, 8, 9, 11), 'ababababababcccccc'),
    ((0, 3, 7, 8), (0, 3, 7, 8), (1, 3, 4, 5, 11), 'abababcccc'),
    ((0, 1, 6, 8, 9), (0, 1, 6, 8, 9), (4, 6, 8, 9, 11), 'ababababcccc'),
    ((1, 2, 3, 4, 5, 6, 7, 8), (1, 2, 3, 4, 5, 6, 7, 8), (0, 1, 5, 6, 8, 9, 10), 'abababababababcccccc'),
    ((0, 1, 2, 4, 5, 6), (0, 1, 2, 4, 5, 6), (0, 1, 4, 5, 10, 11), 'abababababccccc'),
    ((1, 3, 6, 7, 9), (1, 3, 6, 7, 9), (0, 3, 4, 6, 8, 9, 10, 11), 'ababababccccccc'),
    ((0, 2, 3, 4, 5, 7, 9), (0, 2, 3, 4, 5, 7, 9), (1, 3, 5, 6, 8, 9), 'ababababababccccc'),
    ((0, 1, 2, 5, 6, 8, 9, 10, 11), (0, 1, 2, 5, 6, 8, 9, 10, 11), (0, 1, 2, 3, 4, 9, 10, 11), 'ababababababababccccccc'),
    ((0, 2, 4, 11), (0, 2, 4, 11), (0, 1, 7, 8, 9, 10, 11), 'abababcccccc'),
    ((1, 2, 3, 7, 8, 9, 10, 11), (1, 2, 3, 7, 8, 9, 10, 11), (6, 7, 8, 9, 10), 'abababababababcccc'),
    ((0, 3, 5, 6, 7), (0, 3, 5, 6, 7), (0, 1, 6, 11), 'ababababccc'),
    ((1, 4, 5, 6, 8, 9, 10), (1, 4, 5, 6, 8, 9, 10), (0, 1, 2, 3, 4, 6, 7, 8, 11), 'ababababababcccccccc'),
    ((0, 1, 3, 4, 7, 8, 9, 10), (0, 1, 3, 4, 7, 8, 9, 10), (2, 3, 4, 7, 8), 'abababababababcccc'),
    ((3, 5, 11), (3, 5, 11), (0, 4, 5, 7, 8, 10), 'ababccccc'),
    ((3, 4, 5, 6, 8, 9), (3, 4, 5, 6, 8, 9), (0, 1, 2, 3, 4, 7, 8), 'abababababcccccc'),
    ((5, 7), (5, 7), (0, 1, 2, 5, 6, 7, 9, 11), 'abccccccc'),
    ((3, 7, 11), (3, 7, 11), (3, 4, 5, 6, 8, 9, 11), 'ababcccccc'),
    ((4, 6, 8, 9, 11), (4, 6, 8, 9, 11), (1, 2, 4, 6, 8, 9, 10, 11), 'ababababccccccc'),
    ((3, 4, 6, 7, 8, 9), (3, 4, 6, 7, 8, 9), (1, 2, 3, 5, 10), 'abababababcccc'),
)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def rank42_gates(left, right, target):
    """Emit an exact multiply-add on three disjoint 12-wire words."""
    for left_bits, right_bits, output_bits, order in TERMS:
        a, *a_rest = (left[i] for i in left_bits)
        b, *b_rest = (right[i] for i in right_bits)
        c, *c_rest = (target[i] for i in output_bits)
        ports = {
            "a": iter((wire, a) for wire in a_rest),
            "b": iter((wire, b) for wire in b_rest),
            "c": iter((c, wire) for wire in c_rest),
        }
        basis = [(b"CX", *next(ports[side])) for side in order]
        yield from basis
        yield (b"CCX", a, b, c)
        yield from reversed(basis)


def validate_tensor():
    field = km.GF2Field(12)
    tensor = [tuple(reduce(xor, (1 << i for i in bits), 0) for bits in term[:3])
              for term in TERMS]
    for i, j in itertools.product(range(12), repeat=2):
        value = reduce(xor, (out for a, b, out in tensor if (a >> i) & (b >> j) & 1), 0)
        if value != field.mul(1 << i, 1 << j):
            raise ValueError(f"Recovered GF(2^12) tensor disagrees at basis pair {(i, j)}.")


def bind_term(gates, source, mapping, used):
    """Unify the symbolic operand wires with concrete KMX wires."""
    for (expected, *ports), row in zip(gates, source, strict=True):
        words = row.split()
        if words[0] != expected or len(words) != len(ports) + 1:
            return False
        for port, wire in zip(ports, words[1:], strict=True):
            if port in mapping:
                if mapping[port] != wire:
                    return False
            elif wire in used:
                return False
            else:
                mapping[port] = wire
                used.add(wire)
    return True


def emit_synthesis(source, output, template):
    """Regenerate complete, exact matches and retain all interstitial gates."""
    cursor = 0
    count = 0
    first_ccx = next(i for i, gate in enumerate(template) if gate[0] == b"CCX")
    first_size = 2 * first_ccx + 1
    for center, row in enumerate(source):
        start = center - first_ccx
        end = start + len(template)
        if not row.startswith(b"CCX ") or start < cursor or end > len(source):
            continue
        mapping, used = {}, set()
        if not bind_term(template[:first_size], source[start:start + first_size], mapping, used):
            continue
        if not bind_term(template[first_size:], source[start + first_size:end], mapping, used):
            continue
        if len(mapping) != 36:
            raise ValueError("Recovered multiplication does not bind three complete words.")
        words = tuple(tuple(mapping[base + bit] for bit in range(12)) for base in (0, 12, 24))
        regenerated = [b" ".join(gate) + b"\n" for gate in rank42_gates(*words)]
        if regenerated != source[start:end]:
            raise ValueError("Regenerated multiplication differs from the V5 gate window.")
        output.writelines(source[cursor:start])
        output.writelines(regenerated)
        cursor = end
        count += 1
    output.writelines(source[cursor:])
    return count


def regenerate(source, output):
    template = tuple(rank42_gates(range(12), range(12, 24), range(24, 36)))
    start = {f'INFO_TAG "@enter:{stage}"\n'.encode(): stage for stage in STAGES}
    counts = Counter()
    with source.open("rb") as incoming, output.open("wb") as outgoing:
        for row in incoming:
            if row not in start:
                outgoing.write(row)
                continue
            stage = start[row]
            outgoing.write(row)
            end = f'INFO_TAG "@exit:{stage}"\n'.encode()
            block = list(itertools.takewhile(lambda line: line != end, incoming))
            counts[stage] = emit_synthesis(block, outgoing, template)
            outgoing.write(end)
    if set(counts) != set(STAGES) or not all(counts.values()):
        raise ValueError(f"Missing rank-42 calls in V5 synthesis stages: {counts}")
    return dict(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    args = parser.parse_args()
    config = args.config.resolve()
    if config.parent != HERE / "configs" or not re.fullmatch(r"[a-zA-Z0-9_-]+\.json", config.name):
        parser.error("--config must resolve to a JSON in the experiment's configs directory.")
    if json.loads(config.read_text()) != {"mode": "rank42_reference", "reference_sha256": REFERENCE_SHA256}:
        parser.error("Unexpected config or V5 reference hash.")
    reference = args.reference.resolve()
    if digest(reference) != REFERENCE_SHA256:
        parser.error("--reference must be the pinned V5 KMB.")
    validate_tensor()
    output = REPO / "artifacts" / "dqi" / HERE.name / (config.stem + ".kmb")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(output)
    with tempfile.TemporaryDirectory(dir=output.parent) as workspace:
        workspace = Path(workspace)
        original = workspace / "original.kmx"
        regenerated = workspace / "regenerated.kmx"
        binary = workspace / "candidate.kmb"
        circuit = km.Circuit.from_file(str(reference), format="kmb")
        circuit.to_file(str(original), format="kmx")
        del circuit
        counts = regenerate(original, regenerated)
        candidate = km.Circuit.from_file(str(regenerated), format="kmx")
        stats = candidate.operation_statistics()
        candidate.to_file(str(binary), format="kmb")
        artifact_hash = digest(binary)
        if artifact_hash != REFERENCE_SHA256:
            raise ValueError(f"Rebuilt binary differs from pinned V5: {artifact_hash}")
        binary.replace(output)
    print(json.dumps({"status": "BUILT", "artifact": str(output), "sha256": artifact_hash,
                      "rank42_calls": counts, "tensor_basis_pairs": 144,
                      "qubits": candidate.num_qubits, "static_toffoli_like": stats.num_toffoli_like},
                     indent=2))


if __name__ == "__main__":
    main()
