from __future__ import annotations

import html
from pathlib import Path

from .coherence import score_media_coherence
from .constants import C_STAR, LAMBDA, OMEGA_C, PHI


def _li(items: list[dict], keys: list[str]) -> str:
    out = []
    for item in items:
        parts = [f"{k}: {item.get(k)}" for k in keys]
        out.append(f"<li>{html.escape(' | '.join(parts))}</li>")
    return "\n".join(out)


def create_timeline_preview_html(packet: dict) -> str:
    coherence = score_media_coherence(packet)
    s = packet.get("structure", {})
    audio = packet.get("audio", {})
    visual = packet.get("visual", {})
    sync = packet.get("sync", {})
    receipt = packet.get("receipt", {})

    prompt = html.escape(packet.get("intent", {}).get("prompt", ""))
    pass_fail = "PASS" if coherence.get("passed") else "FAIL"

    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\" />
<title>WaveForgeStudio Timeline Preview</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 24px; background: #111; color: #f2f2f2; }}
section {{ border: 1px solid #333; padding: 12px; margin: 12px 0; border-radius: 8px; }}
h1,h2 {{ color: #ffd166; }}
small {{ color: #aaa; }}
ul {{ margin: 0; padding-left: 20px; }}
</style>
</head>
<body>
<h1>WaveForgeStudio Timeline Preview</h1>
<section><h2>Packet</h2>
<p>project: {packet.get('project')} | schema: {packet.get('schema')} | seed: {packet.get('seed')} | mode: {packet.get('mode')} | duration: {packet.get('duration_seconds')}</p>
<p>prompt: {prompt}</p></section>
<section><h2>PHI369 Constants</h2>
<p>PHI={PHI} LAMBDA={LAMBDA} C_STAR={C_STAR} OMEGA_C={OMEGA_C}</p>
<p>Coherence overall={coherence.get('overall')} ({pass_fail})</p></section>
<section><h2>3 Acts</h2><ul>{_li(s.get('acts', []), ['act','start','end'])}</ul></section>
<section><h2>6 Scenes</h2><ul>{_li(s.get('scenes', []), ['scene','start','end'])}</ul></section>
<section><h2>9 Sync Events</h2><ul>{_li(sync.get('events', []), ['event','timestamp','binding'])}</ul></section>
<section><h2>Audio Sections</h2><ul>{_li(audio.get('sections', []), ['name','start','end'])}</ul></section>
<section><h2>Visual Scenes/Shots</h2>
<p>scene_count={len(visual.get('scenes', []))} shot_count={len(visual.get('shots', []))}</p>
<ul>{_li(visual.get('scenes', []), ['scene','start','end'])}</ul></section>
<section><h2>PHI Cut Points</h2><ul>{_li(s.get('phi_cuts', []), ['ratio','timestamp'])}</ul></section>
<section><h2>Receipt</h2>
<p>packet_hash={receipt.get('packet_hash')}</p>
<p>content_hash={receipt.get('content_hash')}</p></section>
<footer><small>Deterministic preview only — no media rendered.</small></footer>
</body></html>"""


def write_timeline_preview(packet: dict, out_dir: str | Path) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "timeline_preview.html"
    path.write_text(create_timeline_preview_html(packet), encoding="utf-8")
    return path
