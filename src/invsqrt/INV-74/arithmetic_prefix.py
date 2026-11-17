"""Recover the normalization/consumed-root prefix using tracked arithmetic.

Syed Asad Ali's Apache-2.0 INV-51 helpers provide normalization and consumed
square root. Two explicit phase/frame schedules adapt their generated gates to
this Q44 artifact. This module reads no tape, table, bundle or original input.

For k=floor((22-bit_length(x))/2), n=x*4**k and R=floor(sqrt(16*n)),
the resulting root is v=R-4096, residual bits 1..9 are those of
h=(n-floor(R*(R+1)/16)-1) mod 1024, residual bit 0 is retired, and
flags encode k xor 12*(n mod 2). The root frame is exhaustively checked on
3,133,452 valid inputs with zero HMR outcomes; branch evidence is separate.
"""
from pathlib import Path
from types import SimpleNamespace
import importlib.util
import sys

import kickmix as km


def arithmetic_modules():
    """Load only normalization/root and their mathematical compiler primitives."""
    path = Path(__file__).resolve().parent.parent/'INV-51/circuit.py'
    spec = importlib.util.spec_from_file_location('_inv74_shared_arithmetic', path)
    source = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = source
    spec.loader.exec_module(source)
    # No INV-51 generator/data bundle is allowed. Missing math data fails closed.
    source._TABLES = {}
    def component(name, key):
        spec = source._Spec(name, source._VROOT/key)
        module = source._new_module(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    normal = component('_inv74_normalization', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn2df/normalization9475.py')
    root = component('_inv74_root', 'work/c10/narrow/arithmetic_round2/research/root_normalization/native_rn3/root192.py')
    patch = component('_inv74_narrow_normalization', 'patches/patch_fwd_narrow.py')
    patch.apply(SimpleNamespace(components={'normalization': normal}))
    return normal, root


class PrefixSchedule:
    """Place the recovered phase/frame changes on a freshly generated prefix.

The numeric boundary is a guarded compiler coordinate for a fixed target, not
an assumption that helper implementations can change without revalidation.
Other builder calls pass through unchanged, retaining allocator ownership.
"""

    def __init__(self, builder):
        self.builder = builder
        self.phase_inserted = False
        self.parity_inserted = False
        self.root_stage = False

    def __getattr__(self, name):
        return getattr(self.builder, name)

    def ccx(self, a, b, target):
        cb = self.builder
        if not self.root_stage and (a, b, target) == (km.q(36), km.q(1), km.q(21)):
            if self.phase_inserted or len(str(cb.finish_circuit()).splitlines()) != 208:
                raise RuntimeError('Normalization phase owner/schedule changed')
            cb.z_pow(km.q(35), '0.5')
            cb.z_pow(km.q(36), '1.5')
            cb.z_pow(km.q(21), '0.5')
            cb.ccx(a, b, target)
            cb.z_pow(km.q(21), '1.5')
            self.phase_inserted = True
        else:
            cb.ccx(a, b, target)

    def x(self, target):
        cb = self.builder
        if self.root_stage and not self.parity_inserted and target == km.q(36) and len(str(cb.finish_circuit()).splitlines()) == 1612:
            # q0 becomes normalized input parity and is framed into flags[2:4].
            cb.x(km.q(0))
            for i in (12, 13, 14, 36):
                cb.cx(km.q(i), km.q(0))
            for i in (24, 25):
                cb.cx(km.q(0), km.q(i))
            outcome = cb.alloc_bits(1)[0]
            if outcome != km.b(0):
                raise RuntimeError('Residual parity measurement owner changed')
            cb.hmr(km.q(0), outcome)
            cb.push_condition(outcome)
            cb.cz(km.q(24), km.q(25))
            cb.pop_condition()
            cb.free(outcome)
            cb.free(km.q(0))
            self.parity_inserted = True
        cb.x(target)


def create_prefix():
    """Return the 1649 generated prefix instructions, without register metadata."""
    normal, root = arithmetic_modules()
    builder = km.CircuitBuilder()
    builder.set_max_qubits(44)
    x = list(builder.alloc_qubits(22))
    flags = list(builder.alloc_qubits(4))
    schedule = PrefixSchedule(builder)
    normal.forward(schedule, x, flags)
    schedule.root_stage = True
    root.forward(schedule, x)
    lines = str(builder.finish_circuit()).splitlines()
    if not schedule.phase_inserted or not schedule.parity_inserted or len(lines) != 1649:
        raise RuntimeError('Arithmetic prefix schedule did not match fixed target')
    return builder,x,flags


def build_prefix():
    """Compile the prefix from its live arithmetic state."""
    builder,_,_=create_prefix()
    return str(builder.finish_circuit()).splitlines()
