from __future__ import annotations

import json
from pathlib import Path

from .artifact_ledger import file_sha256
from .command_inventory import create_command_inventory
from .hashing import canonical_json, sha256_digest
from .schema_registry import list_schemas

_STABLE_TS = "1979-03-06T03:06:09Z"


def _load_json(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _rel(path: str) -> str:
    return Path(path).as_posix()


def _artifact_file(final_dir: Path, rel_path: str) -> tuple[bool, str | None]:
    full = final_dir / rel_path
    return full.exists(), file_sha256(full) if full.exists() else None


def create_signature_envelope(final_dir: str | Path) -> dict:
    final_path = Path(final_dir)
    final_manifest = _load_json(final_path / "final_release_manifest.json")
    final_receipt = _load_json(final_path / "final_release_receipt.json")
    verification = _load_json(final_path / "release_build_verification.json")
    certificate = _load_json(final_path / "release_certificate.json")
    command_inventory = create_command_inventory()
    schema_inventory = {"schema": "waveforge.schema_registry_inventory.v1_alpha", "schemas": sorted(list_schemas(), key=lambda x: x["name"])}
    schema_registry_hash = sha256_digest(json.loads(canonical_json(schema_inventory)))

    rb_zip_present, rb_zip_sha = _artifact_file(final_path, "release_build.zip")
    cb_zip_present, cb_zip_sha = _artifact_file(final_path, "certificate_bundle/certificate_bundle.zip")
    fm_present, fm_sha = _artifact_file(final_path, "final_release_manifest.json")

    fields = {
        "final_release_hash": (final_receipt or {}).get("final_release_hash"),
        "release_build_zip_sha256": rb_zip_sha,
        "certificate_bundle_zip_sha256": cb_zip_sha,
        "verification_hash": (verification or {}).get("receipt", {}).get("verification_hash"),
        "certificate_hash": (certificate or {}).get("receipt", {}).get("release_certificate_hash"),
        "command_inventory_hash": command_inventory["receipt"]["command_inventory_hash"],
        "schema_registry_hash": schema_registry_hash,
    }
    payload_hash = sha256_digest(json.loads(canonical_json(fields)))

    envelope = {
        "schema": "waveforge.signature_envelope.v3_alpha",
        "project": "WaveForgeStudio",
        "version": "3.1-alpha",
        "final_root": ".",
        "envelope_status": "unsigned" if fm_present else "incomplete",
        "signature_policy": {
            "signing_ready_payload": True,
            "cryptographic_signature": False,
            "private_key_handling": False,
            "public_key_verification": False,
            "external_transparency_log": False,
            "legal_certificate": False,
            "external_calls_allowed": False,
            "subprocess_allowed": False,
            "network_allowed": False,
            "hosting": False,
            "browser_automation": False,
        },
        "source_artifacts": {
            "final_release_manifest": {"path": _rel("final_release_manifest.json"), "present": fm_present, "sha256": fm_sha, "receipt_hash": (final_receipt or {}).get("final_release_hash")},
            "release_build_zip": {"path": _rel("release_build.zip"), "present": rb_zip_present, "sha256": rb_zip_sha},
            "certificate_bundle_zip": {"path": _rel("certificate_bundle/certificate_bundle.zip"), "present": cb_zip_present, "sha256": cb_zip_sha},
            "verification_report": {"path": _rel("release_build_verification.json"), "present": verification is not None, "verification_hash": (verification or {}).get("receipt", {}).get("verification_hash")},
            "release_certificate": {"path": _rel("release_certificate.json"), "present": certificate is not None, "certificate_hash": (certificate or {}).get("receipt", {}).get("release_certificate_hash")},
            "command_inventory": {"path": None, "present": True, "command_inventory_hash": command_inventory["receipt"]["command_inventory_hash"]},
            "schema_registry": {"path": None, "present": True, "schema_registry_hash": schema_registry_hash},
        },
        "signing_payload": {
            "algorithm_hint": "future-ed25519-detached",
            "canonicalization": "waveforge.canonical_json.sorted.v1",
            "payload_hash": payload_hash,
            "fields": fields,
        },
        "signature": {"status": "unsigned", "signature_algorithm": None, "public_key_id": None, "signature_value": None, "signed_at": None, "signature_receipt": None},
        "limitations": [
            "Signing-ready envelope only; not cryptographically signed.",
            "No private keys are handled.",
            "No public-key verification is performed.",
            "No external transparency log is used.",
            "No legal certification is implied.",
        ],
        "outputs": {"envelope": "signature_envelope.json", "receipt": "signature_envelope_receipt.json", "markdown": "SIGNATURE_ENVELOPE.md"},
    }
    envelope_hash = sha256_digest(json.loads(canonical_json(envelope)))
    envelope["receipt"] = {"schema": "waveforge.signature_envelope_receipt.v3_alpha", "signature_envelope_hash": envelope_hash, "created_at": _STABLE_TS}
    return envelope


def write_signature_envelope(final_dir: str | Path) -> dict:
    final_path = Path(final_dir)
    final_path.mkdir(parents=True, exist_ok=True)
    envelope = create_signature_envelope(final_path)
    (final_path / "signature_envelope.json").write_text(json.dumps(envelope, indent=2, sort_keys=True), encoding="utf-8")
    (final_path / "signature_envelope_receipt.json").write_text(json.dumps(envelope["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    f = envelope["signing_payload"]["fields"]
    (final_path / "SIGNATURE_ENVELOPE.md").write_text(
        "# WaveForgeStudio Signature Envelope\n\n"
        f"- Envelope Status: {envelope['envelope_status']}\n"
        f"- Payload Hash: {envelope['signing_payload']['payload_hash']}\n"
        f"- Final Release Hash: {f['final_release_hash']}\n"
        f"- release_build.zip sha256: {f['release_build_zip_sha256']}\n"
        f"- certificate_bundle.zip sha256: {f['certificate_bundle_zip_sha256']}\n"
        f"- Verification Hash: {f['verification_hash']}\n"
        f"- Certificate Hash: {f['certificate_hash']}\n"
        f"- Command Inventory Hash: {f['command_inventory_hash']}\n"
        f"- Schema Registry Hash: {f['schema_registry_hash']}\n\n"
        "## Signature Fields (Unsigned)\n"
        "- signature_algorithm: null\n- public_key_id: null\n- signature_value: null\n- signed_at: null\n- signature_receipt: null\n\n"
        "## Limitations\n" + "\n".join([f"- {x}" for x in envelope["limitations"]]) + "\n\n"
        "Signing-ready envelope only — not cryptographically signed.\n",
        encoding="utf-8",
    )
    return envelope


def validate_signature_envelope(envelope: dict) -> list[str]:
    e = []
    if envelope.get("schema") != "waveforge.signature_envelope.v3_alpha": e.append("schema invalid")
    if envelope.get("version") != "3.1-alpha": e.append("version invalid")
    if envelope.get("envelope_status") not in {"unsigned", "incomplete"}: e.append("envelope_status invalid")
    p = envelope.get("signature_policy", {})
    checks = {"signing_ready_payload": True, "cryptographic_signature": False, "private_key_handling": False, "public_key_verification": False, "external_transparency_log": False, "legal_certificate": False, "external_calls_allowed": False, "subprocess_allowed": False, "network_allowed": False, "hosting": False, "browser_automation": False}
    for k, v in checks.items():
        if p.get(k) is not v: e.append(f"{k} must be {v}")
    if not envelope.get("source_artifacts"): e.append("source_artifacts required")
    if not envelope.get("signing_payload", {}).get("payload_hash"): e.append("signing_payload.payload_hash required")
    if envelope.get("signature", {}).get("status") != "unsigned": e.append("signature.status invalid")
    if envelope.get("signature", {}).get("signature_value") is not None: e.append("signature.signature_value must be null")
    if not envelope.get("outputs", {}).get("envelope"): e.append("outputs.envelope required")
    if not envelope.get("receipt", {}).get("signature_envelope_hash"): e.append("receipt.signature_envelope_hash required")
    if not isinstance(envelope.get("limitations"), list): e.append("limitations must be list")
    for _, artifact in (envelope.get("source_artifacts") or {}).items():
        path = artifact.get("path") if isinstance(artifact, dict) else None
        if path and Path(path).is_absolute(): e.append("source artifact path must be relative")
    return e


def assert_valid_signature_envelope(envelope: dict) -> None:
    errors = validate_signature_envelope(envelope)
    if errors:
        raise ValueError("Invalid signature envelope: " + "; ".join(errors))


def read_signature_envelope_info(final_dir: str | Path) -> dict:
    f = Path(final_dir)
    ep = f / "signature_envelope.json"
    rp = f / "signature_envelope_receipt.json"
    mp = f / "SIGNATURE_ENVELOPE.md"
    envelope = _load_json(ep) if ep.exists() else {}
    txt = mp.read_text(encoding="utf-8", errors="ignore").lower() if mp.exists() else ""
    return {"exists": f.exists(), "envelope_exists": ep.exists(), "receipt_exists": rp.exists(), "markdown_exists": mp.exists(), "envelope_status": envelope.get("envelope_status") if envelope else None, "payload_hash": envelope.get("signing_payload", {}).get("payload_hash") if envelope else None, "signature_envelope_hash": envelope.get("receipt", {}).get("signature_envelope_hash") if envelope else None, "contains_waveforge": "waveforge" in txt}
