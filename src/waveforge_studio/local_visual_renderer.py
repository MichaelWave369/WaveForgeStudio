from __future__ import annotations

import json
from html import escape
from pathlib import Path

from .av_timeline import create_av_timeline
from .hashing import canonical_json, sha256_digest
from .renderer_handoff import create_renderer_handoff
from .validation import validate_media_packet
from .version import DEFAULT_RELEASE_TIMESTAMP


def _bound(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))


def create_visual_render_manifest(packet: dict, frame_count: int = 9, width: int = 1280, height: int = 720) -> dict:
    frame_count = _bound(frame_count, 1, 36)
    width = _bound(width, 320, 3840)
    height = _bound(height, 240, 2160)
    timeline = create_av_timeline(packet)
    handoff = create_renderer_handoff(packet)
    frames = [f"render/storyboard/frame_{i:03d}.svg" for i in range(1, frame_count + 1)]
    m = {
        "schema": "waveforge.local_visual_render_manifest.v1_alpha",
        "project": "WaveForgeStudio",
        "version": "1.2-alpha",
        "source_packet_hash": packet.get("receipt", {}).get("packet_hash", sha256_digest(packet)),
        "seed": int(packet.get("seed", 0) or 0),
        "mode": packet.get("mode", "mythic-reel"),
        "duration_seconds": int(packet.get("duration_seconds", 0) or 0),
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "render_policy": {
            "local_only": True,
            "stdlib_only": True,
            "external_calls_allowed": False,
            "subprocess_allowed": False,
            "network_allowed": False,
            "image_generation": False,
            "video_rendering": False,
            "placeholder_visuals": True,
        },
        "outputs": {"storyboard_index": "render/storyboard_index.html", "frames": frames},
        "timeline_reference": {"schema": "waveforge.av_timeline.v0", "timeline_hash": timeline["receipt"]["timeline_hash"]},
        "handoff_reference": {"schema": "waveforge.renderer_handoff.v0", "handoff_hash": handoff["receipt"]["handoff_hash"]},
    }
    m["receipt"] = {
        "schema": "waveforge.local_visual_render_receipt.v1_alpha",
        "visual_render_hash": sha256_digest(json.loads(canonical_json(m))),
        "source_packet_hash": m["source_packet_hash"],
        "created_at": DEFAULT_RELEASE_TIMESTAMP,
    }
    return m


def _svg_frame(packet: dict, manifest: dict, idx: int) -> str:
    w, h = manifest["width"], manifest["height"]
    seed = manifest["seed"]
    c = ["#0f172a", "#111827", "#1f2937", "#0b1020"][(seed + idx) % 4]
    accent = ["#22d3ee", "#a78bfa", "#f59e0b", "#34d399"][(seed * (idx + 3)) % 4]
    prompt = escape(packet.get("intent", {}).get("prompt", ""))
    scenes = packet.get("visual", {}).get("scenes", [])
    symbols = packet.get("visual", {}).get("symbols", [])
    sc = scenes[(idx - 1) % len(scenes)] if scenes else {}
    scene_label = escape(str(sc.get("label", sc.get("name", f"scene_{idx}"))))
    sym = escape(str(symbols[(idx - 1) % len(symbols)] if symbols else "phi_symbol"))
    marker_time = round((idx - 1) * (max(1, manifest["duration_seconds"]) / max(1, manifest["frame_count"])), 2)
    circles = "".join([f'<circle cx="{w//2}" cy="{h//2}" r="{80 + i*60}" fill="none" stroke="{accent}" stroke-opacity="0.25"/>' for i in range(3)])
    nodes = "".join([f'<circle cx="{120+i*40}" cy="{h-80}" r="6" fill="{accent}"/>' for i in range(6)])
    dots = "".join([f'<circle cx="{w-220+i*18}" cy="70" r="4" fill="{accent}"/>' for i in range(9)])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<rect width="100%" height="100%" fill="{c}"/>
{circles}
{nodes}
{dots}
<text x="48" y="56" fill="#e5e7eb" font-size="28">WaveForgeStudio</text>
<text x="48" y="96" fill="#cbd5e1" font-size="20">Frame {idx:03d}</text>
<text x="48" y="132" fill="#cbd5e1" font-size="18">Scene: {scene_label}</text>
<text x="48" y="164" fill="#cbd5e1" font-size="18">Symbol: {sym}</text>
<text x="48" y="196" fill="#cbd5e1" font-size="18">Marker: {marker_time}s</text>
<text x="48" y="228" fill="#cbd5e1" font-size="15">placeholder visual — no image generation</text>
<text x="48" y="{h-40}" fill="#94a3b8" font-size="13">{prompt}</text>
</svg>'''


def render_visual_stub(packet: dict, out_dir: str | Path, frame_count: int = 9, width: int = 1280, height: int = 720) -> dict:
    errs = validate_media_packet(packet)
    if errs:
        raise ValueError("Invalid media packet: " + "; ".join(errs))
    out = Path(out_dir)
    m = create_visual_render_manifest(packet, frame_count=frame_count, width=width, height=height)
    sb = out / "render" / "storyboard"
    sb.mkdir(parents=True, exist_ok=True)
    for i, fp in enumerate(m["outputs"]["frames"], start=1):
        (out / fp).write_text(_svg_frame(packet, m, i), encoding="utf-8")
    links = "\n".join([f'<li><a href="{escape(Path(f).name)}">{escape(Path(f).name)}</a></li>' for f in m["outputs"]["frames"]])
    (out / m["outputs"]["storyboard_index"]).write_text(f"<html><body><h1>WaveForgeStudio Storyboard</h1><p>placeholder visual — no image generation</p><ul>{links}</ul></body></html>", encoding="utf-8")
    (out / "visual_render_manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    (out / "visual_render_receipt.json").write_text(json.dumps(m["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "VISUAL_RENDER_SUMMARY.md").write_text(f"# Visual Render Summary\n\n- frame_count: {m['frame_count']}\n- storyboard_index: {m['outputs']['storyboard_index']}\n- visual_render_hash: {m['receipt']['visual_render_hash']}\n", encoding="utf-8")
    return m


def read_svg_info(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        return {"exists": False, "size_bytes": 0, "contains_svg": False, "contains_waveforge": False}
    txt = p.read_text(encoding="utf-8", errors="ignore")
    return {"exists": True, "size_bytes": p.stat().st_size, "contains_svg": "<svg" in txt.lower(), "contains_waveforge": "waveforge" in txt.lower()}


def validate_visual_render_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get("schema") != "waveforge.local_visual_render_manifest.v1_alpha": e.append("schema invalid")
    rp=manifest.get("render_policy", {})
    if rp.get("local_only") is not True: e.append("local_only must be true")
    for k in ["external_calls_allowed","subprocess_allowed","network_allowed","image_generation","video_rendering"]:
        if rp.get(k) is not False: e.append(f"{k} must be false")
    if rp.get("placeholder_visuals") is not True: e.append("placeholder_visuals must be true")
    if not manifest.get("outputs", {}).get("storyboard_index"): e.append("outputs.storyboard_index required")
    if len(manifest.get("outputs", {}).get("frames", [])) < 1: e.append("at least 1 frame required")
    if not manifest.get("receipt", {}).get("visual_render_hash"): e.append("receipt.visual_render_hash required")
    return e


def assert_valid_visual_render_manifest(manifest: dict) -> None:
    e=validate_visual_render_manifest(manifest)
    if e: raise ValueError("Invalid visual render manifest: " + "; ".join(e))
