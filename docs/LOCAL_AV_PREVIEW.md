# Local AV Preview Page

Offline deterministic AV preview that references local WAV/SVG artifacts.

- no video rendering
- no muxing
- no browser automation
- no external APIs/subprocesses/FFmpeg/network

Generated files:
- `render/av_preview.html`
- `av_preview_manifest.json`
- `av_preview_receipt.json`
- `AV_PREVIEW_SUMMARY.md`

Includes audio player (if audio exists), storyboard gallery, timeline markers, and hash summary.

CLI:
```bash
python -m waveforge_studio.cli preview-av tests/fixtures/sovereign_signal.project.waveforge.json --out runs/av_preview_verify
python -m waveforge_studio.cli av-preview-validate runs/av_preview_verify/av_preview_manifest.json
```
