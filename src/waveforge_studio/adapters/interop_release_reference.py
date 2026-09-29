from __future__ import annotations

from typing import Any

from .paracut_bridge import assert_valid_paracut_bridge_intake
from ..hashing import sha256_digest


def create_interop_release_reference(intake: dict[str, Any]) -> dict[str, Any]:
    """Create a hash-bound release reference from an accepted ParaCut v2 intake.

    This is not rendered media and not a WaveForge final release. It is a
    deterministic packaging reference that lets live acceptance continue
    through the WaveForge room without fabricating a render.
    """

    assert_valid_paracut_bridge_intake(intake)
    if intake.get("schema") != "waveforge.paracut_bridge_intake.v2_alpha":
        raise ValueError("Interop release reference requires v2 ParaCut intake")

    plan = intake["render_plan"]
    lineage = intake["creative_lineage"]
    body = {
        "schema": "waveforge.interop_release_reference.v1",
        "project": "WaveForgeStudio",
        "created_at": intake.get("received_at"),
        "source": {
            "transfer_id": intake.get("transfer_id"),
            "plan_id": plan["plan_id"],
            "project_id": plan["project_id"],
            "plan_revision": intake["plan_revision"],
            "render_plan_hash": intake["source_content_hash"],
            "creative_lineage_hash": intake["creative_lineage_hash"],
            "creative_manifest_hash": lineage["creativeManifestHash"],
        },
        "planned_output": {
            "uri": plan["output_uri"],
            "preset": plan.get("preset"),
            "duration_seconds": plan.get("duration_seconds"),
        },
        "mediaRendered": False,
        "finalRelease": False,
        "authority": {
            "renderAuthorized": False,
            "networkAuthorized": False,
            "subprocessAuthorized": False,
            "publishAuthorized": False,
            "automaticImportAuthorized": False,
            "mediaAcquisitionAuthorized": False,
        },
        "notes": [
            "Reference-only packaging evidence from an accepted ParaCut RenderPlan.",
            "No media was rendered by creating this reference.",
            "This object is not a WaveForge final release manifest.",
        ],
    }
    reference_hash = "sha256:" + sha256_digest(body)
    return {
        **body,
        "receipt": {
            "schema": "waveforge.interop_release_reference_receipt.v1",
            "release_reference_hash": reference_hash,
            "created_at": intake.get("received_at"),
        },
    }


def validate_interop_release_reference(reference: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if reference.get("schema") != "waveforge.interop_release_reference.v1":
        errors.append("schema invalid")
    if reference.get("project") != "WaveForgeStudio":
        errors.append("project must be WaveForgeStudio")
    if reference.get("mediaRendered") is not False:
        errors.append("mediaRendered must be false")
    if reference.get("finalRelease") is not False:
        errors.append("finalRelease must be false")

    source = reference.get("source") or {}
    for key in (
        "transfer_id",
        "plan_id",
        "project_id",
        "plan_revision",
        "render_plan_hash",
        "creative_lineage_hash",
        "creative_manifest_hash",
    ):
        if source.get(key) in (None, ""):
            errors.append(f"source.{key} required")

    authority = reference.get("authority") or {}
    for key in (
        "renderAuthorized",
        "networkAuthorized",
        "subprocessAuthorized",
        "publishAuthorized",
        "automaticImportAuthorized",
        "mediaAcquisitionAuthorized",
    ):
        if authority.get(key) is not False:
            errors.append(f"authority.{key} must be false")

    receipt = reference.get("receipt") or {}
    expected_body = {key: value for key, value in reference.items() if key != "receipt"}
    expected_hash = "sha256:" + sha256_digest(expected_body)
    if receipt.get("release_reference_hash") != expected_hash:
        errors.append("receipt.release_reference_hash does not match reference contents")
    return errors


def assert_valid_interop_release_reference(reference: dict[str, Any]) -> None:
    errors = validate_interop_release_reference(reference)
    if errors:
        raise ValueError("Invalid WaveForge interop release reference: " + "; ".join(errors))
