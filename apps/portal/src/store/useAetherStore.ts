import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AuthSlice, createAuthSlice } from './slices/authSlice';
import { TelemetrySlice, createTelemetrySlice } from './slices/telemetrySlice';
import { DataSlice, createDataSlice } from './slices/dataSlice';
import { UISlice, createUISlice } from './slices/uiSlice';
import { ErrorSlice, createErrorSlice } from './slices/errorSlice';
import { PreferencesSlice, createPreferencesSlice } from './slices/preferencesSlice';

import { idbStorage } from './storage';

// Re-export types for convenience
export * from './types';
export * from './constants';

// ─── Combined State Interface ──────────────────────────────
export type AetherState = AuthSlice & TelemetrySlice & DataSlice & UISlice & ErrorSlice & PreferencesSlice & {
    isListening: boolean;
    animationTrigger: DataSlice['animationTrigger'];
    setAnimationTrigger: (t: DataSlice['animationTrigger']) => void;
    setListening: (l: boolean) => void;
};

// ─── Root Store ───────────────────────────────────────────
export const useAetherStore = create<AetherState>()(
    persist(
        (set, get, ...a) => ({
            ...createAuthSlice(set, get, ...a),
            ...createTelemetrySlice(set, get, ...a),
            ...createDataSlice(set, get, ...a),
            ...createUISlice(set, get, ...a),
            ...createErrorSlice(set, get, ...a),
            ...createPreferencesSlice(set, get, ...a),
            isListening: false,
            animationTrigger: "none",
            setAnimationTrigger: (t) => set({ animationTrigger: t }),
            setListening: (l) => set({ isListening: l }),
        }),
        {
            name: 'aether-neural-vault', // Rename for the new persistence layer
            storage: idbStorage,
            partialize: (state) => ({
                preferences: state.preferences,
                personaConfig: state.personaConfig,
                themeConfig: state.themeConfig,
                visualSettings: state.visualSettings,
                cachedSkills: state.cachedSkills,
                workspaceGalaxy: state.workspaceGalaxy,
                notesPlanet: state.notesPlanet,
            }),
        }
    )
);

// ─── Optimized Selectors (Neural Access Points) ──────────────
// These prevent unnecessary re-renders in heavy UI components.

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
