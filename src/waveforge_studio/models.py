from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class BaseModel:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class IntentPacket(BaseModel):
    prompt: str
    archetype: str
    purpose: str


@dataclass
class StructurePacket(BaseModel):
    pattern: str
    phi: float
    lambda_value: float
    c_star: float
    omega_c: float
    fib_timing: list[float] = field(default_factory=list)


@dataclass
class AudioGraph(BaseModel):
    tempo_bpm: int
    key: str
    sections: list[dict[str, Any]]
    stems: list[str]
    voiceover_cues: list[dict[str, Any]]
    sonic_palette: list[str]


@dataclass
class VisualGraph(BaseModel):
    scenes: list[dict[str, Any]]
    shots: list[dict[str, Any]]
    symbols: list[str]
    color_field: list[str]
    camera_motion: list[str]
    render_style: str


@dataclass
class SyncLattice(BaseModel):
    events: list[dict[str, Any]]
    beat_to_cut: list[dict[str, Any]]
    section_to_scene: list[dict[str, Any]]
    voice_to_symbol: list[dict[str, Any]]
    peak_to_reveal: list[dict[str, Any]]


@dataclass
class GovernancePacket(BaseModel):
    sgl_policy: str
    sml_lineage: list[str]
    continuity_mode: str


@dataclass
class Receipt(BaseModel):
    schema: str
    project: str
    seed: int
    created_at: str
    content_hash: str
    packet_hash: str
    coherence_passed: bool
    lineage: list[str]


@dataclass
class MediaPacket(BaseModel):
    schema: str
    project: str
    seed: int
    mode: str
    intent: dict[str, Any]
    structure: dict[str, Any]
    audio: dict[str, Any]
    visual: dict[str, Any]
    sync: dict[str, Any]
    governance: dict[str, Any]
    receipt: dict[str, Any]


@dataclass
class RenderManifest(BaseModel):
    schema: str
    project: str
    seed: int
    audio_render: str
    video_render: str
    final_artifact: str
    required_outputs: list[str]
