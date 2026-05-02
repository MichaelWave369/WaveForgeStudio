import os
import subprocess
import sys
from pathlib import Path

from waveforge_studio.adapters.waverider_bridge import create_waverider_bundle, write_waverider_bundle
from waveforge_studio.media_packet import create_media_packet


def test_create_waverider_bundle_schema_and_shape():
    p = create_media_packet("hello")
    b = create_waverider_bundle(p)
    assert b["schema"] == "waveforge.waverider_bundle.v0"
    for k in ["world", "scene_graph", "shot_graph", "symbol_graph", "motion_graph", "sync_reference", "audio_reference", "receipt"]:
        assert k in b
    assert b["scene_graph"]["scene_count"] == 6
    assert b["shot_graph"]["shot_count"] == 9


def test_waverider_hash_determinism_and_seed_change():
    b1 = create_waverider_bundle(create_media_packet("hello", seed=369369))
    b2 = create_waverider_bundle(create_media_packet("hello", seed=369369))
    b3 = create_waverider_bundle(create_media_packet("hello", seed=369370))
    assert b1["receipt"]["bundle_hash"] == b2["receipt"]["bundle_hash"]
    assert b1["receipt"]["bundle_hash"] != b3["receipt"]["bundle_hash"]


def test_write_and_cli_exports(tmp_path: Path):
    p = create_media_packet("hello")
    write_waverider_bundle(p, tmp_path)
    for fn in ["waverider_bundle.json", "waverider_world.json", "waverider_scene_graph.json", "waverider_shot_graph.json", "waverider_symbol_graph.json", "waverider_motion_graph.json", "waverider_receipt.json", "WAVERIDER_BRIDGE_SUMMARY.md"]:
        assert (tmp_path / fn).exists()

    env = os.environ.copy(); env["PYTHONPATH"] = "src"
    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")
    out = tmp_path / "cli"
    r = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "export-waverider", str(fixture), "--out", str(out)], capture_output=True, text=True, env=env)
    assert r.returncode == 0
    assert (out / "waverider_bundle.json").exists()


def test_compile_with_waverider_and_all_flags(tmp_path: Path):
    env = os.environ.copy(); env["PYTHONPATH"] = "src"
    run1 = tmp_path / "run1"
    r1 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "compile", "hello", "--out", str(run1), "--export-waverider"], capture_output=True, text=True, env=env)
    assert r1.returncode == 0
    assert (run1 / "waverider" / "waverider_bundle.json").exists()

    run2 = tmp_path / "run2"
    r2 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "compile", "hello", "--out", str(run2), "--preview", "--export-phiaudio", "--export-waverider"], capture_output=True, text=True, env=env)
    assert r2.returncode == 0
    assert (run2 / "timeline_preview.html").exists()
    assert (run2 / "phiaudio" / "phiaudio_bundle.json").exists()
    assert (run2 / "waverider" / "waverider_bundle.json").exists()
