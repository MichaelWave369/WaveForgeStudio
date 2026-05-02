from __future__ import annotations

from .base import BaseAdapter
from .waverider_bridge import create_waverider_bundle


class WaveRiderStubAdapter(BaseAdapter):
    name = "waverider"
    kind = "visual"

    def render(self, manifest_or_packet: dict) -> dict:
        bundle = create_waverider_bundle(manifest_or_packet)
        return {
            "adapter": "WaveRider",
            "status": "planned",
            "rendered": False,
            "bundle_schema": bundle["schema"],
            "bundle_hash": bundle["receipt"]["bundle_hash"],
            "message": "WaveRider bundle prepared; real visual rendering not implemented in v0.3.",
        }
