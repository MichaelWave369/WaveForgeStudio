# WaveForgeStudio — PHI369 Sovereign Media Studio

**Doctrine:** WaveForgeStudio does not glue songs onto videos. It compiles one governed creative intent into synchronized audio, visual, motion, memory, and render artifacts.

**Tagline:** Intent → Signal → Sound → World → Artifact

## Architecture (text diagram)
WaveForgeStudio = WaveTalk × PHIAudio × WaveRider

Intent Packet
  -> Formula Compiler (3/6/9)
  -> Audio Graph (plan)
  -> Visual Graph (plan)
  -> Sync Lattice (alignment)
  -> Receipt + Render Manifest
  -> Sovereign Artifact Bundle (deterministic JSON + markdown)

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m pytest
```

## CLI Example
```bash
waveforge-studio compile "The Sovereign Signal awakens across the infinite fractal wave." --duration 72 --seed 369369 --out runs/sovereign_signal
python -m waveforge_studio.cli compile "prompt text" --out runs/test
```

## PHI369 constants
- PHI = 1.61803398875
- LAMBDA = 0.61803398875
- C_STAR = PHI / 2
- OMEGA_C = 47 / 125
- DEFAULT_SEED = 369369
- FIB_SEQUENCE = [1,1,2,3,5,8,13,21,34]
- DEFAULT_STRUCTURE = "3-6-9"

## MVP limitations
- Deterministic manifests only (no real media rendering).
- No external API calls or vendor integration.
- Adapter modules are stubs for future sovereign runtime bridges.

## Private / Proprietary
WaveForgeStudio is private proprietary work for PHI369 Labs / Parallax.
