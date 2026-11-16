"""Compare complete measurement-branch operators, not gate counts alone."""
from pathlib import Path
import importlib.util
import io
import unittest

import kickmix as km
import numpy as np

path = Path(__file__).resolve().parents[1] / 'postprocessing' / 'solution.py'
spec = importlib.util.spec_from_file_location('pp005', path)
pp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pp)


def text(circuit):
    out = io.StringIO()
    circuit.to_file(out, format='kmx')
    return out.getvalue()


def branch_operator(circuit, outcomes):
    """Independent dense semantics, with fixed outcomes for each measured bit.

Every column is an arbitrary input basis vector. Equality of these matrices
therefore covers coherent/entangled targets without an initial-zero premise.
"""
    size = 1 << circuit.num_qubits
    state = np.eye(size, dtype=complex)
    indices = np.arange(size)
    bits = {}
    for line in text(circuit).splitlines():
        t = line.split()
        if not t or t[0] in {'REGISTER', 'APPEND_TO_REGISTER'}:
            continue
        if 'if' in t:
            if not bits.get(t[-1], 0):
                continue
            t = t[:-2]
        op, args = t[0], t[1:]
        if op in {'X', 'CX', 'CCX'}:
            qs = [int(q[1:]) for q in args]
            active = np.ones(size, dtype=bool)
            for control in qs[:-1]:
                active &= ((indices >> control) & 1) != 0
            permutation = indices.copy()
            permutation[active] ^= 1 << qs[-1]
            state = state[permutation]
        elif op == 'CZ':
            a, b = (int(q[1:]) for q in args)
            phase = 1 - 2 * (((indices >> a) & (indices >> b)) & 1)
            state = phase[:, None] * state
        elif op == 'HMR':
            target = int(args[0][1:])
            outcome = outcomes[args[1]]
            bits[args[1]] = outcome
            rows = indices[(indices & (1 << target)) == 0]
            result = np.zeros_like(state)
            result[rows] = (state[rows] + (-1)**outcome * state[rows | (1 << target)]) / np.sqrt(2)
            state = result
        else:
            raise AssertionError('Unsupported dense test instruction: ' + line)
    return state


class Rewrite(unittest.TestCase):
    def equivalent(self, source, outcomes=({'b0': 0}, {'b0': 1})):
        original = km.Circuit(source)
        unchanged = text(original)
        candidate, count = pp.rewrite(original, operation_index=0)
        self.assertEqual(count, 1)
        self.assertEqual(text(original), unchanged)
        for outcome in outcomes:
            np.testing.assert_allclose(branch_operator(original, outcome),
                                       branch_operator(candidate, outcome), atol=1e-14)

    def test_arbitrary_target_state(self):
        self.equivalent('CCX q0 q1 q2\nHMR q2 b0\n')

    def test_controls_change_in_between(self):
        self.equivalent('CCX q0 q1 q2\nX q0\nCX q0 q1\nHMR q2 b0\n')

    def test_other_measurement_commutes(self):
        self.equivalent('CCX q0 q1 q2\nHMR q3 b1\nHMR q2 b0\n',
                        tuple({'b0': a, 'b1': b} for a in (0, 1) for b in (0, 1)))

    def test_target_read_rejected(self):
        c = km.Circuit('CCX q0 q1 q2\nCX q2 q3\nHMR q2 b0\n')
        self.assertEqual(pp.rewrite(c, operation_index=0)[1], 0)

    def test_target_write_rejected(self):
        c = km.Circuit('CCX q0 q1 q2\nX q2\nHMR q2 b0\n')
        self.assertEqual(pp.rewrite(c)[1], 0)

    def test_measurement_bit_read_rejected(self):
        c = km.Circuit('CCX q0 q1 q2\nCZ q0 q1 if b0\nHMR q2 b0\n')
        self.assertEqual(pp.rewrite(c)[1], 0)

    def test_measurement_bit_write_rejected(self):
        c = km.Circuit('CCX q0 q1 q2\nBIT_INVERT b0\nHMR q2 b0\n')
        self.assertEqual(pp.rewrite(c)[1], 0)

    def test_condition_scope_rejected(self):
        c = km.Circuit('PUSH_CONDITION if b1\nCCX q0 q1 q2\nHMR q2 b0\nPOP_CONDITION\n')
        self.assertEqual(pp.rewrite(c)[1], 0)

    def test_condition_barrier_rejected(self):
        c = km.Circuit('CCX q0 q1 q2\nPUSH_CONDITION if b1\nX q0\nPOP_CONDITION\nHMR q2 b0\n')
        self.assertEqual(pp.rewrite(c)[1], 0)

    def test_registers_and_exact_angles_preserved(self):
        c = km.Circuit('APPEND_TO_REGISTER q0 r0\nREGISTER r0 "x"\nCCX q0 q1 q2\nZ_POW q0 0.0000000000000000000001\nHMR q2 b0\n')
        out, count = pp.rewrite(c, operation_index=0)
        self.assertEqual(count, 1)
        self.assertEqual(str(c.register_data), str(out.register_data))
        self.assertEqual([s for s in text(c).splitlines() if s.startswith('Z_POW')],
                         [s for s in text(out).splitlines() if s.startswith('Z_POW')])

    def test_only_one_selected_site(self):
        c = km.Circuit('CCX q0 q1 q2\nHMR q2 b0\nCCX q0 q1 q3\nHMR q3 b1\n')
        out, count = pp.rewrite(c, operation_index=2)
        self.assertEqual(count, 1)
        self.assertTrue(text(out).startswith('CCX q0 q1 q2\nHMR q2 b0\n'))

    def test_invalid_indices(self):
        for index in (-1, True, 1.5, '0', 99):
            with self.subTest(index=index), self.assertRaises(ValueError):
                pp.rewrite(km.Circuit('X q0'), operation_index=index)

    def test_no_candidate(self):
        c = km.Circuit('CX q0 q1\n')
        self.assertEqual(pp.rewrite(c), (c, 0))


if __name__ == '__main__':
    unittest.main()
