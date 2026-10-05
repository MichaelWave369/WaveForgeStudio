from __future__ import annotations

from typing import Any

from .hashing import sha256_digest

PHIAUDIO_RUNTIME_LOCK_SCHEMA = "waveforge.phiaudio_runtime_lock.v0.1"
PHIAUDIO_RUNTIME_REPOSITORY = "MichaelWave369/PHIAudio"
PHIAUDIO_RUNTIME_COMMIT = "2c4855ba9bf7687428347733f4ae435bbee5a934"
PHIAUDIO_RUNTIME_PACKAGE = "phiaudio-sovereign"
PHIAUDIO_RUNTIME_PACKAGE_VERSION = "0.1.0"
PHIAUDIO_RUNTIME_CLI_CONTRACT = "phiaudio-render.v0.1"


def phiaudio_runtime_lock_body() -> dict[str, Any]:
    return {
        "schema": PHIAUDIO_RUNTIME_LOCK_SCHEMA,
        "repository": PHIAUDIO_RUNTIME_REPOSITORY,
        "commit": PHIAUDIO_RUNTIME_COMMIT,
        "package": PHIAUDIO_RUNTIME_PACKAGE,
        "package_version": PHIAUDIO_RUNTIME_PACKAGE_VERSION,
        "cli_contract": PHIAUDIO_RUNTIME_CLI_CONTRACT,
    }


def phiaudio_runtime_lock() -> dict[str, Any]:
    body = phiaudio_runtime_lock_body()
    return {
        **body,
        "lock_sha256": sha256_digest(body),
    }
