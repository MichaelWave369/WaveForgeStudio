# Release Build Verification Report

Purpose: local end-to-end auditor report for an existing `release_build/` folder.

## What is checked
- manifests/receipts for release build, gallery, collection, collection export, release deck, release deck ZIP, and release build ZIP (if present)
- expected output file presence
- stage hash consistency checks
- ZIP sha256 consistency against receipts
- no absolute paths in known manifests
- safe/offline policy validation via existing validators

## Strict vs non-strict
- non-strict: missing `release_build.zip` without ZIP manifest is warning
- strict: requires `release_build.zip` and `release_build_zip_manifest.json`; unconfirmed/mismatched stage hashes fail

## Generated files
- `release_build_verification.json`
- `release_build_verification_receipt.json`
- `RELEASE_BUILD_VERIFICATION.md`

## CLI
```bash
python -m waveforge_studio.cli verify-release-build runs/release_build_zip_verify
python -m waveforge_studio.cli verify-release-build runs/release_build_zip_verify --strict
python -m waveforge_studio.cli release-build-verification-validate runs/release_build_zip_verify/release_build_verification.json
python -m waveforge_studio.cli release-build runs --out runs/release_build_zip_verify --title "Golden Signal Release" --include-tag has-zip --zip --verify
```

## Limitations
- local verification only
- no external services
- no runtime execution
- no cryptographic signature yet, only hashes/receipts
