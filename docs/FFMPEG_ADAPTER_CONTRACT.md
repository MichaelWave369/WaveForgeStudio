# Optional FFmpeg Export Adapter Contract

Contract-only definition; FFmpeg is not executed.

CLI:
```bash
python -m waveforge_studio.cli ffmpeg-adapter-contract --out runs/ffmpeg_contract
python -m waveforge_studio.cli ffmpeg-adapter-contract-validate runs/ffmpeg_contract/ffmpeg_adapter_contract.json
python -m waveforge_studio.cli finalize-release runs --out runs/final_release_ffmpeg_contract --title "Golden Signal Release" --include-tag has-zip --renderer-adapters --ffmpeg-adapter-contract
```
