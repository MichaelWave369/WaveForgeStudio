# Deterministic Release Deck ZIP

Purpose: deterministic ZIP archive for `release_deck/`.

Rules:
- sorted relative entries
- stable ZIP timestamps
- deterministic compression
- exclude hidden/cache files
- exclude ZIP and ZIP manifest/receipt/summary from archive payload

Generated files:
- `release_deck.zip`
- `release_deck_zip_manifest.json`
- `release_deck_zip_receipt.json`
- `RELEASE_DECK_ZIP_SUMMARY.md`

CLI:
- `python -m waveforge_studio.cli zip-release-deck runs/gallery/collection_export/release_deck`
- `python -m waveforge_studio.cli release-deck-zip-validate runs/gallery/collection_export/release_deck/release_deck_zip_manifest.json`

Limitations:
- not PowerPoint
- no slide rendering
- no video rendering
- no muxing
- no browser automation
- no external APIs/subprocesses/network
