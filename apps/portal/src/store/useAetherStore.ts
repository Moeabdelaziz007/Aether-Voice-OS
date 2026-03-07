import { create } from 'zustand';
import { persist } from 'zustand/middleware';

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

export interface ThemeConfig {
    currentTheme: ThemeType;
    accentColor: string;
    glowIntensity: number; // 0 - 1
    blurIntensity: number; // 3 - 24px
    grainEnabled: boolean;
    scanlinesEnabled: boolean;
    typography: 'monospace' | 'sans-serif';
}

export interface VisualSettings {
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

export interface SilentHint {
    id: string;
    text: string;
    code?: string;
    explanation?: string;
    priority: 'info' | 'warning' | 'suggestion';
    type: 'hint' | 'code';
    timestamp: number;
}

export interface NeuralEvent {
    id: string;
    fromAgent: string;
    toAgent: string;
    task: string;
    status: 'active' | 'completed' | 'pending';
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

// ─── Constants & Lookups ───────────────────────────────────
export const ACCENT_COLORS: Record<AccentColor, { primary: string; glow: string; rgb: string }> = {
    cyan: { primary: '#00f3ff', glow: 'rgba(0, 243, 255, 0.4)', rgb: '0, 243, 255' },
    purple: { primary: '#bc13fe', glow: 'rgba(188, 19, 254, 0.4)', rgb: '188, 19, 254' },
    amber: { primary: '#f59e0b', glow: 'rgba(245, 158, 11, 0.4)', rgb: '245, 158, 11' },
    emerald: { primary: '#10b981', glow: 'rgba(16, 185, 129, 0.4)', rgb: '16, 185, 129' },
    rose: { primary: '#f43f5e', glow: 'rgba(244, 63, 94, 0.4)', rgb: '244, 63, 94' },
    green: { primary: '#22c55e', glow: 'rgba(34, 197, 94, 0.4)', rgb: '34, 197, 94' },
    blue: { primary: '#3b82f6', glow: 'rgba(59, 130, 246, 0.4)', rgb: '59, 130, 246' },
};

export const VOICE_TONE_PROMPTS: Record<VoiceTone, string> = {
    professional: 'Respond in a concise, professional manner. Be direct and efficient.',
    casual: 'Be relaxed and conversational. Use natural language, like talking to a friend.',
    friendly: 'Be warm, encouraging, and supportive. Celebrate wins, be patient with errors.',
    mentor: 'Be a wise teacher. Explain the "why" behind things. Guide, don\'t just answer.',
    minimal: 'Ultra-brief responses. One sentence max unless asked for more detail.',
};

export const SUPERPOWER_META: Record<keyof Superpowers, { icon: string; label: string; desc: string }> = {
    visionPulse: { icon: '👁', label: 'Vision Pulse', desc: 'See your screen for visual context' },
    silentHints: { icon: '💡', label: 'Silent Hints', desc: 'Proactive code suggestions' },
    emotionSense: { icon: '🎭', label: 'Emotion Sense', desc: 'Detect frustration from voice' },
    autoHeal: { icon: '🔧', label: 'Auto-Heal', desc: 'Diagnose terminal errors' },
    codeSearch: { icon: '🔍', label: 'Code Search', desc: 'Semantic codebase search' },
    contextScrape: { icon: '🌐', label: 'Context Scrape', desc: 'Pull docs from the web' },
    zenShield: { icon: '🧘', label: 'Zen Shield', desc: 'Protect your flow state' },
};

export const SKILL_META: Record<SkillFocus, { icon: string; label: string }> = {
    coding: { icon: '⌨️', label: 'Coding' },
    debugging: { icon: '🐛', label: 'Debugging' },
    architecture: { icon: '🏗️', label: 'Architecture' },
    devops: { icon: '🚀', label: 'DevOps' },
    learning: { icon: '📚', label: 'Learning' },
    creative: { icon: '🎨', label: 'Creative' },
};

export const MOOD_META: Record<AIMood, { icon: string; color: string }> = {
    neutral: { icon: '⚪', color: '#888' },
    helpful: { icon: '💙', color: '#00f3ff' },
    focused: { icon: '🟡', color: '#f59e0b' },
    curious: { icon: '💜', color: '#bc13fe' },
    concerned: { icon: '🔴', color: '#f43f5e' },
};

// ─── Default Values ────────────────────────────────────────
const DEFAULT_PERSONA: AetherPersona = {
    name: 'Aether',
    role: 'Developer Co-Pilot',
    mood: 'neutral',
    feeling: '',
    expertise: 'General',
    voiceTone: 'Calm',
    experienceLevel: 'Senior',
    greeting: 'Hey! How can I help you today?',
    activeSkills: ['coding', 'debugging'],
};

const DEFAULT_SUPERPOWERS: Superpowers = {
    visionPulse: true,
    silentHints: true,
    emotionSense: true,
    autoHeal: false,
    codeSearch: true,
    contextScrape: false,
    zenShield: true,
};

const DEFAULT_PREFERENCES: UserPreferences = {
    accentColor: 'cyan',
    waveStyle: 'helix',
    transcriptMode: 'whisper',
    emotionDisplay: 'aura',
    showTelemetry: true,
    showParticles: true,
    personaName: 'Aether',
    personaRole: 'Developer Co-Pilot',
    voiceTone: 'friendly',
    experienceLevel: 'expert',
    superpowers: DEFAULT_SUPERPOWERS,
    skillFocus: ['coding', 'debugging'],
    rememberContext: true,
    greeting: 'Hey! How can I help you today?',
    volume: 0.7,
    isMuted: false,
    soundEffectsEnabled: true,
    ambientSoundsEnabled: true,
};

// ─── Tool Call Entry ───────────────────────────────────────
export interface ToolCallEntry {
    id: string;
    toolName: string;
    status: 'running' | 'success' | 'error';
    latencyMs?: number;
    timestamp: number;
}

// ─── State Interface ───────────────────────────────────────
interface AetherState {
    // Realm
    currentRealm: RealmType;

