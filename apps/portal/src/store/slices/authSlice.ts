import { StateCreator } from 'zustand';
import { ConnectionStatus, EngineState, RealmType, RepairState } from '../types';
import { DEFAULT_REPAIR_STATE } from '../constants';

export interface AuthSlice {
    currentRealm: RealmType;
    status: ConnectionStatus;
    engineState: EngineState;
    connectionMode: 'gemini' | 'gateway';
    sessionStartTime: number | null;
    repairState: RepairState;

    setRealm: (realm: RealmType) => void;
    setStatus: (status: ConnectionStatus) => void;
    setEngineState: (state: EngineState) => void;
    setConnectionMode: (mode: 'gemini' | 'gateway') => void;
    setSessionStartTime: (time: number | null) => void;
    setRepairState: (state: RepairState) => void;
    clearRepairState: () => void;
}

export const createAuthSlice: StateCreator<AuthSlice> = (set) => ({
    currentRealm: "void",
    status: "disconnected",
    engineState: "IDLE",
    connectionMode: 'gemini',
    sessionStartTime: null,
    repairState: DEFAULT_REPAIR_STATE,

    setRealm: (currentRealm) => set({ currentRealm }),
    setStatus: (status) => set({ status }),
    setEngineState: (engineState) => set({ engineState }),
    setConnectionMode: (connectionMode) => set({ connectionMode }),
    setSessionStartTime: (sessionStartTime) => set({ sessionStartTime }),
    setRepairState: (repairState) => set({ repairState }),
    clearRepairState: () => set({ repairState: DEFAULT_REPAIR_STATE }),
});
