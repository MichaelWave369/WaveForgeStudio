from __future__ import annotations

import re
from typing import Any

from ..hashing import sha256_digest

_SHA256 = re.compile(r"^sha256:[0-9a-fA-F]{64}$")


def create_paracut_bridge_intake(bridge: dict[str, Any]) -> dict[str, Any]:
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
    intake["receipt"] = {
        "schema": "waveforge.paracut_bridge_intake_receipt.v1_alpha",
        "intake_hash": sha256_digest(intake),
        "bridge_hash": intake["bridge_hash"],
        "source_content_hash": source_content_hash,
        "created_at": bridge.get("createdAt"),
    }
    return intake


def validate_paracut_bridge_intake(intake: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if intake.get("schema") != "waveforge.paracut_bridge_intake.v1_alpha":
        errors.append("schema invalid")
    if intake.get("source_system") != "ParaCut":
        errors.append("source_system must be ParaCut")
    if not intake.get("bridge_hash"):
        errors.append("bridge_hash required")
    render_plan = intake.get("render_plan")
    if not isinstance(render_plan, dict):
        errors.append("render_plan required")
    else:
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
