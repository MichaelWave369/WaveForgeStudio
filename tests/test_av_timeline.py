import json
from pathlib import Path

from waveforge_studio.av_timeline import create_av_timeline, validate_av_timeline, write_av_timeline
from waveforge_studio.cli import main as cli_main
from waveforge_studio.media_packet import create_media_packet


def test_av_timeline_shape_and_hash_behavior():
    t1 = create_av_timeline(create_media_packet("hello", seed=369369))
    t2 = create_av_timeline(create_media_packet("hello", seed=369369))
    t3 = create_av_timeline(create_media_packet("hello", seed=369370))
    assert t1["schema"] == "waveforge.av_timeline.v0"
    assert len(t1["tracks"]) == 6
    assert len(t1["markers"]) >= 9
    assert t1["receipt"]["timeline_hash"] == t2["receipt"]["timeline_hash"]
    assert t1["receipt"]["timeline_hash"] != t3["receipt"]["timeline_hash"]


def test_av_timeline_validation_errors(tmp_path: Path):
    t = create_av_timeline(create_media_packet("hello"))
    assert validate_av_timeline(t) == []
    bad = json.loads(json.dumps(t)); bad["tracks"][0]["clips"][0]["end"] = bad["tracks"][0]["clips"][0]["start"]
    assert any("timing" in x for x in validate_av_timeline(bad))
    bad2 = json.loads(json.dumps(t)); bad2["tracks"][1]["id"] = bad2["tracks"][0]["id"]
    assert any("track ids" in x for x in validate_av_timeline(bad2))


def test_write_and_cli_and_compile(tmp_path: Path, monkeypatch):
    p = create_media_packet("hello")
    write_av_timeline(p, tmp_path)
    for fn in ["av_timeline.json", "av_timeline_receipt.json", "av_timeline_markers.csv", "AV_TIMELINE_SUMMARY.md"]:
        assert (tmp_path / fn).exists()

    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")
    out = tmp_path / "cli"
    monkeypatch.setattr("sys.argv", ["waveforge-studio", "timeline", str(fixture), "--out", str(out)])
    assert cli_main() == 0
    monkeypatch.setattr("sys.argv", ["waveforge-studio", "timeline-validate", str(out / 'av_timeline.json')])
    assert cli_main() == 0

    run = tmp_path / "run"
    monkeypatch.setattr("sys.argv", ["waveforge-studio", "compile", "hello", "--out", str(run), "--bundle", "--queue", "--run-queue", "--timeline"])
    assert cli_main() == 0
    for fn in ["production_bundle.json", "render_queue.json", "execution_report.json", "artifact_ledger.json", "av_timeline.json", "timeline_preview.html"]:
        assert (run / fn).exists()
    assert (run / "phiaudio" / "phiaudio_bundle.json").exists()
    assert (run / "waverider" / "waverider_bundle.json").exists()
    assert (run / "wavetalk" / "wavetalk_bundle.json").exists()
