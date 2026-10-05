# PHIAudio Operator CLI

WaveForgeStudio now exposes the governed PHIAudio runtime pilot through explicit operator commands.

## Availability

```bash
waveforge-studio phiaudio-runtime-status
```

Missing runtime availability is informational and returns success with `available=false`. This keeps unrelated WaveForge workflows independent from PHIAudio installation state.

## Render

```bash
waveforge-studio render-phiaudio RUN_ROOT --enable-phiaudio
```

Optional controls:

- `--bundle phiaudio/phiaudio_bundle.json`
- `--out render/phiaudio`
- `--runtime-command phiaudio-render`
- `--sample-rate 48000`
- `--timeout 60`

## Safety

The CLI delegates to the already-qualified runtime pilot, so it preserves:

- explicit operator enablement,
- local executable discovery,
- `shell=False`,
- run-root output containment,
- no network requirement,
- independent manifest/receipt verification,
- independent artifact SHA-256 and size checks.

The command prints a bounded verification summary. It does not treat PHIAudio availability or render output as operational authority.
