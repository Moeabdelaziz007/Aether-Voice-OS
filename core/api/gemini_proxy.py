"""
Aether Voice OS — Gemini Proxy API

Secure backend proxy for Gemini API to hide API key from frontend.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request, WebSocket

router = APIRouter(prefix="/api/gemini", tags=["gemini"])

GEMINI_WS_URL = "wss://generativelanguage.googleapis.com/ws"
GEMINI_HTTP_URL = "https://generativelanguage.googleapis.com"


def get_api_key() -> str:
    """Get Gemini API key from environment."""
    key = os.getenv("GOOGLE_API_KEY")
    is_benchmark = os.getenv("AETHER_BENCHMARK_MODE", "false").lower() == "true"

    if not key and not is_benchmark:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_API_KEY not configured. Explicit key required unless AETHER_BENCHMARK_MODE=true",
        )
    return key or "AIza_MOCK_KEY_FOR_BENCHMARK"


@router.post("/generate")
async def proxy_generate(request: Request) -> dict[str, Any]:
    """Proxy HTTP requests to Gemini API."""
    api_key = get_api_key()
    data = await request.json()

    model = data.get("model", "gemini-2.5-flash-live-preview-03-2026")
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
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Gemini API error: {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Request failed: {str(e)}")


@router.websocket("/live")
async def proxy_live_websocket(websocket: WebSocket):
    """
    DEPRECATED: Direct Gemini Live proxy is disabled in favor of Aether Gateway (Port 18789).
    This endpoint now serves as a stub for compatibility.
    """
    await websocket.accept()
    await websocket.send_json(
        {
            "type": "error",
            "message": "Direct Gemini Live WS Proxy is DISABLED. Use Aether Gateway Protocol on port 18789.",
            "code": "WS_DISABLED_USE_GATEWAY",
        }
    )
    await websocket.close(code=1000)


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    api_key = get_api_key()

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{GEMINI_HTTP_URL}/v1beta/models",
                headers={"x-goog-api-key": api_key},
            )
            if response.status_code == 200:
                return {"status": "healthy", "gemini": "connected"}
            return {"status": "degraded", "gemini": f"error_{response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
