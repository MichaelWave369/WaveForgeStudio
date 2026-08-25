from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

from waveforge_studio.adapters.paracut_bridge import (
    assert_valid_paracut_bridge_intake,
    create_paracut_bridge_intake,
)
from waveforge_studio.hashing import sha256_digest


def _load_bridge() -> dict:
    path = Path(__file__).parent / "fixtures" / "parallax-pass5-waveforge-bridge.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_pass5_real_artifact_survives_paracut_bridge_and_waveforge_receipt():
    bridge = _load_bridge()
    plan = bridge["payloadRefOrInline"]["native"]
    image_uri = plan["inputs"][0]["uri"]
    prefix, encoded = image_uri.split(",", 1)
    assert prefix == "data:image/png;base64"

    png_bytes = base64.b64decode(encoded)
    png_sha256 = hashlib.sha256(png_bytes).hexdigest()
    assert len(png_bytes) == 1150
    assert png_sha256 == "06f4e6612f5cda7c8596813426c35fd44a40f8d11db016c3e7a655ac6d7c342c"

    plan_sha256 = sha256_digest(plan)
    assert plan_sha256 == "c929aa69ebf11d0c6878caedefb7dffc621f52fb5716b55acc45e01be16ac088"
    assert bridge["contentHash"] == f"sha256:{plan_sha256}"
    assert sha256_digest(bridge) == "58c15e00d96a4a823a316b1c4e732deaa3ff9f7f816d9d2fe2be260ac2e46f1a"

    intake = create_paracut_bridge_intake(bridge)
    assert_valid_paracut_bridge_intake(intake)

    assert intake["source_content_hash"] == bridge["contentHash"]
    assert intake["bridge_hash"] == sha256_digest(bridge)
    assert intake["receipt"]["bridge_hash"] == intake["bridge_hash"]
    assert intake["receipt"]["source_content_hash"] == bridge["contentHash"]
    assert intake["lineage"]["source_project_id"] == "project_pass5_real_artifact_001"
    assert intake["lineage"]["source_job_id"] == "job_pass5_real_artifact_001"
    assert intake["lineage"]["source_plan_id"] == "plan_pass5_real_artifact_001"

    assert intake["safety"] == {
        "reference_only": True,
        "handoff_only": True,
        "requires_user_action": True,
        "external_calls_allowed": False,
        "subprocess_allowed": False,
        "network_allowed": False,
        "real_rendering_allowed": False,
        "auto_import_into_media_packet": False,
    }
