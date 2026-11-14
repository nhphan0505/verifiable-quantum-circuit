"""Generate the q26 DQI circuit from the Python sources included with DQI-39.

The q26 carry implementation is from Atakan Aldemir's QCC C44 Five Helper
Release Sources v1. See DESCRIPTION.md for attribution and build instructions.
The build starts from the decoder's Python functions and compiler plans.
"""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys
import tempfile

import kickmix as km


CONFIGS = Path(__file__).resolve().parent / "configs"
WORD_BITS = 12
SYNDROME_WORDS = 70
POSITIONS = 4095


def emit_decoder(builder, syndromes, masks, decoder, repair):
    """Project masks, extract and synthesize, apply phase, then restore inputs."""
    # Upstream modules use `circ` as the name of the Kickmix builder API.
    sys.modules["circ"] = km
    sys.path.insert(0, str(decoder))
    import decode_carry_round7  # Installs the upstream flag-carry transformations.
    if repair:
        sys.path.insert(0, str(decoder.parent / "tools"))
        from q26_transfer_build import install_retention

        # Group 4 can encounter an intermediate pole. Retain its own flag
        # and keep its return independent of the existing groups 5–16.
        entry = decode_carry_round7.decode
        from walk_bound import functions

        selected = set(range(4, 17))
        # The deferred normalization wrapper has its own routing table.
        # Extend both directions so group 4 has the matching gauge token.
        from direct_deferred_companion import forward_deferred

        scopes = {id(fn.__globals__): fn.__globals__ for fn in functions(entry)}
        for scope in scopes.values():
            if "_a18_deferred_select" not in scope:
                continue
            scope["_a18_deferred_select"] |= {4}
            original = scope["forward_original"]
            reference = scope["ref"]

            def forward(b, words, gi, reverse=False, token=None, normalizer=None,
                        *, original=original, reference=reference):
                if gi == 4 and not reverse:
                    return forward_deferred(b, words, gi, reference)
                return original(b, words, gi, reverse, token, normalizer)

            scope["forward_original"] = forward
        install_retention(entry, decoder, {4, 16}, selected, False, {})
        entry(builder, syndromes, masks)
        return

    from decode_norm_deferred_flag_unsynthesis import g, consume_synthesis, route_words

    project_masks = g["baseline"].project
    restore_masks = g["baseline"].restore
    transform_syndromes = g["linear_words"]
    extract = g["extraction"]
    synthesize = g["synthesize"]
    convert = g["convert_safe"]
    scan = g["baseline"].scan

    with builder.mark("mask_projection"):
        saved_masks = project_masks(builder, syndromes, masks)
    with builder.mark("initial"):
        transform_syndromes(builder, syndromes, g["matrix"])
    with builder.mark("extract"):
        extraction = extract(builder, syndromes)
    with builder.mark("synthesis"):
        locator, evaluator, undo = synthesize(builder, syndromes, extraction["pole"])
    with builder.mark("convert"):
        token = convert(builder, locator, evaluator, monic_root=True)
    with builder.mark("scan"):
        scan(builder, locator, evaluator, masks, skip_points=g["baseline"].SELECTED,
             node_polynomial=g["Pscan"])
    with builder.mark("unconvert"):
        convert(builder, locator, evaluator, True, phase_token=token)
    with builder.mark("padded_unsynthesis"):
        heads, tail = consume_synthesis(builder, locator, evaluator, extraction["pole"], undo)
        route_words(builder, [wire for group in heads for wire in group] + tail, syndromes)
    with builder.mark("unextract"):
        extract(builder, syndromes, True, extraction)
    with builder.mark("uninitial"):
        transform_syndromes(builder, syndromes, g["matrix"], True)
    with builder.mark("restore_masks"):
        restore_masks(builder, masks, saved_masks)


