from __future__ import annotations

import os

import jwt

from core.infra.transport.handshake import verify_jwt


def test_verify_jwt_success(monkeypatch):
    monkeypatch.setenv("AETHER_JWT_SECRET", "s")
    token = jwt.encode({"sub": "abc"}, "s", algorithm="HS256")
    assert verify_jwt(token) is True


def test_verify_jwt_fails_without_secret(monkeypatch):
    monkeypatch.delenv("AETHER_JWT_SECRET", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    token = jwt.encode({"sub": "abc"}, "s", algorithm="HS256")
    assert verify_jwt(token) is False
