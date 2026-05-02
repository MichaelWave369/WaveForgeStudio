# Render Queue / Job Manifest (v0.6)

## Purpose
Define a deterministic, plan-only orchestration manifest for safe future rendering.

## Schema overview
`waveforge.render_queue.v0` captures execution policy, 9-job DAG plan, counts, and queue receipt hash.

## 9-job structure
WaveTalk export, PHIAudio export, WaveRider export, timeline preview, production bundle, 3 blocked future render placeholders, and final receipt export.

## Execution policy
`plan_only`, with external/network/subprocess/real-rendering all disabled.

## Blocked future render jobs
Future render jobs are explicitly `blocked_plan_only`.

## Relationship to production bundle
Queue orchestrates artifacts around production bundle creation and future render phases.

## Limitations
Plan-only manifest; no execution.

## Future path
Supports a future safe local execution engine with strict policy controls.
