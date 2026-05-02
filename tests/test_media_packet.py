from waveforge_studio.constants import C_STAR
from waveforge_studio.coherence import score_media_coherence
from waveforge_studio.media_packet import create_media_packet


def test_default_packet_sections_present():
    p = create_media_packet("hello")
    for k in ["audio", "visual", "sync", "governance", "receipt"]:
        assert k in p


def test_default_coherence_passes():
    p = create_media_packet("hello")
    s = score_media_coherence(p)
    assert s["overall"] >= C_STAR
    assert s["passed"] is True
