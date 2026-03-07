#!/bin/bash
# 🔙 AetherOS — Firebase Rollback Script
# Quickly rollback to previous Firebase Hosting version

set -e

CYAN='\033[96m'
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
RESET='\033[0m'

print_header() {
    echo -e "\n${CYAN}${BOLD}⟡ $1 ⟡${RESET}\n"
}

print_header "FIREBASE ROLLBACK"

# Check if firebase-tools is installed
if ! command -v firebase &> /dev/null; then
    echo -e "${RED}❌ Firebase CLI not found. Install with: npm install -g firebase-tools${RESET}"
    exit 1
fi

# Get project ID from .firebaserc
PROJECT_ID=$(jq -r '.projects.default' .firebaserc 2>/dev/null || echo "")

if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID="notional-armor-456623-e8"
    echo -e "${YELLOW}⚠️  Using default project: $PROJECT_ID${RESET}"
fi

echo -e "${BOLD}Project:${RESET} $PROJECT_ID"
echo ""

# List recent releases
print_header "RECENT RELEASES"

firebase hosting:releases list --project "$PROJECT_ID" | head -20

echo ""
echo -e "${YELLOW}Instructions:${RESET}"
echo "1. Copy the version number you want to rollback to (e.g., 10)"
echo "2. Press Ctrl+C to cancel"
echo "3. Or press Enter to rollback to previous version"
echo ""

read -p "Rollback to version: " VERSION

if [ -z "$VERSION" ]; then
    VERSION="-1"  # Previous version
fi

echo ""
echo -e "${CYAN}🔄 Rolling back to version $VERSION...${RESET}"

# Perform rollback
firebase hosting:rollback "$VERSION" --project "$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Rollback successful!${RESET}"
    echo ""
    echo -e "${BOLD}Live URL:${RESET} https://$PROJECT_ID.web.app"
    echo -e "${YELLOW}Note: Changes may take 30-60 seconds to propagate globally${RESET}"
else
    echo ""
    echo -e "${RED}❌ Rollback failed. Check Firebase Console for details.${RESET}"
    exit 1
fi
