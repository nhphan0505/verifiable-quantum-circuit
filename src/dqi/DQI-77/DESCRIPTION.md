# [DQI-77] Port the v25 DQI generator and verify pass-through decoder bytes

Loại: Tinh chỉnh một phương án.

## Upstream sources

Use the [pinned v25 notebook](https://www.kaggle.com/code/orecord/quantum-circuit-compilation-pipeline?scriptVersionId=372019840) and [Tony Li's task generator v2](https://www.kaggle.com/datasets/tonylica/quantum-ai-32-85306-task-generators/versions/2). The generator ZIP has SHA-256 `2715ee84ce70d59c2e799ee397e11b253e9822e54fbe76fda51a8f274e555496`. The bundle carries upstream notices including contributions from team ThemBones. Keep the bundle external and intact, including its notices and pinned Linux Kickmix SDK. The Apache-2.0 notebook is the source of pipeline behavior.

## Generator and post-processing

Assemble the source stages in their declared order. The selector maps received bits to 4,024 12-bit residuals with GF(2) parity masks, sorts them using an odd-even network, selects lambda and clears mu. The four D16 substitutions use masked XOR parities and 70 shared bilinear terms plus an 84-term companion. Preserving stage boundaries, field wiring, measurement order, root-1330 phase handling and gauge restoration is required for the 900-qubit result.

The notebook verifies and packages the generator output byte-for-byte. The track's post-processing step validates SHA-256 `4b5721411adc239f61fc11c773a2358b75dfe7cb15586efae4f0459c77d77e52` and passes through the file. No gate transformation is part of this experiment.

## Verification plan

- Baseline: the generator release manifest from v2, with all relevant member hashes. The v25 publication supplies the processed reference.
- Prediction: the build reproduces the expected member hashes. A changed circuit hash rejects the port.
- Stop at exact component reproduction or a diagnosed source, runtime or numerical mismatch. Preserve the original source bytes and retain the verified build-only record.
- Run the official local full verifier after artifact handoff. Build-only provenance does not establish an official local score.

## Reproduction status

Local grading pending.

## Build

Run from this worktree with the Linux Python 3.13 environment and the pinned bundle.

```sh
python src/dqi/DQI-77/solution.py --config src/dqi/DQI-77/configs/notebook-v25.json --generator-bundle /path/to/generators.zip
```

The build calls the [standalone PP-007 method](postprocessing/PP-007/DESCRIPTION.md) from this experiment's postprocessing directory. The method can also be run separately using the linked CLI instructions.

## Repository-native notebook generator

The native config uses the public merged J-fraction generator named in the notebook, from [Ahmed Berat Ozer's source dataset](https://www.kaggle.com/datasets/ahmedberatozer/df-thc-group-compression-factorization). The notebook's scored cell used the later Tony Li D16 release, whose inherited stages are distributed as KMX.

Attached notebook SHA-256 1406a547dae8d22b2171e019d5754c2724ef97ede01b07b0f786308acf365c8a.

    python src/dqi/DQI-77/solution.py --config src/dqi/DQI-77/configs/notebook-native.json

The native build reads its generator and inputs from the checkout. Historical release configs remain available with their original bundle arguments. The native output is a separate artifact with its own provenance and requires local grading.
