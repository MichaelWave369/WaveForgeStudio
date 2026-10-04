from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..artifact_ledger import file_sha256
from ..hashing import sha256_digest


class PHIAudioRuntimeError(RuntimeError):
    """Raised when the governed PHIAudio pilot cannot accept a render."""


@dataclass(frozen=True, slots=True)
class PHIAudioRuntimeResult:
    status: str
    runtime_command: str
    source_bundle_hash: str
    manifest_hash: str
    receipt_hash: str
    master_sha256: str
    stem_count: int
    warnings: tuple[str, ...]


class PHIAudioRuntimeAdapter:
    """Opt-in local PHIAudio runtime pilot."""

    name = "phiaudio"
    kind = "audio"
    mode = "external_local_runtime"

    def __init__(
        self,
        runtime_command: str = "phiaudio-render",
        *,
        timeout_seconds: float = 60.0,
    ) -> None:
        if not runtime_command:
            raise ValueError("runtime_command must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.runtime_command = runtime_command
        self.timeout_seconds = timeout_seconds

    def executable(self) -> str | None:
        return shutil.which(self.runtime_command)

    def available(self) -> bool:
        return self.executable() is not None

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "available": self.available(),
            "mode": self.mode,
            "runtime_command": self.runtime_command,
            "default_enabled": False,
            "requires_operator_enablement": True,
            "network_allowed": False,
        }

    @staticmethod
    def _contained_relative(root: Path, path: Path, label: str) -> Path:
        root = root.resolve()
        candidate = path if path.is_absolute() else root / path
        candidate = candidate.resolve()
        try:
            return candidate.relative_to(root)
        except ValueError as exc:
            raise PHIAudioRuntimeError(
                f"{label} must stay inside the WaveForge run root"
            ) from exc

    @staticmethod
    def _read_json(path: Path, label: str) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PHIAudioRuntimeError(f"invalid {label}: {path}") from exc
        if not isinstance(value, dict):
            raise PHIAudioRuntimeError(f"{label} must be a JSON object")
        return value

    @staticmethod
    def _require_sha(value: object, label: str) -> str:
        if not isinstance(value, str) or len(value) != 64:
            raise PHIAudioRuntimeError(f"{label} must be a SHA-256 digest")
        try:
            int(value, 16)
        except ValueError as exc:
            raise PHIAudioRuntimeError(f"{label} must be a SHA-256 digest") from exc
        if value.lower() != value:
            raise PHIAudioRuntimeError(f"{label} must be lowercase")
        return value

    def render_bundle(
        self,
        *,
        run_root: str | Path,
        bundle_path: str | Path = "phiaudio/phiaudio_bundle.json",
        output_dir: str | Path = "render/phiaudio",
        operator_enabled: bool = False,
        sample_rate: int = 48_000,
    ) -> PHIAudioRuntimeResult:
        if operator_enabled is not True:
            raise PHIAudioRuntimeError(
                "PHIAudio execution requires explicit operator enablement"
            )
        if sample_rate not in {44_100, 48_000, 96_000}:
            raise PHIAudioRuntimeError("unsupported PHIAudio sample rate")

        executable = self.executable()
        if executable is None:
            raise PHIAudioRuntimeError(
                f"PHIAudio runtime unavailable: {self.runtime_command}"
            )

        root = Path(run_root).resolve()
        bundle_rel = self._contained_relative(root, Path(bundle_path), "bundle_path")
        output_rel = self._contained_relative(root, Path(output_dir), "output_dir")
        bundle_abs = root / bundle_rel
        if not bundle_abs.is_file():
            raise PHIAudioRuntimeError(f"PHIAudio bundle not found: {bundle_rel}")

        bundle = self._read_json(bundle_abs, "PHIAudio bundle")
        receipt = bundle.get("receipt")
        if not isinstance(receipt, dict):
            raise PHIAudioRuntimeError("PHIAudio bundle receipt missing")
        expected_bundle_hash = self._require_sha(
            receipt.get("bundle_hash"),
            "PHIAudio bundle receipt.bundle_hash",
        )

        completed = subprocess.run(
            [
                executable,
                "--bundle",
                bundle_rel.as_posix(),
                "--out",
                output_rel.as_posix(),
                "--enable-phiaudio",
                "--sample-rate",
                str(sample_rate),
            ],
            cwd=root,
            shell=False,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise PHIAudioRuntimeError(
                f"PHIAudio runtime failed with code {completed.returncode}: {detail}"
            )

        output_abs = root / output_rel
        manifest_path = output_abs / "phiaudio_render_manifest.json"
        receipt_path = output_abs / "phiaudio_render_receipt.json"
        manifest = self._read_json(manifest_path, "PHIAudio render manifest")
        runtime_receipt = self._read_json(receipt_path, "PHIAudio render receipt")

        if manifest.get("schemaVersion") != "phiaudio.waveforge-render.v0.1":
            raise PHIAudioRuntimeError("unsupported PHIAudio render manifest schema")
        if manifest.get("sourceBundleHash") != expected_bundle_hash:
            raise PHIAudioRuntimeError("PHIAudio source bundle hash mismatch")
        if manifest.get("networkUsed") is not False:
            raise PHIAudioRuntimeError("PHIAudio manifest must report networkUsed=false")
        if manifest.get("operatorEnabled") is not True:
            raise PHIAudioRuntimeError("PHIAudio manifest lost operator enablement evidence")

        manifest_hash = sha256_digest(manifest)
        if runtime_receipt.get("renderManifestDigest") != manifest_hash:
            raise PHIAudioRuntimeError("PHIAudio render manifest digest mismatch")
        if runtime_receipt.get("sourceBundleHash") != expected_bundle_hash:
            raise PHIAudioRuntimeError("PHIAudio runtime receipt source hash mismatch")

        receipt_digest = self._require_sha(
            runtime_receipt.get("receiptDigest"),
            "PHIAudio runtime receipt.receiptDigest",
        )
        receipt_body = dict(runtime_receipt)
        del receipt_body["receiptDigest"]
        if sha256_digest(receipt_body) != receipt_digest:
            raise PHIAudioRuntimeError("PHIAudio runtime receipt digest mismatch")

        files = runtime_receipt.get("files")
        if not isinstance(files, list) or not files:
            raise PHIAudioRuntimeError("PHIAudio runtime receipt files missing")

        verified_ids: set[str] = set()
        master_sha256: str | None = None
        for item in files:
            if not isinstance(item, dict):
                raise PHIAudioRuntimeError("PHIAudio receipt file entry must be an object")
            artifact_id = item.get("id")
            relative_path = item.get("path")
            if not isinstance(artifact_id, str) or not artifact_id:
                raise PHIAudioRuntimeError("PHIAudio artifact id missing")
            if artifact_id in verified_ids:
                raise PHIAudioRuntimeError("duplicate PHIAudio artifact id")
            verified_ids.add(artifact_id)
            if not isinstance(relative_path, str):
                raise PHIAudioRuntimeError("PHIAudio artifact path missing")

            artifact_rel = self._contained_relative(
                root,
                Path(relative_path),
                "artifact path",
            )
            artifact_abs = root / artifact_rel
            if not artifact_abs.is_file():
                raise PHIAudioRuntimeError(f"PHIAudio artifact missing: {artifact_rel}")

            actual_sha = file_sha256(artifact_abs)
            expected_sha = self._require_sha(
                item.get("sha256"),
                f"artifact {artifact_id} sha256",
            )
            if actual_sha != expected_sha:
                raise PHIAudioRuntimeError(
                    f"PHIAudio artifact hash mismatch: {artifact_id}"
                )

            expected_size = item.get("sizeBytes")
            if (
                isinstance(expected_size, bool)
                or not isinstance(expected_size, int)
                or expected_size < 0
                or artifact_abs.stat().st_size != expected_size
            ):
                raise PHIAudioRuntimeError(
                    f"PHIAudio artifact size mismatch: {artifact_id}"
                )

            if artifact_id == "master":
                master_sha256 = actual_sha

        if master_sha256 is None:
            raise PHIAudioRuntimeError("PHIAudio master artifact missing")

        stems = manifest.get("stems")
        warnings = manifest.get("warnings", [])
        if not isinstance(stems, list):
            raise PHIAudioRuntimeError("PHIAudio manifest stems must be a list")
        if not isinstance(warnings, list) or not all(
            isinstance(item, str) for item in warnings
        ):
            raise PHIAudioRuntimeError("PHIAudio warnings must be strings")

        return PHIAudioRuntimeResult(
            status="verified",
            runtime_command=self.runtime_command,
            source_bundle_hash=expected_bundle_hash,
            manifest_hash=manifest_hash,
            receipt_hash=receipt_digest,
            master_sha256=master_sha256,
            stem_count=len(stems),
            warnings=tuple(warnings),
        )
