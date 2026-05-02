# WaveForgeStudio — PHI369 Sovereign Media Studio (v0.1.1)

**Doctrine:** WaveForgeStudio compiles one governed creative intent into synchronized audio, visual, motion, memory, and render artifacts.

**Tagline:** Intent → Signal → Sound → World → Artifact

## Architecture (text diagram)
WaveForgeStudio = WaveTalk × PHIAudio × WaveRider

## Quickstart
```bash
pip install -e .[dev]
python -m pytest
```

## CLI
```bash
waveforge-studio compile "The Sovereign Signal awakens across the infinite fractal wave." --duration 72 --seed 369369 --out runs/sovereign_signal
waveforge-studio validate runs/sovereign_signal/project.waveforge.json
waveforge-studio inspect runs/sovereign_signal/project.waveforge.json
waveforge-studio adapters
```

Compile writes deterministic artifacts including `summary.md`.

## PHI369 constants
- PHI = 1.61803398875
- LAMBDA = 0.61803398875
- C_STAR = PHI / 2
- OMEGA_C = 47 / 125

## MVP limitations
- Deterministic manifests only (no real media rendering)
- No external API calls or vendor integrations
- Adapter modules are stubs

## Private / Proprietary
Private proprietary work for PHI369 Labs / Parallax.
