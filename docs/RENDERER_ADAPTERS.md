# Renderer Adapters

Interface contract only for local/planned/future adapters.

No real rendering, no FFmpeg, no ComfyUI execution, no PHIAudio runtime execution, no WaveRider runtime execution, no subprocesses, no external APIs/network.

CLI:
```bash
python -m waveforge_studio.cli renderer-adapters --out runs/renderer_adapters
python -m waveforge_studio.cli renderer-adapters-validate runs/renderer_adapters/renderer_adapter_manifest.json
python -m waveforge_studio.cli finalize-release runs --out runs/final_release_adapters --title "Golden Signal Release" --include-tag has-zip --renderer-adapters
```