    // Connection
    status: ConnectionStatus;
    engineState: EngineState;
    connectionMode: 'gemini' | 'gateway';
    sessionStartTime: number | null;

    // Audio
    micLevel: number;
    speakerLevel: number;

    // Telemetry
    valence: number;
    arousal: number;
    engagement: number;
    frustrationScore: number;
    pitch: number;
    rate: number;
    spectralCentroid: number;
    noiseFloor: number;
    latencyMs: number;
    lastMutation: string | null;

    // Data
    transcript: TranscriptMessage[];
    neuralEvents: NeuralEvent[];
    systemLogs: string[];
    silentHints: SilentHint[];
    visionActive: boolean;
    lastVisionPulse: string | null;
    zenMode: boolean;
    repairState: RepairState;

    // Multi-Agent (Hive)
    activeSoul: string | null;
    toolCallHistory: ToolCallEntry[];

    // Generative UI
    activeWidgets: { id: string; type: string; props: any }[];
    predictedGoal: string | null;

    // Persona & Preferences
    persona: AetherPersona;
    preferences: UserPreferences;
    settingsOpen: boolean;

    // Terminal Feed State
    terminalLogs: TerminalLog[];
    isInterrupted: boolean;
    scrollPaused: boolean;
    streamingBuffer: string;

    // Skills Management
    activeSkills: Skill[];
    cachedSkills: Skill[];
    skillsSyncStatus: SkillsSyncStatus;

    // Persona Configuration
    personaConfig: PersonaConfig;

    // Theme Configuration
    themeConfig: ThemeConfig;
    visualSettings: VisualSettings;

    // Actions — Realm
    setRealm: (realm: RealmType) => void;

    // Actions — Connection
    setStatus: (status: ConnectionStatus) => void;
    setEngineState: (state: EngineState) => void;
    setConnectionMode: (mode: 'gemini' | 'gateway') => void;
    setSessionStartTime: (time: number | null) => void;

