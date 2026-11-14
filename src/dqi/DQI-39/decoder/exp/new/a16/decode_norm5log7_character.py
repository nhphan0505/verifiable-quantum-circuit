"""A14 nine-companion character decoder with five-Toffoli GF8 norm multiplication.

Install the arithmetic module before constructing the decoder graph.  The
replacement changes only coherent scalar contexts on proved norm domains.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(ROOT / 'exp/new/a10'),
               str(ROOT / 'exp/new/a07'), str(ROOT / 'exp/new/a14')]
import lowclean_norm5log7 as arithmetic

assert 'decode_owner' not in sys.modules
sys.modules['lowclean_shared'] = arithmetic
import decode_nine_character as prior
body = prior.body
from install_log7 import install
INSTALL_LOG = install(body)


def decode(b, S, E):
    return body(b, S, E)
