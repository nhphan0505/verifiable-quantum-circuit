# [INV-76] Port the v25 inverse-square-root generator and verify pass-through circuit bytes

Loại: Tinh chỉnh một phương án.

## Upstream sources

Use the [pinned v25 notebook](https://www.kaggle.com/code/orecord/quantum-circuit-compilation-pipeline?scriptVersionId=372019840) and [Tony Li's task generator v2](https://www.kaggle.com/datasets/tonylica/quantum-ai-32-85306-task-generators/versions/2). The generator ZIP has SHA-256 `2715ee84ce70d59c2e799ee397e11b253e9822e54fbe76fda51a8f274e555496`. The bundle carries upstream notices including contributions from team ThemBones. Keep the bundle external and intact, including its notices and pinned Linux Kickmix SDK. The Apache-2.0 notebook is the source of pipeline behavior.

## Generator and post-processing

Assemble v90 KMX with the v50 divider update and fitted rotation exponents. The divider retains the low carry in both directions, rotates in the even remainder and updates the leftover bit. The q29 lend changes the carry schedule and restores q29 after measurement. The phase repair saves the q38 measurement in b1800, clears b100, emits four controlled-Z gates immediately and delays the fifth until the q29 product is available. Preserve instruction order, phase controls and complete uncomputation on the original 3,133,452-input domain. Expected width is 39 qubits.

The notebook verifies and packages the generator output byte-for-byte. The track's post-processing step validates SHA-256 `68eb8c13ebc75c5e443ed5a8c6357c2c77e6676c499ed1324108bf025faf1489` and passes through the file. No gate transformation is part of this experiment.

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
python src/invsqrt/INV-76/solution.py --config src/invsqrt/INV-76/configs/notebook-v25.json --generator-bundle /path/to/generators.zip
```

The build calls the [standalone PP-006 method](postprocessing/PP-006/DESCRIPTION.md) from this experiment's postprocessing directory. The method can also be run separately using the linked CLI instructions.

## Repository-native notebook generator

The native config runs the attached notebook's own time-multiplexed interpolation generator and coefficient table. Its circuit is distinct from the Tony Li 39-qubit release used by the notebook's scored cells.

Attached notebook SHA-256 1406a547dae8d22b2171e019d5754c2724ef97ede01b07b0f786308acf365c8a.

    python src/invsqrt/INV-76/solution.py --config src/invsqrt/INV-76/configs/notebook-native.json

The native build reads its generator and inputs from the checkout. Historical release configs remain available with their original bundle arguments. The native output is a separate artifact with its own provenance and requires local grading.
