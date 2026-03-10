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
export type AetherState = AuthSlice & TelemetrySlice & DataSlice & UISlice & ErrorSlice & PreferencesSlice;

// ─── Root Store ───────────────────────────────────────────
export const useAetherStore = create<AetherState>()(
    persist(
        (...a) => ({
            ...createAuthSlice(...a),
            ...createTelemetrySlice(...a),
            ...createDataSlice(...a),
            ...createUISlice(...a),
            ...createErrorSlice(...a),
            ...createPreferencesSlice(...a),
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
