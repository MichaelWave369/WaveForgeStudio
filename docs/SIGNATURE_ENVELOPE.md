# Signature Envelope

Purpose: deterministic signing-ready envelope for final releases.

- gathers final release hash and key artifact hashes
- builds canonical signing payload fields
- leaves signature fields unsigned/null for future detached signatures

Generated files:
- signature_envelope.json
- signature_envelope_receipt.json
- SIGNATURE_ENVELOPE.md

CLI:
```bash
python -m waveforge_studio.cli signature-envelope runs/final_release
python -m waveforge_studio.cli signature-envelope-validate runs/final_release/signature_envelope.json
python -m waveforge_studio.cli finalize-release runs --out runs/final_release --title "Golden Signal Release" --include-tag has-zip --signature-envelope
```

Limitations:
- not cryptographically signed
- no private keys
- no public-key verification
- no external transparency log
- no legal certification
