# [DQI-77] Build a merged J-fraction DQI decoder with pointer flags and shared Forney workspace

Loại: Tinh chỉnh một phương án.

## Nguồn và phạm vi

The merged J-fraction source is the Apache-2.0 vqcc_dqi_src release named by the notebook. See [NOTICE.md](NOTICE.md). The [pinned notebook](https://www.kaggle.com/code/orecord/quantum-circuit-compilation-pipeline?scriptVersionId=372019840) and [circuit.py](circuit.py) document the source lineage. This experiment builds one native circuit family. The notebook's scored bundle artifacts are historical evidence for other implementations.

## Thuật toán

The 70 syndrome words encode GF(2^12) moments. MergedJFractionDecoder uses 35 extraction steps, combining two slots per reciprocal where applicable. Pointer flags retain the location of gaps without a full flag bank. The conversion constructs the numerator and the monic locator polynomial from the continued fraction using field shears and explicit coefficient scaling. The reversible kernel uses the public vqcc_dqi_src source named in the notebook and its pinned projection, shared Forney word and pointer flags.

## Điều kiện đúng và đánh đổi

The projection changes the classical error masks using the known syndrome constraints. The Forney scan evaluates the numerator and derivative at each field position, uses one word for the locator root test and the controlled inverse, and applies the corresponding classical-mask-controlled phase. After each position, the live words are restored before advancing by constant field multipliers. The scan reverses its final multipliers. The converter and merged extractor then run in reverse and release the pointer flags. The official verifier checks both restored syndrome values and phase.

## Kế hoạch kiểm chứng

Compare with DQI-BASELINE using equal verifier settings. The native reference artifact is SHA-256 e9d0fad46cc7eb3a7ed2901e8003cb9ce476df0bebc48e1cfbb3a844fd6ca9e5. Predict byte identity for this source cleanup and zero value and phase errors at smoke. Reject a hash mismatch or verification failure. Stop after one clean build and 4,096 smoke shots. Full grading is required for any cost or error-rate claim.

## Cách dựng và bằng chứng

Run the repository Python 3.13 environment with requirements.txt and the [active config](configs/notebook-native.json).

    python src/dqi/DQI-77/solution.py --config src/dqi/DQI-77/configs/notebook-native.json

The active build compiles directly from the checkout. The former bundle configs are retained as archival names for existing results. Their original source/config snapshots remain in Git. Build records identify the actual source used. The verifier is a separate step.
