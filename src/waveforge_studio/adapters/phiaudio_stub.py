from __future__ import annotations

from .base import BaseAdapter
from .phiaudio_bridge import create_phiaudio_bundle


class PHIAudioStubAdapter(BaseAdapter):
    name = "phiaudio"
    kind = "audio"

    def render(self, manifest_or_packet: dict) -> dict:
        bundle = create_phiaudio_bundle(manifest_or_packet)
        return {
            "adapter": "PHIAudio",
            "status": "planned",
            "rendered": False,
            "bundle_schema": bundle["schema"],
            "bundle_hash": bundle["receipt"]["bundle_hash"],
            "message": "PHIAudio bundle prepared; real rendering not implemented in v0.2.",
        }
