# WaveForgeStudio — PHI369 Sovereign Media Studio (v0.9)

## Renderer Handoff Pack
Deterministic future renderer input pack derived from media packet + AV timeline.

## CLI
```bash
waveforge-studio handoff project.waveforge.json --out runs/example
waveforge-studio handoff-validate runs/example/renderer_handoff.json
waveforge-studio compile "prompt" --out runs/example --handoff
waveforge-studio compile "prompt" --out runs/example --bundle --queue --run-queue --timeline --handoff
```

Handoff pack is planning/input only, not execution.


## Golden Demo Smoke Test

```bash
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke
```

Manual equivalent:

```bash
python -m waveforge_studio.cli version
python -m waveforge_studio.cli schemas
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo
python -m waveforge_studio.cli release runs/golden_demo
```


## CI / Fresh Clone Verification

Local check:

```bash
python -m pytest -q
python -m waveforge_studio.cli doctor
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke
```

If Makefile is available:

```bash
make ci-local
```


## Local Audio Render Stub

```bash
python -m waveforge_studio.cli render-audio-stub runs/golden_demo/project.waveforge.json --out runs/golden_demo
python -m waveforge_studio.cli audio-render-validate runs/golden_demo/audio_render_manifest.json
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo_audio --render-audio-stub
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke_audio --render-audio-stub
```


## Local Visual Storyboard Render Stub

```bash
python -m waveforge_studio.cli render-visual-stub runs/golden_demo/project.waveforge.json --out runs/golden_demo
python -m waveforge_studio.cli visual-render-validate runs/golden_demo/visual_render_manifest.json
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo_visual --render-visual-stub
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo_av --render-audio-stub --render-visual-stub
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke_visual --render-visual-stub
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke_av --render-audio-stub --render-visual-stub
```


## Local AV Preview Page

```bash
python -m waveforge_studio.cli preview-av runs/golden_demo/project.waveforge.json --out runs/golden_demo
python -m waveforge_studio.cli av-preview-validate runs/golden_demo/av_preview_manifest.json
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo_preview --av-preview
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo_full_preview --render-audio-stub --render-visual-stub --av-preview
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke_preview --render-audio-stub --render-visual-stub --av-preview
```


## Portable Preview Export Pack

```bash
python -m waveforge_studio.cli pack-preview runs/golden_demo_full_preview --out runs/golden_demo_full_preview/preview_pack
python -m waveforge_studio.cli preview-pack-validate runs/golden_demo_full_preview/preview_pack/preview_pack_manifest.json
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo_pack --render-audio-stub --render-visual-stub --av-preview --preview-pack
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke_pack --render-audio-stub --render-visual-stub --av-preview --preview-pack
```

## Deterministic Preview Pack ZIP

```bash
python -m waveforge_studio.cli zip-preview-pack runs/golden_demo_pack/preview_pack
python -m waveforge_studio.cli preview-pack-zip-validate runs/golden_demo_pack/preview_pack/preview_pack_zip_manifest.json
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo_zip --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke_zip --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip
```

## Local Demo Gallery

```bash
python -m waveforge_studio.cli gallery runs --out runs/gallery
python -m waveforge_studio.cli gallery-validate runs/gallery/gallery_manifest.json

python -m waveforge_studio.cli forge "Demo one" --out runs/demo_one --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip
python -m waveforge_studio.cli forge "Demo two" --out runs/demo_two --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip
python -m waveforge_studio.cli gallery runs --out runs/gallery
```

- searchable gallery with prompt/hash search and tag filtering

## Gallery Collections

```bash
python -m waveforge_studio.cli collection runs/gallery/gallery_manifest.json --out runs/gallery/collection --title "Golden Signal Showcase"
python -m waveforge_studio.cli collection runs/gallery/gallery_manifest.json --out runs/gallery/collection_ready --include-tag alpha-ready --include-tag has-zip
python -m waveforge_studio.cli collection-validate runs/gallery/collection/collection_manifest.json
```

## Collection Export Pack

```bash
python -m waveforge_studio.cli collection-export runs/gallery/collection/collection_manifest.json --out runs/gallery/collection_export
python -m waveforge_studio.cli collection-export-validate runs/gallery/collection_export/collection_export_manifest.json

python -m waveforge_studio.cli forge "Collection Export Demo One" --out runs/export_demo_one --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip
python -m waveforge_studio.cli forge "Collection Export Demo Two" --out runs/export_demo_two --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip
python -m waveforge_studio.cli gallery runs --out runs/gallery
python -m waveforge_studio.cli collection runs/gallery/gallery_manifest.json --out runs/gallery/collection --title "Golden Signal Release" --include-tag has-zip
python -m waveforge_studio.cli collection-export runs/gallery/collection/collection_manifest.json --out runs/gallery/collection_export
```

## Alpha Release Deck

```bash
python -m waveforge_studio.cli release-deck runs/gallery/collection_export/collection_export_manifest.json --out runs/gallery/collection_export/release_deck --title "Golden Signal Release Deck"
python -m waveforge_studio.cli release-deck-validate runs/gallery/collection_export/release_deck/release_deck_manifest.json

python -m waveforge_studio.cli forge "Deck Demo One" --out runs/deck_demo_one --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip
python -m waveforge_studio.cli forge "Deck Demo Two" --out runs/deck_demo_two --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip
python -m waveforge_studio.cli gallery runs --out runs/gallery
python -m waveforge_studio.cli collection runs/gallery/gallery_manifest.json --out runs/gallery/collection --title "Golden Signal Release" --include-tag has-zip
python -m waveforge_studio.cli collection-export runs/gallery/collection/collection_manifest.json --out runs/gallery/collection_export
python -m waveforge_studio.cli release-deck runs/gallery/collection_export/collection_export_manifest.json --out runs/gallery/collection_export/release_deck --title "Golden Signal Release Deck"
```

## Deterministic Release Deck ZIP

```bash
python -m waveforge_studio.cli zip-release-deck runs/gallery/collection_export/release_deck
python -m waveforge_studio.cli release-deck-zip-validate runs/gallery/collection_export/release_deck/release_deck_zip_manifest.json

python -m waveforge_studio.cli forge "Deck Zip Demo One" --out runs/deck_zip_demo_one --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip
python -m waveforge_studio.cli forge "Deck Zip Demo Two" --out runs/deck_zip_demo_two --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip
python -m waveforge_studio.cli gallery runs --out runs/gallery
python -m waveforge_studio.cli collection runs/gallery/gallery_manifest.json --out runs/gallery/collection --title "Golden Signal Release" --include-tag has-zip
python -m waveforge_studio.cli collection-export runs/gallery/collection/collection_manifest.json --out runs/gallery/collection_export
python -m waveforge_studio.cli release-deck runs/gallery/collection_export/collection_export_manifest.json --out runs/gallery/collection_export/release_deck --title "Golden Signal Release Deck"
python -m waveforge_studio.cli zip-release-deck runs/gallery/collection_export/release_deck
```
