# Certificate Bundle

Compact metadata/evidence proof packet from a certified release build.

Includes certificate/verification/release-build evidence, with required and optional files.

Default does **not** copy `release_build.zip`; use `--include-zip-file` when needed.

## Generated files
- `certificate_bundle_manifest.json`
- `certificate_bundle_receipt.json`
- `CERTIFICATE_BUNDLE_SUMMARY.md`

## CLI
```bash
python -m waveforge_studio.cli certificate-bundle runs/release_build_certified
python -m waveforge_studio.cli certificate-bundle runs/release_build_certified --include-zip-file
python -m waveforge_studio.cli certificate-bundle-validate runs/release_build_certified/certificate_bundle/certificate_bundle_manifest.json
python -m waveforge_studio.cli release-build runs --out runs/release_build_bundle --title "Golden Signal Release" --include-tag has-zip --zip --verify --certify --certificate-bundle
```

## Limitations
- metadata proof bundle only
- not cryptographic signing
- no external transparency log
- no legal certification
- no full run copy
- no preview ZIP copy by default
