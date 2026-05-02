from waveforge_studio.media_packet import create_media_packet


def test_sync_lattice_contains_nine_events():
    p = create_media_packet("hello")
    assert len(p["sync"]["events"]) == 9
