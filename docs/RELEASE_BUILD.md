# Unified Release Build

Purpose: one-command deterministic release showcase build from existing runs.

Stages:
1. gallery
2. collection
3. collection export
4. release deck
5. release deck ZIP
6. release build manifest/receipt/summary

Generated files:
- `release_build/gallery/*`
- `release_build/collection/*`
- `release_build/collection_export/*`
- `release_build/release_deck/*`
- `release_build/release_build_manifest.json`
- `release_build/release_build_receipt.json`
- `release_build/RELEASE_BUILD_SUMMARY.md`

Selection flags:
- `--include-tag` repeatable
- `--exclude-tag` repeatable
- `--include-run` repeatable

CLI:
- `python -m waveforge_studio.cli release-build runs --out runs/release_build --title "Golden Signal Release" --include-tag has-zip`
- `python -m waveforge_studio.cli release-build-validate runs/release_build/release_build_manifest.json`

Limitations:
- operates on existing runs only
- no new runs generated
- no media rendering
- no hosting/server/database
- no external APIs/subprocesses/network
