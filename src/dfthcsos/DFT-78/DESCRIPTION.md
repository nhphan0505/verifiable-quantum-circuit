# [DFT-78] Build DFTHC angle loaders with pebbled ANF from declared 7-bit fit inputs

Loại: Tinh chỉnh một phương án.

## File gốc

The upstream [orecord notebook, v25](https://www.kaggle.com/code/orecord/quantum-circuit-compilation-pipeline?scriptVersionId=372019840) (script version 372019840, chemistry ANF cells 13–14) supplies the Apache-2.0 loader compiler. The port adapts it in [circuit.py](circuit.py) to the [Tony Li v2 fit tables and angle edits](https://www.kaggle.com/datasets/tonylica/quantum-ai-32-85306-task-generators/versions/2), with seven-bit words and batches of five. [solution.py](solution.py) adds repository-native packaging and provenance. The upstream fit coefficients are fixed inputs.

## Phần tinh chỉnh và lý do

Test whether pebbled ANF synthesis on a declared 7-bit fit gives a useful loader architecture for chemistry. The hypothesis is that sharing and uncomputing prefix products limits workspace and reaction depth enough to justify the extra Toffolis. The experiment compares complete verifier costs and records the qubit–Toffoli trade-off.

## Thuật toán

The build reads the frozen Tony Li v2 fit as decimal tables, with explicit dtypes and dimensions. The angle word table is the upstream 7-bit input. The loader generator validates and applies the separate row/column/value overrides. It splits the 75 columns into batches of five and computes XOR deltas between successive batches. A packed Möbius transform over GF(2) produces the ANF for each delta. Prefix products are pebbled into scratch, reused across fan-out, and uncomputed by measurement with phase correction. The first batch XORs its absolute words into the target.

## Điều kiện đúng và đánh đổi

Each loader must preserve the selection register, leave scratch clear, and XOR the appropriate delta even when the target begins dirty. The compiler checks the ANF on all legal addresses while choosing padding values for unreachable ones. It writes the matching NPZ using deterministic NPY/ZIP metadata. The frozen fit came from upstream timing-dependent numerical fitting and quantization. This experiment implements table validation, overrides and loader synthesis. The FCIDUMP-based optimizer that originally obtained U, W and H2_I is outside the implementation.

## Kế hoạch kiểm chứng hypothesis

- **Mốc đối chứng.** Use the [official DFT-BASELINE full run](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/872bb089cbf62931fd156f5c86243c7bd053c9a0/results/dfthcsos/DFT-BASELINE/baseline/full/20261113T190138Z-local-full-e2ab8f/verifier.json}) as the original-method reference. The team's best recorded comparator is [DFT-68 full](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/872bb089cbf62931fd156f5c86243c7bd053c9a0/results/dfthcsos/DFT-68/reconstructed/full/20261115T055007Z-local-full-edb6ea/verifier.json) (427 qubits, 14,810 Toffolis, cost 296,635,967.59 on engine 0.6.0 at 78,080 verified shots). The two circuits use different frozen factorizations. The benchmark compares complete artifacts and cannot isolate the effect of loader synthesis.
- **Dự đoán.** The candidate smoke run reports 405 qubits, 42,710 total Toffolis, and λ_eff about 46.92. The metric multiplies λ_eff, total Toffolis and total qubits. At that width and λ_eff, matching DFT-68 would require about 15,610 total Toffolis or fewer. Lower width and loader depth are plausible benefits, while the present Toffoli count makes a cost win unlikely.
- **Ủng hộ / bác bỏ.** Require an official full verifier PASS and cost below 296635967.5935997 to support a complete-artifact cost win against DFT-68. A full PASS with fewer qubits or lower reaction depth and higher total cost supports a resource trade-off only. Reject a verifier failure, including any Hamiltonian error or gap violation. To claim an isolated loader advantage, a separate controlled comparison must hold the fit and angle words fixed.
- **Điều kiện dừng.** Stop after one full run of the pinned candidate. Retain the resource comparison if it verifies, and stop this cost-optimization direction if it misses the DFT-68 target. A same-fit loader comparison or a new fit requires a separate iteration.
- **Kiểm tra ứng viên cuối.** Rebuild the committed notebook-native config and confirm its SHA-256 3abc10ecbd1991563891d30dd29a8ce8292e676a20453f8a1c14960127c20c8b. Use kickmix-engine 0.6.0, matching verifier revision, official full settings and the same seed or salt where configurable. Re-run the comparator if the verifier or profile differs. The existing smoke run checks basic validity and supplies preliminary resource estimates. Its cost is kept separate from full results.

## Cách dựng và bằng chứng

Run the repository Python 3.13 environment with requirements.txt and the [active config](configs/notebook-native.json).

    python src/dfthcsos/DFT-78/solution.py --config src/dfthcsos/DFT-78/configs/notebook-native.json

The active build compiles directly from the checkout. The former bundle configs are retained as archival names for existing results. Their original source/config snapshots remain in Git. Build records identify the actual source used. The verifier is a separate step.

## Kết luận và phiên bản tái lập

A clean GitHub checkout of f707786f79081316e6b3a97b6f74ac9b3eb91bee reproduced the native artifact SHA-256 3abc10ecbd1991563891d30dd29a8ce8292e676a20453f8a1c14960127c20c8b. kickmix-engine 0.6.0 smoke passed with 1,219 verified shots. The current evidence establishes reproducibility and smoke validity.

- [Build provenance](../../../results/dfthcsos/DFT-78/notebook-native/build_only/20261121T091941Z-build-7ee07443/provenance.json)
- [Smoke verifier](../../../results/dfthcsos/DFT-78/notebook-native/smoke/20261121T091942Z-local-smoke-cddb3e/verifier.json)
- [Smoke provenance](../../../results/dfthcsos/DFT-78/notebook-native/smoke/20261121T091942Z-local-smoke-cddb3e/provenance.json)

### Full verification

The notebook-native full run passed with 78,016 verified shots on kickmix-engine 0.6.0. The score was 811,632,454.2457356, a 4.1344x improvement over the official baseline and 2.7361x the cost of DFT-68.

The run used 405 qubits, reaction depth 135, 42,710 Toffolis and lambda_eff 46.92182. Its width and depth were lower than DFT-68's 427 qubits and depth 168, while its Toffoli count was higher than 14,810. The fits differ, so the score comparison cannot isolate the loader. Stop this cost iteration. A same-fit loader comparison belongs to a separate iteration.

The full artifact matches source build 052164a67e85a51b11f6375dc60d3ee4e462d6ac by SHA-256.

- [Full verifier](../../../results/dfthcsos/DFT-78/notebook-native/full/20261123T012234Z-local-full-5d86bb/verifier.json)
- [Full provenance](../../../results/dfthcsos/DFT-78/notebook-native/full/20261123T012234Z-local-full-5d86bb/provenance.json)
