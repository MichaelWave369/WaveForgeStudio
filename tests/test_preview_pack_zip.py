import json
import subprocess
import sys

from waveforge_studio.local_audio_renderer import render_audio_stub
from waveforge_studio.local_av_preview import render_av_preview
from waveforge_studio.local_visual_renderer import render_visual_stub
from waveforge_studio.media_packet import create_media_packet
from waveforge_studio.preview_pack import write_preview_pack
from waveforge_studio.preview_pack_zip import create_preview_pack_zip_manifest, read_preview_pack_zip_info, validate_preview_pack_zip_manifest, write_preview_pack_zip


def _mk_pack(tmp_path):
    p = create_media_packet("x")
    render_audio_stub(p, tmp_path); render_visual_stub(p, tmp_path); render_av_preview(p, tmp_path)
    return write_preview_pack(tmp_path)


def test_manifest_deterministic_and_validation(tmp_path):
    _mk_pack(tmp_path)
    m1 = create_preview_pack_zip_manifest(tmp_path / "preview_pack")
    m2 = create_preview_pack_zip_manifest(tmp_path / "preview_pack")
    assert m1["schema"] == "waveforge.preview_pack_zip_manifest.v1_alpha"
    assert m1["receipt"]["preview_pack_zip_hash"] == m2["receipt"]["preview_pack_zip_hash"]
    bad = dict(m1); bad["files"] = [f for f in m1["files"] if f["path"] != "index.html"]
    assert validate_preview_pack_zip_manifest(bad)
    bad2 = json.loads(json.dumps(m1)); bad2["zip_policy"]["external_calls_allowed"] = True
    assert validate_preview_pack_zip_manifest(bad2)


def test_write_info_and_deterministic_zip(tmp_path):
    _mk_pack(tmp_path / "a")
    m = write_preview_pack_zip(tmp_path / "a" / "preview_pack")
    pp = tmp_path / "a" / "preview_pack"
    for f in ["preview_pack.zip", "preview_pack_zip_manifest.json", "preview_pack_zip_receipt.json", "PREVIEW_PACK_ZIP_SUMMARY.md"]:
        assert (pp / f).exists()
    info = read_preview_pack_zip_info(pp / "preview_pack.zip")
    assert info["exists"] and info["contains_index"] and info["file_count"] > 0 and info["sha256"]

    _mk_pack(tmp_path / "b")
    m2 = write_preview_pack_zip(tmp_path / "b" / "preview_pack")
    assert m["receipt"]["zip_file_sha256"] == m2["receipt"]["zip_file_sha256"]


def test_cli_and_forge_smoke_flags(tmp_path):
    env = {"PYTHONPATH": "src"}
    out = tmp_path / "cli"
    subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "forge", "hello", "--out", str(out), "--render-audio-stub", "--render-visual-stub", "--av-preview", "--preview-pack"], check=True, env=env)
    assert subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "zip-preview-pack", str(out / "preview_pack")], capture_output=True, text=True, env=env).returncode == 0
    assert subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "preview-pack-zip-validate", str(out / "preview_pack/preview_pack_zip_manifest.json")], capture_output=True, text=True, env=env).returncode == 0

    f1 = tmp_path / "forge1"
    assert subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "forge", "hello", "--out", str(f1), "--preview-pack-zip"], capture_output=True, text=True, env=env).returncode == 0
    assert (f1 / "preview_pack/preview_pack.zip").exists()
    f2 = tmp_path / "forge2"
    assert subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "forge", "hello", "--out", str(f2), "--render-audio-stub", "--render-visual-stub", "--av-preview", "--preview-pack", "--preview-pack-zip"], capture_output=True, text=True, env=env).returncode == 0
    assert (f2 / "preview_pack/preview_pack.zip").exists()
    s1 = tmp_path / "smoke1"
    assert subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "smoke", "--out", str(s1), "--preview-pack-zip"], capture_output=True, text=True, env=env).returncode == 0
    s2 = tmp_path / "smoke2"
    assert subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "smoke", "--out", str(s2), "--render-audio-stub", "--render-visual-stub", "--av-preview", "--preview-pack", "--preview-pack-zip"], capture_output=True, text=True, env=env).returncode == 0
