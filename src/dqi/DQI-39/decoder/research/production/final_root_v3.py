"""Paid monic-root forward return and the degree-12 interior return."""
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'research/agents' / name)
                for name in ('a22', 'a16', 'a18', 'a08', 'a01')]
spec = importlib.util.spec_from_file_location(
    'root_return_clean_control', ROOT / 'research/production/selected.py')
reference = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = reference
spec.loader.exec_module(reference)

import scalar_compact_v3 as scalar
from rebind_graph import private_rebind
import three_borrowed_bit_v2 as borrowed
import dot_one_word
import forward_return
import forward_cache_shift
import root_forward_return_v3

decode = private_rebind(reference.decode, {}, scalar.p.ROOT)
cv = scalar.converter_of(decode)
borrowed.install(cv)
dot_one_word.install(cv, scalar)
forward_cache_shift.install(cv, scalar, levels=(8, 5))
root_forward_return_v3.install(cv, scalar, retire_root=True)
forward_return.install(cv, scalar, top=12)
