from __future__ import annotations

import copy

from waveforge_studio.adapters.cineswarm_reference import (
    assert_valid_cineswarm_release_reference,
    create_cineswarm_release_reference,
    validate_cineswarm_release_reference,
)


def _final_release() -> dict:
    return {
        "schema": "waveforge.final_release_manifest.v2_alpha",
        "project": "WaveForgeStudio",
        "version": "2.9-alpha",
        "title": "Harbor Bridge Final",
        "description": "",
        "runs_root": ".",
        "final_root": "final_release",
        "stages": {
            "verification": {"passed": True},
            "certificate": {"certificate_status": "passed"},
        },
        "outputs": {
            "index": "final_release/index.html",
            "release_build_zip": "final_release/release_build.zip",
            "certificate_bundle_zip": "final_release/certificate_bundle/certificate_bundle.zip",
            "manifest": "final_release/final_release_manifest.json",
            "receipt": "final_release/final_release_receipt.json",
        },
        "receipt": {
            "schema": "waveforge.final_release_receipt.v2_alpha",
            "final_release_hash": "a" * 64,
            "created_at": "2026-09-28T19:10:00-07:00",
        },
    }


def _lineage() -> dict:
    return {
        "profile": "parallax.creative-interop.v2",
        "sourceBridgeSchema": "parallax.bridge.v2",
        "sourceTransferId": "creative-v2:harbor-bridge-v3",
        "creativeManifestHash": "sha256:" + "1" * 64,
        "baseContentHash": "sha256:" + "2" * 64,
        "overlayContentHashes": ["sha256:" + "3" * 64],
        "semanticOverlayCount": 1,
    }


def test_cineswarm_reference_is_local_reference_only_and_ratified():
    packet = create_cineswarm_release_reference(_final_release(), creative_lineage=_lineage())
    assert_valid_cineswarm_release_reference(packet)

    assert packet["schema"] == "parallax.bridge.v2"
    assert packet["source"] == "WaveForgeStudio"
    assert packet["target"] == "CineSwarm"
    assert packet["interopProfile"] == "parallax.creative-interop.v2"
    assert packet["extensionProfile"] == "parallax.creative-interop.v2.cineswarm-reference"
    assert packet["extensionStatus"] == "ratified_receiver"
    assert packet["localOnly"] is True
    assert packet["requiresUserAction"] is True
    assert packet["lineageRef"] == _lineage()["creativeManifestHash"]

    authority = packet["authority"]
    assert all(value is False for value in authority.values())


def test_cineswarm_reference_does_not_grant_media_acquisition_or_network_authority():
    packet = create_cineswarm_release_reference(_final_release())
    assert packet["authority"]["mediaAcquisitionAuthorized"] is False
    assert packet["authority"]["networkAuthorized"] is False
    assert packet["authority"]["automaticImportAuthorized"] is False


def test_cineswarm_reference_validation_detects_native_mutation():
    packet = create_cineswarm_release_reference(_final_release())
    tampered = copy.deepcopy(packet)
    tampered["payloadRefOrInline"]["native"]["title"] = "Changed after hash"

    errors = validate_cineswarm_release_reference(tampered)
    assert "contentHash does not match canonical release reference" in errors


def test_cineswarm_reference_validation_detects_authority_escalation():
    packet = create_cineswarm_release_reference(_final_release())
    tampered = copy.deepcopy(packet)
    tampered["authority"]["mediaAcquisitionAuthorized"] = True

    errors = validate_cineswarm_release_reference(tampered)
    assert "authority.mediaAcquisitionAuthorized must be false" in errors


def test_cineswarm_reference_requires_valid_lineage_hash():
    lineage = _lineage()
    lineage["creativeManifestHash"] = "not-a-hash"

    try:
        create_cineswarm_release_reference(_final_release(), creative_lineage=lineage)
    except ValueError as exc:
        assert "creative_lineage.creativeManifestHash" in str(exc)
    else:
        raise AssertionError("invalid creative lineage hash should fail closed")

def test_cineswarm_reference_rejects_status_downgrade_after_ratification():
    packet = create_cineswarm_release_reference(_final_release(), creative_lineage=_lineage())
    downgraded = copy.deepcopy(packet)
    downgraded["extensionStatus"] = "unratified_receiver"

    errors = validate_cineswarm_release_reference(downgraded)
    assert "extensionStatus must be ratified_receiver" in errors

