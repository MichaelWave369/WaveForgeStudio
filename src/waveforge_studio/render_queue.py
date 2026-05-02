from __future__ import annotations

import json
from pathlib import Path

from .hashing import canonical_json, sha256_digest

_STABLE_TS = "1979-03-06T03:06:09Z"


def create_render_queue(packet: dict) -> dict:
    source_packet_hash = sha256_digest(packet)
    jobs = [
        {"id": "job_001_wavetalk_signal", "kind": "bridge_export", "adapter": "WaveTalk", "status": "planned", "depends_on": [], "inputs": ["project.waveforge.json"], "outputs": ["wavetalk/wavetalk_bundle.json"], "description": "Export governed signal/governance/memory contract."},
        {"id": "job_002_phiaudio_audio", "kind": "bridge_export", "adapter": "PHIAudio", "status": "planned", "depends_on": ["job_001_wavetalk_signal"], "inputs": ["project.waveforge.json"], "outputs": ["phiaudio/phiaudio_bundle.json"], "description": "Export planned audio/composition/stem contract."},
        {"id": "job_003_waverider_visual", "kind": "bridge_export", "adapter": "WaveRider", "status": "planned", "depends_on": ["job_001_wavetalk_signal"], "inputs": ["project.waveforge.json"], "outputs": ["waverider/waverider_bundle.json"], "description": "Export planned visual/world/scene contract."},
        {"id": "job_004_timeline_preview", "kind": "preview_export", "adapter": "TimelinePreview", "status": "planned", "depends_on": ["job_002_phiaudio_audio", "job_003_waverider_visual"], "inputs": ["project.waveforge.json"], "outputs": ["timeline_preview.html"], "description": "Generate deterministic audiovisual timeline preview."},
        {"id": "job_005_production_bundle", "kind": "bundle_export", "adapter": "WaveForgeStudio", "status": "planned", "depends_on": ["job_001_wavetalk_signal", "job_002_phiaudio_audio", "job_003_waverider_visual", "job_004_timeline_preview"], "inputs": ["project.waveforge.json"], "outputs": ["production_bundle.json", "PRODUCTION_SUMMARY.md"], "description": "Create unified governed production bundle."},
        {"id": "job_006_future_audio_render", "kind": "future_render", "adapter": "PHIAudio", "status": "blocked_plan_only", "depends_on": ["job_002_phiaudio_audio"], "inputs": ["phiaudio/phiaudio_bundle.json"], "outputs": ["render/audio_mix.wav", "render/stems/"], "description": "Future real audio render placeholder."},
        {"id": "job_007_future_video_render", "kind": "future_render", "adapter": "WaveRider", "status": "blocked_plan_only", "depends_on": ["job_003_waverider_visual"], "inputs": ["waverider/waverider_bundle.json"], "outputs": ["render/video_timeline.json", "render/frames/"], "description": "Future real visual render placeholder."},
        {"id": "job_008_future_final_mux", "kind": "future_render", "adapter": "WaveForgeStudio", "status": "blocked_plan_only", "depends_on": ["job_006_future_audio_render", "job_007_future_video_render"], "inputs": ["render/audio_mix.wav", "render/video_timeline.json"], "outputs": ["render/final_video.mp4"], "description": "Future audio/video mux placeholder."},
        {"id": "job_009_final_receipt", "kind": "receipt_export", "adapter": "WaveForgeStudio", "status": "planned", "depends_on": ["job_005_production_bundle"], "inputs": ["production_bundle.json"], "outputs": ["render_queue_receipt.json"], "description": "Create render queue receipt."},
    ]
    queue = {
        "schema": "waveforge.render_queue.v0",
        "project": "WaveForgeStudio",
        "source_packet_hash": source_packet_hash,
        "seed": packet.get("seed"),
        "mode": packet.get("mode"),
        "duration_seconds": packet.get("duration_seconds"),
        "execution_policy": {
            "mode": "plan_only",
            "external_calls_allowed": False,
            "subprocess_allowed": False,
            "network_allowed": False,
            "real_rendering_allowed": False,
        },
        "jobs": jobs,
        "job_count": 9,
        "planned_count": sum(1 for j in jobs if j["status"] == "planned"),
        "blocked_count": sum(1 for j in jobs if j["status"] == "blocked_plan_only"),
    }
    qhash = sha256_digest(json.loads(canonical_json(queue)))
    queue["receipt"] = {"schema": "waveforge.render_queue_receipt.v0", "queue_hash": qhash, "source_packet_hash": source_packet_hash, "created_at": _STABLE_TS}
    return queue


def validate_render_queue(queue: dict) -> list[str]:
    e = []
    if queue.get("schema") != "waveforge.render_queue.v0":
        e.append("schema must be waveforge.render_queue.v0")
    if queue.get("job_count") != 9:
        e.append("job_count must be 9")
    jobs = queue.get("jobs", [])
    ids = [j.get("id") for j in jobs]
    if len(ids) != len(set(ids)):
        e.append("job ids must be unique")
    idset = set(ids)
    for j in jobs:
        for d in j.get("depends_on", []):
            if d not in idset:
                e.append(f"unknown dependency: {d}")
        if j.get("kind") == "future_render" and j.get("status") != "blocked_plan_only":
            e.append("future_render jobs must be blocked_plan_only")
    pol = queue.get("execution_policy", {})
    if pol.get("mode") != "plan_only":
        e.append("execution_policy.mode must be plan_only")
    for k in ["external_calls_allowed", "subprocess_allowed", "network_allowed", "real_rendering_allowed"]:
        if pol.get(k) is not False:
            e.append(f"execution_policy.{k} must be false")
    if "queue_hash" not in queue.get("receipt", {}):
        e.append("receipt.queue_hash is required")
    return e


def assert_valid_render_queue(queue: dict) -> None:
    errs = validate_render_queue(queue)
    if errs:
        raise ValueError("Invalid render queue: " + "; ".join(errs))


def write_render_queue(packet: dict, out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    q = create_render_queue(packet)
    (out / "render_queue.json").write_text(json.dumps(q, indent=2, sort_keys=True), encoding="utf-8")
    (out / "render_queue_receipt.json").write_text(json.dumps(q["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    lines = "\n".join([f"- {j['id']} ({j['kind']}) [{j['status']}]" for j in q["jobs"]])
    (out / "RENDER_QUEUE_SUMMARY.md").write_text(
        f"# Render Queue Summary\n\n- Source Packet Hash: {q['source_packet_hash']}\n- Seed: {q['seed']}\n- Duration: {q['duration_seconds']}\n- Execution Policy: plan_only\n- Planned: {q['planned_count']}\n- Blocked: {q['blocked_count']}\n- Queue Hash: {q['receipt']['queue_hash']}\n\n## Jobs\n{lines}\n\nPlan-only render queue — no media rendered in v0.6.\n",
        encoding="utf-8",
    )
    return q
