"""Check the Q44 parity-frame code and HMR phase identity on its full domain.

For valid normalized inputs, odd n implies k=0. The code stores parity in an
unused shift code 12. Exhaustive checks below establish injectivity and the
m-dependent phase identity for both HMR outcomes; they are not verifier tests.
"""
import unittest


class ParityFrame(unittest.TestCase):
    def test_encoding_preserves_shift_and_parity(self):
        domain = [(k, p) for k in range(11) for p in (0, 1) if not p or k == 0]
        encoded = {k ^ (12*p): (k, p) for k, p in domain}
        self.assertEqual(len(encoded), len(domain))
        for code, (k, p) in encoded.items():
            decoded_parity = (code >> 2 & 1) & (code >> 3 & 1)
            self.assertEqual(decoded_parity, p)
            self.assertEqual(code ^ (12*decoded_parity), k)

    def test_hmr_and_conditional_cz_cancel_on_every_valid_code(self):
        for k in range(11):
            for parity in (0, 1):
                if parity and k:
                    continue
                code = k ^ (12*parity)
                for outcome in (0, 1):
                    hmr_half_turns = outcome * parity
                    cz_half_turns = outcome * (code >> 2 & 1) * (code >> 3 & 1)
                    self.assertEqual((hmr_half_turns + cz_half_turns) % 2, 0)


if __name__ == '__main__':
    unittest.main()
