from __future__ import annotations


class BaseAdapter:
    name: str = "base"
    kind: str = "generic"

    def available(self) -> bool:
        return False

    def describe(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind,
            "available": self.available(),
            "mode": "stub",
        }

    def render(self, manifest: dict) -> dict:
        return {
            "adapter": self.name,
            "status": "stub",
            "rendered": False,
        }
