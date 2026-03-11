import { create } from 'zustand';

/* ─── Step Types ─── */
export type ForgeStep = 'genesis' | 'brain' | 'memory' | 'skills' | 'visual' | 'review' | 'synthesizing';

/* ─── Vocal DNA ─── */
export interface VocalDNAState {
    voiceId: string;
    provider: 'elevenlabs' | 'google' | 'custom';
    isCloning: boolean;
    cloneProgress: number;
    previewUrl?: string;
}

/* ─── Neural Plug ─── */
export interface NeuralPlug {
    id: string;
    name: string;
    type: 'spotify' | 'gmail' | 'github' | 'slack' | 'notion' | 'calendar';
    icon: string;
    connected: boolean;
    description: string;
}

/* ─── Visual Lens ─── */
export interface VisualLens {
    id: string;
    name: string;
    description: string;
    icon: string;
    category: 'code' | 'security' | 'design' | 'data';
}

/* ─── Soul Blueprint ─── */
export interface SoulBlueprint {
    id: string;
    name: string;
    basePrompt: string;
    category: string;
    icon: string;
    auraLevel: number;
}

/* ─── Agent DNA ─── */
export interface AgentDNA {
    name: string;
    role: string;
    tone: string;
    personality_quarks: string[];
    visual_grounding?: string;
    provider: string;
    model: string;
    apiKey: string;
    memoryType: 'firebase' | 'local';
    skills: string[];
    avatarUrl?: string;
    isForged?: boolean;
    vocalDNA: VocalDNAState;
    neuralPlugs: string[];       // connected plug IDs
    selectedLens: string | null;
    selectedSoul: string | null; // soul blueprint ID
}

/* ─── Voice Mode ─── */
export type VoiceMode = 'idle' | 'listening' | 'processing' | 'responding';

/* ─── Store Interface ─── */
interface ForgeState {
    activeStep: ForgeStep;
    dna: AgentDNA;
    isListening: boolean;
    transcript: string;
    voiceMode: VoiceMode;

    // Actions
    setStep: (step: ForgeStep) => void;
    updateDNA: (update: Partial<AgentDNA>) => void;
    setListening: (listening: boolean) => void;
    setTranscript: (text: string) => void;
    setVoiceMode: (mode: VoiceMode) => void;
    resetForge: () => void;
    completeForge: () => void;

    // Vocal DNA
    updateVocalDNA: (update: Partial<VocalDNAState>) => void;
    startVoiceCloning: () => void;

    // Neural Plugs
    connectPlug: (plugId: string) => void;
    disconnectPlug: (plugId: string) => void;

    // Visual Lenses
    selectLens: (lensId: string | null) => void;

    // Soul Blueprints
    selectSoul: (soulId: string | null) => void;
}

/* ─── Initial State ─── */
const initialVocalDNA: VocalDNAState = {
    voiceId: '',
    provider: 'google',
    isCloning: false,
    cloneProgress: 0,
};

const initialDNA: AgentDNA = {
    name: '',
    role: '',
    tone: 'Professional & Technical',
    personality_quarks: [],
    visual_grounding: '',
    provider: 'google',
    model: 'gemini-2.0-flash',
    apiKey: '',
    memoryType: 'firebase',
    skills: [],
    isForged: false,
    vocalDNA: initialVocalDNA,
    neuralPlugs: [],
    selectedLens: null,
    selectedSoul: null,
};

/* ─── Available Neural Plugs ─── */
export const AVAILABLE_PLUGS: NeuralPlug[] = [
    { id: 'spotify', name: 'Spotify', type: 'spotify', icon: '🎵', connected: false, description: 'Music DJ capabilities — control playlists, discover songs' },
    { id: 'gmail', name: 'Gmail', type: 'gmail', icon: '📧', connected: false, description: 'Email management — read, compose, search messages' },
    { id: 'github', name: 'GitHub', type: 'github', icon: '🐙', connected: false, description: 'Code repository — PR reviews, issue tracking, commits' },
    { id: 'slack', name: 'Slack', type: 'slack', icon: '💬', connected: false, description: 'Team communication — messages, channels, notifications' },
    { id: 'notion', name: 'Notion', type: 'notion', icon: '📝', connected: false, description: 'Knowledge base — docs, databases, wikis' },
    { id: 'calendar', name: 'Google Calendar', type: 'calendar', icon: '📅', connected: false, description: 'Schedule management — events, reminders, availability' },
];

/* ─── Available Visual Lenses ─── */
export const AVAILABLE_LENSES: VisualLens[] = [
    { id: 'code-auditor', name: 'Code Auditor', description: 'Proactively reviews code quality and detects bugs', icon: '🔍', category: 'code' },
    { id: 'security-guard', name: 'Security Guard', description: 'Monitors for vulnerabilities and security threats', icon: '🛡️', category: 'security' },
    { id: 'design-critic', name: 'Design Critic', description: 'Evaluates UI/UX and suggests improvements', icon: '🎨', category: 'design' },
    { id: 'data-analyst', name: 'Data Analyst', description: 'Watches data flows and identifies anomalies', icon: '📊', category: 'data' },
    { id: 'perf-monitor', name: 'Performance Monitor', description: 'Tracks performance metrics and bottlenecks', icon: '⚡', category: 'code' },
    { id: 'accessibility', name: 'Accessibility Auditor', description: 'Ensures WCAG compliance and inclusivity', icon: '♿', category: 'design' },
];

