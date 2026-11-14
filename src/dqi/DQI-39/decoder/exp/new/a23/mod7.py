"""Ancilla-free eleven-Toffoli addition of logarithmic codes modulo seven.

Codes 0..6 are residues; target code7 is a fixed exceptional value and
source code7 acts as residue0. No measurement or phase is introduced.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'exp/new/a16'), str(ROOT / 'exp/new/a10'),
               str(ROOT / 'exp/new/a07')]
from lowclean_norm5 import permutation3
import logscale7


def add_mod7(b, target, source, inverse=False):
    assert len(target) == len(source) == 3
    permutation3(b, target, 'log', True)
    logscale7.scale(b, target, source, inverse)
    permutation3(b, target, 'log')
