# [INV-76] Build the notebook inverse-square-root circuit with time-multiplexed interpolation

Loại: Tinh chỉnh một phương án.

## Nguồn và phạm vi

The circuit and coefficient table come from orecord's Apache-2.0 notebook, cells 3–5. The [pinned notebook](https://www.kaggle.com/code/orecord/quantum-circuit-compilation-pipeline?scriptVersionId=372019840) and [circuit.py](circuit.py) document the source lineage. This experiment builds one native circuit family. The notebook's scored bundle artifacts are historical evidence for other implementations.

## Thuật toán

The 22-qubit input is normalized by the shared leading-bit chain and staged shifts. The parity and seven address bits select one of 256 coefficient rows. The builder splits the quadratic contribution into coarse and residual pieces, interpolates with the fixed-width updates in InvSqrtCfg, and reuses the lookup and arithmetic workspace. _adaptive_lookup changes lookup realization according to the table pattern. _folded_gadd and _shift_pruned keep the low and high arithmetic paths reversible.

## Điều kiện đúng và đánh đổi

The fixed integer table and rational phase angles preserve the upstream approximation. Scratch is cleared by inverse arithmetic or HMR. _demolish returns measurement outcomes to _repair_anf for address-dependent phase correction. The last joint top-normalization repair handles the parity and pending-measurement cases before the flags are freed. Correctness requires input restoration and phase within the official verifier tolerance across the 3,133,452-input domain.

## Kế hoạch kiểm chứng

Compare with INV-BASELINE at the same verifier settings. The notebook-native reference is SHA-256 f7fb315d23c7fbd020781eb88de818faf1b5e1bb04af65c98f34fd0e8f337ad1, 85 qubits and 39,789 instructions as measured in review. Predict byte identity for this source cleanup. Smoke checks 4,096 shots. Reject a hash mismatch, input restoration or phase error. Stop after the clean rebuild and one smoke check. Full grading is required for any cost claim.

## Cách dựng và bằng chứng

Run the repository Python 3.13 environment with requirements.txt and the [active config](configs/notebook-native.json).

    python src/invsqrt/INV-76/solution.py --config src/invsqrt/INV-76/configs/notebook-native.json

The active build compiles directly from the checkout. The former bundle configs are retained as archival names for existing results. Their original source/config snapshots remain in Git. Build records identify the actual source used. The verifier is a separate step.

## Kết quả kiểm chứng

A clean GitHub checkout of 8f07e38b0da4649115e00ab1ca285378a8982098 reproduced the native artifact SHA-256 f7fb315d23c7fbd020781eb88de818faf1b5e1bb04af65c98f34fd0e8f337ad1. kickmix-engine 0.6.0 smoke passed with 4,096 verified shots. Full grading and independent review of this revision are pending.

- [Build provenance](../../../results/invsqrt/INV-76/notebook-native/build_only/20261121T091941Z-build-d9eb213b/provenance.json)
- [Smoke verifier](../../../results/invsqrt/INV-76/notebook-native/smoke/20261121T091942Z-local-smoke-dc4244/verifier.json)
- [Smoke provenance](../../../results/invsqrt/INV-76/notebook-native/smoke/20261121T091942Z-local-smoke-dc4244/provenance.json)
