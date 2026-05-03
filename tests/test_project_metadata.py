from waveforge_studio import __version__
from waveforge_studio import cli, smoke
from waveforge_studio.alpha_artifacts import REQUIRED_ALPHA_ARTIFACTS


def test_project_imports_and_version():
    assert __version__
    assert cli is not None
    assert smoke is not None


def test_required_alpha_artifact_keys_present():
    expected = {
        "project.waveforge.json",
        "release_manifest.json",
        "STUDIO_SEAL.md",
        "forge_report.json",
    }
    assert expected.issubset(set(REQUIRED_ALPHA_ARTIFACTS))
