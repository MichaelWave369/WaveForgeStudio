import json
import subprocess
import sys
from pathlib import Path

from waveforge_studio.media_packet import create_media_packet
from waveforge_studio.local_audio_renderer import render_audio_stub
from waveforge_studio.local_visual_renderer import render_visual_stub
from waveforge_studio.local_av_preview import render_av_preview
from waveforge_studio.preview_pack import create_preview_pack_manifest, write_preview_pack, read_preview_pack_info, validate_preview_pack_manifest


def test_manifest_and_validation(tmp_path):
    m = create_preview_pack_manifest(tmp_path)
    assert m["schema"] == "waveforge.preview_pack_manifest.v1_alpha"
    assert "render/av_preview.html" in m["missing"]
    assert validate_preview_pack_manifest(m)
    p = create_media_packet("x")
    render_audio_stub(p, tmp_path); render_visual_stub(p, tmp_path); render_av_preview(p, tmp_path)
    m2 = create_preview_pack_manifest(tmp_path)
    m3 = create_preview_pack_manifest(tmp_path)
    assert m2["receipt"]["preview_pack_hash"] == m3["receipt"]["preview_pack_hash"]


def test_write_and_cli(tmp_path):
    p = create_media_packet("x")
    render_audio_stub(p, tmp_path); render_visual_stub(p, tmp_path); render_av_preview(p, tmp_path)
    m = write_preview_pack(tmp_path)
    pp = tmp_path / "preview_pack"
    for f in ["index.html","preview_pack_manifest.json","preview_pack_receipt.json","PREVIEW_PACK_SUMMARY.md","media/audio_mix.wav","media/storyboard/frame_001.svg","manifests/av_preview_manifest.json","receipts/av_preview_receipt.json"]:
        assert (pp / f).exists()
    info = read_preview_pack_info(pp)
    assert info["index_exists"] and info["storyboard_frame_count"] >= 1

    env={"PYTHONPATH":"src"}
    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")
    out = tmp_path / "cli"
    subprocess.run([sys.executable,"-m","waveforge_studio.cli","forge","hello","--out",str(out),"--render-audio-stub","--render-visual-stub","--av-preview"],check=True,env=env)
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","pack-preview",str(out),"--out",str(out/"preview_pack")],capture_output=True,text=True,env=env).returncode == 0
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","preview-pack-validate",str(out/"preview_pack/preview_pack_manifest.json")],capture_output=True,text=True,env=env).returncode == 0
    f1 = tmp_path / "forge1"
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","forge","hello","--out",str(f1),"--preview-pack"],capture_output=True,text=True,env=env).returncode == 0
    assert (f1/"preview_pack/index.html").exists()
    f2 = tmp_path / "forge2"
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","forge","hello","--out",str(f2),"--render-audio-stub","--render-visual-stub","--av-preview","--preview-pack"],capture_output=True,text=True,env=env).returncode == 0
    assert (f2/"preview_pack/media/audio_mix.wav").exists()
    s1 = tmp_path / "smoke1"
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","smoke","--out",str(s1),"--preview-pack"],capture_output=True,text=True,env=env).returncode == 0
    s2 = tmp_path / "smoke2"
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","smoke","--out",str(s2),"--render-audio-stub","--render-visual-stub","--av-preview","--preview-pack"],capture_output=True,text=True,env=env).returncode == 0
