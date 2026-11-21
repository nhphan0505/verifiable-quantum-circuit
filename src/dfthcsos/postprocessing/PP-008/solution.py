"""Reproduce the Kaggle v25 DFTHC milestone swap and coefficient refit.

The input is Rithvik's pinned milestone ZIP or its submission_final.pack.
Keep its loader bytes and angle words. Fit W and H2_I by seeded pairwise
column rotations followed by offset optimization under official FeMoCo
error and gap gates. Publish a separate DFTHC ZIP only after checking the
published refit hash. No input archive or external data is modified.

Refit algorithm adapted from orecord's Apache-2.0 Kaggle notebook v25,
scriptVersionId 372019840. Inherited chemistry files are credited in the
Rithvik milestone bundle's LICENSE and NOTICE.
"""

import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

import kickmix as km
import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[4]
MILESTONE_PACK_SHA = "b4e5beedeaa827c7a240bc23df40b9a8f84d87f24c36efcdf5106f4df38ecde9"
TARGET_NPZ = "39a86eb5b3c5b22ccd217c63e3147545ef213faceca8961fda0672fa2ab8bbff"

EXPECTED_DFTHCSOS = {
    "dfthcsos/angle_k_0.kmb": "8df36485e020b9e30353142a694b69018dc7defdf81847a6b405cd0d9b152402",
    "dfthcsos/angle_k_1.kmb": "b84a398bc050db8dd8b4caa5a73ebee8a1ff262453ce9397671775718863f492",
    "dfthcsos/angle_k_2.kmb": "8b22faa7cb7ed947a5cfdab52a302d622fc4130c4b0812d7ffaa54fd3b034f88",
    "dfthcsos/angle_k_3.kmb": "8a241e9e0884bc32433ffd873afef74d7857198f5b34da217641de15578e7a6e",
    "dfthcsos/angle_k_4.kmb": "517985499e517440036e6e080561e34e45364472ac86c19ef1f1472c990c6f88",
    "dfthcsos/angle_k_5.kmb": "0718ed8e096bb8947de07341240448ba2b1ae399801bbc9426ab5e9fa8d789b4",
    "dfthcsos/angle_k_6.kmb": "e476a76381494e6be9a4e046dfa5eaac06eda33a2251c59458d861e26d89a392",
    "dfthcsos/angle_k_7.kmb": "18da4cf5c0c67ca2f169abea481c1aa6ba26db9d3e2fb79263267f7ca5d65dff",
    "dfthcsos/angle_k_8.kmb": "005df3b85f43b06096226f4736fee0f6613d0737386a874e4aadfa83b6c68ec6",
    "dfthcsos/angle_k_9.kmb": "085ec2716e8980aa5dfc36fe3131497f71ef7fb1a463311c143575c1d997a437",
    "dfthcsos/angle_k_10.kmb": "706df9b9dd42586bf78eda4b671ea192131ef0a93ae64cb3054125def250ce95",
    "dfthcsos/angle_k_11.kmb": "5ac10d8f786b6e54f161ee52c7b6a3b42f6b3b76b06edbb9bb248f3f84217097",
    "dfthcsos/angle_k_12.kmb": "6e85a07768f1d9c2aadea1f5cf4f6013678a190f2f96c99c008f0b9d5cbf27b7",
    "dfthcsos/angle_k_13.kmb": "d4ff6058fe7b36a9b21e21d7f5b591966b44c5dd95ce56de6127f54042a2eac9",
    "dfthcsos/angle_k_14.kmb": "022fcb8d0b2ba892c3dfecb77d9f782f78763295d093d113a29859c811166a9d",
    "dfthcsos/submission.npz": "e259454d6957c5a5f46c8753c125724de9fc458e09b9a6922efa002b01cfc9c4"
}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require_digest(path, expected):
    actual = digest(path)
    if actual != expected:
        raise ValueError(f"{path.name}: SHA-256 {actual}, expected {expected}")
    return actual


