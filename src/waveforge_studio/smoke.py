from __future__ import annotations

import json
from pathlib import Path

from .alpha_artifacts import REQUIRED_ALPHA_ARTIFACTS
from .forge_workflow import run_forge_workflow
from .hashing import sha256_digest
from .release_manifest import write_release_manifest
from .studio_seal import write_studio_seal
from .version import DEFAULT_RELEASE_TIMESTAMP, PROJECT_NAME, RELEASE_NAME, __version__


def run_golden_demo_smoke(
    out_dir: str | Path,
    prompt: str = "The Sovereign Signal awakens across the infinite fractal wave.",
    duration_seconds: int = 72,
    seed: int = 369369,
    mode: str = "mythic-reel",
) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    forge_report = run_forge_workflow(prompt=prompt, out_dir=out, duration_seconds=duration_seconds, seed=seed, mode=mode)
    packet = json.loads((out / "project.waveforge.json").read_text(encoding="utf-8"))
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
