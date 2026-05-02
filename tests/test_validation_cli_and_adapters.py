import json
import os
import subprocess
import sys
from pathlib import Path

from waveforge_studio.adapters.registry import list_adapters
from waveforge_studio.hashing import sha256_digest
from waveforge_studio.media_packet import create_media_packet
from waveforge_studio.validation import validate_media_packet


def test_validation_passes_default_packet():
    packet = create_media_packet("hello")
    assert validate_media_packet(packet) == []


def test_validation_fails_missing_schema():
    packet = create_media_packet("hello")
    packet.pop("schema")
    assert any("schema" in e for e in validate_media_packet(packet))


def test_fixture_hash_matches_generated_default():
    fixture = json.loads(Path("tests/fixtures/sovereign_signal.project.waveforge.json").read_text())
    generated = create_media_packet("The Sovereign Signal awakens across the infinite fractal wave.")
    assert sha256_digest(fixture) == sha256_digest(generated)


def test_cli_validate_and_inspect_and_compile_summary(tmp_path: Path):
    packet = create_media_packet("hello")
    p = tmp_path / "project.waveforge.json"
    p.write_text(json.dumps(packet), encoding="utf-8")

    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    val = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "validate", str(p)], capture_output=True, text=True, env=env)
    assert val.returncode == 0
    assert "VALID" in val.stdout

    ins = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "inspect", str(p)], capture_output=True, text=True, env=env)
    assert ins.returncode == 0
    for field in ["project", "schema", "seed", "mode", "prompt", "duration", "audio_sections", "visual_scenes", "sync_events", "coherence_overall", "coherence_passed", "packet_hash"]:
        assert field in ins.stdout

    outdir = tmp_path / "run"
    comp = subprocess.run([
        sys.executable, "-m", "waveforge_studio.cli", "compile", "hello", "--out", str(outdir)
    ], capture_output=True, text=True, env=env)
    assert comp.returncode == 0
    assert (outdir / "summary.md").exists()


def test_adapter_registry_lists_five_stubs():
    adapters = list_adapters()
    names = {a["name"] for a in adapters}
    assert names == {"phiaudio", "wavetalk", "waverider", "comfyui", "phios"}