def extract_milestone(bundle, workspace):
    if bundle.name == "submission_final.pack":
        pack = bundle
    else:
        pack = workspace / "submission_final.pack"
        with zipfile.ZipFile(bundle) as outer, outer.open(pack.name) as source, pack.open("xb") as target:
            shutil.copyfileobj(source, target, 1 << 20)
    require_digest(pack, MILESTONE_PACK_SHA)
    chemistry = workspace / "milestone"
    chemistry.mkdir()
    with zipfile.ZipFile(pack) as archive:
        for member, expected in EXPECTED_DFTHCSOS.items():
            path = chemistry / Path(member).name
            with archive.open(member) as source, path.open("xb") as target:
                shutil.copyfileobj(source, target, 1 << 20)
            require_digest(path, expected)
    return chemistry


def infer_loader_brot(chem_dir: Path, data: dict, fallback: int = 7) -> int:
    if "brot" in data:
        return int(np.asarray(data["brot"]).item())

    kmb_path = chem_dir / "angle_k_0.kmb"
    if kmb_path.is_file():
        from dfthcsos.scoreinfra.circuits import register_layout

        circ = km.Circuit.from_file(str(kmb_path), format="kmb")
        layout = register_layout([circ])
        if layout.words:
            return len(layout.words[0])

    return fallback


