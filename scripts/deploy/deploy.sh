#!/bin/bash
# 🌌 AetherOS - Deployment Script (Phase 15: The Cloud Strike)
# This script deploys the Backend to GCP Cloud Run and the Frontend to Firebase Hosting.

set -e

# --- Configuration ---
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
SERVICE_NAME="aether-kernel"
HOSTING_DIR="apps/portal"

echo "🚀 Starting Deployment for Project: $PROJECT_ID"

# Check for required environment variables in .env
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found. Please create one based on .env.example"
    exit 1
fi

# Extract keys for Cloud Run
G_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2- | tr -d '\"' | tr -d "'")
JWT_SECRET=$(grep AETHER_JWT_SECRET .env | cut -d '=' -f2- | tr -d '\"' | tr -d "'")

if [ -z "$G_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY missing in .env"
    exit 1
fi

# --- 1. Backend (GCP Cloud Run) ---
echo "📦 Building Backend Container (Google Artifact Registry)..."
# We'll use Cloud Build to keep it simple and serverless
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME .

echo "🚢 Deploying Backend to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 18789 \
    --set-env-vars "GOOGLE_API_KEY=$G_API_KEY,AETHER_JWT_SECRET=$JWT_SECRET,FIRESTORE_PROJECT=$PROJECT_ID" \
    --memory 2Gi \
    --cpu 1

# Get the Backend URL
BACKEND_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
WS_URL=${BACKEND_URL/https/wss}

echo "🔗 Backend Live at: $WS_URL"

# --- 2. Frontend (Firebase Hosting) ---
echo "🏗️ Building Frontend (Next.js 15)..."
cd $HOSTING_DIR

# Inject the production WebSocket URL into the build
NEXT_PUBLIC_AETHER_GATEWAY_URL=$WS_URL npm run build

echo "🧹 Pre-deployment cleanup..."
# Ensure 'out' exists as expected by firebase.json
if [ ! -d "out" ]; then
    echo "❌ Error: Build did not produce an 'out' directory. Check next.config.js for 'output: export'."
    exit 1
fi

cd ../..

echo "🔥 Deploying to Firebase Hosting..."
firebase deploy --only hosting

echo "✅ AetherOS is LIVE and REACHABLE!"
echo "Backend (WS): $WS_URL"
echo "Frontend: Check your Firebase Hosting URL"
