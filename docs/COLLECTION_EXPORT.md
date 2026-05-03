# Collection Export Pack

Purpose: turn a curated collection into a portable release pack.

Collection vs export:
- Collection curates run references.
- Collection export copies compact selected artifacts for sharing.

Generated files:
- `collection_export/index.html`
- `collection_export/collection_export_manifest.json`
- `collection_export/collection_export_receipt.json`
- `collection_export/COLLECTION_EXPORT_SUMMARY.md`
- copied `collection/` metadata files
- copied `runs/<export_id>/preview_pack.zip` (+ zip manifest/receipt when present)
- `runs/<export_id>/run_summary.json`

Not copied:
- full run directories
- large render trees outside selected compact artifacts

CLI:
- `python -m waveforge_studio.cli collection-export runs/gallery/collection/collection_manifest.json --out runs/gallery/collection_export`
- `python -m waveforge_studio.cli collection-export-validate runs/gallery/collection_export/collection_export_manifest.json`

Limitations:
- no full run copy
- no server/database/hosting
- no external APIs/subprocesses/network
