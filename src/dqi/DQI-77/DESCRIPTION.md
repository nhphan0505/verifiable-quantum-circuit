# [DQI-77] Build a merged J-fraction DQI decoder with pointer flags and shared Forney workspace

Loại: Tinh chỉnh một phương án.

## File gốc

The upstream [orecord notebook, v25](https://www.kaggle.com/code/orecord/quantum-circuit-compilation-pipeline?scriptVersionId=372019840) (script version 372019840, DQI section) names the Apache-2.0 merged J-fraction generator from the [public source dataset](https://www.kaggle.com/datasets/ahmedberatozer/df-thc-group-compression-factorization). See [NOTICE.md](NOTICE.md) for attribution. The repo port pins the projection, pointer flags, shared Forney word and 35-step settings in the checked-in decoder source. [circuit.py](circuit.py) and [solution.py](solution.py) wire that source to the repository runtime and provenance workflow.

## Phần tinh chỉnh và lý do

Evaluate merged J-fraction extraction with pointer flags and a shared Forney word as an alternate decoder architecture. The hypothesis is that fewer reciprocals per pair of slots and lower flag/workspace pressure could offset the arithmetic and scan cost in the official DQI metric.

## Thuật toán

The 70 syndrome words encode GF(2^12) moments. MergedJFractionDecoder uses 35 extraction steps, combining two slots per reciprocal where applicable. Pointer flags retain the location of gaps without a full flag bank. The conversion constructs the numerator and the monic locator polynomial from the continued fraction using field shears and explicit coefficient scaling. The reversible kernel uses the public vqcc_dqi_src source named in the notebook and its pinned projection, shared Forney word and pointer flags.

## Điều kiện đúng và đánh đổi

The projection changes the classical error masks using the known syndrome constraints. The Forney scan evaluates the numerator and derivative at each field position, uses one word for the locator root test and the controlled inverse, and applies the corresponding classical-mask-controlled phase. After each position, the live words are restored before advancing by constant field multipliers. The scan reverses its final multipliers. The converter and merged extractor then run in reverse and release the pointer flags. The official verifier checks both restored syndrome values and phase.

## Kế hoạch kiểm chứng hypothesis

- **Mốc đối chứng.** Use the [official DQI-BASELINE full run](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/872bb089cbf62931fd156f5c86243c7bd053c9a0/results/dqi/DQI-BASELINE/baseline/full/20261113T175827Z-local-full-b6b5a4/verifier.json}) as the original-method reference. The team's best recorded comparator is [DQI-72 full](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/872bb089cbf62931fd156f5c86243c7bd053c9a0/results/dqi/DQI-72/reconstructed/full/20261115T094523Z-local-full-502791/verifier.json) (889 qubits, cost 360,733,280,431.94 on engine 0.6.0 at 102,400 shots).
- **Dự đoán.** The native smoke run uses 898 qubits and approximately 1.085 million mean Toffolis per shot. The full metric is repetition factor times squared width times mean Toffolis, so the candidate at 898 qubits needs a repetition-factor × mean-Toffoli product below approximately 447,336 to beat DQI-72. The observed gate count makes a cost win unlikely. The 4,096-shot repetition factor is specific to smoke and must not be used as the full-run factor.
- **Ủng hộ / bác bỏ.** On the official 102,400-shot profile, require a verifier PASS and cost below 360733280431.94055 to support a cost improvement over DQI-72. Inspect the value and phase error counts, mean Toffolis, width and repetition factor to explain the result. A full PASS above the threshold leaves this as a reproducible alternate decoder reference. A verifier failure rejects the candidate.
- **Điều kiện dừng.** Stop after one official full run of the pinned configuration. If it misses the DQI-72 cost target, preserve the measured trade-off. Changes to extraction, projection, or Forney arithmetic belong to a separate iteration.
- **Kiểm tra ứng viên cuối.** Rebuild the committed notebook-native config and confirm its SHA-256 e9d0fad46cc7eb3a7ed2901e8003cb9ce476df0bebc48e1cfbb3a844fd6ca9e5. Use kickmix-engine 0.6.0, matching verifier revision, official full settings and the same seed or salt where configurable. Re-run the comparator if the verifier or profile differs. The existing smoke run checks basic validity and supplies preliminary resource estimates. Its cost is kept separate from full results.

## Cách dựng và bằng chứng

Run the repository Python 3.13 environment with requirements.txt and the [active config](configs/notebook-native.json).

    python src/dqi/DQI-77/solution.py --config src/dqi/DQI-77/configs/notebook-native.json

The active build compiles directly from the checkout. The former bundle configs are retained as archival names for existing results. Their original source/config snapshots remain in Git. Build records identify the actual source used. The verifier is a separate step.

## Kết luận và phiên bản tái lập

A clean GitHub checkout of f1e272a4ccdf7e23b8b63b173bbcac0e2b52ca5d reproduced the native artifact SHA-256 e9d0fad46cc7eb3a7ed2901e8003cb9ce476df0bebc48e1cfbb3a844fd6ca9e5. kickmix-engine 0.6.0 smoke passed with 4,096 verified shots. The verifier reported 0 value errors and 0 phase errors. The current evidence establishes reproducibility and smoke validity. The hypothesis about full-run cost and resource trade-offs remains open.

- [Build provenance](../../../results/dqi/DQI-77/notebook-native/build_only/20261121T092255Z-build-8c164fff/provenance.json)
- [Smoke verifier](../../../results/dqi/DQI-77/notebook-native/smoke/20261121T092307Z-local-smoke-13d495/verifier.json)
- [Smoke provenance](../../../results/dqi/DQI-77/notebook-native/smoke/20261121T092307Z-local-smoke-13d495/provenance.json)
