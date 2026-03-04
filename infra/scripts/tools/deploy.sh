#!/bin/bash

# 🧬 Aether OS — Automated Cloud Deployment Script (GCP)
# This script builds and deploys the Aether Brain/Gateway to Cloud Run.

set -e # Exit on error

# Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="aether-engine"
REGION="us-central1"

echo "🚀 Starting Aether OS Moonshot Deployment..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# 1. Enable Required APIs
echo "📡 Enabling Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    firestore.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    --quiet

# 2. Build the Docker Image
echo "📦 Building Artifacts with Cloud Build..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME .

# 3. Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="AETHER_AI_API_VERSION=v1alpha,AETHER_AI_MODEL=gemini-2.0-flash-exp" \
    --quiet

echo "✅ Aether Brain successfully deployed!"
echo "Endpoint: $(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')"
echo "---"
echo "Next Step: update your local .env AETHER_GW_HOST to point to the Cloud Run URL."
