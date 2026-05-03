from __future__ import annotations

import json
from html import escape
from pathlib import Path

from .hashing import canonical_json, sha256_digest

_STABLE_TS = "1979-03-06T03:06:09Z"
_SKIP = {"__pycache__", ".pytest_cache"}


def _safe_dirs(root: Path):
    for p in sorted(root.iterdir()):
        if not p.is_dir():
            continue
        if p.name.startswith(".") or p.name in _SKIP:
            continue
        yield p


def _read_json(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _qualifies(run: Path) -> bool:
    return any((run / x).exists() for x in ["project.waveforge.json", "forge_report.json", "release_manifest.json", "smoke_report.json", "preview_pack/preview_pack_manifest.json"])


def _summary(root: Path, run: Path) -> dict:
    rel = run.relative_to(root).as_posix()
    project = _read_json(run / "project.waveforge.json")
    forge = _read_json(run / "forge_report.json")
    release = _read_json(run / "release_manifest.json")
    smoke = _read_json(run / "smoke_report.json")
    pp = _read_json(run / "preview_pack/preview_pack_manifest.json")
    ppz = _read_json(run / "preview_pack/preview_pack_zip_manifest.json")
    av = run / "render/av_preview.html"
    ppi = run / "preview_pack/index.html"
    zipf = run / "preview_pack/preview_pack.zip"
    return {
        "run_path": rel,
        "present": {
            "project": project is not None,
            "forge_report": forge is not None,
            "release_manifest": release is not None,
            "smoke_report": smoke is not None,
            "av_preview": av.exists(),
            "preview_pack": ppi.exists(),
            "preview_pack_zip": zipf.exists(),
        },
        "prompt": (project or forge or smoke or {}).get("prompt"),
        "seed": (project or forge or smoke or {}).get("seed"),
        "mode": (project or forge or smoke or {}).get("mode"),
        "duration_seconds": (project or forge or smoke or {}).get("duration_seconds"),
        "alpha_ready": release.get("alpha_ready") if release else None,
        "smoke_passed": smoke.get("smoke_passed") if smoke else None,
        "hashes": {
            "source_packet_hash": (forge or smoke or {}).get("source_packet_hash"),
            "release_hash": ((release or {}).get("receipt", {}) or {}).get("release_hash"),
            "smoke_hash": ((smoke or {}).get("receipt", {}) or {}).get("smoke_hash"),
            "preview_pack_hash": ((pp or {}).get("receipt", {}) or {}).get("preview_pack_hash"),
            "preview_pack_zip_hash": ((ppz or {}).get("receipt", {}) or {}).get("preview_pack_zip_hash"),
            "zip_file_sha256": ((ppz or {}).get("receipt", {}) or {}).get("zip_file_sha256"),
        },
        "links": {
            "av_preview": f"{rel}/render/av_preview.html" if av.exists() else None,
            "preview_pack_index": f"{rel}/preview_pack/index.html" if ppi.exists() else None,
            "preview_pack_zip": f"{rel}/preview_pack/preview_pack.zip" if zipf.exists() else None,
            "release_manifest": f"{rel}/release_manifest.json" if release else None,
            "smoke_report": f"{rel}/smoke_report.json" if smoke else None,
        },
    }


def discover_waveforge_runs(root_dir: str | Path) -> list[dict]:
    root = Path(root_dir)
    runs = []
    for d in _safe_dirs(root):
        stack = [d]
        while stack:
            cur = stack.pop()
            if cur.name.startswith(".") or cur.name in _SKIP:
                continue
            if _qualifies(cur):
                runs.append(_summary(root, cur))
                continue
            for c in sorted(cur.iterdir(), reverse=True):
                if c.is_dir() and not c.name.startswith(".") and c.name not in _SKIP:
                    stack.append(c)
    return sorted(runs, key=lambda x: x["run_path"])


def create_gallery_manifest(root_dir: str | Path, gallery_dir: str | Path | None = None) -> dict:
    root = Path(root_dir)
    out = Path(gallery_dir) if gallery_dir else root / "gallery"
    runs = discover_waveforge_runs(root)
    m = {
        "schema": "waveforge.demo_gallery_manifest.v1_alpha",
        "project": "WaveForgeStudio",
        "version": "1.6-alpha",
        "root": ".",
        "gallery_root": out.name,
        "gallery_policy": {"local_index_only": True, "copies_assets": False, "external_calls_allowed": False, "subprocess_allowed": False, "network_allowed": False, "hosting": False, "browser_automation": False},
        "run_count": len(runs),
        "ready_count": sum(1 for r in runs if r.get("alpha_ready") is True),
        "smoke_passed_count": sum(1 for r in runs if r.get("smoke_passed") is True),
        "zip_count": sum(1 for r in runs if r.get("present", {}).get("preview_pack_zip") is True),
        "runs": runs,
        "outputs": {"index": f"{out.name}/index.html", "manifest": f"{out.name}/gallery_manifest.json", "receipt": f"{out.name}/gallery_receipt.json", "summary": f"{out.name}/GALLERY_SUMMARY.md"},
    }
    m["receipt"] = {"schema": "waveforge.demo_gallery_receipt.v1_alpha", "gallery_hash": sha256_digest(json.loads(canonical_json(m))), "created_at": _STABLE_TS}
    return m


def write_demo_gallery(root_dir: str | Path, gallery_dir: str | Path | None = None) -> dict:
    root = Path(root_dir)
    out = Path(gallery_dir) if gallery_dir else root / "gallery"
    out.mkdir(parents=True, exist_ok=True)
    m = create_gallery_manifest(root, out)
    rows = []
    for r in m["runs"]:
        links = " ".join([f'<a href="../{escape(v)}">{escape(k)}</a>' for k, v in r["links"].items() if v])
        rows.append(f"<tr><td>{escape(r['run_path'])}</td><td>{escape(str(r['prompt']))}</td><td>{r['seed']}</td><td>{escape(str(r['mode']))}</td><td>{r['duration_seconds']}</td><td>{r['alpha_ready']}</td><td>{r['smoke_passed']}</td><td>{links}</td><td>{escape(str(r['hashes']))}</td></tr>")
    html = f"""<html><head><title>WaveForgeStudio Demo Gallery</title><style>body{{font-family:sans-serif}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:6px;vertical-align:top}}</style></head><body><h1>WaveForgeStudio Demo Gallery</h1><p>Runs: {m['run_count']} | Ready: {m['ready_count']} | Smoke passed: {m['smoke_passed_count']} | ZIP: {m['zip_count']}</p><table><tr><th>run</th><th>prompt</th><th>seed</th><th>mode</th><th>duration</th><th>alpha</th><th>smoke</th><th>links</th><th>hashes</th></tr>{''.join(rows)}</table><p>Local gallery index only — assets are not copied or hosted.</p></body></html>"""
    (out / "index.html").write_text(html, encoding="utf-8")
    (out / "gallery_manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    (out / "gallery_receipt.json").write_text(json.dumps(m["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "GALLERY_SUMMARY.md").write_text(f"# Gallery Summary\n\n- run_count: {m['run_count']}\n- ready_count: {m['ready_count']}\n- smoke_passed_count: {m['smoke_passed_count']}\n- zip_count: {m['zip_count']}\n- gallery_hash: {m['receipt']['gallery_hash']}\n", encoding="utf-8")
    return m


def validate_gallery_manifest(manifest: dict) -> list[str]:
    e = []
    if manifest.get("schema") != "waveforge.demo_gallery_manifest.v1_alpha": e.append("schema invalid")
    p = manifest.get("gallery_policy", {})
    chk = {"local_index_only": True, "copies_assets": False, "external_calls_allowed": False, "subprocess_allowed": False, "network_allowed": False, "hosting": False, "browser_automation": False}
    for k, v in chk.items():
        if p.get(k) is not v: e.append(f"{k} must be {v}")
    if not manifest.get("outputs", {}).get("index"): e.append("outputs.index required")
    if not manifest.get("receipt", {}).get("gallery_hash"): e.append("receipt.gallery_hash required")
    if manifest.get("run_count") != len(manifest.get("runs", [])): e.append("run_count mismatch")
    return e


def assert_valid_gallery_manifest(manifest: dict) -> None:
    e = validate_gallery_manifest(manifest)
    if e:
        raise ValueError("Invalid gallery manifest: " + "; ".join(e))


def read_gallery_info(gallery_dir: str | Path) -> dict:
    g = Path(gallery_dir)
    idx = g / "index.html"
    man = g / "gallery_manifest.json"
    rec = g / "gallery_receipt.json"
    summ = g / "GALLERY_SUMMARY.md"
    run_count = 0
    if man.exists():
        run_count = json.loads(man.read_text(encoding="utf-8")).get("run_count", 0)
    txt = idx.read_text(encoding="utf-8", errors="ignore").lower() if idx.exists() else ""
    return {"exists": g.exists(), "index_exists": idx.exists(), "manifest_exists": man.exists(), "receipt_exists": rec.exists(), "summary_exists": summ.exists(), "run_count": run_count, "contains_waveforge": "waveforge" in txt}
