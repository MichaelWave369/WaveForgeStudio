# Portable Preview Export Pack

Deterministic folder export for local AV preview artifacts.

- folder export only (no zip by default)
- no video rendering, muxing, or browser automation
- no external APIs, subprocesses, FFmpeg, or network

Includes copied media, manifests, receipts, and summary in `preview_pack/`.

CLI:
```bash
python -m waveforge_studio.cli pack-preview runs/golden_demo_full_preview --out runs/golden_demo_full_preview/preview_pack
python -m waveforge_studio.cli preview-pack-validate runs/golden_demo_full_preview/preview_pack/preview_pack_manifest.json
```
