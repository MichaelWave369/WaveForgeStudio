from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from waveforge_studio.hashing import sha256_digest
from waveforge_studio.phiaudio_runtime_attestation import (
    PHIAudioRuntimeAttestationError,
    create_phiaudio_runtime_attestation,
)
from waveforge_studio.phiaudio_runtime_lock import phiaudio_runtime_lock


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _fixture(root: Path) -> None:
    root.mkdir()
    (root / "src").mkdir()
    (root / "dist").mkdir()
    (root / "src" / "index.ts").write_text("export const x = 1;\n")
    (root / "dist" / "index.js").write_text("export const x = 1;\n")
    (root / "tsconfig.json").write_text("{}\n")
    lock = phiaudio_runtime_lock()
    (root / "package.json").write_text(
        json.dumps(
            {
                "name": lock["package"],
                "version": lock["package_version"],
            }
        )
    )
    _git(root, "init")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")


def test_attestation_fails_when_checkout_does_not_match_lock(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    _fixture(root)

    with pytest.raises(
        PHIAudioRuntimeAttestationError,
        match="commit does not match",
    ):
        create_phiaudio_runtime_attestation(root)


def test_lock_includes_exact_git_tree_identity() -> None:
    lock = phiaudio_runtime_lock()
    assert lock["schema"] == "waveforge.phiaudio_runtime_lock.v0.2"
    assert lock["git_tree_sha"] == "c08ac250f65a6ce0e76d989eba138386e382fde1"
    assert len(lock["lock_sha256"]) == 64


def test_manifest_digest_is_order_independent_for_canonical_entries() -> None:
    first = [
        {"path": "src/a.ts", "sha256": "a" * 64, "size_bytes": 1},
        {"path": "src/b.ts", "sha256": "b" * 64, "size_bytes": 2},
    ]
    second = list(first)
    assert sha256_digest(first) == sha256_digest(second)
