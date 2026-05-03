# WaveForgeStudio — PHI369 Sovereign Media Studio (v0.9)

## Renderer Handoff Pack
Deterministic future renderer input pack derived from media packet + AV timeline.

## CLI
```bash
waveforge-studio handoff project.waveforge.json --out runs/example
waveforge-studio handoff-validate runs/example/renderer_handoff.json
waveforge-studio compile "prompt" --out runs/example --handoff
waveforge-studio compile "prompt" --out runs/example --bundle --queue --run-queue --timeline --handoff
```

Handoff pack is planning/input only, not execution.


## Golden Demo Smoke Test

```bash
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke
```

Manual equivalent:

```bash
python -m waveforge_studio.cli version
python -m waveforge_studio.cli schemas
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo
python -m waveforge_studio.cli release runs/golden_demo
```


## CI / Fresh Clone Verification

Local check:

```bash
python -m pytest -q
python -m waveforge_studio.cli doctor
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke
```

If Makefile is available:

```bash
make ci-local
```


## Local Audio Render Stub

```bash
python -m waveforge_studio.cli render-audio-stub runs/golden_demo/project.waveforge.json --out runs/golden_demo
python -m waveforge_studio.cli audio-render-validate runs/golden_demo/audio_render_manifest.json
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo_audio --render-audio-stub
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke_audio --render-audio-stub
```


## Local Visual Storyboard Render Stub

```bash
python -m waveforge_studio.cli render-visual-stub runs/golden_demo/project.waveforge.json --out runs/golden_demo
python -m waveforge_studio.cli visual-render-validate runs/golden_demo/visual_render_manifest.json
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo_visual --render-visual-stub
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo_av --render-audio-stub --render-visual-stub
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke_visual --render-visual-stub
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke_av --render-audio-stub --render-visual-stub
```
