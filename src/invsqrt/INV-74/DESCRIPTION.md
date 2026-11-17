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
metadata. These are upstream reported values; the measured local full result is documented below. The private Q44 generator/search was not
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

Complete arithmetic source `c843a80857d8f42e5c9d7113ae547417e0f58b2f` built from a fresh
GitHub clone and a new pinned venv, invoked from outside the checkout. The
entry point produced exactly 200369 bytes and the input SHA-256. A separate
stream comparison checked every byte. See [clean build](../../../results/invsqrt/INV-74/reconstructed/build_only/20261117T160232Z-exact-e9c11e96/clean_checkout_build.json),
[byte comparison](../../../results/invsqrt/INV-74/reconstructed/build_only/20261117T160232Z-exact-e9c11e96/byte_comparison.json) and
[dependency audit](../../../results/invsqrt/INV-74/reconstructed/build_only/20261117T160232Z-exact-e9c11e96/dependency_audit.json).
Run `20261117T160232Z-exact-e9c11e96` is build-only and establishes `RECONSTRUCTED_EXACT` for this
arithmetic snapshot. Later description/manifest changes do not change its
source commit. The audit rejected an earlier unused model dependency; the
accepted build uses a local mathematical layout permutation instead.

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

## Local notebook handoff

The local KMB is `artifacts/invsqrt/INV-74/reconstructed.kmb`; paired config:
`src/invsqrt/INV-74/configs/reconstructed.json`. Actual build provenance and
hashes are linked in [delivery.json](delivery.json). A fresh build of source
`12d971d5d2a6f8b8b3ef20e30eaeaf73d9416716` matches every original byte. The
notebook selection functions were executed without running the verifier and
confirmed INV-74 / reconstructed is discoverable. Refresh the list and select
that ID; selecting INV-41 uses a different experiment's config directory.

Git excludes `artifacts/`, and the repository checker rejects tracked KMBs.
Therefore pulling this branch supplies JSON/source/provenance; the KMB must
be generated locally or obtained separately. The measured smoke/full results and their build links are recorded below.

## Measured results and review handoff

Source/config build commit: `12d971d5d2a6f8b8b3ef20e30eaeaf73d9416716`.
The KMB installed from that clean build was used for both local notebook runs;
its hash is the original target hash. The original `review.json` records the
notebook's ambiguous-build warning because three builds have identical output.
It is preserved. Added `provenance.json` and `review_v2.json` link the actual
handoff build and validate the recorded profile, source, verifier and hashes.
These are author checks, not an independent review.

| Mode | Run | Result | Score | Shots |
| --- | --- | --- | ---: | ---: |
| smoke | [20261117T163400Z-local-smoke-62712d](../../../results/invsqrt/INV-74/reconstructed/smoke/20261117T163400Z-local-smoke-62712d/verifier.json) | PASS | 73630.74893951333 | 4096 |
| full | [20261117T163551Z-local-full-50ae76](../../../results/invsqrt/INV-74/reconstructed/full/20261117T163551Z-local-full-50ae76/verifier.json) | PASS | 75170.62025728542 | 200540928 |

Full uses the official invsqrt verifier, kickmix-engine 0.6.0, four threads and
no reduced-domain/shot options. Smoke uses max-x 4096 and one shot per input.
Both recorded stdout JSONs exactly match verifier.json; stderr is empty. Both
use WSL Linux, Python 3.13.18, AVX2; the Windows build used Python 3.13.7. Pins
kickmix/numpy/scipy are unchanged. See metadata and provenance for both contexts.
No seed override is recorded; the command and engine defaults define the run.

Baseline full cost 2076774.233715282 divided by INV-74 full 75170.62025728542
is **27.6274723636x**, a **96.380414441%** cost reduction. Only full is entered
in SCORES; smoke is retained for its limited verification scope. Q44 uses
1458.2501961744188 mean Toffolis, 1 T and 34 rotations in the full record.
Worst error/tolerance is 0.9912046209041316 at x=191189, below the limit but
close to it; this measured PASS is not an analytic approximation-error proof.
The small difference from the upstream reported 75170.66 is kept explicit.

The reconstruction hypothesis (independent arithmetic source reproduces the
original KMB exactly) is supported by byte comparison and the recorded full
PASS. No further optimization was implemented or claimed. Stop this recovery
stage and request independent review; do not infer recovery of the private
search/refit. [grading_summary.json](evidence/grading_summary.json) contains
ratios, run/build links and immutable raw-file hashes.

Reviewer setup: fresh clone, checkout the build source commit above, create a
new Python 3.13 venv and install requirements.txt. Invoke solution.py using
absolute source/config paths from a cwd outside the checkout. Expected KMB is
200369 bytes with the target SHA-256. Check dependency_audit.json against the
committed helpers/data, then inspect the forward/inverse carry and table phase
contracts. All runtime inputs and license notices are committed; no author
bundle is required. Independent code review and merge remain outstanding.
