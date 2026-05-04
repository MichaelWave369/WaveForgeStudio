from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

from .artifact_ledger import file_sha256
from .hashing import canonical_json, sha256_digest

_STABLE_TS = (1980, 1, 1, 0, 0, 0)
_STABLE_CREATED = "1979-03-06T03:06:09Z"
_EXPECTED = ["index.html", "preview_pack_manifest.json", "preview_pack_receipt.json", "PREVIEW_PACK_SUMMARY.md"]
_EXCLUDE = {"preview_pack.zip", "preview_pack_zip_manifest.json", "preview_pack_zip_receipt.json", "PREVIEW_PACK_ZIP_SUMMARY.md"}


def _include(rel: Path) -> bool:
    if any(p.startswith(".") for p in rel.parts):
        return False
    if any(p in {"__pycache__", ".pytest_cache"} for p in rel.parts):
        return False
    if rel.name in _EXCLUDE:
        return False
    return True


def _collect_files(pack: Path) -> list[dict]:
    files = []
    for p in sorted(pack.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(pack)
        if not _include(rel):
            continue
        files.append({"path": rel.as_posix(), "size_bytes": p.stat().st_size, "sha256": file_sha256(p)})
    return files


def create_preview_pack_zip_manifest(pack_dir: str | Path, zip_path: str | Path | None = None) -> dict:
    pack = Path(pack_dir)
    zp = Path(zip_path) if zip_path else pack / "preview_pack.zip"
    files = _collect_files(pack) if pack.exists() else []
    file_paths = {f["path"] for f in files}
    missing = [x for x in _EXPECTED if x not in file_paths]
    if "media/audio_mix.wav" not in file_paths:
        missing.append("media/audio_mix.wav")
    if not any(p.startswith("media/storyboard/frame_") and p.endswith(".svg") for p in file_paths):
        missing.append("media/storyboard/frame_*.svg")
    for pref in ["manifests/av_preview_manifest.json", "receipts/av_preview_receipt.json"]:
        if pref not in file_paths:
            missing.append(pref)
    m = {
        "schema": "waveforge.preview_pack_zip_manifest.v1_alpha",
        "project": "WaveForgeStudio",
        "version": "1.5-alpha",
        "pack_root": ".",
        "zip_output": zp.name,
        "zip_policy": {
            "deterministic_zip": True,
            "stable_timestamps": True,
            "sorted_entries": True,
            "relative_paths_only": True,
            "external_calls_allowed": False,
            "subprocess_allowed": False,
            "network_allowed": False,
            "video_rendering": False,
            "muxing": False,
            "browser_automation": False,
        },
        "files": files,
        "file_count": len(files),
        "missing": sorted(missing),
        "outputs": {
            "zip": zp.name,
            "zip_manifest": "preview_pack_zip_manifest.json",
            "zip_receipt": "preview_pack_zip_receipt.json",
            "summary": "PREVIEW_PACK_ZIP_SUMMARY.md",
        },
    }
    h = sha256_digest(json.loads(canonical_json(m)))
    m["receipt"] = {
        "schema": "waveforge.preview_pack_zip_receipt.v1_alpha",
        "preview_pack_zip_hash": h,
        "zip_file_sha256": None,
        "created_at": _STABLE_CREATED,
    }
    return m


def validate_preview_pack_zip_manifest(manifest: dict) -> list[str]:
    e = []
    if manifest.get("schema") != "waveforge.preview_pack_zip_manifest.v1_alpha": e.append("schema invalid")
    p = manifest.get("zip_policy", {})
    checks = {
        "deterministic_zip": True, "stable_timestamps": True, "sorted_entries": True, "relative_paths_only": True,
        "external_calls_allowed": False, "subprocess_allowed": False, "network_allowed": False,
        "video_rendering": False, "muxing": False, "browser_automation": False,
    }
    for k, v in checks.items():
        if p.get(k) is not v: e.append(f"{k} must be {v}")
    if not manifest.get("outputs", {}).get("zip"): e.append("outputs.zip required")
    if not manifest.get("receipt", {}).get("preview_pack_zip_hash"): e.append("receipt.preview_pack_zip_hash required")
    present = {f.get("path") for f in manifest.get("files", [])}
    if "index.html" not in present: e.append("index.html must be present")
    if "preview_pack_manifest.json" not in present: e.append("preview_pack_manifest.json must be present")
    return e


def assert_valid_preview_pack_zip_manifest(manifest: dict) -> None:
    e = validate_preview_pack_zip_manifest(manifest)
    if e:
        raise ValueError("Invalid preview pack zip manifest: " + "; ".join(e))


def write_preview_pack_zip(pack_dir: str | Path, zip_path: str | Path | None = None) -> dict:
    pack = Path(pack_dir)
    if not pack.exists() or not pack.is_dir():
        raise ValueError("pack_dir must exist")
    zp = Path(zip_path) if zip_path else pack / "preview_pack.zip"
    manifest = create_preview_pack_zip_manifest(pack, zp)
    compression = ZIP_DEFLATED
    try:
        _ = ZIP_DEFLATED
    except Exception:
        compression = ZIP_STORED
    with ZipFile(zp, "w", compression=compression, compresslevel=9) as zf:
        for f in manifest["files"]:
            rel = f["path"]
            src = pack / rel
            zi = ZipInfo(filename=rel, date_time=_STABLE_TS)
            zi.compress_type = compression
            zf.writestr(zi, src.read_bytes())
    manifest["receipt"]["zip_file_sha256"] = file_sha256(zp)
    (pack / "preview_pack_zip_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (pack / "preview_pack_zip_receipt.json").write_text(json.dumps(manifest["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    (pack / "PREVIEW_PACK_ZIP_SUMMARY.md").write_text(
        "# Preview Pack ZIP Summary\n\n"
        f"- zip: {zp.name}\n"
        f"- file_count: {manifest['file_count']}\n"
        f"- preview_pack_zip_hash: {manifest['receipt']['preview_pack_zip_hash']}\n"
        f"- zip_file_sha256: {manifest['receipt']['zip_file_sha256']}\n",
        encoding="utf-8",
    )
    return manifest


def read_preview_pack_zip_info(zip_path: str | Path) -> dict:
    zp = Path(zip_path)
    if not zp.exists():
        return {"exists": False, "size_bytes": 0, "file_count": 0, "contains_index": False, "contains_audio": False, "storyboard_frame_count": 0, "sha256": ""}
    with ZipFile(zp, "r") as zf:
        names = zf.namelist()
    return {
        "exists": True,
        "size_bytes": zp.stat().st_size,
        "file_count": len(names),
        "contains_index": "index.html" in names,
        "contains_audio": "media/audio_mix.wav" in names,
        "storyboard_frame_count": len([n for n in names if n.startswith("media/storyboard/frame_") and n.endswith(".svg")]),
        "sha256": file_sha256(zp),
    }
