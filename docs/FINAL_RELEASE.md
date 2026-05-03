# Final Release

One-command deterministic final release workflow from existing runs.

Stages: release build -> release_build.zip -> verification -> certificate -> certificate bundle -> certificate_bundle.zip -> index page -> final manifest/receipt.

Generated files include `final_release_manifest.json`, `final_release_receipt.json`, and `FINAL_RELEASE_SUMMARY.md` plus all release-build artifacts.

## CLI
```bash
python -m waveforge_studio.cli finalize-release runs --out runs/final_release --title "Golden Signal Release" --include-tag has-zip
python -m waveforge_studio.cli final-release-validate runs/final_release/final_release_manifest.json
```

Difference from `release-build`: finalizer orchestrates full post-build proof/index pipeline in one command.

## Limitations
- operates on existing runs
- does not create new runs
- does not render media
- no hosting/server/database
- no external APIs/subprocesses/network
- not cryptographically signed
- no legal certification
