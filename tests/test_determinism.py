from waveforge_studio.hashing import sha256_digest
from waveforge_studio.media_packet import create_media_packet


def test_same_input_same_packet_hash():
    p1 = create_media_packet("x", seed=369369)
    p2 = create_media_packet("x", seed=369369)
    assert sha256_digest(p1) == sha256_digest(p2)


def test_different_seed_changes_packet_hash():
    p1 = create_media_packet("x", seed=369369)
    p2 = create_media_packet("x", seed=369370)
    assert sha256_digest(p1) != sha256_digest(p2)
