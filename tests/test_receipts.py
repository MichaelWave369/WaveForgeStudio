from waveforge_studio.media_packet import create_media_packet
from waveforge_studio.receipts import create_receipt


def test_receipt_content_hash_stable():
    p = create_media_packet("hello")
    r1 = create_receipt(p, created_at="1979-03-06T03:06:09Z")
    r2 = create_receipt(p, created_at="1979-03-06T03:06:09Z")
    assert r1["content_hash"] == r2["content_hash"]