    // Actions — Audio
    setAudioLevels: (mic: number, speaker: number) => void;
    setLatencyMs: (latencyMs: number) => void;
    setTelemetry: (data: { frustration?: number; valence?: number; arousal?: number; engagement?: number; zen_mode?: boolean; pitch?: number; rate?: number; spectralCentroid?: number; noiseFloor?: number }, latency: number) => void;
    setMutation: (mutation: string) => void;
    setVisionPulse: (lastVisionPulse: string) => void;

    // Actions — Data
    addTranscriptMessage: (msg: Omit<TranscriptMessage, 'id' | 'timestamp'>) => void;
    addNeuralEvent: (event: Omit<NeuralEvent, 'id'>) => void;
    updateNeuralEvent: (id: string, updates: Partial<NeuralEvent>) => void;
    addSystemLog: (log: string) => void;
    addSilentHint: (hint: SilentHint) => void;
    dismissHint: (id: string) => void;
    setVisionActive: (active: boolean) => void;
    clearTranscript: () => void;
    setRepairState: (state: RepairState) => void;
    clearRepairState: () => void;

    // Actions — Multi-Agent (Hive)
    setActiveSoul: (soul: string | null) => void;
    addToolCall: (entry: Omit<ToolCallEntry, 'id' | 'timestamp'>) => void;

    // Actions — Generative UI
    addWidget: (type: string, props: any) => void;
    removeWidget: (id: string) => void;
    clearWidgets: () => void;
    setPredictedGoal: (goal: string | null) => void;

    // Actions — Persona & Preferences
    setPersona: (updates: Partial<AetherPersona>) => void;
    setPreferences: (updates: Partial<UserPreferences>) => void;
    toggleSuperpower: (key: keyof Superpowers) => void;
    toggleSkillFocus: (skill: SkillFocus) => void;
    toggleSettings: () => void;
    resetPreferences: () => void;

    // Actions — Terminal Feed
    addTerminalLog: (level: TerminalLog['level'], message: string, widgetId?: string) => void;
    clearTerminalLogs: () => void;
    setInterrupted: (interrupted: boolean) => void;
    setScrollPaused: (paused: boolean) => void;
    setStreamingBuffer: (buffer: string) => void;

    // Actions — Skills Management
    setActiveSkills: (skills: Skill[]) => void;
    setCachedSkills: (skills: Skill[]) => void;
    toggleSkill: (skillId: string) => void;
    setSkillsSyncStatus: (status: SkillsSyncStatus) => void;

    // Actions — Persona Configuration
    setPersonaConfig: (config: Partial<PersonaConfig>) => void;

