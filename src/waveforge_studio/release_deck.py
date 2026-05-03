from __future__ import annotations

import json
from html import escape
from pathlib import Path

from .hashing import canonical_json, sha256_digest

_STABLE = "1979-03-06T03:06:09Z"


def create_release_deck_manifest(collection_export_manifest: dict, collection_export_manifest_path: str | Path | None = None, deck_dir: str | Path | None = None, title: str | None = None, subtitle: str = "PHI369 Sovereign Media Showcase") -> dict:
    cpath = Path(collection_export_manifest_path) if collection_export_manifest_path else None
    out = Path(deck_dir) if deck_dir else (cpath.parent / "release_deck" if cpath else Path("release_deck"))
    t = title or collection_export_manifest.get("title") or "WaveForgeStudio Release Deck"
    cards = []
    for i, run in enumerate(collection_export_manifest.get("runs", []), start=1):
        cid = f"card_{i:03d}"
        cards.append({
            "card_id": cid,
            "card_file": f"cards/{cid}.html",
            "run_path": run.get("run_path"),
            "export_id": run.get("export_id"),
            "prompt": run.get("prompt"),
            "seed": run.get("seed"),
            "mode": run.get("mode"),
            "duration_seconds": run.get("duration_seconds"),
            "archetype": run.get("archetype"),
            "tags": run.get("tags", []),
            "links": {
                "preview_zip": f"../{run.get('target',{}).get('preview_pack_zip')}" if run.get("target", {}).get("preview_pack_zip") else None,
                "zip_manifest": f"../{run.get('target',{}).get('preview_pack_zip_manifest')}" if run.get("target", {}).get("preview_pack_zip_manifest") else None,
                "zip_receipt": f"../{run.get('target',{}).get('preview_pack_zip_receipt')}" if run.get("target", {}).get("preview_pack_zip_receipt") else None,
                "run_summary": f"../{run.get('target',{}).get('run_summary')}" if run.get("target", {}).get("run_summary") else None,
            },
            "hashes": run.get("hashes", {"preview_pack_zip_hash": None, "zip_file_sha256": None}),
        })
    m = {
        "schema": "waveforge.release_deck_manifest.v2_alpha",
        "project": "WaveForgeStudio",
        "version": "2.0-alpha",
        "title": t,
        "subtitle": subtitle,
        "source_collection_export_hash": (collection_export_manifest.get("receipt", {}) or {}).get("collection_export_hash"),
        "deck_policy": {"offline_html_deck": True, "copies_assets": False, "external_calls_allowed": False, "subprocess_allowed": False, "network_allowed": False, "hosting": False, "browser_automation": False, "powerpoint": False, "video_rendering": False, "muxing": False},
        "card_count": len(cards),
        "cards": cards,
        "outputs": {"index": f"{out.name}/index.html", "markdown": f"{out.name}/RELEASE_DECK.md", "manifest": f"{out.name}/release_deck_manifest.json", "receipt": f"{out.name}/release_deck_receipt.json"},
    }
    m["receipt"] = {"schema": "waveforge.release_deck_receipt.v2_alpha", "release_deck_hash": sha256_digest(json.loads(canonical_json(m))), "created_at": _STABLE}
    return m


