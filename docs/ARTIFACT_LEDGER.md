# Artifact Ledger (v0.7)

## Purpose
Create deterministic hash ledger over output artifacts.

## Schema overview
`waveforge.artifact_ledger.v0` with relative file list, size, sha256, and ledger receipt.

## Hash policy
Sorted relative paths, sha256 per file, deterministic ledger hash.

## Excluded files
Hidden paths, __pycache__, .pytest_cache, artifact_ledger.json, artifact_ledger_receipt.json.

## Generated files
artifact_ledger.json, artifact_ledger_receipt.json, ARTIFACT_LEDGER_SUMMARY.md.

## Limitations
Ledger audits files only; does not validate semantic correctness of content.
