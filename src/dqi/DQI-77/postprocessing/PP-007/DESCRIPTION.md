# [PP-007] Verify and pass through the Kaggle v25 DQI decoder

## Hypothesis and scope

A SHA-256 gate followed by an exclusive byte-for-byte copy reproduces v25 output and preserves circuit semantics, phase, ancillas and cost. This identity method rejects corruption and does not introduce a circuit optimization.

## Source and design

Use the [pinned Kaggle notebook](https://www.kaggle.com/code/orecord/quantum-circuit-compilation-pipeline?scriptVersionId=372019840) and the [existing experiment](https://github.com/nhphan0505/verifiable-quantum-circuit/pull/80). The source benchmark is the generator output KMB from DQI-77 with SHA-256 `4b5721411adc239f61fc11c773a2358b75dfe7cb15586efae4f0459c77d77e52`.

Stream real KMB bytes through SHA-256 into temporary output, compare the pinned digest, and publish a new KMB only on success. The default digest is the pinned release. The API also accepts an explicit digest for other fixtures.

## Verification

Test exact output, hash mismatch, input preservation and occupied output refusal. Compare source and standalone output under the same repository smoke profile. Reject any byte, score or verifier status difference. Stop after one pinned benchmark pair. Full grading is outside this check.

## Status

Used the existing DQI-77 build-only KMB after checking the committed source and artifact hashes. The standalone API at source commit 056c91ea10ac345d8a5d234c8c46c16c76efbe14 produced exactly the input bytes. Both input and output passed kickmix-engine 0.6.0 smoke with four threads and --num-shots 4096 and had equal verifier costs. Full grading has not been run. Temporary outputs were removed.

## Usage

Call apply(source, output, expected_sha256=...) to obtain the verified digest. The optional digest defaults to the release hash; the CLI accepts --expected-sha256. An existing destination is rejected. Use Python 3.13 and the repository environment. Choose a new destination in an existing directory on a filesystem supporting hard links.

    python src/dqi/DQI-77/postprocessing/PP-007/solution.py INPUT.kmb OUTPUT.kmb

For API use, load solution.py by path with importlib.util.spec_from_file_location and call apply on the loaded module.

This copy is part of [PR #80](https://github.com/nhphan0505/verifiable-quantum-circuit/pull/80). The experiment entry point calls the same standalone API used by the CLI.
