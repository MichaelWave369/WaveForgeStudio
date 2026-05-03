import json
import subprocess
import sys
from pathlib import Path

from waveforge_studio.local_visual_renderer import create_visual_render_manifest, render_visual_stub, read_svg_info, validate_visual_render_manifest
from waveforge_studio.media_packet import create_media_packet


def test_manifest_validation_and_determinism():
    p = create_media_packet("x", seed=369369)
    m1 = create_visual_render_manifest(p)
    m2 = create_visual_render_manifest(p)
    assert m1["schema"] == "waveforge.local_visual_render_manifest.v1_alpha"
    assert m1["receipt"]["visual_render_hash"] == m2["receipt"]["visual_render_hash"]
    m3 = create_visual_render_manifest(create_media_packet("x", seed=1))
    assert m1["receipt"]["visual_render_hash"] != m3["receipt"]["visual_render_hash"]
    assert validate_visual_render_manifest(m1) == []
    bad = json.loads(json.dumps(m1)); bad["render_policy"]["external_calls_allowed"] = True
    assert validate_visual_render_manifest(bad)
    bad2 = json.loads(json.dumps(m1)); bad2["render_policy"]["image_generation"] = True
    assert validate_visual_render_manifest(bad2)


def test_render_and_cli(tmp_path):
    p = create_media_packet("x")
    m = render_visual_stub(p, tmp_path)
    for f in ["render/storyboard/frame_001.svg","render/storyboard/frame_009.svg","render/storyboard_index.html","visual_render_manifest.json","visual_render_receipt.json","VISUAL_RENDER_SUMMARY.md"]:
        assert (tmp_path / f).exists()
    info = read_svg_info(tmp_path / "render/storyboard/frame_001.svg")
    assert info["contains_svg"] and info["contains_waveforge"]
    m2 = render_visual_stub(p, tmp_path / "b")
    assert m["receipt"]["visual_render_hash"] == m2["receipt"]["visual_render_hash"]

    env={"PYTHONPATH":"src"}
    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")
    out = tmp_path / "cli"
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","render-visual-stub",str(fixture),"--out",str(out)],capture_output=True,text=True,env=env).returncode == 0
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","visual-render-validate",str(out/"visual_render_manifest.json")],capture_output=True,text=True,env=env).returncode == 0
    f1 = tmp_path / "f1"
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","forge","hello","--out",str(f1),"--render-visual-stub"],capture_output=True,text=True,env=env).returncode == 0
    assert (f1 / "render/storyboard/frame_001.svg").exists()
    f2 = tmp_path / "f2"
    assert subprocess.run([sys.executable,"-m","waveforge_studio.cli","forge","hello","--out",str(f2),"--render-audio-stub","--render-visual-stub"],capture_output=True,text=True,env=env).returncode == 0
    assert (f2 / "render/audio_mix.wav").exists() and (f2 / "render/storyboard/frame_001.svg").exists()
    s1 = tmp_path / "s1"
    r1 = subprocess.run([sys.executable,"-m","waveforge_studio.cli","smoke","--out",str(s1),"--render-visual-stub"],capture_output=True,text=True,env=env)
    assert r1.returncode == 0 and json.loads(r1.stdout)["smoke_passed"] is True
    s2 = tmp_path / "s2"
    r2 = subprocess.run([sys.executable,"-m","waveforge_studio.cli","smoke","--out",str(s2),"--render-audio-stub","--render-visual-stub"],capture_output=True,text=True,env=env)
    assert r2.returncode == 0 and json.loads(r2.stdout)["smoke_passed"] is True
