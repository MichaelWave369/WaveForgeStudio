import json
import os
import subprocess
import sys
from pathlib import Path

from waveforge_studio.adapters.phiaudio_bridge import create_phiaudio_bundle, write_phiaudio_bundle
from waveforge_studio.media_packet import create_media_packet


def test_create_phiaudio_bundle_schema():
    p = create_media_packet("hello")
    b = create_phiaudio_bundle(p)
    assert b["schema"] == "waveforge.phiaudio_bundle.v0"


def test_bundle_hash_deterministic_and_seed_sensitive():
    p1 = create_media_packet("hello", seed=369369)
    p2 = create_media_packet("hello", seed=369369)
    p3 = create_media_packet("hello", seed=369370)
    b1 = create_phiaudio_bundle(p1)
    b2 = create_phiaudio_bundle(p2)
    b3 = create_phiaudio_bundle(p3)
    assert b1["receipt"]["bundle_hash"] == b2["receipt"]["bundle_hash"]
    assert b1["receipt"]["bundle_hash"] != b3["receipt"]["bundle_hash"]


def test_bundle_shape_and_write(tmp_path: Path):
    p = create_media_packet("hello")
    b = write_phiaudio_bundle(p, tmp_path)
    for k in ["composition", "stems", "sync", "visual_reference", "receipt"]:
        assert k in b
    for fn in [
        "phiaudio_bundle.json",
        "phiaudio_composition.json",
        "phiaudio_stems.json",
        "phiaudio_sync.json",
        "phiaudio_receipt.json",
        "PHIAUDIO_BRIDGE_SUMMARY.md",
    ]:
        assert (tmp_path / fn).exists()


def test_cli_export_and_compile_export(tmp_path: Path):
    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    out = tmp_path / "phiaudio"
    r = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "export-phiaudio", str(fixture), "--out", str(out)], capture_output=True, text=True, env=env)
    assert r.returncode == 0
    assert (out / "phiaudio_bundle.json").exists()

    run_out = tmp_path / "run"
    r2 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "compile", "hello", "--out", str(run_out), "--export-phiaudio"], capture_output=True, text=True, env=env)
    assert r2.returncode == 0
    assert (run_out / "phiaudio" / "phiaudio_bundle.json").exists()
