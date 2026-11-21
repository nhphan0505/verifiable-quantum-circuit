"""Build this experiment with merged J-fraction extraction and Forney phase correction.

The notebook-native config runs circuit.py from a committed checkout. Use
Python 3.13 and requirements.txt. The output and build-only provenance use
repository paths. Prior config files are retained for historical run links.
"""
import argparse
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRACK = HERE.parent.name
EXPERIMENT = HERE.name


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


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


def record_build(config_path, commit, output, component_hashes, sources):
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
    args = parser.parse_args()
    config_path = args.config.resolve(strict=True)
    if config_path != HERE / "configs" / "notebook-native.json":
        parser.error("Only configs/notebook-native.json is active. Other configs are historical.")
    if sys.version_info[:2] != (3, 13):
        parser.error("Use the repository Python 3.13 environment")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output = ROOT / "artifacts" / TRACK / EXPERIMENT / (config_path.stem + EXTENSION)
    if output.exists():
        raise FileExistsError(output)
    sources = native_dependencies()
    commit = source_snapshot(config_path, sources)
    output.parent.mkdir(parents=True, exist_ok=True)
    hashes = build_native(output)
    record_build(config_path, commit, output, hashes, sources)


EXTENSION = ".kmb"
GENERATOR_TASK = "dqi"
PACKAGE_NAMES = ("kickmix", "numpy")


def native_dependencies():
    return [HERE / "circuit.py", *sorted((HERE / "decoder").glob("*.py")), *sorted((ROOT / "verifiers" / "dqi").glob("*.py"))]


def build_native(output):
    from circuit import build_circuit

    staged = output.parent / f".{output.name}.{uuid.uuid4().hex}.tmp"
    try:
        build_circuit().to_file(staged, format="kmb")
        os.link(staged, output)
    finally:
        staged.unlink(missing_ok=True)
    return {f"{GENERATOR_TASK}.kmb": digest(output)}


if __name__ == "__main__":
    main()
