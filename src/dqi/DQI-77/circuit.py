"""Emit the merged J-fraction decoder named in the attached notebook.

The public Apache-2.0 source uses 35 extraction steps, pointer flags,
mask projection, and the shared Forney inverse word. See NOTICE.md.
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
