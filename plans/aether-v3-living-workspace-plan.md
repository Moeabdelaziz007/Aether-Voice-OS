# Aether OS V3.0 Living AI Workspace Architecture Plan

## Executive Summary

Transform Aether OS from a static dashboard into a **Living AI Workspace** - a dynamic, interactive environment where a 3D avatar actively works, navigates, and organizes while the user observes and collaborates in real-time.

---

## 1. Vision: The Living Workspace Paradigm

### Core Concept

- **From**: Static dashboard with widgets and panels
- **To**: Dynamic workspace where AI avatar actively performs tasks
- **Experience**: User watches avatar navigate, work, and organize in real-time

### Key Differentiators

- **Mobile 3D Avatar**: QuantumNeuralAvatar evolves into a mobile, working entity
- **Autonomous Operation**: Avatar performs tasks independently while user observes
- **Interactive Workspace**: Drag-and-drop apps, real-time activity stream
- **Living Environment**: Workspace responds to avatar's actions and user interactions

---

## 2. Theme Design System

### Color Palette (Topology + Quantum + Carbon Fiber)

```css
:root {
  /* Void & Dark Base */
  --void-primary: #020003;
  --carbon-weave: #1A1A1F;
  
  /* Structure & Depth */
  --carbon-structure: #4A4A52;
  --medium-gray: #6B6B70;
  
  /* Quantum Highlights */
  --neo-green-primary: #39FF14;
  --quantum-blue: #00FFFF;
  --topology-purple: #8B2FFF;
  
  /* Accent Colors */
  --success-green: #39FF14;
  --warning-amber: #FFBF00;
  --error-red: #FF3855;
}
```

### Carbon Fiber Texture CSS

```css
.carbon-fiber {
  background:
    radial-gradient(
      circle at 20% 50%,
      rgba(74, 74, 82, 0.3) 0%,
      transparent 50%
    ),
    radial-gradient(
      circle at 80% 20%,
      rgba(26, 26, 31, 0.4) 0%,
      transparent 50%
    ),
    linear-gradient(
      135deg,
      #1A1A1F 0%,
      #4A4A52 25%,
      #1A1A1F 50%,
      #4A4A52 75%,
      #1A1A1F 100%
    );
  background-size: 100px 100px;
}
```

### Quantum Topology Overlay

```css
.topology-overlay {
  background-image:
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0, 255, 255, 0.03) 2px,
      rgba(0, 255, 255, 0.03) 4px
    ),
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 2px,
      rgba(139, 47, 255, 0.02) 2px,
      rgba(139, 47, 255, 0.02) 4px
    ),
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 4px,
      rgba(57, 255, 20, 0.01) 4px,
      rgba(57, 255, 20, 0.01) 8px
    );
  animation: quantum-pulse 30s infinite linear;
}

@keyframes quantum-pulse {
  0% { opacity: 0.05; }
  50% { opacity: 0.15; }
  100% { opacity: 0.05; }
}
```

---

## 3. Workspace Architecture

### 3.1 Canvas Layout

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

### 3.2 App Dock (Left Sidebar)

```typescript
interface AppDock {
  position: 'left' | 'right' | 'top' | 'bottom';
  width: number;
  height: number;
  apps: DockApp[];
  isExpanded: boolean;
}

interface DockApp {
  id: string;
  name: string;
  icon: string;
  type: 'google-workspace' | 'development' | 'widget' | 'skill';
  component: React.ComponentType;
  isPinned: boolean;
  isRunning: boolean;
}
```

### 3.3 Draggable Workspace Apps

```typescript
interface WorkspaceApp {
  id: string;
  name: string;
  type: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  zIndex: number;
  isResizable: boolean;
  isMovable: boolean;
  state: Record<string, any>;
}
```

### 3.4 Floating Panels

```typescript
interface FloatingPanel {
  id: string;
  title: string;
  content: React.ReactNode;
  position: { x: number; y: number };
  size: { width: number; height: number };
  isVisible: boolean;
  isModal: boolean;
  canDrag: boolean;
}
```

### 3.5 Activity Stream

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

### 3.6 Bottom Control Bar

```typescript
interface ControlBar {
  isVisible: boolean;
  controls: ControlItem[];
  statusIndicators: StatusIndicator[];
}

interface ControlItem {
  id: string;
  icon: string;
  action: () => void;
  isActive: boolean;
}
```

