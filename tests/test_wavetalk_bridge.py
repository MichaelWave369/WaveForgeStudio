import os
import subprocess
import sys
from pathlib import Path

from waveforge_studio.adapters.wavetalk_bridge import create_wavetalk_bundle, write_wavetalk_bundle
from waveforge_studio.media_packet import create_media_packet


def test_wavetalk_schema_and_shape():
    b = create_wavetalk_bundle(create_media_packet("hello"))
    assert b["schema"] == "waveforge.wavetalk_bundle.v0"
    for k in ["signal", "routing", "governance", "memory", "replay", "receipts"]:
        assert k in b
    assert "coherence_threshold" in b["governance"]
    assert "coherence_passed" in b["governance"]
    assert b["memory"]["source_packet_hash"]


def test_wavetalk_hash_determinism_and_seed_change():
    b1 = create_wavetalk_bundle(create_media_packet("hello", seed=369369))
    b2 = create_wavetalk_bundle(create_media_packet("hello", seed=369369))
    b3 = create_wavetalk_bundle(create_media_packet("hello", seed=369370))
    assert b1["receipts"]["signal_receipt"]["bundle_hash"] == b2["receipts"]["signal_receipt"]["bundle_hash"]
    assert b1["receipts"]["signal_receipt"]["bundle_hash"] != b3["receipts"]["signal_receipt"]["bundle_hash"]


def test_write_and_cli_and_compile(tmp_path: Path):
    p = create_media_packet("hello")
    write_wavetalk_bundle(p, tmp_path)
    for fn in ["wavetalk_bundle.json", "wavetalk_signal.json", "wavetalk_routing.json", "wavetalk_governance.json", "wavetalk_memory.json", "wavetalk_replay.json", "wavetalk_receipt.json", "WAVETALK_BRIDGE_SUMMARY.md"]:
        assert (tmp_path / fn).exists()

    env = os.environ.copy(); env["PYTHONPATH"] = "src"
    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")
    out = tmp_path / "cli"
    r = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "export-wavetalk", str(fixture), "--out", str(out)], capture_output=True, text=True, env=env)
    assert r.returncode == 0
    assert (out / "wavetalk_bundle.json").exists()

    run = tmp_path / "run"
    r2 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "compile", "hello", "--out", str(run), "--export-wavetalk", "--export-phiaudio", "--export-waverider", "--preview"], capture_output=True, text=True, env=env)
    assert r2.returncode == 0
    assert (run / "wavetalk" / "wavetalk_bundle.json").exists()
    assert (run / "phiaudio" / "phiaudio_bundle.json").exists()
    assert (run / "waverider" / "waverider_bundle.json").exists()
    assert (run / "timeline_preview.html").exists()
