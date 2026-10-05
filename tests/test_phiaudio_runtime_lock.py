from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from waveforge_studio.phiaudio_runtime_lock import (
    PHIAUDIO_RUNTIME_COMMIT,
    PHIAUDIO_RUNTIME_REPOSITORY,
    phiaudio_runtime_lock,
)


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "waveforge_studio.cli", *args],
        cwd=cwd,
        env=dict(os.environ),
        text=True,
        capture_output=True,
        check=False,
    )


def test_runtime_lock_is_self_hashed_and_pins_known_good_source() -> None:
    lock = phiaudio_runtime_lock()

    assert lock["repository"] == PHIAUDIO_RUNTIME_REPOSITORY
    assert lock["commit"] == PHIAUDIO_RUNTIME_COMMIT
    assert len(lock["commit"]) == 40
    assert len(lock["lock_sha256"]) == 64
    assert lock["schema"] == "waveforge.phiaudio_runtime_lock.v0.1"
    assert lock["cli_contract"] == "phiaudio-render.v0.1"


def test_runtime_lock_cli_is_machine_readable(tmp_path: Path) -> None:
    result = _run("phiaudio-runtime-lock", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == phiaudio_runtime_lock()
