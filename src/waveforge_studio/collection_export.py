from __future__ import annotations

import json
import re
import shutil
from html import escape
from pathlib import Path

from .artifact_ledger import file_sha256
from .hashing import canonical_json, sha256_digest

_STABLE = "1979-03-06T03:06:09Z"


def _safe_id(run_path: str) -> str:
    x = run_path.lower().replace("\\", "__").replace("/", "__")
    x = re.sub(r"[^a-z0-9_-]+", "-", x).strip("-")
    return x or "run"


def _rel_or_none(p: Path, base: Path) -> str | None:
    try:
        return p.relative_to(base).as_posix()
    except Exception:
        return None


def create_collection_export_manifest(collection_manifest: dict, collection_manifest_path: str | Path | None = None, export_dir: str | Path | None = None) -> dict:
    cm_path = Path(collection_manifest_path) if collection_manifest_path else None
    collection_dir = cm_path.parent if cm_path else Path(".")
    root = collection_dir.parent
    roots = [root, root.parent]
    out_name = Path(export_dir).name if export_dir else "collection_export"
    runs = []
    missing = []
    for r in collection_manifest.get("runs", []):
        run_path = r.get("run_path", "")
        eid = _safe_id(run_path)
        src_zip = r.get("links", {}).get("preview_pack_zip") or f"{run_path}/preview_pack/preview_pack.zip"
        src_m = f"{run_path}/preview_pack/preview_pack_zip_manifest.json"
        src_r = f"{run_path}/preview_pack/preview_pack_zip_receipt.json"
        def pick(rel):
            for b in roots:
                c=(b/rel).resolve()
                if c.exists():
                    return c
            return (roots[0]/rel).resolve()
        pzip = pick(src_zip)
        pm = pick(src_m)
        pr = pick(src_r)
        p = {
            "preview_pack_zip": pzip.exists(),
            "preview_pack_zip_manifest": pm.exists(),
            "preview_pack_zip_receipt": pr.exists(),
        }
        if not p["preview_pack_zip"]:
            missing.append({"run_path": run_path, "artifact": "preview_pack_zip", "source": src_zip})
        run_item = {
            "export_id": eid,
            "run_path": run_path,
            "prompt": r.get("prompt"),
            "seed": r.get("seed"),
            "mode": r.get("mode"),
            "duration_seconds": r.get("duration_seconds"),
            "archetype": r.get("archetype"),
            "tags": r.get("tags", []),
            "source": {
                "preview_pack_zip": _rel_or_none(pzip, root) or src_zip,
                "preview_pack_zip_manifest": _rel_or_none(pm, root) or src_m,
                "preview_pack_zip_receipt": _rel_or_none(pr, root) or src_r,
            },
            "target": {
                "preview_pack_zip": f"runs/{eid}/preview_pack.zip",
                "preview_pack_zip_manifest": f"runs/{eid}/preview_pack_zip_manifest.json",
                "preview_pack_zip_receipt": f"runs/{eid}/preview_pack_zip_receipt.json",
                "run_summary": f"runs/{eid}/run_summary.json",
            },
            "present": p,
            "hashes": {
                "preview_pack_zip_hash": (json.loads(pm.read_text(encoding="utf-8")).get("receipt", {}) if pm.exists() else {}).get("preview_pack_zip_hash"),
                "zip_file_sha256": file_sha256(pzip) if pzip.exists() else None,
            },
        }
        runs.append(run_item)
    zip_count = sum(1 for r in runs if r["present"]["preview_pack_zip"])
    m = {
        "schema": "waveforge.collection_export_manifest.v1_alpha",
        "project": "WaveForgeStudio",
        "version": "1.9-alpha",
        "title": collection_manifest.get("title", "WaveForgeStudio Collection"),
        "description": collection_manifest.get("description", ""),
        "source_collection_hash": (collection_manifest.get("receipt", {}) or {}).get("collection_hash"),
        "source_collection_path": Path(collection_manifest_path).name if collection_manifest_path else "collection_manifest.json",
        "export_root": out_name,
        "export_policy": {"portable_collection_export": True, "copies_full_runs": False, "copies_preview_pack_zips": True, "external_calls_allowed": False, "subprocess_allowed": False, "network_allowed": False, "hosting": False, "browser_automation": False, "video_rendering": False, "muxing": False},
        "run_count": len(runs),
        "zip_count": zip_count,
        "missing_zip_count": len(runs)-zip_count,
        "runs": runs,
        "missing": missing,
        "outputs": {"index": f"{out_name}/index.html", "manifest": f"{out_name}/collection_export_manifest.json", "receipt": f"{out_name}/collection_export_receipt.json", "summary": f"{out_name}/COLLECTION_EXPORT_SUMMARY.md"},
    }
    m["receipt"] = {"schema": "waveforge.collection_export_receipt.v1_alpha", "collection_export_hash": sha256_digest(json.loads(canonical_json(m))), "created_at": _STABLE}
    return m


