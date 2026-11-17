# [INV-74] Tái dựng Fusion 44 qubit bằng Python và phục hồi số học từ KMX

Original builder: **Syed Asad Ali**, dataset `syed3000/vqcc-own-circuit-portfolio`.
Independent arithmetic reconstruction; see [NOTICE](NOTICE.txt) and
[Apache-2.0](LICENSE.txt). Issue #74, branch
`exp/INV-74-fusion44-reconstruction`, owner `Cheemshoang`, draft PR #75.

## Input and conversion

`invsqrt_x2763.kmb`: 200369 bytes, SHA-256
`47b318383a03c52e08a5c222c5600fd52e004b468f53fad038082fc0f26386ef`.
44 qubits, register x[0:22], 24132 operations. KMB → KMX → KMB was checked
before reconstruction; the latest separate KMX → KMB check also matched every
byte. Original input is immutable and is never read by solution.py.

The supplied Q44 cost 75170.66 and ratio 27.63× agree with the upstream dataset
metadata. These are upstream reported values; this work has no new verifier
score, PASS or improvement claim. The private Q44 generator/search was not
available and is not claimed recovered.

## Arithmetic generator

The source now composes words and measured carry debts throughout, following
the module structure used by INV-66. There is no expanded gate list, original
KMX/KMB, compressed submission or external bundle in the runtime inputs.

- `circuit.py`: live allocator composition, inverse normalization and original
  input/register layout.
- `arithmetic_prefix.py`: normalized consumed square root and recovered parity
  frame. For k=floor((22-bit_length(x))/2), n=x*4**k, R=isqrt(16*n), the root
  fraction is v=R-4096 and residual is
  h=(n-floor(R*(R+1)/16)-1) modulo 1024. The first residual bit is packed into
  flags until seed/product unfolds it.
- `lookup.py`, `data/coefficient_codes.json`: two six-input Boolean coefficient
  codebooks. Invertible GF(2) matrices and factored quadratic coordinates
  replace lookup gate calls; measured coordinates retain 64-codeword truths.
- `coefficient.py`: 64 intercepts/slopes, six rounded signed interpolation rows,
  low-byte arithmetic and a deferred high-word overflow.
- `seed_product.py`: three signed seed rows, folded residual parity and ten
  rounded product rows; returns mandatory inverse carry tokens.
- `divider.py`, `divider_inverse.py`: triangular remainder initializer, 24
  balanced feed/rotate rows and inverse recurrence. `data/history_code.json`
  is the seven-input Boolean sign-15 restoration certificate.
- `phase.py`, `phase_parameters.py`: N27 reflected phase walk with 27 base and
  seven overflow angles, root/history borrowing and exact phase repayment.
- `return_path.py`, `data/cleanup_codes.json`: return interpolation, inverse
  product/seed, early slope retirement, six-bit address decoder and repayment
  of every table measurement phase. Every quadratic phase is checked over all
  64 table codewords. The last two coordinates use three conditioned helper
  charts with polynomial identities checked at construction.
- `arithmetic_body.py`: shared mathematical compiler context and forward body.
  Selected helpers come from tracked `../INV-51/circuit.py`; its data bundle is
  disabled. `solution.py` audits all declared source/data/runtime reads.

Data certificates contain small Boolean mathematical problems, with no opcode
stream, physical owner lists, measurement IDs, rotation tape or whole-circuit
program. Allocation and finishing slots remain fixed because byte-exact
reconstruction is the target. This is an independently recovered arithmetic
implementation, not the original source, numerical fit or search procedure.

## Evidence and current acceptance

Isolated component reconstruction matched each original operation through the
normalization inverse at boundary 24120. Input-layout restoration accounts for
the final 12 operations. Full entry-point build from a fresh GitHub checkout
must validate the composed allocator and exact KMB after the source commit.
The current arithmetic source has not yet been accepted on the strength of a
previous gate-level build.

Historical clean build source `36553eb7800dfa7afd1185aaf924297219642dc3`
matched all bytes; its immutable records remain at
`results/invsqrt/INV-74/reconstructed/build_only/20261117T112724Z-exact-4e8c34e8`.
The forward arithmetic checkpoint `8059cdf4bc8caeb6f7eca9421402fe604fbf87b9`
also built exact from a fresh clone/venv. Those runs are distinct from the
current complete arithmetic source.

Root/frame semantics were checked for all 3,133,452 valid x with zero HMR
outcomes (`evidence/exhaustive_root.json`). A separate 141-input check used
zero plus four random measurement streams per input, preserving x, scratch
zero and phase (`evidence/branch_analysis.json`). These are semantic analysis,
not a verifier run or a complete approximation-error proof.

No new postprocessing rewrite is applied. The conservative INV-66 dead-write
CCX→HMR/CZ guard found zero candidates (`evidence/pp_guard_scan.json`). Any
future improvement needs a separately scoped experiment and measured score.

## Reproduce

Use a clean checkout of the source commit and a fresh Python 3.13 venv; install
`requirements.txt`. Run `src/invsqrt/INV-74/solution.py` with absolute `--config`
pointing to this checkout's `configs/reconstructed.json`, from any cwd. Output:
`artifacts/invsqrt/INV-74/reconstructed.kmb`. New records:
`results/invsqrt/INV-74/reconstructed/build_only/<run-id>/`. Existing output is
never overwritten. No smoke/full grading, independent review or merge is
claimed by a build-only record.
