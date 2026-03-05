#!/bin/bash
# 🌌 AetherOS — Firebase Deployment Validator & Deployer
# Validates Firebase configuration and deploys the portal

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${CYAN}${BOLD}⟡ AETHER FIREBASE DEPLOYMENT VALIDATOR ⟡${RESET}"
echo

# 1. Check Firebase CLI installation
echo -e "${BLUE}Checking Firebase CLI...${RESET}"
if ! command -v firebase &> /dev/null; then
    echo -e "${RED}❌ Firebase CLI not found. Installing...${RESET}"
    npm install -g firebase-tools
else
    echo -e "${GREEN}✅ Firebase CLI installed ($(firebase --version))${RESET}"
fi

# 2. Check authentication
echo -e "${BLUE}Checking Firebase authentication...${RESET}"
if firebase login:list &>/dev/null; then
    echo -e "${GREEN}✅ Firebase authenticated${RESET}"
else
    echo -e "${YELLOW}⚠️  Not authenticated. Please run: firebase login${RESET}"
    exit 1
fi

# 3. Validate project configuration
echo -e "${BLUE}Validating Firebase project configuration...${RESET}"
if [ ! -f "firebase.json" ]; then
    echo -e "${RED}❌ firebase.json not found${RESET}"
    exit 1
fi

if [ ! -f ".firebaserc" ]; then
    echo -e "${RED}❌ .firebaserc not found${RESET}"
    exit 1
fi

PROJECT_ID=$(jq -r '.projects.default' .firebaserc)
echo -e "${GREEN}✅ Project configured: $PROJECT_ID${RESET}"

# 4. Check required files
echo -e "${BLUE}Checking required deployment files...${RESET}"

PORTAL_OUT="apps/portal/out"
if [ ! -d "$PORTAL_OUT" ]; then
    echo -e "${YELLOW}⚠️  Portal build not found. Building...${RESET}"
    cd apps/portal
    npm run build
    cd ../..
else
    echo -e "${GREEN}✅ Portal build found${RESET}"
fi

# 5. Validate firebase.json configuration
echo -e "${BLUE}Validating firebase.json...${RESET}"
if jq -e '.hosting' firebase.json >/dev/null 2>&1; then
    HOSTING_PUBLIC=$(jq -r '.hosting.public' firebase.json)
    echo -e "${GREEN}✅ Hosting configured for: $HOSTING_PUBLIC${RESET}"
    
    if [ ! -d "$HOSTING_PUBLIC" ]; then
        echo -e "${RED}❌ Hosting directory $HOSTING_PUBLIC does not exist${RESET}"
        exit 1
    fi
else
    echo -e "${RED}❌ No hosting configuration found in firebase.json${RESET}"
    exit 1
fi

# 6. Check Firestore configuration
echo -e "${BLUE}Validating Firestore configuration...${RESET}"
if [ -f "firestore.rules" ]; then
    echo -e "${GREEN}✅ Firestore rules found${RESET}"
fi

if [ -f "firestore.indexes.json" ]; then
    echo -e "${GREEN}✅ Firestore indexes configuration found${RESET}"
fi

# 7. Test build
echo -e "${BLUE}Testing portal build...${RESET}"
cd apps/portal
BUILD_STATUS=$(npm run build 2>&1)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Portal builds successfully${RESET}"
else
    echo -e "${RED}❌ Portal build failed${RESET}"
    echo "$BUILD_STATUS"
    exit 1
fi
cd ../..

# 8. Deploy
echo
echo -e "${CYAN}${BOLD}Deploying to Firebase...${RESET}"
firebase deploy --only hosting

echo
echo -e "${GREEN}${BOLD}✅ Deployment completed successfully!${RESET}"
echo -e "${BLUE}Visit: https://$PROJECT_ID.web.app${RESET}"