# WaveForgeStudio — PHI369 Sovereign Media Studio (v0.7)

## Safe Queue Runner
v0.7 adds safe local export execution from render queue; future render jobs stay blocked.

## Artifact Ledger
Deterministic artifact hash ledger for auditable output directories.

## CLI
```bash
waveforge-studio run-queue project.waveforge.json --out runs/example
waveforge-studio ledger runs/example
waveforge-studio compile "prompt" --out runs/example --run-queue
waveforge-studio compile "prompt" --out runs/example --bundle --queue --run-queue
```

Safe local exports only; no media rendering.
