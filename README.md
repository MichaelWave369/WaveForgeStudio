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
