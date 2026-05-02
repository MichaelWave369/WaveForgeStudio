from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .hashing import canonical_json, sha256_digest

_STABLE_TS = "1979-03-06T03:06:09Z"
_EXCLUDE = {"artifact_ledger.json", "artifact_ledger_receipt.json"}


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _include(rel: Path) -> bool:
    parts = rel.parts
    if any(p.startswith(".") for p in parts):
        return False
    if any(p in {"__pycache__", ".pytest_cache"} for p in parts):
        return False
    if rel.name in _EXCLUDE:
        return False
    return True


def create_artifact_ledger(root_dir: str | Path) -> dict:
    root = Path(root_dir)
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if not _include(rel):
            continue
        files.append({"path": rel.as_posix(), "size_bytes": p.stat().st_size, "sha256": file_sha256(p)})
    ledger = {"schema": "waveforge.artifact_ledger.v0", "project": "WaveForgeStudio", "root": ".", "files": files, "file_count": len(files)}
    lhash = sha256_digest(json.loads(canonical_json(ledger)))
    ledger["receipt"] = {"schema": "waveforge.artifact_ledger_receipt.v0", "ledger_hash": lhash, "created_at": _STABLE_TS}
    return ledger


def write_artifact_ledger(root_dir: str | Path) -> dict:
    root = Path(root_dir)
    root.mkdir(parents=True, exist_ok=True)
    ledger = create_artifact_ledger(root)
    (root / "artifact_ledger.json").write_text(json.dumps(ledger, indent=2, sort_keys=True), encoding="utf-8")
    (root / "artifact_ledger_receipt.json").write_text(json.dumps(ledger["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    (root / "ARTIFACT_LEDGER_SUMMARY.md").write_text(
        f"# Artifact Ledger Summary\n\n- File Count: {ledger['file_count']}\n- Ledger Hash: {ledger['receipt']['ledger_hash']}\n",
        encoding="utf-8",
    )
    return ledger
