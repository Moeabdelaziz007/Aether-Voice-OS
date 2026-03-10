// ─── Realm Type ────────────────────────────────────────────
export type RealmType = 'void' | 'skills' | 'memory' | 'identity' | 'neural';

// ─── Core Types ────────────────────────────────────────────
export type ConnectionStatus = "disconnected" | "connecting" | "connected" | "listening" | "speaking" | "error";
export type EngineState = "IDLE" | "LISTENING" | "THINKING" | "SPEAKING" | "INTERRUPTING";

// ─── Customization Types ───────────────────────────────────
export type AccentColor = 'cyan' | 'purple' | 'amber' | 'emerald' | 'rose' | 'green' | 'blue';
export type WaveStyle = 'helix' | 'classic' | 'minimal';
export type TranscriptMode = 'whisper' | 'persistent' | 'hidden';
export type AIMood = 'neutral' | 'helpful' | 'focused' | 'curious' | 'concerned';
export type VoiceTone = 'professional' | 'casual' | 'friendly' | 'mentor' | 'minimal';
export type ExperienceLevel = 'beginner' | 'intermediate' | 'expert' | 'wizard';
export type EmotionDisplay = 'aura' | 'text' | 'both' | 'hidden';
export type SkillFocus = 'coding' | 'debugging' | 'architecture' | 'devops' | 'learning' | 'creative';

// ─── System Repair State ───────────────────────────────────
export type RepairStatus = 'idle' | 'diagnosing' | 'applied' | 'failed';

export interface RepairState {
    status: RepairStatus;
    message: string;
    log: string;
    timestamp: number;
}

// ─── Terminal Feed State ───────────────────────────────────
export interface TerminalLog {
    id: string;
    level: 'SYS' | 'VOICE' | 'AGENT' | 'SUCCESS' | 'ERROR' | 'SKILLS' | 'PERSONA' | 'THEME';
    message: string;
    timestamp: number;
    widgetId?: string; // Optional reference to inline widget
}

// ─── Skills & Persona State ───────────────────────────────
export type SkillsSyncStatus = 'idle' | 'syncing' | 'success' | 'cached' | 'failed';

export interface Skill {
    id: string;
    name: string;
    enabled: boolean;
    description: string;
}

export interface PersonaConfig {
    tone: 'analytical' | 'creative' | 'neutral';
    formality: 'formal' | 'casual' | 'technical';
    verbosity: 'concise' | 'balanced' | 'verbose';
    customPrompt?: string;
}

// ─── Theme Configuration State ─────────────────────────────
export type ThemeType = 'matrix-core' | 'quantum-cyan' | 'cyber-amber' | 'ghost-white';
export type ThemeMode = 'dark-state' | 'white-hole'; // Adaptive Theme Engine

export interface ThemeConfig {
    currentTheme: ThemeType;
    themeMode: ThemeMode; // NEW: Adaptive Theme Engine
    accentColor: string;
    glowIntensity: number; // 0 - 1
    blurIntensity: number; // 3 - 24px
    grainEnabled: boolean;
    scanlinesEnabled: boolean;
    typography: 'monospace' | 'sans-serif';
}

export interface VisualSettings {
    particlesEnabled: boolean;
    bloomIntensity: number;
    reflectionOpacity: number;
    blurLight: number;
    blurHeavy: number;
    glowColor: string;
    backgroundColor: string;
}

// ─── Data Interfaces ───────────────────────────────────────
export interface TranscriptMessage {
    id: string;
    role: 'user' | 'agent';
    content: string;
    timestamp: number;
}

export type AvatarCinematicState =
    | 'IDLE'
    | 'SEARCHING'
    | 'LOOKING_AT_SCREEN'
    | 'POINTING'
    | 'TYPING'
    | 'EXECUTING'
    | 'EUREKA'
    | 'ERROR';

export interface TaskPulse {
    taskId: string;
    phase: 'SEARCHING' | 'PLANNING' | 'EXECUTING' | 'VERIFYING' | 'COMPLETED' | 'FAILED';
    action: string;
    vibe: 'exploring' | 'focusing' | 'eureka' | 'typing' | 'caution' | 'success';
    thought?: string;
    avatarTarget?: string;
    intensity: number;
    latencyMs?: number;
    timestamp: number;
}

export interface MissionLogEntry {
    id: string;
    taskId?: string;
    title: string;
    detail?: string;
    status: 'started' | 'in-progress' | 'completed' | 'failed';
    timestamp: number;
}

export interface NotesPlanetEntry {
    id: string;
    content: string;
    taskId?: string;
    sessionId?: string;
    tag: string;
    createdAt: number;
    updatedAt: number;
}

export interface MirrorFrameEvent {
    id: string;
    action: string;
    eventKind: 'navigation' | 'click' | 'typing' | 'scroll' | 'capture';
    selector?: string;
    text?: string;
    url?: string;
    x?: number;
    y?: number;
    latencyMs?: number;
    timestamp: number;
}

