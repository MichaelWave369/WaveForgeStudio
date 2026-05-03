# Release Build Index Page

Deterministic operator launch page for a `release_build/` folder.

Links deck/gallery/collection/export archives and proof artifacts with status badges, counts, and hashes.

Generated files:
- `index.html`
- `release_build_index_manifest.json`
- `release_build_index_receipt.json`
- `RELEASE_BUILD_INDEX_SUMMARY.md`

## CLI
```bash
python -m waveforge_studio.cli release-build-index runs/release_build
python -m waveforge_studio.cli release-build-index-validate runs/release_build/release_build_index_manifest.json
python -m waveforge_studio.cli release-build runs --out runs/release_build_indexed --title "Golden Signal Release" --include-tag has-zip --zip --verify --certify --certificate-bundle --certificate-bundle-zip --index
```

## Limitations
- launch page only
- no hosting
- no asset copying
- no media rendering
- no external APIs/subprocesses/network
