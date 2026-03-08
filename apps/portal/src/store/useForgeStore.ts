import { create } from 'zustand';

export type ForgeStep = 'genesis' | 'brain' | 'memory' | 'skills' | 'visual' | 'review' | 'synthesizing';

export interface AgentDNA {
    name: string;
    role: string;
    tone: string;
    provider: string;
    model: string;
    apiKey: string;
    memoryType: 'firebase' | 'local';
    skills: string[];
    avatarUrl?: string;
}

interface ForgeState {
    activeStep: ForgeStep;
    dna: AgentDNA;
    isListening: boolean;
    transcript: string;

    // Actions
    setStep: (step: ForgeStep) => void;
    updateDNA: (update: Partial<AgentDNA>) => void;
    setListening: (listening: boolean) => void;
    setTranscript: (text: string) => void;
    resetForge: () => void;
}

const initialDNA: AgentDNA = {
    name: '',
    role: '',
    tone: 'Professional & Technical',
    provider: 'google',
    model: 'gemini-2.0-flash',
    apiKey: '',
    memoryType: 'firebase',
    skills: [],
};

export const useForgeStore = create<ForgeState>((set) => ({
    activeStep: 'genesis',
    dna: initialDNA,
    isListening: false,
    transcript: '',

    setStep: (step) => set({ activeStep: step }),
    updateDNA: (update) => set((state) => ({ dna: { ...state.dna, ...update } })),
    setListening: (listening) => set({ isListening: listening }),
    setTranscript: (text) => set({ transcript: text }),
    resetForge: () => set({ activeStep: 'genesis', dna: initialDNA, transcript: '' }),
}));
