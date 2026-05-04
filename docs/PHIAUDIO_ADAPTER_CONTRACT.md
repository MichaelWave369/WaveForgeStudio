# PHIAudio Adapter Pilot Contract

Contract-only definition; PHIAudio runtime is not executed.

CLI:
```bash
python -m waveforge_studio.cli phiaudio-adapter-contract --out runs/phiaudio_contract
python -m waveforge_studio.cli phiaudio-adapter-contract-validate runs/phiaudio_contract/phiaudio_adapter_contract.json
python -m waveforge_studio.cli finalize-release runs --out runs/final_release_phiaudio_contract --title "Golden Signal Release" --include-tag has-zip --renderer-adapters --phiaudio-adapter-contract
```