def write_release_deck(collection_export_manifest_path: str | Path, deck_dir: str | Path | None = None, title: str | None = None, subtitle: str = "PHI369 Sovereign Media Showcase") -> dict:
    cpath = Path(collection_export_manifest_path)
    cem = json.loads(cpath.read_text(encoding="utf-8"))
    out = Path(deck_dir) if deck_dir else cpath.parent / "release_deck"
    (out / "cards").mkdir(parents=True, exist_ok=True)
    m = create_release_deck_manifest(cem, cpath, out, title, subtitle)

    rows=[]
    md_cards=[]
    for i, c in enumerate(m["cards"], start=1):
        links = " ".join([f'<a href="{escape(v)}">{escape(k)}</a>' for k,v in c["links"].items() if v])
        card_html=f"<html><head><title>{escape(m['title'])} - {escape(c['card_id'])}</title><style>body{{font-family:sans-serif}}</style></head><body><p><a href='../index.html'>Back to deck</a></p><h1>{escape(m['title'])}</h1><h2>{escape(c['card_id'])}</h2><p>{escape(str(c['prompt']))}</p><p>seed={escape(str(c['seed']))} mode={escape(str(c['mode']))} duration={escape(str(c['duration_seconds']))} archetype={escape(str(c.get('archetype')))}</p><p>tags: {escape(', '.join(c.get('tags',[])))}</p><p>{links}</p><p>hashes: {escape(str(c.get('hashes',{})))}</p></body></html>"
        (out / c["card_file"]).write_text(card_html, encoding="utf-8")
        rows.append(f"<tr><td>{i}</td><td><a href='{escape(c['card_file'])}'>{escape(c['card_id'])}</a></td><td>{escape(str(c['prompt']))}</td><td>{escape(str(c['seed']))}</td><td>{escape(str(c['mode']))}</td></tr>")
        md_cards.append(f"## {c['card_id']}\n\n- prompt: {c.get('prompt')}\n- tags: {', '.join(c.get('tags', []))}\n- preview_zip: {c.get('links',{}).get('preview_zip')}\n- hashes: {c.get('hashes')}\n")

    index_html=f"<html><head><title>{escape(m['title'])}</title><style>body{{font-family:sans-serif}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:6px}}</style></head><body><h1>{escape(m['title'])}</h1><h2>{escape(m['subtitle'])}</h2><p>card_count: {m['card_count']}</p><p>source_collection_export_hash: {escape(str(m['source_collection_export_hash']))}</p><table><tr><th>#</th><th>card</th><th>prompt</th><th>seed</th><th>mode</th></tr>{''.join(rows)}</table><p>WaveForgeStudio offline release deck only — assets are linked, not copied.</p></body></html>"
    (out / "index.html").write_text(index_html, encoding="utf-8")
    md=f"# {m['title']}\n\n{subtitle}\n\n- card_count: {m['card_count']}\n- source_collection_export_hash: {m['source_collection_export_hash']}\n\n" + "\n".join(md_cards) + "\nWaveForgeStudio offline release deck only — assets are linked, not copied.\n"
    (out / "RELEASE_DECK.md").write_text(md, encoding="utf-8")
    (out / "release_deck_manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    (out / "release_deck_receipt.json").write_text(json.dumps(m["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    return m


def validate_release_deck_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get("schema")!="waveforge.release_deck_manifest.v2_alpha": e.append("schema invalid")
    p=manifest.get("deck_policy",{})
    for k,v in {"offline_html_deck":True,"copies_assets":False,"external_calls_allowed":False,"subprocess_allowed":False,"network_allowed":False,"hosting":False,"browser_automation":False,"powerpoint":False,"video_rendering":False,"muxing":False}.items():
        if p.get(k) is not v: e.append(f"{k} must be {v}")
    if not manifest.get("outputs",{}).get("index"): e.append("outputs.index required")
    if not manifest.get("outputs",{}).get("markdown"): e.append("outputs.markdown required")
    if not manifest.get("receipt",{}).get("release_deck_hash"): e.append("receipt.release_deck_hash required")
    if not isinstance(manifest.get("cards"), list): e.append("cards list required")
    if manifest.get("card_count")!=len(manifest.get("cards",[])): e.append("card_count mismatch")
    if not manifest.get("title"): e.append("title required")
    return e


def assert_valid_release_deck_manifest(manifest: dict) -> None:
    e=validate_release_deck_manifest(manifest)
    if e: raise ValueError("Invalid release deck manifest: "+"; ".join(e))


def read_release_deck_info(deck_dir: str | Path) -> dict:
    d=Path(deck_dir)
    idx=d/'index.html'; man=d/'release_deck_manifest.json'; rec=d/'release_deck_receipt.json'; md=d/'RELEASE_DECK.md'
    card_count=0
    if man.exists(): card_count=json.loads(man.read_text(encoding='utf-8')).get('card_count',0)
    txt=idx.read_text(encoding='utf-8',errors='ignore').lower() if idx.exists() else ''
    return {"exists":d.exists(),"index_exists":idx.exists(),"manifest_exists":man.exists(),"receipt_exists":rec.exists(),"markdown_exists":md.exists(),"card_count":card_count,"contains_waveforge":"waveforge" in txt}
