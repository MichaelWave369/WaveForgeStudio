import os
import subprocess
import sys
from pathlib import Path

from waveforge_studio.media_packet import create_media_packet
from waveforge_studio.timeline_preview import create_timeline_preview_html, write_timeline_preview


def test_preview_html_contains_core_fields():
    p = create_media_packet("hello")
    h = create_timeline_preview_html(p)
    assert "WaveForgeStudio Timeline Preview" in h
    assert str(p["seed"]) in h
    assert "hello" in h
    assert "9 Sync Events" in h


def test_preview_html_deterministic():
    p = create_media_packet("hello")
    assert create_timeline_preview_html(p) == create_timeline_preview_html(p)


def test_write_preview(tmp_path: Path):
    p = create_media_packet("hello")
    out = write_timeline_preview(p, tmp_path)
    assert out.exists()
    assert out.name == "timeline_preview.html"


def test_cli_preview_and_compile_flags(tmp_path: Path):
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")

    out = tmp_path / "preview"
    r = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "preview", str(fixture), "--out", str(out)], capture_output=True, text=True, env=env)
    assert r.returncode == 0
    assert (out / "timeline_preview.html").exists()

    run1 = tmp_path / "run1"
    r2 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "compile", "hello", "--out", str(run1), "--preview"], capture_output=True, text=True, env=env)
    assert r2.returncode == 0
    assert (run1 / "timeline_preview.html").exists()

    run2 = tmp_path / "run2"
    r3 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "compile", "hello", "--out", str(run2), "--preview", "--export-phiaudio"], capture_output=True, text=True, env=env)
    assert r3.returncode == 0
    assert (run2 / "timeline_preview.html").exists()
    assert (run2 / "phiaudio" / "phiaudio_bundle.json").exists()
