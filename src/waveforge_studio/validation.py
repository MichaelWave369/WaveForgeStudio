from __future__ import annotations


def validate_audio_graph(audio: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(audio, dict):
        return ["audio must be an object"]
    if not audio.get("sections"):
        errors.append("audio.sections is required")
    if not audio.get("stems"):
        errors.append("audio.stems is required")
    return errors


def validate_visual_graph(visual: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(visual, dict):
        return ["visual must be an object"]
    if not visual.get("scenes"):
        errors.append("visual.scenes is required")
    if not visual.get("shots"):
        errors.append("visual.shots is required")
    return errors


def validate_sync_lattice(sync: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(sync, dict):
        return ["sync must be an object"]
    events = sync.get("sync_events") or sync.get("events") or []
    if not events:
        errors.append("sync.events or sync.sync_events is required")
    elif len(events) != 9:
        errors.append("sync must include 9 events for 3/6/9 structure")
    return errors


def validate_media_packet(packet: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, dict):
        return ["packet must be an object"]

    required = ["schema", "project", "seed", "intent", "structure", "audio", "visual", "sync", "governance", "receipt"]
    for key in required:
        if key not in packet:
            errors.append(f"missing top-level key: {key}")

    if packet.get("schema") != "waveforge.media_packet.v0":
        errors.append("schema must equal waveforge.media_packet.v0")
    if packet.get("project") != "WaveForgeStudio":
        errors.append("project must equal WaveForgeStudio")
    if not isinstance(packet.get("seed"), int):
        errors.append("seed must be int")
    if "duration_seconds" in packet and packet["duration_seconds"] <= 0:
        errors.append("duration_seconds must be positive")

    structure = packet.get("structure", {})
    for k in ["phi", "lambda", "c_star", "omega_c", "fib_timing"]:
        if k not in structure:
            errors.append(f"structure.{k} is required")

    errors.extend(validate_audio_graph(packet.get("audio", {})))
    errors.extend(validate_visual_graph(packet.get("visual", {})))
    errors.extend(validate_sync_lattice(packet.get("sync", {})))

    governance = packet.get("governance", {})
    if "coherence_threshold" not in governance:
        errors.append("governance.coherence_threshold is required")

    receipt = packet.get("receipt", {})
    if "packet_hash" not in receipt:
        errors.append("receipt.packet_hash is required")
    if "content_hash" not in receipt:
        errors.append("receipt.content_hash is required")
    return errors


def assert_valid_media_packet(packet: dict) -> None:
    errors = validate_media_packet(packet)
    if errors:
        raise ValueError("Invalid media packet: " + "; ".join(errors))
