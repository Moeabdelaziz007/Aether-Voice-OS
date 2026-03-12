# Voice-to-Agent Quick Start Guide

## 🎯 What Was Implemented

Three major feature sets for voice-first agent creation and management:

### 1. End-to-End Voice-to-Agent Creation
- User speaks agent definition (name, persona, skills)
- System extracts structure via Gemini function calling
- Agent saved to Firestore with idempotency
- Spoken confirmation of success/failure
- Automatic rollback on write failure

### 2. Dynamic Widgets from Gemini Output
- Gemini generates WidgetSpec[] based on context
- Schema validation prevents malformed content
- Component registry maps types to React components
- Auto-layout widgets in grid system
- Priority-based rendering (high/medium/low)

### 3. GemiGram Interface
- Telegram-like voice-first UI
- 3-panel layout: Agents | Main | Widgets
- Real-time voice activity indicator
- Global voice command router
- Keyboard accessibility (dev-only fallback)

---

## 🚀 Quick Integration Steps

### Step 1: Add Firebase Environment Variables

In Vercel project settings (Settings > Vars):

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=your_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_domain.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_bucket.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

### Step 2: Import GemiGram Interface

```typescript
// In your main page or layout
import GemiGramInterface from '@/components/gemigram/GemiGramInterface';

export default function Page() {
  return <GemiGramInterface />;
}
```

### Step 3: Create Agent via Voice

```typescript
// In a voice handler
import { createAgentFromVoice } from '@/services/agentService';

const agentInput = {
  name: 'Atlas',
  persona: 'A helpful assistant that...',
  skills: ['research', 'analysis', 'writing'],
};

const { agentId, agent, isNew } = await createAgentFromVoice(
  agentInput,
  'unique-idempotency-key' // Optional but recommended
);
```

### Step 4: Render Dynamic Widgets

```typescript
// From Gemini function call response
import { parseGeminiWidgetResponse } from '@/services/widgets/planner';
import { renderWidgets } from '@/services/widgets/registry';

const geminiResponse = {
  function: 'create_widgets',
  widgets: [ /* WidgetSpec[] */ ]
};

const { widgets } = parseGeminiWidgetResponse(geminiResponse);
const rendered = renderWidgets(widgets);
```

---

## 📝 Voice Command Examples

```bash
# Open existing agent
"Open agent Atlas"

# Create new agent
"Create agent Assistant"

# Deploy agent
"Deploy"

# Manage UI
"Show widgets"
"Hide widgets"

# Get help
"Help"
"What can you do?"
```

---

## 🔧 File Reference

### Core Services

| File | Purpose |
|------|---------|
| `lib/validation.ts` | Zod schemas for all inputs |
| `services/agentService.ts` | Agent CRUD + idempotency |
| `services/widgets/schema.ts` | Widget type definitions |
| `services/widgets/registry.tsx` | Component rendering map |
| `services/widgets/planner.ts` | Widget layout & optimization |

### UI Components

| File | Purpose |
|------|---------|
| `components/gemigram/GemiGramInterface.tsx` | Main container |
| `components/gemigram/AgentListPanel.tsx` | Agent list with status |
| `components/gemigram/VoiceControlPanel.tsx` | Microphone button |
| `components/gemigram/WidgetPanel.tsx` | Dynamic widgets |
| `components/gemigram/VoiceActivityIndicator.tsx` | Real-time status |
| `components/gemigram/GlobalVoiceRouter.tsx` | Command parser |

---

## 🛡️ Error Handling

All functions include comprehensive error handling:

```typescript
try {
  const result = await createAgentFromVoice(input);
} catch (error) {
  if (error instanceof ZodError) {
    // Validation error - show user-friendly message
    console.error('Invalid agent input:', error.errors);
  } else if (error.code === 'auth/unauthenticated') {
    // Authentication error
    console.error('Please log in first');
  } else {
    // Firebase or network error
    console.error('Failed to create agent:', error.message);
  }
}
```

---

## 🎨 Customization

### Register Custom Widget Component

```typescript
import { registerCustomWidget } from '@/services/widgets/registry';
import MyCustomWidget from './MyCustomWidget';

registerCustomWidget('my_custom_type', MyCustomWidget);
```

### Add New Voice Command

Edit `GlobalVoiceRouter.tsx`, add pattern:

