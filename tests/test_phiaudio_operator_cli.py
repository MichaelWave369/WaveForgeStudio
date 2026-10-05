from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from waveforge_studio.adapters.phiaudio_bridge import create_phiaudio_bundle
from waveforge_studio.media_packet import create_media_packet


def _write_bundle(root: Path) -> None:
    packet = create_media_packet(
        "WaveForge PHIAudio operator CLI",
        duration_seconds=6,
        seed=369,
        mode="test",
    )
    bundle = create_phiaudio_bundle(packet)
    path = root / "phiaudio" / "phiaudio_bundle.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")


def _fake_runtime(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def digest(value):
    payload=json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

p=argparse.ArgumentParser()
p.add_argument('--bundle',required=True)
p.add_argument('--out',required=True)
p.add_argument('--enable-phiaudio',action='store_true')
p.add_argument('--sample-rate',required=True)
a=p.parse_args()
if not a.enable_phiaudio:
    raise SystemExit(9)

bundle=json.loads(Path(a.bundle).read_text())
out=Path(a.out)
stems=out/'stems'
stems.mkdir(parents=True,exist_ok=True)
master=out/'master.wav'
stem=stems/'stem_cli.wav'
master.write_bytes(b'RIFF'+b'\\x00'*60)
stem.write_bytes(b'RIFF'+b'\\x01'*60)
master_sha=sha(master)
stem_sha=sha(stem)

manifest={
  'schemaVersion':'phiaudio.waveforge-render.v0.1',
  'sourceSchema':'waveforge.phiaudio_bundle.v0',
  'sourcePacketHash':bundle['source_packet_hash'],
  'sourceBundleHash':bundle['receipt']['bundle_hash'],
  'sampleRate':int(a.sample_rate),
  'stemCount':1,
  'master':{'id':'master','sha256':master_sha,'sizeBytes':master.stat().st_size,'mediaType':'audio/wav'},
  'stems':[{'id':'stem_cli','sha256':stem_sha,'sizeBytes':stem.stat().st_size,'mediaType':'audio/wav'}],
  'masterPeakBeforeLimit':0.5,
  'masterLimiterGain':1,
  'warnings':[],
  'operatorEnabled':True,
  'networkUsed':False,
}
(out/'phiaudio_render_manifest.json').write_text(json.dumps(manifest,indent=2))
receipt={
  'schemaVersion':'phiaudio.waveforge-cli-receipt.v0.1',
  'sourceBundleHash':bundle['receipt']['bundle_hash'],
  'renderManifestDigest':digest(manifest),
  'outputRoot':a.out,
  'files':[
    {'id':'master','path':str(master).replace('\\\\','/'),'sha256':master_sha,'sizeBytes':master.stat().st_size},
    {'id':'stem_cli','path':str(stem).replace('\\\\','/'),'sha256':stem_sha,'sizeBytes':stem.stat().st_size},
  ],
}
receipt['receiptDigest']=digest(receipt)
(out/'phiaudio_render_receipt.json').write_text(json.dumps(receipt,indent=2))
""",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | 0o111)


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    return subprocess.run(
        [sys.executable, "-m", "waveforge_studio.cli", *args],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_status_reports_missing_runtime_without_failure(tmp_path: Path) -> None:
    result = _run(
        "phiaudio-runtime-status",
        "--runtime-command",
        "definitely-not-installed-phiaudio",
        cwd=tmp_path,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["available"] is False
    assert payload["default_enabled"] is False
    assert payload["requires_operator_enablement"] is True


def test_render_cli_fails_closed_without_operator_enablement(tmp_path: Path) -> None:
    runtime = tmp_path / "phiaudio-render"
    _fake_runtime(runtime)
    _write_bundle(tmp_path)

    result = _run(
        "render-phiaudio",
        ".",
        "--runtime-command",
        str(runtime),
        cwd=tmp_path,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert "operator enablement" in payload["error"]


def test_render_cli_runs_and_returns_verified_receipt_summary(tmp_path: Path) -> None:
    runtime = tmp_path / "phiaudio-render"
    _fake_runtime(runtime)
    _write_bundle(tmp_path)

    result = _run(
        "render-phiaudio",
        ".",
        "--runtime-command",
        str(runtime),
        "--enable-phiaudio",
        "--sample-rate",
        "48000",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "verified"
    assert payload["stem_count"] == 1
    assert len(payload["source_bundle_hash"]) == 64
    assert len(payload["manifest_hash"]) == 64
    assert len(payload["receipt_hash"]) == 64
    assert len(payload["master_sha256"]) == 64
    assert payload["warnings"] == []
    assert (tmp_path / "render" / "phiaudio" / "master.wav").is_file()


def test_render_cli_rejects_output_escape_before_runtime_execution(tmp_path: Path) -> None:
    runtime = tmp_path / "phiaudio-render"
    _fake_runtime(runtime)
    _write_bundle(tmp_path)

    result = _run(
        "render-phiaudio",
        ".",
        "--runtime-command",
        str(runtime),
        "--enable-phiaudio",
        "--out",
        "../escape",
        cwd=tmp_path,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "inside the WaveForge run root" in payload["error"]
