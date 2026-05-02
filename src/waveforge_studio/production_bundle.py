from __future__ import annotations

import json
from pathlib import Path

from .adapters.phiaudio_bridge import create_phiaudio_bundle, write_phiaudio_bundle
from .adapters.waverider_bridge import create_waverider_bundle, write_waverider_bundle
from .adapters.wavetalk_bridge import create_wavetalk_bundle, write_wavetalk_bundle
from .coherence import score_media_coherence
from .constants import C_STAR, LAMBDA, OMEGA_C, PHI
from .hashing import canonical_json, sha256_digest
from .render_manifest import create_render_manifest
from .timeline_preview import write_timeline_preview
from .av_timeline import write_av_timeline, create_av_timeline
from .renderer_handoff import write_renderer_handoff

_STABLE_TS = "1979-03-06T03:06:09Z"
_DOCTRINE = "Intent → Signal → Sound → World → Artifact"


def create_production_bundle(packet: dict) -> dict:
    source_packet_hash = sha256_digest(packet)
    phia = create_phiaudio_bundle(packet)
    wave = create_waverider_bundle(packet)
    talk = create_wavetalk_bundle(packet)
    coh = score_media_coherence(packet)

    bundle = {
        "schema": "waveforge.production_bundle.v0",
        "project": "WaveForgeStudio",
        "seed": packet.get("seed"),
        "mode": packet.get("mode"),
        "duration_seconds": packet.get("duration_seconds"),
        "source_packet_hash": source_packet_hash,
        "doctrine": _DOCTRINE,
        "contents": {
            "media_packet": "project.waveforge.json",
            "audio_graph": "audio_graph.json",
            "visual_graph": "visual_graph.json",
            "sync_lattice": "sync_lattice.json",
            "render_manifest": "render_manifest.json",
            "receipt": "receipt.json",
            "timeline_preview": "timeline_preview.html",
            "phiaudio_bundle": "phiaudio/phiaudio_bundle.json",
            "waverider_bundle": "waverider/waverider_bundle.json",
            "wavetalk_bundle": "wavetalk/wavetalk_bundle.json",
            "render_queue": "render_queue.json",
            "av_timeline": "av_timeline.json",
            "renderer_handoff": "renderer_handoff.json",
        },
        "contracts": {
            "phiaudio": {"schema": phia["schema"], "bundle_hash": phia["receipt"]["bundle_hash"]},
            "waverider": {"schema": wave["schema"], "bundle_hash": wave["receipt"]["bundle_hash"]},
            "wavetalk": {"schema": talk["schema"], "bundle_hash": talk["receipts"]["signal_receipt"]["bundle_hash"]},
        },
        "coherence": {
            "threshold": C_STAR,
            "overall": coh["overall"],
            "passed": coh["passed"],
        },
    }
    bundle_hash = sha256_digest(json.loads(canonical_json(bundle)))
    bundle["receipt"] = {
        "schema": "waveforge.production_bundle_receipt.v0",
        "bundle_hash": bundle_hash,
        "source_packet_hash": source_packet_hash,
        "created_at": _STABLE_TS,
    }
    return bundle


def write_production_bundle(packet: dict, out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "project.waveforge.json").write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    (out / "audio_graph.json").write_text(json.dumps(packet.get("audio", {}), indent=2, sort_keys=True), encoding="utf-8")
    (out / "visual_graph.json").write_text(json.dumps(packet.get("visual", {}), indent=2, sort_keys=True), encoding="utf-8")
    (out / "sync_lattice.json").write_text(json.dumps(packet.get("sync", {}), indent=2, sort_keys=True), encoding="utf-8")
    (out / "render_manifest.json").write_text(json.dumps(create_render_manifest(packet), indent=2, sort_keys=True), encoding="utf-8")
    (out / "receipt.json").write_text(json.dumps(packet.get("receipt", {}), indent=2, sort_keys=True), encoding="utf-8")
    write_timeline_preview(packet, out)
    av = write_av_timeline(packet, out)
    rh = write_renderer_handoff(packet, out)
    write_phiaudio_bundle(packet, out / "phiaudio")
    write_waverider_bundle(packet, out / "waverider")
    write_wavetalk_bundle(packet, out / "wavetalk")

    prod = create_production_bundle(packet)
    (out / "production_bundle.json").write_text(json.dumps(prod, indent=2, sort_keys=True), encoding="utf-8")

    s = packet.get("structure", {})
    summary = f"""# WaveForgeStudio Production Summary

- Prompt: {packet.get('intent', {}).get('prompt')}
- Seed: {packet.get('seed')}
- Mode: {packet.get('mode')}
- Duration: {packet.get('duration_seconds')}
- Doctrine: {_DOCTRINE}
- 3/6/9 counts: acts={len(s.get('acts', []))}, scenes={len(s.get('scenes', []))}, sync={len(packet.get('sync', {}).get('events', []))}
- PHI constants: PHI={PHI}, LAMBDA={LAMBDA}, C_STAR={C_STAR}, OMEGA_C={OMEGA_C}
- Coherence: {prod['coherence']['overall']} passed={prod['coherence']['passed']}
- Source Packet Hash: {prod['source_packet_hash']}
- PHIAudio Bundle Hash: {prod['contracts']['phiaudio']['bundle_hash']}
- WaveRider Bundle Hash: {prod['contracts']['waverider']['bundle_hash']}
- WaveTalk Bundle Hash: {prod['contracts']['wavetalk']['bundle_hash']}
- WaveTalk role: signal / governance / memory / continuity
- AV Timeline Hash: {av['receipt']['timeline_hash']}
- AV timeline role: unified audio/video timing contract
- Renderer Handoff Hash: {rh['receipt']['handoff_hash']}
- Renderer handoff role: planned local adapter input pack
- Production Bundle Hash: {prod['receipt']['bundle_hash']}

Generated files:
- project.waveforge.json
- audio_graph.json
- visual_graph.json
- sync_lattice.json
- render_manifest.json
- receipt.json
- timeline_preview.html
- production_bundle.json
- phiaudio/*
- waverider/*
- wavetalk/*

Deterministic production bundle only — no media rendered in v0.4.
"""
    (out / "PRODUCTION_SUMMARY.md").write_text(summary, encoding="utf-8")
    return prod
