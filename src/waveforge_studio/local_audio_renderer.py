from __future__ import annotations

import json, math, struct, wave
from pathlib import Path

from .av_timeline import create_av_timeline
from .hashing import canonical_json, sha256_digest
from .validation import validate_media_packet
from .version import DEFAULT_RELEASE_TIMESTAMP


_DEF_SR = 48000


def _clip_i16(v: float) -> int:
    return max(-32768, min(32767, int(round(v))))


def _write_wav(path: Path, samples: list[int], sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack("<" + "h" * len(samples), *samples))


def create_audio_render_manifest(packet: dict, max_duration_seconds: int = 12, sample_rate: int = _DEF_SR) -> dict:
    timeline = create_av_timeline(packet)
    requested = int(packet.get("duration_seconds", 0) or 0)
    rendered = max(1, min(requested if requested > 0 else max_duration_seconds, int(max_duration_seconds)))
    manifest = {
        "schema": "waveforge.local_audio_render_manifest.v1_alpha",
        "project": "WaveForgeStudio",
        "version": "1.1-alpha",
        "source_packet_hash": packet.get("receipt", {}).get("packet_hash", sha256_digest(packet)),
        "seed": int(packet.get("seed", 0) or 0),
        "mode": packet.get("mode", "mythic-reel"),
        "requested_duration_seconds": requested,
        "rendered_duration_seconds": rendered,
        "sample_rate": int(sample_rate),
        "channels": 1,
        "sample_width_bytes": 2,
        "render_policy": {
            "local_only": True,
            "stdlib_only": True,
            "external_calls_allowed": False,
            "subprocess_allowed": False,
            "network_allowed": False,
            "generative_audio": False,
            "placeholder_audio": True,
        },
        "outputs": {
            "mix": "render/audio_mix.wav",
            "stems": [
                "render/stems/stem_click.wav",
                "render/stems/stem_tone.wav",
                "render/stems/stem_voice_placeholder.wav",
            ],
        },
        "timeline_reference": {"schema": "waveforge.av_timeline.v0", "timeline_hash": timeline["receipt"]["timeline_hash"]},
    }
    manifest["receipt"] = {
        "schema": "waveforge.local_audio_render_receipt.v1_alpha",
        "audio_render_hash": sha256_digest(json.loads(canonical_json(manifest))),
        "source_packet_hash": manifest["source_packet_hash"],
        "created_at": DEFAULT_RELEASE_TIMESTAMP,
    }
    return manifest


def read_wav_info(path: str | Path) -> dict:
    with wave.open(str(path), "rb") as wf:
        frames = wf.getnframes()
        sr = wf.getframerate()
        return {"channels": wf.getnchannels(), "sample_rate": sr, "sample_width_bytes": wf.getsampwidth(), "frame_count": frames, "duration_seconds": frames / sr if sr else 0}


def render_audio_stub(packet: dict, out_dir: str | Path, max_duration_seconds: int = 12, sample_rate: int = _DEF_SR) -> dict:
    errs = validate_media_packet(packet)
    if errs:
        raise ValueError("Invalid media packet: " + "; ".join(errs))
    out = Path(out_dir)
    manifest = create_audio_render_manifest(packet, max_duration_seconds=max_duration_seconds, sample_rate=sample_rate)
    dur = manifest["rendered_duration_seconds"]
    sr = manifest["sample_rate"]
    total = dur * sr
    tempo = int(packet.get("audio", {}).get("tempo_bpm", 108) or 108)
    freq = 220 + (int(packet.get("seed", 0) or 0) % 441)

    click = [0] * total
    tone = [0] * total
    voice = [0] * total
    beat_step = max(1, int(sr * 60 / max(1, tempo)))
    click_len = max(1, int(sr * 0.01))
    for i in range(0, total, beat_step):
        for j in range(min(click_len, total - i)):
            click[i + j] = _clip_i16(3000 * (1 - j / click_len))
    for n in range(total):
        tone[n] = _clip_i16(1200 * math.sin(2 * math.pi * freq * (n / sr)))
    cues = packet.get("audio", {}).get("voiceover_cues", [])
    for cue in cues:
        start = int(min(dur, max(0.0, float(cue.get("timestamp", 0)))) * sr)
        for j in range(min(int(sr * 0.08), total - start)):
            voice[start + j] = _clip_i16(900 * math.sin(2 * math.pi * 440 * (j / sr)))
    mix = [_clip_i16(0.5 * click[i] + 0.8 * tone[i] + 0.8 * voice[i]) for i in range(total)]

    mix_p = out / "render" / "audio_mix.wav"
    click_p = out / "render" / "stems" / "stem_click.wav"
    tone_p = out / "render" / "stems" / "stem_tone.wav"
    voice_p = out / "render" / "stems" / "stem_voice_placeholder.wav"
    _write_wav(mix_p, mix, sr); _write_wav(click_p, click, sr); _write_wav(tone_p, tone, sr); _write_wav(voice_p, voice, sr)

    (out / "audio_render_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (out / "audio_render_receipt.json").write_text(json.dumps(manifest["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "AUDIO_RENDER_SUMMARY.md").write_text(f"# Audio Render Summary\n\n- rendered_duration_seconds: {dur}\n- sample_rate: {sr}\n- mix: {manifest['outputs']['mix']}\n- audio_render_hash: {manifest['receipt']['audio_render_hash']}\n", encoding="utf-8")
    return manifest


def validate_audio_render_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get("schema") != "waveforge.local_audio_render_manifest.v1_alpha": e.append("schema invalid")
    rp = manifest.get("render_policy", {})
    if rp.get("local_only") is not True: e.append("render_policy.local_only must be true")
    for k in ["external_calls_allowed", "subprocess_allowed", "network_allowed", "generative_audio"]:
        if rp.get(k) is not False: e.append(f"render_policy.{k} must be false")
    if rp.get("placeholder_audio") is not True: e.append("render_policy.placeholder_audio must be true")
    if not manifest.get("outputs", {}).get("mix"): e.append("outputs.mix required")
    if len(manifest.get("outputs", {}).get("stems", [])) < 3: e.append("at least 3 stems required")
    if not manifest.get("receipt", {}).get("audio_render_hash"): e.append("receipt.audio_render_hash required")
    return e


def assert_valid_audio_render_manifest(manifest: dict) -> None:
    e=validate_audio_render_manifest(manifest)
    if e: raise ValueError("Invalid audio render manifest: " + "; ".join(e))
