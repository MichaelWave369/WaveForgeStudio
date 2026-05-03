# Alpha Release Deck

Purpose: deterministic offline showcase deck built from a collection export.

Release deck vs collection export:
- Collection export gathers compact artifacts.
- Release deck presents those artifacts as offline HTML cards + markdown.

Generated files:
- `release_deck/index.html`
- `release_deck/RELEASE_DECK.md`
- `release_deck/release_deck_manifest.json`
- `release_deck/release_deck_receipt.json`
- `release_deck/cards/card_001.html`...

Card structure:
- prompt, seed/mode/duration/archetype
- tags
- links to ZIP/manifest/receipt/run_summary
- hash snippets

CLI:
- `python -m waveforge_studio.cli release-deck runs/gallery/collection_export/collection_export_manifest.json --out runs/gallery/collection_export/release_deck --title "Golden Signal Release Deck"`
- `python -m waveforge_studio.cli release-deck-validate runs/gallery/collection_export/release_deck/release_deck_manifest.json`

Limitations:
- not PowerPoint
- not a slide renderer
- assets linked, not copied
- no server/database/hosting
- no external APIs/subprocesses/network
