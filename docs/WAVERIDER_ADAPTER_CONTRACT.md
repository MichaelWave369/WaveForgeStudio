# WaveRider Adapter Pilot Contract

Contract-only definition; WaveRider runtime is not executed.

CLI:
```bash
python -m waveforge_studio.cli waverider-adapter-contract --out runs/waverider_contract
python -m waveforge_studio.cli waverider-adapter-contract-validate runs/waverider_contract/waverider_adapter_contract.json
python -m waveforge_studio.cli finalize-release runs --out runs/final_release_waverider_contract --title "Golden Signal Release" --include-tag has-zip --renderer-adapters --waverider-adapter-contract
```