---

## 4. 3D Avatar System

### 4.1 Avatar States

```typescript
enum AvatarState {
  IDLE = 'idle',
  NAVIGATING = 'navigating',
  WORKING = 'working',
  SPEAKING = 'speaking',
  THINKING = 'thinking',
  ERROR = 'error'
}
```

### 4.2 Gesture System

```typescript
interface Gesture {
  type: 'point' | 'grab' | 'type' | 'press' | 'wave' | 'nod';
  target?: string;
  duration?: number;
  animation: string;
}
```

### 4.3 Movement & Pathfinding

```typescript
interface MovementPath {
  start: { x: number; y: number };
  end: { x: number; y: number };
  waypoints: Array<{ x: number; y: number }>;
  duration: number;
  animationCurve: string;
}
```

### 4.4 Avatar Component Structure

```typescript
interface MobileAvatar {
  id: string;
  name: string;
  position: { x: number; y: number };
  state: AvatarState;
  currentTask: string;
  isSpeaking: boolean;
  isThinking: boolean;
  gestures: Gesture[];
  movementPath?: MovementPath;
}
```

---

## 5. App Dock & Integration System

### 5.1 App Categories

```typescript
enum AppCategory {
  GOOGLE_WORKSPACE = 'google-workspace',
  DEVELOPMENT = 'development',
  WIDGETS = 'widgets',
  SKILLS = 'skills',
  UTILITIES = 'utilities'
}
```

### 5.2 Google Workspace Apps

```typescript
interface GoogleWorkspaceApp {
  id: string;
  name: string;
  icon: string;
  api: 'gmail' | 'calendar' | 'drive' | 'tasks';
  permissions: string[];
  component: React.ComponentType;
}
```

### 5.3 Development Tools

```typescript
interface DevelopmentApp {
  id: string;
  name: string;
  icon: string;
  tool: 'vscode' | 'github' | 'terminal' | 'docker';
  component: React.ComponentType;
}
```

### 5.4 Widgets

```typescript
interface WidgetApp {
  id: string;
  name: string;
  icon: string;
  type: 'weather' | 'crypto' | 'news' | 'stocks' | 'clock';
  component: React.ComponentType;
}
```

### 5.5 Skills as Apps

```typescript
interface SkillApp {
  id: string;
  name: string;
  icon: string;
  skillId: string;
  component: React.ComponentType;
  isRunning: boolean;
}
```

---

## 6. Google Workspace Integration

### 6.1 OAuth 2.0 Authentication

```typescript
interface GoogleAuth {
  clientId: string;
  clientSecret: string;
  redirectUri: string;
  scopes: string[];
  token: {
    access_token: string;
    refresh_token: string;
    expires_in: number;
    token_type: string;
  };
}
```

### 6.2 Gmail API Integration

```typescript
interface GmailService {
  readEmails(userId: string, query?: string): Promise<Email[]>;
  composeEmail(to: string, subject: string, body: string): Promise<string>;
  searchEmails(query: string): Promise<Email[]>;
}

interface Email {
  id: string;
  threadId: string;
  labelIds: string[];
  snippet: string;
  historyId: string;
  internalDate: string;
  payload: {
    mimeType: string;
    headers: Header[];
    body: {
      size: number;
      data?: string;
    };
    parts?: EmailPart[];
  };
}
```

### 6.3 Calendar API Integration

```typescript
interface CalendarService {
  listEvents(calendarId: string, timeMin?: Date, timeMax?: Date): Promise<CalendarEvent[]>;
  createEvent(calendarId: string, event: CalendarEvent): Promise<string>;
  updateEvent(calendarId: string, eventId: string, updates: Partial<CalendarEvent>): Promise<string>;
}

interface CalendarEvent {
  id: string;
  summary: string;
  description: string;
  start: {
    dateTime: string;
    timeZone: string;
  };
  end: {
    dateTime: string;
    timeZone: string;
  };
  attendees?: {
    email: string;
    displayName?: string;
    responseStatus?: string;
  }[];
  reminders?: {
    useDefault: boolean;
    overrides?: {
      method: string;
      minutes: number;
    }[];
  };
}
```

### 6.4 Drive API Integration

