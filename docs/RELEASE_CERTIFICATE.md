# Release Certificate

Deterministic human-readable certificate derived from release build + verification outputs.

## Summary
- release title
- release/verification hashes
- release build ZIP sha256
- selected run and deck counts
- verification status and strict mode

## Statuses
- `certified`
- `certified_with_warnings`
- `not_certified`

## require-passed behavior
Use `--require-passed` to force nonzero exit when verification did not pass.

## Generated files
- `release_certificate.json`
- `release_certificate_receipt.json`
- `RELEASE_CERTIFICATE.md`

## CLI
```bash
python -m waveforge_studio.cli certify-release-build runs/release_build_zip_verify
python -m waveforge_studio.cli certify-release-build runs/release_build_zip_verify --require-passed
python -m waveforge_studio.cli release-certificate-validate runs/release_build_zip_verify/release_certificate.json
python -m waveforge_studio.cli release-build runs --out runs/release_build_certified --title "Golden Signal Release" --include-tag has-zip --zip --verify --certify
```

## Limitations
- not cryptographic signing
- no external transparency log
- no legal certification
- local verification only
