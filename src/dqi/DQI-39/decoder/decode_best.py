"""Convenience alias for the exact final measured decoder function.

The import cleanup is host-only and is the same cleanup used by run_suite.
There is no builder, shot, seed, measurement, or input inspection here.
"""
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'exp/new/root'), str(ROOT/'playbook/kit')]
from loader_cache import install
install()
_spec = importlib.util.spec_from_file_location('selected_decoder_implementation', ROOT / 'exp/new/root/decode_norm5log7.py')
_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)
decode = _module.decode

from loader_prune import prune
LOADER_MEMORY = prune()
