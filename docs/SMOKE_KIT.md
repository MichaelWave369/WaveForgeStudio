# Golden Demo Smoke Kit (v1.0.1-alpha)

## Purpose
Provide a single deterministic local smoke path for alpha workflow validation.

## Commands
```bash
python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke
```

Manual equivalent:
```bash
python -m waveforge_studio.cli version
python -m waveforge_studio.cli schemas
python -m waveforge_studio.cli forge "The Sovereign Signal awakens across the infinite fractal wave." --out runs/golden_demo
python -m waveforge_studio.cli release runs/golden_demo
```

## Expected Outputs
- `smoke_report.json`
- `smoke_report_receipt.json`
- `SMOKE_SUMMARY.md`

## Smoke report schema overview
- `schema`: `waveforge.smoke_report.v1_alpha`
- deterministic core metadata and run inputs
- required/missing artifact checks
- stable receipt hash and stable timestamp

## What smoke verifies
- forge workflow runs locally
- release manifest and studio seal exist
- required alpha artifacts are present
- release is `alpha_ready`

## What smoke does not verify
- no real media rendering quality
- no external APIs or runtime bridges

## Limitation
Plan-only deterministic artifact generation; no real media rendering.
