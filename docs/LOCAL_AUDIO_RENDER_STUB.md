# Local Audio Render Stub

Purpose: create deterministic local WAV placeholder artifacts safely using Python stdlib only.

## Safety
- local only
- stdlib only
- no external APIs
- no subprocesses
- no FFmpeg
- no PHIAudio runtime execution

## Generated files
- `render/audio_mix.wav`
- `render/stems/stem_click.wav`
- `render/stems/stem_tone.wav`
- `render/stems/stem_voice_placeholder.wav`
- `audio_render_manifest.json`
- `audio_render_receipt.json`
- `AUDIO_RENDER_SUMMARY.md`

## WAV characteristics
- mono
- 16-bit PCM
- default 48kHz
- deterministic samples

## CLI usage
```bash
python -m waveforge_studio.cli render-audio-stub tests/fixtures/sovereign_signal.project.waveforge.json --out runs/audio_stub_verify
python -m waveforge_studio.cli audio-render-validate runs/audio_stub_verify/audio_render_manifest.json
```

Limitation: placeholder audio only.
