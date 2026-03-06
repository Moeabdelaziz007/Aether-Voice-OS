"""
Aether Voice OS — Gemini Proxy API

Secure backend proxy for Gemini API to hide API key from frontend.
"""

from __future__ import annotations

import os
from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Request, WebSocket
except ImportError:  # pragma: no cover - lightweight fallback for non-API environments
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail
            super().__init__(f"{status_code}: {detail}")

    class Request:  # type: ignore[override]
        async def json(self) -> dict[str, Any]:
            return {}

    class WebSocket:  # type: ignore[override]
        query_params: dict[str, str] = {}

        async def accept(self) -> None:
            return None

        async def close(self, code: int = 1000, reason: str = "") -> None:
            return None

    class APIRouter:  # type: ignore[override]
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

router = APIRouter(prefix="/api/gemini", tags=["gemini"])

GEMINI_HTTP_URL = "https://generativelanguage.googleapis.com"


def get_api_key() -> str:
    """Get Gemini API key from environment."""
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="API key not configured")
    return key


@router.post("/generate")
async def proxy_generate(request: Request) -> dict[str, Any]:
    """Proxy HTTP requests to Gemini API."""
    api_key = get_api_key()
    data = await request.json()

    model = data.get("model", "gemini-2.0-flash-exp")
    url = f"{GEMINI_HTTP_URL}/v1beta/models/{model}:generateContent"

    import httpx

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                url,
                json=data.get("body", data),
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key,
                },
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Gemini API error: {e.response.text}",
            ) from e
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Request failed: {str(e)}",
            ) from e


@router.websocket("/live")
async def proxy_live_websocket(websocket: WebSocket) -> None:
    """Placeholder for Gemini Live proxy; currently not implemented."""
    await websocket.accept()
    await websocket.close(code=1011, reason="Gemini live proxy not implemented")


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    api_key = get_api_key()

    import httpx

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{GEMINI_HTTP_URL}/v1beta/models",
                headers={"x-goog-api-key": api_key},
            )
            if response.status_code == 200:
                return {"status": "healthy", "gemini": "connected"}
            return {
                "status": "degraded",
                "gemini": f"error_{response.status_code}",
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
