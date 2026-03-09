import { StateStorage } from 'zustand/middleware';
import { get, set, del } from 'idb-keyval';

/**
 * Custom storage engine for Zustand using IndexedDB (via idb-keyval).
 * Why?
 * 1. Security: IndexedDB is not directly accessible via simple console like localStorage.
 * 2. Capacity: localStorage is limited to ~5MB. IndexedDB can store gigabytes.
 * 3. Performance: Async by nature, prevents blocking the main thread during heavy state persistence.
 */
// Fallback for SSR and testing environments where indexedDB is not available
const isBrowser = typeof window !== 'undefined' && typeof window.indexedDB !== 'undefined';

export const idbStorage: any = {
    getItem: async (name: string): Promise<string | null> => {
        if (!isBrowser) return null;
        try {
            return (await get(name)) || null;
        } catch (e) {
            return null;
        }
    },
    setItem: async (name: string, value: string): Promise<void> => {
        if (!isBrowser) return;
        try {
            await set(name, value);
        } catch (e) {}
    },
    removeItem: async (name: string): Promise<void> => {
        if (!isBrowser) return;
        try {
            await del(name);
        } catch (e) {}
    },
};