    // Actions — Theme Configuration
    setThemeConfig: (config: Partial<ThemeConfig>) => void;
    setVisualSettings: (settings: Partial<VisualSettings>) => void;
}

// ─── Optimized Selectors for Performance ────────────────────
// Simple selectors - use React.memo on components for optimization
export const useAudioLevels = () => {
    const mic = useAetherStore((s) => s.micLevel);
    const speaker = useAetherStore((s) => s.speakerLevel);
    return { mic, speaker };
};

export const useEngineStateSelector = () => useAetherStore((s) => s.engineState);

export const useTranscriptSelector = () => useAetherStore((s) => s.transcript);

export const useCurrentRealmSelector = () => useAetherStore((s) => s.currentRealm);

export const usePreferencesSelector = () => useAetherStore((s) => s.preferences);

export const useTelemetrySelector = () => {
    const valence = useAetherStore((s) => s.valence);
    const arousal = useAetherStore((s) => s.arousal);
    const engagement = useAetherStore((s) => s.engagement);
    const frustrationScore = useAetherStore((s) => s.frustrationScore);
    return { valence, arousal, engagement, frustrationScore };
};

// ─── Store ─────────────────────────────────────────────────
export const useAetherStore = create<AetherState>()(
    persist(
        (set) => ({
            // Initial state
            currentRealm: "void",
            status: "disconnected",
            engineState: "IDLE",
            connectionMode: 'gemini',
            sessionStartTime: null,
            micLevel: 0,
            speakerLevel: 0,
            frustrationScore: 0,
            valence: 0,
            arousal: 0,
            engagement: 0,
            pitch: 0,
            rate: 0,
            spectralCentroid: 0,
            noiseFloor: 0,
            latencyMs: 0,
            lastMutation: null,
            transcript: [],
            neuralEvents: [],
            systemLogs: [],
            silentHints: [],
            visionActive: false,
            lastVisionPulse: null,
            zenMode: false,
            repairState: { status: 'idle', message: '', log: '', timestamp: 0 },
            activeSoul: null,
            activeWidgets: [],
            predictedGoal: null,
            toolCallHistory: [],
            persona: DEFAULT_PERSONA,
            preferences: DEFAULT_PREFERENCES,
            settingsOpen: false,

            // Terminal Feed initial state
            terminalLogs: [],
            isInterrupted: false,
            scrollPaused: false,
            streamingBuffer: '',

            // Skills initial state
            activeSkills: [],
            cachedSkills: [],
            skillsSyncStatus: 'idle',

            // Persona configuration initial state
            personaConfig: {
                tone: 'analytical',
                formality: 'formal',
                verbosity: 'balanced',
            },

            // Theme configuration initial state
            themeConfig: {
                currentTheme: 'matrix-core',
                accentColor: '#00FF41',
                glowIntensity: 1,
                blurIntensity: 12,
                grainEnabled: true,
                scanlinesEnabled: false,
                typography: 'monospace',
            },

            visualSettings: {
                blurLight: 12,
                blurHeavy: 24,
                glowColor: '#00FF41',
                backgroundColor: '#0B0B0C',
            },

            // Realm actions
            setRealm: (currentRealm) => set({ currentRealm }),

            // Connection actions
            setStatus: (status) => set({ status }),
            setEngineState: (engineState) => set({ engineState }),
            setConnectionMode: (connectionMode) => set({ connectionMode }),
            setSessionStartTime: (sessionStartTime) => set({ sessionStartTime }),

            // Audio actions
            setAudioLevels: (micLevel, speakerLevel) => set({ micLevel, speakerLevel }),
            setLatencyMs: (latencyMs) => set({ latencyMs }),
            setTelemetry: (data, latencyMs) => set((state) => ({
                ...state,
                ...data,
                frustrationScore: data.frustration ?? state.frustrationScore,
                zenMode: data.zen_mode ?? state.zenMode,
                latencyMs,
            })),
            setMutation: (lastMutation) => set({ lastMutation }),
            setVisionPulse: (lastVisionPulse: string) => set({ lastVisionPulse }),

            // Data actions
            addTranscriptMessage: (msg) => set((state) => ({
                transcript: [...state.transcript, {
                    ...msg,
                    id: crypto.randomUUID(),
                    timestamp: Date.now(),
                }],
            })),

            addNeuralEvent: (event) => set((state) => ({
                neuralEvents: [...state.neuralEvents, { ...event, id: crypto.randomUUID() }],
            })),

            updateNeuralEvent: (id, updates) => set((state) => ({
                neuralEvents: state.neuralEvents.map(evt =>
                    evt.id === id ? { ...evt, ...updates } : evt
                ),
            })),

            addSystemLog: (log) => set((state) => {
                const newLogs = [...state.systemLogs, log];
                return { systemLogs: newLogs.slice(-50) };
            }),

            addSilentHint: (hint) => set((state) => ({
                silentHints: [...state.silentHints, hint].slice(-10),
            })),

            dismissHint: (id) => set((state) => ({
                silentHints: state.silentHints.filter(h => h.id !== id),
            })),

            setVisionActive: (visionActive) => set({ visionActive }),
            clearTranscript: () => set({ transcript: [] }),
            setRepairState: (repairState) => set({ repairState }),
            clearRepairState: () => set({ repairState: { status: 'idle', message: '', log: '', timestamp: 0 } }),

            // Multi-Agent actions
            setActiveSoul: (activeSoul) => set({ activeSoul }),
            addToolCall: (entry) => set((state) => ({
                toolCallHistory: [...state.toolCallHistory, {
                    ...entry,
                    id: crypto.randomUUID(),
                    timestamp: Date.now(),
                }].slice(-50),
            })),

            // Generative UI actions
            addWidget: (type, props) => set((state) => ({
                activeWidgets: [...state.activeWidgets, { id: crypto.randomUUID(), type, props }]
            })),
            removeWidget: (id) => set((state) => ({
                activeWidgets: state.activeWidgets.filter(w => w.id !== id)
            })),
            clearWidgets: () => set({ activeWidgets: [] }),
            setPredictedGoal: (predictedGoal) => set({ predictedGoal }),

            // Persona & Preferences actions
            setPersona: (updates) => set((state) => ({
                persona: { ...state.persona, ...updates },
            })),

            setPreferences: (updates) => set((state) => ({
                preferences: { ...state.preferences, ...updates },
            })),

            toggleSuperpower: (key) => set((state) => ({
                preferences: {
                    ...state.preferences,
                    superpowers: {
                        ...state.preferences.superpowers,
                        [key]: !state.preferences.superpowers[key],
                    },
                },
            })),

            toggleSkillFocus: (skill) => set((state) => {
                const current = state.preferences.skillFocus;
                const next = current.includes(skill)
                    ? current.filter(s => s !== skill)
                    : [...current, skill];
                return {
                    preferences: { ...state.preferences, skillFocus: next },
                    persona: { ...state.persona, activeSkills: next },
                };
            }),

            toggleSettings: () => set((state) => ({
                settingsOpen: !state.settingsOpen,
            })),

            resetPreferences: () => set({
                preferences: DEFAULT_PREFERENCES,
                persona: DEFAULT_PERSONA,
            }),

            // Terminal Feed actions
            addTerminalLog: (level, message, widgetId) => set((state) => ({
                terminalLogs: [...state.terminalLogs, {
                    id: crypto.randomUUID(),
                    level,
                    message,
                    timestamp: Date.now(),
                    widgetId,
                }].slice(-50), // Keep max 50 logs
            })),

            clearTerminalLogs: () => set({ terminalLogs: [] }),
            setInterrupted: (isInterrupted) => set({ isInterrupted }),
            setScrollPaused: (scrollPaused) => set({ scrollPaused }),
            setStreamingBuffer: (streamingBuffer) => set({ streamingBuffer }),

            // Skills Management actions
            setActiveSkills: (activeSkills) => set({ activeSkills }),
            setCachedSkills: (cachedSkills) => set({ cachedSkills }),

            toggleSkill: (skillId) => set((state) => ({
                activeSkills: state.activeSkills.map(skill =>
                    skill.id === skillId ? { ...skill, enabled: !skill.enabled } : skill
                ),
            })),

            setSkillsSyncStatus: (skillsSyncStatus) => set({ skillsSyncStatus }),

            // Persona Configuration actions
            setPersonaConfig: (updates) => set((state) => ({
                personaConfig: { ...state.personaConfig, ...updates },
            })),

            // Theme Configuration actions
            setThemeConfig: (updates) => set((state) => ({
                themeConfig: { ...state.themeConfig, ...updates },
            })),

            setVisualSettings: (updates) => set((state) => ({
                visualSettings: { ...state.visualSettings, ...updates },
            })),
        }),
        {
            name: 'aether-preferences',
            partialize: (state) => ({
                preferences: state.preferences,
                personaConfig: state.personaConfig,
                themeConfig: state.themeConfig,
                visualSettings: state.visualSettings,
                cachedSkills: state.cachedSkills,
            }),
        }
    )
);
