from __future__ import annotations
import json
from pathlib import Path
from .hashing import canonical_json, sha256_digest
from .signature_envelope import create_signature_envelope, write_signature_envelope

_STABLE_TS = "1979-03-06T03:06:09Z"


def create_detached_signature_manifest(final_dir: str | Path, algorithm_hint: str = "future-ed25519-detached") -> dict:
    final_path = Path(final_dir)
    ep = final_path / "signature_envelope.json"
    envelope = json.loads(ep.read_text(encoding="utf-8")) if ep.exists() else create_signature_envelope(final_path)
    payload_hash = envelope.get("signing_payload", {}).get("payload_hash")
    envelope_hash = envelope.get("receipt", {}).get("signature_envelope_hash")
    warnings = ["Dry-run manifest only; no cryptographic signature was created."]
    if not payload_hash:
        warnings = warnings + ["Signature envelope payload hash missing; manifest marked incomplete."]
    m = {
        "schema": "waveforge.detached_signature_manifest.v3_alpha",
        "project": "WaveForgeStudio",
        "version": "3.2-alpha",
        "final_root": ".",
        "signature_status": "unsigned_dry_run" if payload_hash else "incomplete",
        "detached_signature_policy": {"dry_run_only": True, "signing_manifest": True, "cryptographic_signature": False, "private_key_handling": False, "public_key_verification": False, "external_transparency_log": False, "legal_certificate": False, "external_calls_allowed": False, "subprocess_allowed": False, "network_allowed": False, "hosting": False, "browser_automation": False},
        "source": {"signature_envelope": {"path": "signature_envelope.json", "present": bool(envelope), "signature_envelope_hash": envelope_hash, "payload_hash": payload_hash}},
        "signing_request": {"algorithm_hint": algorithm_hint, "canonicalization": "waveforge.canonical_json.sorted.v1", "payload_hash": payload_hash, "payload_source": "signature_envelope.signing_payload.fields", "detached_signature_target": "detached_signature.sig", "public_key_id_target": "public_key_id.txt"},
        "signature": {"status": "unsigned_dry_run", "signature_algorithm": None, "public_key_id": None, "signature_value": None, "signed_at": None, "signature_file": None, "verification_status": None},
        "warnings": warnings,
        "limitations": ["Detached signature manifest only; not cryptographically signed.", "No private keys are handled.", "No public-key verification is performed.", "No external transparency log is used.", "No legal certification is implied."],
        "outputs": {"manifest": "detached_signature_manifest.json", "receipt": "detached_signature_receipt.json", "markdown": "DETACHED_SIGNATURE.md"},
    }
    mhash = sha256_digest(json.loads(canonical_json(m)))
    m["receipt"] = {"schema": "waveforge.detached_signature_receipt.v3_alpha", "detached_signature_manifest_hash": mhash, "created_at": _STABLE_TS}
    return m


def write_detached_signature_manifest(final_dir: str | Path, algorithm_hint: str = "future-ed25519-detached") -> dict:
    final_path = Path(final_dir)
    if not (final_path / "signature_envelope.json").exists():
        write_signature_envelope(final_path)
    m = create_detached_signature_manifest(final_path, algorithm_hint=algorithm_hint)
    (final_path / "detached_signature_manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    (final_path / "detached_signature_receipt.json").write_text(json.dumps(m["receipt"], indent=2, sort_keys=True), encoding="utf-8")
    (final_path / "DETACHED_SIGNATURE.md").write_text(
        "# WaveForgeStudio Detached Signature Manifest\n\n"
        f"- Signature Status: {m['signature_status']}\n"
        f"- Algorithm Hint: {m['signing_request']['algorithm_hint']}\n"
        f"- Payload Hash: {m['signing_request']['payload_hash']}\n"
        f"- Source Signature Envelope Hash: {m['source']['signature_envelope']['signature_envelope_hash']}\n"
        "- Unsigned Fields: signature_algorithm/public_key_id/signature_value/signed_at/signature_file = null\n"
        f"- Detached Signature Target: {m['signing_request']['detached_signature_target']}\n\n"
        "## Warnings\n" + "\n".join([f"- {w}" for w in m["warnings"]]) + "\n\n"
        "## Limitations\n" + "\n".join([f"- {x}" for x in m["limitations"]]) + "\n\n"
        "Dry-run only — no cryptographic signature was created.\n",
        encoding="utf-8",
    )
    return m


def validate_detached_signature_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get("schema")!="waveforge.detached_signature_manifest.v3_alpha": e.append("schema invalid")
    if manifest.get("version")!="3.2-alpha": e.append("version invalid")
    if manifest.get("signature_status") not in {"unsigned_dry_run","incomplete"}: e.append("signature_status invalid")
    p=manifest.get("detached_signature_policy",{})
    checks={"dry_run_only":True,"signing_manifest":True,"cryptographic_signature":False,"private_key_handling":False,"public_key_verification":False,"external_transparency_log":False,"legal_certificate":False,"external_calls_allowed":False,"subprocess_allowed":False,"network_allowed":False,"hosting":False,"browser_automation":False}
    for k,v in checks.items():
        if p.get(k) is not v: e.append(f"{k} must be {v}")
    if not manifest.get("source",{}).get("signature_envelope"): e.append("source.signature_envelope required")
    if not manifest.get("signing_request",{}).get("payload_hash"): e.append("signing_request.payload_hash required")
    s=manifest.get("signature",{})
    if s.get("status")!="unsigned_dry_run": e.append("signature.status invalid")
    if s.get("signature_value") is not None: e.append("signature.signature_value must be null")
    if s.get("signature_file") is not None: e.append("signature.signature_file must be null")
    if s.get("public_key_id") is not None: e.append("signature.public_key_id must be null")
    if not manifest.get("outputs",{}).get("manifest"): e.append("outputs.manifest required")
    if not manifest.get("receipt",{}).get("detached_signature_manifest_hash"): e.append("receipt.detached_signature_manifest_hash required")
    if not isinstance(manifest.get("limitations"), list): e.append("limitations must be list")
    src_path = manifest.get("source",{}).get("signature_envelope",{}).get("path")
    if src_path and Path(src_path).is_absolute(): e.append("source path must be relative")
    for _,v in (manifest.get("outputs") or {}).items():
        if isinstance(v,str) and Path(v).is_absolute(): e.append("output path must be relative")
    return e

def assert_valid_detached_signature_manifest(manifest: dict) -> None:
    err=validate_detached_signature_manifest(manifest)
    if err: raise ValueError("Invalid detached signature manifest: "+"; ".join(err))

def read_detached_signature_info(final_dir: str | Path) -> dict:
    f=Path(final_dir)
    mp=f/'detached_signature_manifest.json'; rp=f/'detached_signature_receipt.json'; md=f/'DETACHED_SIGNATURE.md'
    m=json.loads(mp.read_text(encoding='utf-8')) if mp.exists() else {}
    txt=md.read_text(encoding='utf-8',errors='ignore').lower() if md.exists() else ''
    return {"exists":f.exists(),"manifest_exists":mp.exists(),"receipt_exists":rp.exists(),"markdown_exists":md.exists(),"signature_status":m.get("signature_status") if m else None,"payload_hash":m.get("signing_request",{}).get("payload_hash") if m else None,"detached_signature_manifest_hash":m.get("receipt",{}).get("detached_signature_manifest_hash") if m else None,"contains_waveforge":"waveforge" in txt}
