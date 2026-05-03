import json
import subprocess
import sys

from waveforge_studio.demo_gallery import create_gallery_manifest, derive_run_tags, discover_waveforge_runs, read_gallery_info, validate_gallery_manifest, write_demo_gallery


def test_discover_empty(tmp_path):
    assert discover_waveforge_runs(tmp_path) == []


def test_tags_and_gallery_search(tmp_path):
    env = {"PYTHONPATH": "src"}
    run1 = tmp_path / "demo1"
    run2 = tmp_path / "demo2"
    subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "forge", "one", "--out", str(run1)], check=True, env=env)
    subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "forge", "two", "--out", str(run2), "--render-audio-stub", "--render-visual-stub", "--av-preview", "--preview-pack", "--preview-pack-zip"], check=True, env=env)

    runs = discover_waveforge_runs(tmp_path)
    assert len(runs) >= 2
    assert runs == sorted(runs, key=lambda x: x["run_path"])
    assert all(isinstance(r.get("tags"), list) for r in runs)
    assert any(r.get("archetype") == "sovereign_signal" for r in runs)

    sample = {"alpha_ready": True, "smoke_passed": None, "mode": "mythic reel", "seed": 1, "archetype": "sovereign signal", "present": {"av_preview": True, "preview_pack": True, "preview_pack_zip": True, "audio_stub": True, "visual_stub": True}}
    t = derive_run_tags(sample)
    assert t == sorted(t)
    assert "alpha-ready" in t and "smoke-missing" in t and "has-zip" in t and "mode:mythic-reel" in t

    m1 = create_gallery_manifest(tmp_path)
    m2 = create_gallery_manifest(tmp_path)
    assert m1["schema"] == "waveforge.demo_gallery_manifest.v1_alpha"
    assert m1["receipt"]["gallery_hash"] == m2["receipt"]["gallery_hash"]
    assert m1["search"]["enabled"] is True
    assert isinstance(m1["search"]["available_tags"], list)
    assert m1["search"]["available_tags"] == sorted(m1["search"]["available_tags"])
    assert "filters" in m1 and m1["filters"]["has_zip"]["true"] >= 1
    assert not validate_gallery_manifest(m1)

    bad = json.loads(json.dumps(m1)); del bad["search"]["available_tags"]
    assert validate_gallery_manifest(bad)
    bad2 = json.loads(json.dumps(m1)); bad2["runs"][0].pop("tags", None)
    assert validate_gallery_manifest(bad2)

    m = write_demo_gallery(tmp_path)
    g = tmp_path / "gallery"
    for f in ["index.html", "gallery_manifest.json", "gallery_receipt.json", "GALLERY_SUMMARY.md"]:
        assert (g / f).exists()
    info = read_gallery_info(g)
    assert info["index_exists"] and info["contains_waveforge"]
    html = (g / "index.html").read_text(encoding="utf-8")
    assert 'id=\'q\'' in html or 'id="q"' in html
    assert 'id=\'gallery-data\'' in html or 'id="gallery-data"' in html
    assert "Reset Filters" in html
    assert "tag-btn" in html

    for r in m["runs"]:
        for v in r["links"].values():
            if v:
                assert not v.startswith("/")

    out = subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "gallery", str(tmp_path), "--out", str(tmp_path / "gallery2")], capture_output=True, text=True, env=env)
    assert out.returncode == 0
    payload = json.loads(out.stdout)
    assert "tag_count" in payload
    assert subprocess.run([sys.executable, "-m", "waveforge_studio.cli", "gallery-validate", str(tmp_path / "gallery2/gallery_manifest.json")], capture_output=True, text=True, env=env).returncode == 0
