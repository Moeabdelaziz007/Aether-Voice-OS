import { StateCreator } from 'zustand';
import {
    AetherPersona, UserPreferences, Skill, SkillsSyncStatus, PersonaConfig,
    ThemeConfig, VisualSettings, Superpowers, SkillFocus
} from '../types';
import {
    DEFAULT_PERSONA, DEFAULT_PREFERENCES, DEFAULT_PERSONA_CONFIG,
    DEFAULT_THEME_CONFIG, DEFAULT_VISUAL_SETTINGS
} from '../constants';

export interface PreferencesSlice {
    persona: AetherPersona;
    preferences: UserPreferences;
    settingsOpen: boolean;
    activeSkills: Skill[];
    cachedSkills: Skill[];
    skillsSyncStatus: SkillsSyncStatus;
    personaConfig: PersonaConfig;
    themeConfig: ThemeConfig;
    visualSettings: VisualSettings;

    setPersona: (updates: Partial<AetherPersona>) => void;
    setPreferences: (updates: Partial<UserPreferences>) => void;
    toggleSuperpower: (key: keyof Superpowers) => void;
    toggleSkillFocus: (skill: SkillFocus) => void;
    toggleSettings: () => void;
    resetPreferences: () => void;
    setActiveSkills: (skills: Skill[]) => void;
    setCachedSkills: (skills: Skill[]) => void;
    toggleSkill: (skillId: string) => void;
    setSkillsSyncStatus: (status: SkillsSyncStatus) => void;
    setPersonaConfig: (config: Partial<PersonaConfig>) => void;
    setThemeConfig: (config: Partial<ThemeConfig>) => void;
    setVisualSettings: (settings: Partial<VisualSettings>) => void;
    toggleThemeMode: () => void;
}

export const createPreferencesSlice: StateCreator<PreferencesSlice> = (set) => ({
    persona: DEFAULT_PERSONA,
    preferences: DEFAULT_PREFERENCES,
    settingsOpen: false,
    activeSkills: [],
    cachedSkills: [],
    skillsSyncStatus: 'idle',
    personaConfig: DEFAULT_PERSONA_CONFIG,
    themeConfig: DEFAULT_THEME_CONFIG,
    visualSettings: DEFAULT_VISUAL_SETTINGS,

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

    setActiveSkills: (activeSkills) => set({ activeSkills }),
    setCachedSkills: (cachedSkills) => set({ cachedSkills }),

    toggleSkill: (skillId) => set((state) => ({
        activeSkills: state.activeSkills.map(skill =>
            skill.id === skillId ? { ...skill, enabled: !skill.enabled } : skill
        ),
    })),

    setSkillsSyncStatus: (skillsSyncStatus) => set({ skillsSyncStatus }),

    setPersonaConfig: (updates) => set((state) => ({
        personaConfig: { ...state.personaConfig, ...updates },
    })),

    setThemeConfig: (updates) => set((state) => ({
        themeConfig: { ...state.themeConfig, ...updates },
    })),

    setVisualSettings: (updates) => set((state) => ({
        visualSettings: { ...state.visualSettings, ...updates },
    })),

    toggleThemeMode: () => set((state) => ({
        themeConfig: {
            ...state.themeConfig,
            themeMode: state.themeConfig.themeMode === 'dark-state' ? 'white-hole' : 'dark-state',
        },
    })),
});