```typescript
interface DriveService {
  searchFiles(query: string, fields?: string): Promise<DriveFile[]>;
  uploadFile(filePath: string, metadata: DriveFileMetadata): Promise<string>;
  downloadFile(fileId: string, destinationPath: string): Promise<void>;
}

interface DriveFile {
  id: string;
  name: string;
  mimeType: string;
  size: number;
  createdTime: string;
  modifiedTime: string;
  owners: {
    displayName: string;
    emailAddress: string;
  }[];
}
```

---

## 7. Real-time Activity Stream

### 7.1 Activity Stream Component

```typescript
interface ActivityStream {
  activities: ActivityItem[];
  currentAvatarAction: string;
  isStreaming: boolean;
  filter: ActivityFilter;
  autoScroll: boolean;
}

interface ActivityFilter {
  showUserActions: boolean;
  showAvatarActions: boolean;
  showErrors: boolean;
  showProgress: boolean;
}
```

### 7.2 Real-time Updates

```typescript
interface RealTimeUpdate {
  type: 'avatar-action' | 'user-action' | 'app-event' | 'system-event';
  data: any;
  timestamp: Date;
}
```

---

## 8. Implementation Phases

### Phase 1: Foundation (Weeks 1-2)

- [ ] Create new theme system with CSS variables
- [ ] Build WorkspaceCanvas component
- [ ] Implement AppDock with basic app management
- [ ] Create ActivityStream component
- [ ] Set up bottom control bar

### Phase 2: Avatar Mobility (Weeks 3-4)

- [ ] Design and implement MobileAvatar component
- [ ] Create gesture system and animations
- [ ] Implement pathfinding and movement logic
- [ ] Add avatar state management
- [ ] Integrate avatar with workspace navigation

### Phase 3: App Integration (Weeks 5-6)

- [ ] Implement Google Workspace OAuth
- [ ] Create Gmail, Calendar, Drive services
- [ ] Build development tool integrations
- [ ] Add widget system
- [ ] Convert skills to dock apps

### Phase 4: Activity Stream (Weeks 7-8)

- [ ] Implement real-time activity tracking
- [ ] Create activity stream UI
- [ ] Add progress indicators and status updates
- [ ] Implement filtering and search
- [ ] Add user interaction logging

### Phase 5: Autonomous Operation (Weeks 9-10)

- [ ] Implement autonomous task execution
- [ ] Add avatar decision-making logic
- [ ] Create user observation system
- [ ] Implement error recovery
- [ ] Performance optimization and testing

---

## 9. Migration Path from Current Dashboard

### 9.1 WidgetGrid → App Dock + Workspace Panels

- **Current**: Static grid of widgets
- **New**: Dynamic app dock with draggable workspace panels
- **Migration**: Convert existing widgets to dock apps

### 9.2 SkillsPanel → Skills as Dock Apps

- **Current**: Panel-based skill management
- **New**: Skills as individual dock apps
- **Migration**: Wrap skills in app components

### 9.3 QuantumNeuralAvatar → Mobile 3D Avatar

- **Current**: Static avatar with limited movement
- **New**: Mobile avatar with full workspace navigation
- **Migration**: Enhance existing avatar with mobility features

---

## 10. Key Files to Create/Modify

### 10.1 Frontend Components

```
src/components/workspace/
├── WorkspaceCanvas.tsx
├── AppDock.tsx
├── ActivityStream.tsx
├── MobileAvatar.tsx
├── ControlBar.tsx
└── quantum-topology.css

src/components/apps/
├── GoogleWorkspace/
│   ├── GmailApp.tsx
│   ├── CalendarApp.tsx
│   ├── DriveApp.tsx
│   └── TasksApp.tsx
├── Development/
│   ├── VSCodeApp.tsx
│   ├── GitHubApp.tsx
│   └── TerminalApp.tsx
├── Widgets/
│   ├── WeatherApp.tsx
│   ├── CryptoApp.tsx
│   ├── NewsApp.tsx
│   └── StocksApp.tsx
└── Skills/
    └── SkillApp.tsx
```

### 10.2 Backend Services

```
src/services/
├── google-workspace/
│   ├── auth.ts
│   ├── gmail.ts
│   ├── calendar.ts
│   └── drive.ts
├── workspace-tool.ts
└── workspace-agent.py
```

### 10.3 Theme System

```
src/styles/
├── quantum-topology.css
├── carbon-fiber.css
└── theme-variables.css
```

---

## 11. Technical Considerations

### 11.1 Performance Optimization

