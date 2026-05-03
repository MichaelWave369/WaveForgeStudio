# Deterministic Release Build ZIP

## Purpose
Create a deterministic, portable top-level archive for an existing unified `release_build` directory.

## Deterministic ZIP Rules
- deterministic ZIP entry ordering
- stable timestamps
- relative paths only
- no hosting/server/database behavior
- no browser automation
- no PowerPoint, video rendering, or muxing
- no external APIs, subprocesses, or network usage

## Generated Files
Inside the release build directory:
- `release_build.zip`
- `release_build_zip_manifest.json`
- `release_build_zip_receipt.json`
- `RELEASE_BUILD_ZIP_SUMMARY.md`

## CLI Usage
```bash
python -m waveforge_studio.cli zip-release-build runs/release_build
python -m waveforge_studio.cli zip-release-build runs/release_build --out runs/release_build/custom_release_build.zip
```

## Validation
```bash
python -m waveforge_studio.cli release-build-zip-validate runs/release_build/release_build_zip_manifest.json
```

## Inline release-build ZIP
```bash
python -m waveforge_studio.cli release-build runs --out runs/release_build_zip --title "Golden Signal Release" --include-tag has-zip --zip
```
