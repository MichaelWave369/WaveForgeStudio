from __future__ import annotations

from .comfyui_stub import ComfyUIStubAdapter
from .phiaudio_stub import PHIAudioStubAdapter
from .phios_stub import PhiOSStubAdapter
from .waverider_stub import WaveRiderStubAdapter
from .wavetalk_stub import WaveTalkStubAdapter


_ADAPTERS = {
    "phiaudio": PHIAudioStubAdapter(),
    "wavetalk": WaveTalkStubAdapter(),
    "waverider": WaveRiderStubAdapter(),
    "comfyui": ComfyUIStubAdapter(),
    "phios": PhiOSStubAdapter(),
}


def list_adapters() -> list[dict]:
    return [a.describe() for _, a in sorted(_ADAPTERS.items())]


def get_adapter(name: str):
    return _ADAPTERS.get(name.lower())
