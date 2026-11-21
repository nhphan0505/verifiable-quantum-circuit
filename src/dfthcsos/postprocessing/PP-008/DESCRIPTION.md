# [PP-008] Swap milestone chemistry loaders and refit coefficients as in Kaggle v25

## Hypothesis and scope

The standalone application of the v25 chemistry replacement and refit can reproduce the 15 published loader hashes and coefficient archive while preserving the official Hamiltonian error and gap conditions. The scope is dfthcsos.

## Source and design

Use the [pinned Kaggle notebook](https://www.kaggle.com/code/orecord/quantum-circuit-compilation-pipeline?scriptVersionId=372019840) and the [existing experiment](https://github.com/nhphan0505/verifiable-quantum-circuit/pull/81). The source benchmark is the unprocessed generated chemistry ZIP from DFT-78 with SHA-256 `440676b07a0e4af85fb7a223aecc8af18b9fcd762d9adb623c75a37a90ae49cb`.

Read the pinned Rithvik milestone pack, extract only its 16 hash-checked chemistry members, and run the Apache-2.0 v25 seeded 250-round pairwise column rotation and L-BFGS-B offset fit. Only W and H2_I in the matched coefficient table may change. Use the original official FeMoCo inputs to enforce the metric gates. The loader bytes, angle words, tree and other arrays are preserved during the fit. Package a separate track ZIP with the repo packaging helper.

## Verification

Test invalid pack and occupied output rejection and hash-checked member extraction. Compare the generated base and standalone candidate against the same official verifier at one shot per address. Reject byte mismatches or verifier failure. The comparison measures the combined swap and refit. Stop after one pinned benchmark pair. Full grading is outside this check.

## Status

Awaiting implementation and verification.

## Usage

Call apply(milestone, output, verifier_data=directory) for the pinned chemistry release. The CLI accepts the same paths with --verifier-data. Use either the original ZIP or the exact file named submission_final.pack. Use Python 3.13 and the repository environment. Choose a new destination in an existing directory on a filesystem supporting hard links.

    python src/dfthcsos/postprocessing/PP-008/solution.py MILESTONE.zip OUTPUT.zip --verifier-data OFFICIAL_DFTHCSOS

For API use, load solution.py by path with importlib.util.spec_from_file_location and call apply on the loaded module.
