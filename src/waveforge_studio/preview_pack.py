from __future__ import annotations

import json, shutil
from html import escape
from pathlib import Path

from .hashing import canonical_json, sha256_digest
from .version import DEFAULT_RELEASE_TIMESTAMP

_MANIFESTS = ["av_preview_manifest.json","audio_render_manifest.json","visual_render_manifest.json","project.waveforge.json","av_timeline.json","renderer_handoff.json","production_bundle.json","artifact_ledger.json"]
_RECEIPTS = ["av_preview_receipt.json","audio_render_receipt.json","visual_render_receipt.json","receipt.json","release_manifest_receipt.json","forge_report_receipt.json"]


def create_preview_pack_manifest(source_dir: str | Path, pack_dir: str | Path | None = None) -> dict:
    src = Path(source_dir)
    pack = Path(pack_dir) if pack_dir else src / "preview_pack"
    req = [
        {"source": "render/av_preview.html", "target": "index.html", "present": (src / "render/av_preview.html").exists()},
        {"source": "render/audio_mix.wav", "target": "media/audio_mix.wav", "present": (src / "render/audio_mix.wav").exists()},
    ]
    frames = []
    sb = src / "render" / "storyboard"
    if sb.exists():
        for p in sorted(sb.glob("frame_*.svg")):
            frames.append({"source": f"render/storyboard/{p.name}", "target": f"media/storyboard/{p.name}", "present": True})
    manifests = [{"source": f, "target": f"manifests/{f}", "present": (src / f).exists()} for f in _MANIFESTS]
    receipts = [{"source": f, "target": f"receipts/{f}", "present": (src / f).exists()} for f in _RECEIPTS]
    missing = [x["source"] for x in req if not x["present"]]
    if not (src / "av_preview_manifest.json").exists():
        missing.append("av_preview_manifest.json")
    m = {
        "schema": "waveforge.preview_pack_manifest.v1_alpha",
        "project": "WaveForgeStudio",
        "version": "1.4-alpha",
        "source_root": ".",
        "pack_root": pack.name,
        "pack_policy": {"portable_folder": True, "zip_created": False, "external_calls_allowed": False, "subprocess_allowed": False, "network_allowed": False, "video_rendering": False, "muxing": False, "browser_automation": False},
        "required_assets": req,
        "storyboard_frames": frames,
        "manifests": manifests,
        "receipts": receipts,
        "missing": sorted(missing),
        "outputs": {"pack_index": f"{pack.name}/index.html", "pack_manifest": f"{pack.name}/preview_pack_manifest.json", "pack_receipt": f"{pack.name}/preview_pack_receipt.json", "summary": f"{pack.name}/PREVIEW_PACK_SUMMARY.md"},
    }
    m["receipt"] = {"schema": "waveforge.preview_pack_receipt.v1_alpha", "preview_pack_hash": sha256_digest(json.loads(canonical_json(m))), "created_at": DEFAULT_RELEASE_TIMESTAMP}
    return m


def write_preview_pack(source_dir: str | Path, pack_dir: str | Path | None = None) -> dict:
    src = Path(source_dir)
    pack = Path(pack_dir) if pack_dir else src / "preview_pack"
    pack.mkdir(parents=True, exist_ok=True)
    m = create_preview_pack_manifest(src, pack)
    for item in m["required_assets"] + m["storyboard_frames"] + m["manifests"] + m["receipts"]:
        if item["present"]:
            s = src / item["source"]
            t = pack / item["target"]
            t.parent.mkdir(parents=True, exist_ok=True)
            if s.exists(): shutil.copy2(s, t)
    frames = [x["target"] for x in m["storyboard_frames"] if x["present"]]
    audio_present = any(x["target"] == "media/audio_mix.wav" and x["present"] for x in m["required_assets"]) and (pack / "media/audio_mix.wav").exists()
    gallery = "".join([f'<figure><img src="{escape(f)}" style="max-width:280px"><figcaption>{escape(f)}</figcaption></figure>' for f in frames])
    audio = '<audio controls src="media/audio_mix.wav"></audio>' if audio_present else '<p>Audio missing</p>'
    (pack / "index.html").write_text(f"<html><body><h1>WaveForgeStudio Portable Preview Pack</h1>{audio}<h2>Storyboard</h2>{gallery}<p>Offline preview only — no video rendered or muxed.</p></body></html>", encoding="utf-8")
    (pack / "preview_pack_manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    (pack / "preview_pack_receipt.json").write_text(json.dumps(m["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    (pack / "PREVIEW_PACK_SUMMARY.md").write_text(f"# Preview Pack Summary\n\n- missing: {len(m['missing'])}\n- storyboard_frames: {len(frames)}\n- preview_pack_hash: {m['receipt']['preview_pack_hash']}\n", encoding="utf-8")
    return m


def validate_preview_pack_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get("schema") != "waveforge.preview_pack_manifest.v1_alpha": e.append("schema invalid")
    p=manifest.get("pack_policy", {})
    if p.get("portable_folder") is not True: e.append("portable_folder true required")
    if p.get("zip_created") is not False: e.append("zip_created false required")
    for k in ["external_calls_allowed","subprocess_allowed","network_allowed","video_rendering","muxing","browser_automation"]:
        if p.get(k) is not False: e.append(f"{k} must be false")
    if not manifest.get("outputs", {}).get("pack_index"): e.append("outputs.pack_index required")
    if not manifest.get("receipt", {}).get("preview_pack_hash"): e.append("receipt.preview_pack_hash required")
    required = {x["source"]: x.get("present") for x in manifest.get("required_assets", [])}
    if required.get("render/av_preview.html") is not True: e.append("render/av_preview.html must be present")
    m_present = {x["source"]: x.get("present") for x in manifest.get("manifests", [])}
    if m_present.get("av_preview_manifest.json") is not True: e.append("av_preview_manifest.json must be present")
    return e


def assert_valid_preview_pack_manifest(manifest: dict) -> None:
    e=validate_preview_pack_manifest(manifest)
    if e: raise ValueError("Invalid preview pack manifest: " + "; ".join(e))


def read_preview_pack_info(pack_dir: str | Path) -> dict:
    p=Path(pack_dir)
    idx=p/'index.html'; man=p/'preview_pack_manifest.json'; rec=p/'preview_pack_receipt.json'; summ=p/'PREVIEW_PACK_SUMMARY.md'
    frames = list((p/'media/storyboard').glob('frame_*.svg')) if (p/'media/storyboard').exists() else []
    txt = idx.read_text(encoding='utf-8', errors='ignore').lower() if idx.exists() else ''
    return {"exists": p.exists(), "index_exists": idx.exists(), "manifest_exists": man.exists(), "receipt_exists": rec.exists(), "summary_exists": summ.exists(), "media_audio_exists": (p/'media/audio_mix.wav').exists(), "storyboard_frame_count": len(frames), "contains_waveforge": 'waveforge' in txt}
