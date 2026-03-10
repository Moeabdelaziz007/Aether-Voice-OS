#!/bin/bash
# 🌌 AetherOS - Zero-Budget Tunneling Deployment
# This script bypasses GCP billing by using Localtunnel for the Backend
# and Firebase Hosting for the Frontend.

set -e

# --- Configuration ---
PORT=18789
HOSTING_DIR="apps/portal"

echo "🚀 Starting Zero-Budget Deployment (Localtunnel)..."

# 1. Kill any existing tunnel or gateway
echo "🧹 Cleaning up existing processes..."
pkill -f "localtunnel" || true
pkill -f "core/server.py" || true

# 2. Start the Backend Gateway in the background
echo "📡 Starting Aether Core Gateway on port $PORT..."
export PYTHONPATH=$PYTHONPATH:.
python3 core/server.py > gateway.log 2>&1 &
BACKEND_PID=$!

# Wait for gateway to be ready
echo "⏳ Waiting for gateway to initialize..."
sleep 5

# 3. Start Localtunnel and capture URL
echo "🚇 Initializing Localtunnel..."
# We use npx to avoid global installation
LT_URL=$(npx localtunnel --port $PORT --print-requests=false | grep -o 'https://[^ ]*' | head -1)

if [ -z "$LT_URL" ]; then
    echo "❌ Error: Failed to generate Localtunnel URL."
    kill $BACKEND_PID
    exit 1
fi

# Convert https to wss for the gateway
WS_URL=${LT_URL/https/wss}

echo "🔗 Tunnel established: $LT_URL"
echo "🛠️ WebSocket Target: $WS_URL"

# 4. Build Frontend with the Tunnel URL
echo "🏗️ Building Frontend (Next.js 15)..."
cd $HOSTING_DIR

# Inject the tunnel WebSocket URL into the build
NEXT_PUBLIC_AETHER_GATEWAY_URL=$WS_URL npm run build

echo "🧹 Pre-deployment cleanup..."
if [ ! -d "out" ]; then
    echo "❌ Error: Build did not produce an 'out' directory."
    cd ../..
    kill $BACKEND_PID
    exit 1
fi

cd ../..

# 5. Deploy to Firebase Hosting
echo "🔥 Deploying to Firebase Hosting..."
firebase deploy --only hosting

echo "✅ AetherOS is LIVE and TUNNELED!"
echo "------------------------------------------------"
echo "Live Frontend: [Check Firebase URL]"
echo "Backend Status: Running locally (PID $BACKEND_PID)"
echo "Tunnel URL: $LT_URL"
echo "------------------------------------------------"
echo "⚠️  Keep this terminal open to keep the backend alive for judges."

# Wait for processes
wait $BACKEND_PID
