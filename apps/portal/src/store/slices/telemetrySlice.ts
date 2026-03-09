import { StateCreator } from 'zustand';

export interface TelemetrySlice {
    micLevel: number;
    speakerLevel: number;
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
    lastVisionPulse: string | null;

    setAudioLevels: (mic: number, speaker: number) => void;
    setLatencyMs: (latencyMs: number) => void;
    setTelemetry: (data: { frustration?: number; valence?: number; arousal?: number; engagement?: number; zen_mode?: boolean; pitch?: number; rate?: number; spectralCentroid?: number; noiseFloor?: number }, latency: number) => void;
    setMutation: (mutation: string) => void;
    setVisionPulse: (lastVisionPulse: string) => void;
}

export const createTelemetrySlice: StateCreator<TelemetrySlice> = (set) => ({
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
    lastVisionPulse: null,

    setAudioLevels: (micLevel, speakerLevel) => set({ micLevel, speakerLevel }),
    setLatencyMs: (latencyMs) => set({ latencyMs }),
    setTelemetry: (data, latencyMs) => set((state) => ({
        ...state,
        ...data,
        frustrationScore: data.frustration ?? state.frustrationScore,
        latencyMs,
    })),
    setMutation: (lastMutation) => set({ lastMutation }),
    setVisionPulse: (lastVisionPulse) => set({ lastVisionPulse }),
});
