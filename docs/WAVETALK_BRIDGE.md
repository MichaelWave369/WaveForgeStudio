# WaveTalk Bridge Contract (v0.5)

## Purpose
Create deterministic WaveTalk-compatible sovereign signal/governance/memory bundle exports from WaveForge media packets.

## Schema overview
`waveforge.wavetalk_bundle.v0` contains signal, routing, governance, memory lineage/receipts, replay guarantees, and bridge receipt.

## Generated files
- wavetalk_bundle.json
- wavetalk_signal.json
- wavetalk_routing.json
- wavetalk_governance.json
- wavetalk_memory.json
- wavetalk_replay.json
- wavetalk_receipt.json
- WAVETALK_BRIDGE_SUMMARY.md

## Relationship to governance
Carries coherence threshold/overall/pass state and policy review stub fields.

## Relationship to memory / lineage / receipts
Includes lineage and packet receipt linkage for replay-safe continuity posture.

## Relationship to production bundle
Production bundle embeds WaveTalk contract hash and includes wavetalk/ artifacts.

## Future integration plan
Future WaveTalk/SGL/SML runtime can consume this contract for real routing, policy review, and sovereign continuity orchestration.

## Limitations
Deterministic local export only; no networked runtime.
