from __future__ import annotations

import json
from html import escape
from pathlib import Path

from .hashing import canonical_json, sha256_digest

_STABLE_TS = "1979-03-06T03:06:09Z"
_SKIP = {"__pycache__", ".pytest_cache"}


def _norm_tag(v: str) -> str:
    return "-".join(v.strip().lower().split())


def derive_run_tags(run_summary: dict) -> list[str]:
    tags: set[str] = set()
    present = run_summary.get("present", {})
    if run_summary.get("alpha_ready") is True:
        tags.add("alpha-ready")
    elif run_summary.get("alpha_ready") is False:
        tags.add("not-alpha-ready")
    if run_summary.get("smoke_passed") is True:
        tags.add("smoke-passed")
    elif run_summary.get("smoke_passed") is None:
        tags.add("smoke-missing")
    if present.get("av_preview"):
        tags.add("has-av-preview")
    if present.get("preview_pack"):
        tags.add("has-preview-pack")
    if present.get("preview_pack_zip"):
        tags.add("has-zip")
    if present.get("audio_stub"):
        tags.add("has-audio-stub")
    if present.get("visual_stub"):
        tags.add("has-visual-stub")
    if run_summary.get("mode"):
        tags.add(f"mode:{_norm_tag(str(run_summary['mode']))}")
    if run_summary.get("seed") is not None:
        tags.add(f"seed:{run_summary['seed']}")
    if run_summary.get("archetype"):
        tags.add(f"archetype:{_norm_tag(str(run_summary['archetype']))}")
    return sorted(tags)


