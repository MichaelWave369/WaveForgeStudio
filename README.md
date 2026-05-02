# WaveForgeStudio — PHI369 Sovereign Media Studio (v0.6)

WaveForgeStudio compiles governed intent into synchronized artifacts.

## Render Queue / Job Manifest (v0.6)
Deterministic plan-only orchestration queue for future safe local render execution.

## CLI
```bash
waveforge-studio queue project.waveforge.json --out runs/example
waveforge-studio queue-validate runs/example/render_queue.json
waveforge-studio compile "prompt" --out runs/example --queue
waveforge-studio compile "prompt" --out runs/example --bundle --queue
```

Plan-only orchestration; no runtime execution.