def write_collection_export(collection_manifest_path: str | Path, export_dir: str | Path | None = None) -> dict:
    cm = Path(collection_manifest_path)
    collection_manifest = json.loads(cm.read_text(encoding="utf-8"))
    out = Path(export_dir) if export_dir else cm.parent / "collection_export"
    out.mkdir(parents=True, exist_ok=True)
    m = create_collection_export_manifest(collection_manifest, cm, out)
    root = cm.parent.parent
    roots=[root, root.parent]

    coll_out = out / "collection"
    coll_out.mkdir(parents=True, exist_ok=True)
    for f in ["index.html", "collection_manifest.json", "collection_receipt.json", "COLLECTION_SUMMARY.md"]:
        src = cm.parent / f
        if src.exists(): shutil.copy2(src, coll_out / f)
    man_out = out / "manifests"; man_out.mkdir(exist_ok=True)
    shutil.copy2(cm, man_out / "collection_manifest.json")
    sg = cm.parent.parent / "gallery_manifest.json"
    if sg.exists(): shutil.copy2(sg, man_out / "source_gallery_manifest.json")

    for r in m["runs"]:
        rd = out / "runs" / r["export_id"]
        rd.mkdir(parents=True, exist_ok=True)
        for k in ["preview_pack_zip", "preview_pack_zip_manifest", "preview_pack_zip_receipt"]:
            src = None
            for b in roots:
                cand=(b / r["source"][k]).resolve()
                if cand.exists() and cand.is_file() and str(cand).startswith(str(b.resolve())):
                    src=cand; break
            if src is not None:
                shutil.copy2(src, rd / Path(r["target"][k]).name)
        (rd / "run_summary.json").write_text(json.dumps({k: r[k] for k in ["run_path", "prompt", "seed", "mode", "duration_seconds", "archetype", "tags", "present", "hashes"]}, indent=2, sort_keys=True), encoding="utf-8")

    rows=[]
    for r in m["runs"]:
        rows.append(f"<tr><td>{escape(r['export_id'])}</td><td>{escape(str(r['prompt']))}</td><td>{escape(str(r['seed']))}</td><td>{escape(str(r['mode']))}</td><td>{escape(str(r['duration_seconds']))}</td><td>{escape(str(r.get('archetype')))}</td><td>{' '.join([f'<span>{escape(t)}</span>' for t in r.get('tags',[])])}</td><td>{'ZIP MISSING' if not r['present']['preview_pack_zip'] else ''}</td><td><a href='{escape(r['target']['preview_pack_zip'])}'>zip</a> <a href='{escape(r['target']['preview_pack_zip_manifest'])}'>zip_manifest</a> <a href='{escape(r['target']['preview_pack_zip_receipt'])}'>zip_receipt</a> <a href='{escape(r['target']['run_summary'])}'>run_summary</a></td></tr>")
    html=f"<html><head><title>{escape(m['title'])}</title><style>body{{font-family:sans-serif}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:6px}}</style></head><body><h1>{escape(m['title'])}</h1><p>{escape(m['description'])}</p><p>run_count: {m['run_count']} | zip_count: {m['zip_count']} | missing_zip_count: {m['missing_zip_count']}</p><table><tr><th>id</th><th>prompt</th><th>seed</th><th>mode</th><th>duration</th><th>archetype</th><th>tags</th><th>warnings</th><th>links</th></tr>{''.join(rows)}</table><p>WaveForgeStudio portable collection export only — full run directories are not copied.</p></body></html>"
    (out/"index.html").write_text(html,encoding='utf-8')
    (out/"collection_export_manifest.json").write_text(json.dumps(m,indent=2,sort_keys=True),encoding='utf-8')
    (out/"collection_export_receipt.json").write_text(json.dumps(m['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (out/"COLLECTION_EXPORT_SUMMARY.md").write_text(f"# Collection Export Summary\n\n- title: {m['title']}\n- run_count: {m['run_count']}\n- zip_count: {m['zip_count']}\n- missing_zip_count: {m['missing_zip_count']}\n- collection_export_hash: {m['receipt']['collection_export_hash']}\n",encoding='utf-8')
    return m


def validate_collection_export_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get('schema')!='waveforge.collection_export_manifest.v1_alpha': e.append('schema invalid')
    p=manifest.get('export_policy',{})
    for k,v in {'portable_collection_export':True,'copies_full_runs':False,'copies_preview_pack_zips':True,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'hosting':False,'browser_automation':False,'video_rendering':False,'muxing':False}.items():
        if p.get(k) is not v: e.append(f'{k} must be {v}')
    if not manifest.get('outputs',{}).get('index'): e.append('outputs.index required')
    if not manifest.get('receipt',{}).get('collection_export_hash'): e.append('receipt.collection_export_hash required')
    if not isinstance(manifest.get('runs'), list): e.append('runs list required')
    if not manifest.get('title'): e.append('title required')
    if manifest.get('run_count')!=len(manifest.get('runs',[])): e.append('run_count mismatch')
    if manifest.get('zip_count',0)+manifest.get('missing_zip_count',0)!=manifest.get('run_count',0): e.append('zip count mismatch')
    return e


def assert_valid_collection_export_manifest(manifest: dict) -> None:
    e=validate_collection_export_manifest(manifest)
    if e: raise ValueError('Invalid collection export manifest: '+'; '.join(e))


def read_collection_export_info(export_dir: str | Path) -> dict:
    e=Path(export_dir)
    idx=e/'index.html'; man=e/'collection_export_manifest.json'; rec=e/'collection_export_receipt.json'; summ=e/'COLLECTION_EXPORT_SUMMARY.md'
    run_count=0; zip_count=0
    if man.exists():
        d=json.loads(man.read_text(encoding='utf-8')); run_count=d.get('run_count',0); zip_count=d.get('zip_count',0)
    txt=idx.read_text(encoding='utf-8',errors='ignore').lower() if idx.exists() else ''
    return {'exists':e.exists(),'index_exists':idx.exists(),'manifest_exists':man.exists(),'receipt_exists':rec.exists(),'summary_exists':summ.exists(),'run_count':run_count,'zip_count':zip_count,'contains_waveforge':'waveforge' in txt}
