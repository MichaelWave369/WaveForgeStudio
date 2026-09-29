from __future__ import annotations

import re
from typing import Any

from ..hashing import sha256_digest

_SHA256 = re.compile(r"^sha256:[0-9a-fA-F]{64}$")


def _plan_revision(bridge: dict[str, Any]) -> int | None:
    revision = bridge.get("planRevision")
    if revision is None:
        return None
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise ValueError("planRevision must be a positive integer when supplied")
    return revision


def _create_paracut_bridge_intake_v1(bridge: dict[str, Any]) -> dict[str, Any]:
    if bridge.get("schema") != "parallax.bridge.v1":
        raise ValueError("Expected parallax.bridge.v1")
    if bridge.get("protocol") != "parallax-bridge" or bridge.get("version") != 1:
        raise ValueError("Unsupported Parallax bridge protocol/version")
    if bridge.get("source") != "ParaCut" or bridge.get("target") != "WaveForgeStudio":
        raise ValueError("Unsupported bridge route")
    if bridge.get("localOnly") is not True:
        raise ValueError("ParaCut bridge must remain local-only")
    if bridge.get("requiresUserAction") is not True:
        raise ValueError("ParaCut bridge must require explicit user action")
    if bridge.get("payloadType") != "application/vnd.paracut.render-plan+json":
        raise ValueError("Unsupported ParaCut payload type")

    native = (bridge.get("payloadRefOrInline") or {}).get("native")
    if not isinstance(native, dict):
        raise ValueError("Native ParaCut RenderPlan payload is required")
    for field in ("plan_id", "job_id", "project_id", "output_uri", "created_at"):
        if not native.get(field):
            raise ValueError(f"Native ParaCut RenderPlan requires {field}")

    expected_transfer_id = f"paracut-waveforge:{native['plan_id']}"
    if bridge.get("transferId") != expected_transfer_id:
        raise ValueError("transferId does not match native ParaCut plan_id")

    plan_revision = _plan_revision(bridge)
    source_content_hash = bridge.get("contentHash")
    if source_content_hash is not None and not _SHA256.match(str(source_content_hash)):
        raise ValueError("contentHash must be null or sha256:<64 hex>")
    if source_content_hash is not None:
        expected_native_hash = f"sha256:{sha256_digest(native)}"
        if str(source_content_hash).lower() != expected_native_hash:
            raise ValueError("contentHash does not match canonical native ParaCut RenderPlan")

    intake = {
        "schema": "waveforge.paracut_bridge_intake.v1_alpha",
        "project": "WaveForgeStudio",
        "source_system": "ParaCut",
        "source_bridge_schema": "parallax.bridge.v1",
        "transfer_id": bridge.get("transferId"),
        "received_at": bridge.get("createdAt"),
        "source_content_hash": source_content_hash,
        "bridge_hash": sha256_digest(bridge),
        "render_plan": native,
        "lineage": {
            "source_project_id": native["project_id"],
            "source_job_id": native["job_id"],
            "source_plan_id": native["plan_id"],
        },
        "warnings": list(bridge.get("warnings") or []),
        "safety": {
            "reference_only": True,
            "handoff_only": True,
            "requires_user_action": True,
            "external_calls_allowed": False,
            "subprocess_allowed": False,
            "network_allowed": False,
            "real_rendering_allowed": False,
            "auto_import_into_media_packet": False,
        },
    }
    if plan_revision is not None:
        intake["plan_revision"] = plan_revision
    intake["receipt"] = {
        "schema": "waveforge.paracut_bridge_intake_receipt.v1_alpha",
        "intake_hash": sha256_digest(intake),
        "bridge_hash": intake["bridge_hash"],
        "source_content_hash": source_content_hash,
        "created_at": bridge.get("createdAt"),
    }
    return intake



def _assert_sha256(value: Any, label: str) -> str:
    text = str(value or "")
    if not _SHA256.match(text):
        raise ValueError(f"{label} must be sha256:<64 hex>")
    return text.lower()


def _validate_creative_lineage_v2(lineage: Any) -> dict[str, Any]:
    if not isinstance(lineage, dict):
        raise ValueError("Creative Interop v2 requires creativeLineage")
    if lineage.get("profile") != "parallax.creative-interop.v2":
        raise ValueError("creativeLineage.profile must be parallax.creative-interop.v2")
    if lineage.get("sourceBridgeSchema") != "parallax.bridge.v2":
        raise ValueError("creativeLineage.sourceBridgeSchema must be parallax.bridge.v2")
    if not lineage.get("sourceTransferId"):
        raise ValueError("creativeLineage.sourceTransferId required")

    normalized = dict(lineage)
    normalized["creativeManifestHash"] = _assert_sha256(
        lineage.get("creativeManifestHash"), "creativeLineage.creativeManifestHash"
    )
    normalized["baseContentHash"] = _assert_sha256(
        lineage.get("baseContentHash"), "creativeLineage.baseContentHash"
    )

    overlay_hashes = lineage.get("overlayContentHashes")
    count = lineage.get("semanticOverlayCount")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0 or count > 16:
        raise ValueError("creativeLineage.semanticOverlayCount must be an integer from 0 to 16")
    if not isinstance(overlay_hashes, list) or len(overlay_hashes) != count:
        raise ValueError("creativeLineage overlay hash count must match semanticOverlayCount")
    normalized["overlayContentHashes"] = [
        _assert_sha256(value, "creativeLineage.overlayContentHashes") for value in overlay_hashes
    ]

    for field in ("auralithCaptureHash", "auralithReceiptHash"):
        if field in lineage:
            normalized[field] = _assert_sha256(lineage.get(field), f"creativeLineage.{field}")

    asset_hashes = lineage.get("paraCutAssetHashes")
    if asset_hashes is not None:
        if not isinstance(asset_hashes, list):
            raise ValueError("creativeLineage.paraCutAssetHashes must be a list")
        normalized["paraCutAssetHashes"] = [
            _assert_sha256(value, "creativeLineage.paraCutAssetHashes") for value in asset_hashes
        ]

    return normalized