```typescript
{
  pattern: /my\s+command\s+(\w+)/i,
  intent: 'my_intent',
  entityKey: 'myEntity',
}
```

### Extend Agent Schema

Add fields to Firestore schema:

```typescript
interface FirestoreAgent {
  // ... existing fields
  customField?: string; // Add new field
  customMetadata?: Record<string, any>;
}
```

---

## 📊 Database Schema

### Firestore Structure

```
users/{uid}/
├── agents/{agentId}
│   ├── id: string
│   ├── name: string
│   ├── persona: string
│   ├── skills: string[]
│   ├── tools: string[]
│   ├── status: 'draft' | 'active' | 'archived'
│   ├── createdAt: timestamp
│   ├── updatedAt: timestamp
│   └── userId: string
```

### Idempotency Cache

In-memory cache of recent creations:
- TTL: 1 hour
- Auto-cleanup on access
- Returns existing agent if duplicate detected

---

## 🔐 Security Features

1. **Input Validation**
   - Zod schemas enforce type safety
   - Range checks on string lengths
   - Pattern matching for names

2. **User Isolation**
   - Agents scoped to user ID
   - No cross-user access possible
   - Firestore RLS recommended

3. **Idempotency**
   - Prevents duplicate creation
   - Reduces database writes
   - Safe for retries

4. **Error Safety**
   - Graceful fallbacks
   - No sensitive data in logs
   - User-friendly error messages

---

## 🧪 Testing Voice Commands

```typescript
// Manual testing script
const testTranscript = "Create agent named TestBot";
const command = parseVoiceCommand(testTranscript);
console.log(command); // { intent: 'create_agent', entities: { agentName: 'TestBot' } }
```

---

## 🐛 Debugging

Enable detailed logging:

```typescript
// Set in components
console.log('[VoiceRouter] Processing:', transcript);
console.log('[AgentService] Creating agent:', input);
console.log('[WidgetPlanner] Parsed response:', widgets);
```

Monitor in:
- Browser DevTools Console
- Firestore Logs (Firebase Console)
- Terminal Logs (Zustand store)

---

## ⚡ Performance Tips

1. **Batch Agent Creation**
   ```typescript
   const { agentIds, failed } = await batchCreateAgents(inputs);
   ```

2. **Optimize Widget Rendering**
   ```typescript
   const optimized = optimizeWidgetPlan(plan, maxWidgets: 10);
   ```

3. **Cache Widget Components**
   ```typescript
   const Component = useMemo(() => getWidgetComponent(type), [type]);
   ```

---

## 📱 Mobile Considerations

- Microphone button is touch-friendly (large target)
- Voice activity indicator visible on all devices
- Widgets adapt to smaller screens (responsive grid)
- Animations use GPU-accelerated transforms

---

## 🎓 Example: Complete Voice Flow

```typescript
// 1. User speaks (handled by VoiceControlPanel)
// "Create agent named ResearchAssistant with skills writing and analysis"

// 2. Transcript received
const transcript = "Create agent named ResearchAssistant...";

// 3. GlobalVoiceRouter parses it
const command = parseVoiceCommand(transcript);
// { intent: 'create_agent', entities: { agentName: 'ResearchAssistant' } }

// 4. Execute command (in real app, Gemini extracts full details)
const agentInput = {
  name: 'ResearchAssistant',
  persona: 'A research-focused agent...',
  skills: ['writing', 'analysis'],
};

// 5. Create in Firestore
const { agentId, agent } = await createAgentFromVoice(agentInput);

// 6. Gemini generates widgets based on agent
const widgets = parseGeminiWidgetResponse({
  function: 'create_widgets',
  widgets: [
    { type: 'skill_toggle', props: { skillName: 'writing' } },
    { type: 'skill_toggle', props: { skillName: 'analysis' } },
  ]
});

// 7. Render widgets on screen
renderWidgets(widgets);

// 8. Speak confirmation
// "Research Assistant created successfully"
```

---

## 🔗 Related Documentation

- [Voice Features Summary](./VOICE_FEATURES_SUMMARY.md)
- [Firebase Setup](./FIREBASE_SETUP.md)
- [Troubleshooting](./TROUBLESHOOTING.md)

---

**Ready to integrate? Start with the 4 quick steps above! 🚀**
