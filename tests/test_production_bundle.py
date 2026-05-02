import os
import subprocess
import sys
from pathlib import Path

from waveforge_studio.media_packet import create_media_packet
from waveforge_studio.production_bundle import create_production_bundle, write_production_bundle


def test_create_production_bundle_schema_and_hashes():
    p = create_media_packet("hello")
    b = create_production_bundle(p)
    assert b["schema"] == "waveforge.production_bundle.v0"
    for k in ["contents", "contracts", "coherence", "receipt"]:
        assert k in b
    assert b["contracts"]["phiaudio"]["bundle_hash"]
    assert b["contracts"]["waverider"]["bundle_hash"]
    assert b["contracts"]["wavetalk"]["bundle_hash"]


def test_production_bundle_determinism_and_seed_change():
    b1 = create_production_bundle(create_media_packet("hello", seed=369369))
    b2 = create_production_bundle(create_media_packet("hello", seed=369369))
    b3 = create_production_bundle(create_media_packet("hello", seed=369370))
    assert b1["receipt"]["bundle_hash"] == b2["receipt"]["bundle_hash"]
    assert b1["receipt"]["bundle_hash"] != b3["receipt"]["bundle_hash"]


def test_write_production_bundle_and_cli(tmp_path: Path):
    p = create_media_packet("hello")
    write_production_bundle(p, tmp_path)
    for fn in ["project.waveforge.json", "audio_graph.json", "visual_graph.json", "sync_lattice.json", "render_manifest.json", "receipt.json", "timeline_preview.html", "production_bundle.json", "PRODUCTION_SUMMARY.md"]:
        assert (tmp_path / fn).exists()
    assert (tmp_path / "phiaudio" / "phiaudio_bundle.json").exists()
    assert (tmp_path / "waverider" / "waverider_bundle.json").exists()
    assert (tmp_path / "wavetalk" / "wavetalk_bundle.json").exists()

    env = os.environ.copy(); env["PYTHONPATH"] = "src"
    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")
    out = tmp_path / "cli"
    r = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "bundle", str(fixture), "--out", str(out)], capture_output=True, text=True, env=env)
    assert r.returncode == 0
    assert (out / "production_bundle.json").exists()


def test_compile_bundle_flag(tmp_path: Path):
    env = os.environ.copy(); env["PYTHONPATH"] = "src"
    out = tmp_path / "run"
    r = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "compile", "hello", "--out", str(out), "--bundle"], capture_output=True, text=True, env=env)
    assert r.returncode == 0
    assert (out / "production_bundle.json").exists()
    assert (out / "timeline_preview.html").exists()
    assert (out / "phiaudio" / "phiaudio_bundle.json").exists()
    assert (out / "waverider" / "waverider_bundle.json").exists()
    assert (out / "wavetalk" / "wavetalk_bundle.json").exists()