/* ─── Available Soul Blueprints ─── */
export const AVAILABLE_SOULS: SoulBlueprint[] = [
    { id: 'elite-coder', name: 'Elite Coder', basePrompt: 'You are a world-class software engineer with deep expertise in system design, algorithms, and clean code practices.', category: 'Engineering', icon: '💻', auraLevel: 9.5 },
    { id: 'cyber-sentinel', name: 'Cyber Sentinel', basePrompt: 'You are a cybersecurity expert specializing in threat detection, penetration testing, and secure architecture.', category: 'Security', icon: '🛡️', auraLevel: 9.2 },
    { id: 'data-sage', name: 'Data Sage', basePrompt: 'You are a data science expert with mastery in ML pipelines, statistical analysis, and data visualization.', category: 'Data Science', icon: '📊', auraLevel: 9.0 },
    { id: 'creative-mind', name: 'Creative Mind', basePrompt: 'You are a creative director with expertise in design thinking, UX strategy, and brand storytelling.', category: 'Creative', icon: '🎨', auraLevel: 8.8 },
    { id: 'mentor-guide', name: 'Mentor Guide', basePrompt: 'You are a patient and insightful mentor who adapts teaching style to the learner\'s level and emotional state.', category: 'Education', icon: '🧑‍🏫', auraLevel: 9.1 },
    { id: 'devops-ninja', name: 'DevOps Ninja', basePrompt: 'You are a DevOps expert specializing in CI/CD, cloud infrastructure, and system reliability engineering.', category: 'Infrastructure', icon: '🚀', auraLevel: 8.9 },
];

/* ─── Voice Resonators (Vocal DNA) ─── */
export const VOICE_RESONATORS = [
    { id: 'nova', name: 'Nova', provider: 'google' as const, desc: 'Clear, authoritative, professional', gender: 'Female', preview: '🔊' },
    { id: 'echo', name: 'Echo', provider: 'google' as const, desc: 'Warm, conversational, friendly', gender: 'Male', preview: '🔊' },
    { id: 'pulse', name: 'Pulse', provider: 'elevenlabs' as const, desc: 'Energetic, dynamic, youthful', gender: 'Male', preview: '🔊' },
    { id: 'aria', name: 'Aria', provider: 'elevenlabs' as const, desc: 'Elegant, calm, articulate', gender: 'Female', preview: '🔊' },
    { id: 'cipher', name: 'Cipher', provider: 'elevenlabs' as const, desc: 'Mysterious, deep, commanding', gender: 'Male', preview: '🔊' },
    { id: 'custom', name: 'Clone My Voice', provider: 'custom' as const, desc: 'Speak for 10 seconds to harvest your vocal DNA', gender: 'Custom', preview: '🧬' },
];

/* ─── Store Creation ─── */
export const useForgeStore = create<ForgeState>((set, get) => ({
    activeStep: 'genesis',
    dna: initialDNA,
    isListening: false,
    transcript: '',
    voiceMode: 'idle',

    setStep: (step) => set({ activeStep: step }),
    updateDNA: (update) => set((state) => ({ dna: { ...state.dna, ...update } })),
    setListening: (listening) => set({ isListening: listening }),
    setTranscript: (text) => set({ transcript: text }),
    setVoiceMode: (voiceMode) => set({ voiceMode }),

    resetForge: () => set({
        activeStep: 'genesis',
        dna: initialDNA,
        transcript: '',
        voiceMode: 'idle',
    }),

    completeForge: () => set((state) => {
        console.log("🔥 Gemigram Cloud: Syncing Agent DNA...", state.dna);
        return {
            dna: { ...state.dna, isForged: true },
            activeStep: 'review',
        };
    }),

    // Vocal DNA
    updateVocalDNA: (update) => set((state) => ({
        dna: { ...state.dna, vocalDNA: { ...state.dna.vocalDNA, ...update } },
    })),

    startVoiceCloning: () => {
        set((state) => ({
            dna: {
                ...state.dna,
                vocalDNA: { ...state.dna.vocalDNA, isCloning: true, cloneProgress: 0, provider: 'custom' },
            },
        }));
        // Simulate cloning progress
        const interval = setInterval(() => {
            const current = get().dna.vocalDNA.cloneProgress;
            if (current >= 100) {
                clearInterval(interval);
                set((state) => ({
                    dna: {
                        ...state.dna,
                        vocalDNA: { ...state.dna.vocalDNA, isCloning: false, cloneProgress: 100, voiceId: 'custom-clone' },
                    },
                }));
            } else {
                set((state) => ({
                    dna: {
                        ...state.dna,
                        vocalDNA: { ...state.dna.vocalDNA, cloneProgress: current + 10 },
                    },
                }));
            }
        }, 1000);
    },

    // Neural Plugs
    connectPlug: (plugId) => set((state) => ({
        dna: {
            ...state.dna,
            neuralPlugs: state.dna.neuralPlugs.includes(plugId)
                ? state.dna.neuralPlugs
                : [...state.dna.neuralPlugs, plugId],
        },
    })),

    disconnectPlug: (plugId) => set((state) => ({
        dna: {
            ...state.dna,
            neuralPlugs: state.dna.neuralPlugs.filter((id) => id !== plugId),
        },
    })),

    // Visual Lenses
    selectLens: (lensId) => set((state) => ({
        dna: { ...state.dna, selectedLens: lensId },
    })),

    // Soul Blueprints
    selectSoul: (soulId) => set((state) => ({
        dna: { ...state.dna, selectedSoul: soulId },
    })),
}));