- Virtual scrolling for activity stream
- Lazy loading for dock apps
- Canvas optimization for large workspaces
- Avatar animation performance

### 11.2 State Management

- Use Zustand for global state
- Local state for individual components
- Real-time updates via WebSocket
- Offline support with service workers

### 11.3 Accessibility

- Keyboard navigation for all components
- Screen reader support
- High contrast mode
- Reduced motion options

### 11.4 Security

- OAuth 2.0 for Google Workspace
- Content Security Policy
- Input validation and sanitization
- Secure WebSocket connections

---

## 12. Success Metrics

### 12.1 User Engagement

- Time spent watching avatar work
- Number of interactions with dock apps
- Activity stream engagement
- Workspace customization rate

### 12.2 Performance

- Avatar response time (< 100ms)
- App loading time (< 2s)
- Activity stream update latency (< 500ms)
- Memory usage (< 500MB)

### 12.3 User Satisfaction

- Task completion rate
- User feedback scores
- Avatar effectiveness rating
- Workspace usability score

---

*This architecture plan provides a comprehensive roadmap for transforming Aether OS into a Living AI Workspace. The phased approach ensures manageable development while delivering continuous value to users.*

---

## 13. Axiom Integration Upgrade (Fractal Sovereignty + Galaxy Model)

### 13.1 Product Narrative Lock

- **Core Identity**: Embodied Digital Colleague, not a chatbot dashboard
- **Spatial Metaphor**: Each project is a Galaxy; Orb is the central intelligence core
- **Fractal Principle**: Mini systems mirror macro system behavior (micro reflects macro)

### 13.2 Spatial Workspace Model

- **Unified Stage**: Extend `UnifiedScene.tsx` as the single 3D universe
- **Orbital Apps**: Apps appear as planets around the core with focus gravity
- **State-Driven Control**: Agent controls app state APIs instead of raw mouse gestures

### 13.3 Cinematic Protocol (Backend → Frontend)

- Introduce canonical event: `task_pulse`
- Required payload fields:
  - `task_id`, `phase`, `action`, `vibe`
  - `avatar_state`, `avatar_target`, `intensity`
  - `thought`, `latency_ms`, `timestamp`
- Companion events:
  - `workspace_state`
  - `avatar_state`
  - `task_timeline_item`

### 13.4 First AI-First App: Notes Planet

- **Goal**: Launch a NotebookLM-style app with voice-linked notes
- **Experience**: Notes as neural crystals with semantic recall
- **Integration**: Works with existing memory pipeline and mission timeline

### 13.5 72-Hour Execution Slice

- **Day 1**
  - Finalize cinematic event schema
  - Wire gateway event handling in frontend store
  - Add `workspaceGalaxy`, `taskPulse`, and `missionLog` state
- **Day 2**
  - Enable orbital app focus behavior in unified scene
  - Implement Notes Planet shell and open/focus flows
  - Map avatar gaze to focused app target
- **Day 3**
  - Run one end-to-end voice flow with visible cinematic pulses
  - Validate fallback behavior for failed action steps
  - Lock demo script for recording readiness

---

## 14. Galaxy Architecture Spec v1 (Execution Contract)

### 14.1 Core Domain Model

- **Galaxy**: Logical workspace namespace for one project or mission
- **Aether Core**: Central orchestration kernel (internal codename: BlackHoleCore)
- **Planet**: AI agent, tool app, or external integration node
- **Orbit**: Priority and proximity lane around Aether Core
- **Gravity Score**: Routing weight that determines which planet executes next

### 14.2 Galaxy Schema

```json
{
  "galaxy_id": "gal-devops-01",
  "name": "DevOps Galaxy",
  "mode": "execution",
  "focus_planet_id": "planet-voyager-browser",
  "planets": [],
  "policy": {
    "allowed_domains": ["github.com", "docs.python.org"],
    "max_parallel_tasks": 3,
    "sensitive_action_requires_confirm": true
  },
  "created_at": "2026-03-07T00:00:00Z"
}
```

### 14.3 Planet Schema

```json
{
  "planet_id": "planet-notes-codex",
  "type": "app",
  "capabilities": ["note.create", "note.link_voice", "semantic.search"],
  "orbit_lane": "inner",
  "health": "healthy",
  "load": 0.22,
  "confidence": 0.92
}
```

### 14.4 Communication Protocols