def _create_paracut_bridge_intake_v2(bridge: dict[str, Any]) -> dict[str, Any]:
    if bridge.get("schema") != "parallax.bridge.v2":
        raise ValueError("Expected parallax.bridge.v2")
    if bridge.get("protocol") != "parallax-bridge" or bridge.get("version") != 2:
        raise ValueError("Unsupported Parallax bridge protocol/version")
    if bridge.get("interopProfile") != "parallax.creative-interop.v2":
        raise ValueError("Expected parallax.creative-interop.v2 profile")
    if bridge.get("source") != "ParaCut" or bridge.get("target") != "WaveForgeStudio":
        raise ValueError("Unsupported bridge route")
    if bridge.get("localOnly") is not True:
        raise ValueError("ParaCut bridge must remain local-only")
    if bridge.get("requiresUserAction") is not True:
        raise ValueError("ParaCut bridge must require explicit user action")
    if bridge.get("payloadType") != "application/vnd.paracut.render-plan+json":
        raise ValueError("Unsupported ParaCut payload type")

    authority = bridge.get("authority")
    if not isinstance(authority, dict):
        raise ValueError("Creative Interop v2 requires explicit authority block")
    for key in (
        "realRenderingAuthorized",
        "networkAuthorized",
        "subprocessAuthorized",
        "automaticImportAuthorized",
        "publishAuthorized",
    ):
        if authority.get(key) is not False:
            raise ValueError(f"authority.{key} must be false")

    native = (bridge.get("payloadRefOrInline") or {}).get("native")
    if not isinstance(native, dict):
        raise ValueError("Native ParaCut RenderPlan payload is required")
    for field in ("plan_id", "job_id", "project_id", "output_uri", "created_at"):
        if not native.get(field):
            raise ValueError(f"Native ParaCut RenderPlan requires {field}")

    expected_transfer_id = f"paracut-waveforge-v2:{native['plan_id']}"
    if bridge.get("transferId") != expected_transfer_id:
        raise ValueError("transferId does not match native ParaCut plan_id")

    revision = _plan_revision(bridge)
    if revision is None:
        raise ValueError("Creative Interop v2 requires planRevision")

    source_content_hash = _assert_sha256(bridge.get("contentHash"), "contentHash")
    expected_native_hash = f"sha256:{sha256_digest(native)}"
    if source_content_hash != expected_native_hash:
        raise ValueError("contentHash does not match canonical native ParaCut RenderPlan")

    lineage = _validate_creative_lineage_v2(bridge.get("creativeLineage"))
    lineage_ref = bridge.get("lineageRef")
    if lineage_ref != lineage["creativeManifestHash"]:
        raise ValueError("lineageRef must equal creativeLineage.creativeManifestHash")

    creative_lineage_hash = f"sha256:{sha256_digest(lineage)}"
    intake = {
        "schema": "waveforge.paracut_bridge_intake.v2_alpha",
        "project": "WaveForgeStudio",
        "source_system": "ParaCut",
        "source_bridge_schema": "parallax.bridge.v2",
        "interop_profile": "parallax.creative-interop.v2",
        "transfer_id": bridge.get("transferId"),
        "received_at": bridge.get("createdAt"),
        "source_content_hash": source_content_hash,
        "bridge_hash": sha256_digest(bridge),
        "render_plan": native,
        "plan_revision": revision,
        "creative_lineage": lineage,
        "creative_lineage_hash": creative_lineage_hash,
        "lineage": {
            "source_project_id": native["project_id"],
            "source_job_id": native["job_id"],
            "source_plan_id": native["plan_id"],
            "creative_manifest_hash": lineage["creativeManifestHash"],
        },
        "warnings": list(bridge.get("warnings") or []),
        "safety": {
            "reference_only": True,
            "handoff_only": True,
            "requires_user_action": True,
            "external_calls_allowed": False,
            "subprocess_allowed": False,
            "network_allowed": False,
            "real_rendering_allowed": False,
            "auto_import_into_media_packet": False,
            "publish_allowed": False,
        },
    }
    receipt_bound = dict(intake)
    intake["receipt"] = {
        "schema": "waveforge.paracut_bridge_intake_receipt.v2_alpha",
        "intake_hash": sha256_digest(receipt_bound),
        "bridge_hash": intake["bridge_hash"],
        "source_content_hash": source_content_hash,
        "creative_lineage_hash": creative_lineage_hash,
        "creative_manifest_hash": lineage["creativeManifestHash"],
        "created_at": bridge.get("createdAt"),
    }
    return intake


