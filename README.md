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
