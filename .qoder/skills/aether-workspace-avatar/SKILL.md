---
name: aether-workspace-avatar
description: Control 3D mobile avatar in Living Workspace with navigation, gestures, and autonomous task execution. Use when implementing avatar mobility, gesture systems, or workspace automation.
---

# Aether Workspace Avatar

## Overview

This skill controls the mobile 3D avatar system from Aether OS v3.0 Living Workspace - an autonomous entity that navigates, works, and organizes while users observe and collaborate.

## When to Use

Use this skill when:
- Implementing 3D avatar navigation and movement
- Creating gesture-based interactions
- Building autonomous task execution workflows
- Designing living workspace interfaces
- Adding real-time activity streams

## Core Components

### 1. Mobile Avatar Controller

Controls avatar position, state, and movement.

**Avatar States**:
```typescript
enum AvatarState {
  IDLE = 'idle',           // Breathing animation
  NAVIGATING = 'navigating', // Moving to target
  WORKING = 'working',     // Performing task
  SPEAKING = 'speaking',   // Lip sync active
  THINKING = 'thinking',   // Processing
  ERROR = 'error'         // Error feedback
}
```

**Usage**:
```typescript
import { useAvatar } from '@/hooks/useAvatar';

const { avatar, moveTo, setGesture } = useAvatar();

// Navigate to app
await moveTo({ x: 400, y: 300 });

// Set working state
setAvatarState(AvatarState.WORKING);
```

### 2. Gesture System

Comprehensive gesture vocabulary for interaction.

**Available Gestures**:
- **Point**: Direct attention to element
- **Grab**: Interact with draggable items
- **Type**: Simulate typing animation
- **Press**: Click buttons/controls
- **Wave**: Greeting/acknowledgment
- **Nod**: Agreement/confirmation

**Usage**:
```typescript
interface Gesture {
  type: 'point' | 'grab' | 'type' | 'press' | 'wave' | 'nod';
  target?: string;
  duration?: number;
  animation: string;
}

// Execute gesture
executeGesture({
  type: 'point',
  target: 'gmail-app',
  duration: 1500
});
```

### 3. Pathfinding Engine

Autonomous navigation with obstacle avoidance.

**Features**:
- A* pathfinding algorithm
- Dynamic obstacle avoidance
- Smooth curve interpolation
- Waypoint optimization

**Usage**:
```typescript
const pathfinder = new Pathfinder();

const path = await pathfinder.findPath(
  startPosition: { x: 0, y: 0 },
  endPosition: { x: 800, y: 600 },
  obstacles: appPositions
);

// Returns optimized waypoints
// [{x: 100, y: 50}, {x: 400, y: 300}, ...]
```

### 4. Activity Stream

Real-time feed of avatar and user actions.

**Structure**:
```typescript
interface ActivityItem {
  id: string;
  timestamp: Date;
  avatarAction: string;
  userAction?: string;
  app: string;
  status: 'started' | 'completed' | 'failed' | 'in-progress';
  progress?: number;
  details?: string;
}
```

**Usage**:
```typescript
import { useActivityStream } from '@/hooks/useActivityStream';

const { activities, addActivity } = useActivityStream();

// Log avatar action
addActivity({
  avatarAction: 'Navigating to Gmail',
  app: 'gmail',
  status: 'in-progress',
  progress: 0.6
});
```

## Workspace Architecture

### Canvas System

Infinite workspace canvas with pan/zoom:

```typescript
interface WorkspaceCanvas {
  id: string;
  dimensions: { width: number; height: number };
  backgroundColor: string;
  gridSize: number;
  zoomLevel: number;
  panPosition: { x: number; y: number };
}
```

### App Dock

Drag-and-drop app management:

```typescript
interface DockApp {
  id: string;
  name: string;
  icon: string;
  type: 'google-workspace' | 'development' | 'widget' | 'skill';
  isPinned: boolean;
  isRunning: boolean;
}
```

**Categories**:
1. Google Workspace (Gmail, Calendar, Drive, Tasks)
2. Development Tools (VSCode, GitHub, Terminal)
3. Widgets (Weather, Crypto, News, Stocks)
4. Skills (Custom AI agent skills)

## Workflow Patterns

### Autonomous Task Execution

```typescript
async function executeTask(task: string) {
  // 1. Parse task requirements
  const requirements = parseTask(task);
  
  // 2. Select appropriate app
  const targetApp = selectApp(requirements);
  
  // 3. Navigate to app
  await avatar.moveTo(targetApp.position);
  
  // 4. Execute task with gestures
  setGesture({ type: 'type', content: task.input });
  setGesture({ type: 'press', target: 'submit-button' });
  
  // 5. Report completion
  stream.addActivity({
    avatarAction: `Completed: ${task}`,
    status: 'completed'
  });
}
```

### Gesture Sequence

```typescript
const emailWorkflow = [
  { type: 'navigate', target: gmailPosition },
  { type: 'gesture', name: 'point', target: 'compose-btn' },
  { type: 'gesture', name: 'press', target: 'compose-btn' },
  { type: 'gesture', name: 'type', content: emailBody },
  { type: 'gesture', name: 'point', target: 'send-btn' },
  { type: 'gesture', name: 'press', target: 'send-btn' }
];

await executeGestureSequence(emailWorkflow);
```

