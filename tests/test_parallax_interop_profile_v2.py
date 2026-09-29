from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_parallax_creative_interop_v2_manifest_binds_frozen_spec_text():
    spec = (ROOT / "docs" / "PARALLAX_CREATIVE_INTEROP_V2.md").read_bytes()
    manifest = json.loads((ROOT / "parallax-creative-interop.v2.json").read_text(encoding="utf-8"))

    actual = hashlib.sha256(spec).hexdigest()
    assert actual == manifest["spec_sha256"]
    assert manifest["protocol_id"] == "parallax.creative-interop.v2"
    assert manifest["status"] == "candidate_pending_repository_ratification"
    assert manifest["optional_extensions"][0]["status"] == "unratified_receiver"
    assert manifest["canonical_owned_scope"] == [
        "MichaelWave369/Domistika",
        "MichaelWave369/Auralith369",
        "MichaelWave369/paracut",
        "MichaelWave369/WaveForgeStudio",
    ]
