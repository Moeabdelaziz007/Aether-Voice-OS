import { StateCreator } from 'zustand';
import {
    TranscriptMessage, NeuralEvent, SilentHint, ToolCallEntry,
    TerminalLog, FeedEntry, GlobalAgent, MemoryCrystal, DragState
} from '../types';

export interface DataSlice {
    transcript: TranscriptMessage[];
    neuralEvents: NeuralEvent[];
    systemLogs: string[];
    silentHints: SilentHint[];
    activeSoul: string | null;
    toolCallHistory: ToolCallEntry[];
    terminalLogs: TerminalLog[];
    isInterrupted: boolean;
    scrollPaused: boolean;
    streamingBuffer: string;
    platformFeed: FeedEntry[];
    globalRegistry: Record<string, GlobalAgent>;
    activeHubView: 'discovery' | 'my-agents' | 'forge';
    memoryCrystals: MemoryCrystal[];
    dragState: DragState;
    animationTrigger: 'none' | 'soul-swap' | 'laser-scan' | 'high-voltage' | 'tether-stream';

    addTranscriptMessage: (msg: Omit<TranscriptMessage, 'id' | 'timestamp'>) => void;
    addNeuralEvent: (event: Omit<NeuralEvent, 'id'>) => void;
    updateNeuralEvent: (id: string, updates: Partial<NeuralEvent>) => void;
    addSystemLog: (log: string) => void;
    addSilentHint: (hint: SilentHint) => void;
    dismissHint: (id: string) => void;
    clearTranscript: () => void;
    setActiveSoul: (soul: string | null) => void;
    addToolCall: (entry: Omit<ToolCallEntry, 'id' | 'timestamp'>) => void;
    addTerminalLog: (level: TerminalLog['level'], message: string, widgetId?: string) => void;
    clearTerminalLogs: () => void;
    setInterrupted: (interrupted: boolean) => void;
    setScrollPaused: (paused: boolean) => void;
    setStreamingBuffer: (buffer: string) => void;
    pushToFeed: (entry: Omit<FeedEntry, 'id' | 'timestamp'>) => void;
    updateGlobalAgent: (agent: GlobalAgent) => void;
    setHubView: (view: 'discovery' | 'my-agents' | 'forge') => void;
    addCrystal: (crystal: Omit<MemoryCrystal, 'id'>) => void;
    removeCrystal: (id: string) => void;
    setDragState: (updates: Partial<DragState>) => void;
    absorbCrystal: (id: string) => void;
    triggerAnimation: (type: 'none' | 'soul-swap' | 'laser-scan' | 'high-voltage' | 'tether-stream') => void;
}

export const createDataSlice: StateCreator<DataSlice> = (set, get) => ({
    transcript: [],
    neuralEvents: [],
    systemLogs: [],
    silentHints: [],
    activeSoul: null,
    toolCallHistory: [],
    terminalLogs: [],
    isInterrupted: false,
    scrollPaused: false,
    streamingBuffer: '',
    platformFeed: [],
    globalRegistry: {},
    activeHubView: 'discovery',
    memoryCrystals: [
        { id: '1', label: 'Initial Refactor', type: 'code', color: '#00f3ff', metadata: {} },
        { id: '2', label: 'Gemini Integration', type: 'research', color: '#bc13fe', metadata: {} },
    ],
    dragState: { isDragging: false, activeData: null as any, type: 'data' },
    animationTrigger: 'none',

    addTranscriptMessage: (msg) => set((state) => ({
        transcript: [...state.transcript, {
            ...msg,
            id: crypto.randomUUID(),
            timestamp: Date.now(),
        }],
    })),

    addNeuralEvent: (event) => set((state) => ({
        neuralEvents: [...state.neuralEvents, { ...event, id: crypto.randomUUID() }],
    })),

    updateNeuralEvent: (id, updates) => set((state) => ({
        neuralEvents: state.neuralEvents.map(evt =>
            evt.id === id ? { ...evt, ...updates } : evt
        ),
    })),

    addSystemLog: (log) => set((state) => {
        const newLogs = [...state.systemLogs, log];
        return { systemLogs: newLogs.slice(-50) };
    }),

    addSilentHint: (hint) => set((state) => ({
        silentHints: [...state.silentHints, hint].slice(-10),
    })),

    dismissHint: (id) => set((state) => ({
        silentHints: state.silentHints.filter(h => h.id !== id),
    })),

    clearTranscript: () => set({ transcript: [] }),

    setActiveSoul: (activeSoul) => set({ activeSoul }),

    addToolCall: (entry) => set((state) => ({
        toolCallHistory: [...state.toolCallHistory, {
            ...entry,
            id: crypto.randomUUID(),
            timestamp: Date.now(),
        }].slice(-50),
    })),

    addTerminalLog: (level, message, widgetId) => set((state) => ({
        terminalLogs: [...state.terminalLogs, {
            id: crypto.randomUUID(),
            level,
            message,
            timestamp: Date.now(),
            widgetId,
        }].slice(-50),
    })),

    clearTerminalLogs: () => set({ terminalLogs: [] }),
    setInterrupted: (isInterrupted) => set({ isInterrupted }),
    setScrollPaused: (scrollPaused) => set({ scrollPaused }),
    setStreamingBuffer: (streamingBuffer) => set({ streamingBuffer }),

    pushToFeed: (entry) => set((state) => ({
        platformFeed: [{
            ...entry,
            id: crypto.randomUUID(),
            timestamp: Date.now()
        }, ...state.platformFeed].slice(0, 100)
    })),

    updateGlobalAgent: (agent) => set((state) => ({
        globalRegistry: { ...state.globalRegistry, [agent.id]: agent }
    })),

    setHubView: (activeHubView) => set({ activeHubView }),

    addCrystal: (crystal) => set((state) => ({
        memoryCrystals: [...state.memoryCrystals, { ...crystal, id: crypto.randomUUID() }]
    })),

    removeCrystal: (id) => set((state) => ({
        memoryCrystals: state.memoryCrystals.filter(c => c.id !== id)
    })),

    setDragState: (updates) => set((state) => ({
        dragState: { ...state.dragState, ...updates }
    })),

    absorbCrystal: (id) => {
        const crystal = get().memoryCrystals.find(c => c.id === id);
        if (crystal) {
            set((state) => ({
                terminalLogs: [...state.terminalLogs, {
                    id: crypto.randomUUID(),
                    level: 'SUCCESS' as const,
                    message: `💎 Crystal Absorbed: ${crystal.label}`,
                    timestamp: Date.now()
                }].slice(-50),
                memoryCrystals: state.memoryCrystals.filter(c => c.id !== id)
            }));
        }
    },

    triggerAnimation: (type) => {
        set({ animationTrigger: type });
        if (type !== 'none') {
            setTimeout(() => {
                if (get().animationTrigger === type) {
                    set({ animationTrigger: 'none' });
                }
            }, 3000);
        }
    },
});
