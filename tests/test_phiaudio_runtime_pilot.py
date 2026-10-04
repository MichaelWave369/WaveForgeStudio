from __future__ import annotations

import json
from pathlib import Path

import pytest

from waveforge_studio.adapters.phiaudio_bridge import create_phiaudio_bundle
from waveforge_studio.adapters.phiaudio_runtime import (
    PHIAudioRuntimeAdapter,
    PHIAudioRuntimeError,
)
from waveforge_studio.artifact_ledger import file_sha256
from waveforge_studio.media_packet import create_media_packet


def _write_bundle(root: Path) -> Path:
    packet = create_media_packet(
        "PHIAudio runtime pilot",
        duration_seconds=6,
        seed=369,
        mode="test",
    )
    bundle = create_phiaudio_bundle(packet)
    path = root / "phiaudio" / "phiaudio_bundle.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _fake_runtime(path: Path, *, wrong_hash: bool = False) -> None:
    hash_expr = '"0"*64' if wrong_hash else "master_sha"
    source = f"""#!/usr/bin/env python3
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
out=Path(a.out); stems=out/'stems'
stems.mkdir(parents=True,exist_ok=True)
master=out/'master.wav'; stem=stems/'stem_bass.wav'
master.write_bytes(b'RIFF'+b'\\x00'*60)
stem.write_bytes(b'RIFF'+b'\\x01'*60)

master_sha=sha(master)
stem_sha=sha(stem)
manifest={{
    'schemaVersion':'phiaudio.waveforge-render.v0.1',
    'sourceSchema':'waveforge.phiaudio_bundle.v0',
    'sourcePacketHash':bundle['source_packet_hash'],
    'sourceBundleHash':bundle['receipt']['bundle_hash'],
    'sampleRate':int(a.sample_rate),
    'stemCount':1,
    'master':{{'id':'master','sha256':master_sha,'sizeBytes':master.stat().st_size,'mediaType':'audio/wav'}},
    'stems':[{{'id':'stem_bass','sha256':stem_sha,'sizeBytes':stem.stat().st_size,'mediaType':'audio/wav'}}],
    'masterPeakBeforeLimit':0.5,
    'masterLimiterGain':1,
    'warnings':[],
    'operatorEnabled':True,
    'networkUsed':False,
}}
(out/'phiaudio_render_manifest.json').write_text(json.dumps(manifest,indent=2))
receipt={{
    'schemaVersion':'phiaudio.waveforge-cli-receipt.v0.1',
    'sourceBundleHash':bundle['receipt']['bundle_hash'],
    'renderManifestDigest':digest(manifest),
    'outputRoot':a.out,
    'files':[
        {{'id':'master','path':str(master).replace('\\\\','/'),'sha256':{hash_expr},'sizeBytes':master.stat().st_size}},
        {{'id':'stem_bass','path':str(stem).replace('\\\\','/'),'sha256':stem_sha,'sizeBytes':stem.stat().st_size}},
    ],
}}
receipt['receiptDigest']=digest(receipt)
(out/'phiaudio_render_receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({{'status':'rendered'}}))
"""
    path.write_text(source, encoding="utf-8")
    path.chmod(path.stat().st_mode | 0o111)


def test_runtime_is_optional_when_binary_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PATH", "")
    adapter = PHIAudioRuntimeAdapter("definitely-not-phiaudio")
    assert adapter.available() is False
    assert adapter.describe()["default_enabled"] is False


def test_operator_enablement_is_required(tmp_path: Path) -> None:
    runtime = tmp_path / "phiaudio-render"
    _fake_runtime(runtime)
    _write_bundle(tmp_path)
    adapter = PHIAudioRuntimeAdapter(str(runtime))

    with pytest.raises(PHIAudioRuntimeError, match="operator enablement"):
        adapter.render_bundle(run_root=tmp_path)


def test_runtime_pilot_executes_and_independently_verifies_artifacts(
    tmp_path: Path,
) -> None:
    runtime = tmp_path / "phiaudio-render"
    _fake_runtime(runtime)
    _write_bundle(tmp_path)

    adapter = PHIAudioRuntimeAdapter(str(runtime))
    result = adapter.render_bundle(
        run_root=tmp_path,
        operator_enabled=True,
        sample_rate=48_000,
    )

    assert result.status == "verified"
    assert len(result.source_bundle_hash) == 64
    assert len(result.manifest_hash) == 64
    assert len(result.receipt_hash) == 64
    assert result.master_sha256 == file_sha256(
        tmp_path / "render" / "phiaudio" / "master.wav"
    )
    assert result.stem_count == 1
    assert result.warnings == ()


def test_runtime_rejects_artifact_hash_mismatch(tmp_path: Path) -> None:
    runtime = tmp_path / "phiaudio-render"
    _fake_runtime(runtime, wrong_hash=True)
    _write_bundle(tmp_path)
    adapter = PHIAudioRuntimeAdapter(str(runtime))

    with pytest.raises(PHIAudioRuntimeError, match="artifact hash mismatch"):
        adapter.render_bundle(run_root=tmp_path, operator_enabled=True)


def test_runtime_rejects_output_escape(tmp_path: Path) -> None:
    runtime = tmp_path / "phiaudio-render"
    _fake_runtime(runtime)
    _write_bundle(tmp_path)
    adapter = PHIAudioRuntimeAdapter(str(runtime))

    with pytest.raises(PHIAudioRuntimeError, match="inside the WaveForge run root"):
        adapter.render_bundle(
            run_root=tmp_path,
            output_dir="../escape",
            operator_enabled=True,
        )
