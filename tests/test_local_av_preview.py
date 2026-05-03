import json
import subprocess
import sys
from pathlib import Path

from waveforge_studio.local_av_preview import create_av_preview_manifest, render_av_preview, read_preview_info, validate_av_preview_manifest
from waveforge_studio.local_audio_renderer import render_audio_stub
from waveforge_studio.local_visual_renderer import render_visual_stub
from waveforge_studio.media_packet import create_media_packet


def test_manifest_and_validation(tmp_path):
    p = create_media_packet("x", seed=369369)
    m1 = create_av_preview_manifest(p, tmp_path)
    m2 = create_av_preview_manifest(p, tmp_path)
    assert m1["schema"] == "waveforge.local_av_preview_manifest.v1_alpha"
    assert m1["receipt"]["av_preview_hash"] == m2["receipt"]["av_preview_hash"]
    assert m1["assets"]["audio_mix"]["present"] is False
    render_audio_stub(p, tmp_path); render_visual_stub(p, tmp_path)
    m3 = create_av_preview_manifest(p, tmp_path)
    assert m3["assets"]["audio_mix"]["present"] is True
    assert len(m3["assets"]["storyboard_frames"]) > 0
    assert validate_av_preview_manifest(m3) == []
    bad = json.loads(json.dumps(m3)); bad["preview_policy"]["external_calls_allowed"] = True
    assert validate_av_preview_manifest(bad)
    bad2 = json.loads(json.dumps(m3)); bad2["preview_policy"]["muxing"] = True
    assert validate_av_preview_manifest(bad2)


def test_render_preview_and_cli(tmp_path):
    p = create_media_packet("x")
    render_audio_stub(p, tmp_path); render_visual_stub(p, tmp_path)
    m = render_av_preview(p, tmp_path)
    for f in ["render/av_preview.html", "av_preview_manifest.json", "av_preview_receipt.json", "AV_PREVIEW_SUMMARY.md"]:
        assert (tmp_path / f).exists()
    info = read_preview_info(tmp_path / "render/av_preview.html")
    assert info["contains_html"] and info["contains_waveforge"] and info["contains_audio_tag"]

    env={"PYTHONPATH":"src"}
    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")
    out = tmp_path / "cli"
    subprocess.run([sys.executable,"-m","waveforge_studio.cli","render-audio-stub",str(fixture),"--out",str(out)],check=True,env=env)
    subprocess.run([sys.executable,"-m","waveforge_studio.cli","render-visual-stub",str(fixture),"--out",str(out)],check=True,env=env)
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","preview-av",str(fixture),"--out",str(out)],capture_output=True,text=True,env=env).returncode == 0
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","av-preview-validate",str(out/"av_preview_manifest.json")],capture_output=True,text=True,env=env).returncode == 0
    f1 = tmp_path / "forge1"
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","forge","hello","--out",str(f1),"--av-preview"],capture_output=True,text=True,env=env).returncode == 0
    assert (f1 / "render/av_preview.html").exists()
    f2 = tmp_path / "forge2"
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","forge","hello","--out",str(f2),"--render-audio-stub","--render-visual-stub","--av-preview"],capture_output=True,text=True,env=env).returncode == 0
    assert (f2 / "render/audio_mix.wav").exists() and (f2 / "render/storyboard/frame_001.svg").exists() and (f2 / "render/av_preview.html").exists()
    s1 = tmp_path / "smoke1"
    r1 = subprocess.run([sys.executable,"-m","waveforge_studio.cli","smoke","--out",str(s1),"--av-preview"],capture_output=True,text=True,env=env)
    assert r1.returncode == 0 and json.loads(r1.stdout)["smoke_passed"] is True
    s2 = tmp_path / "smoke2"
    r2 = subprocess.run([sys.executable,"-m","waveforge_studio.cli","smoke","--out",str(s2),"--render-audio-stub","--render-visual-stub","--av-preview"],capture_output=True,text=True,env=env)
    assert r2.returncode == 0 and json.loads(r2.stdout)["smoke_passed"] is True and (s2 / "render/av_preview.html").exists()
