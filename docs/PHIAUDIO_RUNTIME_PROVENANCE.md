# PHIAudio Runtime Provenance Lock

WaveForgeStudio now keeps one canonical known-good PHIAudio runtime identity.

The current lock binds:

- repository: `MichaelWave369/PHIAudio`
- commit: `2c4855ba9bf7687428347733f4ae435bbee5a934`
- package identity/version
- CLI contract version
- canonical lock SHA-256

## Command

```bash
waveforge-studio phiaudio-runtime-lock
```

The real cross-repository qualification workflow consumes this command to choose the exact PHIAudio commit. The commit is no longer duplicated as a hidden YAML constant.

## Per-render provenance

A successful WaveForge PHIAudio render summary now includes:

- qualified PHIAudio repository,
- qualified PHIAudio commit,
- runtime-lock SHA-256,
- SHA-256 of the executable path actually invoked.

This distinguishes two facts:

1. **Qualification identity**: the PHIAudio source revision WaveForge has qualified.
2. **Invocation identity**: the bytes of the local executable launcher WaveForge actually invoked.

The executable digest alone is not a reproducible-build attestation for every imported JavaScript module. A later supply-chain rung may bind a signed package/SBOM or content-addressed runtime tree. This rung deliberately does not claim more than it proves.

## Upgrade rule

Changing the known-good commit changes the lock SHA-256 and triggers review plus the real cross-repository qualification workflow.
