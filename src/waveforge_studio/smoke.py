from __future__ import annotations

import json
from pathlib import Path

from .alpha_artifacts import REQUIRED_ALPHA_ARTIFACTS
from .forge_workflow import run_forge_workflow
from .hashing import sha256_digest
from .release_manifest import write_release_manifest
from .studio_seal import write_studio_seal
from .version import DEFAULT_RELEASE_TIMESTAMP, PROJECT_NAME, RELEASE_NAME, __version__
from .local_audio_renderer import render_audio_stub
from .local_visual_renderer import render_visual_stub
from .local_av_preview import render_av_preview
from .preview_pack import write_preview_pack
from .preview_pack_zip import write_preview_pack_zip


def run_golden_demo_smoke(
    out_dir: str | Path,
    prompt: str = "The Sovereign Signal awakens across the infinite fractal wave.",
    duration_seconds: int = 72,
    seed: int = 369369,
    mode: str = "mythic-reel",
    render_audio: bool = False,
    render_visual: bool = False,
    av_preview: bool = False,
    preview_pack: bool = False,
    preview_pack_zip: bool = False,
) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    forge_report = run_forge_workflow(prompt=prompt, out_dir=out, duration_seconds=duration_seconds, seed=seed, mode=mode)
    packet = json.loads((out / "project.waveforge.json").read_text(encoding="utf-8"))
    audio_manifest = render_audio_stub(packet, out) if render_audio else None
    visual_manifest = render_visual_stub(packet, out) if render_visual else None
    preview_manifest = render_av_preview(packet, out) if av_preview else None
    pack_manifest = write_preview_pack(out) if (preview_pack or preview_pack_zip) else None
    zip_manifest = write_preview_pack_zip(out / "preview_pack") if preview_pack_zip else None
    release_manifest = write_release_manifest(out, packet=packet)
    write_studio_seal(out, release_manifest)
    release_manifest = write_release_manifest(out, packet=packet)
    write_studio_seal(out, release_manifest)

    present_files = {str(p.relative_to(out)).replace("\\", "/") for p in out.rglob("*") if p.is_file()}
    missing_artifacts = [f for f in REQUIRED_ALPHA_ARTIFACTS if f not in present_files]

    checks = [
        {"id": "check_001_version", "name": "Version metadata present", "passed": bool(__version__)},
        {"id": "check_002_release_manifest_alpha_ready", "name": "Release manifest alpha_ready true", "passed": bool(release_manifest.get("alpha_ready"))},
        {"id": "check_003_studio_seal", "name": "STUDIO_SEAL.md exists", "passed": "STUDIO_SEAL.md" in present_files},
        {"id": "check_004_artifact_ledger", "name": "artifact_ledger.json exists", "passed": "artifact_ledger.json" in present_files},
        {"id": "check_005_forge_report", "name": "forge_report.json exists", "passed": "forge_report.json" in present_files},
        {"id": "check_006_required_artifacts", "name": "All required alpha artifacts are present", "passed": len(missing_artifacts) == 0},
    ]
    if render_audio:
        checks.append({"id": "check_007_local_audio_stub", "name": "Local audio stub rendered", "passed": (out / "render" / "audio_mix.wav").exists() and audio_manifest is not None})
    if render_visual:
        checks.append({"id": "check_008_local_visual_stub", "name": "Local visual storyboard rendered", "passed": (out / "render" / "storyboard" / "frame_001.svg").exists() and visual_manifest is not None})
    if av_preview:
        checks.append({"id": "check_009_local_av_preview", "name": "Local AV preview rendered", "passed": (out / "render" / "av_preview.html").exists() and preview_manifest is not None})
    if preview_pack or preview_pack_zip:
        checks.append({"id": "check_010_preview_pack", "name": "Portable preview pack created", "passed": (out / "preview_pack" / "index.html").exists() and pack_manifest is not None})
    if preview_pack_zip:
        checks.append({"id": "check_011_preview_pack_zip", "name": "Portable preview ZIP created", "passed": (out / "preview_pack" / "preview_pack.zip").exists() and zip_manifest is not None})

    smoke_passed = all(c["passed"] for c in checks)
    report = {
        "schema": "waveforge.smoke_report.v1_alpha",
        "project": PROJECT_NAME,
        "version": __version__,
        "release_name": RELEASE_NAME,
        "prompt": prompt,
        "seed": seed,
        "duration_seconds": duration_seconds,
        "mode": mode,
        "alpha_ready": bool(release_manifest.get("alpha_ready")),
        "checks": checks,
        "required_artifacts": REQUIRED_ALPHA_ARTIFACTS,
        "missing_artifacts": missing_artifacts,
        "source_packet_hash": forge_report.get("source_packet_hash", ""),
        "artifact_ledger_hash": forge_report.get("artifact_ledger_hash", ""),
        "release_hash": release_manifest.get("receipt", {}).get("release_hash", ""),
        "smoke_passed": smoke_passed,
    }
    smoke_hash = sha256_digest(report)
    report["receipt"] = {
        "schema": "waveforge.smoke_report_receipt.v1_alpha",
        "smoke_hash": smoke_hash,
        "created_at": DEFAULT_RELEASE_TIMESTAMP,
    }
    return report


def write_golden_demo_smoke(out_dir: str | Path, **kwargs) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    report = run_golden_demo_smoke(out, **kwargs)
    (out / "smoke_report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (out / "smoke_report_receipt.json").write_text(json.dumps(report["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "SMOKE_SUMMARY.md").write_text(
        "# Golden Demo Smoke Summary\n\n"
        f"- smoke_passed: {report['smoke_passed']}\n"
        f"- alpha_ready: {report['alpha_ready']}\n"
        f"- release_hash: {report['release_hash']}\n"
        f"- smoke_hash: {report['receipt']['smoke_hash']}\n",
        encoding="utf-8",
    )
    return report
