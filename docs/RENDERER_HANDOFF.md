# Renderer Handoff Pack (v0.9)

## Purpose
Generate deterministic renderer input briefs from WaveForge packet + AV timeline.

## Schema overview
`waveforge.renderer_handoff.v0` includes audio/visual/sync handoff payloads, renderer slots, safety posture, and deterministic receipt hash.

## Audio handoff
Music brief, stem plan, voiceover script, mix notes.

## Visual handoff
Shot prompts, keyframe prompts, motion prompts, transition plan.

## Sync handoff
Markers, beat-to-cut, voice-to-symbol, peak-to-reveal.

## Renderer slots
At least six planned/blocked slots for future local adapters.

## Safety posture
Strict no external calls, subprocesses, network, or real rendering.

## Generated files
renderer_handoff.json and companion brief markdown/json files.

## Relationship to AV timeline
Uses AV timeline hash and markers as handoff timing source.

## Relationship to future adapters
Acts as practical local renderer input pack for future guarded execution.

## Limitations
No real rendering; deterministic planning only.
