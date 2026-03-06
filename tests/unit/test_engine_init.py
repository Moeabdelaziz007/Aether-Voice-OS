from __future__ import annotations

import importlib
import sys
import types
from types import SimpleNamespace


def _module(name: str, **attrs):
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    sys.modules[name] = mod
    return mod


def _install_import_stubs() -> None:
    class Dummy:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

    class GatewayDummy(Dummy):
        def broadcast_binary(self, *args, **kwargs) -> None:
            return None

    class VectorStoreDummy(Dummy):
        def load(self, *args, **kwargs) -> None:
            return None

    # google SDK stubs
    runners = _module("google.adk.runners", InMemoryRunner=Dummy)
    adk = _module("google.adk", runners=runners)
    genai = _module("google.genai", types=SimpleNamespace())
    _module("google", adk=adk, genai=genai)

    # core.ai stubs
    _module("core.ai.handoff")
    _module("core.ai", handoff=sys.modules["core.ai.handoff"])
    _module("core.ai.adk_agents", root_agent=object())
    _module(
        "core.ai.agents.proactive",
        CodeAwareProactiveAgent=Dummy,
        ProactiveInterventionEngine=Dummy,
    )
    _module("core.ai.genetic", GeneticOptimizer=Dummy)
    _module("core.ai.hive", HiveCoordinator=Dummy)
    _module("core.ai.session", GeminiLiveSession=Dummy)

    # audio stubs
    _module("core.audio.capture", AudioCapture=Dummy)
    _module(
        "core.audio.paralinguistics",
        ParalinguisticAnalyzer=Dummy,
        ParalinguisticFeatures=Dummy,
    )
    _module("core.audio.playback", AudioPlayback=Dummy)
    _module("core.audio.processing", AdaptiveVAD=Dummy)

    # other dependency stubs
    _module("core.identity.package", AthPackage=Dummy)
    _module("core.infra.cloud.firebase.interface", FirebaseConnector=Dummy)

    def _load_config() -> SimpleNamespace:
        return _build_config()

    _module("core.infra.config", AetherConfig=Dummy, load_config=_load_config)
    _module("core.infra.transport.gateway", AetherGateway=GatewayDummy)
    _module("core.services.admin_api", SHARED_STATE={}, AdminAPIServer=Dummy)
    _module("core.services.registry", AetherRegistry=Dummy)

    # tools package + submodules
    tool_mod = types.ModuleType("core.tools")
    for name in ["hive_memory", "memory_tool", "system_tool", "tasks_tool", "vision_tool"]:
        setattr(tool_mod, name, types.ModuleType(f"core.tools.{name}"))
    sys.modules["core.tools"] = tool_mod

    _module("core.tools.router", ToolRouter=Dummy)
    _module("core.tools.vector_store", LocalVectorStore=VectorStoreDummy)


def _build_config() -> SimpleNamespace:
    return SimpleNamespace(
        ai=SimpleNamespace(api_key="test-key"),
        audio=SimpleNamespace(mic_queue_max=8, send_sample_rate=16000),
        gateway=SimpleNamespace(),
        packages_dir="brain/packages",
        log_level="INFO",
    )


def test_engine_init_does_not_raise_attribute_or_type_errors() -> None:
    _install_import_stubs()
    engine_module = importlib.import_module("core.engine")

    engine = engine_module.AetherEngine(config=_build_config())

    assert engine is not None


def test_engine_startup_smoke_initializes_core_components() -> None:
    _install_import_stubs()
    engine_module = importlib.import_module("core.engine")

    engine = engine_module.AetherEngine(config=_build_config())

    assert engine._gateway is not None
    assert engine._hive is not None
    assert engine._session is not None
    assert engine._capture is not None
    assert engine._playback is not None