def refine_live_npz_in_place(
    chem_dir: Path,
    data_dir: Path,
    rounds: int = 250,
    seed: int = 20261102,
):
    """Adapt the Apache-2.0 v25 notebook refit for the official local data paths."""
    npz_path = chem_dir / "submission.npz"

    with np.load(npz_path, allow_pickle=False) as archive:
        data = {key: np.array(archive[key], copy=True) for key in archive.files}

    angle_words = np.asarray(data["angle_words"], dtype=np.int64)
    brot = infer_loader_brot(chem_dir, data, fallback=7)

    if brot <= 0 or int(angle_words.max()) >= (1 << brot):
        raise ValueError(
            f"Invalid word width: brot={brot}, max word={int(angle_words.max())}."
        )
    print(f"Loader word width: {brot} bits")

    reference = importlib.import_module("dfthcsos.scoreinfra.reference")
    metric_math = importlib.import_module("dfthcsos.scoreinfra.dfthc_math")

    integrals = reference.load_reference(reference.check_fcidump(data_dir / reference.FCIDUMP_NAME))
    fixed = reference.load_fixed_shifts(data_dir / reference.FIXED_SHIFTS_NAME)
    energy_upper = reference.UPPER_ENERGY

    U = np.asarray(data["U"], dtype=np.float64)
    W0 = np.asarray(data["W"], dtype=np.float64)
    H20 = np.asarray(data["H2_I"], dtype=np.float64)
    tree_edges = np.asarray(data["tree_edges"], dtype=np.int64)

    R, _, C = W0.shape
    N = U.shape[-1]

    shift = np.asarray(
        metric_math.symmetric_from_lower(fixed["Hsym_lower"], N),
        dtype=np.float64,
    )
    beta = float(fixed["H1_I"]) - 0.5 * np.trace(shift)

    def evaluate_metrics(W, H2):
        offsets = H2 - W.sum(axis=1)
        return metric_math.evaluate_dfthc_angle_words(
            angle_words,
            W,
            offsets,
            shift,
            beta,
            integrals,
            brot=brot,
            tree_edges=tree_edges,
            energy_upper=energy_upper,
        )

    # The 1e-10 allowance is only for floating-point roundoff.
    metric_tolerance = 1e-10

    def is_valid(metrics):
        return bool(
            metrics["error_1"] <= 0.020 + metric_tolerance
            and metrics["error_2"] <= 0.020 + metric_tolerance
            and metrics["Lambda"] > 49.0
            and metrics["E_gap"] > 3.914898
            and metrics["gap_in_domain"]
        )

    initial_metrics = evaluate_metrics(W0, H20)
    print(
        f"[Initial] lambda_eff: {initial_metrics['lambda_eff']:.9f} | "
        f"Lambda: {initial_metrics['Lambda']:.6f} | "
        f"E_gap: {initial_metrics['E_gap']:.9f} | "
        f"err1: {1e3 * initial_metrics['error_1']:.7f} mHa | "
        f"err2: {1e3 * initial_metrics['error_2']:.7f} mHa"
    )

    if not is_valid(initial_metrics):
        raise RuntimeError(
            "The starting factorization does not meet the metric gates. "
            "The file was not changed; rely on the official verifier for validity."
        )

    best_W = W0.copy()
    best_H2 = H20.copy()
    best_metrics = initial_metrics

    offsets0 = best_H2 - best_W.sum(axis=1)
    A = np.concatenate([best_W, offsets0[:, None, :]], axis=1)
    rng = np.random.default_rng(seed)
    accepted_rotations = 0

    # Search pairwise column rotations that lower the L1-based cost.
    for _ in range(rounds):
        for _ in range(3 * C):
            i, j = rng.choice(C, 2, replace=False)
            x, y = A[:, :, i].copy(), A[:, :, j].copy()

            theta_z = np.mod(np.arctan2(y, x), np.pi / 2.0)
            theta_g = np.broadcast_to(
                np.linspace(0.0, np.pi / 2.0, 64)[None, :],
                (R, 64),
            )
            theta = np.concatenate([theta_z, theta_g], axis=1)

            cos_theta = np.cos(theta)[:, :, None]
            sin_theta = np.sin(theta)[:, :, None]
            x_new = cos_theta * x[:, None, :] + sin_theta * y[:, None, :]
            y_new = cos_theta * y[:, None, :] - sin_theta * x[:, None, :]

            l1_x = np.abs(x_new[:, :, :-1]).sum(axis=2)
            total_x = np.abs(x_new[:, :, :-1].sum(axis=2) + x_new[:, :, -1])
            l1_y = np.abs(y_new[:, :, :-1]).sum(axis=2)
            total_y = np.abs(y_new[:, :, :-1].sum(axis=2) + y_new[:, :, -1])

            scores = (l1_x + total_x) ** 2 + (l1_y + total_y) ** 2
            best_indices = np.argmin(scores, axis=1)
            best_theta = np.where(
                scores[np.arange(R), best_indices] < scores[:, 0] - 1e-13,
                theta[np.arange(R), best_indices],
                0.0,
            )

            if np.any(best_theta != 0.0):
                cos_best = np.cos(best_theta)[:, None]
                sin_best = np.sin(best_theta)[:, None]
                A[:, :, i] = cos_best * x + sin_best * y
                A[:, :, j] = cos_best * y - sin_best * x
                accepted_rotations += int(np.count_nonzero(best_theta))

    W_rotated = A[:, :-1, :]
    offsets_rotated = A[:, -1, :]
    H2_rotated = offsets_rotated + W_rotated.sum(axis=1)
    rotated_metrics = evaluate_metrics(W_rotated, H2_rotated)

    if (
        is_valid(rotated_metrics)
        and rotated_metrics["lambda_eff"] < best_metrics["lambda_eff"]
    ):
        best_W = W_rotated
        best_H2 = H2_rotated
        best_metrics = rotated_metrics
        print(
            f"[Column rotations: {accepted_rotations} accepted] "
            f"lambda_eff: {best_metrics['lambda_eff']:.9f}"
        )

    # Optimize offsets while preserving the one-body contribution.
    current_W = best_W.copy()
    current_offsets = best_H2 - current_W.sum(axis=1)
    sum_W = current_W.sum(axis=1)
    l1_W = np.abs(current_W).sum(axis=1)

    base_lambda_two = 0.25 * float(
        np.sum((l1_W + np.abs(current_offsets + sum_W)) ** 2)
    )
    lambda_one_body = float(best_metrics["Lambda"]) - base_lambda_two
    base_gap_constant = float(best_metrics["E_gap"]) - 0.5 * float(
        np.sum(current_offsets**2)
    )
    minimum_gap = 3.914898 + 1e-6
    combined_target = np.einsum("rc,rbc->rb", current_offsets, current_W)

    def offset_objective(flat_offsets):
        offsets = flat_offsets.reshape(R, C)
        difference = (
            np.einsum("rc,rbc->rb", offsets, current_W) - combined_target
        )
        penalty = 1e8 * float(np.sum(difference**2))
        penalty_gradient = 2e8 * np.einsum(
            "rb,rbc->rc", difference, current_W
        )

        gap = base_gap_constant + 0.5 * float(np.sum(offsets**2))
        w_b = offsets + sum_W
        lam = lambda_one_body + 0.25 * float(
            np.sum((l1_W + np.abs(w_b)) ** 2)
        )
        radicand = gap * (2.0 * lam - gap)

        if radicand <= 0:
            return 1e12, np.zeros_like(flat_offsets)

        loss = 0.5 * math.log(radicand) + penalty
        gap_gradient = offsets
        lambda_gradient = 0.5 * (l1_W + np.abs(w_b)) * np.sign(w_b)
        gradient = (
            (lam - gap) * gap_gradient + gap * lambda_gradient
        ) / radicand + penalty_gradient

        if gap < minimum_gap:
            loss += 1e7 * (minimum_gap - gap) ** 2
            gradient -= 2e7 * (minimum_gap - gap) * gap_gradient

        return loss, gradient.ravel()

    optimizer_result = minimize(
        offset_objective,
        current_offsets.ravel(),
        jac=True,
        method="L-BFGS-B",
        options={"maxiter": 300, "ftol": 1e-14, "gtol": 1e-10},
    )
    print("Offset optimizer:", optimizer_result.message)

    optimized_offsets = optimizer_result.x.reshape(R, C)
    optimized_H2 = optimized_offsets + sum_W
    optimized_metrics = evaluate_metrics(current_W, optimized_H2)

    if (
        is_valid(optimized_metrics)
        and optimized_metrics["lambda_eff"] < best_metrics["lambda_eff"]
    ):
        best_W = current_W
        best_H2 = optimized_H2
        best_metrics = optimized_metrics
        print(f"[Offset optimization] lambda_eff: {best_metrics['lambda_eff']:.9f}")

    if best_metrics["lambda_eff"] >= initial_metrics["lambda_eff"] - 1e-7:
        print("No valid improvement found; the original file was left unchanged.")
        return None

    # Build and validate the exact serialized candidate before replacing the original.
    candidate_data = dict(data)
    candidate_data["W"] = best_W.astype(data["W"].dtype)
    candidate_data["H2_I"] = best_H2.astype(data["H2_I"].dtype)

    candidate_path = chem_dir / "submission.refined.tmp.npz"
    np.savez(candidate_path, **candidate_data)

    with np.load(candidate_path, allow_pickle=False) as archive:
        saved_W = np.asarray(archive["W"], dtype=np.float64)
        saved_H2 = np.asarray(archive["H2_I"], dtype=np.float64)

    final_metrics = evaluate_metrics(saved_W, saved_H2)
    if (
        not is_valid(final_metrics)
        or final_metrics["lambda_eff"] >= initial_metrics["lambda_eff"]
    ):
        candidate_path.unlink(missing_ok=True)
        print("Saved candidate failed validation; the original file was left unchanged.")
        return None

    candidate_path.replace(npz_path)

    with npz_path.open("rb") as file:
        final_sha = hashlib.file_digest(file, "sha256").hexdigest()

    print(
        f"Optimized file saved. lambda_eff: "
        f"{initial_metrics['lambda_eff']:.9f} -> {final_metrics['lambda_eff']:.9f}"
    )
    print("SHA-256:", final_sha)
    return final_sha


