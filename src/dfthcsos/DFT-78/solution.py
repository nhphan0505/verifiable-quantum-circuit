"""DFT-78 standalone builder for Kaggle notebook v25 (script 372019840).

Generate the 15 base loaders from KMX and write the coefficient NPZ from the released numerical parameters and angle-word edits. The base and notebook configs share that generator. The notebook config swaps in 15 precompiled loaders and a matched table from Rithvik's verified milestone pack, then refits only W and H2_I. For each rank, rotate pairs of columns of the combined weights and offsets, seeded as in v25, then search offsets with L-BFGS-B. Offsets are H2_I minus the leaf sum of W. The objective penalizes deviation of the one-body contraction and gaps near the bound. Preserve angle words, tree edges and all replacement loader bytes. The 7-bit angle words must remain compatible with the replacement loaders. Accept the serialized NPZ only if the official metric math reports valid Hamiltonian errors and gap and lambda_eff decreases.

Uses the pinned external Tony Li v2 archive and the notebook lineage
credited in DESCRIPTION.md. Run on x86-64 Linux/WSL with Python 3.13.
The default notebook-native config builds from the checked-in circuit.py. Historical scored configs accept --generator-bundle. Writes the repository artifact and
build_only provenance after the required digest comparisons.
"""

import argparse
import hashlib
from importlib.metadata import version
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
import uuid
import zipfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRACK = HERE.parent.name
EXPERIMENT = HERE.name
POSTPROCESS_SOURCE = HERE / "postprocessing" / "PP-008" / "solution.py"
GENERATOR_SHA = "2715ee84ce70d59c2e799ee397e11b253e9822e54fbe76fda51a8f274e555496"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require_digest(path, expected):
    actual = digest(path)
    if actual != expected:
        raise ValueError(f"{path.name}: SHA-256 {actual}, expected {expected}")
    return actual


