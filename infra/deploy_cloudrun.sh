#!/bin/bash
# Aether-Voice-OS: Gemini Live Cloud Run Deployer (V3)
# ═════════════════════════════════════════════════════

PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="aether-gateway-live"
REGION="us-central1"

echo "🚀 Deploying Aether-Voice-OS to Cloud Run..."

# Build the container
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME} .

# Deploy the service
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_API_KEY=${GOOGLE_API_KEY}" \
  --set-env-vars="AETHER_JWT_SECRET=${AETHER_JWT_SECRET}" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600

echo "✅ Deployment complete. Service URL:"
gcloud run services describe ${SERVICE_NAME} --format 'value(status.url)' --region ${REGION}
