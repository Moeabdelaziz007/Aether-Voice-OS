"""Module-level import/parsing test for Gemini proxy."""

from __future__ import annotations

import importlib
import sys
import types


class _DummyRouter:
    def __init__(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def websocket(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def get(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator


class _DummyHTTPException(Exception):
    def __init__(self, status_code: int, detail):
        self.status_code = status_code
        self.detail = detail


class _DummyRequest:  # pragma: no cover - import compatibility stub
    pass


class _DummyWebSocket:  # pragma: no cover - import compatibility stub
    pass


def test_gemini_proxy_module_imports() -> None:
    """Ensure gemini_proxy parses and imports without SyntaxError."""
    fastapi_stub = types.ModuleType("fastapi")
    fastapi_stub.APIRouter = _DummyRouter
    fastapi_stub.HTTPException = _DummyHTTPException
    fastapi_stub.Request = _DummyRequest
    fastapi_stub.WebSocket = _DummyWebSocket

    original_fastapi = sys.modules.get("fastapi")
    sys.modules["fastapi"] = fastapi_stub
    try:
        module = importlib.import_module("core.api.gemini_proxy")
        assert module is not None
    finally:
        if original_fastapi is not None:
            sys.modules["fastapi"] = original_fastapi
        else:
            sys.modules.pop("fastapi", None)

        sys.modules.pop("core.api.gemini_proxy", None)
