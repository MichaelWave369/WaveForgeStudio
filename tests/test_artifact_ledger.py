from pathlib import Path

from waveforge_studio.artifact_ledger import create_artifact_ledger, file_sha256, write_artifact_ledger


def test_file_sha256_stable(tmp_path: Path):
    f = tmp_path / "a.txt"
    f.write_text("abc", encoding="utf-8")
    assert file_sha256(f) == file_sha256(f)


def test_ledger_schema_relative_and_deterministic(tmp_path: Path):
    (tmp_path / "x.txt").write_text("x", encoding="utf-8")
    l1 = create_artifact_ledger(tmp_path)
    l2 = create_artifact_ledger(tmp_path)
    assert l1["schema"] == "waveforge.artifact_ledger.v0"
    assert l1["receipt"]["ledger_hash"] == l2["receipt"]["ledger_hash"]
    assert all(not p["path"].startswith("/") for p in l1["files"])


def test_write_artifact_ledger(tmp_path: Path):
    (tmp_path / "x.txt").write_text("x", encoding="utf-8")
    write_artifact_ledger(tmp_path)
    for fn in ["artifact_ledger.json", "artifact_ledger_receipt.json", "ARTIFACT_LEDGER_SUMMARY.md"]:
        assert (tmp_path / fn).exists()
