#!/bin/bash
# 🌌 AetherOS — Deployment Oracle (V1.0)
# Deploys the full-stack AetherOS environment in containerized mode.

set -e

# Visuals
CYAN='\033[96m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${CYAN}${BOLD}⟡ AETHER DEPLOYMENT SIGNAL ⟡${RESET}"

# 1. Check for API Key
if [ -z "$GOOGLE_API_KEY" ]; then
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    if [ -z "$GOOGLE_API_KEY" ]; then
        echo "❌ Error: GOOGLE_API_KEY is not set. Please add it to your .env or export it."
        exit 1
    fi
fi

# 2. Build and Launch
echo "🚀 Initializing Containers..."
docker compose build

echo "✨ Igniting AetherOS Stack..."
docker compose up -d

echo -e "\n${CYAN}✦ AetherOS is now live!${RESET}"
echo "  - Portal (HUD): http://localhost:3000"
echo "  - Kernel (Gateway): ws://localhost:18789"
echo "  - Admin API: http://localhost:18790"
echo -e "\n${BOLD}Speak anytime — The Aether is listening.${RESET}"