- **Control Plane**: `task_pulse`, `avatar_state`, `workspace_state`, `task_timeline_item`
- **Data Plane**: tool arguments/results and structured extraction payloads
- **Telemetry Plane**: latency, retries, failure category, confidence trend
- **Envelope Standard**:
  - `type`: event name
  - `payload`: typed object
  - `protocol_version`: required, starts at `1`
  - `timestamp`: unix ms

### 14.5 Aether Core Routing Algorithm

- **Goal**: choose best planet for each task node with deterministic fallback
- **Scoring Function**:
  - `score = 0.35*capability_match + 0.25*confidence - 0.15*latency - 0.15*load + 0.10*continuity`
- **Routing Steps**:
  - Extract intent and decompose task into nodes
  - Compute score for eligible planets
  - Assign top planet and emit `task_pulse` with `phase=PLANNING`
  - Execute node and re-score if failure/timeout occurs
  - Trigger rollback path when hard failure threshold is hit

### 14.6 Reliability Controls

- Circuit breaker per planet after 3 consecutive hard failures
- Retry budget per task node (max 2 retries)
- Hard timeout tiers:
  - Control step: 120ms target
  - Tool execution step: 2–8s by class
- Rollback contract integrated with deep handover protocol

### 14.7 MultiAgentOrchestrator Integration Points

- Extend handover context with:
  - `galaxy_id`
  - `orbit_lane`
  - `gravity_score`
  - `focus_target`
- Attach control emission hooks:
  - Before handover preparation
  - After transfer success/failure
  - On rollback
- Map orchestration lifecycle to cinematic phases:
  - `NEGOTIATING` → `PLANNING`
  - `TRANSFERRING` → `EXECUTING`
  - `VALIDATING` → `VERIFYING`
  - `COMPLETED/FAILED` final pulse

### 14.8 Performance Targets (SLOs)

- P95 control-event propagation (backend → frontend): `< 80ms`
- P95 avatar visual reaction after pulse: `< 120ms`
- Handover success rate: `>= 97%`
- Wrong-planet routing rate: `<= 3%`
- Rollback completion after critical failure: `< 300ms`
- Dropped control events: `<= 0.5%`

### 14.9 Success Metrics (Product + Engineering)

- Mission visibility completeness in timeline: `>= 95%`
- End-to-end flow success (voice → visible execution): `>= 90%`
- User perceived "agent is alive" rating: `>= 4.5 / 5`
- Demo stability (no fatal stop in 3 runs): `3/3`

---

## 15. Progress Snapshot (Current Round)

### 15.1 Completed

- [x] Added cinematic state contract to frontend store (`avatarCinematicState`, `taskPulse`, `missionLog`, `workspaceGalaxy`)
- [x] Added gateway handlers for `task_pulse`, `avatar_state`, `workspace_state`, `task_timeline_item`
- [x] Upgraded architecture plan with Axiom Integration and Galaxy direction
- [x] Defined Galaxy Architecture Spec v1 with data contracts, routing model, and SLOs

### 15.2 In Progress

- [x] Connect avatar animation graph to cinematic states in 3D scene
- [x] Render mission log HUD component using `missionLog` and `taskPulse`
- [x] Introduce backend event emitters for canonical cinematic protocol

### 15.3 Next Execution Slice

- [ ] Build backend `workspace_tool` with focus/move/materialize actions
- [ ] Add `galaxy_id` to orchestration context and tool traces
- [ ] Run one fully visible voice flow in a single galaxy with fallback path

---

## 16. AIX Mapping Spec v0.1 (Aether Adapter Layer)

### 16.1 Scope and Policy

- AIX integration is **adapter-only** for this phase, not runtime source of truth
- Internal Galaxy/Planet schemas remain canonical during demo cycle
- Supported operations in v0.1:
  - `import_agent_profile.aix` → internal model
  - `export_agent_profile.aix` → portable package

### 16.2 Mapping Matrix (AIX → Aether)

