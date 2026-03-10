import { StateCreator } from 'zustand';

export type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface AetherError {
    id: string;
    code: string;
    message: string;
    severity: ErrorSeverity;
    retryable: boolean;
    timestamp: number;
    actionLabel?: string;
    onAction?: () => void;
}

export interface ErrorSlice {
    errors: AetherError[];
    addError: (error: Omit<AetherError, 'id' | 'timestamp'>) => string;
    dismissError: (id: string) => void;
    clearErrors: () => void;
    getLastError: () => AetherError | null;
}

export const createErrorSlice: StateCreator<ErrorSlice> = (set, get) => ({
    errors: [],
    addError: (error) => {
        const id = crypto.randomUUID();
        const newError: AetherError = {
            ...error,
            id,
            timestamp: Date.now(),
        };
        set((state) => ({
            errors: [newError, ...state.errors].slice(0, 10), // Keep last 10
        }));
        return id;
    },
    dismissError: (id) => set((state) => ({
        errors: state.errors.filter((e) => e.id !== id),
    })),
    clearErrors: () => set({ errors: [] }),
    getLastError: () => {
        const { errors } = get();
        return errors.length > 0 ? errors[0] : null;
    },
});
