import json
from pathlib import Path

from core.infra.config import AetherConfig
from core.services.registry import AetherRegistry


def test_default_packages_dir_resolves_to_repo_brain_packages(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    config = AetherConfig(_env_file=None)
    expected = Path(__file__).resolve().parents[2] / "brain" / "packages"

    assert Path(config.packages_dir) == expected


def test_registry_discovers_manifest_and_lazy_loads_package(tmp_path):
    package_dir = tmp_path / "test-pkg"
    package_dir.mkdir()

    manifest = {
        "name": "unit-test-agent",
        "version": "1.0.0",
        "persona": "Unit test persona",
        "voice_id": "Puck",
        "language": "en-US",
        "capabilities": ["audio.input"],
        "tools": [],
    }

    (package_dir / "manifest.json").write_text(json.dumps(manifest))
    (package_dir / "prompts").mkdir()
    (package_dir / "prompts" / "system.txt").write_text("system prompt")

    registry = AetherRegistry(str(tmp_path))
    discovered = registry.scan()

    assert discovered == 1
    package = registry.get("unit-test-agent")
    assert package.manifest.name == "unit-test-agent"
