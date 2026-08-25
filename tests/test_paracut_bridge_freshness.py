from __future__ import annotations

import copy

import pytest

from waveforge_studio.adapters.paracut_bridge import (
    accept_paracut_bridge_revision,
    create_paracut_bridge_intake,
)
from waveforge_studio.hashing import sha256_digest


def _bridge(revision: int | None, *, plan_id: str = "plan_rev_005", output_uri: str = "./exports/rev5.mp4") -> dict:
    native = {
        "plan_id": plan_id,
        "job_id": f"job_{plan_id}",
        "project_id": "project_freshness",
        "output_uri": output_uri,
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
        "created_at": "2026-08-25T22:40:00Z",
    }
    bridge = {
        "schema": "parallax.bridge.v1",
        "protocol": "parallax-bridge",
        "version": 1,
        "transferId": f"paracut-waveforge:{plan_id}",
        "source": "ParaCut",
        "target": "WaveForgeStudio",
        "createdAt": "2026-08-25T22:40:00Z",
        "localOnly": True,
        "payloadType": "application/vnd.paracut.render-plan+json",
        "payloadRefOrInline": {"native": native},
        "contentHash": f"sha256:{sha256_digest(native)}",
        "trustLabels": [],
        "warnings": [],
        "compatibilityNotes": ["Reference-only handoff; not render authorization."],
        "lineageRef": None,
        "requiresUserAction": True,
    }
    if revision is not None:
        bridge["planRevision"] = revision
    return bridge


def test_legacy_bridge_remains_valid_without_freshness_metadata():
    intake = create_paracut_bridge_intake(_bridge(None))
    assert "plan_revision" not in intake
    assert intake["safety"]["real_rendering_allowed"] is False


def test_freshness_aware_intake_requires_revision():
    with pytest.raises(ValueError, match="requires planRevision"):
        accept_paracut_bridge_revision(_bridge(None), {})


def test_newer_revision_accepts_exact_replay_is_idempotent_and_rollback_fails():
    ledger: dict[str, dict] = {}

    revision_5 = _bridge(5)
    accepted = accept_paracut_bridge_revision(revision_5, ledger)
    assert accepted["status"] == "accepted"
    assert ledger["project_freshness"]["plan_revision"] == 5

    replay = accept_paracut_bridge_revision(copy.deepcopy(revision_5), ledger)
    assert replay["status"] == "replay"
    assert replay["bridge_hash"] == accepted["bridge_hash"]
    assert ledger["project_freshness"]["plan_revision"] == 5

    revision_4 = _bridge(4, plan_id="plan_rev_004", output_uri="./exports/rev4.mp4")
    with pytest.raises(ValueError, match="stale plan revision 4"):
        accept_paracut_bridge_revision(revision_4, ledger)

    assert ledger["project_freshness"]["plan_revision"] == 5


def test_same_revision_with_different_valid_content_is_equivocation():
    ledger: dict[str, dict] = {}
    accept_paracut_bridge_revision(_bridge(5), ledger)

    conflicting = _bridge(5, plan_id="plan_rev_005_conflict", output_uri="./exports/conflict.mp4")
    with pytest.raises(ValueError, match="same planRevision carries different bridge content"):
        accept_paracut_bridge_revision(conflicting, ledger)


def test_higher_revision_advances_consumer_owned_ledger():
    ledger: dict[str, dict] = {}
    accept_paracut_bridge_revision(_bridge(5), ledger)
    result = accept_paracut_bridge_revision(
        _bridge(6, plan_id="plan_rev_006", output_uri="./exports/rev6.mp4"),
        ledger,
    )
    assert result["status"] == "accepted"
    assert ledger["project_freshness"]["plan_revision"] == 6
    assert ledger["project_freshness"]["plan_id"] == "plan_rev_006"


@pytest.mark.parametrize("bad_revision", [0, -1, True, 1.5])
def test_invalid_revision_values_fail_closed(bad_revision):
    bridge = _bridge(None)
    bridge["planRevision"] = bad_revision
    with pytest.raises(ValueError, match="positive integer"):
        create_paracut_bridge_intake(bridge)
