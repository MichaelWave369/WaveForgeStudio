from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from .hashing import sha256_digest
from .phiaudio_runtime_lock import phiaudio_runtime_lock

PHIAUDIO_RUNTIME_ATTESTATION_SCHEMA = (
    "waveforge.phiaudio_runtime_attestation.v0.1"
)


class PHIAudioRuntimeAttestationError(ValueError):
    """Raised when a PHIAudio checkout cannot satisfy the runtime lock."""


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _tree_manifest(root: Path, relative_root: str) -> list[dict[str, object]]:
    directory = root / relative_root
    if not directory.is_dir():
        raise PHIAudioRuntimeAttestationError(
            f"required runtime directory missing: {relative_root}"
        )

    files: list[dict[str, object]] = []
    for path in sorted(item for item in directory.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        files.append(
            {
                "path": relative,
                "sha256": _file_sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return files


def _git_value(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        shell=False,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise PHIAudioRuntimeAttestationError(
            f"git {' '.join(args)} failed: {detail}"
        )
    return completed.stdout.strip()


def create_phiaudio_runtime_attestation(
    runtime_root: str | Path,
) -> dict[str, Any]:
    root = Path(runtime_root).resolve()
    lock = phiaudio_runtime_lock()

    actual_commit = _git_value(root, "rev-parse", "HEAD")
    actual_tree = _git_value(root, "rev-parse", "HEAD^{tree}")
    if actual_commit != lock["commit"]:
        raise PHIAudioRuntimeAttestationError(
            "PHIAudio checkout commit does not match runtime lock"
        )
    if actual_tree != lock["git_tree_sha"]:
        raise PHIAudioRuntimeAttestationError(
            "PHIAudio Git tree does not match runtime lock"
        )

    package_path = root / "package.json"
    tsconfig_path = root / "tsconfig.json"
    if not package_path.is_file() or not tsconfig_path.is_file():
        raise PHIAudioRuntimeAttestationError(
            "PHIAudio package.json and tsconfig.json are required"
        )

    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PHIAudioRuntimeAttestationError(
            "PHIAudio package.json is invalid"
        ) from exc

    if package.get("name") != lock["package"]:
        raise PHIAudioRuntimeAttestationError(
            "PHIAudio package name does not match runtime lock"
        )
    if package.get("version") != lock["package_version"]:
        raise PHIAudioRuntimeAttestationError(
            "PHIAudio package version does not match runtime lock"
        )

    source_files = _tree_manifest(root, "src")
    dist_files = _tree_manifest(root, "dist")
    dependency_lock = next(
        (
            name
            for name in ("package-lock.json", "npm-shrinkwrap.json")
            if (root / name).is_file()
        ),
        None,
    )

    body: dict[str, Any] = {
        "schema": PHIAUDIO_RUNTIME_ATTESTATION_SCHEMA,
        "runtime_lock_sha256": lock["lock_sha256"],
        "repository": lock["repository"],
        "commit": actual_commit,
        "git_tree_sha": actual_tree,
        "package": lock["package"],
        "package_version": lock["package_version"],
        "package_json_sha256": _file_sha256(package_path),
        "tsconfig_sha256": _file_sha256(tsconfig_path),
        "source_manifest_sha256": sha256_digest(source_files),
        "source_file_count": len(source_files),
        "dist_manifest_sha256": sha256_digest(dist_files),
        "dist_file_count": len(dist_files),
        "dependency_lock_present": dependency_lock is not None,
        "dependency_lock_file": dependency_lock,
        "dependency_lock_sha256": (
            _file_sha256(root / dependency_lock)
            if dependency_lock is not None
            else None
        ),
        "warnings": (
            []
            if dependency_lock is not None
            else ["no_committed_dependency_lock"]
        ),
    }
    return {
        **body,
        "attestation_sha256": sha256_digest(body),
    }