def build_circuit(decoder, repair=False):
    builder = km.CircuitBuilder()
    syndromes = [builder.alloc_qubits(WORD_BITS) for _ in range(SYNDROME_WORDS)]
    masks = [builder.alloc_bits(WORD_BITS) for _ in range(POSITIONS)]
    emit_decoder(builder, syndromes, masks, decoder, repair)

    # Match q26's published register serialization.
    declarations = []
    for prefix, wire, count, register_offset in (
        ("S", "q", SYNDROME_WORDS, 0), ("E", "b", POSITIONS, SYNDROME_WORDS)
    ):
        for index in range(count):
            register = register_offset + index
            declarations.append(f'REGISTER r{register} "{prefix}{index}"')
            declarations.extend(
                f"APPEND_TO_REGISTER {wire}{WORD_BITS * index + bit} r{register}"
                for bit in range(WORD_BITS)
            )
    return km.Circuit("\n".join(declarations)) + builder.finish_circuit()


def cancel_cnot_runs(source, target):
    """Cancel CX pairs across commuting CX gates, within bounded runs.

    A CX(a,b) commutes with CX(c,d) exactly when a != d and b != c,
    for distinct wires within each gate. Other instructions end a run.
    """
    pending = []
    last_pair = {}
    writes = {}
    reads = {}
    removed = 0

    def flush():
        target.writelines(row for row in pending if row is not None)
        pending.clear()
        last_pair.clear()
        writes.clear()
        reads.clear()

    for row in source:
        if row.startswith(b"CX "):
            _, left, right, *suffix = row.split()
            if not suffix:
                key = left, right
                previous = last_pair.get(key, -1)
                if previous >= 0 and previous > max(writes.get(left, -1), reads.get(right, -1)):
                    pending[previous] = None
                    del last_pair[key]
                    removed += 2
                else:
                    last_pair[key] = len(pending)
                    writes[right] = len(pending)
                    reads[left] = len(pending)
                    pending.append(row)
                if len(pending) >= 16384:
                    flush()
                continue
        if pending:
            flush()
        target.write(row)
    if pending:
        flush()
    return removed


def optimize(original, output):
    circuit = km.Circuit.from_file(str(original), format="kmb")
    before = circuit.operation_statistics()
    source = original.with_suffix(".kmx")
    rewritten = original.with_name("rewritten.kmx")
    circuit.to_file(str(source), format="kmx")
    registers = dict(circuit.register_data)
    width = circuit.num_qubits, circuit.num_bits
    del circuit
    with source.open("rb") as incoming, rewritten.open("wb") as outgoing:
        removed = cancel_cnot_runs(incoming, outgoing)
    candidate = km.Circuit.from_file(str(rewritten), format="kmx")
    after = candidate.operation_statistics()
    if (candidate.num_qubits, candidate.num_bits) != width or dict(candidate.register_data) != registers:
        raise ValueError("Register interface changed")
    if after.num_toffoli_like != before.num_toffoli_like or before.num_instructions - after.num_instructions != removed:
        raise ValueError("Unexpected resource change")
    candidate.to_file(str(output), format="kmb")
    with output.open("rb") as stream:
        sha = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"sha256": sha, "qubits": width[0], "classical_bits": width[1],
            "static_toffoli_like": after.num_toffoli_like, "instructions": after.num_instructions,
            "cnot_removed": removed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIGS / "q26_homogeneous_group4.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    output = args.output.resolve()
    if output.suffix != ".kmb" or version("kickmix") != "1.0.0":
        parser.error("Use a .kmb output path and Kickmix 1.0.0.")
    if output.exists():
        parser.error("Choose a fresh output path.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as directory:
        workspace = Path(directory)
        decoder = Path(__file__).resolve().parent / "decoder"
        repair = config.get("homogeneous_group4", False)
        generated = workspace / "generated.kmb"
        print("Generating q26 from Python", flush=True)
        build_circuit(decoder, repair).to_file(str(generated), format="kmb")
        print("Canceling commuting CNOT pairs", flush=True)
        candidate = workspace / "optimized.kmb"
        report = optimize(generated, candidate)
        # Publish without replacing another build's output.
        output.hardlink_to(candidate)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
