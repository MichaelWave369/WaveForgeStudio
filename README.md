# WaveForgeStudio — PHI369 Sovereign Media Studio (v0.5)

WaveForgeStudio compiles governed intent into synchronized artifacts.

## WaveTalk Bridge (v0.5)
Deterministic sovereign signal/governance/memory bundle export contract (no network runtime).

## Unified Production Bundle (recommended v0.5 export)
Bundle mode now includes WaveTalk + PHIAudio + WaveRider + Timeline Preview outputs in one deterministic auditable package.

## CLI
```bash
waveforge-studio export-wavetalk project.waveforge.json --out runs/example/wavetalk
waveforge-studio compile "prompt" --out runs/example --export-wavetalk
waveforge-studio compile "prompt" --out runs/example --export-wavetalk --export-phiaudio --export-waverider --preview
waveforge-studio bundle project.waveforge.json --out runs/example_bundle
waveforge-studio compile "prompt" --out runs/example --bundle
```

## Limitations
Deterministic contracts only — no real signal, audio, or visual rendering runtime in v0.5.
