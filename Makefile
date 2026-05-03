test:
	PYTHONPATH=src pytest -q

doctor:
	PYTHONPATH=src python -m waveforge_studio.cli doctor

smoke:
	PYTHONPATH=src python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke

ci-local:
	PYTHONPATH=src pytest -q
	PYTHONPATH=src python -m waveforge_studio.cli doctor
	PYTHONPATH=src python -m waveforge_studio.cli smoke --out runs/golden_demo_smoke
