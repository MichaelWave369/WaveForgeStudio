from __future__ import annotations

import json
from html import escape
from pathlib import Path

from .hashing import canonical_json, sha256_digest

_STABLE = "1979-03-06T03:06:09Z"


def _norm(t: str) -> str:
    return "-".join(t.strip().lower().split())


def create_gallery_collection_manifest(gallery_manifest: dict, title: str = "WaveForgeStudio Collection", description: str = "", include_tags: list[str] | None = None, include_run_paths: list[str] | None = None, exclude_tags: list[str] | None = None, collection_dir: str | Path | None = None) -> dict:
    runs = gallery_manifest.get("runs", [])
    include_tags_n = sorted({_norm(x) for x in (include_tags or [])})
    exclude_tags_n = sorted({_norm(x) for x in (exclude_tags or [])})
    include_paths = include_run_paths or []
    by_path = {r.get("run_path"): r for r in runs}
    missing = []
    if include_paths:
        base = []
        for p in include_paths:
            if p in by_path:
                base.append(by_path[p])
            else:
                missing.append(p)
    else:
        base = list(runs)

    selected = []
    for r in base:
        tags = {_norm(t) for t in r.get("tags", [])}
        if include_tags_n and not all(t in tags for t in include_tags_n):
            continue
        if exclude_tags_n and any(t in tags for t in exclude_tags_n):
            continue
        selected.append(r)

    out_name = Path(collection_dir).name if collection_dir else "collection"
    m = {
        "schema": "waveforge.gallery_collection_manifest.v1_alpha",
        "project": "WaveForgeStudio",
        "version": "1.8-alpha",
        "title": title,
        "description": description,
        "source_gallery_hash": ((gallery_manifest.get("receipt", {}) or {}).get("gallery_hash")),
        "selection": {
            "include_tags": include_tags_n,
            "include_run_paths": include_paths,
            "exclude_tags": exclude_tags_n,
            "missing_run_paths": missing,
        },
        "collection_policy": {
            "curated_index_only": True,
            "copies_assets": False,
            "external_calls_allowed": False,
            "subprocess_allowed": False,
            "network_allowed": False,
            "hosting": False,
            "browser_automation": False,
        },
        "run_count": len(selected),
        "ready_count": sum(1 for r in selected if r.get("alpha_ready") is True),
        "smoke_passed_count": sum(1 for r in selected if r.get("smoke_passed") is True),
        "zip_count": sum(1 for r in selected if r.get("present", {}).get("preview_pack_zip") is True),
        "available_tags": sorted({t for r in selected for t in r.get("tags", [])}),
        "runs": selected,
        "outputs": {
            "index": f"{out_name}/index.html",
            "manifest": f"{out_name}/collection_manifest.json",
            "receipt": f"{out_name}/collection_receipt.json",
            "summary": f"{out_name}/COLLECTION_SUMMARY.md",
        },
    }
    m["receipt"] = {"schema": "waveforge.gallery_collection_receipt.v1_alpha", "collection_hash": sha256_digest(json.loads(canonical_json(m))), "created_at": _STABLE}
    return m


