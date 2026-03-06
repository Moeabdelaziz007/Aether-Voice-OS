import importlib
import sys
import types
from types import SimpleNamespace


def _install_google_stubs() -> None:
    """Install minimal google.* stubs needed for importing core.engine in tests."""
    if "google" in sys.modules:
        return

    google_mod = types.ModuleType("google")
    genai_mod = types.ModuleType("google.genai")
    adk_mod = types.ModuleType("google.adk")
    adk_runners_mod = types.ModuleType("google.adk.runners")

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

    class DummyInMemoryRunner:
        def __init__(self, *args, **kwargs):
            pass

    genai_mod.Client = DummyClient
    genai_mod.types = types.SimpleNamespace(Part=object)
    adk_runners_mod.InMemoryRunner = DummyInMemoryRunner

    google_mod.genai = genai_mod
    adk_mod.runners = adk_runners_mod

    sys.modules["google"] = google_mod
    sys.modules["google.genai"] = genai_mod
    sys.modules["google.adk"] = adk_mod
    sys.modules["google.adk.runners"] = adk_runners_mod


def _install_engine_dependency_stubs() -> None:
    """Install lightweight stubs for optional engine dependencies."""

    def install_module(name: str, **attrs):
        mod = types.ModuleType(name)
        for key, value in attrs.items():
            setattr(mod, key, value)
        sys.modules[name] = mod

    class DummyComponent:
        def __init__(self, *args, **kwargs):
            pass

        async def initialize(self):
            return False

    class DummyHive:
        def __init__(self, *args, **kwargs):
            pass

        def set_pre_warm_callback(self, callback):
            self._pre_warm_callback = callback

    class DummySessionModuleClass:
        def __init__(self, *args, **kwargs):
            self._gateway = kwargs["gateway"]

    install_module("core.ai.adk_agents", root_agent=object())
    install_module(
        "core.ai.agents.proactive",
        CodeAwareProactiveAgent=DummyComponent,
        ProactiveInterventionEngine=DummyComponent,
        VisionPulseAgent=DummyComponent,
    )
    install_module("core.ai.genetic", GeneticOptimizer=DummyComponent)
    install_module("core.ai.session", GeminiLiveSession=DummySessionModuleClass)
    install_module("core.audio.capture", AudioCapture=DummyComponent)
    install_module("core.audio.playback", AudioPlayback=DummyComponent)
    install_module("core.audio.processing", AdaptiveVAD=DummyComponent, RingBuffer=DummyComponent)
    install_module(
        "core.audio.paralinguistics",
        ParalinguisticAnalyzer=DummyComponent,
        ParalinguisticFeatures=object,
    )
    install_module("core.infra.cloud.firebase.interface", FirebaseConnector=DummyComponent)
    install_module("core.services.registry", AetherRegistry=DummyComponent)
    install_module("core.ai.hive", HiveCoordinator=DummyHive)
    install_module("core.infra.transport.gateway", AetherGateway=DummyComponent)
    install_module("core.tools.hive_memory", set_firebase_connector=lambda *a, **k: None)
    install_module("core.tools.memory_tool", set_firebase_connector=lambda *a, **k: None)
    install_module("core.tools.system_tool")
    install_module("core.tools.tasks_tool", set_firebase_connector=lambda *a, **k: None)
    install_module("core.tools.vision_tool")


def test_engine_init_does_not_raise_type_error(monkeypatch):
    _install_google_stubs()
    _install_engine_dependency_stubs()
    engine_module = importlib.import_module("core.engine")

    class DummyToolRouter:
        def __init__(self):
            self._vector_store = None
            self.names = []
            self.count = 0

        def register_module(self, *args, **kwargs):
            return None

        def register(self, *args, **kwargs):
            return None

    class DummyVectorStore:
        def __init__(self, *args, **kwargs):
            pass

        def load(self, *args, **kwargs):
            return True

    class DummySession:
        def __init__(self, *args, **kwargs):
            self._gateway = kwargs["gateway"]

    class DummyGateway:
        def __init__(self, *args, **kwargs):
            pass

        async def broadcast(self, *args, **kwargs):
            return None

        async def broadcast_binary(self, *args, **kwargs):
            return None

    class DummyRegistry:
        def __init__(self, *args, **kwargs):
            pass

    class DummyAdminAPI:
        def __init__(self, *args, **kwargs):
            pass

    class DummyHiveCoordinator:
        def __init__(self, *args, **kwargs):
            self.active_soul = SimpleNamespace(manifest=SimpleNamespace(name="ArchitectExpert"))

        def set_pre_warm_callback(self, callback):
            self._pre_warm_callback = callback

    monkeypatch.setattr(engine_module, "ToolRouter", DummyToolRouter)
    monkeypatch.setattr(engine_module, "AetherGateway", DummyGateway)
    monkeypatch.setattr(engine_module, "GeminiLiveSession", DummySession)
    monkeypatch.setattr(engine_module, "AetherRegistry", DummyRegistry)
    monkeypatch.setattr(engine_module, "HiveCoordinator", DummyHiveCoordinator)
    monkeypatch.setattr(engine_module, "AdminAPIServer", DummyAdminAPI)

    vector_store_module = importlib.import_module("core.tools.vector_store")
    monkeypatch.setattr(vector_store_module, "LocalVectorStore", DummyVectorStore)

    config = SimpleNamespace(
        audio=SimpleNamespace(mic_queue_max=5, send_sample_rate=16000, vad_window_sec=5.0),
        ai=SimpleNamespace(api_key="test-key"),
        gateway=SimpleNamespace(host="0.0.0.0", port=18789),
        log_level="INFO",
        packages_dir="packages",
    )

    engine = engine_module.AetherEngine(config=config)

    assert engine._gateway is not None
    assert engine._session is not None
    assert engine._session._gateway is engine._gateway
