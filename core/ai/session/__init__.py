"""Gemini session package facade."""

__all__ = ["GeminiLiveSession"]


def __getattr__(name: str):
    if name == "GeminiLiveSession":
        from core.ai.session.facade import GeminiLiveSession

        return GeminiLiveSession
    raise AttributeError(name)
