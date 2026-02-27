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
    lastVisionPulse: string | null;
    zenMode: boolean;

    // Actions
    setStatus: (status: ConnectionStatus) => void;
    setEngineState: (state: EngineState) => void;
    setAudioLevels: (mic: number, speaker: number) => void;
    setTelemetry: (data: { frustration?: number, valence?: number, arousal?: number, engagement?: number, zen_mode?: boolean, pitch?: number, rate?: number }, latency: number) => void;
    setMutation: (mutation: string) => void;
    setVisionPulse: (lastVisionPulse: string) => void;
    addTranscriptMessage: (msg: Omit<TranscriptMessage, 'id' | 'timestamp'>) => void;
    addNeuralEvent: (event: Omit<NeuralEvent, 'id'>) => void;
    updateNeuralEvent: (id: string, updates: Partial<NeuralEvent>) => void;
    addSystemLog: (log: string) => void;
    clearTranscript: () => void;
}

export const useAetherStore = create<AetherState>((set) => ({
    status: "disconnected",
    engineState: "IDLE",
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
    lastVisionPulse: null,
    zenMode: false,

    setStatus: (status) => set({ status }),
    setEngineState: (engineState) => set({ engineState }),
    setAudioLevels: (micLevel, speakerLevel) => set({ micLevel, speakerLevel }),
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

    clearTranscript: () => set({ transcript: [] })
}));
