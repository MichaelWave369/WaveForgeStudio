# PHIAudio Runtime Pilot

WaveForgeStudio can now invoke the external PHIAudio runtime after explicit operator enablement.

## Boundary

The pilot discovers a local `phiaudio-render` executable, remains disabled unless the caller supplies operator enablement, launches with `shell=False`, uses the existing `phiaudio/phiaudio_bundle.json` contract, requests output only under the WaveForge run root, performs no installation or network discovery, and does not turn runtime availability into authority.

A missing PHIAudio executable reports `available=false` and does not break unrelated WaveForge workflows.

## Verification

A zero exit code is not sufficient. WaveForgeStudio independently verifies source bundle hash continuity, render manifest schema, `networkUsed=false`, operator-enablement evidence, canonical render-manifest digest, the self-hashed runtime receipt, every returned artifact path, every artifact SHA-256 and byte size, and presence of the master artifact.

Only then does the adapter return `status=verified`.

## Current scope

This is an opt-in pilot API. It does not replace the generic stub UI or automatically enable PHIAudio in normal forge runs. A later UX/CLI rung can expose operator controls after field qualification with a real installed PHIAudio checkout.
