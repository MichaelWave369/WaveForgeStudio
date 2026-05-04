# Adapter Contract Bundle

Purpose: future renderer law pack combining renderer adapters + FFmpeg/PHIAudio/WaveRider contracts.

CLI:
```bash
python -m waveforge_studio.cli adapter-contract-bundle --out runs/adapter_contract_bundle
python -m waveforge_studio.cli adapter-contract-bundle-validate runs/adapter_contract_bundle/adapter_contract_bundle_manifest.json
python -m waveforge_studio.cli finalize-release runs --out runs/final_release_adapter_bundle --title "Golden Signal Release" --include-tag has-zip --adapter-contract-bundle
```
