# Real PHIAudio Cross-Repository Qualification

WaveForgeStudio now carries a CI qualification that executes against the real PHIAudio repository rather than a fake runtime.

## Pinned runtime

The workflow pins PHIAudio commit:

`2c4855ba9bf7687428347733f4ae435bbee5a934`

This is the merge commit for PHIAudio PR #7, the first release line containing the governed `phiaudio-render` CLI.

Pinning avoids silently changing the qualified runtime when PHIAudio main advances.

## Qualification path

```text
WaveForgeStudio checkout
        |
        +--> pinned PHIAudio checkout
                 |
                 +--> npm typecheck + full tests
                 +--> build phiaudio-render
        |
        v
WaveForge compile --export-phiaudio
        |
        v
real phiaudio-render
        |
        v
master + stems + manifest + receipt
        |
        v
WaveForge independent verification
        |
        v
cross-repository evidence artifact
```

The workflow verifies runtime discovery, operator gating metadata, zero-network declaration, real WaveForge bundle compatibility, real RIFF/WAV output, independent master SHA-256, receipt continuity, and at least one stem.

## Upgrade rule

Changing the pinned PHIAudio commit is a qualification change. The new commit should be reviewed and pass this workflow before WaveForgeStudio treats it as the new known-good runtime.

This workflow does not make PHIAudio mandatory for ordinary WaveForgeStudio CI or local use.
