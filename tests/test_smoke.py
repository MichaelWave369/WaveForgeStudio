import json
import subprocess
import sys

from waveforge_studio.alpha_artifacts import REQUIRED_ALPHA_ARTIFACTS
from waveforge_studio.smoke import run_golden_demo_smoke, write_golden_demo_smoke


def test_run_golden_demo_smoke(tmp_path):
    out = tmp_path / "smoke"
    rep = run_golden_demo_smoke(out)
    assert rep["schema"] == "waveforge.smoke_report.v1_alpha"
    assert rep["smoke_passed"] is True
    assert rep["alpha_ready"] is True
    assert rep["missing_artifacts"] == []
    assert sorted(rep["required_artifacts"]) == sorted(REQUIRED_ALPHA_ARTIFACTS)


def test_smoke_hash_deterministic(tmp_path):
    a = run_golden_demo_smoke(tmp_path / "a")
    b = run_golden_demo_smoke(tmp_path / "b")
    assert a["receipt"]["smoke_hash"] == b["receipt"]["smoke_hash"]


def test_write_golden_demo_smoke(tmp_path):
    out = tmp_path / "smoke"
    write_golden_demo_smoke(out)
    assert (out / "smoke_report.json").exists()
    assert (out / "smoke_report_receipt.json").exists()
    assert (out / "SMOKE_SUMMARY.md").exists()


def test_cli_smoke_and_doctor(tmp_path):
    env = {"PYTHONPATH": "src"}
    out = tmp_path / "cli-smoke"
    r1 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "doctor"], capture_output=True, text=True, env=env)
    assert r1.returncode == 0
    assert "renderer_status" in r1.stdout
    r2 = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "smoke", "--out", str(out)], capture_output=True, text=True, env=env)
    assert r2.returncode == 0
    payload = json.loads(r2.stdout)
    assert payload["smoke_passed"] is True
