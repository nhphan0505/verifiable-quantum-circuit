"""
Merged j-fraction extraction and forney phase correction.

The 70 syndrome words encode GF(2^12) moments. MergedJFractionDecoder uses 35 extraction steps, combining two slots per reciprocal where applicable. Pointer flags retain the location of gaps without a full flag bank. The conversion constructs the numerator and the monic locator polynomial from the continued fraction using field shears and explicit coefficient scaling. The reversible kernel uses the public vqcc_dqi_src source named in the notebook and its pinned projection, shared Forney word and pointer flags.

The projection changes the classical error masks using the known syndrome constraints. The Forney scan evaluates the numerator and derivative at each field position, uses one word for the locator root test and the controlled inverse, and applies the corresponding classical-mask-controlled phase. After each position, the live words are restored before advancing by constant field multipliers. The scan reverses its final multipliers. The converter and merged extractor then run in reverse and release the pointer flags. The official verifier checks both restored syndrome values and phase.

Run solution.py with configs/notebook-native.json in the repository Python
3.13 environment. The output is checked separately by the official verifier.
See NOTICE.md for upstream attribution.
"""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def build_circuit():
    helpers = [str(HERE / "decoder"), str(ROOT / "verifiers" / "dqi")]
    sys.path[:0] = helpers
    try:
        from jfraction_merged_decoder import MergedJFractionDecoder, StaticArithmeticBuilder, build

        return build(StaticArithmeticBuilder(), iterations=35, decoder_type=MergedJFractionDecoder)
    finally:
        del sys.path[:len(helpers)]
