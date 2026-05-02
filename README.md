# WaveForgeStudio — PHI369 Sovereign Media Studio (v0.4)

WaveForgeStudio compiles governed intent into synchronized artifacts.

## Unified Production Bundle (recommended v0.4 export)
Bundle mode creates full deterministic operator package including packet artifacts, PHIAudio bridge, WaveRider bridge, timeline preview, and production receipt.

## CLI
```bash
waveforge-studio bundle project.waveforge.json --out runs/example_bundle
waveforge-studio compile "prompt" --out runs/example --bundle
waveforge-studio compile "prompt" --out runs/example --export-phiaudio --export-waverider --preview
```

Also available: `validate`, `inspect`, `adapters`, `preview`, `export-phiaudio`, `export-waverider`.

## Limitations
Deterministic production bundle only — no media rendered in v0.4.
