from __future__ import annotations

import argparse
import json
from pathlib import Path

from .media_packet import create_media_packet
from .render_manifest import create_render_manifest


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
    c.set_defaults(func=compile_command)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
