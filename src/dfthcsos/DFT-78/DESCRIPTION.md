# [DFT-78] Port the v25 chemistry generator and reproduce the loader swap and coefficient refit

Loại: Kết hợp nhiều phương án.

## Upstream sources

Use the [pinned v25 notebook](https://www.kaggle.com/code/orecord/quantum-circuit-compilation-pipeline?scriptVersionId=372019840) and [Tony Li's task generator v2](https://www.kaggle.com/datasets/tonylica/quantum-ai-32-85306-task-generators/versions/2). The generator ZIP has SHA-256 `2715ee84ce70d59c2e799ee397e11b253e9822e54fbe76fda51a8f274e555496`. The bundle carries upstream notices including contributions from team ThemBones. Keep the bundle external and intact, including its notices and pinned Linux Kickmix SDK. The Apache-2.0 notebook is the source of pipeline behavior.

## Generator and post-processing

Generate the 15 base loaders from KMX and write the coefficient NPZ from the released numerical parameters and angle-word edits. The base and notebook configs share that generator. The notebook config swaps in 15 precompiled loaders and a matched table from Rithvik's verified milestone pack, then refits only W and H2_I. For each rank, rotate pairs of columns of the combined weights and offsets, seeded as in v25, then search offsets with L-BFGS-B. Offsets are H2_I minus the leaf sum of W. The objective penalizes deviation of the one-body contraction and gaps near the bound. Preserve angle words, tree edges and all replacement loader bytes. The 7-bit angle words must remain compatible with the replacement loaders. Accept the serialized NPZ only if the official metric math reports valid Hamiltonian errors and gap and lambda_eff decreases.

The [Rithvik milestone dataset](https://www.kaggle.com/datasets/rithvikredrouthu/qcc-milestone-set) supplies the notebook replacement. Its inner `submission_final.pack` has SHA-256 `b4e5beedeaa827c7a240bc23df40b9a8f84d87f24c36efcdf5106f4df38ecde9`. Validate all 16 components before fitting. Upstream v25 reports an improvement from 46.923700398 to 46.923699426. The target NPZ SHA-256 is `39a86eb5b3c5b22ccd217c63e3147545ef213faceca8961fda0672fa2ab8bbff`.

## Verification plan

- Baseline: the generator release manifest from v2, with all relevant member hashes. The v25 publication supplies the processed reference.
- Prediction: the build reproduces the expected member hashes. The weighted refit lowers lambda_eff with every replacement loader hash unchanged. A numerical or hash mismatch rejects exact reproduction.
- Stop at exact component reproduction or a diagnosed source, runtime or numerical mismatch. Preserve the original source bytes and retain the verified build-only record.
- Run the official local full verifier after artifact handoff. Build-only provenance does not establish an official local score.

## Reproduction status

Local grading pending.
