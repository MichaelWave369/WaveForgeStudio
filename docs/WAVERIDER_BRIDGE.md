# WaveRider Bridge Contract (v0.3)

## Purpose
Provide deterministic bridge export from WaveForge media packets to a WaveRider-compatible visual/world/render bundle.

## Schema overview
`waveforge.waverider_bundle.v0` includes world, scene graph, shot graph, symbol graph, motion graph, sync and audio references, render targets, and deterministic receipt.

## Generated files
- waverider_bundle.json
- waverider_world.json
- waverider_scene_graph.json
- waverider_shot_graph.json
- waverider_symbol_graph.json
- waverider_motion_graph.json
- waverider_receipt.json
- WAVERIDER_BRIDGE_SUMMARY.md

## Relationship to visual_graph and sync_lattice
This bridge transforms `visual` + `sync` packet sections into WaveRider-facing graph contracts while preserving 3/6/9 structure.

## Future integration plan
Future WaveRider runtime can consume this contract for storyboard/keyframe generation and real timeline rendering.

## Limitations
Deterministic contract only; no real image/video rendering or external integration.
