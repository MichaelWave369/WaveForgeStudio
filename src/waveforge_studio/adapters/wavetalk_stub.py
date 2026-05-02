from __future__ import annotations

from .base import BaseAdapter
from .wavetalk_bridge import create_wavetalk_bundle


class WaveTalkStubAdapter(BaseAdapter):
    name = "wavetalk"
    kind = "governance"

    def render(self, manifest_or_packet: dict) -> dict:
        bundle = create_wavetalk_bundle(manifest_or_packet)
        return {
            "adapter": "WaveTalk",
            "status": "planned",
            "rendered": False,
            "bundle_schema": bundle["schema"],
            "bundle_hash": bundle["receipts"]["signal_receipt"]["bundle_hash"],
            "message": "WaveTalk bundle prepared; real signal runtime not implemented in v0.5.",
        }