| AIX Field | Aether Target | Notes |
|---|---|---|
| `meta.id` | `planet_id` | Stable identity for imported agent planet |
| `meta.name` | `planet.display_name` | UI label in orbital workspace |
| `meta.version` | `planet.profile_version` | Tracked for migration safety |
| `persona.role` | `planet.persona.role` | Role intent in orchestrator hints |
| `persona.tone` | `planet.persona.tone` | Mapped to voice/style presets |
| `persona.instructions` | `planet.persona.instructions` | High-priority behavioral constraint |
| `skills[]` | `planet.capabilities[]` | Only `enabled=true` imported in v0.1 |
| `tools[]` / tool configs | `planet.tool_bindings` | Bound through ToolRouter aliases |
| `mcp.servers[]` | `planet.mcp_endpoints[]` | Stored with auth policy metadata only |
| `memory.episodic` | `planet.memory.episodic` | Adapter tags for current memory layer |
| `memory.semantic` | `planet.memory.semantic` | Vector index reference key |
| `memory.procedural` | `planet.memory.procedural` | Workflow policy hints |
| `security.checksum` | `planet.integrity.checksum` | Verified on import if present |
| `security.signature` | `planet.integrity.signature` | Validation optional in v0.1 |
| `requirements.hardware/software` | `planet.runtime_requirements` | Informational + preflight checks |
| `network.allowed_domains` | `galaxy.policy.allowed_domains` | Merged with deny-by-default policy |
| `pricing` / `economics` | `planet.commercial_profile` | Stored only, not enforced in runtime |

### 16.3 Mapping Matrix (Aether → AIX)

| Aether Field | AIX Target | Notes |
|---|---|---|
| `planet_id` | `meta.id` | UUID preserved if valid |
| `planet.display_name` | `meta.name` | Human-facing export name |
| `planet.profile_version` | `meta.version` | Semantic version string |
| `planet.persona.*` | `persona.*` | Role/tone/instructions round-trip |
| `planet.capabilities[]` | `skills[]` | Exported as enabled skills |
| `planet.tool_bindings` | `tools[]` | Includes auth mode and limits |
| `planet.mcp_endpoints[]` | `mcp.servers[]` | Endpoint + capability declarations |
| `planet.memory.*` | `memory.*` | Adapter metadata and pointers |
| `planet.integrity.*` | `security.*` | Checksum generated at export |
| `planet.runtime_requirements` | `requirements.*` | Optional block |
| `galaxy.policy.allowed_domains` | `network.allowed_domains` | Exported for portability |

### 16.4 Import Contract (v0.1)

- Accepted formats: YAML, JSON, TOML
- Required minimum fields:
  - `meta.id`
  - `meta.name`
  - `persona.role`
- Import pipeline:
  - Parse
  - Schema validate
  - Integrity verify (if checksum/signature provided)
  - Transform to internal Planet model
  - Register in selected Galaxy
  - Emit `workspace_state` + `task_timeline_item`

### 16.5 Export Contract (v0.1)

- Export source: one internal planet profile + optional galaxy policy overlay
- Export steps:
  - Collect normalized internal model
  - Transform to target AIX format
  - Generate SHA-256 checksum
  - Optionally attach signature metadata
  - Write package and emit mission log event

### 16.6 Validation Rules

- Reject import on:
  - Missing required fields
  - Invalid ID format
  - Tool capabilities outside policy
  - Domain permissions violating galaxy guardrails
- Degrade gracefully on:
  - Unknown optional fields (store under `extensions`)
  - Unsupported pricing/economic keys (preserve without runtime enforcement)

### 16.7 Security and Trust Model

- v0.1:
  - Integrity check preferred, signature optional
  - Domain allowlist enforced by galaxy policy
  - Sensitive tools remain confirmation-gated
- v0.2 target:
  - Mandatory signature for external packages
  - Trust registry for verified publishers

### 16.8 Implementation Files (Planned)

- Backend:
  - `core/adapters/aix_parser.py`
  - `core/adapters/aix_mapper.py`
  - `core/tools/aix_tool.py`
- Frontend:
  - `apps/portal/src/components/apps/AixImportExportPanel.tsx`
  - `apps/portal/src/store/useAetherStore.ts` (import/export state slices)

### 16.9 Acceptance Criteria

- Import one valid AIX package and spawn a usable planet in target galaxy
- Export one internal planet to AIX with checksum generated
- Round-trip test preserves persona + enabled capabilities + policy domains
- Failure paths render graceful mission log entries without runtime crash

---

## 17. Master Execution Todo (All Phases, Mini Subtasks)

### 17.1 Phase A — Cinematic Control Plane

- [x] Add cinematic store contracts (`taskPulse`, `missionLog`, `workspaceGalaxy`)
- [x] Add gateway listeners for cinematic event types
- [x] Add backend canonical emitters for `task_pulse` and `avatar_state`
- [x] Add protocol versioning enforcement (`protocol_version=1`)
- [x] Add event payload validation guardrail

