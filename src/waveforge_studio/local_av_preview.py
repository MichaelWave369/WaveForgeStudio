from __future__ import annotations

import json
from html import escape
from pathlib import Path

from .av_timeline import create_av_timeline
from .hashing import canonical_json, sha256_digest
from .validation import validate_media_packet
from .version import DEFAULT_RELEASE_TIMESTAMP


def _load_json(p: Path) -> dict | None:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def create_av_preview_manifest(packet: dict, out_dir: str | Path) -> dict:
    out = Path(out_dir)
    timeline = _load_json(out / "av_timeline.json") or create_av_timeline(packet)
    frames = sorted([p.relative_to(out).as_posix() for p in (out / "render" / "storyboard").glob("frame_*.svg")]) if (out / "render" / "storyboard").exists() else []
    audio_manifest = _load_json(out / "audio_render_manifest.json")
    visual_manifest = _load_json(out / "visual_render_manifest.json")
    m = {
        "schema": "waveforge.local_av_preview_manifest.v1_alpha",
        "project": "WaveForgeStudio",
        "version": "1.3-alpha",
        "source_packet_hash": packet.get("receipt", {}).get("packet_hash", sha256_digest(packet)),
        "seed": int(packet.get("seed", 0) or 0),
        "mode": packet.get("mode", "mythic-reel"),
        "duration_seconds": int(packet.get("duration_seconds", 0) or 0),
        "preview_policy": {
            "offline_only": True,
            "local_relative_assets": True,
            "external_calls_allowed": False,
            "subprocess_allowed": False,
            "network_allowed": False,
            "video_rendering": False,
            "muxing": False,
            "browser_automation": False,
        },
        "assets": {
            "audio_mix": {"path": "render/audio_mix.wav", "present": (out / "render/audio_mix.wav").exists()},
            "storyboard_index": {"path": "render/storyboard_index.html", "present": (out / "render/storyboard_index.html").exists()},
            "storyboard_frames": [{"path": f, "present": True} for f in frames],
        },
        "timeline_reference": {"schema": "waveforge.av_timeline.v0", "timeline_hash": timeline.get("receipt", {}).get("timeline_hash", "")},
        "render_references": {
            "audio_render_hash": (audio_manifest or {}).get("receipt", {}).get("audio_render_hash"),
            "visual_render_hash": (visual_manifest or {}).get("receipt", {}).get("visual_render_hash"),
        },
        "outputs": {"preview_html": "render/av_preview.html"},
    }
    m["receipt"] = {
        "schema": "waveforge.local_av_preview_receipt.v1_alpha",
        "av_preview_hash": sha256_digest(json.loads(canonical_json(m))),
        "source_packet_hash": m["source_packet_hash"],
        "created_at": DEFAULT_RELEASE_TIMESTAMP,
    }
    return m


def render_av_preview(packet: dict, out_dir: str | Path) -> dict:
    errs = validate_media_packet(packet)
    if errs:
        raise ValueError("Invalid media packet: " + "; ".join(errs))
    out = Path(out_dir)
    (out / "render").mkdir(parents=True, exist_ok=True)
    m = create_av_preview_manifest(packet, out)
    timeline = _load_json(out / "av_timeline.json") or create_av_timeline(packet)
    markers = timeline.get("markers", [])
    marker_html = "".join([f"<li>{escape(str(x.get('label','marker')))} @ {x.get('time')}</li>" for x in markers])
    frames_html = "".join([f'<figure><img src="{escape(x["path"])}" alt="{escape(x["path"])}" style="max-width:320px"><figcaption>{escape(x["path"])}</figcaption></figure>' for x in m["assets"]["storyboard_frames"]])
    audio_tag = f'<audio controls src="{escape(m["assets"]["audio_mix"]["path"])}"></audio>' if m["assets"]["audio_mix"]["present"] else '<p>Audio mix missing.</p>'
    html = f"""<html><head><meta charset='utf-8'><title>WaveForgeStudio Local AV Preview</title><style>body{{font-family:Arial;background:#0b1020;color:#e5e7eb}}.ok{{color:#34d399}}.bad{{color:#f87171}}</style></head><body>
<h1>WaveForgeStudio Local AV Preview</h1>
<p>project={escape(m['project'])} version={escape(m['version'])} mode={escape(m['mode'])} seed={m['seed']} duration={m['duration_seconds']}</p>
<p>audio: <span class='{ 'ok' if m['assets']['audio_mix']['present'] else 'bad'}'>{m['assets']['audio_mix']['present']}</span> | visual frames: <span class='{ 'ok' if len(m['assets']['storyboard_frames'])>0 else 'bad'}'>{len(m['assets']['storyboard_frames'])}</span> | preview muxed: <span class='bad'>false</span></p>
{audio_tag}
<h2>Storyboard</h2>{frames_html}
<h2>Timeline markers</h2><ul>{marker_html}</ul>
<h2>Hashes</h2><ul><li>source_packet_hash: {escape(m['source_packet_hash'])}</li><li>audio_render_hash: {escape(str(m['render_references']['audio_render_hash']))}</li><li>visual_render_hash: {escape(str(m['render_references']['visual_render_hash']))}</li><li>av_preview_hash: {escape(m['receipt']['av_preview_hash'])}</li></ul>
<p><strong>Offline preview only — no video rendered or muxed.</strong></p></body></html>"""
    (out / "render" / "av_preview.html").write_text(html, encoding="utf-8")
    (out / "av_preview_manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    (out / "av_preview_receipt.json").write_text(json.dumps(m["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "AV_PREVIEW_SUMMARY.md").write_text(f"# AV Preview Summary\n\n- preview_html: {m['outputs']['preview_html']}\n- audio_present: {m['assets']['audio_mix']['present']}\n- frame_count: {len(m['assets']['storyboard_frames'])}\n- av_preview_hash: {m['receipt']['av_preview_hash']}\n", encoding="utf-8")
    return m


def validate_av_preview_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get("schema")!="waveforge.local_av_preview_manifest.v1_alpha": e.append("schema invalid")
    p=manifest.get("preview_policy", {})
    if p.get("offline_only") is not True: e.append("offline_only true required")
    for k in ["external_calls_allowed","subprocess_allowed","network_allowed","video_rendering","muxing","browser_automation"]:
        if p.get(k) is not False: e.append(f"{k} must be false")
    if not manifest.get("outputs", {}).get("preview_html"): e.append("outputs.preview_html required")
    if not manifest.get("receipt", {}).get("av_preview_hash"): e.append("receipt.av_preview_hash required")
    if "storyboard_frames" not in manifest.get("assets", {}): e.append("assets.storyboard_frames required")
    return e


def assert_valid_av_preview_manifest(manifest: dict) -> None:
    e=validate_av_preview_manifest(manifest)
    if e: raise ValueError("Invalid av preview manifest: " + "; ".join(e))


def read_preview_info(path: str | Path) -> dict:
    p=Path(path)
    if not p.exists(): return {"exists": False, "size_bytes": 0, "contains_html": False, "contains_audio_tag": False, "contains_waveforge": False}
    t=p.read_text(encoding="utf-8", errors="ignore").lower()
    return {"exists": True, "size_bytes": p.stat().st_size, "contains_html": "<html" in t, "contains_audio_tag": "<audio" in t, "contains_waveforge": "waveforge" in t}