def source_snapshot(config_path, sources):
    # Git for Windows understands the linked worktree paths written by the host.
    dotgit = ROOT / ".git"
    git = "git"
    if os.name == "posix" and dotgit.is_file():
        gitdir = dotgit.read_text(encoding="utf-8").split(": ", 1)[1].strip()
        if len(gitdir) > 2 and gitdir[1] == ":":
            git = "git.exe"
    commit = subprocess.check_output([git, "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    for path in (Path(__file__).resolve(), config_path, *sources):
        relative = path.relative_to(ROOT).as_posix()
        committed = subprocess.check_output([git, "show", f"{commit}:{relative}"], cwd=ROOT)
        if path.read_bytes() != committed:
            raise ValueError(f"Commit the exact bytes of {relative} before building")
    return commit


def build_generator(bundle, workspace, task):
    # Verifying the archive first pins every executable, source file and notice.
    require_digest(bundle, GENERATOR_SHA)
    source = workspace / "source"
    with zipfile.ZipFile(bundle) as archive:
        # Only extract members needed by the selected release build.
        names = [
            name for name in archive.namelist()
            if name in {"expected_sha256.json", "generate.py"}
            or name.startswith((task + "/", "runtime/kickmix/"))
        ]
        archive.extractall(source, members=names)
    child_env = os.environ.copy()
    child_env.pop("PYTHONPATH", None)
    build = workspace / "generated"
    subprocess.run(
        [sys.executable, str(source / "generate.py"), task, "--output", str(build)],
        check=True,
        env=child_env,
    )
    return build


def load_postprocess():
    spec = spec_from_file_location("pp_008", POSTPROCESS_SOURCE)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def record_build(config_path, commit, output, component_hashes, inputs, sources):
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = ROOT / "results" / TRACK / EXPERIMENT / config_path.stem / "build_only" / (
        f"{now}-build-{uuid.uuid4().hex[:8]}"
    )
    run.mkdir(parents=True)
    provenance = {
        "track": TRACK,
        "experiment_id": EXPERIMENT,
        "config_name": config_path.stem,
        "source_commit": commit,
        "source_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "source_sha256": digest(Path(__file__)),
        "build_config_path": config_path.relative_to(ROOT).as_posix(),
        "build_config_sha256": digest(config_path),
        "artifact_path": output.relative_to(ROOT).as_posix(),
        "artifact_sha256": digest(output),
        "build_command": [sys.executable, *sys.argv],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "packages": {name: version(name) for name in PACKAGE_NAMES},
            "input_sha256": inputs,
        },
        "component_sha256": component_hashes,
        "build_dependencies": {path.relative_to(ROOT).as_posix(): digest(path) for path in sources},
        "build_run": None,
    }
    (run / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"BUILT {output}\nSHA-256 {provenance['artifact_sha256']}\nProvenance {run}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=HERE / "configs" / "notebook-native.json")
    parser.add_argument("--generator-bundle", type=Path, help="Pinned Tony Li v2 ZIP for historical release configs")
    add_track_arguments(parser)
    args = parser.parse_args()
    config_path = args.config.resolve(strict=True)
    if config_path.parent != HERE / "configs" or config_path.suffix != ".json":
        parser.error("--config must identify a JSON file inside this experiment's configs directory")
    if sys.version_info[:2] != (3, 13):
        parser.error("Use the repository Python 3.13 environment")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    native = config.get("builder") == "notebook-native"
    if not native and (args.generator_bundle is None or sys.platform != "linux" or platform.machine() != "x86_64"):
        parser.error("Historical release configs require --generator-bundle on x86-64 Linux")
    output = ROOT / "artifacts" / TRACK / EXPERIMENT / (config_path.stem + EXTENSION)
    if output.exists():
        raise FileExistsError(output)
    sources = native_dependencies() if native else [POSTPROCESS_SOURCE]
    commit = source_snapshot(config_path, sources)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="orecord-v25-") as scratch:
        workspace = Path(scratch)
        if native:
            hashes = build_native(output, workspace, config)
            inputs = {}
        else:
            base = build_generator(args.generator_bundle.resolve(strict=True), workspace, GENERATOR_TASK)
            hashes, inputs = package_build(base, output, config, args)
            inputs["generator_bundle"] = GENERATOR_SHA
            inputs["upstream_kickmix_sdk"] = "c66b3216c4029e0cdfd09054306aa0feadf53ab2f50c1164e37f752874e5005e"
    record_build(config_path, commit, output, hashes, inputs, sources)


EXTENSION = ".zip"
GENERATOR_TASK = "chemistry"
PACKAGE_NAMES = ("numpy", "scipy", "kickmix")


def add_track_arguments(parser):
    parser.add_argument("--milestone-bundle", type=Path, help="Rithvik's dataset ZIP or its submission_final.pack")
    parser.add_argument("--verifier-data", type=Path, default=ROOT / "verifiers" / "dfthcsos",
                        help="Directory containing the official FeMoCo integral and fixed-shift files")


def package_build(base, output, config, args):
    mode = config["postprocess"]
    if mode == "none":
        sys.path.insert(0, str(ROOT / "src" / "common"))
        from package_submission import package_dfthcsos

        return package_dfthcsos(base / "dfthcsos", output)["component_sha256"], {}
    if mode != "swap-and-refit":
        raise ValueError(f"Unknown chemistry post-processing mode: {mode}")
    if args.milestone_bundle is None:
        raise ValueError("--milestone-bundle is required for swap-and-refit")
    method = load_postprocess()
    data_dir = args.verifier_data.resolve(strict=True)
    report = method.apply(
        args.milestone_bundle.resolve(strict=True), output,
        verifier_data=data_dir, rounds=config["rounds"], seed=config["seed"],
    )
    return report["component_sha256"], {
        "milestone_pack": method.MILESTONE_PACK_SHA,
        "fcidump": digest(data_dir / "FeMoCo76o113e.fcidump"),
        "fixed_shifts": digest(data_dir / "FeMoCo76o113e.fixed_shifts.npz"),
    }


def native_dependencies():
    return [HERE / "circuit.py", *sorted((HERE / "data").glob("*.npy")), ROOT / "src" / "common" / "package_submission.py"]


def build_native(output, workspace, config):
    from circuit import build_components

    sys.path.insert(0, str(ROOT / "src" / "common"))
    from package_submission import package_dfthcsos

    components = workspace / "dfthcsos"
    build_components(components, brot=config["brot"], batch_size=config["batch_size"])
    return package_dfthcsos(components, output)["component_sha256"]


if __name__ == "__main__":
    main()
