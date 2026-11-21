"""Independently verify and preserve the pinned Kaggle v25 invsqrt KMB.

A streamed SHA-256 check guards the exclusive output copy. Since every byte is
preserved, the gate sequence, measurement-controlled phases and workspace
behavior are identical. This is an identity step. It adds no circuit rewrite.
Use apply(source, output, expected_sha256=...) or run this file as a CLI.
"""

import argparse
import hashlib
import os
from pathlib import Path
import re
import tempfile

EXPECTED_SHA256 = "68eb8c13ebc75c5e443ed5a8c6357c2c77e6676c499ed1324108bf025faf1489"


def apply(source: Path, output: Path, *, expected_sha256: str = EXPECTED_SHA256) -> str:
    """Publish the digest-verified bytes as a new file and return their SHA-256."""
    source, output = Path(source), Path(output)
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ValueError("expected_sha256 must be 64 lowercase hexadecimal characters")
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    digest = hashlib.sha256()
    with tempfile.TemporaryDirectory(prefix=".v25-pass-", dir=output.parent) as scratch:
        staged = Path(scratch) / "candidate"
        with source.open("rb") as incoming, staged.open("xb") as outgoing:
            while block := incoming.read(1 << 20):
                digest.update(block)
                outgoing.write(block)
        actual = digest.hexdigest()
        if actual != expected_sha256:
            raise ValueError(f"SHA-256 mismatch: expected {expected_sha256}, got {actual}")
        # Linking within the same volume publishes a complete file without overwrite.
        os.link(staged, output)
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected-sha256", default=EXPECTED_SHA256)
    args = parser.parse_args()
    print(apply(args.source, args.output, expected_sha256=args.expected_sha256))


if __name__ == "__main__":
    main()
