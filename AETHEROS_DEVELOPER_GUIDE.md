# AetherOS Developer Guide — Phase 12

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [State Management (Zustand)](#state-management)
3. [Server Actions](#server-actions)
4. [Components](#components)
5. [CSS Variable System](#css-variable-system)
6. [Widget System](#widget-system)
7. [Intent Parsing](#intent-parsing)
8. [Testing](#testing)
9. [Accessibility](#accessibility)
10. [Performance Tips](#performance-tips)

---

## Architecture Overview

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   ThemeProvider (Context)                   │
│  Manages CSS variable updates for zero-latency theming      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼──────────┐                 ┌─────────▼──────────┐
│  BackgroundEngine │                 │   TerminalFeed    │
│  • SVG grain      │                 │  • Log display    │
│  • Grid overlay   │                 │  • Auto-scroll    │
│  • Scanlines      │                 │  • Interruption   │
└───────────────────┘                 └───────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼──────────┐          ┌─────────▼──────────┐
│     Omnibar      │          │ GenerativePortal   │
│  • Intent input  │          │ • Widget renderer  │
│  • Intent parse  │          │ • Widget lifecycle │
│  • Widget inject │          │                    │
└───────────────────┘          └───────────────────┘
        │
        └─────────────────┬────────────────────┐
                          │                    │
                ┌─────────▼──────┐    ┌─────────▼──────┐
                │ useAetherStore │    │ Server Actions │
                │  (Zustand)     │    │  (800ms async) │
                └────────────────┘    └────────────────┘
```

### Key Concepts

- **Zero-Latency Theme Switching**: CSS variables updated on :root directly, bypassing React re-renders
- **Graceful Degradation**: 800ms timeout on API calls with automatic fallback to localStorage cache
- **Intent Parsing**: Omnibar detects user intent (skills, persona, theme) and injects appropriate widget
- **Smart Auto-Scroll**: Terminal maintains sticky scroll only when user at bottom; pauses on manual scroll

---

## State Management

### Zustand Store Structure

Located in `/src/store/useAetherStore.ts`

#### Core State Slices

```typescript
// Terminal Feed State
terminalLogs: TerminalLog[];           // Color-coded log entries
isInterrupted: boolean;                 // Voice interruption flag
scrollPaused: boolean;                  // Manual scroll pause
streamingBuffer: string;                // Typewriter effect buffer

// Skills Management
activeSkills: Skill[];                  // Enabled/disabled skills
cachedSkills: Skill[];                  // Fallback cache from localStorage
skillsSyncStatus: SkillsSyncStatus;     // 'idle' | 'syncing' | 'success' | 'cached' | 'failed'

// Persona Configuration
personaConfig: PersonaConfig;           // tone, formality, verbosity
// Possible values:
// - tone: 'analytical' | 'creative' | 'neutral'
// - formality: 'formal' | 'casual' | 'technical'
// - verbosity: 'concise' | 'balanced' | 'verbose'

// Theme Configuration
themeConfig: ThemeConfig;               // Active theme + visual settings
// - currentTheme: 'matrix-core' | 'quantum-cyan' | 'cyber-amber' | 'ghost-white'
// - glowIntensity: 0-1 (maps to CSS var)
// - blurIntensity: 3-24px
// - grainEnabled: boolean
// - scanlinesEnabled: boolean

// Generative UI
activeWidgets: { id: string; type: string; props: any }[];
```

#### Key Actions

```typescript
// Terminal
addTerminalLog(level, message, widgetId?)  // Add log entry
clearTerminalLogs()                         // Clear all logs
setInterrupted(boolean)                     // Set interruption flag
setScrollPaused(boolean)                    // Toggle scroll pause

// Skills
setActiveSkills(Skill[])                    // Set active skills list
toggleSkill(skillId)                        // Toggle individual skill
setSkillsSyncStatus(status)                 // Update sync status

// Persona
setPersonaConfig(Partial<PersonaConfig>)    // Update persona settings

// Theme
setThemeConfig(Partial<ThemeConfig>)        // Update theme
setVisualSettings(Partial<VisualSettings>)  // Update visual effects

// Widgets
addWidget(type, props)                      // Inject widget
removeWidget(id)                            // Remove widget
clearWidgets()                              // Clear all widgets
```

#### Persistence

Store automatically persists to localStorage via Zustand middleware:
- Terminal logs (last 50)
- Persona config
- Theme settings
- Cached skills

Restore on app load: `useAetherStore.getState()` reads from localStorage

---

## Server Actions

Located in `/src/app/actions/`

### terminalActions.ts

```typescript
/**
 * Process user intent and stream response logs
 * @param userInput - User command text
 * @param personaConfig - Persona settings (optional)
 * @param activeSkills - Active skills list (optional)
 */
export async function processIntent(
    userInput: string,
    personaConfig?: PersonaConfig,
    activeSkills?: string[]
)

/**
 * Stream agent response character-by-character
 * Generator function for streaming responses
 */
export async function* streamAgentResponse(message: string)

/**
 * Direct log addition for optimistic updates
 */
export async function addTerminalLogAction(
    level: TerminalLog['level'],
    message: string
)
```

### skillsActions.ts

**Key Feature: 800ms Timeout + Graceful Fallback**

```typescript
/**
 * Sync skills with clawhib.ai API (with timeout)
 * - Hard timeout: 800ms
 * - Falls back to localStorage cache on timeout
 * - Logs: "[SYS] clawhib.ai sync delayed. Using local cached skills. [OK]"
 */
export async function syncSkillsWithFallback()

/**
 * Toggle individual skill on/off
 * @param skillId - Skill ID to toggle
 */
export async function toggleSkill(skillId: string)

/**
 * Get current active skills
 */
export async function getActiveSkills()

/**
 * Initialize skills on app load
 */
export async function initializeSkills()
```

### personaActions.ts

```typescript
/**
 * Build LLM system prompt from persona config
 * Generates instructions based on tone, formality, verbosity
 */
export async function buildSystemPrompt(
    personaConfig: PersonaConfig
): Promise<string>

/**
 * Update persona configuration
 * Logs changes to terminal
 */
export async function updatePersona(
    config: Partial<PersonaConfig>
)

/**
 * Apply pre-built persona preset
 * - 'analytical_engineer'
 * - 'friendly_mentor'
 * - 'concise_assistant'
 */
export async function applyPersonaPreset(presetName: string)
```

---

## Components

### ThemeProvider.tsx

**Purpose**: Zero-latency CSS variable updates without React re-renders

```typescript
/**
 * ThemeProvider Context
 * - Watches themeConfig in Zustand
 * - Updates :root CSS variables directly
 * - No component re-renders on theme change
 */
export default function ThemeProvider({ children })

/**
 * Hook to use theme
 */
export function useTheme() {
  return {
    setTheme: (name: ThemeType) => {},
    setAccentColor: (hex: string) => {},
    setGlowIntensity: (value: 0-1) => {},
    toggleGrain: () => {},
    toggleScanlines: () => {},
    // ... etc
  };
}
```

### BackgroundEngine.tsx

**Purpose**: SVG grain texture + grid/scanline overlays

```typescript
/**
 * BackgroundEngine Component
 * Features:
 * - Procedural SVG grain (feTurbulence)
 * - Optional animated grid
 * - Optional CRT scanlines
 * - Fixed positioning with z-index layering
 * - 3-5% opacity for subtlety
 */
export default function BackgroundEngine()
```

### TerminalFeed.tsx

**Purpose**: Scrollable log display with smart auto-scroll

```typescript
/**
 * TerminalFeed Component
 * Features:
 * - Smart auto-scroll: Sticky at bottom, pause on manual scroll
 * - Voice interruption handling
 * - Color-coded log levels
 * - Hover effects for readability
 * - Mobile responsive (responsive font sizes, touch-friendly)
 * - Keyboard accessible (Tab, Space, Arrow keys)
 * - Screen reader support (aria-live region)
 */
export default function TerminalFeed()

// Logs capped at 50 entries (auto-pruning)
// Format: [LEVEL] message (timestamp)
```

### SkillsManagerWidget.tsx

```typescript
/**
 * Skills Manager Widget
 * Terminal-style interface for skill toggling
 * - Displays active/cached skills
 * - Shows sync status: [SYNCING] → [SUCCESS]|[CACHED]|[FAILED]
 * - Gracefully handles 800ms timeout
 */
export function SkillsManagerWidget()
```

### PersonaConfigWidget.tsx

```typescript
/**
 * Persona Config Widget
 * - 3 quick presets (analytical_engineer, friendly_mentor, concise_assistant)
 * - Tone selector (analytical | creative | neutral)
 * - Formality selector (formal | casual | technical)
 * - Verbosity selector (concise | balanced | verbose)
 * - Real-time system prompt generation
 */
export function PersonaConfigWidget()
```

### ThemeSettingsWidget.tsx

```typescript
/**
 * Theme Settings Widget
 * - 4 theme swatches (Matrix Core, Quantum Cyan, Cyber Amber, Ghost White)
 * - Glow Intensity slider (0-100%)
 * - Blur Intensity slider (3-40px)
 * - Grain Texture toggle
 * - Scanlines toggle
 * - Live preview as sliders move
 */
export function ThemeSettingsWidget()
```

### WidgetRegistry.tsx

```typescript
/**
 * Central registry of all widgets
 * Maps widget type string to React component
 */
export const WIDGET_REGISTRY: Record<string, React.FC> = {
  'system_status': SystemStatusWidget,
  'port_registry': PortStatusWidget,
  'skills_manager': SkillsManagerWidget,
  'persona_config': PersonaConfigWidget,
  'theme_settings': ThemeSettingsWidget,
};
```

### Omnibar.tsx

```typescript
/**
 * Omnibar Component
 * Features:
 * - 3-level intent system (Quick, Discuss, Agent)
 * - Intent parsing with keyword detection
 * - Automatic widget injection
 * - Keyboard shortcuts: ⌘K to open, Enter to execute, Esc to close
 * - Optimistic UI feedback
 * - Status indicator (connected/disconnected)
 */
export default function Omnibar()
```

---

## CSS Variable System

Located in `/src/app/globals.css`

### Theme Variables

```css
:root {
  /* Matrix Core (default) */
  --bg-primary: #0B0B0C;
  --text-primary: #00FF41;
  --text-secondary: #AAAAAA;
  --text-dim: #555555;
  --accent-primary: #00FF41;
  --glow-primary: rgba(0, 255, 65, 0.4);
  
  /* Glassmorphism */
  --blur-light: 12px;
  --blur-heavy: 24px;
  --glass-opacity: 0.9;
  
  /* Log Level Colors */
  --log-sys: #00FF41;        /* System: Green */
  --log-voice: #00FFFF;      /* Voice input: Cyan */
  --log-agent: #FFB000;      /* Agent response: Amber */
  --log-success: #10B981;    /* Success: Emerald */
  --log-error: #FF5555;      /* Error: Red */
  --log-skills: #00E5FF;     /* Skills: Cyan */
  --log-persona: #FF99FF;    /* Persona: Magenta */
  --log-theme: #FFD700;      /* Theme: Gold */
  
  /* Glow Effects */
  --glow-intensity: 1;       /* 0-1 scale */
  --glow-color: rgba(0, 255, 65, 0.4);
  
  /* Typography */
  --f-mono: 'Geist Mono', monospace;
  --f-sans: 'Geist', sans-serif;
}

/* Theme 1: Matrix Core */
:root.theme-matrix-core {
  --bg-primary: #0B0B0C;
  --text-primary: #00FF41;
  --glow-color: rgba(0, 255, 65, 0.4);
}

/* Theme 2: Quantum Cyan */
:root.theme-quantum-cyan {
  --bg-primary: #050914;
  --text-primary: #00E5FF;
  --glow-color: rgba(0, 229, 255, 0.3);
}

/* Theme 3: Cyber Amber */
:root.theme-cyber-amber {
  --bg-primary: #110F0A;
  --text-primary: #FFB000;
  --glow-color: rgba(255, 176, 0, 0.3);
}

/* Theme 4: Ghost White */
:root.theme-ghost-white {
  --bg-primary: #000000;
  --text-primary: #FFFFFF;
  --glow-color: rgba(255, 255, 255, 0.2);
}
```

### Updating CSS Variables from JavaScript

```typescript
// In ThemeProvider.tsx
const root = document.documentElement;

// Update color
root.style.setProperty('--text-primary', '#00FF41');

// Update numeric value
root.style.setProperty('--glow-intensity', String(0.8));

// Update pixel value
root.style.setProperty('--blur-heavy', '24px');
```

### Creating New Theme

```typescript
// 1. Add theme type
export type ThemeType = '...' | 'my-new-theme';

// 2. Add CSS
:root.theme-my-new-theme {
  --bg-primary: #1a1a1a;
  --text-primary: #FF0000;
  --glow-color: rgba(255, 0, 0, 0.4);
}

// 3. Use in UI
getState().setThemeConfig({ currentTheme: 'my-new-theme' });
```

---

## Widget System

### Creating Custom Widget

```typescript
/**
 * MyCustomWidget.tsx
 */
'use client';

import React from 'react';
import { useAetherStore } from '@/store/useAetherStore';

/**
 * MyCustomWidget — Description of functionality
 * 
 * Features:
 * - Feature 1
 * - Feature 2
 */
export function MyCustomWidget() {
    const addTerminalLog = useAetherStore(s => s.addTerminalLog);
    
    const handleAction = () => {
        addTerminalLog('SYS', 'Custom widget action performed');
    };
    
    return (
        <div style={{
            padding: '1rem',
            border: '1px solid var(--text-dim)',
            borderRadius: '4px',
            background: 'rgba(255,255,255,0.02)',
        }}>
            <h3 style={{ color: 'var(--text-primary)' }}>My Custom Widget</h3>
            <button onClick={handleAction}>
                Perform Action
            </button>
        </div>
    );
}
```

### Register in WidgetRegistry

```typescript
// In WidgetRegistry.tsx
import { MyCustomWidget } from './MyCustomWidget';

export const WIDGET_REGISTRY: Record<string, React.FC> = {
    // ... existing widgets
    'my_custom_widget': MyCustomWidget,
};
```

### Inject Widget

```typescript
// From Omnibar or any component
useAetherStore.getState().addWidget('my_custom_widget', {
    // Pass props here
    customProp: 'value',
});
```

---

## Intent Parsing

Located in `/src/components/shared/Omnibar.tsx`

### Intent Detection Keywords

```typescript
const intentMap = {
    'skills_manager': ['manage skills', 'toggle skill', 'skills', 'sync skills', 'what skills'],
    'persona_config': ['persona', 'set tone', 'change formality', 'change verbosity', 'preset'],
    'theme_settings': ['theme', 'display settings', 'change theme', 'glow', 'blur', 'scanlines'],
};
```

### Adding New Intent

1. **Add keywords to intent map**
```typescript
intentMap['my_new_widget'] = ['keyword1', 'keyword2', ...];
```

2. **Register widget in WidgetRegistry**

3. **Test intent parsing**
```bash
npm test -- aetheros-e2e.test.ts
```

---

## Testing

### E2E Test Suite

Located in `/src/__tests__/aetheros-e2e.test.ts`

#### Test Categories

1. **Graceful Degradation**: 800ms timeout + cache fallback
2. **Widget Injection**: Intent → widget injection flow
3. **Theme Switching**: CSS variable updates
4. **Skills Management**: Toggle, sync, status
5. **Persona Configuration**: Tone, formality, verbosity
6. **Voice Interruption**: Clearing widgets, resetting state
7. **Terminal Logging**: Log entries, color coding, auto-pruning
8. **Auto-Scroll**: Sticky scroll, pause/resume behavior

#### Running Tests

```bash
# Run all tests
npm test

# Run E2E tests only
npm test -- aetheros-e2e.test.ts

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

#### Writing New Tests

```typescript
describe('Phase X — Feature Name', () => {
    beforeEach(() => {
        // Setup: Clear state before each test
        const { getState } = useAetherStore;
        getState().clearTerminalLogs();
    });

    it('should [do something]', async () => {
        // Arrange
        const { getState } = useAetherStore;
        
        // Act
        await act(async () => {
            // Perform action
        });
        
        // Assert
        expect(getState().someState).toEqual(expectedValue);
    });
});
```

---

## Accessibility

### Reference

See `ACCESSIBILITY_AUDIT.md` for complete WCAG AA compliance checklist.

### Key Patterns

#### Screen Reader Support

```tsx
// Log container
<div
    role="log"
    aria-live="polite"
    aria-label="Terminal log feed"
>
    {logs.map(log => (
        <div key={log.id} role="status">
            {log.message}
        </div>
    ))}
</div>

// Interactive element
<button
    aria-label="Toggle skill"
    aria-pressed={isActive}
    aria-describedby="skill-desc"
>
    Toggle
</button>
```

#### Keyboard Navigation

```typescript
// In Omnibar
const handleKeyDown = (e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        toggleOmnibar();
    }
    if (e.key === 'Enter') {
        executeCommand();
    }
    if (e.key === 'Escape') {
        closeOmnibar();
    }
};
```

#### Focus Management

```typescript
// Visible focus indicator
button:focus {
    outline: 2px solid var(--text-primary);
    outline-offset: 2px;
    box-shadow: 0 0 8px var(--glow-color);
}
```

---

## Performance Tips

### 1. Minimize Store Subscriptions

```typescript
// ✅ Good: Specific selector
const skills = useAetherStore(s => s.activeSkills);

// ❌ Bad: Entire store (causes unnecessary re-renders)
const state = useAetherStore();
```

### 2. Memoize Expensive Calculations

```typescript
const personaPrompt = useMemo(() => {
    return buildSystemPrompt(personaConfig);
}, [personaConfig]);
```

### 3. Use React.memo for Widget Components

```typescript
export const MyWidget = React.memo(function MyWidget() {
    // Only re-renders if props change
    return <div>...</div>;
});
```

### 4. Avoid Inline Functions in JSX

```typescript
// ✅ Good
const handleClick = useCallback(() => {
    // ...
}, [dependencies]);

// ❌ Bad
<button onClick={() => doSomething()}>Click</button>
```

### 5. Code Splitting for 3D Scene

```typescript
// In page.tsx
const UnifiedScene = dynamic(() => import('@/components/UnifiedScene'), {
    ssr: false,
    loading: () => <LoadingPlaceholder />,
});
```

### 6. CSS Variable Updates (Zero-Latency Theming)

```typescript
// ✅ Good: Direct CSS property update, no React re-render
root.style.setProperty('--text-primary', newColor);

// ❌ Bad: State update triggers component re-render
const [color, setColor] = useState(newColor);
```

### 7. Defer Expensive Operations

```typescript
// Use setTimeout for non-critical updates
setTimeout(() => {
    syncSkillsWithFallback(); // Non-blocking
}, 100);
```

---

## Troubleshooting

### Terminal Logs Not Updating

```typescript
// Check: Are you calling addTerminalLog correctly?
useAetherStore.getState().addTerminalLog('SYS', 'My message');

// Check: Is TerminalFeed subscribed to terminalLogs?
const terminalLogs = useAetherStore((s) => s.terminalLogs);
```

### Theme Not Applying

```typescript
// Check: CSS variables updated on :root?
console.log(document.documentElement.style.getPropertyValue('--text-primary'));

// Check: ThemeProvider wrapping app?
// <ThemeProvider><App /></ThemeProvider>
```

### Widget Not Injecting

```typescript
// Check: Is widget registered in WidgetRegistry?
import { WIDGET_REGISTRY } from '@/components/generative/WidgetRegistry';
console.log(WIDGET_REGISTRY['my_widget']); // Should not be undefined

// Check: Is intent parsing detecting keyword?
// Add console.log in Omnibar intent parsing logic
```

### Skills Sync Hanging

```typescript
// Check: Is 800ms timeout working?
console.log(useAetherStore.getState().skillsSyncStatus);
// Should transition: 'syncing' → 'success'|'cached'|'failed' within 900ms

// Check: Is cache available?
console.log(useAetherStore.getState().cachedSkills);
```

---

## Resources

- [Next.js Docs](https://nextjs.org/docs)
- [Zustand Docs](https://github.com/pmndrs/zustand)
- [React Docs](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Framer Motion](https://www.framer.com/motion/)

---

## Questions?

Refer to component JSDoc comments for detailed API documentation:
- `src/components/TerminalFeed.tsx`
- `src/components/ThemeProvider.tsx`
- `src/components/shared/Omnibar.tsx`
- `src/app/actions/skillsActions.ts`
