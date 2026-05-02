import json
import os
import subprocess
import sys
from pathlib import Path

from waveforge_studio.media_packet import create_media_packet
from waveforge_studio.render_queue import create_render_queue, validate_render_queue, write_render_queue


def test_queue_schema_count_and_hash_behavior():
    q1 = create_render_queue(create_media_packet("hello", seed=369369))
    q2 = create_render_queue(create_media_packet("hello", seed=369369))
    q3 = create_render_queue(create_media_packet("hello", seed=369370))
    assert q1["schema"] == "waveforge.render_queue.v0"
    assert q1["job_count"] == 9
    assert q1["receipt"]["queue_hash"] == q2["receipt"]["queue_hash"]
    assert q1["receipt"]["queue_hash"] != q3["receipt"]["queue_hash"]


def test_future_jobs_blocked_and_validation_cases():
    q = create_render_queue(create_media_packet("hello"))
    for j in q["jobs"]:
        if j["kind"] == "future_render":
            assert j["status"] == "blocked_plan_only"
    assert validate_render_queue(q) == []
    bad = json.loads(json.dumps(q))
    bad["jobs"][1]["id"] = bad["jobs"][0]["id"]
    assert any("unique" in e for e in validate_render_queue(bad))
    bad2 = json.loads(json.dumps(q))
    bad2["jobs"][0]["depends_on"] = ["missing_job"]
    assert any("unknown dependency" in e for e in validate_render_queue(bad2))


def test_write_and_cli_and_compile_queue(tmp_path: Path):
    p = create_media_packet("hello")
    write_render_queue(p, tmp_path)
    for fn in ["render_queue.json", "render_queue_receipt.json", "RENDER_QUEUE_SUMMARY.md"]:
        assert (tmp_path / fn).exists()

    env = os.environ.copy(); env["PYTHONPATH"] = "src"
    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")
    out = tmp_path / "cli"
    r = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "queue", str(fixture), "--out", str(out)], capture_output=True, text=True, env=env)
    assert r.returncode == 0
    qpath = out / "render_queue.json"
    assert qpath.exists()

    r2 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "queue-validate", str(qpath)], capture_output=True, text=True, env=env)
    assert r2.returncode == 0

    run = tmp_path / "run"
    r3 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "compile", "hello", "--out", str(run), "--queue"], capture_output=True, text=True, env=env)
    assert r3.returncode == 0
    assert (run / "render_queue.json").exists()

    run2 = tmp_path / "run2"
    r4 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "compile", "hello", "--out", str(run2), "--bundle", "--queue"], capture_output=True, text=True, env=env)
    assert r4.returncode == 0
    assert (run2 / "production_bundle.json").exists()
    assert (run2 / "render_queue.json").exists()
