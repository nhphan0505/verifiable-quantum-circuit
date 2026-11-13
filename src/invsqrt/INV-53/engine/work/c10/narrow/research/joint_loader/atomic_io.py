# Copyright 2026 Syed Asad Ali. SPDX-License-Identifier: Apache-2.0.
# Adapted for INV-53; upstream credits retained in NOTICE and lineage manifest.
"""Atomic branch artifacts so an overlapping parent checkpoint is coherent."""
from pathlib import Path as _IntegratedPath
INTEGRATED_ROOT = _IntegratedPath(__file__).resolve().parents[5]
import os
from pathlib import Path

def atomic_text(path, text):
    path = Path(path)
    temporary = path.with_name('.' + path.name + '.tmp.' + str(os.getpid()))
    temporary.write_text(text)
    os.replace(temporary, path)
