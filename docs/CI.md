# CI / Fresh Clone Verification

## What CI checks
- package install in editable mode with test extras
- test suite execution (`pytest -q`)
- doctor command runs
- smoke workflow runs and writes deterministic outputs

## Local equivalent
```bash
python -m pytest -q
python -m waveforge_studio.cli doctor
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke
```

Using Makefile:
```bash
make ci-local
```

## What CI intentionally does not do
- no real media rendering
- no external API calls
- no vendor runtime calls (PHIAudio, WaveRider, WaveTalk, ComfyUI, PhiOS, FFmpeg)
- no secret-dependent integration checks
