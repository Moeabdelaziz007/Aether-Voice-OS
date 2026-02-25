# 🚀 Aether OS — Deployment Guide (Contest Build)

This guide details how to deploy the **Aether Voice OS** stack to Google Cloud Platform (GCP) to achieve the scalable, low-latency performance required for the Gemini Live Agent Challenge.

## ☁️ Architecture Overview

Aether is designed as a **Cloud-Native Hybrid** system:

- **Edge Node (Local)**: Handles high-fidelity audio I/O via PyAudio C-threads.
- **Brain (GCP)**: Aether Gateway and L2 Synapse Daemons running on Cloud Run.
- **Memory (Firestore)**: Persistent session and knowledge storage.

---

## 🛠️ Step 1: GCP Infrastructure Setup

### 1. Enable APIs

```bash
gcloud services enable \
    run.googleapis.com \
    firestore.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com
```

### 2. Configure Firebase (Firestore)

Aether requires Firestore in Native Mode.

1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Initialize Firestore in your project.
3. Add a service account to `core/tools/firebase_key.json` (Local) or use ADC (Cloud).

---

## 📦 Step 2: Containerization & Cloud Run

Aether is deployed as a stateless container that orchestrates the Gemini Live connection.

### 1. Build the Docker Image

```bash
gcloud builds submit --tag gcr.io/[PROJECT_ID]/aether-engine .
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy aether-engine \
    --image gcr.io/[PROJECT_ID]/aether-engine \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_API_KEY=[YOUR_KEY],AETHER_AI_MODEL=gemini-2.0-flash-exp"
```

---

## 🔒 Step 3: Secret Management (V0.2)

For production security, move keys into GCP Secret Manager:

```bash
echo -n "AIzaSy..." | gcloud secrets create GEMINI_KEY --data-file=-
gcloud run deploy aether-engine --update-secrets=GOOGLE_API_KEY=GEMINI_KEY:latest
```

---

## ⚡ Automated Deployment

Run the included `deploy.sh` for a one-click deployment experience:

```bash
chmod +x deploy.sh
./deploy.sh
```