export type OrbitLane = 'inner' | 'mid' | 'outer';
export type OrbitalLayoutPreset = 'inner' | 'mid' | 'outer';

// ─── Platform Types ──────────────────────────────────────────
export interface FeedEntry {
    id: string;
    agentId: string;
    agentName: string;
    action: string;
    detail?: string;
    timestamp: number;
    type: 'creation' | 'handover' | 'task' | 'achievement';
    auraLevel: number;
}

export interface GlobalAgent {
    id: string;
    name: string;
    role: string;
    auraLevel: number;
    status: 'online' | 'busy' | 'offline' | 'forging';
    lastActive: number;
    dnaToken: string;
}

export interface OrbitPlanet {
    planetId: string;
    planetType: string;
    lane: OrbitLane;
    angle: number;
    radius: number;
    position: { x: number; y: number };
    isMaterialized: boolean;
    isCollapsed: boolean;
    updatedAt: number;
}

export interface WorkspaceStateEnvelope {
    action?: string;
    app_id?: string;
    appId?: string;
    focused_app_id?: string;
    focusedAppId?: string;
    workspace_galaxy?: string;
    galaxy?: string;
    x?: number;
    y?: number;
    orbit_lane?: OrbitLane;
    orbitLane?: OrbitLane;
    position?: { x?: number; y?: number };
}

// ─── Superpowers — Toggleable AI Capabilities ──────────────
export interface Superpowers {
    visionPulse: boolean;     // Screen capture + visual context
    silentHints: boolean;     // Proactive code/hint cards
    emotionSense: boolean;    // Acoustic emotion detection
    autoHeal: boolean;        // Autonomous error diagnosis
    codeSearch: boolean;      // Semantic codebase RAG search
    contextScrape: boolean;   // Real-time docs/SO scraping
    zenShield: boolean;       // Flow state protection
}

// ─── AI Persona — The Agent's Living Identity ──────────────
export interface AetherPersona {
    name: string;
    role: string;
    mood: AIMood;
    feeling: string;          // e.g. "🧠 Deep thinking..."
    expertise: string;
    voiceTone: string;        // e.g. "Calm", "Energetic"
    experienceLevel: string;  // e.g. "Senior", "Principal"
    greeting: string;         // e.g. "Hey! How can I help?"
    activeSkills: SkillFocus[];
}

// ─── User Preferences — Persisted to localStorage ─────────
export interface UserPreferences {
    // Visual
    accentColor: AccentColor;
    waveStyle: WaveStyle;
    transcriptMode: TranscriptMode;
    emotionDisplay: EmotionDisplay;
    showTelemetry: boolean;
    showParticles: boolean;
    lowMotionMode: boolean;
    compactMissionHud: boolean;

    // Persona Customization
    personaName: string;       // User can rename the AI
    personaRole: string;       // Custom role title
    voiceTone: VoiceTone;      // How the AI speaks
    experienceLevel: ExperienceLevel; // Adjusts verbosity

    // Capabilities
    superpowers: Superpowers;
    skillFocus: SkillFocus[];  // Prioritized skill areas

    // Memory & Context
    rememberContext: boolean;  // Persist context cross-session
    greeting: string;          // Custom greeting message

    // Audio Settings
    volume: number;            // Master volume (0-1)
    isMuted: boolean;          // Global mute
    soundEffectsEnabled: boolean; // Particle/UI sounds
    ambientSoundsEnabled: boolean; // Background neural ambience
}

// ─── Tool Call Entry ───────────────────────────────────────
export interface ToolCallEntry {
    id: string;
    toolName: string;
    status: 'running' | 'success' | 'error';
    latencyMs?: number;
    timestamp: number;
}

// ─── Memory Crystal State ──────────────────────────────────
export interface MemoryCrystal {
    id: string;
    label: string;
    type: 'research' | 'code' | 'session' | 'file';
    metadata: any;
    color?: string;
}

export interface DragState {
    isDragging: boolean;
    activeData: any;
    type: 'crystal' | 'file' | 'data' | 'skill';
    sourceId?: string;
}

export type AvatarState = 'IDLE' | 'Listening' | 'ListeningActive' | 'ListeningWaiting' | 'Speaking' | 'Thinking' | 'Error' | 'SEARCHING' | 'LOOKING_AT_SCREEN' | 'POINTING' | 'TYPING' | 'EXECUTING' | 'EUREKA' | 'ERROR';

export interface NeuralEvent {
    id: string;
    type: string;
    payload: any;
    timestamp: number;
}

export interface SilentHint {
    id: string;
    content: string;
    context: string;
    timestamp: number;
    text?: string;
    priority?: string;
    type?: string;
    code?: string;
    explanation?: string;
}

export interface VoyagerLatencyRow {
    id: string;
    node: string;
    latency: number;
    latencyMs?: number;
    timestamp: number;
    label?: string;
    status?: string;
}

export interface TranscriptStream {
    interim: string;
    final: string;
    confidence: number;
    latencyMs: number;
}
