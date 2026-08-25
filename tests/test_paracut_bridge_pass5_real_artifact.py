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
    assert prefix == "data:image/svg+xml;base64"

    artifact_bytes = base64.b64decode(encoded)
    artifact_sha256 = hashlib.sha256(artifact_bytes).hexdigest()
    assert len(artifact_bytes) == 356
    assert artifact_sha256 == "e973d160eb0774197d2d59db89277c9c6a28ff0e2b736a24fe3bebb559fb9efe"

    plan_sha256 = sha256_digest(plan)
    assert plan_sha256 == "dbfaa18ae5cfff24a8252f69f18ffe69e72afba3f0a729c6eb3bb32668c53710"
    assert bridge["contentHash"] == f"sha256:{plan_sha256}"
    assert sha256_digest(bridge) == "9826123c19dc9b43ba680440a426fdcd6b4d684e64cde8b7e8eea01924ea6266"

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
