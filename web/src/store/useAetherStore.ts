import { create } from 'zustand';

// Types from our hooks
export type ConnectionStatus = "disconnected" | "connecting" | "connected" | "listening" | "speaking" | "error";
export type EngineState = "IDLE" | "LISTENING" | "THINKING" | "SPEAKING" | "INTERRUPTING";

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

interface AetherState {
    // Global Connection State
    status: ConnectionStatus;
    engineState: EngineState;
    connectionMode: 'gemini' | 'gateway';
    sessionStartTime: number | null;

    // Real-time Audio Levels (0.0 to 1.0)
    micLevel: number;
    speakerLevel: number;

    // Affective Telemetry
    valence: number;
    arousal: number;
    engagement: number;
    frustrationScore: number;
    pitch: number;
    rate: number;
    latencyMs: number;
    lastMutation: string | null;

    transcript: TranscriptMessage[];
    neuralEvents: NeuralEvent[];
    systemLogs: string[];
    silentHints: SilentHint[];
    visionActive: boolean;
    lastVisionPulse: string | null;
    zenMode: boolean;

    // Actions
    setStatus: (status: ConnectionStatus) => void;
    setEngineState: (state: EngineState) => void;
    setConnectionMode: (mode: 'gemini' | 'gateway') => void;
    setSessionStartTime: (time: number | null) => void;
    setAudioLevels: (mic: number, speaker: number) => void;
    setLatencyMs: (latencyMs: number) => void;
    setTelemetry: (data: { frustration?: number, valence?: number, arousal?: number, engagement?: number, zen_mode?: boolean, pitch?: number, rate?: number }, latency: number) => void;
    setMutation: (mutation: string) => void;
    setVisionPulse: (lastVisionPulse: string) => void;
    addTranscriptMessage: (msg: Omit<TranscriptMessage, 'id' | 'timestamp'>) => void;
    addNeuralEvent: (event: Omit<NeuralEvent, 'id'>) => void;
    updateNeuralEvent: (id: string, updates: Partial<NeuralEvent>) => void;
    addSystemLog: (log: string) => void;
    addSilentHint: (hint: SilentHint) => void;
    dismissHint: (id: string) => void;
    setVisionActive: (active: boolean) => void;
    clearTranscript: () => void;
}

export const useAetherStore = create<AetherState>((set) => ({
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
    latencyMs: 0,
    lastMutation: null,
    transcript: [],
    neuralEvents: [],
    systemLogs: [],
    silentHints: [],
    visionActive: false,
    lastVisionPulse: null,
    zenMode: false,

    setStatus: (status) => set({ status }),
    setEngineState: (engineState) => set({ engineState }),
    setConnectionMode: (connectionMode) => set({ connectionMode }),
    setSessionStartTime: (sessionStartTime) => set({ sessionStartTime }),
    setAudioLevels: (micLevel, speakerLevel) => set({ micLevel, speakerLevel }),
    setLatencyMs: (latencyMs) => set({ latencyMs }),
    setTelemetry: (data, latencyMs) => set((state) => ({
        ...state,
        ...data,
        frustrationScore: data.frustration ?? state.frustrationScore,
        zenMode: data.zen_mode ?? state.zenMode,
        latencyMs
    })),
    setMutation: (lastMutation) => set({ lastMutation }),
    setVisionPulse: (lastVisionPulse: string) => set({ lastVisionPulse }),

    addTranscriptMessage: (msg) => set((state) => ({
        transcript: [...state.transcript, {
            ...msg,
            id: crypto.randomUUID(),
            timestamp: Date.now()
        }]
    })),

    addNeuralEvent: (event) => set((state) => ({
        neuralEvents: [...state.neuralEvents, { ...event, id: crypto.randomUUID() }]
    })),

    updateNeuralEvent: (id, updates) => set((state) => ({
        neuralEvents: state.neuralEvents.map(evt =>
            evt.id === id ? { ...evt, ...updates } : evt
        )
    })),

    addSystemLog: (log) => set((state) => {
        const newLogs = [...state.systemLogs, log];
        return { systemLogs: newLogs.slice(-50) }; // Keep last 50 logs
    }),

    addSilentHint: (hint) => set((state) => ({
        silentHints: [...state.silentHints, hint].slice(-10) // Keep last 10 hints
    })),

    dismissHint: (id) => set((state) => ({
        silentHints: state.silentHints.filter(h => h.id !== id)
    })),

    setVisionActive: (visionActive) => set({ visionActive }),

    clearTranscript: () => set({ transcript: [] })
}));