def _read_json(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _qualifies(run: Path) -> bool:
    checks = ["project.waveforge.json", "forge_report.json", "release_manifest.json", "smoke_report.json", "preview_pack/preview_pack_manifest.json"]
    return any((run / c).exists() for c in checks)


def extract_run_metadata(run_dir: Path, root_dir: Path) -> dict:
    rel = run_dir.relative_to(root_dir).as_posix()
    project = _read_json(run_dir / "project.waveforge.json")
    forge = _read_json(run_dir / "forge_report.json")
    release = _read_json(run_dir / "release_manifest.json")
    smoke = _read_json(run_dir / "smoke_report.json")
    pp = _read_json(run_dir / "preview_pack/preview_pack_manifest.json")
    ppz = _read_json(run_dir / "preview_pack/preview_pack_zip_manifest.json")

    av = run_dir / "render/av_preview.html"
    ppi = run_dir / "preview_pack/index.html"
    zipf = run_dir / "preview_pack/preview_pack.zip"
    audio = run_dir / "render/audio_mix.wav"
    visual = run_dir / "render/storyboard"
    audio_manifest = run_dir / "audio_render_manifest.json"
    visual_manifest = run_dir / "visual_render_manifest.json"

    src = project or forge or smoke or {}
    out = {
        "run_path": rel,
        "present": {
            "project": project is not None,
            "forge_report": forge is not None,
            "release_manifest": release is not None,
            "smoke_report": smoke is not None,
            "av_preview": av.exists(),
            "preview_pack": ppi.exists(),
            "preview_pack_zip": zipf.exists(),
            "audio_stub": audio.exists() or audio_manifest.exists(),
            "visual_stub": visual.exists() or visual_manifest.exists(),
        },
        "prompt": src.get("intent", {}).get("prompt") if project else src.get("prompt"),
        "seed": src.get("seed"),
        "mode": src.get("mode"),
        "duration_seconds": src.get("duration_seconds"),
        "archetype": (project or {}).get("intent", {}).get("archetype"),
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
    out["tags"] = derive_run_tags(out)
    return out


def discover_waveforge_runs(root_dir: str | Path) -> list[dict]:
    root = Path(root_dir)
    runs = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name in _SKIP:
            continue
        stack = [child]
        while stack:
            cur = stack.pop()
            if cur.name.startswith(".") or cur.name in _SKIP:
                continue
            if _qualifies(cur):
                runs.append(extract_run_metadata(cur, root))
                continue
            for c in sorted(cur.iterdir(), reverse=True):
                if c.is_dir() and not c.name.startswith(".") and c.name not in _SKIP:
                    stack.append(c)
    return sorted(runs, key=lambda r: r["run_path"])


def create_gallery_manifest(root_dir: str | Path, gallery_dir: str | Path | None = None) -> dict:
    root = Path(root_dir)
    out = Path(gallery_dir) if gallery_dir else root / "gallery"
    runs = discover_waveforge_runs(root)
    tags = sorted({t for r in runs for t in r.get("tags", [])})
    modes = sorted({r["mode"] for r in runs if r.get("mode")})
    arch = sorted({r["archetype"] for r in runs if r.get("archetype")})
    m = {
        "schema": "waveforge.demo_gallery_manifest.v1_alpha",
        "project": "WaveForgeStudio",
        "version": "1.7-alpha",
        "root": ".",
        "gallery_root": out.name,
        "gallery_policy": {"local_index_only": True, "copies_assets": False, "external_calls_allowed": False, "subprocess_allowed": False, "network_allowed": False, "hosting": False, "browser_automation": False},
        "run_count": len(runs),
        "ready_count": sum(1 for r in runs if r.get("alpha_ready") is True),
        "smoke_passed_count": sum(1 for r in runs if r.get("smoke_passed") is True),
        "zip_count": sum(1 for r in runs if r.get("present", {}).get("preview_pack_zip") is True),
        "search": {"enabled": True, "fields": ["prompt", "seed", "mode", "duration_seconds", "archetype", "tags", "hashes"], "tag_count": len(tags), "available_tags": tags},
        "filters": {
            "modes": modes,
            "archetypes": arch,
            "alpha_ready": {"true": sum(1 for r in runs if r.get("alpha_ready") is True), "false": sum(1 for r in runs if r.get("alpha_ready") is False), "null": sum(1 for r in runs if r.get("alpha_ready") is None)},
            "smoke_passed": {"true": sum(1 for r in runs if r.get("smoke_passed") is True), "false": sum(1 for r in runs if r.get("smoke_passed") is False), "null": sum(1 for r in runs if r.get("smoke_passed") is None)},
            "has_zip": {"true": sum(1 for r in runs if r.get("present", {}).get("preview_pack_zip") is True), "false": sum(1 for r in runs if r.get("present", {}).get("preview_pack_zip") is not True)},
        },
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
    cards = []
    for r in m["runs"]:
        links = " ".join([f'<a href="../{escape(v)}">{escape(k)}</a>' for k, v in r["links"].items() if v])
        chips = " ".join([f'<span class="chip">{escape(t)}</span>' for t in r.get("tags", [])])
        cards.append(f"<tr data-run='{escape(json.dumps(r, sort_keys=True))}'><td>{escape(r['run_path'])}</td><td>{escape(str(r['prompt']))}</td><td>{escape(str(r['seed']))}</td><td>{escape(str(r['mode']))}</td><td>{escape(str(r['duration_seconds']))}</td><td>{escape(str(r['archetype']))}</td><td>{chips}</td><td>{escape(str(r['alpha_ready']))}/{escape(str(r['smoke_passed']))}/{escape(str(r['present'].get('preview_pack_zip')))}</td><td>{links}</td><td>{escape(str(r['hashes']))}</td></tr>")
    tags = "".join([f'<button type="button" class="tag-btn" data-tag="{escape(t)}">{escape(t)}</button>' for t in m["search"]["available_tags"]])
    data_json = escape(json.dumps(m["runs"], sort_keys=True))
    html = f"""<html><head><title>WaveForgeStudio Demo Gallery</title><style>body{{font-family:sans-serif}}.controls{{display:grid;grid-template-columns:repeat(4,minmax(180px,1fr));gap:8px}}table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:6px;vertical-align:top}}.chip{{display:inline-block;background:#eee;border-radius:8px;padding:2px 6px;margin:1px}}</style></head><body><h1>WaveForgeStudio Demo Gallery</h1><p>Runs: {m['run_count']} | Ready: {m['ready_count']} | Smoke passed: {m['smoke_passed_count']} | ZIP: {m['zip_count']}</p><div class='controls'><input id='q' placeholder='Search prompt/hash/tag'><select id='mode'><option value=''>all modes</option>{''.join([f'<option>{escape(x)}</option>' for x in m['filters']['modes']])}</select><select id='arch'><option value=''>all archetypes</option>{''.join([f'<option>{escape(x)}</option>' for x in m['filters']['archetypes']])}</select><select id='alpha'><option value=''>alpha any</option><option value='true'>alpha true</option><option value='false'>alpha false</option><option value='null'>alpha null</option></select><select id='smoke'><option value=''>smoke any</option><option value='true'>smoke true</option><option value='false'>smoke false</option><option value='null'>smoke null</option></select><select id='zip'><option value=''>zip any</option><option value='true'>zip true</option><option value='false'>zip false</option></select><button id='reset' type='button'>Reset Filters</button><div id='visible'>Visible: {m['run_count']}</div></div><div id='tags'>{tags}</div><table id='runs'><tr><th>run</th><th>prompt</th><th>seed</th><th>mode</th><th>duration</th><th>archetype</th><th>tags</th><th>badges</th><th>links</th><th>hashes</th></tr>{''.join(cards)}</table><script type='application/json' id='gallery-data'>{data_json}</script><script>(function(){{const rows=[...document.querySelectorAll('#runs tr[data-run]')];const q=document.getElementById('q');const mode=document.getElementById('mode');const arch=document.getElementById('arch');const alpha=document.getElementById('alpha');const smoke=document.getElementById('smoke');const zip=document.getElementById('zip');const visible=document.getElementById('visible');const tags=new Set();function ok(r){{const txt=JSON.stringify(r).toLowerCase();if(q.value && !txt.includes(q.value.toLowerCase())) return false;if(mode.value && String(r.mode)!==mode.value) return false;if(arch.value && String(r.archetype)!==arch.value) return false;if(alpha.value && String(r.alpha_ready)!==alpha.value) return false;if(smoke.value && String(r.smoke_passed)!==smoke.value) return false;if(zip.value && String(!!r.present.preview_pack_zip)!==zip.value) return false;for (const t of tags) if(!(r.tags||[]).includes(t)) return false;return true;}}function apply(){{let c=0;rows.forEach(row=>{{const r=JSON.parse(row.dataset.run);const show=ok(r);row.style.display=show?'':'none';if(show)c++;}});visible.textContent='Visible: '+c;}}document.querySelectorAll('.tag-btn').forEach(b=>b.onclick=()=>{{const t=b.dataset.tag;if(tags.has(t)){{tags.delete(t);b.style.fontWeight='normal';}}else{{tags.add(t);b.style.fontWeight='bold';}}apply();}});[q,mode,arch,alpha,smoke,zip].forEach(x=>x.oninput=apply);document.getElementById('reset').onclick=()=>{{q.value='';mode.value='';arch.value='';alpha.value='';smoke.value='';zip.value='';tags.clear();document.querySelectorAll('.tag-btn').forEach(b=>b.style.fontWeight='normal');apply();}};apply();}})();</script><p>Local gallery index only — assets are not copied or hosted.</p></body></html>"""
    (out / "index.html").write_text(html, encoding="utf-8")
    (out / "gallery_manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    (out / "gallery_receipt.json").write_text(json.dumps(m["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "GALLERY_SUMMARY.md").write_text(f"# Gallery Summary\n\n- run_count: {m['run_count']}\n- ready_count: {m['ready_count']}\n- smoke_passed_count: {m['smoke_passed_count']}\n- zip_count: {m['zip_count']}\n- tag_count: {m['search']['tag_count']}\n- gallery_hash: {m['receipt']['gallery_hash']}\n", encoding="utf-8")
    return m


def validate_gallery_manifest(manifest: dict) -> list[str]:
    e = []
    if manifest.get("schema") != "waveforge.demo_gallery_manifest.v1_alpha": e.append("schema invalid")
    p = manifest.get("gallery_policy", {})
    for k, v in {"local_index_only": True, "copies_assets": False, "external_calls_allowed": False, "subprocess_allowed": False, "network_allowed": False, "hosting": False, "browser_automation": False}.items():
        if p.get(k) is not v: e.append(f"{k} must be {v}")
    search = manifest.get("search", {})
    if search.get("enabled") is not True: e.append("search.enabled true required")
    if not isinstance(search.get("available_tags"), list): e.append("search.available_tags list required")
    if not isinstance(manifest.get("filters"), dict): e.append("filters required")
    if manifest.get("run_count") != len(manifest.get("runs", [])): e.append("run_count mismatch")
    if not manifest.get("outputs", {}).get("index"): e.append("outputs.index required")
    if not manifest.get("receipt", {}).get("gallery_hash"): e.append("receipt.gallery_hash required")
    for r in manifest.get("runs", []):
        if not isinstance(r.get("tags"), list): e.append("run tags required")
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
    run_count = json.loads(man.read_text(encoding="utf-8")).get("run_count", 0) if man.exists() else 0
    txt = idx.read_text(encoding="utf-8", errors="ignore").lower() if idx.exists() else ""
    return {"exists": g.exists(), "index_exists": idx.exists(), "manifest_exists": man.exists(), "receipt_exists": rec.exists(), "summary_exists": summ.exists(), "run_count": run_count, "contains_waveforge": "waveforge" in txt}
