# Certificate Bundle ZIP

Deterministic ZIP archive for the compact certificate bundle proof packet.

Rules: sorted entries, relative paths only, stable timestamps, deterministic compression, excludes hidden/cache files and self-referential ZIP sidecars.

Generated files in `certificate_bundle/`:
- `certificate_bundle.zip`
- `certificate_bundle_zip_manifest.json`
- `certificate_bundle_zip_receipt.json`
- `CERTIFICATE_BUNDLE_ZIP_SUMMARY.md`

## CLI
```bash
python -m waveforge_studio.cli zip-certificate-bundle runs/release_build/certificate_bundle
python -m waveforge_studio.cli certificate-bundle-zip-validate runs/release_build/certificate_bundle/certificate_bundle_zip_manifest.json
python -m waveforge_studio.cli release-build runs --out runs/release_build_bundle_zip --title "Golden Signal Release" --include-tag has-zip --zip --verify --certify --certificate-bundle --certificate-bundle-zip
```

## Limitations
- metadata proof archive only
- not cryptographic signing
- no external transparency log
- no legal certification
- no full run copy
- no preview ZIP copy by default
- no external APIs/subprocesses/network