def create_paracut_bridge_intake(bridge: dict[str, Any]) -> dict[str, Any]:
    if bridge.get("schema") == "parallax.bridge.v2" or bridge.get("version") == 2:
        return _create_paracut_bridge_intake_v2(bridge)
    return _create_paracut_bridge_intake_v1(bridge)

def accept_paracut_bridge_revision(
    bridge: dict[str, Any],
    accepted_revisions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Validate a bridge and apply consumer-owned monotonic freshness state.

    The caller owns ``accepted_revisions``. Exact replay of the same revision and
    bridge hash is idempotent. Lower revisions and same-revision/different-hash
    equivocation fail closed.
    """

    intake = create_paracut_bridge_intake(bridge)
    revision = _plan_revision(bridge)
    if revision is None:
        raise ValueError("freshness-aware intake requires planRevision")

    plan = intake["render_plan"]
    project_id = str(plan["project_id"])
    bridge_hash = str(intake["bridge_hash"])
    current = accepted_revisions.get(project_id)

    if current is not None:
        current_revision = int(current["plan_revision"])
        current_hash = str(current["bridge_hash"])
        if revision < current_revision:
            raise ValueError(
                f"stale plan revision {revision}; highest accepted revision is {current_revision}"
            )
        if revision == current_revision:
            if bridge_hash != current_hash:
                raise ValueError("same planRevision carries different bridge content")
            return {
                "status": "replay",
                "project_id": project_id,
                "plan_revision": revision,
                "bridge_hash": bridge_hash,
                "intake": intake,
            }

    record = {
        "plan_revision": revision,
        "plan_id": str(plan["plan_id"]),
        "bridge_hash": bridge_hash,
    }
    accepted_revisions[project_id] = record
    return {
        "status": "accepted",
        "project_id": project_id,
        "plan_revision": revision,
        "bridge_hash": bridge_hash,
        "record": record,
        "intake": intake,
    }


def validate_paracut_bridge_intake(intake: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if intake.get("schema") != "waveforge.paracut_bridge_intake.v1_alpha":
        errors.append("schema invalid")
    if intake.get("source_system") != "ParaCut":
        errors.append("source_system must be ParaCut")
    if not intake.get("bridge_hash"):
        errors.append("bridge_hash required")
    plan_revision = intake.get("plan_revision")
    if plan_revision is not None and (
        isinstance(plan_revision, bool) or not isinstance(plan_revision, int) or plan_revision < 1
    ):
        errors.append("plan_revision must be a positive integer")
    render_plan = intake.get("render_plan")
    if not isinstance(render_plan, dict):
        errors.append("render_plan required")
    else:
        expected_transfer_id = f"paracut-waveforge:{render_plan.get('plan_id')}"
        if intake.get("transfer_id") != expected_transfer_id:
            errors.append("transfer_id does not match render_plan.plan_id")
        source_content_hash = intake.get("source_content_hash")
        if source_content_hash is not None:
            expected_native_hash = f"sha256:{sha256_digest(render_plan)}"
            if str(source_content_hash).lower() != expected_native_hash:
                errors.append("source_content_hash does not match canonical render_plan")

    safety = intake.get("safety") or {}
    for key in (
        "reference_only",
        "handoff_only",
        "requires_user_action",
    ):
        if safety.get(key) is not True:
            errors.append(f"safety.{key} must be true")
    for key in (
        "external_calls_allowed",
        "subprocess_allowed",
        "network_allowed",
        "real_rendering_allowed",
        "auto_import_into_media_packet",
    ):
        if safety.get(key) is not False:
            errors.append(f"safety.{key} must be false")

    receipt = intake.get("receipt") or {}
    if not receipt.get("intake_hash"):
        errors.append("receipt.intake_hash required")
    else:
        receipt_bound_intake = {key: value for key, value in intake.items() if key != "receipt"}
        if receipt.get("intake_hash") != sha256_digest(receipt_bound_intake):
            errors.append("receipt.intake_hash does not match intake contents")
    if receipt.get("bridge_hash") != intake.get("bridge_hash"):
        errors.append("receipt.bridge_hash does not match intake.bridge_hash")
    if receipt.get("source_content_hash") != intake.get("source_content_hash"):
        errors.append("receipt.source_content_hash does not match intake.source_content_hash")

    return errors


def assert_valid_paracut_bridge_intake(intake: dict[str, Any]) -> None:
    errors = validate_paracut_bridge_intake(intake)
    if errors:
        raise ValueError("Invalid ParaCut bridge intake: " + "; ".join(errors))