def write_gallery_collection(gallery_manifest_path: str | Path, collection_dir: str | Path | None = None, title: str = "WaveForgeStudio Collection", description: str = "", include_tags: list[str] | None = None, include_run_paths: list[str] | None = None, exclude_tags: list[str] | None = None) -> dict:
    gpath = Path(gallery_manifest_path)
    gallery_manifest = json.loads(gpath.read_text(encoding="utf-8"))
    out = Path(collection_dir) if collection_dir else gpath.parent / "collection"
    out.mkdir(parents=True, exist_ok=True)
    m = create_gallery_collection_manifest(gallery_manifest, title=title, description=description, include_tags=include_tags, include_run_paths=include_run_paths, exclude_tags=exclude_tags, collection_dir=out)
    cards = []
    for r in m["runs"]:
        chips = " ".join([f'<span class="chip">{escape(str(t))}</span>' for t in r.get("tags", [])])
        links = " ".join([f'<a href="../{escape(v)}">{escape(k)}</a>' for k, v in r.get("links", {}).items() if v])
        cards.append(f"<tr><td>{escape(str(r.get('run_path')))}</td><td>{escape(str(r.get('prompt')))}</td><td>{escape(str(r.get('seed')))}</td><td>{escape(str(r.get('mode')))}</td><td>{escape(str(r.get('duration_seconds')))}</td><td>{escape(str(r.get('archetype')))}</td><td>{chips}</td><td>{escape(str(r.get('alpha_ready')))} / {escape(str(r.get('smoke_passed')))} / {escape(str(r.get('present',{}).get('preview_pack_zip')))}</td><td>{links}</td><td>{escape(str(r.get('hashes')))}</td></tr>")
    html = f"""<html><head><title>{escape(m['title'])}</title><style>body{{font-family:sans-serif}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:6px;vertical-align:top}}.chip{{display:inline-block;background:#eee;border-radius:8px;padding:2px 6px;margin:1px}}</style></head><body><h1>{escape(m['title'])}</h1><p>{escape(m['description'])}</p><p>Runs: {m['run_count']} | Ready: {m['ready_count']} | Smoke passed: {m['smoke_passed_count']} | ZIP: {m['zip_count']}</p><p>include_tags: {escape(', '.join(m['selection']['include_tags']))} | exclude_tags: {escape(', '.join(m['selection']['exclude_tags']))}</p><p>missing_run_paths: {escape(', '.join(m['selection']['missing_run_paths']))}</p><table><tr><th>run</th><th>prompt</th><th>seed</th><th>mode</th><th>duration</th><th>archetype</th><th>tags</th><th>badges</th><th>links</th><th>hashes</th></tr>{''.join(cards)}</table><p>WaveForgeStudio local curated collection only — assets are not copied or hosted.</p></body></html>"""
    (out / "index.html").write_text(html, encoding="utf-8")
    (out / "collection_manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    (out / "collection_receipt.json").write_text(json.dumps(m["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "COLLECTION_SUMMARY.md").write_text(f"# Collection Summary\n\n- title: {m['title']}\n- run_count: {m['run_count']}\n- ready_count: {m['ready_count']}\n- smoke_passed_count: {m['smoke_passed_count']}\n- zip_count: {m['zip_count']}\n- collection_hash: {m['receipt']['collection_hash']}\n", encoding="utf-8")
    return m


def validate_gallery_collection_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get("schema") != "waveforge.gallery_collection_manifest.v1_alpha": e.append("schema invalid")
    if not manifest.get("title"): e.append("title required")
    p=manifest.get("collection_policy",{})
    for k,v in {"curated_index_only":True,"copies_assets":False,"external_calls_allowed":False,"subprocess_allowed":False,"network_allowed":False,"hosting":False,"browser_automation":False}.items():
        if p.get(k) is not v: e.append(f"{k} must be {v}")
    if not manifest.get("outputs",{}).get("index"): e.append("outputs.index required")
    if not manifest.get("receipt",{}).get("collection_hash"): e.append("receipt.collection_hash required")
    if not isinstance(manifest.get("runs"), list): e.append("runs list required")
    if manifest.get("run_count") != len(manifest.get("runs",[])): e.append("run_count mismatch")
    return e


def assert_valid_gallery_collection_manifest(manifest: dict) -> None:
    e=validate_gallery_collection_manifest(manifest)
    if e: raise ValueError("Invalid gallery collection manifest: " + "; ".join(e))


def read_gallery_collection_info(collection_dir: str | Path) -> dict:
    c=Path(collection_dir)
    idx=c/'index.html'; man=c/'collection_manifest.json'; rec=c/'collection_receipt.json'; summ=c/'COLLECTION_SUMMARY.md'
    run_count=0
    if man.exists(): run_count=json.loads(man.read_text(encoding='utf-8')).get('run_count',0)
    txt=idx.read_text(encoding='utf-8',errors='ignore').lower() if idx.exists() else ''
    return {"exists": c.exists(), "index_exists": idx.exists(), "manifest_exists": man.exists(), "receipt_exists": rec.exists(), "summary_exists": summ.exists(), "run_count": run_count, "contains_waveforge": "waveforge" in txt}