def apply(milestone: Path, output: Path, *, verifier_data: Path) -> dict:
    """Reproduce the pinned 250-round refit and publish a new track ZIP."""
    milestone, output, verifier_data = Path(milestone), Path(output), Path(verifier_data)
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    sys.path.insert(0, str(ROOT / "src" / "common"))
    from package_submission import package_dfthcsos

    sys.path.insert(0, str(ROOT / "verifiers"))
    with tempfile.TemporaryDirectory(prefix=".v25-chem-", dir=output.parent) as scratch:
        workspace = Path(scratch)
        chemistry = extract_milestone(milestone, workspace)
        if refine_live_npz_in_place(chemistry, verifier_data) is None:
            raise ValueError("The v25 refit did not improve the milestone factorization")
        require_digest(chemistry / "submission.npz", TARGET_NPZ)
        for name, expected in EXPECTED_DFTHCSOS.items():
            if name.endswith(".kmb"):
                require_digest(chemistry / Path(name).name, expected)
        staged = workspace / "candidate.zip"
        report = package_dfthcsos(chemistry, staged)
        os.link(staged, output)
    report["artifact_path"] = str(output)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("milestone", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--verifier-data", type=Path, default=ROOT / "verifiers" / "dfthcsos")
    args = parser.parse_args()
    print(json.dumps(apply(args.milestone, args.output, verifier_data=args.verifier_data), indent=2))


if __name__ == "__main__":
    main()