## Configuration

### Avatar Settings

```typescript
const AVATAR_CONFIG = {
  movement: {
    speed: 300, // pixels per second
    acceleration: 150,
    deceleration: 200,
    turnSpeed: 0.8
  },
  gestures: {
    defaultDuration: 1000,
    smoothTransitions: true,
    enableMicroExpressions: true
  },
  appearance: {
    theme: 'quantum-neural',
    colorScheme: 'neo-green',
    opacity: 0.95
  }
};
```

### Theme Variables

```css
:root {
  /* Quantum Highlights */
  --neo-green-primary: #39FF14;
  --quantum-blue: #00FFFF;
  --topology-purple: #8B2FFF;
  
  /* Carbon Base */
  --void-primary: #020003;
  --carbon-weave: #1A1A1F;
}
```

## Testing

### Component Tests

```typescript
import { render, screen } from '@testing-library/react';
import { MobileAvatar } from '@/components/MobileAvatar';

test('avatar navigates to target position', async () => {
  render(<MobileAvatar />);
  
  const avatar = screen.getByTestId('avatar');
  fireEvent.click(screen.getByText('Move to Gmail'));
  
  await waitFor(() => {
    expect(avatar).toHaveStyle('transform: translate(400px, 300px)');
  });
});
```

### Gesture Tests

```typescript
test('executes point gesture correctly', () => {
  const { result } = renderHook(() => useGesture());
  
  act(() => {
    result.current.execute({
      type: 'point',
      target: 'test-element'
    });
  });
  
  expect(result.current.activeGesture).toBe('point');
  expect(result.current.gestureTarget).toBe('test-element');
});
```

### E2E Tests (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test('avatar completes email workflow', async ({ page }) => {
  await page.goto('/workspace');
  
  // Trigger avatar to compose email
  await page.click('#compose-email-btn');
  
  // Watch avatar navigate and type
  await expect(page.locator('#avatar'))
    .toHaveAttribute('data-state', 'working');
  
  // Verify email sent
  await expect(page.locator('#sent-confirmation'))
    .toBeVisible();
});
```

## Performance Metrics

- **Avatar Frame Rate**: 60 FPS maintained
- **Gesture Recognition**: 95% accuracy
- **Pathfinding Latency**: <50ms average
- **Movement Smoothness**: 120 interpolation steps/sec

## Troubleshooting

### Issue: Avatar Gets Stuck

**Solutions**:
1. Check obstacle map accuracy
2. Increase pathfinding search radius
3. Add escape behavior for deadlocks
4. Implement fallback straight-line path

### Issue: Gestures Not Recognized

**Solutions**:
1. Calibrate gesture recognition thresholds
2. Increase training data for ML model
3. Add manual override option
4. Improve visual feedback during recognition

### Issue: Janky Movement

**Solutions**:
1. Optimize canvas re-rendering
2. Use CSS transforms instead of position updates
3. Implement requestAnimationFrame loop
4. Reduce unnecessary state updates

## Advanced Patterns

### Predictive Navigation

```typescript
class PredictiveNavigator {
  predictNextDestination(): Position {
    const history = this.getActivityHistory();
    const patterns = this.extractPatterns(history);
    
    // User always opens Calendar after Gmail in morning
    if (patterns.morningRoutine && this.atGmail()) {
      return this.calendarPosition;
    }
    
    return null; // No prediction
  }
}
```

### Emotion-Based Animation

```typescript
function animateWithEmotion(baseAnimation: string, emotion: string) {
  const emotionModifiers = {
    excited: { speed: 1.5, amplitude: 1.3 },
    frustrated: { speed: 0.7, amplitude: 0.8 },
    thinking: { speed: 0.5, amplitude: 0.6 },
    neutral: { speed: 1.0, amplitude: 1.0 }
  };
  
  const modifier = emotionModifiers[emotion];
  applyAnimationModifier(baseAnimation, modifier);
}
```

## Examples

### Example 1: Morning Routine

```typescript
// Avatar autonomously executes morning checklist
const morningRoutine = [
  { app: 'calendar', action: 'show-today' },
  { app: 'gmail', action: 'summarize-unread' },
  { app: 'weather', action: 'display-forecast' },
  { app: 'crypto', action: 'show-prices' }
];

for (const task of morningRoutine) {
  await avatar.navigateTo(task.app);
  await avatar.executeGesture(task.action);
  await sleep(3000); // Let user see each app
}
```

### Example 2: User Collaboration

```typescript
// User drags app to canvas
onAppDrop(app, position) {
  // Avatar acknowledges and moves to help
  avatar.say("Great choice! Let me set that up for you.");
  avatar.moveTo(position);
  avatar.executeGesture('type', { content: app.defaultData });
}
```

## Related Resources

- [Workspace Plan](#)
- [Workspace Updates](#)
- [Avatar Implementation Guide](#)

## Security Considerations

- Sandbox avatar actions to prevent DOM manipulation
- Validate all gesture targets
- Implement rate limiting on autonomous actions
- Provide manual override controls
- Audit all automated workflows
