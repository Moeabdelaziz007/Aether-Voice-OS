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
    frustrationScore: number;
    latencyMs: number;

    // Data
    transcript: TranscriptMessage[];
    neuralEvents: NeuralEvent[];
    systemLogs: string[];

    // Actions
    setStatus: (status: ConnectionStatus) => void;
    setEngineState: (state: EngineState) => void;
    setAudioLevels: (mic: number, speaker: number) => void;
    setTelemetry: (frustration: number, latency: number) => void;
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
    latencyMs: 0,
    transcript: [],
    neuralEvents: [],
    systemLogs: [],

    setStatus: (status) => set({ status }),
    setEngineState: (engineState) => set({ engineState }),
    setAudioLevels: (micLevel, speakerLevel) => set({ micLevel, speakerLevel }),
    setTelemetry: (frustrationScore, latencyMs) => set({ frustrationScore, latencyMs }),

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
