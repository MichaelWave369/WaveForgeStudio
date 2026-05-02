# PHIAUDIO Bridge Contract (v0.2)

## Purpose
Provide a deterministic, local-first bridge contract from `waveforge.media_packet.v0` to `waveforge.phiaudio_bundle.v0`.

## Schema overview
The PHIAudio bundle includes source packet hash, composition plan, stems/event plans, sync mappings, visual references, render targets, and a deterministic bridge receipt.

## Generated files
- phiaudio_bundle.json
- phiaudio_composition.json
- phiaudio_stems.json
- phiaudio_sync.json
- phiaudio_receipt.json
- PHIAUDIO_BRIDGE_SUMMARY.md

## Future integration plan
Future PHIAudio runtime can consume this bundle for real synthesis, stem rendering, mixdown, and timeline production.

## Limitations
This is not real rendering. No external APIs, no vendor integrations, and no runtime audio generation are included in v0.2.
