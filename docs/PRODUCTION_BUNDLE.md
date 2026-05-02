# Unified Production Bundle (v0.4)

## Purpose
Create one deterministic governed export package that aggregates WaveForge packet artifacts, bridge contracts, preview, receipts, and production summary.

## Schema overview
`waveforge.production_bundle.v0` includes contents mapping, bridge contract hashes, coherence envelope, and deterministic bundle receipt.

## Generated files
Top-level production files plus `phiaudio/` and `waverider/` sub-bundles.

## Relationship to PHIAudio bridge
Production bundle embeds PHIAudio contract hash and includes PHIAudio bridge output files.

## Relationship to WaveRider bridge
Production bundle embeds WaveRider contract hash and includes WaveRider bridge output files.

## Relationship to timeline preview
Production bundle contains deterministic timeline preview for operator inspection.

## Limitations
Deterministic production bundle only; no media rendered.

## Future path
Feeds future real render orchestration runtime with auditable cross-domain contract artifacts.
