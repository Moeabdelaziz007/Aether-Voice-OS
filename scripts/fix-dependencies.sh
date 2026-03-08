#!/bin/bash
set -e

echo "[v0] Starting dependency sync..."
cd /vercel/share/v0-project/apps/portal

echo "[v0] Current directory: $(pwd)"
echo "[v0] Node version: $(node --version)"
echo "[v0] npm version: $(npm --version)"

echo "[v0] Installing dependencies..."
npm install --legacy-peer-deps

echo "[v0] Dependencies installed successfully"
echo "[v0] Checking firebase..."
npm list firebase

echo "[v0] Dependency sync complete!"
