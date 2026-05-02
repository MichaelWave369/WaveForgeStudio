import os
import subprocess
import sys
from pathlib import Path

from waveforge_studio.media_packet import create_media_packet
from waveforge_studio.queue_runner import run_queue_safe, write_queue_execution


def test_run_queue_safe_shape_and_counts(tmp_path: Path):
    p = create_media_packet("hello")
    r = run_queue_safe(p, tmp_path)
    assert r["schema"] == "waveforge.safe_queue_execution.v0"
    assert r["completed_count"] == 6
    assert r["blocked_count"] == 3
    assert r["failed_count"] == 0
    for j in r["jobs"]:
        if j["id"] in {"job_006_future_audio_render", "job_007_future_video_render", "job_008_future_final_mux"}:
            assert j["status"] == "blocked_plan_only" and j["executed"] is False


def test_execution_deterministic_and_write(tmp_path: Path):
    p = create_media_packet("hello")
    r1 = write_queue_execution(p, tmp_path / "a")
    r2 = write_queue_execution(p, tmp_path / "b")
    assert r1["receipt"]["execution_hash"] == r2["receipt"]["execution_hash"]
    assert (tmp_path / "a" / "execution_report.json").exists()
    assert (tmp_path / "a" / "execution_receipt.json").exists()
    assert (tmp_path / "a" / "artifact_ledger.json").exists()
    assert (tmp_path / "a" / "av_timeline.json").exists()


def test_cli_run_queue_ledger_and_compile_flags(tmp_path: Path):
    env = os.environ.copy(); env["PYTHONPATH"] = "src"
    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")
    out = tmp_path / "run"
    r = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "run-queue", str(fixture), "--out", str(out)], capture_output=True, text=True, env=env)
    assert r.returncode == 0
    assert (out / "execution_report.json").exists()
    r2 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "ledger", str(out)], capture_output=True, text=True, env=env)
    assert r2.returncode == 0

    c1 = tmp_path / "c1"
    rc1 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "compile", "hello", "--out", str(c1), "--run-queue"], capture_output=True, text=True, env=env)
    assert rc1.returncode == 0
    assert (c1 / "execution_report.json").exists() and (c1 / "artifact_ledger.json").exists()

    c2 = tmp_path / "c2"
    rc2 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "compile", "hello", "--out", str(c2), "--bundle", "--queue", "--run-queue"], capture_output=True, text=True, env=env)
    assert rc2.returncode == 0
    for fn in ["production_bundle.json", "render_queue.json", "execution_report.json", "artifact_ledger.json"]:
        assert (c2 / fn).exists()
    assert (c2 / "wavetalk" / "wavetalk_bundle.json").exists()
    assert (c2 / "phiaudio" / "phiaudio_bundle.json").exists()
    assert (c2 / "waverider" / "waverider_bundle.json").exists()
