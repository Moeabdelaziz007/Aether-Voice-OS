"""
Aether Voice OS — Gemini Proxy API

Secure backend proxy for Gemini API to hide API key from frontend.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException, Request, WebSocket

router = APIRouter(prefix="/api/gemini", tags=["gemini"])

GEMINI_HTTP_URL = "https://generativelanguage.googleapis.com"


def _http_error(status_code: int, code: str, message: str) -> HTTPException:
    """Create a consistent HTTPException payload."""
    return HTTPException(
        status_code=status_code,
        detail={
            "error": {
                "code": code,
                "message": message,
            }
        },
    )


def get_api_key() -> str:
    """Get Gemini API key from environment."""
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise _http_error(
            status_code=500,
            code="GEMINI_API_KEY_MISSING",
            message="GOOGLE_API_KEY is not configured on the server.",
        )
    return key


@router.post("/generate")
async def proxy_generate(request: Request) -> dict[str, Any]:
    """Proxy HTTP requests to Gemini API."""
    import httpx

    api_key = get_api_key()
    data = await request.json()

    model = data.get("model", "gemini-2.0-flash-exp")
    url = f"{GEMINI_HTTP_URL}/v1beta/models/{model}:generateContent"

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
        except httpx.HTTPStatusError as exc:
            raise _http_error(
                status_code=exc.response.status_code,
                code="GEMINI_HTTP_ERROR",
                message="Gemini API returned a non-success response.",
            ) from exc
        except httpx.RequestError as exc:
            raise _http_error(
                status_code=502,
                code="GEMINI_UPSTREAM_UNREACHABLE",
                message=f"Could not reach Gemini API: {exc}",
            ) from exc


@router.websocket("/live")
async def proxy_live_websocket(websocket: WebSocket) -> None:
    """Temporarily disabled websocket proxy for Gemini Live API."""
    await websocket.accept()
    await websocket.send_json(
        {
            "error": {
                "code": "LIVE_PROXY_DISABLED",
                "message": (
                    "The Gemini Live WebSocket proxy is temporarily disabled "
                    "until a full bidirectional bridge is implemented."
                ),
            }
        }
    )
    await websocket.close(code=1013, reason="Gemini live proxy disabled")


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for Gemini connectivity."""
    import httpx

    api_key = get_api_key()

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{GEMINI_HTTP_URL}/v1beta/models",
                headers={"x-goog-api-key": api_key},
            )
            response.raise_for_status()
            return {"status": "healthy", "gemini": "connected"}
        except httpx.HTTPStatusError as exc:
            raise _http_error(
                status_code=exc.response.status_code,
                code="GEMINI_HEALTHCHECK_HTTP_ERROR",
                message="Gemini health check received a non-success response.",
            ) from exc
        except httpx.RequestError as exc:
            raise _http_error(
                status_code=502,
                code="GEMINI_HEALTHCHECK_UNREACHABLE",
                message=f"Gemini health check failed: {exc}",
            ) from exc
