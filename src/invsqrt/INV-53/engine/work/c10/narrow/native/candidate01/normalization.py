# Copyright 2026 Syed Asad Ali. SPDX-License-Identifier: Apache-2.0.
# Adapted for INV-53; upstream credits retained in NOTICE and lineage manifest.
"""Native binding of the frozen, independently proved pair-normalization map."""
from pathlib import Path as _IntegratedPath
INTEGRATED_ROOT = _IntegratedPath(__file__).resolve().parents[5]
from common import *
import importlib.util
PATH = NARROW / 'research/quantized_producer/pair_normalization.py'
SHA = '6af7fc14bc3c904efe480e2e23aee2fcbd97ad23f0a7ba324d8c05e1c8ec17fe'
pass
spec = importlib.util.spec_from_file_location('native_pair_normalization_source', PATH)
source = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = source
spec.loader.exec_module(source)
forward = source.forward
inverse = source.inverse
MAX_X = source.MAX_X
