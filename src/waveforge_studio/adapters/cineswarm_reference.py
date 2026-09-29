from __future__ import annotations

import re
from typing import Any

from ..hashing import sha256_digest

_HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


def create_cineswarm_release_reference(
    final_release: dict[str, Any],
    *,
    creative_lineage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if final_release.get("schema") != "waveforge.final_release_manifest.v2_alpha":
        raise ValueError("Expected waveforge.final_release_manifest.v2_alpha")

    receipt = final_release.get("receipt")
    if not isinstance(receipt, dict):
        raise ValueError("WaveForge final release receipt required")
    release_hash = str(receipt.get("final_release_hash") or "")
    if not _HEX64.match(release_hash):
        raise ValueError("WaveForge final release hash must be 64 hex characters")

    stages = final_release.get("stages") or {}
    verification = stages.get("verification") or {}
    certificate = stages.get("certificate") or {}
    outputs = final_release.get("outputs") or {}

    native: dict[str, Any] = {
        "schema": "waveforge.cineswarm_release_reference.v1_alpha",
        "releaseSchema": final_release["schema"],
        "title": str(final_release.get("title") or "WaveForgeStudio Final Release"),
        "finalReleaseHash": "sha256:" + release_hash.lower(),
        "verificationPassed": verification.get("passed"),
        "certificateStatus": certificate.get("certificate_status"),
        "outputs": {
            "index": outputs.get("index"),
            "releaseBuildZip": outputs.get("release_build_zip"),
            "certificateBundleZip": outputs.get("certificate_bundle_zip"),
            "manifest": outputs.get("manifest"),
            "receipt": outputs.get("receipt"),
        },
    }

    if creative_lineage is not None:
        if not isinstance(creative_lineage, dict):
            raise ValueError("creative_lineage must be an object")
        if creative_lineage.get("profile") != "parallax.creative-interop.v2":
            raise ValueError("creative_lineage.profile must be parallax.creative-interop.v2")
        manifest_hash = str(creative_lineage.get("creativeManifestHash") or "")
        if not re.match(r"^sha256:[0-9a-fA-F]{64}$", manifest_hash):
            raise ValueError("creative_lineage.creativeManifestHash must be sha256:<64 hex>")
        native["creativeLineage"] = creative_lineage

    content_hash = "sha256:" + sha256_digest(native)
    created_at = str(receipt.get("created_at") or "")
    if not created_at:
        raise ValueError("WaveForge final release receipt created_at required")

    return {
        "schema": "parallax.bridge.v2",
        "protocol": "parallax-bridge",
        "version": 2,
        "interopProfile": "parallax.creative-interop.v2",
        "extensionProfile": "parallax.creative-interop.v2.cineswarm-reference",
        "extensionStatus": "unratified_receiver",
        "transferId": "waveforge-cineswarm:" + release_hash.lower(),
        "source": "WaveForgeStudio",
        "target": "CineSwarm",
        "createdAt": created_at,
        "localOnly": True,
        "payloadType": "application/vnd.waveforge.final-release-reference+json",
        "payloadRefOrInline": {"native": native},
        "contentHash": content_hash,
        "trustLabels": ["reference-only", "release-lineage-bound"],
        "warnings": [
            "CineSwarm receiver adoption is not ratified by this repository.",
        ],
        "compatibilityNotes": [
            "Reference-only release handoff. This packet does not authorize CineSwarm import, acquisition, publishing, rendering, or network activity.",
            "Receiver must independently verify contentHash and require explicit human acceptance before any local import.",
        ],
        "lineageRef": (
            creative_lineage.get("creativeManifestHash")
            if isinstance(creative_lineage, dict)
            else None
        ),
        "requiresUserAction": True,
        "authority": {
            "automaticImportAuthorized": False,
            "networkAuthorized": False,
            "subprocessAuthorized": False,
            "renderAuthorized": False,
            "publishAuthorized": False,
            "mediaAcquisitionAuthorized": False,
        },
    }


def validate_cineswarm_release_reference(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get("schema") != "parallax.bridge.v2":
        errors.append("schema invalid")
    if packet.get("protocol") != "parallax-bridge" or packet.get("version") != 2:
        errors.append("protocol/version invalid")
    if packet.get("source") != "WaveForgeStudio" or packet.get("target") != "CineSwarm":
        errors.append("route invalid")
    if packet.get("extensionProfile") != "parallax.creative-interop.v2.cineswarm-reference":
        errors.append("extensionProfile invalid")
    if packet.get("extensionStatus") != "unratified_receiver":
        errors.append("extensionStatus must remain unratified_receiver")
    if packet.get("localOnly") is not True:
        errors.append("localOnly must be true")
    if packet.get("requiresUserAction") is not True:
        errors.append("requiresUserAction must be true")

    native = (packet.get("payloadRefOrInline") or {}).get("native")
    if not isinstance(native, dict):
        errors.append("native release reference required")
    else:
        expected_hash = "sha256:" + sha256_digest(native)
        if str(packet.get("contentHash") or "").lower() != expected_hash:
            errors.append("contentHash does not match canonical release reference")

    authority = packet.get("authority") or {}
    for key in (
        "automaticImportAuthorized",
        "networkAuthorized",
        "subprocessAuthorized",
        "renderAuthorized",
        "publishAuthorized",
        "mediaAcquisitionAuthorized",
    ):
        if authority.get(key) is not False:
            errors.append(f"authority.{key} must be false")

    return errors


def assert_valid_cineswarm_release_reference(packet: dict[str, Any]) -> None:
    errors = validate_cineswarm_release_reference(packet)
    if errors:
        raise ValueError("Invalid CineSwarm release reference: " + "; ".join(errors))
