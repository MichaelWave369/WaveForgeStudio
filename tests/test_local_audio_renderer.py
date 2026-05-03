import json
import subprocess
import sys
from pathlib import Path

from waveforge_studio.local_audio_renderer import create_audio_render_manifest, render_audio_stub, read_wav_info, validate_audio_render_manifest
from waveforge_studio.media_packet import create_media_packet


def test_manifest_and_validation():
    p = create_media_packet("x", seed=369369)
    m1 = create_audio_render_manifest(p)
    m2 = create_audio_render_manifest(p)
    assert m1["schema"] == "waveforge.local_audio_render_manifest.v1_alpha"
    assert m1["receipt"]["audio_render_hash"] == m2["receipt"]["audio_render_hash"]
    p2 = create_media_packet("x", seed=1)
    m3 = create_audio_render_manifest(p2)
    assert m1["receipt"]["audio_render_hash"] != m3["receipt"]["audio_render_hash"]
    assert validate_audio_render_manifest(m1) == []
    bad = json.loads(json.dumps(m1))
    bad["render_policy"]["external_calls_allowed"] = True
    assert validate_audio_render_manifest(bad)


def test_render_outputs_and_wav_info(tmp_path):
    p = create_media_packet("x")
    m = render_audio_stub(p, tmp_path)
    files = [
        "render/audio_mix.wav",
        "render/stems/stem_click.wav",
        "render/stems/stem_tone.wav",
        "render/stems/stem_voice_placeholder.wav",
        "audio_render_manifest.json",
        "audio_render_receipt.json",
        "AUDIO_RENDER_SUMMARY.md",
    ]
    for f in files:
        assert (tmp_path / f).exists()
    for f in files[:4]:
        i = read_wav_info(tmp_path / f)
        assert i["channels"] == 1 and i["sample_rate"] == 48000 and i["sample_width_bytes"] == 2 and i["frame_count"] > 0
    m2 = render_audio_stub(p, tmp_path / "second")
    assert m["receipt"]["audio_render_hash"] == m2["receipt"]["audio_render_hash"]


def test_cli_and_forge_smoke_flags(tmp_path):
    env={"PYTHONPATH":"src"}
    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")
    out = tmp_path / "ra"
    r1 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "render-audio-stub", str(fixture), "--out", str(out)], capture_output=True, text=True, env=env)
    assert r1.returncode == 0
    r2 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "audio-render-validate", str(out / "audio_render_manifest.json")], capture_output=True, text=True, env=env)
    assert r2.returncode == 0
    f_out = tmp_path / "forge"
    r3 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "forge", "hello", "--out", str(f_out), "--render-audio-stub"], capture_output=True, text=True, env=env)
    assert r3.returncode == 0
    assert (f_out / "render" / "audio_mix.wav").exists()
    s_out = tmp_path / "smoke"
    r4 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "smoke", "--out", str(s_out), "--render-audio-stub"], capture_output=True, text=True, env=env)
    assert r4.returncode == 0
    assert (s_out / "render" / "audio_mix.wav").exists()
    assert json.loads(r4.stdout)["smoke_passed"] is True