### 17.2 Phase B — Avatar Embodiment

- [x] Map cinematic states to animation graph nodes
- [ ] Implement gaze targeting by `avatar_target`
- [x] Add eureka pulse visual trigger
- [x] Add graceful failure visual state
- [ ] Add low-motion fallback mode

### 17.3 Phase C — Mission HUD

- [x] Build `ActionTimeline` from `missionLog`
- [x] Build `ThoughtEcho` strip from `taskPulse.thought`
- [x] Add status vocabulary mapping (`TARGET_ACQUIRED`, `SYNAPSES_LINKED`)
- [x] Add retry/failure reason rows
- [ ] Add compact mode for demo recording

### 17.4 Phase D — Orbital Workspace

- [ ] Add orbit registry in global store
- [ ] Add focused planet state + transitions
- [ ] Implement materialize/collapse app behavior
- [ ] Add orbital layout presets (inner/mid/outer)
- [ ] Add focus mode environment morphing

### 17.5 Phase E — Workspace Tool Backend

- [x] Create `workspace_tool` module
- [x] Add `focus_app` action
- [x] Add `move_app` action
- [x] Add `materialize_app` action
- [x] Add `collapse_app` action
- [x] Emit `workspace_state` updates per action

### 17.6 Phase F — Notes Planet (AI-first App)

- [ ] Create Notes Planet shell UI
- [ ] Add note create/update/delete actions
- [ ] Link notes to task IDs and voice session IDs
- [ ] Add semantic note recall endpoint
- [ ] Add one showcase flow in demo script

### 17.7 Phase G — Voyager + Mirror

- [ ] Add browser control tool wrapper
- [ ] Add mirror frame event contract
- [ ] Add click/typing highlight overlays
- [ ] Add latency instrumentation rows in HUD
- [ ] Add single fallback script path for demo

### 17.8 Phase H — Galaxy Orchestration

- [ ] Extend handover context with `galaxy_id`
- [ ] Add gravity score routing helper
- [ ] Add wrong-planet fallback reassignment
- [ ] Add rollback hooks with cinematic pulse
- [ ] Add per-galaxy policy enforcement checks

### 17.9 Phase I — AIX Adapter Layer

- [x] Implement `aix_parser` with JSON/TOML support
- [x] Add optional YAML parser bridge (if available)
- [x] Implement AIX ↔ Planet/Galaxy mapper
- [x] Add import/export tool functions
- [x] Add checksum generation and verification
- [x] Add round-trip tests

### 17.10 Phase J — Quality, Proof, and Demo Readiness

- [x] Add unit tests for routing and payload validation
- [ ] Add integration test for voice-to-visual flow
- [x] Run backend tests and capture pass evidence
- [x] Run lint and static checks
- [ ] Run dry-run demo 3 times with fallback check

---

## 18. External Repo Triage Protocol (Speed Without Derailment)

### 18.1 Decision Rules

- Adopt only if integration is `<= 4 hours` and risk is low
- Prefer patterns and interfaces over direct copy of full stacks
- Reject any code path with unrestricted shell/runtime control
- Treat external repos as inspiration unless they reduce core timeline risk

### 18.2 Current Candidate Assessment

- **private-journal-mcp**
  - Fit: High for Notes Planet memory indexing and semantic recall
  - Cost: Medium (adapter + storage bridge)
  - Decision: Adopt selective ideas only in v0.1
- **smallest-agent**
  - Fit: Low for production due to unrestricted bash model
  - Cost: Low to inspect, high security risk to integrate
  - Decision: Do not integrate runtime code; use only minimal architecture inspiration
- **Zentix-Protocol**
  - Fit: High as architecture inspiration (AIX DNA, multi-agent messaging)
  - Cost: High if directly integrated before demo
  - Decision: Mine patterns and naming; avoid deep dependency now

### 18.3 Intake Workflow for 80 Repos

- Submit top 5 repos first by immediate demo impact
- Score each repo on:
  - **Relevance** (0-5)
  - **Integration Time** (0-5, lower is better)
  - **Security Risk** (0-5, lower is better)
  - **Maintenance Cost** (0-5, lower is better)
- Accept only repos with:
  - Relevance `>= 4`
  - Integration Time `<= 2`
  - Security Risk `<= 2`
