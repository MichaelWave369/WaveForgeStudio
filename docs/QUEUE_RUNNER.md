# Queue Runner (v0.7)

## Purpose
Safely execute only deterministic local export jobs from render queue.

## Safe execution policy
No external calls, no subprocess, no network, no real rendering.

## Allowed jobs
WaveTalk/PHIAudio/WaveRider bridge exports, timeline preview, production bundle, final receipt export.

## Blocked jobs
future audio render, future video render, future final mux.

## Generated files
execution_report.json, execution_receipt.json, EXECUTION_SUMMARY.md, artifact ledger files.

## Relationship to render queue
Consumes validated queue job graph and updates status report.

## Relationship to artifact ledger
Writes ledger at end of run for auditable artifact hashing.

## Limitations
Plan-only safe runner; no real render execution.

## Future path
Guarded local execution engine with staged unlocks.
