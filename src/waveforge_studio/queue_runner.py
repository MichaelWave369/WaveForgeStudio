from __future__ import annotations

import json
from pathlib import Path

from .adapters.phiaudio_bridge import write_phiaudio_bundle
from .adapters.waverider_bridge import write_waverider_bundle
from .adapters.wavetalk_bridge import write_wavetalk_bundle
from .artifact_ledger import write_artifact_ledger
from .hashing import canonical_json, sha256_digest
from .production_bundle import write_production_bundle
from .render_queue import create_render_queue, validate_render_queue
from .timeline_preview import write_timeline_preview
from .av_timeline import write_av_timeline
from .validation import validate_media_packet

_STABLE_TS = "1979-03-06T03:06:09Z"


def run_queue_safe(packet: dict, out_dir: str | Path, queue: dict | None = None) -> dict:
    errs = validate_media_packet(packet)
    if errs:
        raise ValueError("Invalid media packet: " + "; ".join(errs))
    q = queue or create_render_queue(packet)
    qerrs = validate_render_queue(q)
    if qerrs:
        raise ValueError("Invalid render queue: " + "; ".join(qerrs))

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "render_queue.json").write_text(json.dumps(q, indent=2, sort_keys=True), encoding="utf-8")
    (out / "render_queue_receipt.json").write_text(json.dumps(q["receipt"], indent=2, sort_keys=True), encoding="utf-8")

    jobs_report = []
    failed = 0
    for job in q["jobs"]:
        jid = job["id"]
        if jid == "job_001_wavetalk_signal":
            write_wavetalk_bundle(packet, out / "wavetalk"); status, executed = "completed", True
        elif jid == "job_002_phiaudio_audio":
            write_phiaudio_bundle(packet, out / "phiaudio"); status, executed = "completed", True
        elif jid == "job_003_waverider_visual":
            write_waverider_bundle(packet, out / "waverider"); status, executed = "completed", True
        elif jid == "job_004_timeline_preview":
            write_timeline_preview(packet, out); status, executed = "completed", True
        elif jid == "job_005_production_bundle":
            write_production_bundle(packet, out); status, executed = "completed", True
        elif jid in {"job_006_future_audio_render", "job_007_future_video_render", "job_008_future_final_mux"}:
            status, executed = "blocked_plan_only", False
        elif jid == "job_009_final_receipt":
            status, executed = "completed", True
        else:
            status, executed = "failed", False; failed += 1
        jobs_report.append({"id": jid, "status": status, "executed": executed, "outputs": job.get("outputs", [])})

    write_av_timeline(packet, out)
    ledger = write_artifact_ledger(out)
    completed = sum(1 for j in jobs_report if j["status"] == "completed")
    blocked = sum(1 for j in jobs_report if j["status"] == "blocked_plan_only")
    report = {
        "schema": "waveforge.safe_queue_execution.v0",
        "project": "WaveForgeStudio",
        "source_packet_hash": sha256_digest(packet),
        "queue_hash": q["receipt"]["queue_hash"],
        "mode": "safe_local_exports_only",
        "execution_policy": {"external_calls_allowed": False, "subprocess_allowed": False, "network_allowed": False, "real_rendering_allowed": False},
        "jobs": jobs_report,
        "completed_count": completed,
        "blocked_count": blocked,
        "failed_count": failed,
        "artifact_ledger": {"path": "artifact_ledger.json", "ledger_hash": ledger["receipt"]["ledger_hash"]},
    }
    ex_hash = sha256_digest(json.loads(canonical_json(report)))
    report["receipt"] = {"schema": "waveforge.safe_queue_execution_receipt.v0", "execution_hash": ex_hash, "source_packet_hash": report["source_packet_hash"], "queue_hash": report["queue_hash"], "created_at": _STABLE_TS}
    return report


def write_queue_execution(packet: dict, out_dir: str | Path, queue: dict | None = None) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    report = run_queue_safe(packet, out, queue=queue)
    (out / "execution_report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (out / "execution_receipt.json").write_text(json.dumps(report["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    lines = "\n".join([f"- {j['id']}: {j['status']}" for j in report["jobs"]])
    (out / "EXECUTION_SUMMARY.md").write_text(
        f"# Safe Queue Execution Summary\n\n- Source Packet Hash: {report['source_packet_hash']}\n- Queue Hash: {report['queue_hash']}\n- Execution Mode: {report['mode']}\n- Completed: {report['completed_count']}\n- Blocked: {report['blocked_count']}\n- Failed: {report['failed_count']}\n- Artifact Ledger Hash: {report['artifact_ledger']['ledger_hash']}\n- Execution Hash: {report['receipt']['execution_hash']}\n\n## Jobs\n{lines}\n\nSafe local export runner only — no media rendered in v0.7.\n",
        encoding="utf-8",
    )
    return report
