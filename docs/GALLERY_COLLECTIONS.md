# Gallery Collections

Purpose: curate deterministic subsets of gallery runs into showcases/playlists.

Collection vs gallery:
- Gallery discovers all runs.
- Collection selects an ordered subset by run path and/or tags.

Generated files:
- `collection/index.html`
- `collection/collection_manifest.json`
- `collection/collection_receipt.json`
- `collection/COLLECTION_SUMMARY.md`

Selection:
- `--include-run` preserves requested order
- `--include-tag` requires all included tags
- `--exclude-tag` removes runs with matching tags

CLI:
- `python -m waveforge_studio.cli collection runs/gallery/gallery_manifest.json --out runs/gallery/collection --title "Golden Signal Showcase"`
- `python -m waveforge_studio.cli collection runs/gallery/gallery_manifest.json --out runs/gallery/collection_ready --include-tag alpha-ready --include-tag has-zip`
- `python -m waveforge_studio.cli collection-validate runs/gallery/collection/collection_manifest.json`

Limitations:
- index-only, assets linked not copied
- no server/database/hosting
- no external APIs/subprocesses/network
