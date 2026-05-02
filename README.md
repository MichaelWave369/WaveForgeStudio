# WaveForgeStudio — PHI369 Sovereign Media Studio (v0.8)

## Unified AV Timeline
Deterministic unified audio/video timing contract and future source of truth for render orchestration.

## CLI
```bash
waveforge-studio timeline project.waveforge.json --out runs/example
waveforge-studio timeline-validate runs/example/av_timeline.json
waveforge-studio compile "prompt" --out runs/example --timeline
waveforge-studio compile "prompt" --out runs/example --bundle --queue --run-queue --timeline
```
