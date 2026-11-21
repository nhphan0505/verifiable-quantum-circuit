# [DFT-78] Build DFTHC angle loaders with pebbled ANF from declared 7-bit fit inputs

Loại: Tinh chỉnh một phương án.

## Nguồn và phạm vi

The Apache-2.0 notebook supplies the ANF compiler. The readable fit tables and angle edits are from [Tony Li v2](https://www.kaggle.com/datasets/tonylica/quantum-ai-32-85306-task-generators/versions/2). The [pinned notebook](https://www.kaggle.com/code/orecord/quantum-circuit-compilation-pipeline?scriptVersionId=372019840) and [circuit.py](circuit.py) document the source lineage. This experiment builds one native circuit family. The notebook's scored bundle artifacts are historical evidence for other implementations.

## Thuật toán

The build reads the frozen Tony Li v2 fit as decimal tables, with explicit dtypes and dimensions. The angle word table is the upstream 7-bit input. The loader generator validates and applies the separate row/column/value overrides. It splits the 75 columns into batches of five and computes XOR deltas between successive batches. A packed MÃ¶bius transform over GF(2) produces the ANF for each delta. Prefix products are pebbled into scratch, reused across fan-out, and uncomputed by measurement with phase correction. The first batch XORs its absolute words into the target.

## Điều kiện đúng và đánh đổi

Each loader must preserve the selection register, leave scratch clear, and XOR the appropriate delta even when the target begins dirty. The compiler checks the ANF on all legal addresses while choosing padding values for unreachable ones. It writes the matching NPZ using deterministic NPY/ZIP metadata. The frozen fit came from upstream timing-dependent numerical fitting and quantization. This experiment implements table validation, overrides and loader synthesis. The FCIDUMP-based optimizer that originally obtained U, W and H2_I is outside the implementation.

## Kế hoạch kiểm chứng

Compare with DFT-BASELINE using equal verifier settings. The native artifact before this refactor is SHA-256 3abc10ecbd1991563891d30dd29a8ce8292e676a20453f8a1c14960127c20c8b. Predict byte identity after restoring readable source tables and applying the same 409 edits at runtime. Check each loader and NPZ digest, width at most 128, and official Hamiltonian errors and gap in smoke. Reject any hash or verifier mismatch. Stop after the clean build and a one-shot-per-address smoke run. Full grading is required for any cost claim.

## Cách dựng và bằng chứng

Run the repository Python 3.13 environment with requirements.txt and the [active config](configs/notebook-native.json).

    python src/dfthcsos/DFT-78/solution.py --config src/dfthcsos/DFT-78/configs/notebook-native.json

The active build compiles directly from the checkout. The former bundle configs are retained as archival names for existing results. Their original source/config snapshots remain in Git. Build records identify the actual source used. The verifier is a separate step.
