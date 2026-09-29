from __future__ import annotations

import copy

import pytest

from waveforge_studio.adapters.paracut_bridge import (
    accept_paracut_bridge_revision,
    assert_valid_paracut_bridge_intake,
    create_paracut_bridge_intake,
    validate_paracut_bridge_intake,
)
from waveforge_studio.hashing import sha256_digest


def _lineage() -> dict:
    return {
        "profile": "parallax.creative-interop.v2",
        "sourceBridgeSchema": "parallax.bridge.v2",
        "sourceTransferId": "creative-v2:harbor-bridge-v3",
        "creativeManifestHash": "sha256:" + "1" * 64,
        "baseContentHash": "sha256:" + "2" * 64,
        "overlayContentHashes": ["sha256:" + "3" * 64],
        "semanticOverlayCount": 1,
        "auralithCaptureHash": "sha256:" + "4" * 64,
        "auralithReceiptHash": "sha256:" + "5" * 64,
        "paraCutAssetHashes": ["sha256:" + "2" * 64, "sha256:" + "3" * 64],
    }


def _bridge(revision: int = 1) -> dict:
    plan = {
        "plan_id": "plan_interop_v2_001",
        "job_id": "job_interop_v2_001",
        "project_id": "project_interop_v2_001",
        "output_uri": "./exports/interop-v2.mp4",
        "preset": {
            "preset_id": "preset_wide_1080p",
            "name": "Wide 1080p",
            "platform": "wide",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "video_codec": "h264",
            "audio_codec": "aac",
            "container": "mp4",
        },
        "duration_seconds": 12,
        "inputs": [],
        "clips": [],
        "filter_graph": [],
        "argv": [],
        "warnings": [],
        "created_at": "2026-09-28T18:55:00-07:00",
    }
    lineage = _lineage()
    return {
        "schema": "parallax.bridge.v2",
        "protocol": "parallax-bridge",
        "version": 2,
        "interopProfile": "parallax.creative-interop.v2",
        "transferId": "paracut-waveforge-v2:" + plan["plan_id"],
        "source": "ParaCut",
        "target": "WaveForgeStudio",
        "createdAt": "2026-09-28T18:55:00-07:00",
        "localOnly": True,
        "payloadType": "application/vnd.paracut.render-plan+json",
        "payloadRefOrInline": {"native": plan},
        "contentHash": "sha256:" + sha256_digest(plan),
        "planRevision": revision,
        "creativeLineage": lineage,
        "trustLabels": ["creative-lineage-bound"],
        "warnings": [],
        "compatibilityNotes": [
            "Reference-only handoff.",
            "Creative lineage grants no execution authority.",
        ],
        "lineageRef": lineage["creativeManifestHash"],
        "requiresUserAction": True,
        "authority": {
            "realRenderingAuthorized": False,
            "networkAuthorized": False,
            "subprocessAuthorized": False,
            "automaticImportAuthorized": False,
            "publishAuthorized": False,
        },
    }


def test_v2_intake_binds_render_plan_and_creative_lineage():
    bridge = _bridge()
    intake = create_paracut_bridge_intake(bridge)
    assert_valid_paracut_bridge_intake(intake)

    assert intake["schema"] == "waveforge.paracut_bridge_intake.v2_alpha"
    assert intake["interop_profile"] == "parallax.creative-interop.v2"
    assert intake["plan_revision"] == 1
    assert intake["creative_lineage"]["creativeManifestHash"] == bridge["creativeLineage"]["creativeManifestHash"]
    assert intake["creative_lineage_hash"] == "sha256:" + sha256_digest(bridge["creativeLineage"])
    assert intake["receipt"]["creative_lineage_hash"] == intake["creative_lineage_hash"]
    assert intake["receipt"]["creative_manifest_hash"] == bridge["creativeLineage"]["creativeManifestHash"]
    assert intake["safety"]["real_rendering_allowed"] is False
    assert intake["safety"]["network_allowed"] is False
    assert intake["safety"]["publish_allowed"] is False


def test_v2_rejects_render_plan_mutated_after_hash():
    bridge = _bridge()
    bridge["payloadRefOrInline"]["native"]["output_uri"] = "./exports/tampered.mp4"

    with pytest.raises(ValueError, match="contentHash does not match canonical native ParaCut RenderPlan"):
        create_paracut_bridge_intake(bridge)


def test_v2_rejects_lineage_hash_shape_mutation():
    bridge = _bridge()
    bridge["creativeLineage"]["baseContentHash"] = "sha256:not-valid"

    with pytest.raises(ValueError, match="creativeLineage.baseContentHash"):
        create_paracut_bridge_intake(bridge)


def test_v2_rejects_lineage_ref_substitution():
    bridge = _bridge()
    bridge["lineageRef"] = "sha256:" + "9" * 64

    with pytest.raises(ValueError, match="lineageRef"):
        create_paracut_bridge_intake(bridge)


@pytest.mark.parametrize(
    "flag",
    [
        "realRenderingAuthorized",
        "networkAuthorized",
        "subprocessAuthorized",
        "automaticImportAuthorized",
        "publishAuthorized",
    ],
)
def test_v2_rejects_authority_escalation(flag: str):
    bridge = _bridge()
    bridge["authority"][flag] = True

    with pytest.raises(ValueError, match="must be false"):
        create_paracut_bridge_intake(bridge)


def test_v2_intake_validation_detects_lineage_mutation_after_receipt():
    intake = create_paracut_bridge_intake(_bridge())
    tampered = copy.deepcopy(intake)
    tampered["creative_lineage"]["creativeManifestHash"] = "sha256:" + "8" * 64

    errors = validate_paracut_bridge_intake(tampered)
    assert "creative_lineage_hash does not match creative_lineage" in errors
    assert "lineage.creative_manifest_hash does not match creative_lineage" in errors
    assert "receipt.intake_hash does not match intake contents" in errors


def test_v2_freshness_replay_and_rollback_rules_hold():
    ledger: dict[str, dict] = {}
    first = accept_paracut_bridge_revision(_bridge(2), ledger)
    assert first["status"] == "accepted"

    replay = accept_paracut_bridge_revision(copy.deepcopy(_bridge(2)), ledger)
    assert replay["status"] == "replay"

    stale = _bridge(1)
    with pytest.raises(ValueError, match="stale plan revision"):
        accept_paracut_bridge_revision(stale, ledger)


def test_v1_still_dispatches_to_legacy_intake():
    plan = _bridge()["payloadRefOrInline"]["native"]
    legacy = {
        "schema": "parallax.bridge.v1",
        "protocol": "parallax-bridge",
        "version": 1,
        "transferId": "paracut-waveforge:" + plan["plan_id"],
        "source": "ParaCut",
        "target": "WaveForgeStudio",
        "createdAt": plan["created_at"],
        "localOnly": True,
        "payloadType": "application/vnd.paracut.render-plan+json",
        "payloadRefOrInline": {"native": plan},
        "contentHash": "sha256:" + sha256_digest(plan),
        "trustLabels": [],
        "warnings": [],
        "compatibilityNotes": [],
        "lineageRef": None,
        "requiresUserAction": True,
    }
    intake = create_paracut_bridge_intake(legacy)
    assert intake["schema"] == "waveforge.paracut_bridge_intake.v1_alpha"
