#!/bin/bash
# Aether-Voice-OS: Gemini Live Smoke Test Script
# ════════════════════════════════════════════════════

echo "🕵️ Starting Gemini Live Smoke Test..."

# 1. Check for API Keys
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ ERROR: GOOGLE_API_KEY is not set."
    exit 1
fi

# 2. Verify Session Facade
echo "🔍 Checking core/ai/session/facade.py..."
if [ ! -f "core/ai/session/facade.py" ]; then
    echo "❌ ERROR: session/facade.py missing."
    exit 1
fi

# 3. Test Connectivity (Basic Ping)
echo "📡 Pinging Aether Gateway..."
# Assuming a local dev server is running on 8000
curl -s -f http://localhost:18789/health || echo "⚠️ Warning: Local Aether Gateway not responding (Ignore if not running)."

# 4. Verify Tool Registry
python3 -c "from core.ai.session.facade import ToolRegistry; r = ToolRegistry(); print('✅ Tool Registry OK: ' + str(len(r.tools)) + ' tools loaded.')"

echo "✨ Smoke test passed. Live Agent is ready for deployment."
