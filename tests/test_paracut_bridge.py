from __future__ import annotations

import copy

import pytest

from waveforge_studio.adapters.paracut_bridge import (
    assert_valid_paracut_bridge_intake,
    create_paracut_bridge_intake,
    validate_paracut_bridge_intake,
)
from waveforge_studio.hashing import sha256_digest


def _bridge() -> dict:
    native = {
        "plan_id": "plan_interop_001",
        "job_id": "job_interop_001",
        "project_id": "project_interop_001",
        "output_uri": "./exports/interop.mp4",
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
        "created_at": "2026-08-25T17:15:00Z",
    }
    return {
        "schema": "parallax.bridge.v1",
        "protocol": "parallax-bridge",
        "version": 1,
        "transferId": "paracut-waveforge:plan_interop_001",
        "source": "ParaCut",
        "target": "WaveForgeStudio",
        "createdAt": "2026-08-25T17:15:00Z",
        "localOnly": True,
        "payloadType": "application/vnd.paracut.render-plan+json",
        "payloadRefOrInline": {"native": native},
        "contentHash": f"sha256:{sha256_digest(native)}",
        "trustLabels": [],
        "warnings": [],
        "compatibilityNotes": [
            "Reference-only handoff. WaveForgeStudio must not treat this bridge as render authorization."
        ],
        "lineageRef": None,
        "requiresUserAction": True,
    }


def test_paracut_bridge_intake_is_reference_only_and_receipted():
    bridge = _bridge()
    intake = create_paracut_bridge_intake(bridge)
    assert_valid_paracut_bridge_intake(intake)
    assert intake["source_content_hash"] == bridge["contentHash"]
    assert intake["lineage"]["source_plan_id"] == "plan_interop_001"
    assert intake["safety"]["reference_only"] is True
    assert intake["safety"]["real_rendering_allowed"] is False
    assert intake["safety"]["auto_import_into_media_packet"] is False
    assert intake["receipt"]["bridge_hash"] == intake["bridge_hash"]


def test_paracut_bridge_rejects_removed_human_boundary():
    bridge = _bridge()
    bridge["requiresUserAction"] = False
    with pytest.raises(ValueError, match="explicit user action"):
        create_paracut_bridge_intake(bridge)


def test_paracut_bridge_rejects_invalid_content_hash():
    bridge = _bridge()
    bridge["contentHash"] = "sha256:not-a-real-hash"
    with pytest.raises(ValueError, match="contentHash"):
        create_paracut_bridge_intake(bridge)


def test_paracut_bridge_rejects_native_plan_mutated_after_hash():
    bridge = _bridge()
    bridge["payloadRefOrInline"]["native"]["output_uri"] = "./exports/tampered.mp4"
    with pytest.raises(ValueError, match="does not match canonical native ParaCut RenderPlan"):
        create_paracut_bridge_intake(bridge)


def test_paracut_bridge_rejects_transfer_id_substitution():
    bridge = _bridge()
    bridge["transferId"] = "paracut-waveforge:plan_substituted"
    with pytest.raises(ValueError, match="transferId does not match native ParaCut plan_id"):
        create_paracut_bridge_intake(bridge)


def test_intake_validation_detects_render_plan_mutation_after_receipt():
    intake = create_paracut_bridge_intake(_bridge())
    tampered = copy.deepcopy(intake)
    tampered["render_plan"]["duration_seconds"] = 99
    errors = validate_paracut_bridge_intake(tampered)
    assert "source_content_hash does not match canonical render_plan" in errors
    assert "receipt.intake_hash does not match intake contents" in errors


def test_intake_validation_detects_lineage_substitution_after_receipt():
    intake = create_paracut_bridge_intake(_bridge())
    tampered = copy.deepcopy(intake)
    tampered["lineage"]["source_plan_id"] = "plan_substituted"
    errors = validate_paracut_bridge_intake(tampered)
    assert "receipt.intake_hash does not match intake contents" in errors


def test_intake_validation_detects_transfer_id_substitution_after_receipt():
    intake = create_paracut_bridge_intake(_bridge())
    tampered = copy.deepcopy(intake)
    tampered["transfer_id"] = "paracut-waveforge:plan_substituted"
    errors = validate_paracut_bridge_intake(tampered)
    assert "transfer_id does not match render_plan.plan_id" in errors
    assert "receipt.intake_hash does not match intake contents" in errors


@pytest.mark.parametrize(
    "flag",
    [
        "external_calls_allowed",
        "subprocess_allowed",
        "network_allowed",
        "real_rendering_allowed",
        "auto_import_into_media_packet",
    ],
)
def test_intake_validation_detects_execution_flag_escalation_after_receipt(flag: str):
    intake = create_paracut_bridge_intake(_bridge())
    tampered = copy.deepcopy(intake)
    tampered["safety"][flag] = True
    errors = validate_paracut_bridge_intake(tampered)
    assert f"safety.{flag} must be false" in errors
    assert "receipt.intake_hash does not match intake contents" in errors


def test_intake_validation_detects_receipt_hash_substitution():
    intake = create_paracut_bridge_intake(_bridge())
    tampered = copy.deepcopy(intake)
    tampered["receipt"]["bridge_hash"] = "0" * 64
    errors = validate_paracut_bridge_intake(tampered)
    assert "receipt.bridge_hash does not match intake.bridge_hash" in errors


def test_exact_bridge_replay_is_deterministic_and_cannot_escalate_authority():
    bridge = _bridge()
    first = create_paracut_bridge_intake(copy.deepcopy(bridge))
    second = create_paracut_bridge_intake(copy.deepcopy(bridge))

    # Current intake is stateless and reference-only: exact replay is idempotent,
    # producing the same hashes/receipt instead of multiplying authority.
    assert first == second
    assert first["receipt"]["intake_hash"] == second["receipt"]["intake_hash"]
    assert first["bridge_hash"] == second["bridge_hash"]

    safety = second["safety"]
    assert safety["requires_user_action"] is True
    assert safety["reference_only"] is True
    assert safety["handoff_only"] is True
    assert safety["external_calls_allowed"] is False
    assert safety["subprocess_allowed"] is False
    assert safety["network_allowed"] is False
    assert safety["real_rendering_allowed"] is False
    assert safety["auto_import_into_media_packet"] is False
