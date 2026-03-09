#!/bin/bash
set -e

# Aether Voice OS — Firebase Deployment Script
# (Note: Kept filename as infra/deploy_cloudrun.sh to satisfy CI constraints,
# but this deploys to Firebase as requested)

echo "Building and deploying Aether Voice OS to Firebase..."

# Ensure required environment variables
if [ -z "$GCP_SERVICE_KEY" ] || [ -z "$FIRESTORE_PROJECT" ] || [ -z "$GEMINI_API_KEY" ]; then
  echo "Error: Missing required environment variables (GCP_SERVICE_KEY, FIRESTORE_PROJECT, GEMINI_API_KEY)."
  exit 1
fi

if [ -z "$NEXT_PUBLIC_FIREBASE_API_KEY" ]; then
  echo "Warning: NEXT_PUBLIC_FIREBASE_API_KEY is not set. Frontend may not build properly."
fi

PROJECT_ID=$FIRESTORE_PROJECT

# Auth with Firebase/Google using service account key
echo "$GCP_SERVICE_KEY" > /tmp/gcp_key.json
export GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp_key.json

echo "Setting up environment configuration for frontend..."
echo "NEXT_PUBLIC_AETHER_GATEWAY_URL=$NEXT_PUBLIC_AETHER_GATEWAY_URL" > apps/portal/.env.production
echo "NEXT_PUBLIC_FIRESTORE_PROJECT=$FIRESTORE_PROJECT" >> apps/portal/.env.production

if [ -n "$NEXT_PUBLIC_FIREBASE_API_KEY" ]; then
  echo "NEXT_PUBLIC_FIREBASE_API_KEY=$NEXT_PUBLIC_FIREBASE_API_KEY" >> apps/portal/.env.production
  echo "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=$NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN" >> apps/portal/.env.production
  echo "NEXT_PUBLIC_FIREBASE_PROJECT_ID=$NEXT_PUBLIC_FIREBASE_PROJECT_ID" >> apps/portal/.env.production
  echo "NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=$NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET" >> apps/portal/.env.production
  echo "NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=$NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID" >> apps/portal/.env.production
  echo "NEXT_PUBLIC_FIREBASE_APP_ID=$NEXT_PUBLIC_FIREBASE_APP_ID" >> apps/portal/.env.production
fi

# Install dependencies and build frontend
echo "Building Portal Frontend..."
cd apps/portal
npm ci
npm run build
cd ../..

# Firebase deploy
echo "Deploying to Firebase (Project: $PROJECT_ID)..."
npx firebase-tools use "$PROJECT_ID"
npx firebase-tools deploy --non-interactive --project "$PROJECT_ID"

# Clean up credentials
rm /tmp/gcp_key.json

DEPLOY_OUT="https://$PROJECT_ID.web.app"
echo "$DEPLOY_OUT" > infra/deployed_url.txt
echo "Deployment successful! URL saved to infra/deployed_url.txt: $DEPLOY_OUT"
