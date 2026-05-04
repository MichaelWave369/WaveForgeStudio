# Golden Workflow

Purpose: blessed v3.0-alpha operator flow for deterministic local final release.

## Minimum
1) Forge at least one run with preview-pack-zip.
2) Finalize release from runs root.
3) Open `runs/final_release/index.html`.

## Full workflow
```bash
python -m waveforge_studio.cli forge "Golden Demo One" --out runs/golden_demo_one --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip
python -m waveforge_studio.cli forge "Golden Demo Two" --out runs/golden_demo_two --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip
python -m waveforge_studio.cli finalize-release runs --out runs/final_release --title "Golden Signal Release" --include-tag has-zip
```

Open first: `runs/final_release/index.html`

Share:
- `runs/final_release/release_build.zip`
- `runs/final_release/certificate_bundle/certificate_bundle.zip`

Verify:
```bash
python -m waveforge_studio.cli final-release-validate runs/final_release/final_release_manifest.json
python -m waveforge_studio.cli verify-release-build runs/final_release --strict
python -m waveforge_studio.cli release-certificate-validate runs/final_release/release_certificate.json
```


Optional signing-ready step:
```bash
python -m waveforge_studio.cli signature-envelope runs/final_release
```

```bash
python -m waveforge_studio.cli detached-signature runs/final_release
```

```bash
python -m waveforge_studio.cli renderer-adapters --out runs/final_release
```

```bash
python -m waveforge_studio.cli ffmpeg-adapter-contract --out runs/final_release
```
