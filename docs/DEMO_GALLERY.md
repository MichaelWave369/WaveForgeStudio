# Local Demo Gallery

Purpose: deterministic local HTML index for WaveForge run archives.

Generated files:
- `gallery/index.html`
- `gallery/gallery_manifest.json`
- `gallery/gallery_receipt.json`
- `gallery/GALLERY_SUMMARY.md`

Discovery:
- scans non-hidden run directories
- qualifying files include packet/forge/release/smoke/preview-pack manifest
- links existing local artifacts (AV preview, preview pack, preview zip, manifests)

CLI:
- `python -m waveforge_studio.cli gallery runs --out runs/gallery`
- `python -m waveforge_studio.cli gallery-validate runs/gallery/gallery_manifest.json`

Limitations:
- index-only, assets not copied
- no hosting
- no browser automation
- no external APIs/subprocesses/network


Search + tags:
- prompt/hash/tag text search
- filters for mode, archetype, alpha_ready, smoke_passed, has_zip
- deterministic derived tags, e.g. `alpha-ready`, `has-zip`, `mode:mythic-reel`, `archetype:sovereign_signal`
- local-only static index (no server, no APIs, no subprocesses, no network)
