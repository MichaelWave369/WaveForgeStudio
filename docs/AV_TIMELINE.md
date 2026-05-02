# Unified AV Timeline Contract (v0.8)

## Purpose
Create one deterministic audiovisual score contract across audio, visual, sync, symbols, motion, and markers.

## Schema overview
`waveforge.av_timeline.v0` includes timebase, structure, six tracks, markers, export map, and timeline receipt hash.

## Tracks
music, voiceover, scene keyframes, camera motion, symbols, sync markers.

## Markers
Derived from sync lattice events with deterministic marker IDs/timestamps.

## Relations
- Audio graph provides tempo/sections/voice cues.
- Visual graph provides scenes/shots/symbols/motion cues.
- Sync lattice provides beat-aligned markers and cuts.

## Future render engines
AV timeline is intended as future render orchestration source of truth.

## Limitations
Deterministic contract only; no rendering execution.
