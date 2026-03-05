"""
Aether Voice OS — Gemini Proxy API

Secure backend proxy for Gemini API to hide API key from frontend.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/gemini", tags=["gemini"])

GEMINI_WS_URL = "wss://generativelanguage.googleapis.com/ws"
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
    """Proxy WebSocket connections to Gemini Live API."""
    await websocket.accept()
    api_key = get_api_key()
    model = websocket.query_params.get(
        "model", "gemini-2.5-flash-preview-native-audio-dialog"
    )
    
    ws_url = f"{GEMINI_WS_URL}/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={api_key}"
    
    async with httpx.AsyncClient() as client:
        gemini_ws = None
        try:
            async with client.stream("GET", ws_url) as response:
                if response.status_code != 200:
                    await websocket.close(code=1011, reason="Gemini connection failed")
                    return
                
                async def forward_to_gemini():
                    """Forward messages from client to Gemini."""
                    try:
                        while True:
                            data = await websocket.receive_text()
                            await gemini_ws.send_text(data)
                    except WebSocketDisconnect:
                        pass
                    except Exception as e:
                        print(f"Forward error: {e}")
                
                async def forward_to_client():
                    """Forward messages from Gemini to client."""
                    try:
                        while True:
                            data = await gemini_ws.receive_text()
                            await websocket.send_text(data)
                    except Exception as e:
                        print(f"Receive error: {e}")
                
                await asyncio.gather(
                    forward_to_gemini(),
                    forward_to_client(),
                )
        except Exception as e:
            await websocket.close(code=1011, reason=str(e))


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


import asyncio  # noqa: E402
