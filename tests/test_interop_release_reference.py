from __future__ import annotations

import copy

from waveforge_studio.adapters.interop_release_reference import (
    assert_valid_interop_release_reference,
    create_interop_release_reference,
    validate_interop_release_reference,
)
from waveforge_studio.adapters.paracut_bridge import create_paracut_bridge_intake
from waveforge_studio.hashing import sha256_digest


def _bridge() -> dict:
    plan = {
        "plan_id": "plan_acceptance_003",
        "job_id": "job_acceptance_003",
        "project_id": "interop-acceptance-003",
        "output_uri": "./exports/acceptance-003.mp4",
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
        "warnings": ["Interop Room does not render media."],
        "created_at": "2026-09-29T03:30:00Z",
    }
    lineage = {
        "profile": "parallax.creative-interop.v2",
        "sourceBridgeSchema": "parallax.bridge.v2",
        "sourceTransferId": "creative-v2:acceptance-003",
        "creativeManifestHash": "sha256:" + "1" * 64,
        "baseContentHash": "sha256:" + "2" * 64,
        "overlayContentHashes": ["sha256:" + "3" * 64],
        "semanticOverlayCount": 1,
        "auralithCaptureHash": "sha256:" + "4" * 64,
        "auralithReceiptHash": "sha256:" + "5" * 64,
        "paraCutAssetHashes": ["sha256:" + "2" * 64, "sha256:" + "3" * 64],
    }
    return {
        "schema": "parallax.bridge.v2",
        "protocol": "parallax-bridge",
        "version": 2,
        "interopProfile": "parallax.creative-interop.v2",
        "transferId": "paracut-waveforge-v2:" + plan["plan_id"],
        "source": "ParaCut",
        "target": "WaveForgeStudio",
        "createdAt": plan["created_at"],
        "localOnly": True,
        "payloadType": "application/vnd.paracut.render-plan+json",
        "payloadRefOrInline": {"native": plan},
        "contentHash": "sha256:" + sha256_digest(plan),
        "planRevision": 1,
        "creativeLineage": lineage,
        "trustLabels": ["creative-lineage-bound"],
        "warnings": [],
        "compatibilityNotes": [],
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


def test_interop_release_reference_is_hash_bound_and_explicitly_not_rendered():
    intake = create_paracut_bridge_intake(_bridge())
    reference = create_interop_release_reference(intake)
    assert_valid_interop_release_reference(reference)

    assert reference["schema"] == "waveforge.interop_release_reference.v1"
    assert reference["mediaRendered"] is False
    assert reference["finalRelease"] is False
    assert reference["source"]["render_plan_hash"] == intake["source_content_hash"]
    assert reference["source"]["creative_lineage_hash"] == intake["creative_lineage_hash"]
    assert reference["source"]["creative_manifest_hash"] == intake["creative_lineage"]["creativeManifestHash"]
    assert reference["planned_output"]["uri"] == "./exports/acceptance-003.mp4"
    assert reference["receipt"]["release_reference_hash"].startswith("sha256:")
    assert all(value is False for value in reference["authority"].values())


def test_interop_release_reference_detects_post_receipt_mutation():
    intake = create_paracut_bridge_intake(_bridge())
    reference = create_interop_release_reference(intake)
    tampered = copy.deepcopy(reference)
    tampered["planned_output"]["uri"] = "./exports/not-the-same.mp4"

    errors = validate_interop_release_reference(tampered)
    assert "receipt.release_reference_hash does not match reference contents" in errors


def test_interop_release_reference_rejects_authority_promotion():
    intake = create_paracut_bridge_intake(_bridge())
    reference = create_interop_release_reference(intake)
    tampered = copy.deepcopy(reference)
    tampered["authority"]["renderAuthorized"] = True

    errors = validate_interop_release_reference(tampered)
    assert "authority.renderAuthorized must be false" in errors
