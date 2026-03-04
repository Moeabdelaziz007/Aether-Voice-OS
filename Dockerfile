# ═══════════════════════════════════════════════════════════
# Aether Voice OS — Production Container
# Gemini Live Agent Challenge 2026
# ═══════════════════════════════════════════════════════════
# Multi-stage build:
#   Stage 1: Build Rust signal layer (aether-cortex)
#   Stage 1: Build Rust signal layer (cortex)
#   Stage 2: Slim Python runtime with Rust .so
# ═══════════════════════════════════════════════════════════

# ── Stage 1: Rust build ──────────────────────────────────
FROM rust:bookworm as rust-builder

RUN apt-get update && apt-get install -y \
    clang \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY cortex/ ./cortex/

# Ensure we use release profile for max performance
RUN cd cortex && \
    cargo build --release

# We'll copy the cdylib (.so or .dylib depending on cross-compilation quirks)
RUN cp target/release/libcortex.so /build/cortex.so 2>/dev/null || \
    cp target/release/libcortex.dylib /build/cortex.so 2>/dev/null || true


# ── Stage 2: Python runtime ─────────────────────────────
FROM python:3.11-slim-bookworm AS runtime

# System deps for PyAudio (compilation and runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip for better dependency resolution
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Rust shared library from builder
COPY --from=rust-builder /build/aether_cortex.so /app/core/audio/aether_cortex.so

# Copy application code
COPY core/ ./core/
COPY brain/ ./brain/
COPY main.py .

# Metadata and security labels
LABEL org.opencontainers.image.source="https://github.com/Moeabdelaziz007/Aether-Voice-OS"
LABEL org.opencontainers.image.description="Aether Voice OS — Production Container"
LABEL org.opencontainers.image.authors="Aether Architect"

# Non-root user for security
RUN useradd -m aether && chown -R aether:aether /app
USER aether

# Health check endpoint (gateway WebSocket)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python3 -c "import socket; s=socket.create_connection(('localhost', 18789), 2); s.close()" || exit 1

# Cloud Run uses PORT env var
ENV PORT=18789
EXPOSE 18789

# Entry point
CMD ["python3", "-m", "core.engine"]
