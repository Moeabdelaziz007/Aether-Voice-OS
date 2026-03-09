import { AccentColor, AIMood, ExperienceLevel, PersonaConfig, SkillFocus, Superpowers, ThemeConfig, UserPreferences, VisualSettings, AetherPersona, VoiceTone, TranscriptMode, ThemeMode, WaveStyle, EmotionDisplay } from "./types";

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
export const DEFAULT_PERSONA: AetherPersona = {
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

export const DEFAULT_SUPERPOWERS: Superpowers = {
    visionPulse: true,
    silentHints: true,
    emotionSense: true,
    autoHeal: false,
    codeSearch: true,
    contextScrape: false,
    zenShield: true,
};

export const DEFAULT_PREFERENCES: UserPreferences = {
    accentColor: 'cyan',
    waveStyle: 'helix',
    transcriptMode: 'whisper',
    emotionDisplay: 'aura',
    showTelemetry: true,
    showParticles: true,
    lowMotionMode: false,
    compactMissionHud: false,
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

export const DEFAULT_REPAIR_STATE = { status: 'idle' as const, message: '', log: '', timestamp: 0 };

export const DEFAULT_PERSONA_CONFIG: PersonaConfig = {
    tone: 'analytical',
    formality: 'formal',
    verbosity: 'balanced',
};

export const DEFAULT_THEME_CONFIG: ThemeConfig = {
    currentTheme: 'matrix-core',
    themeMode: 'dark-state',
    accentColor: '#00FF41',
    glowIntensity: 1,
    blurIntensity: 12,
    grainEnabled: true,
    scanlinesEnabled: false,
    typography: 'monospace',
};

export const DEFAULT_VISUAL_SETTINGS: VisualSettings = {
    blurLight: 12,
    blurHeavy: 24,
    glowColor: '#00FF41',
    backgroundColor: '#0B0B0C',
};
