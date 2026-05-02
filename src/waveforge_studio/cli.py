from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters.phiaudio_bridge import write_phiaudio_bundle
from .adapters.registry import list_adapters
from .adapters.waverider_bridge import write_waverider_bundle
from .coherence import score_media_coherence
from .media_packet import create_media_packet
from .production_bundle import write_production_bundle
from .render_manifest import create_render_manifest
from .timeline_preview import write_timeline_preview
from .validation import validate_media_packet


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _load_valid(path: str) -> tuple[dict, list[str]]:
    packet = json.loads(Path(path).read_text(encoding="utf-8"))
    return packet, validate_media_packet(packet)


def compile_command(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    packet = create_media_packet(args.prompt, duration_seconds=args.duration, seed=args.seed, mode=args.mode)
    _write_json(out / "project.waveforge.json", packet)
    _write_json(out / "audio_graph.json", packet["audio"])
    _write_json(out / "visual_graph.json", packet["visual"])
    _write_json(out / "sync_lattice.json", packet["sync"])
    _write_json(out / "render_manifest.json", create_render_manifest(packet))
    _write_json(out / "receipt.json", packet["receipt"])
    (out / "summary.md").write_text(f"# WaveForgeStudio Run Summary\n\n- Coherence Overall: {score_media_coherence(packet)['overall']}\n", encoding="utf-8")
    if args.bundle:
        write_production_bundle(packet, out)
        return 0
    if args.export_phiaudio:
        write_phiaudio_bundle(packet, out / "phiaudio")
    if args.export_waverider:
        write_waverider_bundle(packet, out / "waverider")
    if args.preview:
        write_timeline_preview(packet, out)
    return 0


def validate_command(args: argparse.Namespace) -> int:
    _, errors = _load_valid(args.path)
    if errors:
        print("INVALID media packet")
        return 1
    print("VALID media packet")
    return 0


def inspect_command(args: argparse.Namespace) -> int:
    packet, _ = _load_valid(args.path)
    c = score_media_coherence(packet)
    print(json.dumps({"project": packet.get("project"), "schema": packet.get("schema"), "seed": packet.get("seed"), "mode": packet.get("mode"), "prompt": packet.get("intent", {}).get("prompt"), "duration": packet.get("duration_seconds"), "audio_sections": len(packet.get("audio", {}).get("sections", [])), "visual_scenes": len(packet.get("visual", {}).get("scenes", [])), "sync_events": len(packet.get("sync", {}).get("events", [])), "coherence_overall": c.get("overall"), "coherence_passed": c.get("passed"), "packet_hash": packet.get("receipt", {}).get("packet_hash")}, indent=2, sort_keys=True))
    return 0


def adapters_command(args: argparse.Namespace) -> int:
    print(json.dumps(list_adapters(), indent=2))
    return 0


def export_phiaudio_command(args: argparse.Namespace) -> int:
    packet, errors = _load_valid(args.path)
    if errors:
        print("INVALID media packet")
        return 1
    b = write_phiaudio_bundle(packet, args.out)
    print(f"PHIAudio bundle hash: {b['receipt']['bundle_hash']}")
    return 0


def export_waverider_command(args: argparse.Namespace) -> int:
    packet, errors = _load_valid(args.path)
    if errors:
        print("INVALID media packet")
        return 1
    b = write_waverider_bundle(packet, args.out)
    print(f"WaveRider bundle hash: {b['receipt']['bundle_hash']}")
    return 0


def preview_command(args: argparse.Namespace) -> int:
    packet, errors = _load_valid(args.path)
    if errors:
        print("INVALID media packet")
        return 1
    print(f"Timeline preview: {write_timeline_preview(packet, args.out)}")
    return 0


def bundle_command(args: argparse.Namespace) -> int:
    packet, errors = _load_valid(args.path)
    if errors:
        print("INVALID media packet")
        return 1
    b = write_production_bundle(packet, args.out)
    print(f"Production bundle hash: {b['receipt']['bundle_hash']}")
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
    c.add_argument("--export-waverider", action="store_true")
    c.add_argument("--preview", action="store_true")
    c.add_argument("--bundle", action="store_true")
    c.set_defaults(func=compile_command)
    for name, fn, out in [("validate", validate_command, False), ("inspect", inspect_command, False), ("export-phiaudio", export_phiaudio_command, True), ("export-waverider", export_waverider_command, True), ("preview", preview_command, True), ("bundle", bundle_command, True)]:
        p = sub.add_parser(name)
        p.add_argument("path")
        if out:
            p.add_argument("--out", required=True)
        p.set_defaults(func=fn)
    a = sub.add_parser("adapters")
    a.set_defaults(func=adapters_command)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
