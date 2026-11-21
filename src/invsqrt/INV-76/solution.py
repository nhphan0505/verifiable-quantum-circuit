"""INV-76 standalone builder for Kaggle notebook v25 (script 372019840).

Assemble v90 KMX with the v50 divider update and fitted rotation exponents. The divider retains the low carry in both directions, rotates in the even remainder and updates the leftover bit. The q29 lend changes the carry schedule and restores q29 after measurement. The phase repair saves the q38 measurement in b1800, clears b100, emits four controlled-Z gates immediately and delays the fifth until the q29 product is available. Preserve instruction order, phase controls and complete uncomputation on the original 3,133,452-input domain. Expected width is 39 qubits.

Uses the pinned external Tony Li v2 archive and the notebook lineage
credited in DESCRIPTION.md. Run on x86-64 Linux/WSL with Python 3.13.
Pass --config and --generator-bundle. Writes the repository artifact and
build_only provenance after the required digest comparisons.
"""

import argparse
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import shutil
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
GENERATOR_SHA = "2715ee84ce70d59c2e799ee397e11b253e9822e54fbe76fda51a8f274e555496"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require_digest(path, expected):
    actual = digest(path)
    if actual != expected:
        raise ValueError(f"{path.name}: SHA-256 {actual}, expected {expected}")
    return actual


def source_snapshot(config_path):
    # Git for Windows understands the linked worktree paths written by the host.
    dotgit = ROOT / ".git"
    git = "git"
    if os.name == "posix" and dotgit.is_file():
        gitdir = dotgit.read_text(encoding="utf-8").split(": ", 1)[1].strip()
        if len(gitdir) > 2 and gitdir[1] == ":":
            git = "git.exe"
    commit = subprocess.check_output([git, "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    for path in (Path(__file__).resolve(), config_path):
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


def publish(artifact, output):
    # Exclusive creation also prevents two concurrent builds from replacing each other.
    with artifact.open("rb") as source, output.open("xb") as target:
        try:
            shutil.copyfileobj(source, target, 1 << 20)
        except BaseException:
            target.close()
            output.unlink()
            raise


def record_build(config_path, commit, output, component_hashes, inputs):
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
        "build_run": None,
    }
    (run / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"BUILT {output}\nSHA-256 {provenance['artifact_sha256']}\nProvenance {run}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--generator-bundle", required=True, type=Path, help="Pinned Tony Li v2 ZIP")
    add_track_arguments(parser)
    args = parser.parse_args()
    config_path = args.config.resolve(strict=True)
    if config_path.parent != HERE / "configs" or config_path.suffix != ".json":
        parser.error("--config must identify a JSON file inside this experiment's configs directory")
    if sys.version_info[:2] != (3, 13) or sys.platform != "linux" or platform.machine() != "x86_64":
        parser.error("The pinned upstream generator requires x86-64 Linux and Python 3.13 (WSL on Windows)")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output = ROOT / "artifacts" / TRACK / EXPERIMENT / (config_path.stem + EXTENSION)
    if output.exists():
        raise FileExistsError(output)
    commit = source_snapshot(config_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="orecord-v25-") as scratch:
        workspace = Path(scratch)
        base = build_generator(args.generator_bundle.resolve(strict=True), workspace, GENERATOR_TASK)
        artifact, hashes, inputs = postprocess(base, workspace, config, args)
        publish(artifact, output)
    inputs["generator_bundle"] = GENERATOR_SHA
    inputs["upstream_kickmix_sdk"] = "c66b3216c4029e0cdfd09054306aa0feadf53ab2f50c1164e37f752874e5005e"
    record_build(config_path, commit, output, hashes, inputs)


EXTENSION = ".kmb"
GENERATOR_TASK = "invsqrt"
PACKAGE_NAMES = ("numpy",)
EXPECTED_CIRCUIT = "68eb8c13ebc75c5e443ed5a8c6357c2c77e6676c499ed1324108bf025faf1489"


def add_track_arguments(parser):
    """This task needs only the generator bundle."""


def postprocess(base, workspace, config, args):
    """Validate and return the exact generated circuit without rewriting it."""
    if config["postprocess"] != "verify-and-pass-through":
        raise ValueError("Expected verify-and-pass-through for the v25 submission")
    circuit = base / (GENERATOR_TASK + EXTENSION)
    return circuit, {circuit.name: require_digest(circuit, EXPECTED_CIRCUIT)}, {}


if __name__ == "__main__":
    main()
