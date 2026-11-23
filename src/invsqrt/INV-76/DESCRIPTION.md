# [INV-76] Build the notebook inverse-square-root circuit with time-multiplexed interpolation

Loại: Tinh chỉnh một phương án.

## File gốc

The upstream [orecord notebook, v25](https://www.kaggle.com/code/orecord/quantum-circuit-compilation-pipeline?scriptVersionId=372019840) (script version 372019840, cells 3–5) supplies the Apache-2.0 builder and all 256 coefficient rows. This experiment ports that builder into [circuit.py](circuit.py), with repository-native build and provenance handling in [solution.py](solution.py). The port preserves the arithmetic, coefficient table and phase cleanup.

## Phần tinh chỉnh và lý do

Use time-multiplexed interpolation as an independently reproducible alternative to the division-based circuits. The hypothesis is that adaptive lookup and early workspace reuse can lower conditional reaction depth enough to make this architecture useful even if its wider register increases total verification cost.

## Thuật toán

The 22-qubit input is normalized by the shared leading-bit chain and staged shifts. The parity and seven address bits select one of 256 coefficient rows. The builder splits the quadratic contribution into coarse and residual pieces, interpolates with the fixed-width updates in InvSqrtCfg, and reuses the lookup and arithmetic workspace. _adaptive_lookup changes lookup realization according to the table pattern. _folded_gadd and _shift_pruned keep the low and high arithmetic paths reversible.

## Điều kiện đúng và đánh đổi

The fixed integer table and rational phase angles preserve the upstream approximation. Scratch is cleared by inverse arithmetic or HMR. _demolish returns measurement outcomes to _repair_anf for address-dependent phase correction. The last joint top-normalization repair handles the parity and pending-measurement cases before the flags are freed. Correctness requires input restoration and phase within the official verifier tolerance across the 3,133,452-input domain.

## Kế hoạch kiểm chứng hypothesis

- **Mốc đối chứng.** Use the [official INV-BASELINE full run](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/872bb089cbf62931fd156f5c86243c7bd053c9a0/results/invsqrt/INV-BASELINE/baseline/full/20261113T183503Z-local-full-35f777/verifier.json) as the reference for improvement over the original method. The team's published full references are [INV-74 full](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/91518ae1fda0dd8d272bc841861eab6b74ad82a7/results/invsqrt/INV-74/reconstructed/full/20261117T163551Z-local-full-50ae76/verifier.json) (44 qubits, cost 75,170.62) and [INV-66 full](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/f315c15b5828166e011e91388c2bdf97a54a77f9/results/invsqrt/INV-66/reconstructed/full/20261115T042258Z-local-full-7feec4/verifier.json) (46 qubits, cost 78,719.53), both with engine 0.6.0 and 200,540,928 verified shots. INV-74 is the cost target.
- **Dự đoán.** Width is fixed at 85 qubits. The smoke run shows reaction depth 206 and approximately 1,826 Toffoli-equivalents per shot. These motivate a lower-depth comparison, while the full cost target at 85 qubits requires fewer than 884.36 Toffoli-equivalents per shot. The smoke resource numbers make a cost win unlikely.
- **Ủng hộ / bác bỏ.** On the official full profile, require a verifier PASS and cost below 75,170.62025728542 to support a claim of lower cost than INV-74. A full PASS above that threshold with reaction depth below INV-74's 1,282 supports the alternate architecture's depth advantage only. Compare with INV-66 as a secondary reference. A verifier failure rejects this candidate.
- **Điều kiện dừng.** Stop after one full run of the pinned candidate. If cost misses INV-74, retain it as a depth reference only if the full run confirms the depth advantage. Any further change to precision, workspace, or phase cleanup requires a separate iteration.
- **Kiểm tra ứng viên cuối.** Rebuild the committed notebook-native config and confirm its SHA-256 f7fb315d23c7fbd020781eb88de818faf1b5e1bb04af65c98f34fd0e8f337ad1. Use kickmix-engine 0.6.0, matching verifier revision, official full settings and the same seed or salt where configurable. Re-run the comparator if the verifier or profile differs. The existing smoke run checks basic validity and supplies preliminary resource estimates. Its cost is kept separate from full results.

## Cách dựng và bằng chứng

Run the repository Python 3.13 environment with requirements.txt and the [active config](configs/notebook-native.json).

    python src/invsqrt/INV-76/solution.py --config src/invsqrt/INV-76/configs/notebook-native.json

The active build compiles directly from the checkout. The former bundle configs are retained as archival names for existing results. Their original source/config snapshots remain in Git. Build records identify the actual source used. The verifier is a separate step.

## Kết luận và phiên bản tái lập

A clean GitHub checkout of 8f07e38b0da4649115e00ab1ca285378a8982098 reproduced the native artifact SHA-256 f7fb315d23c7fbd020781eb88de818faf1b5e1bb04af65c98f34fd0e8f337ad1. kickmix-engine 0.6.0 smoke passed with 4,096 verified shots. The current evidence establishes reproducibility and smoke validity. The hypothesis about full-run cost and resource trade-offs remains open.

- [Build provenance](../../../results/invsqrt/INV-76/notebook-native/build_only/20261121T091941Z-build-d9eb213b/provenance.json)
- [Smoke verifier](../../../results/invsqrt/INV-76/notebook-native/smoke/20261121T091942Z-local-smoke-dc4244/verifier.json)
- [Smoke provenance](../../../results/invsqrt/INV-76/notebook-native/smoke/20261121T091942Z-local-smoke-dc4244/provenance.json)
