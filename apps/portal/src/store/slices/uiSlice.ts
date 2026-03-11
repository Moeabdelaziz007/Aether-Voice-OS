import { StateCreator } from 'zustand';
import {
    AvatarCinematicState, TaskPulse, MissionLogEntry, NotesPlanetEntry,
    MirrorFrameEvent, VoyagerLatencyRow, OrbitPlanet, OrbitalLayoutPreset,
    WorkspaceStateEnvelope, OrbitLane
} from '../types';

export type AvatarState = 'Idle' | 'Listening' | 'ListeningActive' | 'ListeningWaiting' | 'Speaking' | 'Thinking' | 'Error';

export interface TranscriptStream {
    interim: string;
    final: string;
    confidence: number;
    latencyMs: number;
}

export interface UISlice {
    // ─── Neural UI State ─────────────────────────────────────
    theme: 'dark' | 'light' | 'system';
    sidebarOpen: boolean;
    activeTab: 'terminal' | 'files' | 'dna' | 'network' | 'telemetry';

    // ─── Avatar & Interaction ────────────────────────────────
    avatarState: AvatarState;
    avatarCinematicState: AvatarCinematicState;
    auraSettings: {
        particlesEnabled: boolean;
        bloomIntensity: number;
        reflectionOpacity: number;
    };

    // ─── Transcript & Real-time Text ────────────────────────
    voiceTranscript: string;
    transcriptStream: TranscriptStream;
    isListening: boolean;
    // ─── Original UI State ───────────────────────────────────
    visionActive: boolean;
    activeWidgets: { id: string; type: string; props: any }[];
    predictedGoal: string | null;
    workspaceGalaxy: string;
    taskPulse: TaskPulse | null;
    missionLog: MissionLogEntry[];
    notesPlanet: NotesPlanetEntry[];
    mirrorFrames: MirrorFrameEvent[];
    voyagerLatencyRows: VoyagerLatencyRow[];
    orbitRegistry: Record<string, OrbitPlanet>;
    focusedPlanetId: string | null;
    orbitalLayoutPreset: OrbitalLayoutPreset;
    focusModeEnvironment: boolean;
    gazeTarget: [number, number, number];
    showTelemetry: boolean;
    omnibarFocused: boolean;

    // ─── Actions ─────────────────────────────────────────────
    setTheme: (theme: 'dark' | 'light' | 'system') => void;
    toggleSidebar: () => void;
    setActiveTab: (tab: 'terminal' | 'files' | 'dna' | 'network' | 'telemetry') => void;
    setAvatarState: (state: AvatarState) => void;
    setAvatarCinematicState: (state: AvatarCinematicState) => void;
    setVoiceTranscript: (transcript: string) => void;
    setTranscriptStream: (stream: Partial<TranscriptStream>) => void;
    setIsListening: (isListening: boolean) => void;
    // ─── Original Actions ────────────────────────────────────
    setVisionActive: (active: boolean) => void;
    addWidget: (type: string, props: any) => void;
    removeWidget: (id: string) => void;
    clearWidgets: () => void;
    setPredictedGoal: (goal: string | null) => void;
    setWorkspaceGalaxy: (galaxy: string) => void;
    setTaskPulse: (pulse: TaskPulse | null) => void;
    pushMissionLog: (entry: Omit<MissionLogEntry, 'id' | 'timestamp'>) => void;
    clearMissionLog: () => void;
    createPlanetNote: (entry: { content: string; tag?: string; taskId?: string; sessionId?: string }) => string;
    updatePlanetNote: (id: string, updates: Partial<Pick<NotesPlanetEntry, 'content' | 'tag' | 'taskId' | 'sessionId'>>) => void;
    deletePlanetNote: (id: string) => void;
    clearPlanetNotes: () => void;
    addMirrorFrameEvent: (event: Omit<MirrorFrameEvent, 'id' | 'timestamp'>) => void;
    clearMirrorFrameEvents: () => void;
    pushVoyagerLatencyRow: (row: Omit<VoyagerLatencyRow, 'id' | 'timestamp'>) => void;
    clearVoyagerLatencyRows: () => void;
    setOrbitalLayoutPreset: (preset: OrbitalLayoutPreset) => void;
    setFocusModeEnvironment: (enabled: boolean) => void;
    setGazeTarget: (target: [number, number, number]) => void;
    upsertOrbitPlanet: (planet: OrbitPlanet) => void;
    focusOrbitPlanet: (planetId: string | null) => void;
    clearOrbitRegistry: () => void;
    applyWorkspaceState: (payload: WorkspaceStateEnvelope) => void;
    setShowTelemetry: (show: boolean) => void;
    setOmnibarFocused: (focused: boolean) => void;
}

