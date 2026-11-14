"""The front half with the conversion pair, on the base's boundary."""
from pathlib import Path
import importlib.util
import sys
import types

import circ

ROOT = Path(__file__).resolve().parent


def _registers_as_lists(builder):
    """The root blocks replace a register in place, so registers are Python lists, not the builder's arrays."""
    alloc_qubits, alloc_bits = builder.alloc_qubits, builder.alloc_bits
    builder.alloc_qubits = lambda self, n: list(alloc_qubits(self, n))
    builder.alloc_bits = lambda self, n: list(alloc_bits(self, n))


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_registers_as_lists(circ.CircuitBuilder)
front = _load('q9_front', ROOT/'decode_frontier.py').decode
_load('ported', ROOT/'research/production/ported.py')
back = _load('selected_round_two', ROOT/'research/production/final_root_v3.py').decode
g = dict(zip(back.__code__.co_freevars, back.__closure__))['g'].cell_contents
scope = dict(front.__globals__, convert_safe=g['convert_safe'], baseline=g['baseline'])
decode = types.FunctionType(front.__code__, scope, front.__name__, front.__defaults__, front.__closure__)
