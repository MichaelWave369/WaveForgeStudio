# Deterministic Preview Pack ZIP

Purpose: create a deterministic ZIP from `preview_pack/` for safe sharing/archive.

Rules:
- sorted relative file paths
- stable ZIP timestamps
- deterministic compression
- exclude hidden files, `__pycache__`, `.pytest_cache`
- exclude `preview_pack.zip` and ZIP manifest/receipt/summary from ZIP payload

Generated files in `preview_pack/`:
- `preview_pack.zip`
- `preview_pack_zip_manifest.json`
- `preview_pack_zip_receipt.json`
- `PREVIEW_PACK_ZIP_SUMMARY.md`

CLI:
- `python -m waveforge_studio.cli zip-preview-pack runs/golden_demo_pack/preview_pack`
- `python -m waveforge_studio.cli preview-pack-zip-validate runs/golden_demo_pack/preview_pack/preview_pack_zip_manifest.json`

Limitations:
- no video rendering
- no muxing
- no browser automation
- no external APIs, subprocesses, FFmpeg, or network
