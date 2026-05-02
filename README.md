# WaveForgeStudio — PHI369 Sovereign Media Studio (v0.2.1)

WaveForgeStudio compiles one governed creative intent into synchronized audio, visual, motion, memory, and render artifacts.

## Core doctrine
WaveForgeStudio does not glue songs onto videos.
It compiles one governed creative intent into synchronized artifacts.

## Timeline Preview (v0.2.1)
Deterministic self-contained HTML inspection view for timeline alignment; this is not rendered video.

## CLI
```bash
waveforge-studio compile "prompt" --out runs/example
waveforge-studio compile "prompt" --out runs/example --preview
waveforge-studio compile "prompt" --out runs/example --export-phiaudio --preview
waveforge-studio preview runs/example/project.waveforge.json --out runs/example
waveforge-studio export-phiaudio runs/example/project.waveforge.json --out runs/example/phiaudio
waveforge-studio validate runs/example/project.waveforge.json
waveforge-studio inspect runs/example/project.waveforge.json
waveforge-studio adapters
```

## PHIAudio Bridge (v0.2)
WaveForge media packet → PHIAudio production bundle via deterministic bridge contract.
This is a planning/export layer only, not real audio rendering.

See `docs/PHIAUDIO_BRIDGE.md` and `docs/TIMELINE_PREVIEW.md`.

## Limitations
- No external API calls.
- No vendor integrations.
- Deterministic manifests/contracts/previews only.
