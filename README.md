# WaveForgeStudio — PHI369 Sovereign Media Studio (v0.3)

WaveForgeStudio compiles governed intent into synchronized artifacts.

## Core doctrine
WaveForgeStudio does not glue songs onto videos.

## Bridge Contracts
- PHIAudio Bridge: deterministic audio production bundle contract.
- WaveRider Bridge: deterministic visual/world/render bundle contract.
- Timeline Preview: deterministic HTML operator inspection.

## CLI
```bash
waveforge-studio export-waverider project.waveforge.json --out runs/example/waverider
waveforge-studio compile "prompt" --out runs/example --export-waverider
waveforge-studio compile "prompt" --out runs/example --export-phiaudio --export-waverider --preview
```

Also available: `validate`, `inspect`, `adapters`, `preview`, `export-phiaudio`.

## Limitations
Deterministic contracts only; no real rendering or external/vendor integrations.
