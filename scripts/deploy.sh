#!/bin/bash
# 🌌 AetherOS — Deployment Oracle (V2.0)
# Deploys the full-stack AetherOS environment with Firebase hosting support

set -e

# Visuals
CYAN='\033[96m'
BOLD='\033[1m'
RESET='\033[0m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'

# Function to print section headers
print_header() {
    echo -e "\n${CYAN}${BOLD}⟡ $1 ⟡${RESET}\n"
}

print_header "AETHER DEPLOYMENT ORACLE"

# Parse command line arguments
DEPLOY_FIREBASE=false
DEPLOY_LOCAL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --firebase|-f)
            DEPLOY_FIREBASE=true
            shift
            ;;
        --local|-l)
            DEPLOY_LOCAL=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --firebase, -f    Deploy to Firebase Hosting"
            echo "  --local, -l       Deploy local containerized version"
            echo "  --help, -h        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# If no options specified, deploy both
if [ "$DEPLOY_FIREBASE" = false ] && [ "$DEPLOY_LOCAL" = false ]; then
    DEPLOY_FIREBASE=true
    DEPLOY_LOCAL=true
fi

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

# 2. Firebase Deployment (if requested)
if [ "$DEPLOY_FIREBASE" = true ]; then
    print_header "FIREBASE DEPLOYMENT"
    
    if [ -f "scripts/firebase-deploy.sh" ]; then
        echo "🚀 Running Firebase deployment validator..."
        bash scripts/firebase-deploy.sh
        echo -e "${GREEN}✅ Firebase deployment completed successfully!${RESET}"
    else
        echo -e "${YELLOW}⚠️  Firebase deployment script not found. Skipping Firebase deployment.${RESET}"
    fi
fi

# 3. Local Container Deployment (if requested)
if [ "$DEPLOY_LOCAL" = true ]; then
    print_header "LOCAL CONTAINER DEPLOYMENT"
    
    echo "🚀 Initializing Containers..."
    docker compose build
    
    echo "✨ Igniting AetherOS Stack..."
    docker compose up -d
    
    echo -e "\n${GREEN}✦ AetherOS Local Stack is now live!${RESET}"
    echo "  - Portal (HUD): http://localhost:3000"
    echo "  - Kernel (Gateway): ws://localhost:18789"
    echo "  - Admin API: http://localhost:18790"
fi

# 4. Final Summary
print_header "DEPLOYMENT SUMMARY"

if [ "$DEPLOY_FIREBASE" = true ]; then
    PROJECT_ID=$(jq -r '.projects.default' .firebaserc 2>/dev/null || echo "unknown")
    echo -e "${GREEN}🌐 Firebase Hosting:${RESET} https://$PROJECT_ID.web.app"
fi

if [ "$DEPLOY_LOCAL" = true ]; then
    echo -e "${GREEN}🏠 Local Development:${RESET} http://localhost:3000"
fi

echo -e "\n${BOLD}Speak anytime — The Aether is listening.${RESET}"

# 5. CI/CD Information
print_header "AUTOMATED DEPLOYMENTS"

echo -e "${CYAN}ℹ️  Automated Firebase Deployment is configured!${RESET}"
echo ""
echo "Every push to ${BOLD}main${RESET} branch will automatically:"
echo "  ✅ Build Next.js portal"
echo "  ✅ Run type checking"
echo "  ✅ Deploy to Firebase Hosting"
echo "  ✅ Validate deployment"
echo "  ✅ Send Discord notification"
echo ""
echo "View deployments: https://github.com/${GITHUB_REPOSITORY:-your-repo}/actions"
echo "Rollback anytime: ${BOLD}bash scripts/firebase_rollback.sh${RESET}"
echo ""
