# Detached Signature Manifest

Dry-run only detached signing manifest derived from signature envelope payload hash.

- purpose: prepare future Ed25519 detached signing inputs
- relationship: consumes signature_envelope signing payload hash
- fields: algorithm hint, payload hash, source envelope hash, target signature file paths
- signature fields remain unsigned/null

Generated files:
- detached_signature_manifest.json
- detached_signature_receipt.json
- DETACHED_SIGNATURE.md

CLI:
```bash
python -m waveforge_studio.cli detached-signature runs/final_release
python -m waveforge_studio.cli detached-signature-validate runs/final_release/detached_signature_manifest.json
python -m waveforge_studio.cli finalize-release runs --out runs/final_release_signing_dry_run --title "Golden Signal Release" --include-tag has-zip --signature-envelope --detached-signature
```

Limitations:
- dry-run only
- not cryptographically signed
- no private keys
- no public-key verification
- no external transparency log
- no legal certification
