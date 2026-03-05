#!/usr/bin/env python3
"""
Aether Voice OS — Zero-Friction Entry Point.

Launch the standalone voice agent with a single command:

    python main.py

The agent will:
  1. Load configuration from .env
  2. Open your microphone and speaker
  3. Connect to Gemini Live over the internet
  4. Start listening immediately — just talk

Compatible with Aether skill specifications and
ADK (Agent Development Kit) lifecycle patterns.
"""

from __future__ import annotations

import asyncio
import importlib
import os
import sys
from pathlib import Path

# Ensure the project root is on sys.path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Load .env before anything else reads env vars
try:
    from dotenv import load_dotenv

    load_dotenv(ROOT.parent / ".env")
except ImportError:
    pass  # dotenv is optional; env vars can be set externally


def print_banner() -> None:
    """Print the Aether startup banner."""
    CYAN = "\033[96m"
    PURPLE = "\033[95m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    print(
        f"""
{CYAN}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   {BOLD}⟡  AETHER VOICE OS  ⟡{RESET}{CYAN}                                ║
║                                                          ║
║   {PURPLE}Standalone Live Agent — Gemini Native Audio{RESET}{CYAN}            ║
║   {DIM}Voice-first • Always listening • Tool-integrated{RESET}{CYAN}        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{RESET}
"""
    )


def check_api_key() -> None:
    """Verify the API key is configured before starting."""
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("AETHER_AI_API_KEY")
    if not key:
        YELLOW = "\033[93m"
        RED = "\033[91m"
        RESET = "\033[0m"
        print(
            f"""
{RED}✗ No API key found.{RESET}

{YELLOW}Set your Gemini API key in one of these ways:{RESET}

  1. Create a .env file:
     echo 'GOOGLE_API_KEY=your-key-here' > .env

  2. Export directly:
     export GOOGLE_API_KEY='your-key-here'

  Get a key at: https://aistudio.google.com/apikey
"""
        )
        sys.exit(1)


def check_dependencies() -> list[str]:
    """Check that critical dependencies are available."""
    missing = []
    try:
        importlib.import_module("pyaudio")
    except ImportError:
        missing.append("pyaudio")
    try:
        importlib.import_module("google.genai")
    except ImportError:
        missing.append("google-genai")
    try:
        importlib.import_module("pydantic_settings")
    except ImportError:
        missing.append("pydantic-settings")
    return missing


def main() -> None:
    """Main entry point."""
    print_banner()

    # Pre-flight checks
    check_api_key()

    missing = check_dependencies()
    if missing:
        RED = "\033[91m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"
        print(f"{RED}✗ Missing dependencies: {', '.join(missing)}{RESET}")
        print(f"{YELLOW}  Install with: pip install {' '.join(missing)}{RESET}")
        sys.exit(1)

    # Import engine only after checks pass
    from core.engine import AetherEngine
    from core.infra.service_container import Container
    
    container = Container()
    
    DIM = "\033[2m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    print(f"{DIM}Starting engine...{RESET}")
    print(f"{CYAN}Speak anytime — Aether is listening.{RESET}")
    print(f"{DIM}Press Ctrl+C to stop.{RESET}\n")

    try:
        engine = container.get('aetherengine')
        print(
            f"{CYAN}✦ Admin API Listening on http://localhost:18790/health "
            f"(Tauri Bridge Active){RESET}"
        )
        asyncio.run(engine.run())
    except KeyboardInterrupt:
        print(f"\n{DIM}Aether signing off. 🌑{RESET}")
    except EnvironmentError as exc:
        RED = "\033[91m"
        RESET = "\033[0m"
        print(f"{RED}Configuration error: {exc}{RESET}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