const ORBIT_PRESET_MULTIPLIER: Record<OrbitalLayoutPreset, number> = {
    inner: 0.85,
    mid: 1.0,
    outer: 1.2,
};

const laneFromRadius = (radius: number): OrbitLane => {
    if (radius < 120) return 'inner';
    if (radius < 220) return 'mid';
    return 'outer';
};

const hashToOrbitSeed = (input: string): number => {
    let hash = 0;
    for (let i = 0; i < input.length; i += 1) {
        hash = (hash * 31 + input.charCodeAt(i)) % 100000;
    }
    return hash;
};

export const createUISlice: StateCreator<UISlice> = (set, get) => ({
    // ─── Neural UI State ─────────────────────────────────────
    theme: 'dark',
    sidebarOpen: false,
    activeTab: 'terminal',

    // ─── Avatar & Interaction ────────────────────────────────
    avatarState: 'Idle',
    avatarCinematicState: 'IDLE',
    auraSettings: {
        particlesEnabled: true,
        bloomIntensity: 0.8,
        reflectionOpacity: 0.5,
    },

    // ─── Transcript & Real-time Text ────────────────────────
    voiceTranscript: '',
    transcriptStream: {
        interim: '',
        final: '',
        confidence: 1.0,
        latencyMs: 0
    },
    isListening: false,
    // ─── Original UI State ───────────────────────────────────
    visionActive: false,
    activeWidgets: [],
    predictedGoal: null,
    workspaceGalaxy: "Genesis",
    taskPulse: null,
    missionLog: [],
    notesPlanet: [],
    mirrorFrames: [],
    voyagerLatencyRows: [],
    orbitRegistry: {},
    focusedPlanetId: null,
    orbitalLayoutPreset: 'mid',
    focusModeEnvironment: false,
    gazeTarget: [0, 0, 5],
    showTelemetry: false,
    omnibarFocused: false,

    // ─── Actions ─────────────────────────────────────────────
    setTheme: (theme) => set({ theme }),
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    setActiveTab: (tab) => set({ activeTab: tab }),
    setAvatarState: (state) => set({ avatarState: state }),
    setAvatarCinematicState: (avatarCinematicState) => set({ avatarCinematicState }),
    setVoiceTranscript: (voiceTranscript) => set({ voiceTranscript }),
    setTranscriptStream: (stream) => set((state) => ({
        transcriptStream: { ...state.transcriptStream, ...stream }
    })),
    setIsListening: (isListening) => set({ isListening }),
    // ─── Original Actions ────────────────────────────────────
    setVisionActive: (visionActive) => set({ visionActive }),
    addWidget: (type, props) => set((state) => ({
        activeWidgets: [...state.activeWidgets, { id: crypto.randomUUID(), type, props }]
    })),
    removeWidget: (id) => set((state) => ({
        activeWidgets: state.activeWidgets.filter(w => w.id !== id)
    })),
    clearWidgets: () => set({ activeWidgets: [] }),
    setPredictedGoal: (predictedGoal) => set({ predictedGoal }),
    setWorkspaceGalaxy: (workspaceGalaxy) => set({ workspaceGalaxy }),
    setTaskPulse: (taskPulse) => set({ taskPulse }),
    pushMissionLog: (entry) => set((state) => ({
        missionLog: [...state.missionLog, {
            ...entry,
            id: crypto.randomUUID(),
            timestamp: Date.now(),
        }].slice(-120),
    })),
    clearMissionLog: () => set({ missionLog: [] }),
    createPlanetNote: ({ content, tag = 'general', taskId, sessionId }) => {
        const noteId = crypto.randomUUID();
        const now = Date.now();
        set((state) => ({
            notesPlanet: [...state.notesPlanet, {
                id: noteId,
                content,
                tag,
                taskId,
                sessionId,
                createdAt: now,
                updatedAt: now,
            }].slice(-500),
        }));
        return noteId;
    },
    updatePlanetNote: (id, updates) => set((state) => ({
        notesPlanet: state.notesPlanet.map((note) =>
            note.id === id
                ? {
                    ...note,
                    ...updates,
                    updatedAt: Date.now(),
                }
                : note
        ),
    })),
    deletePlanetNote: (id) => set((state) => ({
        notesPlanet: state.notesPlanet.filter((note) => note.id !== id),
    })),
    clearPlanetNotes: () => set({ notesPlanet: [] }),
    addMirrorFrameEvent: (event) => set((state) => ({
        mirrorFrames: [...state.mirrorFrames, {
            ...event,
            id: crypto.randomUUID(),
            timestamp: Date.now(),
        }].slice(-40),
    })),
    clearMirrorFrameEvents: () => set({ mirrorFrames: [] }),
    pushVoyagerLatencyRow: (row) => set((state) => ({
        voyagerLatencyRows: [...state.voyagerLatencyRows, {
            ...row,
            id: crypto.randomUUID(),
            timestamp: Date.now(),
        }].slice(-20),
    })),
    clearVoyagerLatencyRows: () => set({ voyagerLatencyRows: [] }),
    setOrbitalLayoutPreset: (orbitalLayoutPreset) => set({ orbitalLayoutPreset }),
    setFocusModeEnvironment: (focusModeEnvironment) => set({ focusModeEnvironment }),
    setGazeTarget: (gazeTarget) => set({ gazeTarget }),
    upsertOrbitPlanet: (planet) => set((state) => ({
        orbitRegistry: {
            ...state.orbitRegistry,
            [planet.planetId]: planet,
        },
    })),
    focusOrbitPlanet: (focusedPlanetId) => set({
        focusedPlanetId,
        focusModeEnvironment: Boolean(focusedPlanetId),
    }),
    clearOrbitRegistry: () => set({
        orbitRegistry: {},
        focusedPlanetId: null,
        focusModeEnvironment: false,
    }),
    applyWorkspaceState: (payload) => set((state) => {
        const galaxy = payload.galaxy || payload.workspace_galaxy;
        const appId = payload.app_id || payload.appId || payload.focused_app_id || payload.focusedAppId;
        const focusedPlanetId = payload.focused_app_id || payload.focusedAppId || state.focusedPlanetId;
        const nextState: any = {};

        if (galaxy) nextState.workspaceGalaxy = galaxy;
        if (!appId) {
            if (focusedPlanetId !== state.focusedPlanetId) {
                nextState.focusedPlanetId = focusedPlanetId;
                nextState.focusModeEnvironment = Boolean(focusedPlanetId);
            }
            return nextState;
        }

        const current = state.orbitRegistry[appId];
        const seed = hashToOrbitSeed(appId);
        const defaultAngle = ((seed % 360) * Math.PI) / 180;
        const defaultRadius = (130 + (seed % 110)) * ORBIT_PRESET_MULTIPLIER[state.orbitalLayoutPreset];
        const x = Number(payload.position?.x ?? payload.x ?? current?.position.x ?? Math.cos(defaultAngle) * defaultRadius);
        const y = Number(payload.position?.y ?? payload.y ?? current?.position.y ?? Math.sin(defaultAngle) * defaultRadius);
        const radius = Math.max(24, Math.hypot(x, y));
        const angle = Math.atan2(y, x);
        const lane = payload.orbit_lane || payload.orbitLane || laneFromRadius(radius);
        const action = payload.action || '';

        if (payload.orbit_lane || payload.orbitLane) {
            nextState.orbitalLayoutPreset = lane;
        }

        const nextPlanet: OrbitPlanet = {
            planetId: appId,
            planetType: current?.planetType || appId.split('-')[0] || 'utility',
            lane,
            angle,
            radius,
            position: { x, y },
            isMaterialized: action === 'materialize_app' ? true : (current?.isMaterialized ?? true),
            isCollapsed: action === 'collapse_app' ? true : action === 'materialize_app' ? false : (current?.isCollapsed ?? false),
            updatedAt: Date.now(),
        };

        const focusFromAction = action === 'focus_app' ? appId : focusedPlanetId;
        const shouldDisableFocusMode = action === 'collapse_app' && (state.focusedPlanetId === appId || focusedPlanetId === appId);

        nextState.orbitRegistry = {
            ...state.orbitRegistry,
            [appId]: nextPlanet,
        };
        nextState.focusedPlanetId = shouldDisableFocusMode ? null : focusFromAction || null;
        nextState.focusModeEnvironment = shouldDisableFocusMode ? false : Boolean(nextState.focusedPlanetId);
        return nextState;
    }),
    setShowTelemetry: (showTelemetry) => set({ showTelemetry }),
    setOmnibarFocused: (omnibarFocused) => set({ omnibarFocused }),
});
