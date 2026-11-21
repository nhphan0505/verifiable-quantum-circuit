"""Load the installed competition helpers without vendoring competition data."""

import kickmix as km
import dqi_reference_circuit as ref


def build(builder, *, iterations=None, decoder_type=None):
    """Build the official decoder, allowing a builder with alternative arithmetic."""
    syndromes = [builder.create_quantum_register(12, name=f'S{i}') for i in range(70)]
    outcomes = [builder.create_classical_register(12, name=f'E{j}') for j in range(4095)]
    decoder_type = ref.ProosAndZalkaDecoder if decoder_type is None else decoder_type
    decoder_type(70, km.GF2Field(12)).build_syndrome_decoding_mbuc(
        builder, syndromes=syndromes, error_mbuc=outcomes,
        n_iters=ref.default_n_iters(70) if iterations is None else iterations)
    return builder.finish_circuit()
