from __future__ import annotations

from .coherence import score_media_coherence
from .hashing import sha256_digest


def create_receipt(packet: dict, created_at: str = "1979-03-06T03:06:09Z") -> dict:
    content = {
        "intent": packet.get("intent"),
        "structure": packet.get("structure"),
        "audio": packet.get("audio"),
        "visual": packet.get("visual"),
        "sync": packet.get("sync"),
    }
    coherence = score_media_coherence(packet)
    return {
        "schema": "waveforge.receipt.v0",
        "project": packet.get("project", "WaveForgeStudio"),
        "seed": packet.get("seed"),
        "created_at": created_at,
        "content_hash": sha256_digest(content),
        "packet_hash": sha256_digest(packet),
        "coherence_passed": coherence["passed"],
        "lineage": ["wavetalk.sgl", "waverider.graph", "phiaudio.plan"],
    }
