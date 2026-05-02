from __future__ import annotations

import json
from pathlib import Path

from ..coherence import score_media_coherence
from ..constants import C_STAR
from ..hashing import canonical_json, sha256_digest

_STABLE_TS = "1979-03-06T03:06:09Z"
_DOCTRINE = "Intent → Signal → Sound → World → Artifact"


def create_wavetalk_bundle(packet: dict) -> dict:
    source_packet_hash = sha256_digest(packet)
    coh = score_media_coherence(packet)
    packet_receipt = packet.get("receipt", {})
    route_id = sha256_digest({"seed": packet.get("seed"), "mode": packet.get("mode"), "source": source_packet_hash})[:16]

    bundle = {
        "schema": "waveforge.wavetalk_bundle.v0",
        "project": "WaveForgeStudio",
        "target_adapter": "WaveTalk",
        "source_packet_hash": source_packet_hash,
        "seed": packet.get("seed"),
        "duration_seconds": packet.get("duration_seconds"),
        "mode": packet.get("mode"),
        "signal": {
            "intent_prompt": packet.get("intent", {}).get("prompt"),
            "archetype": packet.get("intent", {}).get("archetype"),
            "purpose": packet.get("intent", {}).get("purpose"),
            "doctrine": _DOCTRINE,
        },
        "routing": {
            "route_id": route_id,
            "route_kind": "sovereign_media_compile",
            "source": "WaveForgeStudio",
            "targets": ["PHIAudio", "WaveRider", "TimelinePreview", "ProductionBundle"],
            "status": "planned",
        },
        "governance": {
            "mode": "observe",
            "coherence_threshold": C_STAR,
            "coherence_overall": coh["overall"],
            "coherence_passed": coh["passed"],
            "policy_state": "stub",
            "review_required": False,
        },
        "memory": {
            "memory_schema": "waveforge.sml_memory_stub.v0",
            "lineage": packet_receipt.get("lineage", []),
            "source_packet_hash": source_packet_hash,
            "artifact_hashes": {
                "packet": source_packet_hash,
                "receipt": packet_receipt.get("packet_hash", ""),
            },
            "continuity_state": "planned",
        },
        "replay": {
            "deterministic": True,
            "seed": packet.get("seed"),
            "canonical_hashing": "sha256(sorted_compact_json)",
            "created_at": _STABLE_TS,
        },
        "receipts": {
            "packet_receipt": packet_receipt,
        },
    }

    bundle_hash = sha256_digest(json.loads(canonical_json(bundle)))
    bundle["receipts"]["signal_receipt"] = {
        "schema": "waveforge.wavetalk_bridge_receipt.v0",
        "bundle_hash": bundle_hash,
        "source_packet_hash": source_packet_hash,
        "created_at": _STABLE_TS,
    }
    return bundle


def write_wavetalk_bundle(packet: dict, out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bundle = create_wavetalk_bundle(packet)
    (out / "wavetalk_bundle.json").write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    (out / "wavetalk_signal.json").write_text(json.dumps(bundle["signal"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "wavetalk_routing.json").write_text(json.dumps(bundle["routing"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "wavetalk_governance.json").write_text(json.dumps(bundle["governance"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "wavetalk_memory.json").write_text(json.dumps(bundle["memory"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "wavetalk_replay.json").write_text(json.dumps(bundle["replay"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "wavetalk_receipt.json").write_text(json.dumps(bundle["receipts"]["signal_receipt"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "WAVETALK_BRIDGE_SUMMARY.md").write_text(
        f"# WaveTalk Bridge Summary\n\n- Bundle Hash: {bundle['receipts']['signal_receipt']['bundle_hash']}\n- Source Packet Hash: {bundle['source_packet_hash']}\n",
        encoding="utf-8",
    )
    return bundle
