from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters.phiaudio_bridge import write_phiaudio_bundle
from .adapters.registry import list_adapters
from .coherence import score_media_coherence
from .constants import C_STAR, LAMBDA, OMEGA_C, PHI
from .media_packet import create_media_packet
from .render_manifest import create_render_manifest
from .validation import validate_media_packet


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def compile_command(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    packet = create_media_packet(args.prompt, duration_seconds=args.duration, seed=args.seed, mode=args.mode)
    manifest = create_render_manifest(packet)

    _write_json(out / "project.waveforge.json", packet)
    _write_json(out / "audio_graph.json", packet["audio"])
    _write_json(out / "visual_graph.json", packet["visual"])
    _write_json(out / "sync_lattice.json", packet["sync"])
    _write_json(out / "render_manifest.json", manifest)
    _write_json(out / "receipt.json", packet["receipt"])

    shotlist = "\n".join([f"- Scene {s['scene']}: {s['start']}s -> {s['end']}s" for s in packet["visual"]["scenes"]])
    (out / "shotlist.md").write_text(f"# Shotlist\n\n{shotlist}\n", encoding="utf-8")
    voice = "\n".join([f"- {c['timestamp']}s: {c['cue']}" for c in packet["audio"]["voiceover_cues"]])
    (out / "voiceover.md").write_text(f"# Voiceover Cues\n\n{voice}\n", encoding="utf-8")

    coherence = score_media_coherence(packet)
    summary = f"""# WaveForgeStudio Run Summary

- Prompt: {packet['intent']['prompt']}
- Seed: {packet['seed']}
- Duration: {packet['duration_seconds']}
- Mode: {packet['mode']}
- PHI: {PHI}
- LAMBDA: {LAMBDA}
- C_STAR: {C_STAR}
- OMEGA_C: {OMEGA_C}
- Acts: {len(packet['structure'].get('acts', []))}
- Scenes: {len(packet['visual'].get('scenes', []))}
- Sync Events: {len(packet['sync'].get('events', []))}
- Coherence Overall: {coherence['overall']}
- Receipt Hash: {packet['receipt']['packet_hash']}
"""
    (out / "summary.md").write_text(summary, encoding="utf-8")

    if args.export_phiaudio:
        write_phiaudio_bundle(packet, out / "phiaudio")
    return 0


def validate_command(args: argparse.Namespace) -> int:
    packet = json.loads(Path(args.path).read_text(encoding="utf-8"))
    errors = validate_media_packet(packet)
    if errors:
        print("INVALID media packet")
        for e in errors:
            print(f"- {e}")
        return 1
    print("VALID media packet")
    return 0


def inspect_command(args: argparse.Namespace) -> int:
    packet = json.loads(Path(args.path).read_text(encoding="utf-8"))
    coherence = score_media_coherence(packet)
    summary = {
        "project": packet.get("project"),
        "schema": packet.get("schema"),
        "seed": packet.get("seed"),
        "mode": packet.get("mode"),
        "prompt": packet.get("intent", {}).get("prompt"),
        "duration": packet.get("duration_seconds"),
        "audio_sections": len(packet.get("audio", {}).get("sections", [])),
        "visual_scenes": len(packet.get("visual", {}).get("scenes", [])),
        "sync_events": len(packet.get("sync", {}).get("events", [])),
        "coherence_overall": coherence.get("overall"),
        "coherence_passed": coherence.get("passed"),
        "packet_hash": packet.get("receipt", {}).get("packet_hash"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def adapters_command(args: argparse.Namespace) -> int:
    print(json.dumps(list_adapters(), indent=2))
    return 0


def export_phiaudio_command(args: argparse.Namespace) -> int:
    packet = json.loads(Path(args.path).read_text(encoding="utf-8"))
    errors = validate_media_packet(packet)
    if errors:
        print("INVALID media packet")
        for e in errors:
            print(f"- {e}")
        return 1
    bundle = write_phiaudio_bundle(packet, args.out)
    print(f"PHIAudio bundle hash: {bundle['receipt']['bundle_hash']}")
    print(f"Output: {args.out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="waveforge-studio")
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("compile")
    c.add_argument("prompt")
    c.add_argument("--duration", type=int, default=72)
    c.add_argument("--seed", type=int, default=369369)
    c.add_argument("--mode", default="mythic-reel")
    c.add_argument("--out", required=True)
    c.add_argument("--export-phiaudio", action="store_true")
    c.set_defaults(func=compile_command)

    v = sub.add_parser("validate")
    v.add_argument("path")
    v.set_defaults(func=validate_command)

    i = sub.add_parser("inspect")
    i.add_argument("path")
    i.set_defaults(func=inspect_command)

    a = sub.add_parser("adapters")
    a.set_defaults(func=adapters_command)

    e = sub.add_parser("export-phiaudio")
    e.add_argument("path")
    e.add_argument("--out", required=True)
    e.set_defaults(func=export_phiaudio_command)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
