# Local Visual Storyboard Render Stub

Deterministic stdlib-only placeholder storyboard renderer.

- no image generation
- no video rendering
- no WaveRider runtime execution
- no external APIs, subprocesses, or FFmpeg

Outputs:
- `render/storyboard/frame_001.svg` ... `frame_009.svg`
- `render/storyboard_index.html`
- `visual_render_manifest.json`
- `visual_render_receipt.json`
- `VISUAL_RENDER_SUMMARY.md`

CLI:
```bash
python -m waveforge_studio.cli render-visual-stub tests/fixtures/sovereign_signal.project.waveforge.json --out runs/visual_stub_verify
python -m waveforge_studio.cli visual-render-validate runs/visual_stub_verify/visual_render_manifest.json
```
