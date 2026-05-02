import json
from pathlib import Path

from waveforge_studio.cli import main as cli_main
from waveforge_studio.media_packet import create_media_packet
from waveforge_studio.renderer_handoff import create_renderer_handoff, validate_renderer_handoff, write_renderer_handoff


def test_handoff_schema_and_hash_behavior():
    h1 = create_renderer_handoff(create_media_packet("hello", seed=369369))
    h2 = create_renderer_handoff(create_media_packet("hello", seed=369369))
    h3 = create_renderer_handoff(create_media_packet("hello", seed=369370))
    assert h1["schema"] == "waveforge.renderer_handoff.v0"
    assert h1["receipt"]["handoff_hash"] == h2["receipt"]["handoff_hash"]
    assert h1["receipt"]["handoff_hash"] != h3["receipt"]["handoff_hash"]
    assert len(h1["visual_handoff"]["shot_prompts"]) >= 9
    assert len(h1["renderer_slots"]) >= 6


def test_handoff_validation_and_write(tmp_path: Path):
    h = create_renderer_handoff(create_media_packet("hello"))
    assert validate_renderer_handoff(h) == []
    bad = json.loads(json.dumps(h)); bad["safety"]["real_rendering_allowed"] = True
    assert validate_renderer_handoff(bad)
    bad2 = json.loads(json.dumps(h)); bad2["visual_handoff"]["shot_prompts"] = []
    assert validate_renderer_handoff(bad2)

    write_renderer_handoff(create_media_packet("hello"), tmp_path)
    for fn in ["renderer_handoff.json", "renderer_handoff_receipt.json", "audio_render_brief.md", "voiceover_script.md", "visual_shot_prompts.md", "motion_prompt_pack.md", "renderer_slots.json", "RENDERER_HANDOFF_SUMMARY.md"]:
        assert (tmp_path / fn).exists()


def test_cli_and_compile_integration(tmp_path: Path, monkeypatch):
    fixture = Path("tests/fixtures/sovereign_signal.project.waveforge.json")
    out = tmp_path / "h"
    monkeypatch.setattr("sys.argv", ["waveforge-studio", "handoff", str(fixture), "--out", str(out)])
    assert cli_main() == 0
    monkeypatch.setattr("sys.argv", ["waveforge-studio", "handoff-validate", str(out / "renderer_handoff.json")])
    assert cli_main() == 0

    run = tmp_path / "run"
    monkeypatch.setattr("sys.argv", ["waveforge-studio", "compile", "hello", "--out", str(run), "--bundle", "--queue", "--run-queue", "--timeline", "--handoff"])
    assert cli_main() == 0
    for fn in ["production_bundle.json", "render_queue.json", "execution_report.json", "artifact_ledger.json", "av_timeline.json", "renderer_handoff.json", "timeline_preview.html"]:
        assert (run / fn).exists()
